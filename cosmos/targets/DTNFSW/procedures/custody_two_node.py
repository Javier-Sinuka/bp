'''
Node 1
- Setup
    - node 100.42 (default)
    - channel 0 table - include CTEB
    - ADU Proxy table - receive CF PDUs (0x83E) on Channel 0 (dest 200.64)
    - Contact table - send bundles on #0 (port 4551) and receive CCS on #2 (port 4502)
    - Restart Channel 0 after table updates
- Start contact
- Send CF command to transmit a file
    - Receive ADUs, generate bundles and forward to Node-2

Node 2
- Setup
    - MIB PN table - node: 200
    - Contact table - receive bundles on #0 (port 4551) and send CCS on #2 (port 4502)
    - CF Config table - receive PDUs (0x83E, default 0x183F)
    - Channel 0 table - local service number to 64 (destination)
    - Restart Channel 0 after table updates
- Start Contact
    - Wait for bundles from Node-1
- Receive bundles
    - Deliver ADUs, assembled file
'''

## Destination Node-2 setup
answer = ask("Set up Destination Node-2? [y/n]")
if answer.lower() == 'y': 

    load_utility('DTNFSW-1/procedures/load_target_table.py')

    ## Modify MIB PN table to set node EID as destination EID
    load_target_table('/cf/mib_pn_200_64.tbl', 'DTNFSW-2')

    ## Modify Contact table 
    ##    Contact 0: receive bundles on port 4551
    ##    Contact 2: send CCS on port 4502
    #load_target_table('/cf/cont_n2_rx_only_and_ccs.tbl', 'DTNFSW-2')
    load_target_table('/cf/cont_n2_rx_only_and_ccs_cont2.tbl', 'DTNFSW-2')
    
    ## Modify CF Config table to receive 0x83E PDUs (default 0x183F)
    cmd("DTNFSW-2 CF_CMD_DISABLE_ENGINE")
    load_target_table('/cf/cf_rx_083E.tbl', 'DTNFSW-2')
    cmd("DTNFSW-2 CF_CMD_ENABLE_ENGINE")
    
    # Disable CF engine for now
    #cmd("DTNFSW-2 CF_CMD_DISABLE_ENGINE")

    ## Modify Channel 0 table to set local service number to 64 (destination) egress 40000
    load_target_table('/cf/chan_serv_64_40000.tbl', 'DTNFSW-2')
    
    ## Modify ADUP table to remove 0x083E
    load_target_table('/cf/adup_n2_nocf.tbl', 'DTNFSW-2')

    ## Restart Channel 0 after table updates
    cmd("DTNFSW-2 BPNODE_CMD_STOP_APPLICATION with CHAN_ID 0")
    wait(1)
    cmd("DTNFSW-2 BPNODE_CMD_REMOVE_APPLICATION with CHAN_ID 0")
    wait(1)
    cmd("DTNFSW-2 BPNODE_CMD_ADD_APPLICATION with CHAN_ID 0")
    wait(1)
    cmd("DTNFSW-2 BPNODE_CMD_START_APPLICATION with CHAN_ID 0")
    
    ## Setup and start Contact 0 for receiving bundles
    cmd("DTNFSW-2 BPNODE_CMD_CONTACT_SETUP with CONTACT_ID 0")
    wait (1)
    cmd("DTNFSW-2 BPNODE_CMD_CONTACT_START with CONTACT_ID 0")
    wait(5)
    
    
    ## Setup and start Contact 2 for sending CCS
    cmd("DTNFSW-2 BPNODE_CMD_CONTACT_SETUP with CONTACT_ID 2")
    wait (1)
    cmd("DTNFSW-2 BPNODE_CMD_CONTACT_START with CONTACT_ID 2")
    wait(5)
    
    cmd("DTNFSW-2 BPNODE_CMD_RESET_ALL_COUNTERS")

    wait()
##-----------------------------------------------------------------------------

