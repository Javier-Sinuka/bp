##*******************************************************************************************************************
##
## Subsystem Test Case - Storage of Custody Signals
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

## Initialize requirement status
rqmnt_status = {
    "DTN.5.00420":"U",
    "DTN.5.00450":"U",
}

##-------------------------------------------------------------------------------------------------------------------
## 2 TEST CONFIGURATION
##-------------------------------------------------------------------------------------------------------------------

##-------------------------------------------------------------------------------------------------------------------
## 2.1 Lunar User Node Configuration
##-------------------------------------------------------------------------------------------------------------------

## Load MIB PN table to set node number to 101
load_target_table('/cf/pn_lunar.tbl', target_1)

## Load ADU Proxy table
load_target_table('/cf/adu_lunar.tbl', target_1) 

## Load Channel table
load_target_table('/cf/cha_lunar_ct.tbl', target_1)

## Load CF configuration table
cmd(f"{target_1} CF_CMD_DISABLE_ENGINE")
load_target_table('/cf/cf_lunar.tbl', target_1)
cmd(f"{target_1} CF_CMD_ENABLE_ENGINE")

## Start Channel 0 and 1
cmd(f"{target_1} BPNODE_CMD_ADD_APPLICATION with CHAN_ID 0")
wait(1)
cmd(f"{target_1} BPNODE_CMD_START_APPLICATION with CHAN_ID 0")
wait(5)

## Load Lunar User Node Contact table
load_target_table('/cf/con_lunar.tbl', target_1) 

## Set up and start Contacts 0 and 1 on the Lunar User Node
cmd(f"{target_1} BPNODE_CMD_CONTACT_SETUP with CONTACT_ID 0")
wait(1)
cmd(f"{target_1} BPNODE_CMD_CONTACT_SETUP with CONTACT_ID 1")
wait(1)
cmd(f"{target_1} BPNODE_CMD_CONTACT_START with CONTACT_ID 0")
wait(1)
cmd(f"{target_1} BPNODE_CMD_CONTACT_START with CONTACT_ID 1")
wait(1)

##-------------------------------------------------------------------------------------------------------------------
## 2.2 Relay Node Setup for the contact
##-------------------------------------------------------------------------------------------------------------------

## Load MIB PN table modified to set node number to 102
load_target_table('/cf/pn_relay.tbl', target_2)

## Load Contact table
load_target_table('/cf/con_relay_max.tbl', target_2) 

## Set up all Contacts and start Contacts 0 and 1
cmd(f"{target_2} BPNODE_CMD_CONTACT_SETUP with CONTACT_ID 0")
wait(1)
cmd(f"{target_2} BPNODE_CMD_CONTACT_SETUP with CONTACT_ID 1")
wait(1)
cmd(f"{target_2} BPNODE_CMD_CONTACT_SETUP with CONTACT_ID 2")
wait(1)
cmd(f"{target_2} BPNODE_CMD_CONTACT_START with CONTACT_ID 0")
wait(1)
cmd(f"{target_2} BPNODE_CMD_CONTACT_START with CONTACT_ID 1")
wait(10)

##-------------------------------------------------------------------------------------------------------------------
## 3. Create and Store Custody Signals
##-------------------------------------------------------------------------------------------------------------------

## Start a Lunar User data transfer (Lunar User CF transmitting a file)
CFDP_PDU_count_1 = 376
cmd(f"{target_1} CF_CMD_TX_FILE with CFDP_CLASS 'CLASS_1', KEEP 1, CHAN_NUM 0, DEST_ID 1, SRC_FILENAME '/cf/Jojo2.jpg', DST_FILENAME '/cf/Jojo2_in_space.jpg'")
wait(30)

