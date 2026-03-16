##*******************************************************************************************************************
##
## Subsystem Test Case - End to End (ETE) Transfer
##      
##*******************************************************************************************************************
import os
import time
from datetime import datetime

global rqmnt_status

# Setting Script Runner line delay
set_line_delay(0.000)

##-------------------------------------------------------------------------------------------------------------------
## 1 TEST SETUP
##-------------------------------------------------------------------------------------------------------------------

load_utility("FLEET/procedures/load_target_table.py")
load_utility("FLEET/procedures/reject_target_table.py")
load_utility("FLEET/procedures/bpnode_initialization.py")
load_utility("FLEET/procedures/invalid_bundles_send.py")
load_utility("FLEET/procedures/bad_bundles_send.py")
load_utility("FLEET/procedures/bundles_send.py")
load_utility("FLEET/procedures/unknown_blocks_send.py")

target_1 = "DTNFSW-1"
target_2 = "DTNFSW-2"
target_3 = "DTNFSW-3"
target_4 = "DTNFSW-4"
target_5 = "DTNFSW-5"

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

eventlog_filename_3 = "/eventlogs/eventlog_" + target_3 + "_" + curtime + ".txt"
print ("Eventlog filename: ", eventlog_filename_3)
stash_set('eventlog', eventlog_filename_3)
id_3 = script_run(f"{target_3}/procedures/write_event_log.py")
wait(2)

eventlog_filename_4 = "/eventlogs/eventlog_" + target_4 + "_" + curtime + ".txt"
print ("Eventlog filename: ", eventlog_filename_4)
stash_set('eventlog', eventlog_filename_4)
id_4 = script_run(f"{target_4}/procedures/write_event_log.py")
wait(2)

eventlog_filename_5 = "/eventlogs/eventlog_" + target_5 + "_" + curtime + ".txt"
print ("Eventlog filename: ", eventlog_filename_5)
stash_set('eventlog', eventlog_filename_5)
id_5 = script_run(f"{target_5}/procedures/write_event_log.py")
wait(2)

## Initialize each DTN Node
bpnode_initialization(target_1)
bpnode_initialization(target_2)
bpnode_initialization(target_3)
bpnode_initialization(target_4)
bpnode_initialization(target_5)

## Enter IP adress information
relay_ip = ask("Enter Relay Node IP Address: ")
nsn_ip = ask("Enter NSN Node IP Address: ")

## Start captures of IP traffic on the Relay Node
prompt("Start a Wireshark capture of bundles on the Relay Node (capture filter: 'udp port 4557', interface: 'ens5'")

## Start captures of IP traffic on the Ground Node
prompt("Start a Wireshark capture of bundles on the Ground Node (capture filter: 'udp port 4558', interface: 'ens5'")

## Start captures of IP traffic on the NSN Node
prompt("Start a Wireshark capture of bundles on the NSN Node (capture filter: 'udp port 4558', interface: 'ens5'")

