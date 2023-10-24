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
        return BranchResponse(interface=request.interface, result="success", money=self.balance)
    
    # Handle the deposit request from client
    def HandleDeposit(self, request, propagate):
        pid = os.getpid()
        print(f"process {pid} gets a deposit request {request.id}, {request.interface}, {request.money} propagate {propagate}")
        result = "success"
        self.balance += request.money
        if propagate == True:
            self.Propagate_Deposit(request)
        return BranchResponse(interface=request.interface, result=result,money=self.balance)
    
    # Handle the withdraw request from client
    def HandleWithdraw(self, request, propagate):
        pid = os.getpid()
        print(f"process {pid} gets a withdraw request {request.id}, {request.interface}, {request.money} propagate {propagate}")
        result = "success"
        if request.money > self.balance:
            result = "fail"
            return BranchResponse(interface=request.interface, result=result, money=self.balance)
        self.balance -= request.money
        if propagate == True:
            self.Propagate_Withdraw(request)
        return BranchResponse(interface=request.interface, result=result, money=self.balance)
    
    # Handle a request, propagate indicates if it's a propagated requeset from peer branches
    def HandleRequest(self, request, propagate):
        msg = {"id": request.id, "interface": request.interface}
        if request.interface != "query":
           msg["money"] = request.money
        self.recvMsg.append(msg)
        
        # sanity check 
        if request.interface != "query" and request.money < 0:
            return BranchResponse(interface=request.interface, result="fail", money=self.balance)
        
        if request.interface == "query":
            return self.HandleQuery(request)
        elif request.interface == "deposit":
            return self.HandleDeposit(request, propagate)
        elif request.interface == "withdraw":
            return self.HandleWithdraw(request, propagate)
        else:
            pass
    
    # Handle request from client 
    def MsgDelivery(self, request, context):
        pid = os.getpid()
        print(f"process {pid} received request: {request.id}, {request.interface}, {request.money}")
        return self.HandleRequest(request, True)
    
    # Handle propagated request from peers 
    def MsgPropagation(self, request, context):
        return self.HandleRequest(request, False)
    
    # Handle Deposit propagation
    def Propagate_Deposit(self, request):
        for stub in self.stubList:
            stub.MsgPropagation(ClientRequest(id=request.id, interface="deposit", money=request.money))
            #stub.MsgPropagation(request)
    
    # Handle Withdraw propagation
    def Propagate_Withdraw(self, request):
        for stub in self.stubList:
            #stub.MsgPropagation(ClientRequest(id=request.id, interface="withdraw",money=request.money)) 
            stub.MsgPropagation(ClientRequest(id=request.id, interface="withdraw",money=request.money)) 
        