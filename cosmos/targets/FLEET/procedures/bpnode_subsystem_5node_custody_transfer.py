##*******************************************************************************************************************
##
## Subsystem Test Case - End to End (ETE) Transfer with Custody Transfer
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
load_utility("FLEET/procedures/bpnode_initialization.py")

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

## Select whether to set up delay or disruption

ct_with_packet_loss = message_box("Select whether to introduce packet loss between the Lunar User Node and the Relay Node", 'yes', 'no')
if ct_with_packet_loss == "yes":
    ## Set up condition for bundle retransmission due to expiration of the retransmission timer
    prompt("On the Lunar User and Relay Nodes, set up a (one-way) 1% packet loss between the Lunar User Node and the Relay Node")
    ct_with_delay = "no"

if ct_with_packet_loss == "no":
    ct_with_delay = message_box("Select whether to introduce a delay between the Lunar User Node and the Relay Node", 'yes', 'no')
    if ct_with_delay == "yes":
        ## Set up condition for bundle retransmission due to expiration of the retransmission timer
        prompt("On the Lunar User and Relay Nodes, set up a (one-way) 20 second delay between the Lunar User Node and the Relay Node")

## Start capture of IP traffic on the Earth Node
prompt("Start a Wireshark capture of bundles on the Relay Node (capture filter: 'udp port 4556', interface: 'ens5'")

