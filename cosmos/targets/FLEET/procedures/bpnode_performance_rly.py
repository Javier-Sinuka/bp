##******************************************************************************
##
## Performance test of BPNode in Relay Mode
##      
##******************************************************************************

import os
from datetime import datetime

# Setting Script Runner line delay
set_line_delay(0.000)

load_utility("FLEET/procedures/bpnode_initialization.py")
load_utility("FLEET/procedures/load_target_table.py")
load_utility("FLEET/procedures/bundles_send.py")

target = "DTNFSW-1"

# Start event logging
curtime = str(datetime.now()).replace('-','').replace(':','').replace(' ','_')[:-7]
eventlog_filename = "/eventlogs/eventlog_" + target + "_" + curtime + ".txt"
print ("Eventlog filename: ", eventlog_filename)
stash_set('eventlog', eventlog_filename)
id_1 = script_run(f"{target}/procedures/write_event_log.py")
wait(2)

##------------------------------------------------------------------------------
## BPNode Initialization
##------------------------------------------------------------------------------

bpnode_initialization(target)

print("Resetting all counters")
cmd(f"{target} BPNODE_CMD_RESET_ALL_COUNTERS")    
wait(1)

print("Setting host time to Invalid")
cmd(f"{target} CFE_TIME_CMD_SET_STATE with CLOCK_STATE 'INVALID'") 
wait(1)

##------------------------------------------------------------------------------
## Test Setup
##------------------------------------------------------------------------------

print("Selecting how many contact loops to execute")
number_of_contact_loops = ask("Choose number of contact loops: ")

print("Selecting the bundle payload size")
payload_size = ask("Choose payload size (in bytes): ")

print("Selecting how many bundles to send for each contact")
bundles_to_send = ask("Enter number of bundles to send (multiple of 50): ")
total_send_loops = bundles_to_send / 50

print("Selecting the IP address to send to")
send_to_ip = ask("Enter IP address to send to (X.X.X.X): ")

print("Selecting the Data Sender rate limit")
rate_limit_sender = ask("Choose Data Sender initial rate limit (in Mbps): ")

print("Selecting whether to increase the Data Sender rate limit each loop")
rate_limit_sender_increase = ask("Choose whether Data Sender send rate should increase (Y/N): ")

print("Selecting the initial BPNode egress rate limit")
rate_limit_bpnode = ask("Choose BPNode ingfress/egress rate limit in Mbps (50, 100, 150, 200, 300, 1000, 2000, or 5000): ")

## Load contact table
if rate_limit_bpnode == 50:
    load_target_table('/cf/con_perf_50mb.tbl', target)
elif rate_limit_bpnode == 100:
    load_target_table('/cf/con_perf_100mb.tbl', target)
elif rate_limit_bpnode == 150:
    load_target_table('/cf/con_perf_150mb.tbl', target)
elif rate_limit_bpnode == 200:
    load_target_table('/cf/con_perf_200mb.tbl', target)
elif rate_limit_bpnode == 300:
    load_target_table('/cf/con_perf_300mb.tbl', target)
elif rate_limit_bpnode == 1000:
    load_target_table('/cf/con_perf_1gb.tbl', target)
elif rate_limit_bpnode == 2000:
    load_target_table('/cf/con_perf_2gb.tbl', target)
elif rate_limit_bpnode == 5000:
    load_target_table('/cf/con_perf_5gb.tbl', target)
else:
    prompt("Incorrect rate limit, start over")

##------------------------------------------------------------------------------
## Test Start
##------------------------------------------------------------------------------

loop = 0

Start_Time = datetime.now()
print(f"Test Start Time = {Start_Time}")

