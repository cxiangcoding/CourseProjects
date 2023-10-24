import json     #for processing json input 
import sys      #for argv 
import multiprocessing
import threading
from threading import currentThread
from time import sleep
from concurrent import futures

import grpc

import banking_pb2_grpc
from branch import Branch
from customer import Customer
import os
base_port = 50000
output_file = "output.json"

lock = threading.Lock()

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
    sleep(5*branch.id)
    '''
    # best attempt to group branch output from branch processes
    sleep(5 * branch.id)
    output_temp = json.load(open(output_file))
    output_temp.append({"pid":branch.id,"data":branch.get_events()})
    output = json.dumps(output_temp,indent=4)
    with open(output_file,"w") as result:
        result.write(output)
    '''
    print(f"branch {branch.id} events: {branch.get_events()}")
    
    lock.acquire()
    print(f"process {pid} is in locked state to write branch {branch.id} events")
    output_temp = json.load(open(output_file))
    output_temp.append({"pid":branch.id,"data":branch.get_events()})
    output = json.dumps(output_temp,indent=4)
    with open(output_file,"w") as result:
        result.write(output)
    lock.release()

    server.wait_for_termination()

# process client events 
def serverCustomer(customer):
    customer.createStub()
    customer.executeEvents()

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
        
    sleep(20)
    # Wait for customer processes to complete 
    for customer_process in customer_processes:
        customer_process.join()
    
    # Give some time for branches to complete outputing results 
    sleep(20)
    # terminate branch server processes 
    for branch_process in branch_processes:
        branch_process.terminate()
        
# format writing the result file
def formatoutput():
    result = json.load(open(output_file))
    events_dict = {}
    
    for pid in result:
        for event in pid["data"]:
            if event["id"] in events_dict.keys():
                events_dict[event["id"]].append(event)
            else:
                events_dict[event["id"]] = [event]
    
    # sort the events according to the clock 
    for event in events_dict:
        data = sorted(events_dict[event],key=lambda event : event["clock"])
        trimmed_data = []
        for item in data:
            trimmed_data.append({"clock":item["clock"],"name":item["name"]})
        result.append({"eventid":event, "data":trimmed_data})
    
    with open(output_file,"w") as output_result:
        output_result.write(json.dumps(result,indent=4))

if __name__ == "__main__":
    if len(sys.argv) != 2: 
        print("Usage: testmain.py input_json_file")
        exit(-1)
    
    input_file = sys.argv[1]
    
    # create the output file so later processes can append 
    with open(output_file,"w") as fd:
        fd.write("[]")
    
    input_json = json.load(open(input_file))
    
    running(input_json)
    
    # give some time for the processes to complete 
    sleep(10)
    
    formatoutput()
    
    