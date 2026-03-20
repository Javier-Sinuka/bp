##*******************************************************************************************************************
##
## Subsystem Test Case - Maximum Storage Exceeded
##      
##*******************************************************************************************************************
import os
from datetime import datetime

global rqmnt_status

# Setting Script Runner line delay
set_line_delay(0.000)

##-------------------------------------------------------------------------------------------------------------------
## 1. Test Setup
##-------------------------------------------------------------------------------------------------------------------

load_utility("FLEET/procedures/bpnode_initialization.py")
load_utility("FLEET/procedures/load_target_table.py")
load_utility("FLEET/procedures/bundles_send.py")
load_utility("FLEET/procedures/bundles_send_with_delay.py")

target_1 = "DTNFSW-1"
target_2 = "DTNFSW-2"

## Start event logging
curtime = str(datetime.now()).replace('-','').replace(':','').replace(' ','_')[:-7]

eventlog_filename_1 = "/eventlogs/eventlog_" + target_1 + "_" + curtime + ".txt"
print ("Eventlog filename: ", eventlog_filename_1)
stash_set('eventlog', eventlog_filename_1)
id_1 = script_run(f"{target_1}/procedures/write_event_log.py")
wait(2)

eventlog_filename_2 = "/eventlogs/eventlog_" + target_2 + "_" + curtime + ".txt"
print ("Eventlog filename: ", eventlog_filename_2)
stash_set('eventlog', eventlog_filename_2)
id_2 = script_run(f"{target_2}/procedures/write_event_log.py")
wait(2)

bpnode_initialization(target_1)
bpnode_initialization(target_2)

## Enter IP adress information
lunar_ip = ask("Enter Lunar User Node IP Address: ")

# Initialize requirement status
rqmnt_status = {
    #"DTN.5.00050":"U",    DR DTNN-1478
    "DTN.5.00210":"U",
    "DTN.6.04220":"U",
    "DTN.6.04300":"U",
    "DTN.6.04312":"U",
    "DTN.6.25020":"U",
}

##-------------------------------------------------------------------------------------------------------------------
## 2.1 Lunar User Node Setup for receiving bundles
##-------------------------------------------------------------------------------------------------------------------

## Reset all counters
cmd(f"{target_1} BPNODE_CMD_RESET_ALL_COUNTERS")    
wait(1)

## Verify Lunar User Node Storage Size
LUNAR_BUNDLE_AGENT_AVAILABLE_STORAGE = tlm(f"{target_1} BPNODE_NODE_MIB_REPORTS_HK BUNDLE_AGENT_AVAILABLE_STORAGE")
print("Lunar User Node Available Storage:", LUNAR_BUNDLE_AGENT_AVAILABLE_STORAGE)
LUNAR_KBYTES_COUNT_STORAGE_AVAILABLE = tlm(f"{target_1} BPNODE_NODE_MIB_REPORTS_HK KBYTES_COUNT_STORAGE_AVAILABLE")
print("Lunar User Node kbyte Storage Available:", LUNAR_KBYTES_COUNT_STORAGE_AVAILABLE)

assert LUNAR_BUNDLE_AGENT_AVAILABLE_STORAGE == 8000000
assert LUNAR_KBYTES_COUNT_STORAGE_AVAILABLE == 8000000

## Load MIB PN table to set node number to 101
load_target_table('/cf/pn_lunar.tbl', target_1)

## Load Channel table
load_target_table('/cf/cha_lunar.tbl', target_1) 

## Load Contact 0 table for receiving bundles on port 4556
load_target_table('/cf/con_lunar_max.tbl', target_1) 

## Restart Channel 0
cmd(f"{target_1} BPNODE_CMD_ADD_APPLICATION with CHAN_ID 0")
wait(1)
cmd(f"{target_1} BPNODE_CMD_START_APPLICATION with CHAN_ID 0")
wait(1)

## Set up and start Contact 1
cmd(f"{target_1} BPNODE_CMD_CONTACT_SETUP with CONTACT_ID 1")
wait(1)
cmd(f"{target_1} BPNODE_CMD_CONTACT_START with CONTACT_ID 1")
wait(1)

##-------------------------------------------------------------------------------------------------------------------
## 2.2 Send bundles to max out Lunar User Node storage
##-------------------------------------------------------------------------------------------------------------------

## Send 500,000 bundles to the Lunar User Node
bundles_send(103, 1, 8000, 3600, 18000, lunar_ip, 4500, 90)
wait(30)

