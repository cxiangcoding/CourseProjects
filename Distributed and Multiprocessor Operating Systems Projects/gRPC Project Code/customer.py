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
        # pointer for the stub
        self.stub = None

    # create a stub via which RPC can be called
    def createStub(self):
        port = str(base_port + self.id)
        channel = grpc.insecure_channel("localhost:" + port)
        self.stub = banking_pb2_grpc.BranchStub(channel)

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
            
            # send a gRPC request 
            response = self.stub.MsgDelivery(ClientRequest(id=event["id"],interface=event["interface"],money=event["money"]))
            msg = {"interface" : response.interface, "result" : response.result}
            self.recvMsg.append(msg)
            
        print(f"processing query events {query_events}")
        # process query evernts    
        for event in query_events:
            sleep(3)        # sleep 3 seconds to allow updates to complete
            response = self.stub.MsgDelivery(ClientRequest(id=event["id"],interface=event["interface"],money=event["money"]))
            msg = {"interface":response.interface, "result":response.result, "money":response.money}
            self.recvMsg.append(msg)

    # output the responses 
    def output(self):
        return {'id' : self.id, 'recv' : self.recvMsg}