## Source Node-1 setup
answer = ask("Set up Source Node-1? [y/n]")
if answer.lower() == 'y': 

    ## Node-1 setup
    load_utility('DTNFSW-1/procedures/load_new_table.py')

    # Modify channel 0 table to include CTEB - now default
    #load_new_table('/cf/chan0_w_cteb.tbl')

    ## Modify Contact table
    ##    Contact 0: Node-2 destination address for sending bundles (on port 4551, default)
    ##    Contact 2: CCS receipt (on 4502, default)
    #load_new_table('/cf/cont_node2.tbl')
    load_new_table('/cf/cont_two_cont.tbl')

    #cmd("DTNFSW-1 CF_CMD_SET_PARAM with VALUE 1000, KEY 'OUTGOING_FILE_CHUNK_SIZE'")
    
    ## Restart Channel 0 after table updates
    cmd("DTNFSW-1 BPNODE_CMD_STOP_APPLICATION with CHAN_ID 0")
    wait(1)
    cmd("DTNFSW-1 BPNODE_CMD_REMOVE_APPLICATION with CHAN_ID 0")
    wait(1)
    cmd("DTNFSW-1 BPNODE_CMD_ADD_APPLICATION with CHAN_ID 0")
    wait(1)
    cmd("DTNFSW-1 BPNODE_CMD_START_APPLICATION with CHAN_ID 0")

    ## Setup and start contact 0 for sending bundles
    cmd("DTNFSW-1 BPNODE_CMD_CONTACT_SETUP with CONTACT_ID 0")
    wait (1)
    cmd("DTNFSW-1 BPNODE_CMD_CONTACT_START with CONTACT_ID 0")
    wait(5)
    
    ## Setup and start contact 2 for receiving CCS
    cmd("DTNFSW-1 BPNODE_CMD_CONTACT_SETUP with CONTACT_ID 2")
    wait (1)
    cmd("DTNFSW-1 BPNODE_CMD_CONTACT_START with CONTACT_ID 2")
    wait(5)
    
    cmd("DTNFSW-1 BPNODE_CMD_RESET_ALL_COUNTERS")

    wait()
##-----------------------------------------------------------------------------

## Send CF command to transmit a file
#cmd("DTNFSW-1 CF_CMD_TX_FILE with CFDP_CLASS 'CLASS_1', KEEP 1, CHAN_NUM 0, DEST_ID 1, SRC_FILENAME '/cf/file10000_rand.dat', DST_FILENAME '/cf/file10000_rand.temp'")
cmd("DTNFSW-1 CF_CMD_TX_FILE with CFDP_CLASS 'CLASS_1', KEEP 1, CHAN_NUM 0, DEST_ID 1, SRC_FILENAME '/cf/file1M.dat', DST_FILENAME '/cf/file1M.temp'")
#cmd("DTNFSW-1 CF_CMD_TX_FILE with CFDP_CLASS 'CLASS_1', KEEP 1, CHAN_NUM 0, DEST_ID 1, SRC_FILENAME '/cf/file_16.dat', DST_FILENAME '/cf/file16.temp'")
#cmd("DTNFSW-1 CF_CMD_TX_FILE with CFDP_CLASS 'CLASS_1', KEEP 1, CHAN_NUM 0, DEST_ID 1, SRC_FILENAME '/cf/file_1024.dat', DST_FILENAME '/cf/file1024.temp'")
#cmd("DTNFSW-1 CF_CMD_TX_FILE with CFDP_CLASS 'CLASS_1', KEEP 1, CHAN_NUM 0, DEST_ID 1, SRC_FILENAME '/cf/ci_lab.so', DST_FILENAME '/cf/test.temp'")

wait()


## Stop and teardown contacts
cmd("DTNFSW-1 BPNODE_CMD_CONTACT_STOP with CONTACT_ID 0")
cmd("DTNFSW-1 BPNODE_CMD_CONTACT_TEARDOWN with CONTACT_ID 0")
cmd("DTNFSW-2 BPNODE_CMD_CONTACT_STOP with CONTACT_ID 0")
cmd("DTNFSW-2 BPNODE_CMD_CONTACT_TEARDOWN with CONTACT_ID 0")


wait()