## Print counter values
LUNAR_BUNDLE_COUNT_RECEIVED_1 = tlm(f"{target_1} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_RECEIVED")
print("Lunar User Node Bundles Received:", LUNAR_BUNDLE_COUNT_RECEIVED_1)
LUNAR_BUNDLE_COUNT_STORED_1 = tlm(f"{target_1} BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED")
print("Lunar User Node Bundles Stored:", LUNAR_BUNDLE_COUNT_STORED_1)
LUNAR_KBYTES_COUNT_STORAGE_AVAILABLE = tlm(f"{target_1} BPNODE_NODE_MIB_REPORTS_HK KBYTES_COUNT_STORAGE_AVAILABLE")
print("Lunar User Node kbyte Storage Available:", LUNAR_KBYTES_COUNT_STORAGE_AVAILABLE)
LUNAR_BUNDLE_COUNT_DELETED_1 = tlm(f"{target_1} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_DELETED")
print("Lunar User Node Bundles Deleted:", LUNAR_BUNDLE_COUNT_DELETED_1)
LUNAR_BUNDLE_COUNT_DELETED_NO_STORAGE_1 = tlm(f"{target_1} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_DELETED_NO_STORAGE")
print("Lunar User Node Bundles Deleted No Storage:", LUNAR_BUNDLE_COUNT_DELETED_NO_STORAGE_1)

## Verify storage exceeded
assert LUNAR_KBYTES_COUNT_STORAGE_AVAILABLE < 1000
assert LUNAR_BUNDLE_COUNT_DELETED_1 > 0
assert LUNAR_BUNDLE_COUNT_DELETED_1 == LUNAR_BUNDLE_COUNT_DELETED_NO_STORAGE_1
assert LUNAR_BUNDLE_COUNT_STORED_1 + LUNAR_BUNDLE_COUNT_DELETED_1 == 900000
#assert LUNAR_BUNDLE_COUNT_STORED_1 == LUNAR_BUNDLE_COUNT_RECEIVED_1            DR DTNN-1478

## Confirm that the Lunar User Node has maxed out storage
wait_check(f"{target_1} CFE_EVS_LONG_EVENT_MSG PACKET_ID_APP_NAME == 'BPNODE'", 1200)
wait_check(f"{target_1} CFE_EVS_LONG_EVENT_MSG PACKET_ID_EVENT_ID == 611", 1200)
wait_check(f"{target_1} CFE_EVS_LONG_EVENT_MSG PACKET_ID_EVENT_TYPE == 'ERROR'", 6)

# Send 100 additional bundles one by one
bundles_send_with_delay(103, 1, 8000, 3600, 2, lunar_ip, 4500, 50)
wait(5)

# Confirm that the Lunar User Node has maxed out storage
wait_check(f"{target_1} CFE_EVS_LONG_EVENT_MSG PACKET_ID_APP_NAME == 'BPNODE'", 1200)
wait_check(f"{target_1} CFE_EVS_LONG_EVENT_MSG PACKET_ID_EVENT_ID == 756", 1200)
wait_check(f"{target_1} CFE_EVS_LONG_EVENT_MSG PACKET_ID_EVENT_TYPE == 'ERROR'", 6)

## Print counter values
LUNAR_BUNDLE_COUNT_RECEIVED_2 = tlm(f"{target_1} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_RECEIVED")
print("Lunar User Node Bundles Received:", LUNAR_BUNDLE_COUNT_RECEIVED_2)
LUNAR_BUNDLE_COUNT_STORED_2 = tlm(f"{target_1} BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED")
print("Lunar User Node Bundles Stored:", LUNAR_BUNDLE_COUNT_STORED_2)
LUNAR_KBYTES_COUNT_STORAGE_AVAILABLE = tlm(f"{target_1} BPNODE_NODE_MIB_REPORTS_HK KBYTES_COUNT_STORAGE_AVAILABLE")
print("Lunar User Node kbyte Storage Available:", LUNAR_KBYTES_COUNT_STORAGE_AVAILABLE)
LUNAR_BUNDLE_COUNT_DELETED_2 = tlm(f"{target_1} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_DELETED")
print("Lunar User Node Bundles Deleted:", LUNAR_BUNDLE_COUNT_DELETED_2)
LUNAR_BUNDLE_COUNT_DELETED_NO_STORAGE_2 = tlm(f"{target_1} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_DELETED_NO_STORAGE")
print("Lunar User Node Bundles Deleted No Storage:", LUNAR_BUNDLE_COUNT_DELETED_NO_STORAGE_2)

