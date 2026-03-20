##*******************************************************************************************************************
##
## Validation Test Case - Long Duration Test with Custody Transfer and Packet Loss
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
load_target_table('/cf/con_lunar_long.tbl', target_1) 

## Set up Contact 0 on the Lunar User Node
cmd(f"{target_1} BPNODE_CMD_CONTACT_SETUP with CONTACT_ID 0")
wait(1)

##-------------------------------------------------------------------------------------------------------------------
## 2.2 Relay Node Configuration
##-------------------------------------------------------------------------------------------------------------------

## Load MIB PN table to set node number to 102
load_target_table('/cf/pn_relay.tbl', target_2)

## Load Contact table
load_target_table('/cf/con_relay_long.tbl', target_2) 

## Set up Contacts 0 and 1, and 2
cmd(f"{target_2} BPNODE_CMD_CONTACT_SETUP with CONTACT_ID 0")
wait(1)
cmd(f"{target_2} BPNODE_CMD_CONTACT_SETUP with CONTACT_ID 1")
wait(1)
cmd(f"{target_2} BPNODE_CMD_CONTACT_SETUP with CONTACT_ID 2")
wait(1)

##-------------------------------------------------------------------------------------------------------------------
## 2.3 Ground Node Configuration
##-------------------------------------------------------------------------------------------------------------------

## Load MIB PN table to set node number to 103
load_target_table('/cf/pn_ground.tbl', target_3)

## Load Contact table
load_target_table('/cf/con_ground_long.tbl', target_3) 

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
load_target_table('/cf/con_nsn_long.tbl', target_4) 

## Set up Contacts 0, 1, and 2
cmd(f"{target_4} BPNODE_CMD_CONTACT_SETUP with CONTACT_ID 0")
wait(1)
cmd(f"{target_4} BPNODE_CMD_CONTACT_SETUP with CONTACT_ID 1")
wait(1)
cmd(f"{target_4} BPNODE_CMD_CONTACT_SETUP with CONTACT_ID 2")
wait(1)

##-------------------------------------------------------------------------------------------------------------------
## 2.5 Earth User Node Configuration
##-------------------------------------------------------------------------------------------------------------------

## Load MIB PN table modified to set node number to 105
load_target_table('/cf/pn_earth.tbl', target_5)

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

## Load Contact table
load_target_table('/cf/con_earth_long.tbl', target_5) 

## Set up Contact 0
cmd(f"{target_5} BPNODE_CMD_CONTACT_SETUP with CONTACT_ID 0")
wait(1)

##-------------------------------------------------------------------------------------------------------------------
## 3 TEST EXECUTION
##-------------------------------------------------------------------------------------------------------------------

##-------------------------------------------------------------------------------------------------------------------
## 3.1 Set Up Test Conditions
##-------------------------------------------------------------------------------------------------------------------

## Set up link conditions between Lunar User and Relay Nodes
prompt("On the Lunar User Node, set up 10% packet loss and a 1-second delay to the Relay Node")
prompt("On the Relay Node, set up a 1-second delay to the Lunar User Node")

## Select how many contact loops to execute
number_of_contact_loops = ask("Choose number of contact loops: ")

Start_Time = datetime.now()
print(f"Test Start Time = {Start_Time}")

##-------------------------------------------------------------------------------------------------------------------
## 3.2 Execute Test Loop
##-------------------------------------------------------------------------------------------------------------------

loop = 0
CFDP_PDU_count = 0