## Initialize requirement status
rqmnt_status = {
    "DTN.5.00142":"U",
    "DTN.5.00220":"U",
    "DTN.5.00250":"P",
    "DTN.5.00382":"U",
    "DTN.5.00390":"U",
    "DTN.5.00400":"U",
    "DTN.5.00410":"U",
    "DTN.5.00440":"U",
    "DTN.5.00460":"U",
    "DTN.5.00480":"U",
    "DTN.5.00490":"U",
    "DTN.5.00495":"U",
    "DTN.5.00500":"U",
    "DTN.5.00720":"U",
    "DTN.5.00721":"U",
    "DTN.5.00782":"U",
    "DTN.5.00784":"U",
    "DTN.5.00788":"U",
    "DTN.5.00940":"U",
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

cmd(f"{target_1} BPNODE_CMD_ADD_APPLICATION with CHAN_ID 1")
wait(1)
cmd(f"{target_1} BPNODE_CMD_START_APPLICATION with CHAN_ID 1")
wait(5)

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

## Set up Contacts 0, 1, and 2
cmd(f"{target_2} BPNODE_CMD_CONTACT_SETUP with CONTACT_ID 0")
wait(1)
cmd(f"{target_2} BPNODE_CMD_CONTACT_SETUP with CONTACT_ID 1")
wait(1)

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
## 3 RETURN TRANSFER #1
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
LUNAR_BUNDLE_COUNT_IN_CUSTODY = tlm(f"{target_1} BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_IN_CUSTODY")
print("Lunar User Node Bundles In Custody:", LUNAR_BUNDLE_COUNT_IN_CUSTODY)

## Verify successful data creation
assert LUNAR_CFDP_PDU_COUNT_SENT == CFDP_PDU_count_1
assert LUNAR_ADU_COUNT_RECEIVED == CFDP_PDU_count_1
assert LUNAR_BUNDLE_COUNT_GENERATED_ACCEPTED == CFDP_PDU_count_1
assert LUNAR_BUNDLE_COUNT_STORED == CFDP_PDU_count_1
assert LUNAR_BUNDLE_COUNT_IN_CUSTODY == CFDP_PDU_count_1

## Verify requirements
rqmnt_status["DTN.5.00142"] = "P"

## Start Contact 0 on the Lunar User and Relay Nodes
cmd(f"{target_2} BPNODE_CMD_CONTACT_START with CONTACT_ID 0")
wait(1)
cmd(f"{target_1} BPNODE_CMD_CONTACT_START with CONTACT_ID 0")

if ct_with_packet_loss == "yes" or ct_with_delay == "yes":
    ## Capture bundle retransmission information
    wait_check(f"{target_1} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_FORWARDED > 0", 20)
    Retransmission_Timer_Start = time.time()
    print(f"Retransmission Timer Start = {Retransmission_Timer_Start}")
    wait_check(f"{target_1} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_CUSTODY_RE_FORWARDED > 0", 40)
    Retransmission_Timer_End = time.time()
    print(f"Retransmission Timer End = {Retransmission_Timer_End}")
    Retransmission_Time = Retransmission_Timer_End - Retransmission_Timer_Start
    print(f"Retransmission Time = {Retransmission_Time}")
    wait(40)

wait(5)

## Verify that bundles are retransmitted correctly
if ct_with_packet_loss == "yes":
    assert Retransmission_Time < 30
elif ct_with_delay == "yes":
    assert 25 <= Retransmission_Time <= 35

## Verify requirements
if ct_with_packet_loss == "yes":
    rqmnt_status["DTN.5.00721"] = "P"
elif ct_with_delay == "yes":
    rqmnt_status["DTN.5.00720"] = "P"

## Wait for custody of all bundles to have been transferred to the Relay Node
wait_check(f"{target_1} BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_IN_CUSTODY == 0", 300)
wait(30)

## Print counter values
LUNAR_BUNDLE_COUNT_STORED = tlm(f"{target_1} BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED")
print("Lunar User Node Bundles Stored:", LUNAR_BUNDLE_COUNT_STORED)
LUNAR_BUNDLE_COUNT_FORWARDED = tlm(f"{target_1} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_FORWARDED")
print("Lunar User Node Bundles Forwarded:", LUNAR_BUNDLE_COUNT_FORWARDED)

RELAY_BUNDLE_COUNT_RECEIVED = tlm(f"{target_2} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_RECEIVED")
print("Relay Node Bundles Received:", RELAY_BUNDLE_COUNT_RECEIVED)
RELAY_BUNDLE_COUNT_STORED = tlm(f"{target_2} BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED")
print("Relay Node Bundles Stored:", RELAY_BUNDLE_COUNT_STORED)

LUNAR_BUNDLE_COUNT_IN_CUSTODY = tlm(f"{target_1} BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_IN_CUSTODY")
print("Lunar User Node Bundles In Custody:", LUNAR_BUNDLE_COUNT_IN_CUSTODY)
LUNAR_BUNDLE_COUNT_CCS_RECEIVED = tlm(f"{target_1} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_CCS_RECEIVED")
print("Lunar User Node CCS Received:", LUNAR_BUNDLE_COUNT_CCS_RECEIVED)
LUNAR_BUNDLE_COUNT_RECEIVED_CUSTODY_SIGNAL = tlm(f"{target_1} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_RECEIVED_CUSTODY_SIGNAL")
print("Lunar User Node Bundles for which Custody Signal has been Received:", LUNAR_BUNDLE_COUNT_RECEIVED_CUSTODY_SIGNAL)
LUNAR_BUNDLE_COUNT_CUSTODY_TRANSFERRED = tlm(f"{target_1} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_CUSTODY_TRANSFERRED")
print("Lunar User Node Bundles for which Custody has been Transferred to the next Custodian Node:", LUNAR_BUNDLE_COUNT_CUSTODY_TRANSFERRED)
LUNAR_BUNDLE_COUNT_CUSTODY_RE_FORWARDED = tlm(f"{target_1} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_CUSTODY_RE_FORWARDED")
print("Lunar User Node Bundles Re-Forwarded:", LUNAR_BUNDLE_COUNT_CUSTODY_RE_FORWARDED)

RELAY_BUNDLE_COUNT_CUSTODY_REQUEST = tlm(f"{target_2} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_CUSTODY_REQUEST")
print("Relay Node Bundles that are Requesting Custody:", RELAY_BUNDLE_COUNT_CUSTODY_REQUEST)
RELAY_BUNDLE_COUNT_IN_CUSTODY = tlm(f"{target_2} BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_IN_CUSTODY")
print("Relay Node Bundles In Custody:", RELAY_BUNDLE_COUNT_IN_CUSTODY)
RELAY_BUNDLE_COUNT_GENERATED_CCS = tlm(f"{target_2} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_GENERATED_CCS")
print("Relay Node Generated CCS:", RELAY_BUNDLE_COUNT_GENERATED_CCS)
RELAY_BUNDLE_COUNT_GENERATED_CUSTODY_SIGNAL = tlm(f"{target_2} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_GENERATED_CUSTODY_SIGNAL")
print("Relay Node Bundles for which Custody Signal has been Generated:", RELAY_BUNDLE_COUNT_GENERATED_CUSTODY_SIGNAL)

## Verify successful data transfer
assert LUNAR_BUNDLE_COUNT_STORED == 0
assert LUNAR_BUNDLE_COUNT_FORWARDED >= CFDP_PDU_count_1
assert RELAY_BUNDLE_COUNT_RECEIVED >= CFDP_PDU_count_1
assert RELAY_BUNDLE_COUNT_STORED == CFDP_PDU_count_1

assert LUNAR_BUNDLE_COUNT_IN_CUSTODY == 0
assert LUNAR_BUNDLE_COUNT_CCS_RECEIVED > 0
assert LUNAR_BUNDLE_COUNT_RECEIVED_CUSTODY_SIGNAL >= CFDP_PDU_count_1
assert LUNAR_BUNDLE_COUNT_CUSTODY_TRANSFERRED == CFDP_PDU_count_1
if ct_with_delay == "yes":
    assert RELAY_BUNDLE_COUNT_CUSTODY_REQUEST == CFDP_PDU_count_1 * 2
assert RELAY_BUNDLE_COUNT_IN_CUSTODY == CFDP_PDU_count_1
assert RELAY_BUNDLE_COUNT_GENERATED_CCS > 0
if ct_with_delay == "yes":
    assert RELAY_BUNDLE_COUNT_GENERATED_CUSTODY_SIGNAL == CFDP_PDU_count_1 * 2
if ct_with_packet_loss == "yes" or ct_with_delay == "yes":
    assert LUNAR_BUNDLE_COUNT_CUSTODY_RE_FORWARDED > 0

## Verify requirements
rqmnt_status["DTN.5.00382"] = "P"
rqmnt_status["DTN.5.00390"] = "P"
rqmnt_status["DTN.5.00400"] = "P"
rqmnt_status["DTN.5.00460"] = "P"
rqmnt_status["DTN.5.00480"] = "P"
rqmnt_status["DTN.5.00490"] = "P"
rqmnt_status["DTN.5.00940"] = "P"
if ct_with_packet_loss == "yes":
    rqmnt_status["DTN.5.00721"] = "P"

##-------------------------------------------------------------------------------------------------------------------
## 3.3 Execution of the subsequent hops (Relay Node -> Ground Node -> NSN Node -> Earth User Node)
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

## Wait for custody of all bundles to have been transferred to the Earth User Node
wait_check(f"{target_3} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_RECEIVED >= {CFDP_PDU_count_1}", 300)
wait_check(f"{target_4} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_RECEIVED >= {CFDP_PDU_count_1}", 300)
wait_check(f"{target_5} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_RECEIVED >= {CFDP_PDU_count_1}", 300)
wait(30)

## Print counter values
RELAY_BUNDLE_COUNT_FORWARDED = tlm(f"{target_2} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_FORWARDED")
print("Relay Node Bundles Forwarded:", RELAY_BUNDLE_COUNT_FORWARDED)
RELAY_BUNDLE_COUNT_STORED = tlm(f"{target_2} BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED")
print("Relay Node Bundles Stored:", RELAY_BUNDLE_COUNT_STORED)
RELAY_BUNDLE_COUNT_IN_CUSTODY = tlm(f"{target_2} BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_IN_CUSTODY")
print("Relay Node Bundles In Custody:", RELAY_BUNDLE_COUNT_IN_CUSTODY)
RELAY_BUNDLE_COUNT_CUSTODY_TRANSFERRED = tlm(f"{target_2} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_CUSTODY_TRANSFERRED")
print("Relay Node Bundles for which Custody has been Transferred to the next Custodian Node:", RELAY_BUNDLE_COUNT_CUSTODY_TRANSFERRED)

GROUND_BUNDLE_COUNT_RECEIVED = tlm(f"{target_3} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_RECEIVED")
print("Ground Node Bundles Received:", GROUND_BUNDLE_COUNT_RECEIVED)
GROUND_BUNDLE_COUNT_DELETED = tlm(f"{target_3} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_DELETED")
print("Ground Node Bundles Deleted:", GROUND_BUNDLE_COUNT_DELETED)
GROUND_BUNDLE_COUNT_STORED = tlm(f"{target_3} BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED")
print("Ground Node Bundles Stored:", GROUND_BUNDLE_COUNT_STORED)
GROUND_BUNDLE_COUNT_FORWARDED = tlm(f"{target_3} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_FORWARDED")
print("Ground Node Bundles Forwarded:", GROUND_BUNDLE_COUNT_FORWARDED)
GROUND_BUNDLE_COUNT_IN_CUSTODY = tlm(f"{target_3} BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_IN_CUSTODY")
print("Ground Node Bundles In Custody:", GROUND_BUNDLE_COUNT_IN_CUSTODY)
GROUND_BUNDLE_COUNT_CUSTODY_TRANSFERRED = tlm(f"{target_3} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_CUSTODY_TRANSFERRED")
print("Ground Node Bundles for which Custody has been Transferred to the next Custodian Node:", GROUND_BUNDLE_COUNT_CUSTODY_TRANSFERRED)

NSN_BUNDLE_COUNT_RECEIVED = tlm(f"{target_4} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_RECEIVED")
print("NSN Node Bundles Received:", NSN_BUNDLE_COUNT_RECEIVED)
NSN_BUNDLE_COUNT_DELETED = tlm(f"{target_4} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_DELETED")
print("NSN Node Bundles Deleted:", NSN_BUNDLE_COUNT_DELETED)
NSN_BUNDLE_COUNT_STORED = tlm(f"{target_4} BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED")
print("NSN Node Bundles Stored:", NSN_BUNDLE_COUNT_STORED)
NSN_BUNDLE_COUNT_FORWARDED = tlm(f"{target_4} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_FORWARDED")
print("NSN Node Bundles Forwarded:", NSN_BUNDLE_COUNT_FORWARDED)
NSN_BUNDLE_COUNT_IN_CUSTODY = tlm(f"{target_4} BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_IN_CUSTODY")
print("NSN Node Bundles In Custody:", NSN_BUNDLE_COUNT_IN_CUSTODY)
NSN_BUNDLE_COUNT_CUSTODY_TRANSFERRED = tlm(f"{target_4} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_CUSTODY_TRANSFERRED")
print("NSN Node Bundles for which Custody has been Transferred to the next Custodian Node:", NSN_BUNDLE_COUNT_CUSTODY_TRANSFERRED)

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
EARTH_BUNDLE_COUNT_IN_CUSTODY_1 = tlm(f"{target_5} BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_IN_CUSTODY")
print("Earth Node Bundles In Custody:", EARTH_BUNDLE_COUNT_IN_CUSTODY_1)
EARTH_BUNDLE_COUNT_CUSTODY_TRANSFERRED_1 = tlm(f"{target_5} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_CUSTODY_TRANSFERRED")
print("Earth Node Bundles for which Custody has been Transferred to the next Custodian Node:", EARTH_BUNDLE_COUNT_CUSTODY_TRANSFERRED_1)

## Verify successful data transfer
assert RELAY_BUNDLE_COUNT_STORED == 0
assert GROUND_BUNDLE_COUNT_STORED == 0
assert NSN_BUNDLE_COUNT_STORED == 0
assert EARTH_BUNDLE_COUNT_STORED == CFDP_PDU_count_1
assert EARTH_BUNDLE_COUNT_DELIVERED == 0
assert EARTH_ADU_COUNT_DELIVERED == 0
assert RELAY_BUNDLE_COUNT_IN_CUSTODY == 0
assert RELAY_BUNDLE_COUNT_CUSTODY_TRANSFERRED == CFDP_PDU_count_1
assert GROUND_BUNDLE_COUNT_IN_CUSTODY == 0
assert GROUND_BUNDLE_COUNT_CUSTODY_TRANSFERRED == CFDP_PDU_count_1
assert NSN_BUNDLE_COUNT_IN_CUSTODY == 0
assert NSN_BUNDLE_COUNT_CUSTODY_TRANSFERRED == CFDP_PDU_count_1
assert EARTH_BUNDLE_COUNT_IN_CUSTODY_1 == CFDP_PDU_count_1
assert EARTH_BUNDLE_COUNT_CUSTODY_TRANSFERRED_1 == 0

##-------------------------------------------------------------------------------------------------------------------
## 3.4 Earth User Node Service Setup and ADU Delivery
##-------------------------------------------------------------------------------------------------------------------

## Load ADU Proxy table
load_target_table('/cf/adu_earth.tbl', target_5) 

## Load Channel table
load_target_table('/cf/cha_earth_ct.tbl', target_5)

## Load CF configuration table
cmd(f"{target_5} CF_CMD_DISABLE_ENGINE")
load_target_table('/cf/cf_earth.tbl', target_5)
cmd(f"{target_5} CF_CMD_ENABLE_ENGINE")

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

## Wait for all bundles to have been delivered by the Earth User Node
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
EARTH_BUNDLE_COUNT_IN_CUSTODY_2 = tlm(f"{target_5} BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_IN_CUSTODY")
print("Earth Node Bundles In Custody:", EARTH_BUNDLE_COUNT_IN_CUSTODY_2)
EARTH_BUNDLE_COUNT_CUSTODY_TRANSFERRED_2 = tlm(f"{target_5} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_CUSTODY_TRANSFERRED")
print("Earth Node Bundles for which Custody has been Transferred to the next Custodian Node:", EARTH_BUNDLE_COUNT_CUSTODY_TRANSFERRED_2)

## Verify successful data transfer
assert EARTH_BUNDLE_COUNT_DELETED >= CFDP_PDU_count_1
assert EARTH_BUNDLE_COUNT_STORED == 0
assert EARTH_BUNDLE_COUNT_DELIVERED == CFDP_PDU_count_1
assert EARTH_ADU_COUNT_DELIVERED == CFDP_PDU_count_1
assert EARTH_CFDP_PDU_COUNT_RECEIVED == CFDP_PDU_count_1
assert EARTH_BUNDLE_COUNT_IN_CUSTODY_2 == 0
assert EARTH_BUNDLE_COUNT_CUSTODY_TRANSFERRED_2 == 0

prompt("Stop the Wireshark capture")
prompt("For any bundle, expand DTN Bundle Protocol Version 7")
if ct_with_packet_loss == "yes" or ct_with_delay == "yes":
    prompt("Export the bundle data to a plain text file (using File/Export Packet Dissections)")
prompt("Verify that the bundle contains a Type 13 extension block with block number 5")
prompt("Save the Wireshark capture as an artifact")

## Verify requirements
rqmnt_status["DTN.5.00220"] = "P"

if ct_with_delay == "yes":
    ## Remove condition for bundle retransmission due to expiration of the retransmission timer
    prompt("On the Lunar User and Relay Nodes, remove the two-way 20 second delay between the Lunar User Node and the Relay Node")

##-------------------------------------------------------------------------------------------------------------------
## 4 RETURN TRANSFER #2
##-------------------------------------------------------------------------------------------------------------------

## Start creating bundles (CF transmitting a second file)
CFDP_PDU_count_2 = 3203
cmd(f"{target_1} CF_CMD_TX_FILE with CFDP_CLASS 'CLASS_1', KEEP 1, CHAN_NUM 0, DEST_ID 2, SRC_FILENAME '/cf/Jojo4.jpg', DST_FILENAME '/cf/Jojo4_on_earth.jpg'")
wait(20)

## Wait for custody of all bundles to have been transferred to the Earth User Node
wait_check(f"{target_2} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_RECEIVED >= {CFDP_PDU_count_1 + CFDP_PDU_count_2}", 300)
wait_check(f"{target_3} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_RECEIVED >= {CFDP_PDU_count_1 + CFDP_PDU_count_2}", 300)
wait_check(f"{target_4} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_RECEIVED >= {CFDP_PDU_count_1 + CFDP_PDU_count_2}", 300)
wait_check(f"{target_5} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_RECEIVED >= {CFDP_PDU_count_1 + CFDP_PDU_count_2}", 300)
wait(60)

## Print counter values
LUNAR_CFDP_PDU_COUNT_SENT = tlm(f"{target_1} CF_HK CHANNEL_HK_0_COUNTERS_SENT_PDU")
print("Lunar User Node CFDP PDUs Sent:", LUNAR_CFDP_PDU_COUNT_SENT)
LUNAR_ADU_COUNT_RECEIVED = tlm(f"{target_1} BPNODE_NODE_MIB_COUNTERS_HK ADU_COUNT_RECEIVED")
print("Lunar User Node ADUs Received:", LUNAR_ADU_COUNT_RECEIVED)
LUNAR_BUNDLE_COUNT_STORED = tlm(f"{target_1} BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED")
print("Lunar User Node Bundles Stored:", LUNAR_BUNDLE_COUNT_STORED)
LUNAR_BUNDLE_COUNT_IN_CUSTODY = tlm(f"{target_1} BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_IN_CUSTODY")
print("Lunar User Node Bundles In Custody:", LUNAR_BUNDLE_COUNT_IN_CUSTODY)
LUNAR_BUNDLE_COUNT_CUSTODY_TRANSFERRED = tlm(f"{target_1} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_CUSTODY_TRANSFERRED")
print("Lunar User Node Bundles for which Custody has been Transferred to the next Custodian Node:", LUNAR_BUNDLE_COUNT_CUSTODY_TRANSFERRED)

RELAY_BUNDLE_COUNT_STORED = tlm(f"{target_2} BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED")
print("Relay Node Bundles Stored:", RELAY_BUNDLE_COUNT_STORED)
RELAY_BUNDLE_COUNT_IN_CUSTODY = tlm(f"{target_2} BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_IN_CUSTODY")
print("Relay Node Bundles In Custody:", RELAY_BUNDLE_COUNT_IN_CUSTODY)
RELAY_BUNDLE_COUNT_CUSTODY_TRANSFERRED = tlm(f"{target_2} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_CUSTODY_TRANSFERRED")
print("Relay Node Bundles for which Custody has been Transferred to the next Custodian Node:", RELAY_BUNDLE_COUNT_CUSTODY_TRANSFERRED)

GROUND_BUNDLE_COUNT_STORED = tlm(f"{target_3} BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED")
print("Ground Node Bundles Stored:", GROUND_BUNDLE_COUNT_STORED)
GROUND_BUNDLE_COUNT_IN_CUSTODY = tlm(f"{target_3} BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_IN_CUSTODY")
print("Ground Node Bundles In Custody:", GROUND_BUNDLE_COUNT_IN_CUSTODY)
GROUND_BUNDLE_COUNT_CUSTODY_TRANSFERRED = tlm(f"{target_3} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_CUSTODY_TRANSFERRED")
print("Ground Node Bundles for which Custody has been Transferred to the next Custodian Node:", GROUND_BUNDLE_COUNT_CUSTODY_TRANSFERRED)

NSN_BUNDLE_COUNT_STORED = tlm(f"{target_4} BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED")
print("NSN Node Bundles Stored:", NSN_BUNDLE_COUNT_STORED)
NSN_BUNDLE_COUNT_IN_CUSTODY = tlm(f"{target_4} BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_IN_CUSTODY")
print("NSN Node Bundles In Custody:", NSN_BUNDLE_COUNT_IN_CUSTODY)
NSN_BUNDLE_COUNT_CUSTODY_TRANSFERRED = tlm(f"{target_4} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_CUSTODY_TRANSFERRED")
print("NSN Node Bundles for which Custody has been Transferred to the next Custodian Node:", NSN_BUNDLE_COUNT_CUSTODY_TRANSFERRED)

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
EARTH_BUNDLE_COUNT_IN_CUSTODY = tlm(f"{target_5} BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_IN_CUSTODY")
print("Earth Node Bundles In Custody:", EARTH_BUNDLE_COUNT_IN_CUSTODY)
EARTH_BUNDLE_COUNT_CUSTODY_TRANSFERRED = tlm(f"{target_5} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_CUSTODY_TRANSFERRED")
print("Earth Node Bundles for which Custody has been Transferred to the next Custodian Node:", EARTH_BUNDLE_COUNT_CUSTODY_TRANSFERRED)

## Verify successful end to end data transmission
assert LUNAR_CFDP_PDU_COUNT_SENT == CFDP_PDU_count_1 + CFDP_PDU_count_2
assert LUNAR_ADU_COUNT_RECEIVED == CFDP_PDU_count_1 + CFDP_PDU_count_2
assert LUNAR_BUNDLE_COUNT_STORED == 0
assert RELAY_BUNDLE_COUNT_STORED == 0
assert GROUND_BUNDLE_COUNT_STORED == 0
assert NSN_BUNDLE_COUNT_STORED == 0
assert EARTH_BUNDLE_COUNT_RECEIVED >= CFDP_PDU_count_1 + CFDP_PDU_count_2
assert EARTH_BUNDLE_COUNT_STORED == 0
assert EARTH_BUNDLE_COUNT_DELIVERED >= CFDP_PDU_count_1 + CFDP_PDU_count_2
assert EARTH_ADU_COUNT_DELIVERED >= CFDP_PDU_count_1 + CFDP_PDU_count_2
assert EARTH_CFDP_PDU_COUNT_RECEIVED >= CFDP_PDU_count_1 + CFDP_PDU_count_2
assert LUNAR_BUNDLE_COUNT_IN_CUSTODY == 0
assert LUNAR_BUNDLE_COUNT_CUSTODY_TRANSFERRED == CFDP_PDU_count_1 + CFDP_PDU_count_2
assert RELAY_BUNDLE_COUNT_IN_CUSTODY == 0
assert RELAY_BUNDLE_COUNT_CUSTODY_TRANSFERRED >= CFDP_PDU_count_1 + CFDP_PDU_count_2
assert GROUND_BUNDLE_COUNT_IN_CUSTODY == 0
assert GROUND_BUNDLE_COUNT_CUSTODY_TRANSFERRED >= CFDP_PDU_count_1 + CFDP_PDU_count_2
assert NSN_BUNDLE_COUNT_IN_CUSTODY == 0
assert NSN_BUNDLE_COUNT_CUSTODY_TRANSFERRED >= CFDP_PDU_count_1 + CFDP_PDU_count_2
assert EARTH_BUNDLE_COUNT_IN_CUSTODY == 0
assert EARTH_BUNDLE_COUNT_CUSTODY_TRANSFERRED_1 == 0

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
## 5 FORWARD TRANSFERS
##-------------------------------------------------------------------------------------------------------------------

##-------------------------------------------------------------------------------------------------------------------
## 5.1 Channel Registration State Test #1 - Passive/Defer
##-------------------------------------------------------------------------------------------------------------------

## Change Lunar User Node Channel 1 registration state to passive/abandon
cmd(f"{target_1} BPNODE_CMD_SET_REGISTRATION_STATE with CHAN_ID 1, REG_STATE 'PASSIVE_DEFER'")
wait(10)

## Start Earth User to Lunar User data transfer (Earth User CF transmitting a file)
CFDP_PDU_count_3 = 900
cmd(f"{target_5} CF_CMD_TX_FILE with CFDP_CLASS 'CLASS_1', KEEP 1, CHAN_NUM 0, DEST_ID 1, SRC_FILENAME '/cf/Jojo1.jpg', DST_FILENAME '/cf/Jojo1_in_space.jpg'")
wait(20)

## Wait for custody of all bundles to have been transferred to the Lunar User Node
wait_check(f"{target_4} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_RECEIVED >= {CFDP_PDU_count_3}", 300)
wait_check(f"{target_3} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_RECEIVED >= {CFDP_PDU_count_3}", 300)
wait_check(f"{target_2} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_RECEIVED >= {CFDP_PDU_count_3}", 300)
wait_check(f"{target_1} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_RECEIVED >= {CFDP_PDU_count_3}", 300)
wait(60)

## Print counter values
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
LUNAR_BUNDLE_COUNT_IN_CUSTODY = tlm(f"{target_1} BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_IN_CUSTODY")
print("Lunar User Node Bundles In Custody:", LUNAR_BUNDLE_COUNT_IN_CUSTODY)
LUNAR_BUNDLE_COUNT_CUSTODY_TRANSFERRED = tlm(f"{target_1} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_CUSTODY_TRANSFERRED")
print("Lunar User Node Bundles for which Custody has been Transferred to the next Custodian Node:", LUNAR_BUNDLE_COUNT_CUSTODY_TRANSFERRED)

## Verify successful data reception
assert LUNAR_BUNDLE_COUNT_STORED == CFDP_PDU_count_3
assert LUNAR_BUNDLE_COUNT_ABANDONED == 0
assert LUNAR_BUNDLE_COUNT_DELIVERED == 0
assert LUNAR_ADU_COUNT_DELIVERED == 0
assert LUNAR_CFDP_PDU_COUNT_RECEIVED == 0
assert LUNAR_BUNDLE_COUNT_IN_CUSTODY == CFDP_PDU_count_3
assert LUNAR_BUNDLE_COUNT_CUSTODY_TRANSFERRED == 0

## Change Lunar User Node Channel 1 registration state to active
cmd(f"{target_1} BPNODE_CMD_SET_REGISTRATION_STATE with CHAN_ID 1, REG_STATE 'ACTIVE'")
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
LUNAR_BUNDLE_COUNT_IN_CUSTODY = tlm(f"{target_1} BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_IN_CUSTODY")
print("Lunar User Node Bundles In Custody:", LUNAR_BUNDLE_COUNT_IN_CUSTODY)
LUNAR_BUNDLE_COUNT_CUSTODY_TRANSFERRED = tlm(f"{target_1} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_CUSTODY_TRANSFERRED")
print("Lunar User Node Bundles for which Custody has been Transferred to the next Custodian Node:", LUNAR_BUNDLE_COUNT_CUSTODY_TRANSFERRED)

## Verify successful data delivery
assert LUNAR_BUNDLE_COUNT_STORED == 0
assert LUNAR_BUNDLE_COUNT_ABANDONED == 0
assert LUNAR_BUNDLE_COUNT_DELIVERED == CFDP_PDU_count_3
assert LUNAR_ADU_COUNT_DELIVERED == CFDP_PDU_count_3
#assert LUNAR_CFDP_PDU_COUNT_RECEIVED == CFDP_PDU_count_3          DR DTNN-1492
assert LUNAR_BUNDLE_COUNT_IN_CUSTODY == 0
assert LUNAR_BUNDLE_COUNT_CUSTODY_TRANSFERRED == 0

##-------------------------------------------------------------------------------------------------------------------
## 5.2 Channel Registration State Test #2 - Passive/Abandon
##-------------------------------------------------------------------------------------------------------------------

## Change Lunar User Node Channel 1 registration state to passive/abandon
cmd(f"{target_1} BPNODE_CMD_SET_REGISTRATION_STATE with CHAN_ID 1, REG_STATE 'PASSIVE_ABANDON'")
wait(10)

## Print Channel 1 registration status
LUNAR_CHANNEL_1_REG_STATE = tlm(f"{target_1} BPNODE_CHAN_CON_STAT_HK CHAN_STAT_REG_STATE_1")
print("Lunar User Node Channel 1 Registration State:", LUNAR_CHANNEL_1_REG_STATE)

## Verify Channel 1 registration state change
assert LUNAR_CHANNEL_1_REG_STATE == "PASSIVE_ABANDON"

## Start another Earth User to Lunar User data transfer (Earth User CF transmitting a file)
CFDP_PDU_count_4 = 376
cmd(f"{target_5} CF_CMD_TX_FILE with CFDP_CLASS 'CLASS_1', KEEP 1, CHAN_NUM 0, DEST_ID 1, SRC_FILENAME '/cf/Jojo2.jpg', DST_FILENAME '/cf/Jojo2_in_space.jpg'")
wait(20)

## Wait for custody of all bundles to have been transferred to the Relay Node
wait_check(f"{target_4} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_RECEIVED >= {CFDP_PDU_count_3 + CFDP_PDU_count_4}", 300)
wait_check(f"{target_3} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_RECEIVED >= {CFDP_PDU_count_3 + CFDP_PDU_count_4}", 300)
wait_check(f"{target_2} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_RECEIVED >= {CFDP_PDU_count_3 + CFDP_PDU_count_4}", 300)
wait_check(f"{target_1} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_RECEIVED >= {CFDP_PDU_count_3 + CFDP_PDU_count_4}", 300)
wait(60)

## Print counter values
LUNAR_CHANNEL_1_REG_STATE = tlm(f"{target_1} BPNODE_CHAN_CON_STAT_HK CHAN_STAT_REG_STATE_1")
print("Lunar User Node Channel 1 Registration State:", LUNAR_CHANNEL_1_REG_STATE)
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
LUNAR_BUNDLE_COUNT_CUSTODY_REQUEST = tlm(f"{target_1} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_CUSTODY_REQUEST")
print("Lunar User Node Bundles that are Requesting Custody:", LUNAR_BUNDLE_COUNT_CUSTODY_REQUEST)
LUNAR_BUNDLE_COUNT_REJECTED_CUSTODY = tlm(f"{target_1} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_REJECTED_CUSTODY")
print("Lunar User Node Bundles for which custody was rejected:", LUNAR_BUNDLE_COUNT_REJECTED_CUSTODY)
LUNAR_BUNDLE_COUNT_GENERATED_CCS = tlm(f"{target_1} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_GENERATED_CCS")
print("Lunar User Node Generated CCS:", LUNAR_BUNDLE_COUNT_GENERATED_CCS)
LUNAR_BUNDLE_COUNT_GENERATED_CUSTODY_SIGNAL = tlm(f"{target_1} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_GENERATED_CUSTODY_SIGNAL")
print("Lunar User Node Bundles for which Custody Signal has been Generated:", LUNAR_BUNDLE_COUNT_GENERATED_CUSTODY_SIGNAL)
LUNAR_BUNDLE_COUNT_IN_CUSTODY = tlm(f"{target_1} BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_IN_CUSTODY")
print("Lunar User Node Bundles In Custody:", LUNAR_BUNDLE_COUNT_IN_CUSTODY)

RELAY_BUNDLE_COUNT_STORED = tlm(f"{target_2} BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED")
print("Relay Node Bundles Stored:", RELAY_BUNDLE_COUNT_STORED)
RELAY_BUNDLE_COUNT_IN_CUSTODY = tlm(f"{target_2} BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_IN_CUSTODY")
print("Relay Node Bundles In Custody:", RELAY_BUNDLE_COUNT_IN_CUSTODY)
RELAY_BUNDLE_COUNT_CCS_RECEIVED = tlm(f"{target_2} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_CCS_RECEIVED")
print("Relay Node CCS Received:", RELAY_BUNDLE_COUNT_CCS_RECEIVED)
RELAY_BUNDLE_COUNT_RECEIVED_CUSTODY_SIGNAL = tlm(f"{target_2} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_RECEIVED_CUSTODY_SIGNAL")
print("Relay Node Bundles for which Custody Signal has been Received:", RELAY_BUNDLE_COUNT_RECEIVED_CUSTODY_SIGNAL)
RELAY_BUNDLE_COUNT_CUSTODY_TRANSFERRED = tlm(f"{target_2} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_CUSTODY_TRANSFERRED")
print("Relay Node Bundles for which Custody has been Transferred to the next Custodian Node:", RELAY_BUNDLE_COUNT_CUSTODY_TRANSFERRED)
RELAY_BUNDLE_COUNT_CUSTODY_REJECTED = tlm(f"{target_2} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_CUSTODY_REJECTED")
print("Relay Node Bundles for which custody rejected by the Lunar Node:", RELAY_BUNDLE_COUNT_CUSTODY_REJECTED)

## Verify that bundles are abandoned
assert LUNAR_BUNDLE_COUNT_STORED == 0
assert LUNAR_BUNDLE_COUNT_ABANDONED >= CFDP_PDU_count_4
assert LUNAR_BUNDLE_COUNT_DELIVERED == CFDP_PDU_count_3
assert LUNAR_ADU_COUNT_DELIVERED == CFDP_PDU_count_3
#assert LUNAR_CFDP_PDU_COUNT_RECEIVED == CFDP_PDU_count_3          DR DTNN-1492
assert LUNAR_BUNDLE_COUNT_CUSTODY_REQUEST >= CFDP_PDU_count_3 + CFDP_PDU_count_4
assert LUNAR_BUNDLE_COUNT_REJECTED_CUSTODY >= CFDP_PDU_count_4
assert LUNAR_BUNDLE_COUNT_GENERATED_CCS > 0
assert LUNAR_BUNDLE_COUNT_GENERATED_CUSTODY_SIGNAL >= CFDP_PDU_count_3 + CFDP_PDU_count_4
assert LUNAR_BUNDLE_COUNT_IN_CUSTODY == 0
assert RELAY_BUNDLE_COUNT_STORED == CFDP_PDU_count_4
assert RELAY_BUNDLE_COUNT_IN_CUSTODY == CFDP_PDU_count_4
assert RELAY_BUNDLE_COUNT_CUSTODY_TRANSFERRED == CFDP_PDU_count_3
assert RELAY_BUNDLE_COUNT_CUSTODY_REJECTED >= CFDP_PDU_count_4

## Verify requirements
rqmnt_status["DTN.5.00410"] = "P"
rqmnt_status["DTN.5.00440"] = "P"
rqmnt_status["DTN.5.00495"] = "P"
#rqmnt_status["DTN.5.00500"] = "P"     DR DTNN-1539
rqmnt_status["DTN.5.00782"] = "P"
rqmnt_status["DTN.5.00784"] = "P"
rqmnt_status["DTN.5.00788"] = "P"

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
## 6 TEST CLEANUP
##-------------------------------------------------------------------------------------------------------------------

if ct_with_packet_loss == "yes":
    ## Remove condition for bundle retransmission due to expiration of the retransmission timer
    prompt("On the Lunar User and Rely Nodes, remove the two-way 1% packet loss between the Lunar User Node and the Relay Node")

## Stop all contacts on all nodes
cmd(f"{target_1} BPNODE_CMD_CONTACT_STOP with CONTACT_ID 0")
wait(1)
cmd(f"{target_2} BPNODE_CMD_CONTACT_STOP with CONTACT_ID 0")
wait(1)
cmd(f"{target_2} BPNODE_CMD_CONTACT_STOP with CONTACT_ID 1")
wait(1)
cmd(f"{target_3} BPNODE_CMD_CONTACT_STOP with CONTACT_ID 0")
wait(1)
cmd(f"{target_3} BPNODE_CMD_CONTACT_STOP with CONTACT_ID 1")
wait(1)
cmd(f"{target_4} BPNODE_CMD_CONTACT_STOP with CONTACT_ID 0")
wait(1)
cmd(f"{target_4} BPNODE_CMD_CONTACT_STOP with CONTACT_ID 1")
wait(1)
cmd(f"{target_5} BPNODE_CMD_CONTACT_STOP with CONTACT_ID 0")
wait(1)

## Tear down Contact 0 on all nodes
cmd(f"{target_1} BPNODE_CMD_CONTACT_TEARDOWN with CONTACT_ID 0")
wait(1)
cmd(f"{target_1} BPNODE_CMD_CONTACT_TEARDOWN with CONTACT_ID 1")
wait(1)
cmd(f"{target_2} BPNODE_CMD_CONTACT_TEARDOWN with CONTACT_ID 0")
wait(1)
cmd(f"{target_2} BPNODE_CMD_CONTACT_TEARDOWN with CONTACT_ID 1")
wait(1)
cmd(f"{target_3} BPNODE_CMD_CONTACT_TEARDOWN with CONTACT_ID 0")
wait(1)
cmd(f"{target_3} BPNODE_CMD_CONTACT_TEARDOWN with CONTACT_ID 1")
wait(1)
cmd(f"{target_4} BPNODE_CMD_CONTACT_TEARDOWN with CONTACT_ID 0")
wait(1)
cmd(f"{target_4} BPNODE_CMD_CONTACT_TEARDOWN with CONTACT_ID 1")
wait(1)
cmd(f"{target_5} BPNODE_CMD_CONTACT_TEARDOWN with CONTACT_ID 0")
wait(1)
cmd(f"{target_5} BPNODE_CMD_CONTACT_TEARDOWN with CONTACT_ID 1")
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