## Print counter values
LUNAR_BUNDLE_COUNT_RECEIVED = tlm(f"{target_1} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_RECEIVED")
print("Lunar User Node Bundles Received:", LUNAR_BUNDLE_COUNT_RECEIVED)
LUNAR_ADU_COUNT_RECEIVED = tlm(f"{target_1} BPNODE_NODE_MIB_COUNTERS_HK ADU_COUNT_RECEIVED")
print("Lunar User Node ADUs Received:", LUNAR_ADU_COUNT_RECEIVED)
LUNAR_BUNDLE_COUNT_GENERATED_ACCEPTED = tlm(f"{target_1} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_GENERATED_ACCEPTED")
print("Lunar User Node Bundles Generated:", LUNAR_BUNDLE_COUNT_GENERATED_ACCEPTED)
LUNAR_BUNDLE_COUNT_STORED = tlm(f"{target_1} BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED")
print("Lunar User Node Bundles Stored:", LUNAR_BUNDLE_COUNT_STORED)
LUNAR_BUNDLE_COUNT_CCS_RECEIVED = tlm(f"{target_1} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_CCS_RECEIVED")
print("Lunar User Node CCS Received:", LUNAR_BUNDLE_COUNT_CCS_RECEIVED)
LUNAR_BUNDLE_COUNT_RECEIVED_CUSTODY_SIGNAL = tlm(f"{target_1} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_RECEIVED_CUSTODY_SIGNAL")
print("Lunar User Node Bundles for which Custody Signal has been Received:", LUNAR_BUNDLE_COUNT_RECEIVED_CUSTODY_SIGNAL)
LUNAR_BUNDLE_COUNT_IN_CUSTODY = tlm(f"{target_1} BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_IN_CUSTODY")
print("Lunar User Node Bundles In Custody:", LUNAR_BUNDLE_COUNT_IN_CUSTODY)
LUNAR_BUNDLE_COUNT_CUSTODY_TRANSFERRED = tlm(f"{target_1} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_CUSTODY_TRANSFERRED")
print("Lunar User Node Bundles for which Custody has been Transferred to the next Custodian Node:", LUNAR_BUNDLE_COUNT_CUSTODY_TRANSFERRED)
LUNAR_BUNDLE_COUNT_FORWARDED = tlm(f"{target_1} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_FORWARDED")
print("Lunar User Node Bundles Forwarded:", LUNAR_BUNDLE_COUNT_FORWARDED)

RELAY_BUNDLE_COUNT_RECEIVED = tlm(f"{target_2} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_RECEIVED")
print("Relay Node Bundles Received:", RELAY_BUNDLE_COUNT_RECEIVED)
RELAY_BUNDLE_COUNT_STORED = tlm(f"{target_2} BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED")
print("Relay Node Bundles Stored:", RELAY_BUNDLE_COUNT_STORED)
RELAY_BUNDLE_COUNT_CUSTODY_REQUEST = tlm(f"{target_2} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_CUSTODY_REQUEST")
print("Relay Node Bundles that are Requesting Custody:", RELAY_BUNDLE_COUNT_CUSTODY_REQUEST)
RELAY_BUNDLE_COUNT_IN_CUSTODY = tlm(f"{target_2} BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_IN_CUSTODY")
print("Relay Node Bundles In Custody:", RELAY_BUNDLE_COUNT_IN_CUSTODY)
RELAY_BUNDLE_COUNT_GENERATED_CCS = tlm(f"{target_2} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_GENERATED_CCS")
print("Relay Node Generated CCS:", RELAY_BUNDLE_COUNT_GENERATED_CCS)
RELAY_BUNDLE_COUNT_GENERATED_CUSTODY_SIGNAL = tlm(f"{target_2} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_GENERATED_CUSTODY_SIGNAL")
print("Relay Node Bundles for which Custody Signal has been Generated:", RELAY_BUNDLE_COUNT_GENERATED_CUSTODY_SIGNAL)
RELAY_BUNDLE_COUNT_FORWARDED = tlm(f"{target_2} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_FORWARDED")
print("Relay Node Bundles Forwarded:", RELAY_BUNDLE_COUNT_FORWARDED)