while loop < number_of_contact_loops:

    loop = loop + 1

    print("Starting Contact ", loop)
    
    ## Change Earth User Node Channel 0 registration state to passive/defer
    cmd(f"{target_5} BPNODE_CMD_SET_REGISTRATION_STATE with CHAN_ID 0, REG_STATE 'PASSIVE_DEFER'")
    wait(10)

    CFDP_PDU_count = 9225

    ## Start the first data transfer
    cmd(f"{target_1} CF_CMD_TX_FILE with CFDP_CLASS 'CLASS_1', KEEP 1, CHAN_NUM 0, DEST_ID 2, SRC_FILENAME '/cf/Stars1.jpg', DST_FILENAME '/cf/Stars1_on_earth.jpg'")
    wait(10)

    ## Wait for all bundles to have been created
    wait_check(f"{target_1} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_GENERATED_ACCEPTED == {CFDP_PDU_count}", 300)
    wait(10)

    ## Print counter values
    LUNAR_CFDP_PDU_COUNT_SENT = tlm(f"{target_1} CF_HK CHANNEL_HK_0_COUNTERS_SENT_PDU")
    print("Lunar User Node CFDP PDUs Sent:", LUNAR_CFDP_PDU_COUNT_SENT)
    LUNAR_ADU_COUNT_RECEIVED = tlm(f"{target_1} BPNODE_NODE_MIB_COUNTERS_HK ADU_COUNT_RECEIVED")
    print("Lunar User Node ADUs Received:", LUNAR_ADU_COUNT_RECEIVED)
    LUNAR_BUNDLE_COUNT_STORED = tlm(f"{target_1} BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED")
    print("Lunar User Node Bundles Stored:", LUNAR_BUNDLE_COUNT_STORED)
    LUNAR_BUNDLE_COUNT_IN_CUSTODY = tlm(f"{target_1} BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_IN_CUSTODY")
    print("Lunar User Node Bundles In Custody:", LUNAR_BUNDLE_COUNT_IN_CUSTODY)

    ## Start all contacts between the Lunar User and Earth User Nodes
    cmd(f"{target_5} BPNODE_CMD_CONTACT_START with CONTACT_ID 0")
    wait(1)
    cmd(f"{target_4} BPNODE_CMD_CONTACT_START with CONTACT_ID 1")
    wait(1)
    cmd(f"{target_4} BPNODE_CMD_CONTACT_START with CONTACT_ID 0")
    wait(1)
    cmd(f"{target_3} BPNODE_CMD_CONTACT_START with CONTACT_ID 1")
    wait(1)
    cmd(f"{target_3} BPNODE_CMD_CONTACT_START with CONTACT_ID 0")
    wait(1)
    cmd(f"{target_2} BPNODE_CMD_CONTACT_START with CONTACT_ID 1")
    wait(1)
    cmd(f"{target_2} BPNODE_CMD_CONTACT_START with CONTACT_ID 0")
    wait(10)
    cmd(f"{target_1} BPNODE_CMD_CONTACT_START with CONTACT_ID 0")
    wait(10)

    ## Wait for custody of all bundles to have been transferred to the Earth User Node
    wait_check(f"{target_2} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_RECEIVED >= {CFDP_PDU_count}", 600)
    wait_check(f"{target_3} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_RECEIVED >= {CFDP_PDU_count}", 600)
    wait_check(f"{target_4} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_RECEIVED >= {CFDP_PDU_count}", 600)
    wait_check(f"{target_5} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_RECEIVED >= {CFDP_PDU_count}", 600)
    wait(120)

    ## Change Earth User Node Channel 0 registration state to active
    cmd(f"{target_5} BPNODE_CMD_SET_REGISTRATION_STATE with CHAN_ID 0, REG_STATE 'ACTIVE'")
    wait_check(f"{target_5} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_DELIVERED >= {CFDP_PDU_count}", 600)
    wait(10)

    ## Print counter values
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

    ## Verify successful data transfer
    assert LUNAR_CFDP_PDU_COUNT_SENT == CFDP_PDU_count
    assert LUNAR_ADU_COUNT_RECEIVED == CFDP_PDU_count
    assert LUNAR_BUNDLE_COUNT_STORED == 0
    assert LUNAR_BUNDLE_COUNT_IN_CUSTODY == 0
    assert RELAY_BUNDLE_COUNT_STORED == 0
    assert RELAY_BUNDLE_COUNT_IN_CUSTODY == 0
    assert GROUND_BUNDLE_COUNT_STORED == 0
    assert GROUND_BUNDLE_COUNT_IN_CUSTODY == 0
    assert NSN_BUNDLE_COUNT_STORED == 0
    assert NSN_BUNDLE_COUNT_IN_CUSTODY == 0
    assert EARTH_BUNDLE_COUNT_STORED == 0
    assert EARTH_BUNDLE_COUNT_IN_CUSTODY == 0
    assert EARTH_BUNDLE_COUNT_RECEIVED >= CFDP_PDU_count
    assert EARTH_ADU_COUNT_DELIVERED >= CFDP_PDU_count
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

    CFDP_PDU_count = 3203

    ## Start a second data transfer
    cmd(f"{target_1} CF_CMD_TX_FILE with CFDP_CLASS 'CLASS_1', KEEP 1, CHAN_NUM 0, DEST_ID 2, SRC_FILENAME '/cf/Jojo4.jpg', DST_FILENAME '/cf/Jojo4_on_earth.jpg'")
    wait(10)

    ## Wait for custody of all bundles to have been transferred to the Earth User Node
    wait_check(f"{target_2} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_RECEIVED >= {CFDP_PDU_count}", 600)
    wait_check(f"{target_3} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_RECEIVED >= {CFDP_PDU_count}", 600)
    wait_check(f"{target_4} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_RECEIVED >= {CFDP_PDU_count}", 600)
    wait_check(f"{target_5} BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_RECEIVED >= {CFDP_PDU_count}", 600)
    wait(120)

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

    ## Verify successful data transfer
    assert LUNAR_CFDP_PDU_COUNT_SENT == CFDP_PDU_count
    assert LUNAR_ADU_COUNT_RECEIVED == CFDP_PDU_count
    assert LUNAR_BUNDLE_COUNT_STORED == 0
    assert LUNAR_BUNDLE_COUNT_IN_CUSTODY == 0
    assert RELAY_BUNDLE_COUNT_STORED == 0
    assert RELAY_BUNDLE_COUNT_IN_CUSTODY == 0
    assert GROUND_BUNDLE_COUNT_STORED == 0
    assert GROUND_BUNDLE_COUNT_IN_CUSTODY == 0
    assert NSN_BUNDLE_COUNT_STORED == 0
    assert NSN_BUNDLE_COUNT_IN_CUSTODY == 0
    assert EARTH_BUNDLE_COUNT_STORED == 0
    assert EARTH_BUNDLE_COUNT_IN_CUSTODY == 0
    assert EARTH_BUNDLE_COUNT_RECEIVED >= CFDP_PDU_count
    assert EARTH_ADU_COUNT_DELIVERED >= CFDP_PDU_count
    wait(1)

    print("Stopping Contact ", loop)
    ## Stop Contacts on all Nodes
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
    wait(10)

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

