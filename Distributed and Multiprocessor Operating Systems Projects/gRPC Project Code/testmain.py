import json     #for processing json input 
import sys      #for argv 
import multiprocessing
from threading import currentThread
from time import sleep
from concurrent import futures

import grpc

import banking_pb2_grpc
from branch import Branch
from customer import Customer
import os
base_port = 50000
output_file = "output.txt"

# start gRPC server on branch 
def serverBranch(branch):
    pid = os.getpid()
    print(f"Starting process {pid} for {branch.id}, {branch.balance}, {branch.branches}")
    branch.createStubs()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    banking_pb2_grpc.add_BranchServicer_to_server(branch,server)
    port = str(base_port + branch.id)
    server.add_insecure_port("localhost:" + port)
    server.start()
    server.wait_for_termination()
    

# process client events 
def serverCustomer(customer):
    customer.createStub()
    customer.executeEvents()
    
    result = customer.output()
    with open(output_file,"a") as fh:
        fh.write(str(result) + "\n")

# Process input json file
# 1. start the branch processes 
# 2. start customer processes 

# argument is a load json file 
def running(input):
    # list of customer objects 
    customers = []
    # list of customer processes 
    customer_processes = []
    # list of branch objects 
    branches = []
    # list of branch processes
    branch_processes = []
    # list of branches Ids
    branchIds = []
        
    # get the list of branch Ids
    for elem in input:
        if elem["type"] == "branch":
            branchIds.append(elem["id"])
    
    # get the list of branch objects
    for elem in input:
        if elem["type"] == "branch":
            branch = Branch(elem["id"],elem["balance"],branchIds)
            branches.append(branch)
    print(branches)
    
    # start branch server processes
    for branch in branches:
        branch_process = multiprocessing.Process(target=serverBranch,args=(branch,))
        branch_processes.append(branch_process)
        branch_process.start()
        
    # allow the server processes to be created
    sleep(3)
    
    # get the list of customers
    for elem in input:
        if elem["type"] == "customer":
            customer = Customer(elem["id"],elem["events"])
            customers.append(customer)
    
    # start processing customer events 
    for customer in customers:
        customer_process = multiprocessing.Process(target=serverCustomer,args=(customer,))
        customer_processes.append(customer_process)
        customer_process.start()
        
    # Wait for customer processes to complete 
    for customer_process in customer_processes:
        customer_process.join()
        
    # terminate branch server processes 
    for branch_process in branch_processes:
        branch_process.terminate()
        
if __name__ == "__main__":
    if len(sys.argv) != 2: 
        print("Usage: testmain.py input_json_file")
        exit(-1)
    
    input_file = sys.argv[1]
    
    # create the output file so later processes can append 
    open(output_file,"w").close()
    
    input_json = json.load(open(input_file))
    
    running(input_json)
    