## Verify successful custody signal storage on the Relay Node
assert LUNAR_BUNDLE_COUNT_RECEIVED == 0
assert LUNAR_ADU_COUNT_RECEIVED == CFDP_PDU_count_1
assert LUNAR_BUNDLE_COUNT_GENERATED_ACCEPTED == CFDP_PDU_count_1
assert LUNAR_BUNDLE_COUNT_STORED == CFDP_PDU_count_1
assert LUNAR_BUNDLE_COUNT_CCS_RECEIVED == 0
assert LUNAR_BUNDLE_COUNT_RECEIVED_CUSTODY_SIGNAL == 0
assert LUNAR_BUNDLE_COUNT_IN_CUSTODY == CFDP_PDU_count_1
assert LUNAR_BUNDLE_COUNT_CUSTODY_TRANSFERRED == 0
assert LUNAR_BUNDLE_COUNT_FORWARDED >= CFDP_PDU_count_1
assert RELAY_BUNDLE_COUNT_RECEIVED >= CFDP_PDU_count_1
assert RELAY_BUNDLE_COUNT_STORED >= CFDP_PDU_count_1
assert RELAY_BUNDLE_COUNT_CUSTODY_REQUEST >= CFDP_PDU_count_1
assert RELAY_BUNDLE_COUNT_IN_CUSTODY == CFDP_PDU_count_1
assert RELAY_BUNDLE_COUNT_GENERATED_CCS > 0
assert RELAY_BUNDLE_COUNT_GENERATED_CUSTODY_SIGNAL == CFDP_PDU_count_1
assert RELAY_BUNDLE_COUNT_FORWARDED >= CFDP_PDU_count_1

##-------------------------------------------------------------------------------------------------------------------
## 4. Forward Stored Custody Signals
##-------------------------------------------------------------------------------------------------------------------

## Start Contact 2 on the Relay Node to allow Custody Signals to be forwarded from storage
cmd(f"{target_2} BPNODE_CMD_CONTACT_START with CONTACT_ID 2")
wait(30)

## Print counter values
LUNAR_BUNDLE_COUNT_RECEIVED = tlm(f"{target_1} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_RECEIVED")
print("Lunar User Node Bundles Received:", LUNAR_BUNDLE_COUNT_RECEIVED)
LUNAR_BUNDLE_COUNT_STORED = tlm(f"{target_1} BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED")
print("Lunar User Node Bundles Stored:", LUNAR_BUNDLE_COUNT_STORED)
LUNAR_BUNDLE_COUNT_CCS_RECEIVED = tlm(f"{target_1} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_CCS_RECEIVED")
print("Lunar User Node CCS Received:", LUNAR_BUNDLE_COUNT_CCS_RECEIVED)
LUNAR_BUNDLE_COUNT_RECEIVED_CUSTODY_SIGNAL = tlm(f"{target_1} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_RECEIVED_CUSTODY_SIGNAL")
print("Lunar User Node Bundles for which Custody Signal has been Received:", LUNAR_BUNDLE_COUNT_RECEIVED_CUSTODY_SIGNAL)
LUNAR_BUNDLE_COUNT_IN_CUSTODY = tlm(f"{target_1} BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_IN_CUSTODY")
print("Lunar User Node Bundles In Custody:", LUNAR_BUNDLE_COUNT_IN_CUSTODY)
LUNAR_BUNDLE_COUNT_CUSTODY_TRANSFERRED = tlm(f"{target_1} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_CUSTODY_TRANSFERRED")
print("Lunar User Node Bundles for which Custody has been Transferred to the next Custodian Node:", LUNAR_BUNDLE_COUNT_CUSTODY_TRANSFERRED)
LUNAR_BUNDLE_COUNT_FORWARDED = tlm(f"{target_1} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_FORWARDED")
print("Lunar User Node Bundles Forwarded:", LUNAR_BUNDLE_COUNT_FORWARDED)