## Initialize requirement status
rqmnt_status = {
    "DTN.5.00006":"U",
    "DTN.5.00007":"U",
    "DTN.5.00008":"U",
    "DTN.5.00009":"U",
    "DTN.5.00010":"U",
    "DTN.5.00012":"U",
    "DTN.5.00040":"U",
    "DTN.5.00060":"U",
    "DTN.5.00070":"U",
    "DTN.5.00090":"U",
    "DTN.5.00100":"U",
    "DTN.5.00110":"U",
    "DTN.5.00120":"U",
    "DTN.5.00150":"U",
    "DTN.5.00165":"U",
    "DTN.5.00170":"U",
    "DTN.5.00174":"U",
    "DTN.5.00180":"U",
    "DTN.5.00190":"U",
    "DTN.5.00192":"U",
    "DTN.5.00197":"U",
    "DTN.5.00200":"U",
    "DTN.5.00220":"U",
    "DTN.5.00250":"P",
    "DTN.5.00255":"U",
    "DTN.5.00260":"U",
    "DTN.5.00270":"U",
    "DTN.5.00275":"U",
    "DTN.5.00280":"U",
    "DTN.5.00290":"U",
    "DTN.5.00300":"U",
    "DTN.5.00320":"U",
    "DTN.5.00330":"U",
    "DTN.5.00370":"U",
    "DTN.5.00660":"U",
    "DTN.5.00670":"U",
    "DTN.5.00680":"U",
    "DTN.5.00685":"I",
    "DTN.5.00690":"U",
    "DTN.5.00692":"U",
    "DTN.5.00694":"U",
    "DTN.5.00700":"U",
    "DTN.5.00723":"U",
    "DTN.5.00724":"U",
    "DTN.5.00726":"U",
    "DTN.5.00728":"U",
    "DTN.5.00730":"U",
    "DTN.5.00748":"U",
    "DTN.5.00750":"U",
    "DTN.5.00760":"U",
    "DTN.5.00770":"U",
    "DTN.5.00782":"U",
    "DTN.5.00784":"U",
    "DTN.5.00788":"U",
    "DTN.5.00800":"U",
    "DTN.5.00820":"U",
    "DTN.5.00900":"U",
    "DTN.5.00930":"U",
    "DTN.5.00940":"U",
    "DTN.5.01025":"U",
    "DTN.5.01050":"U",
    "DTN.5.01054":"U",
    "DTN.5.01065":"U",
    "DTN.6.04195":"U",
    "DTN.6.10111":"U",
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

## Verify requirements
rqmnt_status["DTN.5.00008"] = "P"
rqmnt_status["DTN.5.00009"] = "P"

## Load Channel table with bad configuration
reject_target_table('/cf/cha_lunar_bad.tbl', target_1) 

## Load Channel table
load_target_table('/cf/cha_lunar.tbl', target_1)

## Load CF configuration table
cmd(f"{target_1} CF_CMD_DISABLE_ENGINE")
load_target_table('/cf/cf_lunar.tbl', target_1)
cmd(f"{target_1} CF_CMD_ENABLE_ENGINE")

## Verify requirements
rqmnt_status["DTN.5.00006"] = "P"
rqmnt_status["DTN.5.00007"] = "P"
rqmnt_status["DTN.5.00930"] = "P"
rqmnt_status["DTN.5.01050"] = "P"

## Start Channel 0 and 1
cmd(f"{target_1} BPNODE_CMD_ADD_APPLICATION with CHAN_ID 0")
wait(1)
cmd(f"{target_1} BPNODE_CMD_START_APPLICATION with CHAN_ID 0")
wait(5)

cmd(f"{target_1} BPNODE_CMD_ADD_APPLICATION with CHAN_ID 1")
wait(1)
cmd(f"{target_1} BPNODE_CMD_START_APPLICATION with CHAN_ID 1")
wait(5)

## Print Channel status
LUNAR_CHANNEL_0_SERVICE_NUM = tlm(f"{target_1} BPNODE_CHAN_CON_STAT_HK CHAN_STAT_LOCAL_SERVICE_NUM_0")
print("Lunar User Node Channel 0 Service Number:", LUNAR_CHANNEL_0_SERVICE_NUM)
LUNAR_CHANNEL_0_STATE = tlm(f"{target_1} BPNODE_CHAN_CON_STAT_HK CHAN_STAT_STATE_0")
print("Lunar User Node Channel 0 State:", LUNAR_CHANNEL_0_STATE)
LUNAR_CHANNEL_0_REG_STATE = tlm(f"{target_1} BPNODE_CHAN_CON_STAT_HK CHAN_STAT_REG_STATE_0")
print("Lunar User Node Channel 0 Registration State:", LUNAR_CHANNEL_0_REG_STATE)

LUNAR_CHANNEL_1_STATE = tlm(f"{target_1} BPNODE_CHAN_CON_STAT_HK CHAN_STAT_STATE_1")
print("Lunar User Node Channel 1 State:", LUNAR_CHANNEL_1_STATE)
LUNAR_CHANNEL_1_SERVICE_NUM = tlm(f"{target_1} BPNODE_CHAN_CON_STAT_HK CHAN_STAT_LOCAL_SERVICE_NUM_1")
print("Lunar User Node Channel 1 Service Number:", LUNAR_CHANNEL_1_SERVICE_NUM)
LUNAR_CHANNEL_1_REG_STATE = tlm(f"{target_1} BPNODE_CHAN_CON_STAT_HK CHAN_STAT_REG_STATE_1")
print("Lunar User Node Channel 1 Registration State:", LUNAR_CHANNEL_1_REG_STATE)
                              
## Verify that Channel 0 is started on the Lunar User Node
assert LUNAR_CHANNEL_0_SERVICE_NUM == 1
assert LUNAR_CHANNEL_0_STATE == "STARTED"
assert LUNAR_CHANNEL_0_REG_STATE == "ACTIVE"

## Load Lunar User Node Contact table
load_target_table('/cf/con_lunar.tbl', target_1) 

## Set up Contact 0 on the Lunar User Node
cmd(f"{target_1} BPNODE_CMD_CONTACT_SETUP with CONTACT_ID 0")
wait(1)

##-------------------------------------------------------------------------------------------------------------------
## 2.2 Relay Node Configuration
##-------------------------------------------------------------------------------------------------------------------

## Load MIB PN table to set node number to 102
load_target_table('/cf/pn_relay.tbl', target_2)

## Load Contact table
load_target_table('/cf/con_relay.tbl', target_2) 

## Print the Rejected Directive counter prior to contact setup
RELAY_BUNDLE_AGENT_REJECTED_DIRECTIVE_COUNT_PRE = tlm(f"{target_2} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_AGENT_REJECTED_DIRECTIVE_COUNT")
print("Relay Node Rejected Directive Counter:", RELAY_BUNDLE_AGENT_REJECTED_DIRECTIVE_COUNT_PRE)

## Set up Contacts 0, 1, and 2
cmd(f"{target_2} BPNODE_CMD_CONTACT_SETUP with CONTACT_ID 0")
wait(1)
cmd(f"{target_2} BPNODE_CMD_CONTACT_SETUP with CONTACT_ID 1")
wait(1)
cmd(f"{target_2} BPNODE_CMD_CONTACT_SETUP with CONTACT_ID 2")
wait(1)
cmd(f"{target_2} BPNODE_CMD_CONTACT_SETUP with CONTACT_ID 3")
wait(10)

## Print the Rejected Directive counter post contact setup
RELAY_BUNDLE_AGENT_REJECTED_DIRECTIVE_COUNT_POST = tlm(f"{target_2} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_AGENT_REJECTED_DIRECTIVE_COUNT")
print("Relay Node Rejected Directive Counter:", RELAY_BUNDLE_AGENT_REJECTED_DIRECTIVE_COUNT_POST)

## Verify that the Contact 3 setup directive failed
assert RELAY_BUNDLE_AGENT_REJECTED_DIRECTIVE_COUNT_POST == RELAY_BUNDLE_AGENT_REJECTED_DIRECTIVE_COUNT_PRE + 1
wait_check(f"{target_2} CFE_EVS_LONG_EVENT_MSG PACKET_ID_APP_NAME == 'BPNODE'", 6)
wait_check(f"{target_2} CFE_EVS_LONG_EVENT_MSG PACKET_ID_EVENT_ID == 550", 6)
wait_check(f"{target_2} CFE_EVS_LONG_EVENT_MSG PACKET_ID_EVENT_TYPE == 'ERROR'", 6)

##-------------------------------------------------------------------------------------------------------------------
## 2.3 Ground Node Configuration
##-------------------------------------------------------------------------------------------------------------------

## Load MIB PN table to set node number to 103
load_target_table('/cf/pn_ground.tbl', target_3)

## Load Contact table
load_target_table('/cf/con_ground.tbl', target_3) 

## Set up Contacts 0, 1, and 2
cmd(f"{target_3} BPNODE_CMD_CONTACT_SETUP with CONTACT_ID 0")
wait(1)
cmd(f"{target_3} BPNODE_CMD_CONTACT_SETUP with CONTACT_ID 1")
wait(1)

##-------------------------------------------------------------------------------------------------------------------
## 2.4 NSN Node Configuration
##-------------------------------------------------------------------------------------------------------------------

## Load MIB PN table to set node number to 104
load_target_table('/cf/pn_nsn.tbl', target_4)

## Load Contact table
load_target_table('/cf/con_nsn.tbl', target_4) 

## Set up Contacts 0, 1, and 2
cmd(f"{target_4} BPNODE_CMD_CONTACT_SETUP with CONTACT_ID 0")
wait(1)
cmd(f"{target_4} BPNODE_CMD_CONTACT_SETUP with CONTACT_ID 1")
wait(1)

##-------------------------------------------------------------------------------------------------------------------
## 2.5 Earth User Node Configuration
##-------------------------------------------------------------------------------------------------------------------

## Load MIB PN table modified to set node number to 105
load_target_table('/cf/pn_earth.tbl', target_5)

## Load Contact table
load_target_table('/cf/con_earth.tbl', target_5) 

## Set up Contact 0
cmd(f"{target_5} BPNODE_CMD_CONTACT_SETUP with CONTACT_ID 0")
wait(1)

##-------------------------------------------------------------------------------------------------------------------
## 3 RETURN TRANSFER #1, PART #1
##-------------------------------------------------------------------------------------------------------------------

##-------------------------------------------------------------------------------------------------------------------
## 3.1 Bundle Set #1 Generation
##-------------------------------------------------------------------------------------------------------------------

## Start creating bundles (CF transmitting a file)
CFDP_PDU_count_1 = 1902
cmd(f"{target_1} CF_CMD_TX_FILE with CFDP_CLASS 'CLASS_1', KEEP 1, CHAN_NUM 0, DEST_ID 2, SRC_FILENAME '/cf/Jojo3.jpg', DST_FILENAME '/cf/Jojo3_on_earth.jpg'")
wait(1)

##-------------------------------------------------------------------------------------------------------------------
## 3.2 Execution of the first hop (Lunar User Node -> Relay Node)
##-------------------------------------------------------------------------------------------------------------------

## Wait for all bundles to have been created
wait_check(f"{target_1} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_GENERATED_ACCEPTED == {CFDP_PDU_count_1}", 600)
wait(10)

## Print counter values
LUNAR_CFDP_PDU_COUNT_SENT = tlm(f"{target_1} CF_HK CHANNEL_HK_0_COUNTERS_SENT_PDU")
print("Lunar User Node CFDP PDUs Sent:", LUNAR_CFDP_PDU_COUNT_SENT)
LUNAR_ADU_COUNT_RECEIVED = tlm(f"{target_1} BPNODE_NODE_MIB_COUNTERS_HK ADU_COUNT_RECEIVED")
print("Lunar User Node ADUs Received:", LUNAR_ADU_COUNT_RECEIVED)
LUNAR_BUNDLE_COUNT_GENERATED_ACCEPTED = tlm(f"{target_1} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_GENERATED_ACCEPTED")
print("Lunar User Node Bundles Generated:", LUNAR_BUNDLE_COUNT_GENERATED_ACCEPTED)
LUNAR_BUNDLE_COUNT_STORED = tlm(f"{target_1} BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED")
print("Lunar User Node Bundles Stored:", LUNAR_BUNDLE_COUNT_STORED)

## Verify successful data creation
assert LUNAR_CFDP_PDU_COUNT_SENT == CFDP_PDU_count_1
assert LUNAR_ADU_COUNT_RECEIVED == CFDP_PDU_count_1
assert LUNAR_BUNDLE_COUNT_GENERATED_ACCEPTED == CFDP_PDU_count_1
assert LUNAR_BUNDLE_COUNT_STORED == CFDP_PDU_count_1

## Verify requirements
rqmnt_status["DTN.5.00010"] = "P"
rqmnt_status["DTN.5.00012"] = "P"
rqmnt_status["DTN.5.00040"] = "P"
rqmnt_status["DTN.5.00110"] = "P"
rqmnt_status["DTN.5.00120"] = "P"
rqmnt_status["DTN.5.00150"] = "P"
rqmnt_status["DTN.5.00200"] = "P"
rqmnt_status["DTN.5.00330"] = "P"

## Start Contact 0 on the Lunar User and Relay Nodes
cmd(f"{target_2} BPNODE_CMD_CONTACT_START with CONTACT_ID 0")
wait(1)
cmd(f"{target_1} BPNODE_CMD_CONTACT_START with CONTACT_ID 0")
wait(5)

## Print Contact 1 status
LUNAR_CONTACT_0_STATE = tlm(f"{target_1} BPNODE_CHAN_CON_STAT_HK CON_STAT_RUN_STATE_0")
print("Lunar User Node Contact 0 State:", LUNAR_CONTACT_0_STATE)
RELAY_CONTACT_0_STATE = tlm(f"{target_2} BPNODE_CHAN_CON_STAT_HK CON_STAT_RUN_STATE_0")
print("Relay Node Contact 0 State:", RELAY_CONTACT_0_STATE)

## Verify that Contact 0 is started on the Lunar User and Relay Nodes
assert LUNAR_CONTACT_0_STATE == "STARTED"
assert RELAY_CONTACT_0_STATE == "STARTED"

## Wait for all bundles to have been received by Relay Node
wait_check(f"{target_2} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_RECEIVED >= {CFDP_PDU_count_1}", 300)
wait(10)

## Print counter values
LUNAR_BUNDLE_COUNT_STORED = tlm(f"{target_1} BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED")
print("Lunar User Node Bundles Stored:", LUNAR_BUNDLE_COUNT_STORED)
LUNAR_BUNDLE_COUNT_FORWARDED = tlm(f"{target_1} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_FORWARDED")
print("Lunar User Node Bundles Forwarded:", LUNAR_BUNDLE_COUNT_FORWARDED)

RELAY_BUNDLE_COUNT_RECEIVED = tlm(f"{target_2} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_RECEIVED")
print("Relay Node Bundles Received:", RELAY_BUNDLE_COUNT_RECEIVED)
RELAY_BUNDLE_COUNT_STORED = tlm(f"{target_2} BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED")
print("Relay Node Bundles Stored:", RELAY_BUNDLE_COUNT_STORED)

## Verify successful data transfer
assert LUNAR_BUNDLE_COUNT_STORED == 0
assert LUNAR_BUNDLE_COUNT_FORWARDED == CFDP_PDU_count_1
assert RELAY_BUNDLE_COUNT_RECEIVED == CFDP_PDU_count_1
assert RELAY_BUNDLE_COUNT_STORED == CFDP_PDU_count_1

## Verify requirements
rqmnt_status["DTN.5.00170"] = "P"
rqmnt_status["DTN.5.00174"] = "P"
rqmnt_status["DTN.5.00692"] = "P"
rqmnt_status["DTN.5.00694"] = "P"
rqmnt_status["DTN.5.00700"] = "P"

##-------------------------------------------------------------------------------------------------------------------
## 4 HANDLING OF INVALID BUNDLES
##-------------------------------------------------------------------------------------------------------------------

##-------------------------------------------------------------------------------------------------------------------
## 4.1 Injection of unknown extension blocks (Relay Node)
##-------------------------------------------------------------------------------------------------------------------

## Inject three bundles containing an unknown extension block
## Earth User EID = 104.1
unknown_blocks_send(104, 1, 600, relay_ip, 4556)
wait(20)

## Print counter values
RELAY_BUNDLE_COUNT_RECEIVED = tlm(f"{target_2} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_RECEIVED")
print("Relay Node Bundles Received:", RELAY_BUNDLE_COUNT_RECEIVED)
RELAY_BUNDLE_COUNT_STORED = tlm(f"{target_2} BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED")
print("Relay Node Bundles Stored:", RELAY_BUNDLE_COUNT_STORED)
RELAY_BUNDLE_COUNT_DELETED_UNSUPPORTED_BLOCK = tlm(f"{target_2} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_DELETED_UNSUPPORTED_BLOCK")
print("Relay Node Bundles Deleted Unsupported Block:", RELAY_BUNDLE_COUNT_DELETED_UNSUPPORTED_BLOCK)
RELAY_BUNDLE_COUNT_DISCARDED = tlm(f"{target_2} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_DISCARDED")
print("Relay Node Bundles Discarded:", RELAY_BUNDLE_COUNT_DISCARDED)
RELAY_BUNDLE_COUNT_DELETED = tlm(f"{target_2} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_DELETED")
print("Relay Node Bundles Deleted:", RELAY_BUNDLE_COUNT_DELETED)

## Verify successful data transfer
assert RELAY_BUNDLE_COUNT_RECEIVED == CFDP_PDU_count_1 + 2
assert RELAY_BUNDLE_COUNT_STORED == CFDP_PDU_count_1 + 2
assert RELAY_BUNDLE_COUNT_DELETED_UNSUPPORTED_BLOCK == 1
assert RELAY_BUNDLE_COUNT_DISCARDED == 1
assert RELAY_BUNDLE_COUNT_DELETED == 1

## Verify requirements
rqmnt_status["DTN.5.00260"] = "P"

##-------------------------------------------------------------------------------------------------------------------
## 4.2 Injection of invalid bundles (Relay Node)
##-------------------------------------------------------------------------------------------------------------------

## Inject a set of 50 bundles including nine invalid bundles
## Earth User EID = 103.1
invalid_bundles_send(103, 1, 600, relay_ip, 4556)
wait(20)

## Print counter values
RELAY_BUNDLE_COUNT_DISCARDED = tlm(f"{target_2} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_DISCARDED")
print("Relay Node Bundles Discarded:", RELAY_BUNDLE_COUNT_DISCARDED)
RELAY_BUNDLE_COUNT_DELETED = tlm(f"{target_2} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_DELETED")
print("Relay Node Bundles Deleted:", RELAY_BUNDLE_COUNT_DELETED)
RELAY_BUNDLE_COUNT_DELETED_EXPIRED = tlm(f"{target_2} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_DELETED_EXPIRED")
print("Relay Node Bundles Deleted Expired:", RELAY_BUNDLE_COUNT_DELETED_EXPIRED)
RELAY_BUNDLE_COUNT_DELETED_HOP_EXCEEDED = tlm(f"{target_2} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_DELETED_HOP_EXCEEDED")
print("Relay Node Bundles Deleted Hop Exceeded:", RELAY_BUNDLE_COUNT_DELETED_HOP_EXCEEDED)
RELAY_BUNDLE_COUNT_DELETED_UNINTELLIGIBLE = tlm(f"{target_2} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_DELETED_UNINTELLIGIBLE")
print("Relay Node Bundles Deleted Unintelligible:", RELAY_BUNDLE_COUNT_DELETED_UNINTELLIGIBLE)
RELAY_BUNDLE_COUNT_DELETED_UNSUPPORTED_BLOCK = tlm(f"{target_2} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_DELETED_UNSUPPORTED_BLOCK")
print("Relay Node Bundles Deleted Unsupported Block:", RELAY_BUNDLE_COUNT_DELETED_UNSUPPORTED_BLOCK)
RELAY_BUNDLE_COUNT_RECEIVED = tlm(f"{target_2} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_RECEIVED")
print("Relay Node Bundles Received:", RELAY_BUNDLE_COUNT_RECEIVED)
RELAY_BUNDLE_COUNT_STORED = tlm(f"{target_2} BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED")
print("Relay Node Bundles Stored:", RELAY_BUNDLE_COUNT_STORED)

## Verify successful data transfer
assert RELAY_BUNDLE_COUNT_DISCARDED == 10
assert RELAY_BUNDLE_COUNT_DELETED == 10
assert RELAY_BUNDLE_COUNT_DELETED_UNINTELLIGIBLE == 9
assert RELAY_BUNDLE_COUNT_RECEIVED == CFDP_PDU_count_1 + 43
assert RELAY_BUNDLE_COUNT_STORED == CFDP_PDU_count_1 + 43

## Verify requirements
rqmnt_status["DTN.5.00180"] = "P"
rqmnt_status["DTN.5.00190"] = "P"
rqmnt_status["DTN.5.00192"] = "P"
rqmnt_status["DTN.5.00255"] = "P"
rqmnt_status["DTN.5.00300"] = "P"
rqmnt_status["DTN.5.00320"] = "P"
rqmnt_status["DTN.5.00370"] = "P"

## Inject randomly corrupted bundles (Earth User EID, lifetime in seconds, number_of_bundles, send to ip/port, rate limit in Mbps)
## Earth User EID = 104.2
## These bundles will be used for testing of lifetime expiration
Lifetime_1_Start = time.time()
print(f"Lifetime 1 Start = {Lifetime_1_Start}")
bad_bundles_send(104, 2, 600, 5000, relay_ip, 4556, 45)
wait(20)

## Print counter values
RELAY_BUNDLE_COUNT_DISCARDED = tlm(f"{target_2} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_DISCARDED")
print("Relay Node Bundles Discarded:", RELAY_BUNDLE_COUNT_DISCARDED)
RELAY_BUNDLE_COUNT_DELETED = tlm(f"{target_2} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_DELETED")
print("Relay Node Bundles Deleted:", RELAY_BUNDLE_COUNT_DELETED)
RELAY_BUNDLE_COUNT_DELETED_EXPIRED = tlm(f"{target_2} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_DELETED_EXPIRED")
print("Relay Node Bundles Deleted Expired:", RELAY_BUNDLE_COUNT_DELETED_EXPIRED)
RELAY_BUNDLE_COUNT_DELETED_HOP_EXCEEDED = tlm(f"{target_2} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_DELETED_HOP_EXCEEDED")
print("Relay Node Bundles Deleted Hop Exceeded:", RELAY_BUNDLE_COUNT_DELETED_HOP_EXCEEDED)
RELAY_BUNDLE_COUNT_DELETED_UNINTELLIGIBLE = tlm(f"{target_2} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_DELETED_UNINTELLIGIBLE")
print("Relay Node Bundles Deleted Unintelligible:", RELAY_BUNDLE_COUNT_DELETED_UNINTELLIGIBLE)
RELAY_BUNDLE_COUNT_DELETED_UNSUPPORTED_BLOCK = tlm(f"{target_2} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_DELETED_UNSUPPORTED_BLOCK")
print("Relay Node Bundles Deleted Unsupported Block:", RELAY_BUNDLE_COUNT_DELETED_UNSUPPORTED_BLOCK)
RELAY_BUNDLE_COUNT_RECEIVED = tlm(f"{target_2} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_RECEIVED")
print("Relay Node Bundles Received:", RELAY_BUNDLE_COUNT_RECEIVED)
RELAY_BUNDLE_COUNT_STORED = tlm(f"{target_2} BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED")
print("Relay Node Bundles Stored:", RELAY_BUNDLE_COUNT_STORED)

## Verify successful data transfer
assert RELAY_BUNDLE_COUNT_DELETED == RELAY_BUNDLE_COUNT_DELETED_HOP_EXCEEDED + RELAY_BUNDLE_COUNT_DELETED_UNINTELLIGIBLE + RELAY_BUNDLE_COUNT_DELETED_UNSUPPORTED_BLOCK
assert RELAY_BUNDLE_COUNT_DELETED == RELAY_BUNDLE_COUNT_DISCARDED
assert RELAY_BUNDLE_COUNT_DELETED_EXPIRED == 0
assert RELAY_BUNDLE_COUNT_DELETED_HOP_EXCEEDED > 0
assert RELAY_BUNDLE_COUNT_DELETED + RELAY_BUNDLE_COUNT_RECEIVED == CFDP_PDU_count_1 + 3 + 50 + 5000

## Verify requirements
rqmnt_status["DTN.5.00260"] = "P"
rqmnt_status["DTN.5.00290"] = "P"

##-------------------------------------------------------------------------------------------------------------------
## 5 RETURN TRANSFER #1, PART #2
##-------------------------------------------------------------------------------------------------------------------

##-------------------------------------------------------------------------------------------------------------------
## 5.1 Execution of the subsequent hops (Relay Node -> Ground Node -> NSN Node -> Earth User Node)
##-------------------------------------------------------------------------------------------------------------------

## Start Contacts
cmd(f"{target_5} BPNODE_CMD_CONTACT_START with CONTACT_ID 0")
wait(1)
cmd(f"{target_4} BPNODE_CMD_CONTACT_START with CONTACT_ID 0")
wait(1)
cmd(f"{target_4} BPNODE_CMD_CONTACT_START with CONTACT_ID 1")
wait(1)
cmd(f"{target_3} BPNODE_CMD_CONTACT_START with CONTACT_ID 0")
wait(1)
cmd(f"{target_3} BPNODE_CMD_CONTACT_START with CONTACT_ID 1")
wait(1)
cmd(f"{target_2} BPNODE_CMD_CONTACT_START with CONTACT_ID 1")
wait(10)

## Wait for all bundles to have been received by the Earth User Node
wait_check(f"{target_5} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_RECEIVED == {CFDP_PDU_count_1}", 300)
wait(10)

## Print counter values
RELAY_BUNDLE_COUNT_FORWARDED = tlm(f"{target_2} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_FORWARDED")
print("Relay Node Bundles Forwarded:", RELAY_BUNDLE_COUNT_FORWARDED)
RELAY_BUNDLE_COUNT_STORED = tlm(f"{target_2} BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED")
print("Relay Node Bundles Stored:", RELAY_BUNDLE_COUNT_STORED)

GROUND_BUNDLE_COUNT_RECEIVED = tlm(f"{target_3} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_RECEIVED")
print("Ground Node Bundles Received:", GROUND_BUNDLE_COUNT_RECEIVED)
GROUND_BUNDLE_COUNT_DELETED = tlm(f"{target_3} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_DELETED")
print("Ground Node Bundles Deleted:", GROUND_BUNDLE_COUNT_DELETED)
GROUND_BUNDLE_COUNT_DELETED_EXPIRED = tlm(f"{target_3} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_DELETED_EXPIRED")
print("Ground Node Bundles Deleted Expired:", GROUND_BUNDLE_COUNT_DELETED_EXPIRED)
GROUND_BUNDLE_COUNT_STORED = tlm(f"{target_3} BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED")
print("Ground Node Bundles Stored:", GROUND_BUNDLE_COUNT_STORED)
GROUND_BUNDLE_COUNT_FORWARDED = tlm(f"{target_3} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_FORWARDED")
print("Ground Node Bundles Forwarded:", GROUND_BUNDLE_COUNT_FORWARDED)

NSN_BUNDLE_COUNT_RECEIVED = tlm(f"{target_4} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_RECEIVED")
print("NSN Node Bundles Received:", NSN_BUNDLE_COUNT_RECEIVED)
NSN_BUNDLE_COUNT_DELETED = tlm(f"{target_4} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_DELETED")
print("NSN Node Bundles Deleted:", NSN_BUNDLE_COUNT_DELETED)
NSN_BUNDLE_COUNT_DELETED_EXPIRED = tlm(f"{target_4} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_DELETED_EXPIRED")
print("NSN Node Bundles Deleted Expired:", NSN_BUNDLE_COUNT_DELETED_EXPIRED)
NSN_BUNDLE_COUNT_STORED = tlm(f"{target_4} BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED")
print("NSN Node Bundles Stored:", NSN_BUNDLE_COUNT_STORED)
NSN_BUNDLE_COUNT_FORWARDED = tlm(f"{target_4} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_FORWARDED")
print("NSN Node Bundles Forwarded:", NSN_BUNDLE_COUNT_FORWARDED)

EARTH_BUNDLE_COUNT_RECEIVED = tlm(f"{target_5} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_RECEIVED")
print("Earth User Node Bundles Received:", EARTH_BUNDLE_COUNT_RECEIVED)
EARTH_BUNDLE_COUNT_DELETED = tlm(f"{target_5} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_DELETED")
print("Earth User Node Bundles Deleted:", EARTH_BUNDLE_COUNT_DELETED)
EARTH_BUNDLE_COUNT_STORED = tlm(f"{target_5} BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED")
print("Earth User Node Bundles Stored:", EARTH_BUNDLE_COUNT_STORED)
EARTH_BUNDLE_COUNT_DELIVERED = tlm(f"{target_5} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_DELIVERED")
print("Earth User Node Bundles Delivered:", EARTH_BUNDLE_COUNT_DELIVERED)
EARTH_ADU_COUNT_DELIVERED = tlm(f"{target_5} BPNODE_NODE_MIB_COUNTERS_HK ADU_COUNT_DELIVERED")
print("Earth User Node ADUs Delivered:", EARTH_ADU_COUNT_DELIVERED)

## Verify successful data transfer
assert RELAY_BUNDLE_COUNT_STORED >= 43
assert GROUND_BUNDLE_COUNT_DELETED_EXPIRED == 0
assert GROUND_BUNDLE_COUNT_STORED == 43
assert NSN_BUNDLE_COUNT_DELETED_EXPIRED == 0
assert NSN_BUNDLE_COUNT_STORED == 0
assert EARTH_BUNDLE_COUNT_DELETED == 0
assert EARTH_BUNDLE_COUNT_STORED == CFDP_PDU_count_1
assert EARTH_BUNDLE_COUNT_DELIVERED == 0
assert EARTH_ADU_COUNT_DELIVERED == 0

## Verify requirements
rqmnt_status["DTN.5.00660"] = "P"

##-------------------------------------------------------------------------------------------------------------------
## 5.2 Earth User Node Service Setup and ADU Delivery
##-------------------------------------------------------------------------------------------------------------------

## Load ADU Proxy table
load_target_table('/cf/adu_earth.tbl', target_5) 

## Verify requirements
rqmnt_status["DTN.5.00726"] = "P"
rqmnt_status["DTN.5.00728"] = "P"

## Load Channel table
load_target_table('/cf/cha_earth.tbl', target_5)

## Load CF configuration table
cmd(f"{target_5} CF_CMD_DISABLE_ENGINE")
load_target_table('/cf/cf_earth.tbl', target_5)
cmd(f"{target_5} CF_CMD_ENABLE_ENGINE")

## Verify requirements
rqmnt_status["DTN.5.00723"] = "P"
rqmnt_status["DTN.5.00724"] = "P"

## Start Channel 0 and 1
cmd(f"{target_5} BPNODE_CMD_ADD_APPLICATION with CHAN_ID 0")
wait(1)
cmd(f"{target_5} BPNODE_CMD_START_APPLICATION with CHAN_ID 0")
wait(5)

cmd(f"{target_5} BPNODE_CMD_ADD_APPLICATION with CHAN_ID 1")
wait(1)
cmd(f"{target_5} BPNODE_CMD_START_APPLICATION with CHAN_ID 1")
wait(5)

## Print Channel status
EARTH_CHANNEL_0_SERVICE_NUM = tlm(f"{target_5} BPNODE_CHAN_CON_STAT_HK CHAN_STAT_LOCAL_SERVICE_NUM_0")
print("Earth User Node Channel 0 Service Number:", EARTH_CHANNEL_0_SERVICE_NUM)
EARTH_CHANNEL_0_STATE = tlm(f"{target_5} BPNODE_CHAN_CON_STAT_HK CHAN_STAT_STATE_0")
print("Earth User Node Channel 0 State:", EARTH_CHANNEL_0_STATE)
EARTH_CHANNEL_0_REG_STATE = tlm(f"{target_5} BPNODE_CHAN_CON_STAT_HK CHAN_STAT_REG_STATE_0")
print("Earth User Node Channel 0 Registration State:", EARTH_CHANNEL_0_REG_STATE)

EARTH_CHANNEL_1_STATE = tlm(f"{target_5} BPNODE_CHAN_CON_STAT_HK CHAN_STAT_STATE_1")
print("Earth User Node Channel 1 State:", EARTH_CHANNEL_1_STATE)
EARTH_CHANNEL_1_SERVICE_NUM = tlm(f"{target_5} BPNODE_CHAN_CON_STAT_HK CHAN_STAT_LOCAL_SERVICE_NUM_1")
print("Earth User Node Channel 1 Service Number:", EARTH_CHANNEL_1_SERVICE_NUM)
EARTH_CHANNEL_1_REG_STATE = tlm(f"{target_5} BPNODE_CHAN_CON_STAT_HK CHAN_STAT_REG_STATE_1")
print("Earth User Node Channel 1 Registration State:", EARTH_CHANNEL_1_REG_STATE)
                              
## Verify that both channels are started on the Earth User Node
assert EARTH_CHANNEL_0_SERVICE_NUM == 1
assert EARTH_CHANNEL_0_STATE == "STARTED"
assert EARTH_CHANNEL_0_REG_STATE == "ACTIVE"
assert EARTH_CHANNEL_1_SERVICE_NUM == 2
assert EARTH_CHANNEL_1_STATE == "STARTED"
assert EARTH_CHANNEL_1_REG_STATE == "ACTIVE"

# Wait for all bundles to have been delivered by the Earth User Node
wait_check(f"{target_5} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_DELIVERED == {CFDP_PDU_count_1}", 300)
wait(10)

## Print counter values
EARTH_BUNDLE_COUNT_DELETED = tlm(f"{target_5} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_DELETED")
print("Earth User Node Bundles Deleted:", EARTH_BUNDLE_COUNT_DELETED)
EARTH_BUNDLE_COUNT_STORED = tlm(f"{target_5} BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED")
print("Earth User Node Bundles Stored:", EARTH_BUNDLE_COUNT_STORED)
EARTH_BUNDLE_COUNT_DELIVERED = tlm(f"{target_5} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_DELIVERED")
print("Earth User Node Bundles Delivered:", EARTH_BUNDLE_COUNT_DELIVERED)
EARTH_ADU_COUNT_DELIVERED = tlm(f"{target_5} BPNODE_NODE_MIB_COUNTERS_HK ADU_COUNT_DELIVERED")
print("Earth User Node ADUs Delivered:", EARTH_ADU_COUNT_DELIVERED)
EARTH_CFDP_PDU_COUNT_RECEIVED = tlm(f"{target_5} CF_HK CHANNEL_HK_0_COUNTERS_RECV_PDU")
print("Earth User Node CFDP PDUs received:", EARTH_CFDP_PDU_COUNT_RECEIVED)

## Verify successful data transfer
assert EARTH_BUNDLE_COUNT_DELETED == CFDP_PDU_count_1
assert EARTH_BUNDLE_COUNT_STORED == 0
assert EARTH_BUNDLE_COUNT_DELIVERED == CFDP_PDU_count_1
assert EARTH_ADU_COUNT_DELIVERED == CFDP_PDU_count_1
assert EARTH_CFDP_PDU_COUNT_RECEIVED == CFDP_PDU_count_1

##-------------------------------------------------------------------------------------------------------------------
## 6 NODE RESTART
##-------------------------------------------------------------------------------------------------------------------

##-------------------------------------------------------------------------------------------------------------------
## 6.1 Lunar User Node Restart
##-------------------------------------------------------------------------------------------------------------------

## Print Node Startup Counter prior to node restart
LUNAR_NODE_STARTUP_COUNTER_PRE = tlm(f"{target_1} BPNODE_NODE_MIB_REPORTS_HK NODE_STARTUP_COUNTER")
print("Lunar User Node Startup Counter:", LUNAR_NODE_STARTUP_COUNTER_PRE)

## Send restart command
cmd(f"{target_1} CFE_ES_CMD_RESTART_APP with APPLICATION 'BPNODE'")
wait(20)

## Print Node Startup Counter post node restart
LUNAR_NODE_STARTUP_COUNTER_POST = tlm(f"{target_1} BPNODE_NODE_MIB_REPORTS_HK NODE_STARTUP_COUNTER")
print("Lunar User Node Startup Counter:", LUNAR_NODE_STARTUP_COUNTER_POST)

## Verify successful node restart
assert LUNAR_NODE_STARTUP_COUNTER_POST == LUNAR_NODE_STARTUP_COUNTER_PRE + 1

## Stop and remove Channel 0
cmd(f"{target_1} BPNODE_CMD_STOP_APPLICATION with CHAN_ID 0")
wait(1)
cmd(f"{target_1} BPNODE_CMD_REMOVE_APPLICATION with CHAN_ID 0")
wait(1)

## Load MIB PN table to set node number to 101
load_target_table('/cf/pn_lunar.tbl', target_1)

## Load ADU Proxy table
load_target_table('/cf/adu_lunar.tbl', target_1) 

## Load Channel table (turning off automatic extension block creation)
load_target_table('/cf/cha_lunar_noext.tbl', target_1)

## Set Lunar User Node time source to invalid
cmd(f"{target_1} CFE_TIME_CMD_SET_STATE with CLOCK_STATE 'INVALID'")

## Load Contact table
load_target_table('/cf/con_lunar.tbl', target_1) 

## Load CF configuration table
cmd(f"{target_1} CF_CMD_DISABLE_ENGINE")
load_target_table('/cf/cf_lunar.tbl', target_1)
cmd(f"{target_1} CF_CMD_ENABLE_ENGINE")

## Restart Channel 0 and 1
cmd(f"{target_1} BPNODE_CMD_ADD_ALL_APPLICATIONS")
wait(1)
cmd(f"{target_1} BPNODE_CMD_START_ALL_APPLICATIONS")
wait(10)

## Print Channel status
LUNAR_CHANNEL_0_SERVICE_NUM = tlm(f"{target_1} BPNODE_CHAN_CON_STAT_HK CHAN_STAT_LOCAL_SERVICE_NUM_0")
print("Lunar User Node Channel 0 Service Number:", LUNAR_CHANNEL_0_SERVICE_NUM)
LUNAR_CHANNEL_0_STATE = tlm(f"{target_1} BPNODE_CHAN_CON_STAT_HK CHAN_STAT_STATE_0")
print("Lunar User Node Channel 0 State:", LUNAR_CHANNEL_0_STATE)
LUNAR_CHANNEL_0_REG_STATE = tlm(f"{target_1} BPNODE_CHAN_CON_STAT_HK CHAN_STAT_REG_STATE_0")
print("Lunar User Node Channel 0 Registration State:", LUNAR_CHANNEL_0_REG_STATE)

LUNAR_CHANNEL_1_STATE = tlm(f"{target_1} BPNODE_CHAN_CON_STAT_HK CHAN_STAT_STATE_1")
print("Lunar User Node Channel 1 State:", LUNAR_CHANNEL_1_STATE)
LUNAR_CHANNEL_1_SERVICE_NUM = tlm(f"{target_1} BPNODE_CHAN_CON_STAT_HK CHAN_STAT_LOCAL_SERVICE_NUM_1")
print("Lunar User Node Channel 1 Service Number:", LUNAR_CHANNEL_1_SERVICE_NUM)
LUNAR_CHANNEL_1_REG_STATE = tlm(f"{target_1} BPNODE_CHAN_CON_STAT_HK CHAN_STAT_REG_STATE_1")
print("Lunar User Node Channel 1 Registration State:", LUNAR_CHANNEL_1_REG_STATE)
                              
## Verify that Channel 0 is started on the Lunar User Node
assert LUNAR_CHANNEL_0_SERVICE_NUM == 1
assert LUNAR_CHANNEL_0_STATE == "STARTED"
assert LUNAR_CHANNEL_0_REG_STATE == "ACTIVE"
assert LUNAR_CHANNEL_1_SERVICE_NUM == 2
assert LUNAR_CHANNEL_1_STATE == "STARTED"
assert LUNAR_CHANNEL_1_REG_STATE == "PASSIVE_DEFER"

## Set up and start Contact 0
cmd(f"{target_1} BPNODE_CMD_CONTACT_SETUP with CONTACT_ID 0")
wait(1)
cmd(f"{target_1} BPNODE_CMD_CONTACT_START with CONTACT_ID 0")
wait(10)

##-------------------------------------------------------------------------------------------------------------------
## 6.2 NSN Node Reload
##-------------------------------------------------------------------------------------------------------------------

## Print Node Startup Counter prior to node reload
NSN_NODE_STARTUP_COUNTER_PRE = tlm(f"{target_4} BPNODE_NODE_MIB_REPORTS_HK NODE_STARTUP_COUNTER")
print("NSN Node Startup Counter:", NSN_NODE_STARTUP_COUNTER_PRE)

## Send reload command
cmd(f"{target_4} CFE_ES_CMD_RELOAD_APP with APPLICATION 'BPNODE', APP_FILE_NAME '/cf/bpnode.so'")
wait(20)

## Print Node Startup Counter post node reload
NSN_NODE_STARTUP_COUNTER_POST = tlm(f"{target_4} BPNODE_NODE_MIB_REPORTS_HK NODE_STARTUP_COUNTER")
print("NSN Node Startup Counter:", NSN_NODE_STARTUP_COUNTER_POST)

## Verify successful node reload
assert NSN_NODE_STARTUP_COUNTER_POST == NSN_NODE_STARTUP_COUNTER_PRE + 1

## Load MIB PN table to set node number to 104 and configure maximum lifetime to 420 seconds
load_target_table('/cf/pn_nsn_life.tbl', target_4)

## Load Contact table
load_target_table('/cf/con_nsn.tbl', target_4) 

## Set up and start Contacts 0, 1, and 2
cmd(f"{target_4} BPNODE_CMD_CONTACT_SETUP with CONTACT_ID 0")
wait(1)
cmd(f"{target_4} BPNODE_CMD_CONTACT_START with CONTACT_ID 0")
wait(1)
cmd(f"{target_4} BPNODE_CMD_CONTACT_SETUP with CONTACT_ID 1")
wait(1)
cmd(f"{target_4} BPNODE_CMD_CONTACT_START with CONTACT_ID 1")
wait(10)

## Print Node Maximum Allowed Lifetime
NSN_NODE_MAXIMUM_LIFETIME = tlm(f"{target_4} BPNODE_NODE_MIB_CONFIG_HK PARAM_SET_MAX_LIFETIME")
print("NSN Node Maximum Allowed Lifetime:", NSN_NODE_MAXIMUM_LIFETIME)

## Verify Node Maximum Allowed Lifetime
assert NSN_NODE_MAXIMUM_LIFETIME == 420000

##-------------------------------------------------------------------------------------------------------------------
## 6.3 Earth User Node Stop/Start
##-------------------------------------------------------------------------------------------------------------------

## Print Node Startup Counter prior to node stop/start
EARTH_NODE_STARTUP_COUNTER_PRE = tlm(f"{target_5} BPNODE_NODE_MIB_REPORTS_HK NODE_STARTUP_COUNTER")
print("Earth User Node Startup Counter:", EARTH_NODE_STARTUP_COUNTER_PRE)

## Send stop command
cmd(f"{target_5} CFE_ES_CMD_STOP_APP with APPLICATION 'BPNODE'")
wait(45)

## Send start command
cmd(f"{target_5} CFE_ES_CMD_START_APP with APPLICATION 'BPNODE', APP_ENTRY_POINT 'BPNode_AppMain', APP_FILE_NAME '/cf/bpnode.so'")
wait(20)

## Print Node Startup Counter post node stop/start
EARTH_NODE_STARTUP_COUNTER_POST = tlm(f"{target_5} BPNODE_NODE_MIB_REPORTS_HK NODE_STARTUP_COUNTER")
print("Earth User Node Startup Counter:", EARTH_NODE_STARTUP_COUNTER_POST)

## Verify successful node stop/start
assert EARTH_NODE_STARTUP_COUNTER_POST == EARTH_NODE_STARTUP_COUNTER_PRE + 1

## Verify requirements
rqmnt_status["DTN.5.01025"] = "P"
rqmnt_status["DTN.5.01065"] = "P"
rqmnt_status["DTN.6.10111"] = "P"

## Stop and remove Channel 0
cmd(f"{target_5} BPNODE_CMD_STOP_APPLICATION with CHAN_ID 0")
wait(1)
cmd(f"{target_5} BPNODE_CMD_REMOVE_APPLICATION with CHAN_ID 0")
wait(1)

## Load MIB PN table to set node number to 105
load_target_table('/cf/pn_earth.tbl', target_5)

## Load ADU Proxy table
load_target_table('/cf/adu_earth.tbl', target_5) 

## Load Channel table
load_target_table('/cf/cha_earth.tbl', target_5)

## Load Contact table
load_target_table('/cf/con_earth.tbl', target_5) 

## Load CF configuration table
cmd(f"{target_5} CF_CMD_DISABLE_ENGINE")
load_target_table('/cf/cf_earth.tbl', target_5)
cmd(f"{target_5} CF_CMD_ENABLE_ENGINE")

## Restart Channel 0 and 1
cmd(f"{target_5} BPNODE_CMD_ADD_ALL_APPLICATIONS")
wait(1)
cmd(f"{target_5} BPNODE_CMD_START_ALL_APPLICATIONS")
wait(1)

## Set up and start Contact 0
cmd(f"{target_5} BPNODE_CMD_CONTACT_SETUP with CONTACT_ID 0")
wait(1)
cmd(f"{target_5} BPNODE_CMD_CONTACT_START with CONTACT_ID 0")
wait(10)

##-------------------------------------------------------------------------------------------------------------------
## 7 RETURN TRANSFER #2
##-------------------------------------------------------------------------------------------------------------------

## Start creating bundles (CF transmitting a second file)
CFDP_PDU_count_2 = 3203
cmd(f"{target_1} CF_CMD_TX_FILE with CFDP_CLASS 'CLASS_1', KEEP 1, CHAN_NUM 0, DEST_ID 2, SRC_FILENAME '/cf/Jojo4.jpg', DST_FILENAME '/cf/Jojo4_on_earth.jpg'")

## Wait for all bundles to have been delivered by the Earth User Node
wait_check(f"{target_5} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_DELIVERED == {CFDP_PDU_count_2}", 300)
wait(10)

## Print counter values
LUNAR_CFDP_PDU_COUNT_SENT = tlm(f"{target_1} CF_HK CHANNEL_HK_0_COUNTERS_SENT_PDU")
print("Lunar User Node CFDP PDUs Sent:", LUNAR_CFDP_PDU_COUNT_SENT)
LUNAR_ADU_COUNT_RECEIVED = tlm(f"{target_1} BPNODE_NODE_MIB_COUNTERS_HK ADU_COUNT_RECEIVED")
print("Lunar User Node ADUs Received:", LUNAR_ADU_COUNT_RECEIVED)
LUNAR_BUNDLE_COUNT_STORED = tlm(f"{target_1} BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED")
print("Lunar User Node Bundles Stored:", LUNAR_BUNDLE_COUNT_STORED)

RELAY_BUNDLE_COUNT_STORED = tlm(f"{target_2} BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED")
print("Relay Node Bundles Stored:", RELAY_BUNDLE_COUNT_STORED)

GROUND_BUNDLE_COUNT_STORED = tlm(f"{target_3} BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED")
print("Ground Node Bundles Stored:", GROUND_BUNDLE_COUNT_STORED)

NSN_BUNDLE_COUNT_STORED = tlm(f"{target_4} BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED")
print("NSN Node Bundles Stored:", NSN_BUNDLE_COUNT_STORED)

EARTH_BUNDLE_COUNT_RECEIVED = tlm(f"{target_5} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_RECEIVED")
print("Earth User Node Bundles Received:", EARTH_BUNDLE_COUNT_RECEIVED)
EARTH_BUNDLE_COUNT_DELETED = tlm(f"{target_5} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_DELETED")
print("Earth User Node Bundles Deleted:", EARTH_BUNDLE_COUNT_DELETED)
EARTH_BUNDLE_COUNT_STORED = tlm(f"{target_5} BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED")
print("Earth User Node Bundles Stored:", EARTH_BUNDLE_COUNT_STORED)
EARTH_BUNDLE_COUNT_DELIVERED = tlm(f"{target_5} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_DELIVERED")
print("Earth User Node Bundles Delivered:", EARTH_BUNDLE_COUNT_DELIVERED)
EARTH_ADU_COUNT_DELIVERED = tlm(f"{target_5} BPNODE_NODE_MIB_COUNTERS_HK ADU_COUNT_DELIVERED")
print("Earth User Node ADUs Delivered:", EARTH_ADU_COUNT_DELIVERED)
EARTH_CFDP_PDU_COUNT_RECEIVED = tlm(f"{target_5} CF_HK CHANNEL_HK_0_COUNTERS_RECV_PDU")
print("Earth User Node CFDP PDUs received:", EARTH_CFDP_PDU_COUNT_RECEIVED)

## Verify successful end to end data transmission
assert LUNAR_CFDP_PDU_COUNT_SENT == CFDP_PDU_count_1 + CFDP_PDU_count_2
assert LUNAR_ADU_COUNT_RECEIVED == CFDP_PDU_count_2
assert LUNAR_BUNDLE_COUNT_STORED == 0
assert RELAY_BUNDLE_COUNT_STORED >= 43
assert GROUND_BUNDLE_COUNT_STORED == 43
assert NSN_BUNDLE_COUNT_STORED == 0
assert EARTH_BUNDLE_COUNT_RECEIVED == CFDP_PDU_count_2
assert EARTH_BUNDLE_COUNT_DELETED == 0
assert EARTH_BUNDLE_COUNT_STORED == 0
assert EARTH_BUNDLE_COUNT_DELIVERED == CFDP_PDU_count_2
assert EARTH_ADU_COUNT_DELIVERED == CFDP_PDU_count_2
assert EARTH_CFDP_PDU_COUNT_RECEIVED == CFDP_PDU_count_1 + CFDP_PDU_count_2

## Verify requirements
rqmnt_status["DTN.5.00730"] = "P"
rqmnt_status["DTN.5.00760"] = "P"
rqmnt_status["DTN.5.00770"] = "P"
rqmnt_status["DTN.5.00788"] = "P"

##-------------------------------------------------------------------------------------------------------------------
## 8 HANDLING OF EXPIRED BUNDLES, PART #1 (PRIMARY BLOCK LIFETIME)
##-------------------------------------------------------------------------------------------------------------------

## Return Lunar User Node time source to valid
cmd(f"{target_1} CFE_TIME_CMD_SET_STATE with CLOCK_STATE 'VALID'")

##-------------------------------------------------------------------------------------------------------------------
## 8.1 Expiration on Bundle Ingress
##-------------------------------------------------------------------------------------------------------------------

## Inject 100 expired bundles to the NSN Node
bundles_send(103, 1, 1000, 5, 2, nsn_ip, 4558, 1)
wait(10)

## Print counter values
RELAY_BUNDLE_COUNT_STORED = tlm(f"{target_2} BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED")
print("Relay Node Bundles Stored:", RELAY_BUNDLE_COUNT_STORED)
RELAY_BUNDLE_COUNT_DELETED_EXPIRED = tlm(f"{target_2} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_DELETED_EXPIRED")
print("Relay Node Bundles Deleted Expired:", RELAY_BUNDLE_COUNT_DELETED_EXPIRED)

GROUND_BUNDLE_COUNT_STORED = tlm(f"{target_3} BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED")
print("Ground Node Bundles Stored:", GROUND_BUNDLE_COUNT_STORED)
GROUND_BUNDLE_COUNT_DELETED_EXPIRED = tlm(f"{target_3} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_DELETED_EXPIRED")
print("Ground Node Bundles Deleted Expired:", GROUND_BUNDLE_COUNT_DELETED_EXPIRED)

NSN_BUNDLE_COUNT_STORED = tlm(f"{target_4} BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED")
print("NSN Node Bundles Stored:", NSN_BUNDLE_COUNT_STORED)
NSN_BUNDLE_COUNT_DELETED_EXPIRED = tlm(f"{target_4} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_DELETED_EXPIRED")
print("NSN Node Bundles Deleted Expired:", NSN_BUNDLE_COUNT_DELETED_EXPIRED)

## Verify successful bundle expiration on ingress
assert RELAY_BUNDLE_COUNT_STORED >= 43
assert RELAY_BUNDLE_COUNT_DELETED_EXPIRED == 0
assert GROUND_BUNDLE_COUNT_STORED == 43
assert GROUND_BUNDLE_COUNT_DELETED_EXPIRED == 0
assert NSN_BUNDLE_COUNT_STORED == 0
assert NSN_BUNDLE_COUNT_DELETED_EXPIRED == 100

## Verify requirements
rqmnt_status["DTN.5.00197"] = "P"

##-------------------------------------------------------------------------------------------------------------------
## 8.2 Expiration from Bundle Storage
##-------------------------------------------------------------------------------------------------------------------

## Wait for all stored bundles to have been expired
wait_check(f"{target_2} BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED == 0", 240)
Lifetime_1_Stop = time.time()
print(f"Lifetime 1 Stop = {Lifetime_1_Stop}")
Actual_Lifetime_1 = Lifetime_1_Stop - Lifetime_1_Start
print(f"Actual Lifetime 1 = {Actual_Lifetime_1}")
wait(60)

## Print counter values
RELAY_BUNDLE_COUNT_STORED = tlm(f"{target_2} BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED")
print("Relay Node Bundles Stored:", RELAY_BUNDLE_COUNT_STORED)
RELAY_BUNDLE_COUNT_DELETED_EXPIRED = tlm(f"{target_2} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_DELETED_EXPIRED")
print("Relay Node Bundles Deleted Expired:", RELAY_BUNDLE_COUNT_DELETED_EXPIRED)

GROUND_BUNDLE_COUNT_STORED = tlm(f"{target_3} BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED")
print("Ground Node Bundles Stored:", GROUND_BUNDLE_COUNT_STORED)
GROUND_BUNDLE_COUNT_DELETED_EXPIRED = tlm(f"{target_3} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_DELETED_EXPIRED")
print("Ground Node Bundles Deleted Expired:", GROUND_BUNDLE_COUNT_DELETED_EXPIRED)

## Verify successful bundle expiration from storage
assert RELAY_BUNDLE_COUNT_STORED == 0
assert RELAY_BUNDLE_COUNT_DELETED_EXPIRED >= 43
assert GROUND_BUNDLE_COUNT_STORED == 0
assert GROUND_BUNDLE_COUNT_DELETED_EXPIRED == 43
assert 600 <= Actual_Lifetime_1 <= 630

##-------------------------------------------------------------------------------------------------------------------
## 9 VERIFICATION OF BUNDLE CONTENT
##-------------------------------------------------------------------------------------------------------------------

prompt("Stop the Wireshark capture of bundles on the Relay Node")
prompt("Change the packet decoding from UDP to BP (using right click/decode as.../Current)")
prompt("Reorder the packets by Time")
prompt("Select the FIRST bundle with Earth User EID 104.1 and verify that it contains a Type 73 unknown canonical block")
prompt("Verify that the SECOND bundle with Earth User EID 104.1 DOES NOT contain an unknown canonical block")
prompt("Scroll down to the FIRST bundle with Earth User EID 105.1")
prompt("Verify that this bundle contains valid Primary, Previous Node, Bundle Age, Hop Count, and Payload Blocks")
prompt("Verify that the primary block of this bundle contains a valid creation timestamp")
prompt("Verify that the Previous Node ID = 102.0 in the Previous Node block")
prompt("Verify that the Bundle Age > 100,000 ms in the Bundle Age block")
prompt("Verify that the Hop Count = 2 in the Hop Count block")
prompt("Scroll down to the LAST bundle with Earth User EID 105.1")
prompt("Verify that this bundle contains a valid Bundle Age block, but no Previous Node block or Hop Count block")
prompt("Save the Wireshark capture as an artifact")

prompt("Stop the Wireshark capture of bundles on the Ground Node")
prompt("Change the packet decoding from UDP to BP (using right click/decode as.../Current)")
prompt("Reorder the packets by Time")
prompt("For any bundle, expand DTN Bundle Protocol Version 7")
prompt("Export the bundle data to a plain text file (using File/Export Packet Dissections)")
prompt("Save the Wireshark capture as an artifact")

prompt("Stop the Wireshark capture of bundles on the NSN Node")
prompt("Change the packet decoding from UDP to BP (using right click/decode as.../Current)")
prompt("Reorder the packets by Time")
prompt("For any bundle, expand DTN Bundle Protocol Version 7")
prompt("Export the bundle data to a plain text file (using File/Export Packet Dissections)")
prompt("Save the Wireshark capture as an artifact")

## Verify requirements
rqmnt_status["DTN.5.00060"] = "P"
rqmnt_status["DTN.5.00070"] = "P"
rqmnt_status["DTN.5.00100"] = "P"
rqmnt_status["DTN.5.00220"] = "P"
rqmnt_status["DTN.5.00250"] = "P"
rqmnt_status["DTN.5.00270"] = "P"
rqmnt_status["DTN.5.00275"] = "P"
rqmnt_status["DTN.5.00280"] = "P"
rqmnt_status["DTN.5.00670"] = "P"
rqmnt_status["DTN.5.00680"] = "P"

## Reset all error counters
cmd(f"{target_1} BPNODE_CMD_RESET_ERROR_COUNTERS")
wait(1)
cmd(f"{target_2} BPNODE_CMD_RESET_ERROR_COUNTERS")
wait(1)
cmd(f"{target_3} BPNODE_CMD_RESET_ERROR_COUNTERS")
wait(1)
cmd(f"{target_4} BPNODE_CMD_RESET_ERROR_COUNTERS")
wait(1)
cmd(f"{target_5} BPNODE_CMD_RESET_ERROR_COUNTERS")
wait(10)

## Reset all bundle counters
cmd(f"{target_1} BPNODE_CMD_RESET_BUNDLE_COUNTERS")
wait(1)
cmd(f"{target_2} BPNODE_CMD_RESET_BUNDLE_COUNTERS")
wait(1)
cmd(f"{target_3} BPNODE_CMD_RESET_BUNDLE_COUNTERS")
wait(1)
cmd(f"{target_4} BPNODE_CMD_RESET_BUNDLE_COUNTERS")
wait(1)
cmd(f"{target_5} BPNODE_CMD_RESET_BUNDLE_COUNTERS")
wait(10)

## Reset all CFDP counters
cmd(f"{target_1} CF_CMD_RESET")
wait(1)
cmd(f"{target_5} CF_CMD_RESET")
wait(10)

##-------------------------------------------------------------------------------------------------------------------
## 10 FORWARD TRANSFERS
##-------------------------------------------------------------------------------------------------------------------

##-------------------------------------------------------------------------------------------------------------------
## 10.1 Channel Registration State Test #1 - Passive/Defer
##-------------------------------------------------------------------------------------------------------------------

## Start Earth User to Lunar User data transfer (Earth User CF transmitting a file)
CFDP_PDU_count_3 = 900
cmd(f"{target_5} CF_CMD_TX_FILE with CFDP_CLASS 'CLASS_1', KEEP 1, CHAN_NUM 0, DEST_ID 1, SRC_FILENAME '/cf/Jojo1.jpg', DST_FILENAME '/cf/Jojo1_in_space.jpg'")
wait(1)
wait_check(f"{target_1} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_RECEIVED == {CFDP_PDU_count_3}", 180)
wait(10)

## Print counter values
LUNAR_BUNDLE_COUNT_DELETED = tlm(f"{target_1} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_DELETED")
print("Lunar User Node Bundles Deleted:", LUNAR_BUNDLE_COUNT_DELETED)
LUNAR_BUNDLE_COUNT_STORED = tlm(f"{target_1} BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED")
print("Lunar User Node Bundles Stored:", LUNAR_BUNDLE_COUNT_STORED)
LUNAR_BUNDLE_COUNT_ABANDONED = tlm(f"{target_1} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_ABANDONED")
print("Lunar User Node Bundles Abandoned:", LUNAR_BUNDLE_COUNT_ABANDONED)
LUNAR_BUNDLE_COUNT_DELIVERED = tlm(f"{target_1} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_DELIVERED")
print("Lunar User Node Bundles Delivered:", LUNAR_BUNDLE_COUNT_DELIVERED)
LUNAR_ADU_COUNT_DELIVERED = tlm(f"{target_1} BPNODE_NODE_MIB_COUNTERS_HK ADU_COUNT_DELIVERED")
print("Lunar User Node ADUs Delivered:", LUNAR_ADU_COUNT_DELIVERED)
LUNAR_CFDP_PDU_COUNT_RECEIVED = tlm(f"{target_1} CF_HK CHANNEL_HK_0_COUNTERS_RECV_PDU")
print("Lunar User Node CFDP PDUs received:", LUNAR_CFDP_PDU_COUNT_RECEIVED)

## Verify successful data reception
assert LUNAR_BUNDLE_COUNT_DELETED == 0
assert LUNAR_BUNDLE_COUNT_STORED == CFDP_PDU_count_3
assert LUNAR_BUNDLE_COUNT_ABANDONED == 0
assert LUNAR_BUNDLE_COUNT_DELIVERED == 0
assert LUNAR_ADU_COUNT_DELIVERED == 0
assert LUNAR_CFDP_PDU_COUNT_RECEIVED == 0

## Verify requirements
rqmnt_status["DTN.5.00750"] = "P"

## Change Lunar User Node Channel 1 registration state to active
cmd(f"{target_1} BPNODE_CMD_SET_REGISTRATION_STATE with CHAN_ID 1, REG_STATE 'ACTIVE'")
wait(1)
wait_check(f"{target_1} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_DELIVERED == {CFDP_PDU_count_3}", 300)
wait(10)

## Print Channel 1 registration status
LUNAR_CHANNEL_1_REG_STATE = tlm(f"{target_1} BPNODE_CHAN_CON_STAT_HK CHAN_STAT_REG_STATE_1")
print("Lunar User Node Channel 1 Registration State:", LUNAR_CHANNEL_1_REG_STATE)

## Verify Channel 1 registration state change
assert LUNAR_CHANNEL_1_REG_STATE == "ACTIVE"

## Print counter values
LUNAR_CHANNEL_1_REG_STATE = tlm(f"{target_1} BPNODE_CHAN_CON_STAT_HK CHAN_STAT_REG_STATE_1")
print("Lunar User Node Channel 1 Registration State:", LUNAR_CHANNEL_1_REG_STATE)
LUNAR_BUNDLE_COUNT_DELETED = tlm(f"{target_1} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_DELETED")
print("Lunar User Node Bundles Deleted:", LUNAR_BUNDLE_COUNT_DELETED)
LUNAR_BUNDLE_COUNT_STORED = tlm(f"{target_1} BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED")
print("Lunar User Node Bundles Stored:", LUNAR_BUNDLE_COUNT_STORED)
LUNAR_BUNDLE_COUNT_ABANDONED = tlm(f"{target_1} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_ABANDONED")
print("Lunar User Node Bundles Abandoned:", LUNAR_BUNDLE_COUNT_ABANDONED)
LUNAR_BUNDLE_COUNT_DELIVERED = tlm(f"{target_1} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_DELIVERED")
print("Lunar User Node Bundles Delivered:", LUNAR_BUNDLE_COUNT_DELIVERED)
LUNAR_ADU_COUNT_DELIVERED = tlm(f"{target_1} BPNODE_NODE_MIB_COUNTERS_HK ADU_COUNT_DELIVERED")
print("Lunar User Node ADUs Delivered:", LUNAR_ADU_COUNT_DELIVERED)
LUNAR_CFDP_PDU_COUNT_RECEIVED = tlm(f"{target_1} CF_HK CHANNEL_HK_0_COUNTERS_RECV_PDU")
print("Lunar User Node CFDP PDUs received:", LUNAR_CFDP_PDU_COUNT_RECEIVED)

## Verify successful data delivery
assert LUNAR_BUNDLE_COUNT_DELETED == CFDP_PDU_count_3
assert LUNAR_BUNDLE_COUNT_STORED == 0
assert LUNAR_BUNDLE_COUNT_ABANDONED == 0
assert LUNAR_BUNDLE_COUNT_DELIVERED == CFDP_PDU_count_3
assert LUNAR_ADU_COUNT_DELIVERED == CFDP_PDU_count_3
#assert LUNAR_CFDP_PDU_COUNT_RECEIVED == CFDP_PDU_count_3          DR DTNN-1492

##-------------------------------------------------------------------------------------------------------------------
## 10.2 Channel Registration State Test #2 - Passive/Abandon
##-------------------------------------------------------------------------------------------------------------------

## Change Lunar User Node Channel 1 registration state to passive/abandon
cmd(f"{target_1} BPNODE_CMD_SET_REGISTRATION_STATE with CHAN_ID 1, REG_STATE 'PASSIVE_ABANDON'")
wait(10)

## Print Channel 1 registration status
LUNAR_CHANNEL_1_REG_STATE = tlm(f"{target_1} BPNODE_CHAN_CON_STAT_HK CHAN_STAT_REG_STATE_1")
print("Lunar User Node Channel 1 Registration State:", LUNAR_CHANNEL_1_REG_STATE)

## Verify Channel 1 registration state change
assert LUNAR_CHANNEL_1_REG_STATE == "PASSIVE_ABANDON"

## Verify requirements                                                                                                                                                                                
rqmnt_status["DTN.5.00748"] = "P"

## Turn on Lunar User BPNode Debug events
cmd(f"{target_5} CFE_EVS_CMD_ENABLE_EVENT_TYPE with BIT_MASK 1")

## Start another Earth User to Lunar User data transfer (Earth User CF transmitting a file)
CFDP_PDU_count_4 = 376
cmd(f"{target_5} CF_CMD_TX_FILE with CFDP_CLASS 'CLASS_1', KEEP 1, CHAN_NUM 0, DEST_ID 1, SRC_FILENAME '/cf/Jojo2.jpg', DST_FILENAME '/cf/Jojo2_in_space.jpg'")

wait_check(f"{target_1} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_RECEIVED == {CFDP_PDU_count_3 + CFDP_PDU_count_4}", 300)
wait(10)

## Print counter values
LUNAR_CHANNEL_1_REG_STATE = tlm(f"{target_1} BPNODE_CHAN_CON_STAT_HK CHAN_STAT_REG_STATE_1")
print("Lunar User Node Channel 1 Registration State:", LUNAR_CHANNEL_1_REG_STATE)
LUNAR_BUNDLE_COUNT_DELETED = tlm(f"{target_1} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_DELETED")
print("Lunar User Node Bundles Deleted:", LUNAR_BUNDLE_COUNT_DELETED)
LUNAR_BUNDLE_COUNT_STORED = tlm(f"{target_1} BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED")
print("Lunar User Node Bundles Stored:", LUNAR_BUNDLE_COUNT_STORED)
LUNAR_BUNDLE_COUNT_ABANDONED = tlm(f"{target_1} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_ABANDONED")
print("Lunar User Node Bundles Abandoned:", LUNAR_BUNDLE_COUNT_ABANDONED)
LUNAR_BUNDLE_COUNT_DELIVERED = tlm(f"{target_1} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_DELIVERED")
print("Lunar User Node Bundles Delivered:", LUNAR_BUNDLE_COUNT_DELIVERED)
LUNAR_ADU_COUNT_DELIVERED = tlm(f"{target_1} BPNODE_NODE_MIB_COUNTERS_HK ADU_COUNT_DELIVERED")
print("Lunar User Node ADUs Delivered:", LUNAR_ADU_COUNT_DELIVERED)
LUNAR_CFDP_PDU_COUNT_RECEIVED = tlm(f"{target_1} CF_HK CHANNEL_HK_0_COUNTERS_RECV_PDU")
print("Lunar User Node CFDP PDUs received:", LUNAR_CFDP_PDU_COUNT_RECEIVED)

## Verify that bundles are abandoned
assert LUNAR_BUNDLE_COUNT_DELETED == CFDP_PDU_count_3 + CFDP_PDU_count_4
assert LUNAR_BUNDLE_COUNT_STORED == 0
assert LUNAR_BUNDLE_COUNT_ABANDONED == CFDP_PDU_count_4
assert LUNAR_BUNDLE_COUNT_DELIVERED == CFDP_PDU_count_3
assert LUNAR_ADU_COUNT_DELIVERED == CFDP_PDU_count_3
#assert LUNAR_CFDP_PDU_COUNT_RECEIVED == CFDP_PDU_count_3          DR DTNN-1492

## Verify requirements
rqmnt_status["DTN.5.00782"] = "P"
rqmnt_status["DTN.5.00784"] = "P"
rqmnt_status["DTN.5.00900"] = "P"
rqmnt_status["DTN.5.00940"] = "P"

## Turn off Lunar User BPNode Debug events
cmd(f"{target_5} CFE_EVS_CMD_DISABLE_EVENT_TYPE with BIT_MASK 1")

## Reset all counters
cmd(f"{target_1} BPNODE_CMD_RESET_ALL_COUNTERS")
wait(1)
cmd(f"{target_2} BPNODE_CMD_RESET_ALL_COUNTERS")
wait(1)
cmd(f"{target_3} BPNODE_CMD_RESET_ALL_COUNTERS")
wait(1)
cmd(f"{target_4} BPNODE_CMD_RESET_ALL_COUNTERS")
wait(1)
cmd(f"{target_5} BPNODE_CMD_RESET_ALL_COUNTERS")
wait(10)

## Reset all CFDP counters
cmd(f"{target_1} CF_CMD_RESET")
wait(1)
cmd(f"{target_5} CF_CMD_RESET")
wait(10)

##-------------------------------------------------------------------------------------------------------------------
## 11 MULTIPLE OVERLAPPING CONTACTS
##-------------------------------------------------------------------------------------------------------------------

## Set up and start Contact 2 on Relay and NSN Nodes
cmd(f"{target_2} BPNODE_CMD_CONTACT_SETUP with CONTACT_ID 2")
wait(1)
cmd(f"{target_2} BPNODE_CMD_CONTACT_START with CONTACT_ID 2")
wait(1)
cmd(f"{target_4} BPNODE_CMD_CONTACT_SETUP with CONTACT_ID 2")
wait(1)
cmd(f"{target_4} BPNODE_CMD_CONTACT_START with CONTACT_ID 2")
wait(10)

## Receive bundle set #1 from the NSN Node
stash_set('bundle_set_size', 1000000)
stash_set('receive_port', 4557)
stash_set('max_duration', 300)
id_11 = script_run("FLEET/procedures/bundles_receive_script.py")
wait(5)

## Send bundle set #1 to the Relay Node (for passthrough)
stash_set('dest_number', 205)
stash_set('dest_service', 3)
stash_set('payload_size', 2000)
stash_set('lifetime_in_sec', 600)
stash_set('total_send_loops', 10000)
stash_set('send_to_ip', relay_ip)
stash_set('send_to_port', 4556)
stash_set('rate_limit', 45)
id_12 = script_run("FLEET/procedures/bundles_send_script.py")
wait(20)

# Create and send new bundes from the Lunar User Node
CFDP_PDU_count_5 = 3203
cmd(f"{target_1} CF_CMD_TX_FILE with CFDP_CLASS 'CLASS_1', KEEP 1, CHAN_NUM 0, DEST_ID 2, SRC_FILENAME '/cf/Jojo4.jpg', DST_FILENAME '/cf/Jojo4_on_earth.jpg'")
wait(40)

## Send bundle set #2 to the Relay Node (for storage at NSN Node)
stash_set('dest_number', 206)
stash_set('dest_service', 3)
stash_set('payload_size', 2000)
stash_set('lifetime_in_sec', 600)
stash_set('total_send_loops', 4000)
stash_set('send_to_ip', relay_ip)
stash_set('send_to_port', 4558)
stash_set('rate_limit', 20)
id_13 = script_run("FLEET/procedures/bundles_send_script.py")
Lifetime_2_Start = time.time()
print(f"Lifetime 2 Start = {Lifetime_2_Start}")
wait(300)

## Print counter values
LUNAR_CFDP_PDU_COUNT_SENT = tlm(f"{target_1} CF_HK CHANNEL_HK_0_COUNTERS_SENT_PDU")
print("Lunar User Node CFDP PDUs Sent:", LUNAR_CFDP_PDU_COUNT_SENT)
LUNAR_ADU_COUNT_RECEIVED = tlm(f"{target_1} BPNODE_NODE_MIB_COUNTERS_HK ADU_COUNT_RECEIVED")
print("Lunar User Node ADUs Received:", LUNAR_ADU_COUNT_RECEIVED)
LUNAR_BUNDLE_COUNT_FORWARDED = tlm(f"{target_1} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_FORWARDED")
print("Lunar User Node Bundles Forwarded:", LUNAR_BUNDLE_COUNT_FORWARDED)

RELAY_BUNDLE_COUNT_RECEIVED = tlm(f"{target_2} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_RECEIVED")
print("Relay Node Bundles Received:", RELAY_BUNDLE_COUNT_RECEIVED)
RELAY_BUNDLE_COUNT_FORWARDED = tlm(f"{target_2} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_FORWARDED")
print("Relay Node Bundles Forwarded:", RELAY_BUNDLE_COUNT_FORWARDED)

GROUND_BUNDLE_COUNT_RECEIVED = tlm(f"{target_3} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_RECEIVED")
print("Ground Node Bundles Received:", GROUND_BUNDLE_COUNT_RECEIVED)
GROUND_BUNDLE_COUNT_FORWARDED = tlm(f"{target_3} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_FORWARDED")
print("Ground Node Bundles Forwarded:", GROUND_BUNDLE_COUNT_FORWARDED)

NSN_BUNDLE_COUNT_RECEIVED = tlm(f"{target_4} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_RECEIVED")
print("NSN Node Bundles Received:", NSN_BUNDLE_COUNT_RECEIVED)
NSN_BUNDLE_COUNT_STORED = tlm(f"{target_4} BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED")
print("NSN Node Bundles Stored:", NSN_BUNDLE_COUNT_STORED)
NSN_BUNDLE_COUNT_DELETED_EXPIRED = tlm(f"{target_4} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_DELETED_EXPIRED")
print("NSN Node Bundles Deleted Expired:", NSN_BUNDLE_COUNT_DELETED_EXPIRED)
NSN_BUNDLE_COUNT_FORWARDED = tlm(f"{target_4} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_FORWARDED")
print("NSN Node Bundles Forwarded:", NSN_BUNDLE_COUNT_FORWARDED)

DTN_TOOLS_BUNDLE_COUNT_RECEIVED = stash_get('bundles_received')
print("DTN Tools Bundles Received:", DTN_TOOLS_BUNDLE_COUNT_RECEIVED)

EARTH_BUNDLE_COUNT_RECEIVED = tlm(f"{target_5} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_RECEIVED")
print("Earth User Node Bundles Received:", EARTH_BUNDLE_COUNT_RECEIVED)
EARTH_ADU_COUNT_DELIVERED = tlm(f"{target_5} BPNODE_NODE_MIB_COUNTERS_HK ADU_COUNT_DELIVERED")
print("Earth User Node ADUs Delivered:", EARTH_ADU_COUNT_DELIVERED)
EARTH_CFDP_PDU_COUNT_RECEIVED = tlm(f"{target_5} CF_HK CHANNEL_HK_0_COUNTERS_RECV_PDU")
print("Earth User Node CFDP PDUs received:", EARTH_CFDP_PDU_COUNT_RECEIVED)

## Verify successful data transfer
assert LUNAR_CFDP_PDU_COUNT_SENT == CFDP_PDU_count_5
assert LUNAR_ADU_COUNT_RECEIVED == CFDP_PDU_count_5
assert LUNAR_BUNDLE_COUNT_FORWARDED == CFDP_PDU_count_5
assert RELAY_BUNDLE_COUNT_RECEIVED == 700000 + CFDP_PDU_count_5
assert RELAY_BUNDLE_COUNT_FORWARDED == 700000 + CFDP_PDU_count_5
assert GROUND_BUNDLE_COUNT_RECEIVED == 700000 + CFDP_PDU_count_5
assert GROUND_BUNDLE_COUNT_FORWARDED == 700000 + CFDP_PDU_count_5
assert NSN_BUNDLE_COUNT_RECEIVED == 700000 + CFDP_PDU_count_5
assert NSN_BUNDLE_COUNT_STORED == 200000
assert NSN_BUNDLE_COUNT_DELETED_EXPIRED == 0
assert NSN_BUNDLE_COUNT_FORWARDED == 500000 + CFDP_PDU_count_5
assert EARTH_BUNDLE_COUNT_RECEIVED == CFDP_PDU_count_5
assert EARTH_ADU_COUNT_DELIVERED == CFDP_PDU_count_5
assert EARTH_CFDP_PDU_COUNT_RECEIVED == CFDP_PDU_count_5

## Verify requirements
rqmnt_status["DTN.5.00165"] = "P"

##-------------------------------------------------------------------------------------------------------------------
## 12 HANDLING OF EXPIRED BUNDLES, PART #2 (MAX ALLOWED LIFETIME)
##-------------------------------------------------------------------------------------------------------------------

##-------------------------------------------------------------------------------------------------------------------
## 12.1 Expiration based on Maximum Allowed Lifetime and using the Bundle Age Block
##-------------------------------------------------------------------------------------------------------------------

## Set NSN Node time source to invalid
cmd(f"{target_4} CFE_TIME_CMD_SET_STATE with CLOCK_STATE 'INVALID'")

## Wait for all stored bundles to have been expired
wait_check(f"{target_4} BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED == 0", 300)
Lifetime_2_Stop = time.time()
print(f"Lifetime 2 Stop = {Lifetime_2_Stop}")
Actual_Lifetime_2 = Lifetime_2_Stop - Lifetime_2_Start
print(f"Actual Lifetime 2 = {Actual_Lifetime_2}")
wait(30)

## Print counter values
NSN_BUNDLE_COUNT_STORED = tlm(f"{target_4} BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED")
print("NSN Node Bundles Stored:", NSN_BUNDLE_COUNT_STORED)
NSN_BUNDLE_COUNT_DELETED_EXPIRED = tlm(f"{target_4} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_DELETED_EXPIRED")
print("NSN Node Bundles Deleted Expired:", NSN_BUNDLE_COUNT_DELETED_EXPIRED)

## Verify successful bundle expiration from storage
assert NSN_BUNDLE_COUNT_STORED == 0
assert NSN_BUNDLE_COUNT_DELETED_EXPIRED == 200000
assert 420 <= Actual_Lifetime_2 <= 450

## Verify requirements
rqmnt_status["DTN.5.00090"] = "P"
rqmnt_status["DTN.5.00800"] = "P"
rqmnt_status["DTN.5.00820"] = "P"
rqmnt_status["DTN.6.04195"] = "P"

## Return NSN Node time source to valid
cmd(f"{target_4} CFE_TIME_CMD_SET_STATE with CLOCK_STATE 'VALID'")

##-------------------------------------------------------------------------------------------------------------------
## 13 TEST CLEANUP
##-------------------------------------------------------------------------------------------------------------------

## Stop all contacts on all nodes
cmd(f"{target_1} BPNODE_CMD_CONTACT_STOP with CONTACT_ID 0")
wait(1)
cmd(f"{target_2} BPNODE_CMD_CONTACT_STOP with CONTACT_ID 0")
wait(1)
cmd(f"{target_2} BPNODE_CMD_CONTACT_STOP with CONTACT_ID 1")
wait(1)
cmd(f"{target_2} BPNODE_CMD_CONTACT_STOP with CONTACT_ID 2")
wait(1)
cmd(f"{target_3} BPNODE_CMD_CONTACT_STOP with CONTACT_ID 0")
wait(1)
cmd(f"{target_3} BPNODE_CMD_CONTACT_STOP with CONTACT_ID 1")
wait(1)
cmd(f"{target_4} BPNODE_CMD_CONTACT_STOP with CONTACT_ID 0")
wait(1)
cmd(f"{target_4} BPNODE_CMD_CONTACT_STOP with CONTACT_ID 1")
wait(1)
cmd(f"{target_4} BPNODE_CMD_CONTACT_STOP with CONTACT_ID 2")
wait(1)
cmd(f"{target_5} BPNODE_CMD_CONTACT_STOP with CONTACT_ID 0")
wait(1)

## Tear down Contact 0 on all nodes
cmd(f"{target_1} BPNODE_CMD_CONTACT_TEARDOWN with CONTACT_ID 0")
wait(1)
cmd(f"{target_2} BPNODE_CMD_CONTACT_TEARDOWN with CONTACT_ID 0")
wait(1)
cmd(f"{target_2} BPNODE_CMD_CONTACT_TEARDOWN with CONTACT_ID 1")
wait(1)
cmd(f"{target_2} BPNODE_CMD_CONTACT_TEARDOWN with CONTACT_ID 2")
wait(1)
cmd(f"{target_3} BPNODE_CMD_CONTACT_TEARDOWN with CONTACT_ID 0")
wait(1)
cmd(f"{target_3} BPNODE_CMD_CONTACT_TEARDOWN with CONTACT_ID 1")
wait(1)
cmd(f"{target_4} BPNODE_CMD_CONTACT_TEARDOWN with CONTACT_ID 0")
wait(1)
cmd(f"{target_4} BPNODE_CMD_CONTACT_TEARDOWN with CONTACT_ID 1")
wait(1)
cmd(f"{target_4} BPNODE_CMD_CONTACT_TEARDOWN with CONTACT_ID 2")
wait(1)
cmd(f"{target_5} BPNODE_CMD_CONTACT_TEARDOWN with CONTACT_ID 0")
wait(1)

## Stop and remove all channels on Lunar User and Earth User Nodes
cmd(f"{target_1} BPNODE_CMD_STOP_APPLICATION with CHAN_ID 0")
wait(1)
cmd(f"{target_1} BPNODE_CMD_REMOVE_APPLICATION with CHAN_ID 0")
wait(1)
cmd(f"{target_1} BPNODE_CMD_STOP_APPLICATION with CHAN_ID 1")
wait(1)
cmd(f"{target_1} BPNODE_CMD_REMOVE_APPLICATION with CHAN_ID 1")
wait(1)
cmd(f"{target_5} BPNODE_CMD_STOP_APPLICATION with CHAN_ID 0")
wait(1)
cmd(f"{target_5} BPNODE_CMD_REMOVE_APPLICATION with CHAN_ID 0")
wait(1)
cmd(f"{target_5} BPNODE_CMD_STOP_APPLICATION with CHAN_ID 1")
wait(1)
cmd(f"{target_5} BPNODE_CMD_REMOVE_APPLICATION with CHAN_ID 1")
wait(1)

## Reset all counters
cmd(f"{target_1} BPNODE_CMD_RESET_ALL_COUNTERS")
wait(1)
cmd(f"{target_2} BPNODE_CMD_RESET_ALL_COUNTERS")
wait(1)
cmd(f"{target_3} BPNODE_CMD_RESET_ALL_COUNTERS")
wait(1)
cmd(f"{target_4} BPNODE_CMD_RESET_ALL_COUNTERS")
wait(1)
cmd(f"{target_5} BPNODE_CMD_RESET_ALL_COUNTERS")
wait(1)

## Reset all CFDP counters
cmd(f"{target_1} CF_CMD_RESET")
wait(1)
cmd(f"{target_5} CF_CMD_RESET")
wait(10)

## Stop running scripts
running_script_stop(id_1)
running_script_stop(id_2)
running_script_stop(id_3)
running_script_stop(id_4)
running_script_stop(id_5)

## Print Requirement Status
for key, value in rqmnt_status.items():
    print(f"***    {key}: {value}")