while loop < number_of_contact_loops:

    loop = loop + 1

    print("Resetting all counters")
    cmd(f"{target} BPNODE_CMD_RESET_ALL_COUNTERS")    
    wait(1)

    ##------------------------------------------------------------------------------
    ## Ingress -> Storage Execution
    ##------------------------------------------------------------------------------

    print("Starting Contact Loop", loop)

    ## Setup and start contact
    cmd(f"{target} BPNODE_CMD_CONTACT_SETUP with CONTACT_ID 0")
    wait(1)
    cmd(f"{target} BPNODE_CMD_CONTACT_SETUP with CONTACT_ID 1")
    wait(1)
    cmd(f"{target} BPNODE_CMD_CONTACT_START with CONTACT_ID 0")
    wait(10)
    
    print("Sending bundles to the DTN Node")
    bundles_send(103, 1, payload_size, 86400, total_send_loops, send_to_ip, 4556, rate_limit_sender)
    wait(30)
    
    ## Print counter values
    RLY_BUNDLE_COUNT_RECEIVED = tlm(f"{target} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_RECEIVED")
    print("Relay Node Bundles Received:", RLY_BUNDLE_COUNT_RECEIVED)
    RLY_BUNDLE_COUNT_STORED = tlm(f"{target} BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED")
    print("Relay Node Bundles Stored:", RLY_BUNDLE_COUNT_STORED)
    RLY_BUNDLE_COUNT_FORWARDED = tlm(f"{target} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_FORWARDED")
    print("Relay Node Bundles Forwarded:", RLY_BUNDLE_COUNT_FORWARDED)

    cmd(f"{target} BPNODE_CMD_CONTACT_STOP with CONTACT_ID 0")
    wait(10)

    ##------------------------------------------------------------------------------
    ## Storage -> Egress Execution
    ##------------------------------------------------------------------------------

    prompt("Start a tcpdump capture on the receiving EC2 instance of udp packets on port 4558 before proceeding")

    ## Start Contact 1
    cmd(f"{target} BPNODE_CMD_CONTACT_START with CONTACT_ID 1")
    wait(10)
    
    ## Wait for all stored bundles to have been egressed
    wait_check(f"{target} BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED == 0", 600)
    wait(10)

    prompt("Stop the tcpdump capture on the receiving EC2 instance and collect arrival times before proceeding")

    ## Print counter values
    RLY_BUNDLE_COUNT_RECEIVED = tlm(f"{target} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_RECEIVED")
    print("Relay Node Bundles Received:", RLY_BUNDLE_COUNT_RECEIVED)
    RLY_BUNDLE_COUNT_STORED = tlm(f"{target} BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED")
    print("Relay Node Bundles Stored:", RLY_BUNDLE_COUNT_STORED)
    RLY_BUNDLE_COUNT_FORWARDED = tlm(f"{target} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_FORWARDED")
    print("Relay Node Bundles Forwarded:", RLY_BUNDLE_COUNT_FORWARDED)

    ##------------------------------------------------------------------------------
    ## Ingress -> Egress Execution
    ##------------------------------------------------------------------------------

    print("Resetting all counters")
    cmd(f"{target} BPNODE_CMD_RESET_ALL_COUNTERS")    
    wait(5)

    cmd(f"{target} BPNODE_CMD_CONTACT_START with CONTACT_ID 0")
    wait(10)

    prompt("Start a tcpdump capture on the receiving EC2 instance of udp packets on port 4558 before proceeding")

    print("Sending bundles to the DTN Node")
    bundles_send(103, 1, payload_size, 86400, total_send_loops, send_to_ip, 4556, rate_limit_sender)
    wait(60)

    prompt("Stop the tcpdump capture on the receiving EC2 instance and collect arrival times before proceeding")

    ## Stop and tear down all Contacts
    cmd(f"{target} BPNODE_CMD_CONTACT_STOP with CONTACT_ID 0")
    wait(1)
    cmd(f"{target} BPNODE_CMD_CONTACT_TEARDOWN with CONTACT_ID 0")
    wait(1)
    cmd(f"{target} BPNODE_CMD_CONTACT_STOP with CONTACT_ID 1")
    wait(1)
    cmd(f"{target} BPNODE_CMD_CONTACT_TEARDOWN with CONTACT_ID 1")
    wait(10)

    ## Print counter values
    RLY_BUNDLE_COUNT_RECEIVED = tlm(f"{target} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_RECEIVED")
    print("Relay Node Bundles Received:", RLY_BUNDLE_COUNT_RECEIVED)
    RLY_BUNDLE_COUNT_STORED = tlm(f"{target} BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED")
    print("Relay Node Bundles Stored:", RLY_BUNDLE_COUNT_STORED)
    RLY_BUNDLE_COUNT_FORWARDED = tlm(f"{target} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_FORWARDED")
    print("Relay Node Bundles Forwarded:", RLY_BUNDLE_COUNT_FORWARDED)

    print("Stopping Contact Loop", loop)
    
    if rate_limit_sender_increase == "Y":
        rate_limit_sender = rate_limit_sender + 10

End_Time = datetime.now()
print(f"Test End Time = {End_Time}")

##-------------------------------------------------------------------------------------------------------------------
## Test Closeout
##-------------------------------------------------------------------------------------------------------------------

print("Resetting all counters")
cmd(f"{target} BPNODE_CMD_RESET_ALL_COUNTERS")    
wait(1)

print("Setting host time to Valid")
cmd(f"{target} CFE_TIME_CMD_SET_STATE with CLOCK_STATE 'VALID'") 
wait(1)

# Stop running scripts
running_script_stop(id_1)