RELAY_BUNDLE_COUNT_RECEIVED = tlm(f"{target_2} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_RECEIVED")
print("Relay Node Bundles Received:", RELAY_BUNDLE_COUNT_RECEIVED)
RELAY_BUNDLE_COUNT_STORED = tlm(f"{target_2} BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED")
print("Relay Node Bundles Stored:", RELAY_BUNDLE_COUNT_STORED)
RELAY_BUNDLE_COUNT_CUSTODY_REQUEST = tlm(f"{target_2} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_CUSTODY_REQUEST")
print("Relay Node Bundles that are Requesting Custody:", RELAY_BUNDLE_COUNT_CUSTODY_REQUEST)
RELAY_BUNDLE_COUNT_IN_CUSTODY = tlm(f"{target_2} BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_IN_CUSTODY")
print("Relay Node Bundles In Custody:", RELAY_BUNDLE_COUNT_IN_CUSTODY)
RELAY_BUNDLE_COUNT_GENERATED_CCS = tlm(f"{target_2} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_GENERATED_CCS")
print("Relay Node Generated CCS:", RELAY_BUNDLE_COUNT_GENERATED_CCS)
RELAY_BUNDLE_COUNT_GENERATED_CUSTODY_SIGNAL = tlm(f"{target_2} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_GENERATED_CUSTODY_SIGNAL")
print("Relay Node Bundles for which Custody Signal has been Generated:", RELAY_BUNDLE_COUNT_GENERATED_CUSTODY_SIGNAL)
RELAY_BUNDLE_COUNT_FORWARDED = tlm(f"{target_2} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_FORWARDED")
print("Relay Node Bundles Forwarded:", RELAY_BUNDLE_COUNT_FORWARDED)

## Verify successful custody signal forwarding
assert LUNAR_BUNDLE_COUNT_RECEIVED > 0
assert LUNAR_BUNDLE_COUNT_STORED == 0
assert LUNAR_BUNDLE_COUNT_CCS_RECEIVED > 0
assert LUNAR_BUNDLE_COUNT_RECEIVED_CUSTODY_SIGNAL == CFDP_PDU_count_1
assert LUNAR_BUNDLE_COUNT_IN_CUSTODY == 0
assert LUNAR_BUNDLE_COUNT_CUSTODY_TRANSFERRED == CFDP_PDU_count_1
assert LUNAR_BUNDLE_COUNT_FORWARDED >= CFDP_PDU_count_1
assert RELAY_BUNDLE_COUNT_RECEIVED > 0
assert RELAY_BUNDLE_COUNT_STORED >= CFDP_PDU_count_1
assert RELAY_BUNDLE_COUNT_CUSTODY_REQUEST >= CFDP_PDU_count_1
assert RELAY_BUNDLE_COUNT_IN_CUSTODY >= CFDP_PDU_count_1
assert RELAY_BUNDLE_COUNT_GENERATED_CCS > 0
assert RELAY_BUNDLE_COUNT_GENERATED_CUSTODY_SIGNAL >= CFDP_PDU_count_1
assert RELAY_BUNDLE_COUNT_FORWARDED > CFDP_PDU_count_1

## Verify requirements
rqmnt_status["DTN.5.00420"] = "P"
rqmnt_status["DTN.5.00450"] = "P"

## Stop Contacts on both nodes
cmd(f"{target_1} BPNODE_CMD_CONTACT_STOP with CONTACT_ID 0")
wait(1)
cmd(f"{target_1} BPNODE_CMD_CONTACT_STOP with CONTACT_ID 1")
wait(1)
cmd(f"{target_2} BPNODE_CMD_CONTACT_STOP with CONTACT_ID 0")
wait(1)
cmd(f"{target_2} BPNODE_CMD_CONTACT_STOP with CONTACT_ID 1")
wait(1)
cmd(f"{target_2} BPNODE_CMD_CONTACT_STOP with CONTACT_ID 2")
wait(10)

##-------------------------------------------------------------------------------------------------------------------
## 5. Test Cleanup
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
cmd(f"{target_2} BPNODE_CMD_CONTACT_TEARDOWN with CONTACT_ID 2")
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

cmd(f"{target_1} CF_CMD_RESET")
wait(10)

# Stop running scripts
running_script_stop(id_1)
running_script_stop(id_2)

# Print Requirement Status
for key, value in rqmnt_status.items():
    print(f"***    {key}: {value}")