## Verify storage exceeded
assert LUNAR_BUNDLE_COUNT_RECEIVED_2 > LUNAR_BUNDLE_COUNT_RECEIVED_1
assert LUNAR_BUNDLE_COUNT_STORED_2 > LUNAR_BUNDLE_COUNT_STORED_1
assert LUNAR_KBYTES_COUNT_STORAGE_AVAILABLE < 10
assert LUNAR_BUNDLE_COUNT_DELETED_2 > LUNAR_BUNDLE_COUNT_DELETED_1
assert LUNAR_BUNDLE_COUNT_DELETED_2 == LUNAR_BUNDLE_COUNT_DELETED_NO_STORAGE_2
assert LUNAR_BUNDLE_COUNT_STORED_2 + LUNAR_BUNDLE_COUNT_DELETED_2 == 900100
#assert LUNAR_BUNDLE_COUNT_STORED_2 == LUNAR_BUNDLE_COUNT_RECEIVED_2            DR DTNN-1478

## The following section is commented out due to DR DTNN-1478

## Send 50 ADUs one by one
loop = 0

while loop < 50:
    loop = loop + 1
    cmd(f"{target_1} CFE_SB_CMD_SEND_SB_STATS")
    wait(2)
wait(5)

## Confirm that the Lunar User Node has maxed out storage
wait_check(f"{target_1} CFE_EVS_LONG_EVENT_MSG PACKET_ID_APP_NAME == 'BPNODE'", 1200)
wait_check(f"{target_1} CFE_EVS_LONG_EVENT_MSG PACKET_ID_EVENT_ID == 698", 1200)
wait_check(f"{target_1} CFE_EVS_LONG_EVENT_MSG PACKET_ID_EVENT_TYPE == 'ERROR'", 6)

## Verify requirements
rqmnt_status["DTN.6.04300"] = "P"

## Print counter values
LUNAR_ADU_COUNT_RECEIVED = tlm(f"{target_1} BPNODE_NODE_MIB_COUNTERS_HK ADU_COUNT_RECEIVED")
print("Lunar User Node ADUs Received:", LUNAR_ADU_COUNT_RECEIVED)
LUNAR_BUNDLE_COUNT_GENERATED_ACCEPTED = tlm(f"{target_1} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_GENERATED_ACCEPTED")
print("Lunar User Node ADUs Accepted:", LUNAR_BUNDLE_COUNT_GENERATED_ACCEPTED)
LUNAR_BUNDLE_COUNT_GENERATED_REJECTED = tlm(f"{target_1} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_GENERATED_REJECTED")
print("Lunar User Node ADUs Rejected:", LUNAR_BUNDLE_COUNT_GENERATED_REJECTED)

LUNAR_BUNDLE_COUNT_RECEIVED_3 = tlm(f"{target_1} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_RECEIVED")
print("Lunar User Node Bundles Received:", LUNAR_BUNDLE_COUNT_RECEIVED_3)
LUNAR_BUNDLE_COUNT_STORED_3 = tlm(f"{target_1} BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED")
print("Lunar User Node Bundles Stored:", LUNAR_BUNDLE_COUNT_STORED_3)
LUNAR_KBYTES_COUNT_STORAGE_AVAILABLE = tlm(f"{target_1} BPNODE_NODE_MIB_REPORTS_HK KBYTES_COUNT_STORAGE_AVAILABLE")
print("Lunar User Node kbyte Storage Available:", LUNAR_KBYTES_COUNT_STORAGE_AVAILABLE)
LUNAR_BUNDLE_COUNT_DELETED_3 = tlm(f"{target_1} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_DELETED")
print("Lunar User Node Bundles Deleted:", LUNAR_BUNDLE_COUNT_DELETED_3)
LUNAR_BUNDLE_COUNT_DELETED_NO_STORAGE_3 = tlm(f"{target_1} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_DELETED_NO_STORAGE")
print("Lunar User Node Bundles Deleted No Storage:", LUNAR_BUNDLE_COUNT_DELETED_NO_STORAGE_3)

