def bundle_egress_nominal(self):

    print("###################################################################")
    print("### Bundle Egress test - Nominal")
    print("###################################################################")

    from dtntools.dtncla.udp import UdpTxSocket, UdpRxSocket
    from dtntools.dtngen.bundle import Bundle
    load_utility ("DTNFSW-1/procedures/build_tests/test_globals.py")
    load_utility ("DTNFSW-1/procedures/build_tests/test_utils.py")
    load_utility ("DTNFSW-1/procedures/dtngen_utils.py")
    load_utility ("DTNFSW-1/procedures/load_new_table.py")
       
    global rqmnt_status

    # Initialize requirement status
    rqmnt_status = {
        "DTN.6.04160":"U", 
        "DTN.6.04180":"U", 
        "DTN.6.04200":"U", 
        "DTN.6.04272":"U", 
        "DTN.6.04320":"I",
        "DTN.6.04322":"I",
        "DTN.6.04370":"I",
        "DTN.6.04371":"I",
        "DTN.6.04390":"U",
        "DTN.6.04610":"U", 
        "DTN.6.07050":"U", 
        "DTN.6.07065":"U", 
        "DTN.6.08712":"U", 
        "DTN.6.12062":"U", 
        "DTN.6.12290":"U", 
        "DTN.6.12362":"U", 
        "DTN.6.12372":"U", 
        "DTN.6.12390":"U",
        "DTN.6.15001":"U", 
        "DTN.6.15011":"U", 
        "DTN.6.15012":"U", 
        "DTN.6.15061":"U", 
        "DTN.6.15071":"U", 
        "DTN.6.15141":"U", 
        "DTN.6.15144":"U", 
        "DTN.6.15157":"U", 
        "DTN.6.15281":"U",
        "DTN.6.19170":"U", 
        "DTN.6.19180":"U", 
        "DTN.6.19190":"U", 
        "DTN.6.19360":"U", 
        "DTN.6.19390":"U", 

        #reset requirements
        "DTN.6.12120":"U", 
        "DTN.6.12150":"U",
        "DTN.6.19090":"U", 
        "DTN.6.20010":"U",
        "DTN.6.20080":"U",
        "DTN.6.20090":"U",
    }

    ## Copy needed test tables from COSMOS to DTNFSW
    prompt("Copy these tables to FSW build/exe/cpu1/cf folder:\n\n" + 
           " - contact_rx_only.tbl\n" +
           " - contact_nominal.tbl\n" +
           " - cont_erate_lim.tbl"          )

    ## Destination EID configuration for Contact 0
    dest_node_0    = 200
    dest_service_0 = 64

    ## Destination EID configuration for Contact 1
    dest_node_1    = 400
    dest_service_1 = 42

    ## Destination EID configuration (for Contact 2)
    dest_node_2    = 600
    dest_service_2 = 12

    ## Address/port configuration
    dest_ip   = DTN_NODE_IP_ADDR
    dest_port_1 = 4501
    dest_port_2 = 4502
    
    local_ip = "0.0.0.0"
    local_port = 4551

    ## Configure/connect Data senders and receivers
    data_sender_0 = UdpTxSocket(dest_ip, dest_port_1) 
    data_sender_0.connect()

    data_sender_2 = UdpTxSocket(dest_ip, dest_port_2) 
    data_sender_2.connect()

    data_receiver = UdpRxSocket(local_ip, local_port)
    data_receiver.connect()
    
    mib_counts_pkt = "BPNODE_NODE_MIB_COUNTERS_HK"
    mib_reports_pkt = "BPNODE_NODE_MIB_REPORTS_HK"
    cont_stat_pkt = "BPNODE_CHAN_CON_STAT_HK"
    
    cmd(f"{target} BPNODE_CMD_RESET_ALL_COUNTERS")    
    
    ## Print MIB Reports packet
    TestUtils.print_mib_reports_pkt()
    
    ## Print Storage packet
    TestUtils.print_storage_pkt()

    ## Enable DEBUG events
    cmd(f"{target} CFE_EVS_CMD_ENABLE_APP_EVENT_TYPE with APP_NAME 'BPNODE', BIT_MASK 1")

    print("===========================================================")
    print("1. Egress Bundles - Nominal")
    print("===========================================================")
    
    print("-----------------------------------------------------------")
    print("1.1 Store a known number of bundles")
    print("-----------------------------------------------------------")

    # Set up a contact so bundles are stored but not forwarded
    # Destination node in contact table is not dest_node (bundle destination)
    load_new_table('/cf/contact_rx_only.tbl')

    # Generate bundles
    num_bundles_0 = 20
    payload = b'\xAA'*1000
    
    print("Generating bundles ...")
    DTNGenUtils.generate_bundles(dest_node_0, dest_service_0, num_bundles_0, payload)

    # Set up and start contact
    cmd(f"{target} BPNODE_CMD_CONTACT_SETUP with CONTACT_ID 0")
    wait(1)
    cmd(f"{target} BPNODE_CMD_CONTACT_START with CONTACT_ID 0")
    
    # Send bundles to storage
    print(f"Sending {num_bundles_0} bundles to DTN Node ...")
    DTNGenUtils.send_bundles(num_bundles_0, dest_node_0, data_sender_0)

    item_name = "BUNDLE_COUNT_STORED"
    exp_val = num_bundles_0
    
    status = TestUtils.verify_item(mib_reports_pkt, item_name, exp_val)

    # Stop and teardown contact
    cmd(f"{target} BPNODE_CMD_CONTACT_STOP with CONTACT_ID 0")
    wait(1)
    cmd(f"{target} BPNODE_CMD_CONTACT_TEARDOWN with CONTACT_ID 0")
    
    print("-----------------------------------------------------------")
    print("1.2 Set up nominal contact")
    print("-----------------------------------------------------------")
        
    # Load nominal contacts table
    load_new_table('/cf/contact_nominal.tbl')

    status = TestUtils.send_command("BPNODE_CMD_CONTACT_SETUP with CONTACT_ID 0")

    for rqmnt in [
        "DTN.6.12062", "DTN.6.12290", "DTN.6.15001",
        "DTN.6.15281", "DTN.6.19360", "DTN.6.19390"
        ]:
        TestUtils.set_requirement_status(rqmnt, status)

    print("-----------------------------------------------------------")
    print("1.3 Start contact")
    print("-----------------------------------------------------------")

    # Get the timestamp of the last event and use it to search for later events 
    last_event_time_str = tlm(f"{target} CFE_EVS_LONG_EVENT_MSG PACKET_TIME")[0:-6]

    status = TestUtils.send_command("BPNODE_CMD_CONTACT_START with CONTACT_ID 0")

    for rqmnt in ["DTN.6.12362"]:
        TestUtils.set_requirement_status(rqmnt, status)
    
    print("..................................")
    print("1.3.1 Verify egress rate telemetry")
    print("..................................")
    status = "F"
   
    if wait(f"{target} {mib_reports_pkt} BUNDLE_EGRESS_RATE_BUNDLES_PER_SEC > 0", 6) and \
       wait(f"{target} {mib_reports_pkt} BUNDLE_EGRESS_RATE_BITS_PER_SEC > 0", 6): status = "P"
       
    print("BUNDLE_EGRESS_RATE_BUNDLES_PER_SEC:", 
        tlm(f"{target} {mib_reports_pkt} BUNDLE_EGRESS_RATE_BUNDLES_PER_SEC"))
    print("BUNDLE_EGRESS_RATE_BITS_PER_SEC:",
        tlm(f"{target} {mib_reports_pkt} BUNDLE_EGRESS_RATE_BITS_PER_SEC"))
    
    if status == "F":            
        print("ERROR - BUNDLE_EGRESS_RATE BUNDLES_PER_SEC/BITS_PER_SEC=0")
        
    for rqmnt in ["DTN.6.07065"]:
        TestUtils.set_requirement_status(rqmnt, status)
        
    print(".........................................")
    print("1.3.2 Verify stored bundles are forwarded")
    print(".........................................")
    
    item_name = "BUNDLE_COUNT_FORWARDED"
    exp_val = num_bundles_0
    
    status = TestUtils.verify_item(mib_counts_pkt, item_name, exp_val)
    '''
    sent_bundle = Bundle.from_json_file(f'/bundles/{dest_node}/generated_bundle_1.json')
    received_bundle = data_receiver.read()
    print(f"Received Bundle: {Bundle.from_bytes(received_bundle).to_json()}")    
    
    check_expression(f"'{received_bundle == sent_bundle}' == 'True'")
    '''

    for rqmnt in [
        "DTN.6.04390", "DTN.6.07050", 
        "DTN.6.15011", "DTN.6.15061", "DTN.6.15281"
        ]:
        TestUtils.set_requirement_status(rqmnt, status)
    
    print("........................................................")
    print("1.3.3 Verify forwarded bundles are deleted from storage ")
    print("........................................................")

    item_name = "BUNDLE_COUNT_STORED"
    exp_val = 0
    
    status = TestUtils.verify_item(mib_reports_pkt, item_name, exp_val)

    for rqmnt in ["DTN.6.04200", "DTN.6.04272", "DTN.6.04390", "DTN.6.08712"]:
        TestUtils.set_requirement_status(rqmnt, status)
    
    item_name = "BUNDLE_COUNT_DELETED"
    exp_val = num_bundles_0
    
    status = TestUtils.verify_item(mib_counts_pkt, item_name, exp_val)
    
    for rqmnt in ["DTN.6.04180"]:
        TestUtils.set_requirement_status(rqmnt, status)

    item_name = "BUNDLE_COUNT_DISCARDED"
    exp_val = num_bundles_0
    
    status = TestUtils.verify_item(mib_counts_pkt, item_name, exp_val)
    
    for rqmnt in ["DTN.6.04160"]:
        TestUtils.set_requirement_status(rqmnt, status)

    
    print("........................................................")
    print("1.3.3 Verify bundle deletion debug event ")
    print("........................................................")
    #BPNODE 614: Discarded 20 egressed bundles from storage
    BPLIB_STOR_DELETE_DBG_EID = 614
    #status = TestUtils.verify_event("BPNODE", BPLIB_STOR_DELETE_DBG_EID, "DEBUG")
    if TestUtils.find_event_in_log("BPNODE", BPLIB_STOR_DELETE_DBG_EID, "DEBUG", last_event_time_str):
        status = "p"
    else:
        status = "F"

    for rqmnt in ["DTN.6.04610"]:
        TestUtils.set_requirement_status(rqmnt, status)        
    
    
    print("-----------------------------------------------------------")
    print("1.4 Stop contact")
    print("-----------------------------------------------------------")

    status = TestUtils.send_command("BPNODE_CMD_CONTACT_STOP with CONTACT_ID 0")

    for rqmnt in ["DTN.6.12372"]:
        TestUtils.set_requirement_status(rqmnt, status)

    ## Tear down contact
    cmd(f"{target} BPNODE_CMD_CONTACT_TEARDOWN with CONTACT_ID 0")
    wait_check(f"{target} {cont_stat_pkt} CON_STAT_RUN_STATE_0 == 'TORNDOWN'", 6)
    

    print("............................................................")
    print("1.4.1 Verify bundle forwarding stops when contact is stopped")
    print("............................................................")
    '''
    - set up contact that only receives bundles and does not send    
    - store a large number of bundles
    - set up egress-rate-limited contact
    - start contact - forwarding will start 
    - stop contact after a short delay
    - verify forwarded bundles stops incrementing
    '''    
    
    ## Set up contact that only receives bundles and does not send
    ## Send bundles to storage
    load_new_table('/cf/contact_rx_only.tbl')
    
    ## Set up and start contact
    cmd(f"{target} BPNODE_CMD_CONTACT_SETUP with CONTACT_ID 0")
    cmd(f"{target} BPNODE_CMD_CONTACT_START with CONTACT_ID 0")
    wait_check(f"{target} {cont_stat_pkt} CON_STAT_RUN_STATE_0 == 'STARTED'", 6)
    
    num_loops = 20
    print(f"Sending {num_bundles_0*num_loops} bundles to DTN node ...")
    with disable_instrumentation():
        for _ in range(num_loops):
            DTNGenUtils.send_bundles(num_bundles_0, dest_node_0, data_sender_0)
    sent_bundles = num_bundles_0*num_loops
    
    wait_packet(target, mib_counts_pkt, 1, 6)
    wait_packet(target, mib_reports_pkt, 1, 6)
    received_cnt = tlm(f"{target} {mib_counts_pkt} BUNDLE_COUNT_RECEIVED")
    stored_cnt = tlm(f"{target} {mib_reports_pkt} BUNDLE_COUNT_STORED")
    print(f"BUNDLE_COUNT_RECEIVED: {received_cnt}  BUNDLE_COUNT_STORED: {stored_cnt}")

    ## Stop and teardown contact
    cmd(f"{target} BPNODE_CMD_CONTACT_STOP with CONTACT_ID 0")
    cmd(f"{target} BPNODE_CMD_CONTACT_TEARDOWN with CONTACT_ID 0")
    
    ## Load egress rate limited contacts table - forwarding will start 
    load_new_table('/cf/cont_erate_lim.tbl')
    
    ## Set up and start contact
    cmd(f"{target} BPNODE_CMD_CONTACT_SETUP with CONTACT_ID 0")
    cmd(f"{target} BPNODE_CMD_CONTACT_START with CONTACT_ID 0")
    #wait_check(f"{target} {cont_stat_pkt} CON_STAT_RUN_STATE_0 == 'STARTED'", 6)

    ## Stop contact after a short delay
    wait(5)
    cmd(f"{target} BPNODE_CMD_CONTACT_STOP with CONTACT_ID 0")
    
    wait_packet(target, mib_counts_pkt, 1, 6)
    forwarded_cnt = tlm(f"{target} {mib_counts_pkt} BUNDLE_COUNT_FORWARDED")
    print(f"BUNDLE_COUNT_FORWARDED: {forwarded_cnt}")
    
    ## Verify forwarded bundles stops incrementing
    wait_packet(target, mib_counts_pkt, 1, 6)
            
    if tlm(f"{target} {mib_counts_pkt} BUNDLE_COUNT_FORWARDED") == forwarded_cnt and \
            forwarded_cnt < received_cnt:
        print("Bundle forwarding stopped as expected")
        status = "P"
    else:
        print("ERROR - Bundle forwarding did not stop as expected")
        status = "F"    
    
    for rqmnt in ["DTN.6.15012", "DTN.6.15071", "DTN.6.15141", "DTN.6.15144"]:
        TestUtils.set_requirement_status(rqmnt, status)
        

    print("-----------------------------------------------------------")
    print("1.5 Bundle flow continuity within and between contacts")
    print("-----------------------------------------------------------")

    print("............................................................")
    print("1.5.1 Start contact, verify bundle forwarding resumes")
    print("............................................................")
    forwarded_cnt = tlm(f"{target} {mib_counts_pkt} BUNDLE_COUNT_FORWARDED")
    
    cmd(f"{target} BPNODE_CMD_CONTACT_START with CONTACT_ID 0")
    wait(10)
    if tlm(f"{target} {mib_counts_pkt} BUNDLE_COUNT_FORWARDED") > forwarded_cnt:
        print("Bundle forwarding resumed as expected")
    else:
        print("ERROR - Bundle forwarding did not resume as expected")
        
    
    print("...........................................................")
    print("1.5.2 Stop and teardown contact")
    print("...........................................................")
    # Bundles in queue flushed and pulled back to storage, queue deleted
    # CLA resources released
    
    cmd(f"{target} BPNODE_CMD_CONTACT_STOP with CONTACT_ID 0")
    wait(6)
    stored_cnt = tlm(f"{target} {mib_reports_pkt} BUNDLE_COUNT_STORED")
    forwarded_cnt = tlm(f"{target} {mib_counts_pkt} BUNDLE_COUNT_FORWARDED")

    cmd(f"{target} BPNODE_CMD_CONTACT_TEARDOWN with CONTACT_ID 0")
    
    wait_check(f"{target} {cont_stat_pkt} CON_STAT_RUN_STATE_0 == 'TORNDOWN'", 6)
    
    # Check bundle pullback to storage
    wait_check(f"{target} {mib_reports_pkt} BUNDLE_COUNT_STORED == {sent_bundles-forwarded_cnt}", 6)
    wait_check(f"{target} {mib_reports_pkt} BUNDLE_COUNT_STORED > {stored_cnt}", 1)
    
    
    print("...........................................................")
    print("1.5.3 Start next contact, verify successful start")
    print("...........................................................")
    # CLA resources made available    
    cmd(f"{target} BPNODE_CMD_CONTACT_SETUP with CONTACT_ID 0")
    cmd(f"{target} BPNODE_CMD_CONTACT_START with CONTACT_ID 0")
    if wait(f"{target} {cont_stat_pkt} CON_STAT_RUN_STATE_0 == 'STARTED'", 6):
        status = "P"
    else:
        status = "F"

    for rqmnt in ["DTN.6.12390"]:
        TestUtils.set_requirement_status(rqmnt, status)
        
        
    print("...........................................................")
    print("1.5.4 Verify all remaining bundles in storage get out")
    print("...........................................................")
    # No bundles should be lost in queue management    
    if wait(f"{target} {mib_reports_pkt} BUNDLE_COUNT_STORED == 0", 60):
        status = "P" 
    else:
        status = "F" 
    forwarded_cnt = tlm(f"{target} {mib_counts_pkt} BUNDLE_COUNT_FORWARDED")
    print(f"BUNDLE_COUNT_FORWARDED: {forwarded_cnt}")
        
    #for rqmnt in ["DTN.6.12400"]:
    #    TestUtils.set_requirement_status(rqmnt, status)
    
    '''
    print("...........................................................")
    print("1.x Contact 1 Egress - SB CLA")
    print("...........................................................")
    
    # Generate bundles
    num_bundles_1 = 15
    payload = b'\xAA'*1000
    DTNGenUtils.generate_bundles(dest_node_1, dest_service_1, num_bundles_1, payload)

    print("Send bundles to storage via contact 0")
    load_new_table('/cf/contact_rx_only.tbl')

    stored_cnt = tlm(f"{target} {mib_reports_pkt} BUNDLE_COUNT_STORED")

    cmd(f"{target} BPNODE_CMD_CONTACT_SETUP with CONTACT_ID 0")
    cmd(f"{target} BPNODE_CMD_CONTACT_START with CONTACT_ID 0")
        
    DTNGenUtils.send_bundles(num_bundles_1, dest_node_1, data_sender_0)
    print(f" ... sent {num_bundles_1} bundles to DTN Node")

    wait(f"{target} {mib_reports_pkt} BUNDLE_COUNT_STORED == stored_cnt+num_bundles_1", 6)
    
    print("Egress bundles from storage via contact 1")
    load_new_table('/cf/contact_nominal.tbl')
    
    received_cnt = tlm(f"{target} SB_CLA_OUT RECEIVED_COUNT")

    cmd(f"{target} BPNODE_CMD_CONTACT_SETUP with CONTACT_ID 1")
    cmd(f"{target} BPNODE_CMD_CONTACT_START with CONTACT_ID 1")
    wait(6)

    print("Verify bundles are received")
    TestUtils.verify_item("SB_CLA_OUT", "RECEIVED_COUNT", received_cnt+num_bundles_1)
    '''

    print("...........................................................")
    print("1.6 Egress on all contacts")
    print("...........................................................")
    
    # Teardown all contacts 
    for cont in range(1): # only 0 has been started
        cmd(f"{target} BPNODE_CMD_CONTACT_STOP with CONTACT_ID {cont}")
        cmd(f"{target} BPNODE_CMD_CONTACT_TEARDOWN with CONTACT_ID {cont}")
   
    ## Start all contacts with receive only contact table so bundles are stored
    load_new_table('/cf/contact_rx_only.tbl')
    
    for cont in range(3):
        cmd(f"{target} BPNODE_CMD_CONTACT_SETUP with CONTACT_ID {cont}")
        cmd(f"{target} BPNODE_CMD_CONTACT_START with CONTACT_ID {cont}")
        
    ## Generate and send bundles to all contacts
    stored_cnt = tlm(f"{target} {mib_reports_pkt} BUNDLE_COUNT_STORED")
    forwarded_cnt = tlm(f"{target} {mib_counts_pkt} BUNDLE_COUNT_FORWARDED")
    sb_received_cnt = tlm(f"{target} SB_CLA_OUT RECEIVED_COUNT")

    print("Generating bundles ...")
    num_bundles_0 = 10
    num_bundles_1 = 15
    num_bundles_2 = 20
    payload = b'\xAA'*1000
    DTNGenUtils.generate_bundles(dest_node_0, dest_service_0, num_bundles_0, payload)
    DTNGenUtils.generate_bundles(dest_node_1, dest_service_1, num_bundles_1, payload)
    DTNGenUtils.generate_bundles(dest_node_2, dest_service_2, num_bundles_2, payload)

    print("Sending bundles ...")
    DTNGenUtils.send_bundles(num_bundles_0, dest_node_0, data_sender_0)
    print(f" ... sent {num_bundles_0} dest_node_0 bundles")

    DTNGenUtils.send_bundles(num_bundles_1, dest_node_1, data_sender_2)
    print(f" ... sent {num_bundles_1} dest_node_1 bundles")

    DTNGenUtils.send_bundles(num_bundles_2, dest_node_2, data_sender_2)
    print(f" ... sent {num_bundles_2} dest_node_2 bundles")

    wait(6)
    
    ## Verify bundles from all contacts are stored
    item_name = "BUNDLE_COUNT_STORED"
    exp_val = stored_cnt+num_bundles_0+num_bundles_1+num_bundles_2
    TestUtils.verify_item(mib_reports_pkt, item_name, exp_val) 

    # Teardown all contacts
    for cont in range(3):
        cmd(f"{target} BPNODE_CMD_CONTACT_STOP with CONTACT_ID {cont}")
        cmd(f"{target} BPNODE_CMD_CONTACT_TEARDOWN with CONTACT_ID {cont}")

    ## Start all contacts with nominal contact table
    load_new_table('/cf/contact_nominal.tbl')

    for cont in range(3):
        cmd(f"{target} BPNODE_CMD_CONTACT_SETUP with CONTACT_ID {cont}")
        cmd(f"{target} BPNODE_CMD_CONTACT_START with CONTACT_ID {cont}")

    wait(5)

    ## Verify stored bundles are forwarded to resspective destinations
    status = "P"
    
    item_name = "BUNDLE_COUNT_FORWARDED"
    exp_val = forwarded_cnt+num_bundles_0+num_bundles_1+num_bundles_2
    if TestUtils.verify_item(mib_counts_pkt, item_name, exp_val) == "F":
        status = "F"

    if TestUtils.verify_item("SB_CLA_OUT", "RECEIVED_COUNT", sb_received_cnt+num_bundles_1) == "F":
        status - "F"
        
    for rqmnt in ["DTN.6.15157"]:
        TestUtils.set_requirement_status(rqmnt, status)
   
   #******************************************************************
    
    print("===========================================================")
    print(" 2. Reset Counters Directives")
    print("===========================================================")
    
    print("-----------------------------------------------------------")
    print(" 2.1 RESET_COUNTER")
    print("-----------------------------------------------------------")

    TestUtils.reset_counter("BUNDLE_COUNT_RECEIVED")
    TestUtils.reset_counter("BUNDLE_COUNT_FORWARDED")
    
    print("-----------------------------------------------------------")
    print("2.2. RESET_BUNDLE_COUNTERS")
    print("-----------------------------------------------------------")
    
    TestUtils.reset_counters("BUNDLE")

    print("-----------------------------------------------------------")
    print("2.3. RESET_ALL_COUNTERS")
    print("-----------------------------------------------------------")
    
    TestUtils.reset_counters("ALL")

    ##*****************************************************************
    ## Teardown all contacts
    for cont in range(3):
        cmd(f"{target} BPNODE_CMD_CONTACT_STOP with CONTACT_ID {cont}")
        cmd(f"{target} BPNODE_CMD_CONTACT_TEARDOWN with CONTACT_ID {cont}")    

    ## Disconnect data senders/receiver
    data_sender_0.disconnect()
    data_sender_2.disconnect()
    data_receiver.disconnect()

    ## Print MIB Reports packet
    TestUtils.print_mib_reports_pkt()
    
    ## Print Storage packet
    TestUtils.print_storage_pkt()
    
    #******************************************************************

    ###################################################################

    ##=================================================================
    ## Print requirement status
    ##=================================================================
    
    print ("******************************")
    print ("***** Requirement Status *****")
    print ("******************************")
    for key, value in rqmnt_status.items():
        print(f"***    {key}: {value}")
    print ("******************************")
    
    ###################################################################
    
    
## main
#bundle_egress_nominal("xxx")
#set_line_delay(0)

