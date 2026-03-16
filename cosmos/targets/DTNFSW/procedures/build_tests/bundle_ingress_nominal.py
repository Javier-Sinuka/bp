def bundle_ingress_nominal(self):

    print("###################################################################")
    print("### Bundle Ingress test - Nominal")
    print("###################################################################")

    from dtntools.dtncla.udp import UdpTxSocket
    load_utility ("DTNFSW-1/procedures/build_tests/test_globals.py")
    load_utility ("DTNFSW-1/procedures/build_tests/test_utils.py")
    load_utility ("DTNFSW-1/procedures/dtngen_utils.py")
    load_utility ("DTNFSW-1/procedures/load_new_table.py")
       
    global rqmnt_status

    # Initialize requirement status
    rqmnt_status = {
        #"DTN.6.04290":"U", 
        "DTN.6.04316":"U", 
        #"DTN.6.04317":"U", 
        #"DTN.6.04420":"U", 
        #"DTN.6.04422":"U", 
        "DTN.6.06430":"I", 
        "DTN.6.06500":"U", 
        "DTN.6.06552":"U", 
        #"DTN.6.06553":"U", 
        "DTN.6.12062":"U", 
        "DTN.6.12290":"U", 
        "DTN.6.12362":"U", 
        "DTN.6.12372":"U", 
        "DTN.6.15001":"U", 
        "DTN.6.15013":"U", 
        "DTN.6.15014":"U", 
        "DTN.6.15041":"U", 
        "DTN.6.15051":"U", 
        "DTN.6.15073":"U", 
        #"DTN.6.15121":"U", 
        #"DTN.6.15131":"U",
        "DTN.6.15141":"U", 
        "DTN.6.15143":"U", 
        "DTN.6.15155":"U", 
        #"DTN.6.15161":"U", 
        #"DTN.6.15195":"U", 
        #"DTN.6.15235":"U",
        #"DTN.6.15241":"U",
        "DTN.6.15281":"U",
        "DTN.6.19180":"U", 
        "DTN.6.19190":"U", 
        "DTN.6.19210":"U", 
        "DTN.6.19260":"U", 
        "DTN.6.19360":"U", 
        "DTN.6.19390":"U", 
        "DTN.6.23090":"U",

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
           " - cont_irate_lim.tbl"
          )

    ## Destination EID configuration (for Contact 0)
    dest_node_0    = 200
    dest_service_0 = 64

    ## Destination EID configuration (for Contact 2)
    dest_node_2    = 600
    dest_service_2 = 12

    ## Address/port configuration
    dest_ip   = DTN_NODE_IP_ADDR
    dest_port_0 = 4501 # Contact 0
    dest_port_2 = 4502 # Contact 2
        
    ## Configure/connect Data Senders
    data_sender_0 = UdpTxSocket(dest_ip, dest_port_0) 
    data_sender_0.connect()
    
    data_sender_2 = UdpTxSocket(dest_ip, dest_port_2) 
    data_sender_2.connect()
    

    cmd(f"{target} BPNODE_CMD_RESET_ALL_COUNTERS")

    mib_counts_pkt  = "BPNODE_NODE_MIB_COUNTERS_HK"
    mib_reports_pkt = "BPNODE_NODE_MIB_REPORTS_HK"
    chan_stat_pkt   = "BPNODE_CHAN_CON_STAT_HK"
    
    setup_cont    = "BPNODE_CMD_CONTACT_SETUP"
    start_cont    = "BPNODE_CMD_CONTACT_START"
    stop_cont     = "BPNODE_CMD_CONTACT_STOP"
    teardown_cont = "BPNODE_CMD_CONTACT_TEARDOWN"
    
    ## Print MIB Reports packet
    TestUtils.print_mib_reports_pkt()
    
    ## Print Storage packet
    TestUtils.print_storage_pkt()

    print("===========================================================")
    print("1. CONTACT 0")
    print("===========================================================")

    print("-----------------------------------------------------------")
    print("1.1 Set up contact")
    print("-----------------------------------------------------------")
    
    # Set up a receive only contact so bundles are stored but not forwarded
    # - Destination node in contact table is not bundle destination
    load_new_table('/cf/contact_rx_only.tbl')
    
    status = TestUtils.send_command(f"{setup_cont} with CONTACT_ID 0")    

    for rqmnt in [
        "DTN.6.12290", "DTN.6.15001", 
        "DTN.6.15281", "DTN.6.19360", "DTN.6.19390"
        ]:
        TestUtils.set_requirement_status(rqmnt, status)
   
    if tlm(f"{target} {chan_stat_pkt} CON_STAT_RUN_STATE_0") == 'SETUP':
        status = "P"
    else:
        print("ERROR - CON_STAT_RUN_STATE_0 not SETUP")
        status = "F"        
    
    for rqmnt in ["DTN.6.19210"]:
        TestUtils.set_requirement_status(rqmnt, status)
        
    print("-----------------------------------------------------------")
    print("1.2 Start contact")
    print("-----------------------------------------------------------")
    
    status = TestUtils.send_command(f"{start_cont} with CONTACT_ID 0")
    for rqmnt in ["DTN.6.12362"]:
        TestUtils.set_requirement_status(rqmnt, status)
        
    if tlm(f"{target} {chan_stat_pkt} CON_STAT_RUN_STATE_0") == 'STARTED':
        status = "P"
    else:
        print("ERROR - CON_STAT_RUN_STATE_0 not STARTED")
        status = "F"        
    
    for rqmnt in ["DTN.6.19210"]:
        TestUtils.set_requirement_status(rqmnt, status)
    
    print("-----------------------------------------------------------")
    print("1.3 Send known number of bundles with Data Sender")
    print("-----------------------------------------------------------")

    print("Generating bundles ...")
    num_bundles = 10
    payload = b'\xAA'*1000
    DTNGenUtils.generate_bundles(dest_node_0, dest_service_0, num_bundles, payload)

    print("Sending bundles to DTN Node ...")
    DTNGenUtils.send_bundles(num_bundles, dest_node_0, data_sender_0)
    print(f" ... sent {num_bundles} bundles to DTN Node")

    print("...................................")
    print("1.3.1 Verify ingress rate telemetry")
    print("...................................")
    status = "F"
   
    if wait(f"{target} {mib_reports_pkt} BUNDLE_INGRESS_RATE_BUNDLES_PER_SEC > 0", 6) and \
       wait(f"{target} {mib_reports_pkt} BUNDLE_INGRESS_RATE_BITS_PER_SEC > 0", 6): status = "P"
       
    print("BUNDLE_INGRESS_RATE_BUNDLES_PER_SEC:",
        tlm(f"{target} {mib_reports_pkt} BUNDLE_INGRESS_RATE_BUNDLES_PER_SEC"))
    print("BUNDLE_INGRESS_RATE_BITS_PER_SEC:",
        tlm(f"{target} {mib_reports_pkt} BUNDLE_INGRESS_RATE_BITS_PER_SEC"))
    
    if status == "F":            
        print("ERROR - BUNDLE_INGRESS_RATE BUNDLES_PER_SEC/BITS_PER_SEC=0")
        
    for rqmnt in ["DTN.6.06500"]:
        TestUtils.set_requirement_status(rqmnt, status)
        
    print("............................................")
    print("1.3.2 Verify bundles are received and stored")
    print("............................................")

    status = "P"
    item_name = "BUNDLE_COUNT_RECEIVED"
    exp_val = num_bundles
    if TestUtils.verify_item(mib_counts_pkt, item_name, exp_val) == "F":
        status = "F"

    item_name = "BUNDLE_COUNT_STORED"
    exp_val = num_bundles
    if TestUtils.verify_item(mib_reports_pkt, item_name, exp_val) == "F":
        status = "F"
    
    for rqmnt in [
            "DTN.6.04316", "DTN.6.06552", "DTN.6.15041", 
            "DTN.6.15051", "DTN.6.15281", "DTN.6.23090",             
            ]:
        TestUtils.set_requirement_status(rqmnt, status)


    print("-----------------------------------------------------------")
    print("1.4 Stop contact")
    print("-----------------------------------------------------------")

    status = TestUtils.send_command(f"{stop_cont} with CONTACT_ID 0")
    
    for rqmnt in ["DTN.6.19210", "DTN.6.12372"]:
        TestUtils.set_requirement_status(rqmnt, status)
        
    if tlm(f"{target} {chan_stat_pkt} CON_STAT_RUN_STATE_0") == 'STOPPED':
        status = "P"
    else:
        print("ERROR - CON_STAT_RUN_STATE_0 not STOPPED")
        status = "F"        
    
    for rqmnt in ["DTN.6.19210"]:
        TestUtils.set_requirement_status(rqmnt, status)
    
    print("-----------------------------------------------------------")
    print("1.5 Send bundles when contact is stopped")
    print("    Verify bundle reception stopped")
    print("-----------------------------------------------------------")

    received_cnt = tlm (f"{target} {mib_counts_pkt} BUNDLE_COUNT_RECEIVED")

    print("Sending bundles to DTN Node ...")
    DTNGenUtils.send_bundles(num_bundles, dest_node_0, data_sender_0)
    print(f" ... sent {num_bundles} bundles to DTN Node")
    
    wait_packet (target, mib_counts_pkt, 2, 10)
    if tlm (f"{target} {mib_counts_pkt} BUNDLE_COUNT_RECEIVED") == received_cnt:
        print("!!! No Bundle reception stopped as expected")
        status = "P"
    else:
        print("!!! ERROR - Bundles reception did not stop as expected")
        status = "F"
    
    for rqmnt in ["DTN.6.15141", "DTN.6.15143"]:
        TestUtils.set_requirement_status(rqmnt, status)

    
    print("-----------------------------------------------------------")
    print("1.6 Teardown contact")
    print("-----------------------------------------------------------")
 
    status = TestUtils.send_command(f"{teardown_cont} with CONTACT_ID 0")
      
    if tlm(f"{target} {chan_stat_pkt} CON_STAT_RUN_STATE_0") == 'TORNDOWN':
        status = "P"
    else:
        print("ERROR - CON_STAT_RUN_STATE_0 not TORNDOWN")
        status = "F"        
    
    for rqmnt in ["DTN.6.19210"]:
        TestUtils.set_requirement_status(rqmnt, status)
        
    #******************************************************************
    
    print("===========================================================")
    print("2. Contact 1 and 2 Directives")
    print("===========================================================")
      
    ## Verify contact directives are accepted and executed

    for cont in [1, 2]:
        
        print("-----------------------------------------------------------")
        print(f"2.{cont} CONTACT {cont}")
        print("-----------------------------------------------------------")
        
        print(".....................................")
        print("CONTACT_SETUP")
        print(".....................................")
            
        status = TestUtils.send_command(f"{setup_cont} with CONTACT_ID {cont}")
        for rqmnt in [
            "DTN.6.12290", "DTN.6.15001", 
            "DTN.6.15281", "DTN.6.19360", "DTN.6.19390"
            ]:
            TestUtils.set_requirement_status(rqmnt, status)
       
        if tlm(f"{target} {chan_stat_pkt} CON_STAT_RUN_STATE_{cont}") == 'SETUP':
            status = "P"
        else:
            print(f"ERROR - CON_STAT_RUN_STATE_{cont} not SETUP")
            status = "F"        
        
        for rqmnt in ["DTN.6.19210"]:
            TestUtils.set_requirement_status(rqmnt, status)

        print(".....................................")
        print("CONTACT_START")
        print(".....................................")
        
        status = TestUtils.send_command(f"{start_cont} with CONTACT_ID {cont}")
        for rqmnt in ["DTN.6.12362"]:
            TestUtils.set_requirement_status(rqmnt, status)
            
        if tlm(f"{target} {chan_stat_pkt} CON_STAT_RUN_STATE_{cont}") == 'STARTED':
            status = "P"
        else:
            print(f"ERROR - CON_STAT_RUN_STATE_{cont} not STARTED")
            status = "F"        
        
        for rqmnt in ["DTN.6.19210"]:
            TestUtils.set_requirement_status(rqmnt, status)

        print(".....................................")
        print("CONTACT_STOP")
        print(".....................................")

        status = TestUtils.send_command(f"{stop_cont} with CONTACT_ID {cont}")    
        for rqmnt in ["DTN.6.19210", "DTN.6.12372"]:
            TestUtils.set_requirement_status(rqmnt, status)
        
        if tlm(f"{target} {chan_stat_pkt} CON_STAT_RUN_STATE_{cont}") == 'STOPPED':
            status = "P"
        else:
            print(f"ERROR - CON_STAT_RUN_STATE_{cont} not STOPPD")
            status = "F"        
        
        for rqmnt in ["DTN.6.19210"]:
            TestUtils.set_requirement_status(rqmnt, status)

        print(".....................................")
        print("CONTACT_TEARDOWN")
        print(".....................................")
     
        status = TestUtils.send_command(f"{teardown_cont} with CONTACT_ID {cont}")
          
        if tlm(f"{target} {chan_stat_pkt} CON_STAT_RUN_STATE_{cont}") == 'TORNDOWN':
            status = "P"
        else:
            print(f"ERROR - CON_STAT_RUN_STATE_{cont} not TORNDOWN")
            status = "F"        
        
        for rqmnt in ["DTN.6.19210"]:
            TestUtils.set_requirement_status(rqmnt, status)
        
    #******************************************************************
      
    print("===========================================================")
    print("3. Simultaneous contacts")
    print("===========================================================")
    
    print("..........")
    print("SETUP")
    print("..........")
    for cont in range (3):
        if TestUtils.send_command(f"{setup_cont} with CONTACT_ID {cont}") == "F":
            print(f"ERROR - could not set up contact {cont}")
        
    print("..........")
    print("START")
    print("..........")
    for cont in range (3):
        if TestUtils.send_command(f"{start_cont} with CONTACT_ID {cont}") == "F":
            print(f"ERROR - could not start contact {cont}")

    print("..........")
    print("STOP")
    print("..........")
    for cont in range (3):
        if TestUtils.send_command(f"{stop_cont} with CONTACT_ID {cont}") == "F":
            print(f"ERROR - could not stop contact {cont}")

    print("..........")
    print("TEARDOWN")
    print("..........")
    for cont in range (3):
        if TestUtils.send_command(f"{teardown_cont} with CONTACT_ID {cont}") == "F":
            print(f"ERROR - could not teardown contact {cont}")

 
    print("-----------------------------------------------------------")
    print("3.1 Bundles receipt from simultaneous contacts - 0 and 2")
    print("-----------------------------------------------------------")
    
    # Contact 1 is for SB CLA OUT - not applicable for bundle receipt
     
    received_cnt = tlm (f"{target} {mib_counts_pkt} BUNDLE_COUNT_RECEIVED")
    stored_cnt = tlm (f"{target} {mib_reports_pkt} BUNDLE_COUNT_STORED")

    ## Enable contacts 0 and 2
    for cont in [0,2]:
        cmd(f"{target} {setup_cont} with CONTACT_ID {cont}")
        cmd(f"{target} {start_cont} with CONTACT_ID {cont}")
        
    print(".............................")
    print("Send bundles to both contacts")
    print(".............................")

    num_bundles_0 = 10
    num_bundles_2 = 15
    payload = b'\xAA'*1000
    DTNGenUtils.generate_bundles(dest_node_0, dest_service_0, num_bundles_0, payload)
    DTNGenUtils.generate_bundles(dest_node_2, dest_service_2, num_bundles_2, payload)

    print("Sending bundles to contact 0 port ...")
    DTNGenUtils.send_bundles(num_bundles_0, dest_node_0, data_sender_0)
    print(f" ... sent {num_bundles_0} dest_node_0 bundles")

    print("Sending bundles to contact 2 port ...")
    DTNGenUtils.send_bundles(num_bundles_2, dest_node_2, data_sender_2)
    print(f" ... sent {num_bundles_2} dest_node_2 bundles")

    print("........................................................")
    print("Verify bundles for both contacts are received and stored")
    print("........................................................")

    status = "P"
    
    item_name = "BUNDLE_COUNT_RECEIVED"
    exp_val = received_cnt+num_bundles_0+num_bundles_2
    if TestUtils.verify_item(mib_counts_pkt, item_name, exp_val) == "F":
        status = "F"

    item_name = "BUNDLE_COUNT_STORED"
    exp_val = stored_cnt+num_bundles_0+num_bundles_2
    if TestUtils.verify_item(mib_reports_pkt, item_name, exp_val) == "F":
        status = "F"
    
    for rqmnt in ["DTN.6.15155"]:
        TestUtils.set_requirement_status(rqmnt, status)
    
    # Teardown both contacts
    for cont in [0,2]:
        cmd(f"{target} {stop_cont} with CONTACT_ID {cont}")
        cmd(f"{target} {teardown_cont} with CONTACT_ID {cont}")

    #******************************************************************
    
    print("===========================================================")
    print("4. Ingress Rate")
    print("===========================================================")
    
    ## Load contact table with ingress rate 1000 bits per cycle (10Hz)
    load_new_table('/cf/cont_irate_lim.tbl')

    ## Start contact
    cmd(f"{target} {setup_cont} with CONTACT_ID 0")
    wait(1)
    cmd(f"{target} {start_cont} with CONTACT_ID 0")
    wait(1)
    
    ## Send bundles
    num_bundles = 1
    payload = b'\xAA'*1000
    DTNGenUtils.generate_bundles(dest_node_0, dest_service_0, num_bundles, payload)

    received_cnt = tlm (f"{target} {mib_counts_pkt} BUNDLE_COUNT_RECEIVED")
    num_loops=50
    print(f"Sending {num_loops*num_bundles} bundles to DTN Node ...")
    with disable_instrumentation():
        for _ in range(num_loops):
            DTNGenUtils.send_bundles(1, dest_node_0, data_sender_0)
    
    ## Verify bundles are received at low rate - expected ~45 sec
    elapsed = wait_check(f"{target} {mib_counts_pkt} BUNDLE_COUNT_RECEIVED == {received_cnt+num_bundles*num_loops}", 60)
    if elapsed > 40 and elapsed < 50:
        print("!!! Bundle ingress rate low as expected")
        status = "P"
    else:
        print("!!! ERROR - Bundle ingress rate not low as expected")
        status = "F"
    
    for rqmnt in ["DTN.6.15013", "DTN.6.15073"]:
        TestUtils.set_requirement_status(rqmnt, status)
        
    #TBD - 15014 exceed the rate limit, the CLA shall send a warning event DTNN-1369
    #TBD - 19260 translate all Event Management event messages event types to host event types 

    ## Stop and teardown contact
    cmd(f"{target} {stop_cont} with CONTACT_ID 0")
    wait(1)
    cmd(f"{target} {teardown_cont} with CONTACT_ID 0")
    wait(1)
    
    #******************************************************************
 
    print("===========================================================")
    print("5. Reset Counters Directives")
    print("===========================================================")
    
    print("-----------------------------------------------------------")
    print("5.1 RESET_COUNTER")
    print("-----------------------------------------------------------")

    TestUtils.reset_counter("BUNDLE_COUNT_RECEIVED")
    status = "P"
    for rqmnt in ["DTN.6.12062"]:
        TestUtils.set_requirement_status(rqmnt, status)
    
    print("-----------------------------------------------------------")
    print("5.2 RESET_ALL_COUNTERS")
    print("-----------------------------------------------------------") 
    
    TestUtils.reset_counters("ALL")

    #******************************************************************
    ## Print MIB Reports packet
    TestUtils.print_mib_reports_pkt()
    
    ## Print Storage packet
    TestUtils.print_storage_pkt()
    
    ## Disconnect data senders
    data_sender_0.disconnect()
    data_sender_2.disconnect()

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
    
# main
#bundle_ingress_nominal("xxx")
#set_line_delay(0)