## Verify storage exceeded
assert LUNAR_ADU_COUNT_RECEIVED == 50
assert LUNAR_BUNDLE_COUNT_GENERATED_ACCEPTED > 0
assert LUNAR_BUNDLE_COUNT_GENERATED_REJECTED > 0
assert LUNAR_BUNDLE_COUNT_GENERATED_ACCEPTED + LUNAR_BUNDLE_COUNT_GENERATED_REJECTED == LUNAR_ADU_COUNT_RECEIVED
assert LUNAR_BUNDLE_COUNT_RECEIVED_3 == LUNAR_BUNDLE_COUNT_RECEIVED_2
assert LUNAR_BUNDLE_COUNT_STORED_3 > LUNAR_BUNDLE_COUNT_STORED_2
#assert LUNAR_BUNDLE_COUNT_STORED_3 == LUNAR_BUNDLE_COUNT_RECEIVED_3            DR DTNN-1478
assert LUNAR_KBYTES_COUNT_STORAGE_AVAILABLE <= 5
assert LUNAR_BUNDLE_COUNT_DELETED_3 == LUNAR_BUNDLE_COUNT_DELETED_2
assert LUNAR_BUNDLE_COUNT_DELETED_3 == LUNAR_BUNDLE_COUNT_DELETED_NO_STORAGE_3
assert LUNAR_BUNDLE_COUNT_GENERATED_REJECTED + LUNAR_BUNDLE_COUNT_STORED_3 + LUNAR_BUNDLE_COUNT_DELETED_3 == 900150

## Verify requirements
#rqmnt_status["DTN.5.00050"] = "P"     DR DTNN-1478
rqmnt_status["DTN.5.00210"] = "P"
rqmnt_status["DTN.6.04312"] = "P"

##-------------------------------------------------------------------------------------------------------------------
## 2.3 Lunar User Node configuration for the contact
##-------------------------------------------------------------------------------------------------------------------

## Set up Contact 0
cmd(f"{target_1} BPNODE_CMD_CONTACT_SETUP with CONTACT_ID 0")
wait(1)

## Enable Debug event messages
cmd(f"{target_1} CFE_EVS_CMD_ENABLE_EVENT_TYPE with BIT_MASK 1")

##-------------------------------------------------------------------------------------------------------------------
## 2.4 Relay Node Setup for the contact
##-------------------------------------------------------------------------------------------------------------------

## Reset all counters
cmd(f"{target_2} BPNODE_CMD_RESET_ALL_COUNTERS")    
wait(1)

## Load MIB PN table modified to set node number to 102
load_target_table('/cf/pn_relay.tbl', target_2)

## Load Contact table
load_target_table('/cf/con_relay_max.tbl', target_2) 

## Set up Contacts 0 and 1
cmd(f"{target_2} BPNODE_CMD_CONTACT_SETUP with CONTACT_ID 0")
wait(1)
cmd(f"{target_2} BPNODE_CMD_CONTACT_SETUP with CONTACT_ID 1")
wait(1)
cmd(f"{target_2} BPNODE_CMD_CONTACT_SETUP with CONTACT_ID 2")
wait(1)

##-------------------------------------------------------------------------------------------------------------------
## 2.5 Execute the contact
##-------------------------------------------------------------------------------------------------------------------

## Start Contacts
cmd(f"{target_2} BPNODE_CMD_CONTACT_START with CONTACT_ID 0")
wait(1)
cmd(f"{target_2} BPNODE_CMD_CONTACT_START with CONTACT_ID 1")
wait(10)
cmd(f"{target_1} BPNODE_CMD_CONTACT_START with CONTACT_ID 0")
wait(10)

wait_check(f"{target_1} CFE_EVS_LONG_EVENT_MSG PACKET_ID_APP_NAME == 'BPNODE'", 120)
wait_check(f"{target_1} CFE_EVS_LONG_EVENT_MSG PACKET_ID_EVENT_ID == 622", 120)
wait_check(f"{target_1} CFE_EVS_LONG_EVENT_MSG PACKET_ID_EVENT_TYPE == 'DEBUG'", 6)

## Disable BPNode Debug event messages
cmd(f"{target_1} CFE_EVS_CMD_DISABLE_EVENT_TYPE with BIT_MASK 1")

## Wait for all bundles to have been received by the Relay Node
wait_check(f"{target_2} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_RECEIVED == {LUNAR_BUNDLE_COUNT_STORED_3}", 1200)

## Confirm that the Lunar User Node has maxed out memory pool usage
LUNAR_BYTES_MEM_HIGH_WATER = tlm(f"{target_1} BPNODE_STORAGE_HK BYTES_MEM_HIGH_WATER")
print("Lunar User Node Bytes Memory High Water:", LUNAR_BYTES_MEM_HIGH_WATER)
assert LUNAR_BYTES_MEM_HIGH_WATER > 15000000

## Verify requirements
rqmnt_status["DTN.6.25020"] = "P"

wait_check(f"{target_1} BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED == 0", 1200)
wait(10)

