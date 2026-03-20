def custody_nominal(self):

    print("###################################################################")
    print("### Custody test")
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
        wait(f"{target} BPNODE_CHAN_CON_STAT_HK CON_STAT_RUN_STATE_0 == 'TORNDOWN'", 6)
        
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
    load_utility('DTNFSW-1/procedures/print_mib_counts_pkt.py')
    
    global rqmnt_status

    rqmnt_status = {    
        "DTN.5.00500":"U",
        "DTN.6.01020":"U",
        "DTN.6.01021":"U",
        "DTN.6.03060":"U",
        "DTN.6.03130":"U",
        "DTN.6.03171":"U",
        #"DTN.6.04272":"U", #Checked in BE
        "DTN.6.04045":"U",
        "DTN.6.04570":"U",
        "DTN.6.05155":"U",
        "DTN.6.05160":"U",
        "DTN.6.07050":"U",
        "DTN.6.08030":"I", #reply
        "DTN.6.08060":"U",
        "DTN.6.08072":"U",
        "DTN.6.08074":"U",
        "DTN.6.08090":"U",
        "DTN.6.08100":"U",
        "DTN.6.08170":"U",
        "DTN.6.08180":"U",
        "DTN.6.08250":"U",
        "DTN.6.08260":"U",
        #"DTN.6.08270":"U", #source
        #"DTN.6.08283":"U", #source
        "DTN.6.08290":"U",
        #"DTN.6.08300":"U", # NOT authorized custodian
        #"DTN.6.08310":"U", # NOT authorized custodian
        "DTN.6.08315":"U",
        "DTN.6.08320":"U",
        "DTN.6.08322":"U",
        #"DTN.6.08323":"U", # source
        "DTN.6.08324":"I", # notify
        "DTN.6.08330":"U",
        #"DTN.6.08332":"U", # storage depleted 
        #"DTN.6.08333":"U", # source
        "DTN.6.08334":"U",
        #"DTN.6.08335":"U", # source
        "DTN.6.08336":"U",
        #"DTN.6.08337":"U", # source
        "DTN.6.08340":"U",
        "DTN.6.08350":"U",
        #"DTN.6.08360":"U", # source
        "DTN.6.08380":"I", # begin CCS
        "DTN.6.08390":"I", # map
        "DTN.6.08391":"I", 
        "DTN.6.08393":"U", # disposition code
        "DTN.6.08395":"U", # disposition code
        "DTN.6.08397":"I",
        "DTN.6.08401":"I", # CCS bundle analysis
        "DTN.6.08420":"U",
        "DTN.6.08430":"U",
        "DTN.6.08435":"U",
        #"DTN.6.08436":"U", # timeout for non-custodial bundles
        "DTN.6.08440":"U",
        "DTN.6.08460":"U",
        "DTN.6.08465":"I", # CCS CBOR Analysis
        "DTN.6.08480":"U",
        "DTN.6.08491":"U",
        #"DTN.6.08492":"U", # source
        "DTN.6.08493":"U", # bundleCountGeneratedRejected for AR/CCS
        #"DTN.6.08494":"U", # source
        "DTN.6.08572":"I", # notify CREB
        "DTN.6.08573":"I", 
        "DTN.6.08574":"I",
        "DTN.6.08580":"U",
        "DTN.6.08585":"U",
        "DTN.6.08590":"U",
        #"DTN.6.08592":"U", # source
        "DTN.6.08600":"U",
        "DTN.6.08610":"U",
        #"DTN.6.08620":"U", # source
        "DTN.6.08630":"U",
        "DTN.6.08640":"U",
        "DTN.6.08650":"U",
        #"DTN.6.08660":"U", # source
        "DTN.6.08662":"U", 
        "DTN.6.08670":"U",
        "DTN.6.08672":"U",
        "DTN.6.08680":"U",
        #"DTN.6.08690":"U", # source
        "DTN.6.08710":"U",
        #"DTN.6.08712":"U", # Checked in BE
        "DTN.6.08714":"U",
        "DTN.6.08715":"U",
        "DTN.6.08716":"I", #Bundle Sequence Number
        "DTN.6.08730":"U", 
        "DTN.6.08740":"U",
        #"DTN.6.08750":"U", # source
        "DTN.6.08760":"U",
        "DTN.6.08810":"U",
        "DTN.6.09485":"U",
        "DTN.6.09490":"I", # AR/CCS CBOR decode analysis from 2-node tests
        "DTN.6.09510":"U", 
        "DTN.6.09520":"I", # CBOR decode
        "DTN.6.09530":"U",
        "DTN.6.19090":"U",
        "DTN.6.19170":"U",
        "DTN.6.19180":"U",
        "DTN.6.19190":"U",
        "DTN.6.20010":"U",
        "DTN.6.20080":"U",
        "DTN.6.20090":"U",
        "DTN.6.26060":"U",
        "DTN.6.26270":"U",
        "DTN.6.26280":"U",
        "DTN.6.26290":"U",
        "DTN.6.26300":"U",
        "DTN.6.26310":"I", # AR/CCS CBOR decode analysis from 2-node tests
        "DTN.6.27410":"U", 
        "DTN.6.27450":"U", 
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
        lifetime=300000,
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
    chan_stat_pkt   = "BPNODE_CHAN_CON_STAT_HK"

    cmd("DTNFSW-1 CFE_EVS_CMD_ENABLE_APP_EVENT_TYPE with APP_NAME 'BPNODE', BIT_MASK 1")

    prompt("'rm bplib-storage.db*' and restart FSW")
    
    cmd("DTNFSW-1 TO_LAB_CMD_ENABLE_OUTPUT with DEST_IP '10.2.11.172'")

    ans = ask("Source or Destination node? [S/D]")
    
    if ans.upper() == 'S':
        print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        print("            Behavior as source node")
        print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")

        print("===========================================================")
        print("1. Bundle creation with CTEB")
        print("===========================================================")
        '''
        - Verify channel not configured for CT by default 08020
        - Load channel table with CTEB included 
        - Add application
        - Send ADU
        - Start tentative contact, egress, and verify CTEB stuff
        '''
        ## Behavior as source node
        
        print("------------------------------------------------------")
        print("Send ADU and verify CTEB in bundle ")
        print("------------------------------------------------------")
        #cmd("DTNFSW-1 BPNODE_CMD_STOP_APPLICATION with CHAN_ID 0")
        #cmd("DTNFSW-1 BPNODE_CMD_REMOVE_APPLICATION with CHAN_ID 0")
        #load_new_table('/cf/chan0_with_cteb.tbl')        
        #cmd("DTNFSW-1 BPNODE_CMD_ADD_APPLICATION with CHAN_ID 0")
        #cmd("DTNFSW-1 BPNODE_CMD_START_APPLICATION with CHAN_ID 0")

        ## Load nominal contacts table so bundle is forwarded
        restart_contact_0('/cf/contact_nominal.tbl')

        cmd(f"{target} BPNODE_CMD_RESET_ALL_COUNTERS")
        wait(2)
        
        ## Send ADU command
        cmd("DTNFSW-1 CFE_SB_CMD_SEND_SB_STATS")
        
        wait_packet(target, mib_counts_pkt, 2, 10)
        
        ## Receive bundle data and verify CTEB
        print("Waiting for bundle to be returned...")
        received_bundle = Bundle.from_bytes(data_receiver.read())
        print(f"Received bundle: {received_bundle.to_json()}")
        
        status = "P"
        
        print("Checking custody transfer block")
        check_expression(f"{len(received_bundle.canon_blocks)} == 5")
        check_expression(f"{received_bundle.canon_blocks[3].blk_type} == {BlockType.CUST_TRANS_EXT}")
        check_expression(f"{received_bundle.canon_blocks[3].blk_num} == {5}")
        '''
        DTN.6.08040: "blk_num"
        DTN.6.08060: "control_flags": 0
        DTN.6.08072: "node_num": 100, "service_num": 0
        DTN.6.08074: "bundle_seq_id": 1
        DTN.6.08090: CTEB
        DTN.6.08100: "blk_type": 13
        DTN.6.08110: "blk_num": 5
        DTN.6.08120: "control_flags": 0
        DTN.6.08130: "crc_typ3": 1
        '''
        for rqmnt in [
            "DTN.6.03171", 
            "DTN.6.08060", "DTN.6.08072", "DTN.6.08074", "DTN.6.08090", "DTN.6.08100", 
            "DTN.6.08714", "DTN.6.08715", "DTN.6.08716", 
            "DTN.6.26060", "DTN.6.26270", "DTN.6.26280", "DTN.6.26290", "DTN.6.26300", 
            "DTN.6.27410", "DTN.6.27450", 
            ]:
            TestUtils.set_requirement_status(rqmnt, status)

        if wait(f"{target} {mib_reports_pkt} BUNDLE_COUNT_IN_CUSTODY == 1", 6):
            status = "P"
        else:
            status = "F"
        for rqmnt in ["DTN.6.08170", "DTN.6.08180", "DTN.6.08290", "DTN.6.08340", "DTN.6.08350"]:
            TestUtils.set_requirement_status(rqmnt, status)
        
        if wait(f"{target} {mib_counts_pkt} BUNDLE_COUNT_CUSTODY_REQUEST == 1", 2):
            status = "P"
        else:
            status = "F"
        for rqmnt in ["DTN.6.08260"]:
            TestUtils.set_requirement_status(rqmnt, status)

        wait(f"{target} {mib_reports_pkt} BUNDLE_COUNT_STORED == 1", 6)
        
        wait()
        
        '''
        ## Verify RESET_BUNDLE_COUNTERS doesn't reset BUNDLE_COUNT_IN_CUSTODY
        cmd(f"{target} BPNODE_CMD_RESET_BUNDLE_COUNTERS")
        
        wait(6)
        if tlm(f"{target} {mib_reports_pkt} BUNDLE_COUNT_IN_CUSTODY") == 1: 
            status = "P"
        else:
            status = "F"
            print("!!! ERROR - BUNDLE_COUNT_IN_CUSTODY should not be be reset")
        for rqmnt in ["DTN.6.12940", "DTN.6.20080"]:
            TestUtils.set_requirement_status(rqmnt, status)            
        '''

        print("===========================================================")
        print("2. CCS receipt by custodian")
        print("===========================================================")
        '''
        Send 10 custodial bundles and store
        - 10 bundles stored and in custody
        Forward bundles on contact with large timer/triggers so no CSS is received
        - 10 bundles forwarded
        Create and send a CCS/AR bundle that indicates:
            - 5 bundles (1-5) accepted and 3 (7-9) rejected
            - 2 bundles (0 and 6) remain to be processed
        - AR bundle received
            - 5 bundles accepted and 3 rejected
            - 8 bundles deleted from storage
            - 5 bundles custody transferred
            - 2 bundles still in custody
        '''    
        ## Start receive-only contact with large triggers
        #restart_contact_0('/cf/contact_rx_only.tbl')
        restart_contact_0('/cf/cont_rx_large_trig.tbl')
        
        stored_cnt = tlm(f"{target} {mib_reports_pkt} BUNDLE_COUNT_STORED")
        custody_cnt = tlm(f"{target} {mib_reports_pkt} BUNDLE_COUNT_IN_CUSTODY")
        
        ## Send 10 custodial bundles 
        for num in range(10):        
            primary_block.creation_timestamp.sequence=num # no duplicate, unique bundle ID
            
            cteb = CustodyTransferBlock(
                blk_type=BlockType.AUTO,
                blk_num=4,
                control_flags=BlockPCFlags.REP_UNPROC,
                crc_type=CRCType.CRC16_X25,
                cteb_data=CTEBData({"bundle_seq_id": 2, "bundle_seq_num": num, "block_src_admin_eid": LOCAL_EID}),
                crc=CRCFlag.CALCULATE,
            )
            
            # Create and send the bundle
            bundle = Bundle(pri_block=primary_block, canon_blocks=[cteb, payload_block])
            data_sender.write(bundle.to_bytes())

        ## Check bundles are stored and in custody
        wait(f"{target} {mib_reports_pkt} BUNDLE_COUNT_STORED == {stored_cnt}+10", 6)
        wait(f"{target} {mib_reports_pkt} BUNDLE_COUNT_IN_CUSTODY == {custody_cnt}+10", 6)
        
        custody_cnt = tlm(f"{target} {mib_reports_pkt} BUNDLE_COUNT_IN_CUSTODY")        
        if wait(f"{target} {mib_counts_pkt} BUNDLE_COUNT_ACCEPTED_CUSTODY == {custody_cnt}", 2):
            status = "P"
        else:
            status = "F"
        for rqmnt in ["DTN.6.08322"]:
            TestUtils.set_requirement_status(rqmnt, status)

        wait()
            
        ## Start nominal contact with large timer/triggers so no CCS is received for a while
        #restart_contact_0('/cf/cont_lg_trg.tbl')
        restart_contact_0('/cf/contact_nominal.tbl')

        '''
        Testing with stored bundles DTNN-1485,1486,1487
        - seq_id increments for each new contact (1 for first contact, 2 for second, ...)
        
        restart_contact_0('/cf/cont_lg_trg.tbl')
        
        cteb_seq_ids  = []
        cteb_seq_nums = []
        
        for x in data_receiver.read_all(): 
            bundle = Bundle.from_bytes(x)
            print(bundle.to_json())
            cteb_seq_ids.append(bundle.canon_blocks[0].cteb_data.bundle_seq_id)
            cteb_seq_nums.append(bundle.canon_blocks[0].cteb_data..bundle_seq_num)
            
        print(cteb_seq_ids)
        print(cteb_seq_nums)
        
        '''
        received_bundle = Bundle.from_bytes(data_receiver.read()) # gets bundle stored in step 1
        wait(1)
        received_bundle = Bundle.from_bytes(data_receiver.read()) 
        #print(f"Received bundle: {received_bundle.to_json()}")

        custody_block = received_bundle.canon_blocks[0]
        cteb_seq_id = custody_block.cteb_data.bundle_seq_id

        wait()
        
        ## Create a CCS/AR bundle that indicates 5 bundles (1-5) accepted and 3 (7-9) rejected
        #  - 3 rejected bundles will remain in custody
        #  - 2 bundles, 0 and 6, will keep getting reforwarded, and remain in custody
        
        primary_block_ar = PrimaryBlock(
            version=7,
            control_flags=BundlePCFlags.IS_ADMIN_RECORD,
            crc_type=CRCType.CRC16_X25,
            dest_eid=LOCAL_EID,
            src_eid=EID({"uri": 2, "ssp": {"node_num": 101, "service_num": 1}}),
            rpt_eid=EID({"uri": 2, "ssp": {"node_num": 100, "service_num": 1}}),
            creation_timestamp=CreationTimestamp({"time": DtnTimeNowMs(), "sequence": 0}),
            lifetime=3600000,
            crc=CRCFlag.CALCULATE,
        )
        
        next_node_ccs = AdminRecordBlock(
            blk_type=BlockType.AUTO,
            blk_num=1,
            control_flags=0,
            crc_type=CRCType.CRC16_X25,
            record_type = AdminRecordType.COMPRESSED_CUSTODY_SIGNAL,
            record_content = CCSData({
                DispositionCode.CUSTODY_ACCEPTED: BundleSequenceCollection(
                                            bundle_seq_id=cteb_seq_id,
                                            first_seq_num=1,
                                            bundle_seq_range=[5]),
                DispositionCode.CUSTODY_REFUSED: BundleSequenceCollection(
                                            bundle_seq_id=cteb_seq_id,
                                            first_seq_num=7,
                                            bundle_seq_range=[3])
            }),
            crc=CRCFlag.CALCULATE
        )

        ar_ccs_bundle = Bundle(pri_block=primary_block_ar, canon_blocks=[next_node_ccs])

        ccs_recd            = tlm(f"{target} {mib_counts_pkt} BUNDLE_COUNT_CCS_RECEIVED")
        ar_recd             = tlm(f"{target} {mib_counts_pkt} BUNDLE_COUNT_RECEIVED_ADMIN_RECORD")
        custody_transferred = tlm(f"{target} {mib_counts_pkt} BUNDLE_COUNT_CUSTODY_TRANSFERRED")
        custody_rejected    = tlm(f"{target} {mib_counts_pkt} BUNDLE_COUNT_CUSTODY_REJECTED")
        reforwarded_cnt     = tlm(f"{target} {mib_counts_pkt} BUNDLE_COUNT_CUSTODY_RE_FORWARDED")
        forwarded_cnt       = tlm(f"{target} {mib_counts_pkt} BUNDLE_COUNT_FORWARDED")
        deleted_cnt         = tlm(f"{target} {mib_counts_pkt} BUNDLE_COUNT_DELETED")

        ## Send the AR/CCS bundle
        data_sender.write(ar_ccs_bundle.to_bytes())
        
        ## Check associated telemetry
        if wait(f"{target} {mib_counts_pkt} BUNDLE_COUNT_CCS_RECEIVED == {ccs_recd}+1", 6):
            status = "P"
        else:
            status = "F"
        for rqmnt in ["DTN.6.08585", "DTN.6.09520", "DTN.6.09530"]:
            TestUtils.set_requirement_status(rqmnt, status)
        
        if wait(f"{target} {mib_counts_pkt} BUNDLE_COUNT_RECEIVED_CUSTODY_SIGNAL == 8", 2):
            status = "P"
        else:
            status = "F"
        for rqmnt in ["DTN.6.08580", "DTN.6.08590"]:
            TestUtils.set_requirement_status(rqmnt, status)
        
        if wait(f"{target} {mib_counts_pkt} BUNDLE_COUNT_RECEIVED_ADMIN_RECORD == {ar_recd}+1", 2): 
            status = "P"
        else:
            status = "F"
        for rqmnt in ["DTN.6.01020", "DTN.6.01021", "DTN.6.05155", "DTN.6.09485"]:
            TestUtils.set_requirement_status(rqmnt, status)
        
        if wait(f"{target} {mib_counts_pkt} BUNDLE_COUNT_CUSTODY_TRANSFERRED == {custody_transferred}+5", 2):
            status = "P"
        else:
            status = "F"
        for rqmnt in ["DTN.6.08610", "DTN.6.08393"]:
            TestUtils.set_requirement_status(rqmnt, status)
        
        if wait(f"{target} {mib_counts_pkt} BUNDLE_COUNT_CUSTODY_REJECTED == {custody_rejected}+3", 2):
            status = "P"
        else:
            status = "F"
        for rqmnt in ["DTN.6.08330", "DTN.6.08680", "DTN.6.08395"]:
            TestUtils.set_requirement_status(rqmnt, status)            
        
        if wait(f"{target} {mib_reports_pkt} BUNDLE_COUNT_IN_CUSTODY == {custody_cnt}-5", 2): #10-8 
            status = "P"
        else:
            status = "F"
        for rqmnt in ["DTN.6.08630", "DTN.6.08650"]:
            TestUtils.set_requirement_status(rqmnt, status)
        
        if wait(f"{target} {mib_counts_pkt} BUNDLE_COUNT_DELETED == {deleted_cnt}+6", 2): #transferred+CCS 
            status = "P"
        else:
            status = "F"
        for rqmnt in ["DTN.6.08600"]:
            TestUtils.set_requirement_status(rqmnt, status)
        
        #wait(f"{target} {mib_reports_pkt} BUNDLE_COUNT_STORED == {stored_cnt}+2", 6)
        '''
        ## Verify custody rejected DEBUG event - moved below due to bundles discarded event after this
        #BPNODE 758: Bundles with sequence ID 3 and sequence numbers 7 - 9 were rejected by downstream node
        BPLIB_CT_REJECTED_DEBG_EID=758
        status = TestUtils.verify_event("BPNODE", BPLIB_CT_REJECTED_DEBG_EID, "DEBUG", directive=False)
        for rqmnt in ["DTN.6.08672"]:
            TestUtils.set_requirement_status(rqmnt, status)
        '''
        
        print("----------------------")
        print(" Bundle Retransmission")
        print("----------------------")
        
        ## Verify retransmission of 2 bundles (0 and 6), and 1 from previous step, every 60 sec
        if wait(f"{target} {mib_counts_pkt} BUNDLE_COUNT_CUSTODY_RE_FORWARDED == {reforwarded_cnt+3}", 70):
            status = "P"
        else:
            status = "F"
        for rqmnt in ["DTN.6.08435", "DTN.6.08640", "DTN.6.08662", "DTN.6.08670", "DTN.6.08710", "DTN.6.08740"]:
            TestUtils.set_requirement_status(rqmnt, status)
        
        if wait(f"{target} {mib_counts_pkt} BUNDLE_COUNT_FORWARDED == {forwarded_cnt+3}", 2):
            status = "P"
        else:
            status = "F"
        for rqmnt in ["DTN.6.04570", "DTN.6.07050", "DTN.6.08730"]:
            TestUtils.set_requirement_status(rqmnt, status)

        wait()
        
        print("===========================================================")
        print("3. Duplicate CCS receipt")
        print("===========================================================")    
    
        ## Send same AR/CCS again, verify error for each accepted bundle in CCS
        #BPNODE 752: Error, at least one bundle with sequence ID 3 in sequence number range [1-5] 
        #could not be found in the CTDB.
        
        data_sender.write(ar_ccs_bundle.to_bytes())
        
        if wait(f"{target} {mib_counts_pkt} BUNDLE_COUNT_CCS_RECEIVED == {ccs_recd}+2", 6):
            status = "P"
        else:
            status = "F"
        for rqmnt in ["DTN.6.08585"]:
            TestUtils.set_requirement_status(rqmnt, status)
        
        if wait(f"{target} {mib_counts_pkt} BUNDLE_COUNT_RECEIVED_CUSTODY_SIGNAL == 8+8", 2):
            status = "P"
        else:
            status = "F"
            #fails now with 11 - DTNN-1536
        for rqmnt in ["DTN.6.08590"]:
            TestUtils.set_requirement_status(rqmnt, status)        
        
        prompt("Expect events: BPNODE 752: Error, at least one bundle with sequence ID 3 in sequence number range [1-5] could not be found in the CTDB.")
    
        ## Verify custody rejected DEBUG event
        #BPNODE 758: Bundles with sequence ID 3 and sequence numbers 7 - 9 were rejected by downstream node
        BPLIB_CT_REJECTED_DEBG_EID=758
        status = TestUtils.verify_event("BPNODE", BPLIB_CT_REJECTED_DEBG_EID, "DEBUG", directive=False)
        for rqmnt in ["DTN.5.00500", "DTN.6.08672"]:
            TestUtils.set_requirement_status(rqmnt, status)
        
        wait()
        
        print("===========================================================")
        print("4. Bundle retransmissions stop after lifetime (300 sec)")
        print("===========================================================")

        lifetime = 300
        wait_time = 0
        stopped = False
        reforwarded_cnt = tlm(f"{target} {mib_counts_pkt} BUNDLE_COUNT_CUSTODY_RE_FORWARDED")
        while wait_time < lifetime+60:
            print("BUNDLE_COUNT_CUSTODY_RE_FORWARDED: ", reforwarded_cnt)
            wait(65)
            reforwarded_cnt_now = tlm(f"{target} {mib_counts_pkt} BUNDLE_COUNT_CUSTODY_RE_FORWARDED")
            if reforwarded_cnt_now == reforwarded_cnt+1: # one bundle from step 1 has a lifetime of 1 hour
                stopped = True
                break
                
            reforwarded_cnt = reforwarded_cnt_now
            wait_time += 65
        
        print("BUNDLE_COUNT_CUSTODY_RE_FORWARDED: ", reforwarded_cnt)
        if stopped:
            print("Refowarding stopped after lifetime as expected!")
        else:
            print("ERROR - Refowarding did not stop after lifetime")
            
        wait()
    

    ##!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        
    elif ans.upper() == 'D':
        print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        print("      Behavior as intermediate/destination node")
        print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        
        # Set the node as 200
        load_new_table('/cf/mib_pn_200_64.tbl')

        primary_block.lifetime = 3600000 #default
        
        print("===========================================================")
        print("1. Custodial and non-custodial bundle storage")
        print("===========================================================")
        '''
        - Create, or generate and send, mix of bundles (e.g., 1-6 for custody, 7-10 for no custody) from source node
        - Verify bundleCountCustodyRequest, bundleCountInCustody against bundleCountGeneratedAccepted/bundleCountReceived
            - bundle_count_stored shows all bundles (10)
            - bundle_count_in_custody shows those in custody (6)
            - The difference shows non-custodial bundles (4)
        '''
        ## Load receive-only contact table with large timer/triggers so bundles are stored 
        ## and no CCS bundle gets generated for a while
        restart_contact_0('/cf/cont_rx_large_trig.tbl')

        stored_cnt = tlm(f"{target} {mib_reports_pkt} BUNDLE_COUNT_STORED")
        ccs_cnt = tlm(f"{target} {mib_counts_pkt} BUNDLE_COUNT_GENERATED_CCS")
        ccs_accepted_cnt = tlm(f"{target} {mib_counts_pkt} BUNDLE_COUNT_GENERATED_ACCEPTED")

        ## Send 6 custodial bundles
        primary_block.creation_timestamp.time=DtnTimeNowMs()
        num_cust = 6
        for num in range(num_cust):
            primary_block.creation_timestamp.sequence=num
            cteb = CustodyTransferBlock(
                blk_type=BlockType.AUTO,
                blk_num=4,
                control_flags=BlockPCFlags.REP_UNPROC,
                crc_type=CRCType.CRC16_X25,
                cteb_data=CTEBData({"bundle_seq_id": 3, "bundle_seq_num": num, "block_src_admin_eid": LOCAL_EID}),
                crc=CRCFlag.CALCULATE,
            )        
            bundle = Bundle(pri_block=primary_block, canon_blocks=[cteb, payload_block])
            data_sender.write(bundle.to_bytes())

        ## Send 4 non-custodial bundles (no CTEB)
        num_non_cust = 4
        for num in range(num_non_cust):
            primary_block.creation_timestamp.sequence=num_cust+num
            bundle = Bundle(pri_block=primary_block, canon_blocks=[payload_block])
            data_sender.write(bundle.to_bytes())

        # Verify custodial and non-custodial bundles are all stored
        ## non-custodial bundles = stored bundles - bundles in custody
        if wait(f"{target} {mib_reports_pkt} BUNDLE_COUNT_STORED == {stored_cnt+num_cust+num_non_cust}", 6):
            status = "P"
        else:
            status = "F"
        for rqmnt in ["DTN.6.08250"]:
            TestUtils.set_requirement_status(rqmnt, status)

        if wait(f"{target} {mib_reports_pkt} BUNDLE_COUNT_IN_CUSTODY == {num_cust}", 6): #08350
            status = "P"
        else:
            status = "F"
        for rqmnt in ["DTN.6.08350"]:
            TestUtils.set_requirement_status(rqmnt, status)

        if wait(f"{target} {mib_counts_pkt} BUNDLE_COUNT_CUSTODY_REQUEST == {num_cust}", 2):
            status = "P"
        else:
            status = "F"
        for rqmnt in ["DTN.6.08260"]:
            TestUtils.set_requirement_status(rqmnt, status)

        if wait(f"{target} {mib_counts_pkt} BUNDLE_COUNT_ACCEPTED_CUSTODY == {num_cust}", 2): 
            status = "P"
        else:
            status = "F"
        for rqmnt in ["DTN.6.08320", "DTN.6.08322"]:
            TestUtils.set_requirement_status(rqmnt, status)

        wait()
        
        
        print("===========================================================")
        print("2. CCS bundle under construction closed on contact stop")
        print("===========================================================")
        stored_cnt = tlm(f"{target} {mib_reports_pkt} BUNDLE_COUNT_STORED")
        cust_cnt = tlm(f"{target} {mib_reports_pkt} BUNDLE_COUNT_IN_CUSTODY")
        ccs_cnt = tlm(f"{target} {mib_counts_pkt} BUNDLE_COUNT_GENERATED_CCS")
        ccs_accepted_cnt = tlm(f"{target} {mib_counts_pkt} BUNDLE_COUNT_GENERATED_ACCEPTED")
        #ccs_forwarded_cnt = tlm(f"{target} {mib_counts_pkt} BUNDLE_COUNT_FORWARDED")
        '''
        # Ingress a few bundles
        for num in range(3):
            primary_block.creation_timestamp.sequence += 1
            cteb.cteb_data.bundle_seq_id=5
            cteb.cteb_data.bundle_seq_num=10+num
            bundle = Bundle(pri_block=primary_block, canon_blocks=[cteb, payload_block])
            data_sender.write(bundle.to_bytes())

        wait(f"{target} {mib_reports_pkt} BUNDLE_COUNT_IN_CUSTODY == {cust_cnt+3}", 6)
        
        wait()
        '''
        ## Stop contact 
        cmd(f"{target} {stop_cont_0}")

        ## Verify CCS bundle under construction is closed
        if wait(f"{target} {mib_counts_pkt} BUNDLE_COUNT_GENERATED_CCS == {ccs_cnt+1}", 10): 
            status = "P"
        else:
            status = "F"
        for rqmnt in ["DTN.6.08810", "DTN.6.09510"]:
            TestUtils.set_requirement_status(rqmnt, status)

        if wait(f"{target} {mib_counts_pkt} BUNDLE_COUNT_GENERATED_ACCEPTED == {ccs_accepted_cnt+1}", 2): 
            status = "P"
        else:
            status = "F"
        for rqmnt in ["DTN.6.08491"]:
            TestUtils.set_requirement_status(rqmnt, status)

        if wait(f"{target} {mib_counts_pkt} BUNDLE_COUNT_ACCEPTED_CUSTODY == {num_cust}", 2): 
            status = "P"
        else:
            status = "F"
        for rqmnt in ["DTN.6.08322"]:
            TestUtils.set_requirement_status(rqmnt, status)

        if wait(f"{target} {mib_counts_pkt} BUNDLE_COUNT_GENERATED_CUSTODY_SIGNAL == {num_cust}", 2):
            status = "P"
        else:
            status = "F"
        for rqmnt in ["DTN.6.08334"]:
            TestUtils.set_requirement_status(rqmnt, status)
        
        if not wait(f"{target} {mib_reports_pkt} BUNDLE_COUNT_STORED == {stored_cnt+1}", 6): #CCS
            print("ERROR - BUNDLE_COUNT_STORED did not update as expected")
            wait()
        
        wait()
        
        ## Receive bundle data and verify CCS
        load_new_table('/cf/cont2_send_ccs.tbl')        
        cmd(f"{target} BPNODE_CMD_CONTACT_SETUP with CONTACT_ID 2")
        cmd(f"{target} BPNODE_CMD_CONTACT_START with CONTACT_ID 2")
        
        print("Waiting for bundle to be returned...")
        received_bundle = Bundle.from_bytes(data_receiver.read())
        print(f"Received bundle: {received_bundle.to_json()}")

        wait()

        print("===========================================================")
        print("3. CCS bundle generation on CS time trigger")
        print("===========================================================")
        ## Verify CCS bundle is generated after time trigger (60 sec)
        #stored_cnt = tlm(f"{target} {mib_reports_pkt} BUNDLE_COUNT_STORED")
        #cust_cnt = tlm(f"{target} {mib_reports_pkt} BUNDLE_COUNT_IN_CUSTODY")
        ccs_cnt = tlm(f"{target} {mib_counts_pkt} BUNDLE_COUNT_GENERATED_CCS")
        ccs_accepted_cnt = tlm(f"{target} {mib_counts_pkt} BUNDLE_COUNT_GENERATED_ACCEPTED")

        restart_contact_0('/cf/cont_rx_cstime_60s.tbl') 
        
        # Ingress a bundle
        primary_block.creation_timestamp.sequence += 1
        cteb.cteb_data.bundle_seq_id=17
        cteb.cteb_data.bundle_seq_num=7
        bundle = Bundle(pri_block=primary_block, canon_blocks=[cteb, payload_block])
        data_sender.write(bundle.to_bytes())
        
        if wait(f"{target} {mib_counts_pkt} BUNDLE_COUNT_GENERATED_CCS == {ccs_cnt+1}", 70):
            status = "P"
        else:
            status = "F"
        for rqmnt in ["DTN.6.08420", "DTN.6.08440", "DTN.6.08460", "DTN.6.08480"]:
            TestUtils.set_requirement_status(rqmnt, status)

        if wait(f"{target} {mib_counts_pkt} BUNDLE_COUNT_GENERATED_ACCEPTED == {ccs_accepted_cnt+1}", 2):
            status = "P"
        else:
            status = "F"
        for rqmnt in ["DTN.6.08491"]:
            TestUtils.set_requirement_status(rqmnt, status)
                
        #wait(f"{target} {mib_reports_pkt} BUNDLE_COUNT_STORED == {stored_cnt+1}", 6) # No CCS, forwarded
        #wait(f"{target} {mib_reports_pkt} BUNDLE_COUNT_IN_CUSTODY == {cust_cnt+1}", 6)

        wait()
        
        print("Waiting for bundle to be returned...")
        received_bundle = Bundle.from_bytes(data_receiver.read())
        print(f"Received bundle: {received_bundle.to_json()}")

        wait()


        print("===========================================================")
        print("4. CCS bundle generation on CS size trigger")
        print("===========================================================")
        '''
        BPLIB_MAX_CS_SIZE_TRIGGER_ALLOWED = 
               BPLIB_MINIMUM_ENCODED_CCS_LEN (63)+ 
               (BPLIB_CT_MAX_SEQ_RANGE_LEN (11) * BPLIB_CT_MAX_SEQ_COLLECTIONS (2))
        BPLIB_MIN_CS_SIZE_TRIGGER_ALLOWED = BPLIB_MINIMUM_ENCODED_CCS_LEN (63)
        '''
        ## Restart contact with size trigger 63
        #stored_cnt = tlm(f"{target} {mib_reports_pkt} BUNDLE_COUNT_STORED")
        ccs_cnt = tlm(f"{target} {mib_counts_pkt} BUNDLE_COUNT_GENERATED_CCS")
        ccs_accepted_cnt = tlm(f"{target} {mib_counts_pkt} BUNDLE_COUNT_GENERATED_ACCEPTED")

        restart_contact_0('/cf/cont_rx_cssize_min.tbl') 

        # Ingress a bundle
        primary_block.creation_timestamp.sequence += 1
        cteb.cteb_data.bundle_seq_id=7
        cteb.cteb_data.bundle_seq_num=5
        bundle = Bundle(pri_block=primary_block, canon_blocks=[cteb, payload_block])
        data_sender.write(bundle.to_bytes())
        
        ## Verify CCS bundle generation
        if wait(f"{target} {mib_counts_pkt} BUNDLE_COUNT_GENERATED_CCS == {ccs_cnt+1}", 6):
            status = "P"
        else:
            status = "F"
        for rqmnt in ["DTN.6.08430", "DTN.6.08480"]:
            TestUtils.set_requirement_status(rqmnt, status)
        
        wait()
        
        print("Waiting for bundle to be returned...")
        received_bundle = Bundle.from_bytes(data_receiver.read())
        print(f"Received bundle: {received_bundle.to_json()}")

        wait()


        print("===========================================================")
        print("5. Custodial (and non-custodial) bundle delivery")
        print("===========================================================")
        #All bundles, custodial(10) and non-custodial(4), should be delivered
        #DTNN-1524 Stored custodial bundles don't get delivered when channel is started
        #Custodial bundles are delivered only if the channel has already been started, i.e., they are not stored.
        
        #Only 4 sre delivered???
        #CFE_SB 21: Send Err:Invalid MsgId(0x0)in msg,App BPNODE.BPNODE.ADU_TX_0
        #   - due to invalid payload
        
        cust_cnt = tlm(f"{target} {mib_reports_pkt} BUNDLE_COUNT_IN_CUSTODY")
        deleted_cnt = tlm(f"{target} {mib_counts_pkt} BUNDLE_COUNT_DELETED")

        ## Set up and start channel for ADU delivery
        cmd(f"{target} BPNODE_CMD_STOP_APPLICATION with CHAN_ID 0")
        cmd(f"{target} BPNODE_CMD_REMOVE_APPLICATION with CHAN_ID 0")
        load_new_table('/cf/chan0_serv_64.tbl')
        cmd(f"{target} BPNODE_CMD_ADD_APPLICATION with CHAN_ID 0")
        cmd(f"{target} BPNODE_CMD_START_APPLICATION with CHAN_ID 0")

        ## Verify custodial and non-custodial bundles get delivered, and deleted
        if wait(f"{target} {mib_counts_pkt} BUNDLE_COUNT_DELIVERED == {cust_cnt+num_non_cust}", 6):
            status = "P"
        else:
            status = "F"
            print("ERROR - BUNDLE_COUNT_DELIVERED not as expected")
        for rqmnt in ["DTN.6.03060"]:
            TestUtils.set_requirement_status(rqmnt, status)

        if wait(f"{target} {mib_counts_pkt} BUNDLE_COUNT_DELETED == {deleted_cnt+cust_cnt+num_non_cust}", 6):
            status = "P"
        else:
            status = "F"
            print("ERROR - BUNDLE_COUNT_DELETED not as expected")
        for rqmnt in ["DTN.6.05160", "DTN.6.08760"]:
            TestUtils.set_requirement_status(rqmnt, status)

        wait()
        
        
        print("===============================================================")
        print(" 6. Custodial bundle rejection in channel PASSIVE_ABANDON state")
        print("===============================================================")
        #BPNODE 758: Bundle custody rejected. src_eid=ipn:101.1, creation_time=824303017615, seq_num=12.
        
        deleted_cnt = tlm(f"{target} {mib_counts_pkt} BUNDLE_COUNT_DELETED")

        cmd(f"{target} BPNODE_CMD_SET_REGISTRATION_STATE with CHAN_ID 0, REG_STATE 'PASSIVE_ABANDON'")
        wait(f"{target} {chan_stat_pkt} CHAN_STAT_REG_STATE_0 == 'PASSIVE_ABANDON'", 6)
        
        # Ingress a bundle
        primary_block.creation_timestamp.sequence += 1
        cteb.cteb_data.bundle_seq_id=17
        cteb.cteb_data.bundle_seq_num=5
        bundle = Bundle(pri_block=primary_block, canon_blocks=[cteb, payload_block])
        data_sender.write(bundle.to_bytes())        

        if wait(f"{target} {mib_counts_pkt} BUNDLE_COUNT_REJECTED_CUSTODY == 1", 6):
            status = "P"
        else:
            status = "F"
            print("ERROR - BUNDLE_COUNT_REJECTED_CUSTODY not as expected")
        for rqmnt in ["DTN.6.08315", "DTN.6.08336"]:
            TestUtils.set_requirement_status(rqmnt, status)

        if wait(f"{target} {mib_counts_pkt} BUNDLE_COUNT_ABANDONED == 1", 6):
            status = "P"
        else:
            status = "F"
            print("ERROR - BUNDLE_COUNT_ABANDONED not as expected")
        for rqmnt in ["DTN.6.03130"]:
            TestUtils.set_requirement_status(rqmnt, status)

        if wait(f"{target} {mib_counts_pkt} BUNDLE_COUNT_DELETED == {deleted_cnt+1}", 6):
            status = "P"
        else:
            status = "F"
            print("ERROR - BUNDLE_COUNT_DELETED not as expected")
        for rqmnt in ["DTN.6.04045"]:
            TestUtils.set_requirement_status(rqmnt, status)
        
        #TBD Verify INFO event
        
        
        wait()
        
    ##!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    else:
        print("Invalid answer")
        exit()
    
    ###################################################################

    print("===========================================================")
    print(" Reset Error/Bundle Counters")
    print("===========================================================")
    #bundleCountInCustody should not be reset DTNN-1522
    
    # Print counters prior to reset for reference
    print_mib_counts_pkt(target)
    
    ## Send RESET_ERROR_COUNTERS command
    TestUtils.reset_counters("ERROR")
    
    ## Send RESET_BUNDLE_COUNTERS command
    TestUtils.reset_counters("BUNDLE")
    '''
    cmd(f"{target} BPNODE_CMD_RESET_BUNDLE_COUNTERS")
    wait(6)
    
    count_list = [
        "BUNDLE_COUNT_CCS_RECEIVED",
        "BUNDLE_COUNT_CUSTODY_REJECTED",
        "BUNDLE_COUNT_CUSTODY_REQUEST",
        "BUNDLE_COUNT_CUSTODY_RE_FORWARDED",
        "BUNDLE_COUNT_CUSTODY_TRANSFERRED",
        "BUNDLE_COUNT_DELETED",
        "BUNDLE_COUNT_DEPLETED",
        "BUNDLE_COUNT_FORWARDED",
        "BUNDLE_COUNT_GENERATED_ACCEPTED",
        "BUNDLE_COUNT_GENERATED_CCS",
        "BUNDLE_COUNT_GENERATED_CUSTODY_SIGNAL",
        "BUNDLE_COUNT_ACCEPTED_CUSTODY",
        "BUNDLE_COUNT_RECEIVED_ADMIN_RECORD",
        "BUNDLE_COUNT_RECEIVED_CUSTODY_SIGNAL",
        "BUNDLE_COUNT_REDUNDANT",
        "BUNDLE_COUNT_REJECTED_CUSTODY",
    ]
    
    ## Verify counts are reset
    status = "P"
    for count in count_list:
        if tlm(f"{target} {mib_counts_pkt} {count}") != 0:
            print(f"!!! ERROR - {count} did not reset")
            status = "F"
    
    for rqmnt in ["DTN.6.12940", "DTN.6.20010", "DTN.6.20080"]:
        TestUtils.set_requirement_status(rqmnt, status)
    '''
    
    wait()
    
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

#custody_nominal("xxx")
