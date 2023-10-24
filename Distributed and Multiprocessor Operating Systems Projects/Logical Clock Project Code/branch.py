from code import interact
import grpc
import banking_pb2
import banking_pb2_grpc
from banking_pb2 import ClientRequest, BranchResponse
import os

base_port = 50000

class Branch(banking_pb2_grpc.BranchServicer):

    def __init__(self, id, balance, branches):
        # unique ID of the Branch
        self.id = id
        # replica of the Branch's balance
        self.balance = balance
        # the list of process IDs of the branches
        self.branches = branches
        # the list of Client stubs to communicate with the branches
        self.stubList = list()
        # a list of received messages used for debugging purpose
        self.recvMsg = list()
        # logical clock 
        self.clock = 1
        # a list of events received by this branch
        self.events = list()

    # Each branch maintains rpc channels to other peer branches in the banking system for propagating updates
    def createStubs(self):
        for branchID in self.branches:
            if branchID != self.id:
                port = str(base_port + branchID)
                pid = os.getpid()
                print(f"pid {pid} Create channel on port {port}")
                channel = grpc.insecure_channel("localhost:" + port)
                self.stubList.append(banking_pb2_grpc.BranchStub(channel))
                
    # Handle the query request from client, return the current balance
    # Note: query request doesn't include money argument
    def HandleQuery(self, request):
        return BranchResponse(id=request.id, interface=request.interface, result="success", money=self.balance, clock=self.clock)
    
    # Handle the deposit request from client
    def HandleDeposit(self, request, propagate):
        pid = os.getpid()
        print(f"process {pid} gets a deposit request {request.id}, {request.interface}, {request.money}, {request.clock}, propagate {propagate}")
        result = "success"
        self.balance += request.money
        if propagate == True:
            self.Propagate_Deposit(request)
        return BranchResponse(id=request.id, interface=request.interface, result=result,money=self.balance, clock=self.clock)
    
    # Handle the withdraw request from client
    def HandleWithdraw(self, request, propagate):
        pid = os.getpid()
        print(f"process {pid} gets a withdraw request {request.id}, {request.interface}, {request.money} propagate {propagate}")
        result = "success"
        if request.money > self.balance:
            result = "fail"
            return BranchResponse(id=request.id, interface=request.interface, result=result, money=self.balance, clock=self.clock)
        self.balance -= request.money
        if propagate == True:
            self.Propagate_Withdraw(request)
        return BranchResponse(id=request.id, interface=request.interface, result=result, money=self.balance, clock=self.clock)
    
    # Handle a request, propagate indicates if it's a propagated requeset from peer branches
    def HandleRequest(self, request, propagate):
        msg = {"id": request.id, "interface": request.interface}
        if request.interface != "query":
           msg["money"] = request.money
        self.recvMsg.append(msg)
        response = None
        
        # sanity check 
        if request.interface != "query" and request.money < 0:
            return BranchResponse(id=request.id, interface=request.interface, result="fail", money=self.balance,clock=self.clock)
        
        # Record execute events 
        if request.interface != "query":
            if propagate:
                self.Event_Execute(request)
            else:
                self.Propagate_Execute(request)
        
            
        if request.interface == "query":
            response = self.HandleQuery(request)
        elif request.interface == "deposit":
            response = self.HandleDeposit(request, propagate)
        elif request.interface == "withdraw":
            response = self.HandleWithdraw(request, propagate)
        else:
            pass
        
        if request.interface != "query" and propagate:
            self.Event_Response(response)

        return response
    
    # Handle request from client 
    def MsgDelivery(self, request, context):
        pid = os.getpid()
        print(f"process {pid} received request: {request.id}, {request.interface}, {request.money}, {request.clock}")
        if request.interface != "query":
            self.Event_Request(request)
        return self.HandleRequest(request, True)
    
    # Handle propagated request from peers 
    def MsgPropagation(self, request, context):
        if request.interface != "query":
            self.Propagate_Request(request)
        return self.HandleRequest(request, False)
    
    # Handle Deposit propagation
    def Propagate_Deposit(self, request):
        for stub in self.stubList:
            response = stub.MsgPropagation(ClientRequest(id=request.id, interface="deposit", money=request.money,clock=self.clock))
            self.Propagate_Response(response)
    
    # Handle Withdraw propagation
    def Propagate_Withdraw(self, request):
        for stub in self.stubList:
            response = stub.MsgPropagation(ClientRequest(id=request.id, interface="withdraw",money=request.money,clock=self.clock)) 
            self.Propagate_Response(response)
            
    # This subevent deals with the receipt of event(deposit and withdraw) from customer
    def Event_Request(self, request):
        self.clock = max(self.clock, request.clock) + 1
        self.events.append({"id":request.id, "name":request.interface + "_request", "clock" : self.clock})
        
    # This subevent deals with the excution of a customer event
    def Event_Execute(self, request):
        self.clock += 1
        self.events.append({"id":request.id, "name":request.interface + "_execute", "clock" : self.clock})
        
    # This subevent deals with the event of propogating a request to fellow branches
    def Propagate_Request(self, request):
        #self.clock += 1
        self.clock = max(self.clock, request.clock) + 1
        self.events.append({"id": request.id, "name": request.interface + "_propagate_request", "clock": self.clock})
        
    # This subevent executes the propagated request
    def Propagate_Execute(self, request):
        self.clock += 1
        self.events.append({"id": request.id, "name": request.interface + "_propagate_execute", "clock": self.clock})
        
    # This subevent handles the receipt of the result of propagated event from fellow branches 
    def Propagate_Response(self, response):
        self.clock = max(self.clock, response.clock) + 1
        self.events.append({"id": response.id, "name": response.interface + "_propagate_response", "clock": self.clock})

    # This subevent returns the response to the customer 
    def Event_Response(self, response):
        self.clock += 1
        self.events.append({"id": response.id, "name": response.interface + "_response", "clock": self.clock})
        
    # print out branch's events list
    def get_events(self):
        return self.events