End_Time = datetime.now()
print(f"Test End Time = {End_Time}")

##-------------------------------------------------------------------------------------------------------------------
## 4 TEST CLEANUP
##-------------------------------------------------------------------------------------------------------------------

## Print memory and storage report values
LUNAR_BYTES_MEM_IN_USE = tlm(f"{target_1} BPNODE_STORAGE_HK BYTES_MEM_IN_USE")
print("Lunar User Node Memory In Use (bytes):", LUNAR_BYTES_MEM_IN_USE)
LUNAR_KB_STORAGE_IN_USE = tlm(f"{target_1} BPNODE_STORAGE_HK KB_STORAGE_IN_USE")
print("Lunar User Node Storage In Use (kB):", LUNAR_KB_STORAGE_IN_USE)

RELAY_BYTES_MEM_IN_USE = tlm(f"{target_2} BPNODE_STORAGE_HK BYTES_MEM_IN_USE")
print("Relay Node Memory In Use (bytes):", RELAY_BYTES_MEM_IN_USE)
RELAY_KB_STORAGE_IN_USE = tlm(f"{target_2} BPNODE_STORAGE_HK KB_STORAGE_IN_USE")
print("Relay Node Storage In Use (kB):", RELAY_KB_STORAGE_IN_USE)

GROUND_BYTES_MEM_IN_USE = tlm(f"{target_3} BPNODE_STORAGE_HK BYTES_MEM_IN_USE")
print("Ground Node Memory In Use (bytes):", GROUND_BYTES_MEM_IN_USE)
GROUND_KB_STORAGE_IN_USE = tlm(f"{target_3} BPNODE_STORAGE_HK KB_STORAGE_IN_USE")
print("Ground Node Storage In Use (kB):", GROUND_KB_STORAGE_IN_USE)

NSN_BYTES_MEM_IN_USE = tlm(f"{target_4} BPNODE_STORAGE_HK BYTES_MEM_IN_USE")
print("NSN Node Memory In Use (bytes):", NSN_BYTES_MEM_IN_USE)
NSN_KB_STORAGE_IN_USE = tlm(f"{target_4} BPNODE_STORAGE_HK KB_STORAGE_IN_USE")
print("NSN Node Storage In Use (kB):", NSN_KB_STORAGE_IN_USE)

EARTH_BYTES_MEM_IN_USE = tlm(f"{target_5} BPNODE_STORAGE_HK BYTES_MEM_IN_USE")
print("Earth User Node Memory In Use (bytes):", EARTH_BYTES_MEM_IN_USE)
EARTH_KB_STORAGE_IN_USE = tlm(f"{target_5} BPNODE_STORAGE_HK KB_STORAGE_IN_USE")
print("Earth User Node Storage In Use (kB):", EARTH_KB_STORAGE_IN_USE)

## Verify memory and storage status
assert LUNAR_BYTES_MEM_IN_USE == 0
assert LUNAR_KB_STORAGE_IN_USE < 50
assert RELAY_BYTES_MEM_IN_USE == 0
assert RELAY_KB_STORAGE_IN_USE < 50
assert GROUND_BYTES_MEM_IN_USE == 0
assert GROUND_KB_STORAGE_IN_USE < 50
assert NSN_BYTES_MEM_IN_USE == 0
assert NSN_KB_STORAGE_IN_USE < 50
assert EARTH_BYTES_MEM_IN_USE == 0
assert EARTH_KB_STORAGE_IN_USE < 50
wait(1)

## Tear down all contacts on all nodes
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

## Stop running scripts
running_script_stop(id_1)
running_script_stop(id_2)
running_script_stop(id_3)
running_script_stop(id_4)
running_script_stop(id_5)