## Print counter values
LUNAR_BUNDLE_COUNT_STORED_4 = tlm(f"{target_1} BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED")
print("Lunar User Node Bundles Stored:", LUNAR_BUNDLE_COUNT_STORED_4)
LUNAR_KBYTES_COUNT_STORAGE_AVAILABLE = tlm(f"{target_1} BPNODE_NODE_MIB_REPORTS_HK KBYTES_COUNT_STORAGE_AVAILABLE")
print("Lunar User Node kbyte Storage Available:", LUNAR_KBYTES_COUNT_STORAGE_AVAILABLE)
LUNAR_BUNDLE_COUNT_FORWARDED_1 = tlm(f"{target_1} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_FORWARDED")
print("Lunar User Node Bundles Forwarded:", LUNAR_BUNDLE_COUNT_FORWARDED_1)

RELAY_BUNDLE_COUNT_RECEIVED_1 = tlm(f"{target_2} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_RECEIVED")
print("Relay Node Bundles Received:", RELAY_BUNDLE_COUNT_RECEIVED_1)

## Verify successful data transfer
assert LUNAR_KBYTES_COUNT_STORAGE_AVAILABLE == 8000000
assert RELAY_BUNDLE_COUNT_RECEIVED_1 == LUNAR_BUNDLE_COUNT_FORWARDED_1

## Verify requirements
rqmnt_status["DTN.6.04220"] = "P"

## Send another 1000 bundles to the Lunar User Node
bundles_send(103, 1, 1000, 3600, 20, lunar_ip, 4556, 90)
wait(10)

## Print counter values
LUNAR_BUNDLE_COUNT_RECEIVED_4 = tlm(f"{target_1} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_RECEIVED")
print("Lunar User Node Bundles Received:", LUNAR_BUNDLE_COUNT_RECEIVED_4)
LUNAR_BUNDLE_COUNT_STORED_5 = tlm(f"{target_1} BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED")
print("Lunar User Node Bundles Stored:", LUNAR_BUNDLE_COUNT_STORED_5)
LUNAR_BUNDLE_COUNT_FORWARDED_2 = tlm(f"{target_1} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_FORWARDED")
print("Lunar User Node Bundles Forwarded:", LUNAR_BUNDLE_COUNT_FORWARDED_2)

RELAY_BUNDLE_COUNT_RECEIVED_2 = tlm(f"{target_2} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_RECEIVED")
print("Relay Node Bundles Received:", RELAY_BUNDLE_COUNT_RECEIVED_2)

## Verify successful data transfer
assert LUNAR_BUNDLE_COUNT_STORED_5 == 0
assert RELAY_BUNDLE_COUNT_RECEIVED_2 == LUNAR_BUNDLE_COUNT_FORWARDED_2

## Stop Contacts on both nodes
cmd(f"{target_1} BPNODE_CMD_CONTACT_STOP with CONTACT_ID 0")
wait(1)
cmd(f"{target_1} BPNODE_CMD_CONTACT_STOP with CONTACT_ID 1")
wait(1)
cmd(f"{target_2} BPNODE_CMD_CONTACT_STOP with CONTACT_ID 0")
wait(1)
cmd(f"{target_2} BPNODE_CMD_CONTACT_STOP with CONTACT_ID 1")
wait(10)

##-------------------------------------------------------------------------------------------------------------------
## 3. Test Cleanup
##-------------------------------------------------------------------------------------------------------------------

## Tear down Contacts on both nodes
cmd(f"{target_1} BPNODE_CMD_CONTACT_TEARDOWN with CONTACT_ID 0")
wait(1)
cmd(f"{target_1} BPNODE_CMD_CONTACT_TEARDOWN with CONTACT_ID 1")
wait(1)
cmd(f"{target_2} BPNODE_CMD_CONTACT_TEARDOWN with CONTACT_ID 0")
wait(1)
cmd(f"{target_2} BPNODE_CMD_CONTACT_TEARDOWN with CONTACT_ID 1")
wait(1)

## Stop and remove Channel 0
cmd(f"{target_1} BPNODE_CMD_STOP_APPLICATION with CHAN_ID 0")
wait(1)
cmd(f"{target_1} BPNODE_CMD_REMOVE_APPLICATION with CHAN_ID 0")
wait(1)

## Reset all counters
cmd(f"{target_1} BPNODE_CMD_RESET_ALL_COUNTERS")
wait(1)
cmd(f"{target_2} BPNODE_CMD_RESET_ALL_COUNTERS")
wait(1)

# Stop running scripts
running_script_stop(id_1)
running_script_stop(id_2)

# Print Requirement Status
for key, value in rqmnt_status.items():
    print(f"***    {key}: {value}")
