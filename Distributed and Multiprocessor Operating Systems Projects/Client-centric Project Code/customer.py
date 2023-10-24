import grpc
from banking_pb2 import ClientRequest
import banking_pb2_grpc
from time import sleep
import os

base_port = 50000

class Customer:
    def __init__(self, id, events):
        # unique ID of the Customer
        self.id = id
        # events from the input
        self.events = events
        # a list of received messages used for debugging purpose
        self.recvMsg = list()
        # writeidset to hold return id set for its events 
        self.writeidset = list()

    # Execute the sevents by sending gRPC requests and get the responses 
    def executeEvents(self):
        # query events are sent after other events
        pid = os.getpid()
        print(f"process {pid} process events {self.events}")
        query_events = list()
        for event in self.events:
            if event["interface"] == "query":
                query_events.append(event)
                continue
            
            # setup the stub to dest port 
            port = str(base_port + event["dest"])
            channel = grpc.insecure_channel("localhost:" + port)
            stub = banking_pb2_grpc.BranchStub(channel)
            # send a gRPC request 
            response = stub.MsgDelivery(ClientRequest(interface=event["interface"], money=event["money"], id=event["id"], writeidset=self.writeidset))
            msg = {"interface" : response.interface, "dest" : event["dest"], "money":response.money}
            self.recvMsg.append(msg)
            
            # update the writeisset with returned value 
            self.writeidset = response.writeidset
            sleep(1)
            
        print(f"processing query events {query_events}")
        # process query evernts    
        for event in query_events:
            sleep(3)        # sleep 3 seconds to allow updates to complete
            # setup the stub to dest port 
            port = str(base_port + event["dest"])
            channel = grpc.insecure_channel("localhost:" + port)
            stub = banking_pb2_grpc.BranchStub(channel)
            response = stub.MsgDelivery(ClientRequest(interface=event["interface"],money=0, id=event["id"], writeidset=self.writeidset))
            msg = {"interface" : response.interface, "dest" : event["dest"], "money":response.money}
            self.recvMsg.append(msg)

        # return the result for the last query 
        return {"id": self.id, "balance" : self.recvMsg[-1]["money"]}
