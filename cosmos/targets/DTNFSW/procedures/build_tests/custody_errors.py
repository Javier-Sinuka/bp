def custody_errors(self):
    
    print("###################################################################")
    print("### Custody test - Errors")
    print("###################################################################")

    setup_cont_0    = "BPNODE_CMD_CONTACT_SETUP with CONTACT_ID 0"
    start_cont_0    = "BPNODE_CMD_CONTACT_START with CONTACT_ID 0"
    stop_cont_0     = "BPNODE_CMD_CONTACT_STOP with CONTACT_ID 0"
    teardown_cont_0 = "BPNODE_CMD_CONTACT_TEARDOWN with CONTACT_ID 0"

    def restart_contact_0(contact_table):
        
        # Tear down contact if not already torn down
        cont_state = tlm(f"{target} BPNODE_CHAN_CON_STAT_HK CON_STAT_RUN_STATE_0")
        if cont_state == 'SETUP' or cont_state == 'STOPPED':
            cmd(f"{target} {teardown_cont_0}")
        elif cont_state == 'STARTED':
            cmd(f"{target} {stop_cont_0}")
            cmd(f"{target} {teardown_cont_0}")        
        wait_check(f"{target} BPNODE_CHAN_CON_STAT_HK CON_STAT_RUN_STATE_0 == 'TORNDOWN'", 6)
        
        # Load new table
        load_new_table(contact_table)
        
        # Restart contact
        cmd(f"{target} {setup_cont_0}")
        cmd(f"{target} {start_cont_0}")
        
        wait(2)
        
    ############################################################################
    
    import copy
    from dtntools.dtngen.utils import DtnTimeNowMs
    from dtntools.dtncla.udp import UdpTxSocket, UdpRxSocket
    from dtntools.dtngen.bundle import Bundle
    from dtntools.dtngen.blocks import (
        AdminRecordBlock,
        CustodyTransferBlock,
        PayloadBlock,
        PrimaryBlock,
        PrimaryBlockSettings,
    )
    from dtntools.dtngen.bundle import Bundle
    from dtntools.dtngen.types import (
        EID,
        BlockType,
        BundlePCFlags,
        BlockPCFlags,
        CRCFlag,
        DispositionCode,
        AdminRecordType,
        CCSData,
        BundleSequenceCollection,
        CRCType,
        CreationTimestamp,
        CTEBData
    )
    load_utility("DTNFSW-1/procedures/build_tests/test_globals.py")
    load_utility("DTNFSW-1/procedures/build_tests/test_utils.py")
    load_utility("DTNFSW-1/procedures/dtngen_utils.py")
    load_utility('DTNFSW-1/procedures/load_new_table.py')

    global rqmnt_status
    
    rqmnt_status = {    
        "DTN.6.03151":"U",
        "DTN.6.03172":"U",
        "DTN.6.08280":"U",
        "DTN.6.08282":"U",
        "DTN.6.08336":"U",
        "DTN.6.08493":"I", #bundleCountGeneratedRejected
        "DTN.6.08672":"U",
        "DTN.6.08820":"U",
        "DTN.6.19090":"U",
        "DTN.6.19160":"U",
        "DTN.6.19170":"U",
        "DTN.6.19360":"U",
        "DTN.6.19390":"U",
    }
    
    ## Configure/connect Data Receiver
    dest_node    = 200
    dest_service = 64

    ## Address/port configuration
    dest_ip   = DTN_NODE_IP_ADDR
    dest_port = 4501 # Contact 0
    #dest_port = 4502 # Contact 2

    local_ip = "0.0.0.0"
    local_port = 4551

    data_sender = UdpTxSocket(dest_ip, dest_port) 
    data_sender.connect()

    data_receiver = UdpRxSocket(local_ip, local_port)
    data_receiver.connect()

    SRC_NODE_NUM = 300
    SRC_SERVICE_NUM = 1
    LOCAL_NODE_NUM = 100

    LOCAL_EID = EID({"uri": 2, "ssp": {"node_num": LOCAL_NODE_NUM, "service_num": 0}})
    TEST_EID = EID ({"uri": 2, "ssp": {"node_num": SRC_NODE_NUM, "service_num": SRC_SERVICE_NUM}})

    cteb_data = CTEBData({"bundle_seq_id": 2, "bundle_seq_num": 10, "block_src_admin_eid": TEST_EID})
    new_cteb_data = CTEBData ({"bundle_seq_id": 1, "bundle_seq_num": 0, "block_src_admin_eid": LOCAL_EID})
    
    primary_block = PrimaryBlock(
        version=7,
        control_flags=BundlePCFlags.MUST_NOT_FRAGMENT,
        crc_type=CRCType.CRC16_X25,
        dest_eid=EID({"uri": 2, "ssp": {"node_num": dest_node, "service_num": dest_service}}),
        src_eid=EID({"uri": 2, "ssp": {"node_num": 101, "service_num": 1}}),
        rpt_eid=EID({"uri": 2, "ssp": {"node_num": 100, "service_num": 1}}),
        creation_timestamp=CreationTimestamp({"time": DtnTimeNowMs(), "sequence": 0}),
        lifetime=3600000,
        crc=CRCFlag.CALCULATE,
    )

    custody_transfer_block = CustodyTransferBlock(
        blk_type=BlockType.AUTO,
        blk_num=4,
        control_flags=0,
        crc_type=CRCType.CRC16_X25,
        cteb_data=cteb_data,
        crc=CRCFlag.CALCULATE,
    )

    payload_block = PayloadBlock(
        blk_type=BlockType.AUTO,
        blk_num=1,
        control_flags=0,
        crc_type=CRCType.CRC16_X25,
        payload=b'\xAA'*8,
        crc=CRCFlag.CALCULATE,
    )

    mib_counts_pkt  = "BPNODE_NODE_MIB_COUNTERS_HK"
    mib_reports_pkt = "BPNODE_NODE_MIB_REPORTS_HK"
    mib_config_hk   = "BPNODE_NODE_MIB_CONFIG_HK"

    cmd("DTNFSW-1 CFE_EVS_CMD_ENABLE_APP_EVENT_TYPE with APP_NAME 'BPNODE', BIT_MASK 1")

    cmd(f"{target} BPNODE_CMD_RESET_ALL_COUNTERS")
    #cmd(f"{target} CFE_SB_CMD_SEND_SB_STATS")
    
    print("===========================================================")
    print("1. Contact table Timeout/Trigger Validation")
    print("===========================================================")
    status = "P"
    
    ## Retransmit timeout < BPLIB_MIN_RETRANSMIT_ALLOWED 1000
    if TestUtils.validate_invalid_table('/cf/cont_timeout_min.tbl') == "F": status = "F" 

    ## Retransmit timeout > BPLIB_MAX_RETRANSMIT_ALLOWED 600000
    if TestUtils.validate_invalid_table('/cf/cont_timeout_max.tbl') == "F": status = "F" 

    ## Time trigger < BPLIB_MIN_CS_TIME_TRIGGER_ALLOWED 1000
    if TestUtils.validate_invalid_table('/cf/cont_time_trg_min.tbl') == "F": status = "F" 
    
    ## Time trigger > Retransmit timeout 
    if TestUtils.validate_invalid_table('/cf/cont_time_trg_max.tbl') == "F": status = "F" 

    ## Size trigger < 63
    if TestUtils.validate_invalid_table('/cf/cont_size_trg_min.tbl') == "F": status = "F" 
    
    ## Time trigger > 85
    if TestUtils.validate_invalid_table('/cf/cont_size_trg_max.tbl') == "F": status = "F" 
    
    for rqmnt in ["DTN.6.08820", "DTN.6.03151"]:
        TestUtils.set_requirement_status(rqmnt, status)


    print("===========================================================")
    print("2. Duplicate bundle receipt - custody accepted, bundle discarded")
    print("===========================================================")
    #DTN.6.08280 signal custody accepted and discard the bundle
    
    ## Start nominal contact - large timer/trigger
    restart_contact_0('/cf/cont_rx_large_trig.tbl')

    ## Send a bundle
    bundle = Bundle(pri_block=primary_block, canon_blocks=[custody_transfer_block, payload_block])
    data_sender.write(bundle.to_bytes())

    wait(f"{target} {mib_reports_pkt} BUNDLE_COUNT_IN_CUSTODY == 1", 6)
    wait(f"{target} {mib_counts_pkt} BUNDLE_COUNT_CUSTODY_REQUEST == 1", 2)
    wait(f"{target} {mib_counts_pkt} BUNDLE_COUNT_ACCEPTED_CUSTODY == 1", 2)

    ## Send duplicate bundle
    data_sender.write(bundle.to_bytes())
    wait()
    if wait(f"{target} {mib_counts_pkt} BUNDLE_COUNT_REDUNDANT == 1", 6):
        status = "P"
    else:
        status = "F"
    for rqmnt in ["DTN.6.08282"]:
        TestUtils.set_requirement_status(rqmnt, status)
        
    if wait(f"{target} {mib_counts_pkt} BUNDLE_COUNT_ACCEPTED_CUSTODY == 2", 1):
        status = "P"
    else:
        status = "F"
    for rqmnt in ["DTN.6.08280"]:
        TestUtils.set_requirement_status(rqmnt, status)
    
    if wait(f"{target} {mib_counts_pkt} BUNDLE_COUNT_DISCARDED == 1", 1):
        status = "P"
    else:
        status = "F"
    for rqmnt in ["DTN.6.08280"]:
        TestUtils.set_requirement_status(rqmnt, status)
    
    # Do sanity checks
    wait(f"{target} {mib_counts_pkt} BUNDLE_COUNT_DELETED == 1", 2) 
    wait(f"{target} {mib_reports_pkt} BUNDLE_COUNT_IN_CUSTODY == 1", 6)
    wait(f"{target} {mib_reports_pkt} BUNDLE_COUNT_STORED == 1", 6)


    print("=============================================================")
    print("3. Add application rejected when paramSupportCustody is false")
    print("=============================================================")
    #BPNODE 541: Could not add application with channel ID 0, RC = -352
    
    ## Set PARAM_SUPPORT_CUSTODY = 'FALSE'
    cmd(f"{target} BPNODE_CMD_STOP_APPLICATION with CHAN_ID 0")
    cmd(f"{target} BPNODE_CMD_REMOVE_APPLICATION with CHAN_ID 0")
    wait(2)
    cmd("DTNFSW-1 BPNODE_CMD_SET_MIB_ITEM with EID_MAXNODE 100, EID_MINNODE 100, MIB_ITEM 'PARAM_SUPPORT_CUSTODY', VALUE 0")
    wait(f"{target} {mib_config_hk} PARAM_SUPPORT_CUSTODY == 'FALSE'", 6) 

    ## Send ADD_APPLICATION directive and verify rejection
    status = TestUtils.send_command("BPNODE_CMD_ADD_APPLICATION with CHAN_ID 0", TestUtils.INVALID_CMD_TYPE)
    for rqmnt in ["DTN.6.03172"]:
        TestUtils.set_requirement_status(rqmnt, status)

    ## Verify error event
    BPLIB_NC_ADD_APP_ERR_EID=541
    TestUtils.verify_event('BPNODE', BPLIB_NC_ADD_APP_ERR_EID, "ERROR")

    wait()
    
    data_sender.disconnect()
    data_receiver.disconnect()

    wait()


    ###################################################################

    ##=================================================================
    ## Print requirement status
    ##=================================================================
    
    print("******************************")
    print("***** Requirement Status *****")
    print("******************************")
    for key, value in rqmnt_status.items():
        print(f"***    {key}: {value}")
    print("******************************")
    ###################################################################

#custody_errors()

