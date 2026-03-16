###################################################################
## Test utility functions
###################################################################

class TestUtils:
    
    ##=================================================================
    ##  set_requirement_status
    ##=================================================================
    @classmethod
    def set_requirement_status(cls, rqmnt, status):
        '''
        Sets requirement status
        - rqmnt_status dictionary is defined/initialized in main
        
        status: "U"/"P"/"F"/"A"
        '''
        
        global rqmnt_status
        
        print ("!!! Setting requirement " + rqmnt + " to " + status)
        if rqmnt_status[rqmnt] != "F": rqmnt_status[rqmnt] = status
    

    ##=================================================================
    ##  send_command
    ##=================================================================
    # Command types
    VALID_CMD_TYPE   = 1
    INVALID_CMD_TYPE = 0

    @classmethod
    def send_command(cls, command, cmd_type=None):    
        '''
        Sends BPNODE command, returns P/F
        Sets status of DTN.6.19090 and DTN.6.19180 (or DTN.6.19160 for invalid commands)
        
        cmd_type: VALID_CMD_TYPE/INVALID_CMD_TYPE
        '''
        
        if cmd_type == None: cmd_type = cls.VALID_CMD_TYPE
        
        if cmd_type == cls.VALID_CMD_TYPE:
            cmd_cnt= tlm (f"<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_AGENT_ACCEPTED_DIRECTIVE_COUNT")
            
            print ("!!! Sending command " + command + "...")
            cmd (f"<%= target_name %> {command}")
            
            wait (f"<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_AGENT_ACCEPTED_DIRECTIVE_COUNT == {cmd_cnt}+1", 6)
        
            if tlm(f"<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_AGENT_ACCEPTED_DIRECTIVE_COUNT") == cmd_cnt+1:
                print ("!!! Command accepted")
                status = "P"
            else:
                print ("!!! ERROR - Command not accepted")
                status = "F"
            
            for rqmnt in ["DTN.6.19090", "DTN.6.19180"]:
                cls.set_requirement_status(rqmnt, status)
        
        else:
            cmd_cnt= tlm (f"<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_AGENT_REJECTED_DIRECTIVE_COUNT")
            
            print ("!!! Sending command " + command + "...")
            cmd_no_range_check (f"<%= target_name %> {command}")
            
            wait (f"<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_AGENT_REJECTED_DIRECTIVE_COUNT == {cmd_cnt}+1", 6)
            if tlm(f"<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_AGENT_REJECTED_DIRECTIVE_COUNT") == cmd_cnt+1:
                print ("!!! Invalid Command rejected as expected")
                status = "P"
            else:
                print ("!!! ERROR - Invalid Command not rejected")
                status = "F"
            
            for rqmnt in ["DTN.6.19090", "DTN.6.19160"]:
                cls.set_requirement_status(rqmnt, status)
        
        return status


    ##=================================================================
    ##  verify_event
    ##=================================================================
    @classmethod
    def verify_event(cls, app_name, evt_id, evt_type, directive=True):
        '''
        Verifies last EVS Event Message received matches expected
        
        directive   None/True  For directives sets status of DTN.6.19170 for error  
                               and DTN.6.19190 for other events 
        '''
        
        app   = tlm(f"<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_APP_NAME")
        eid   = tlm(f"<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_EVENT_ID")
        etype = tlm(f"<%= target_name %> CFE_EVS_LONG_EVENT_MSG PACKET_ID_EVENT_TYPE")
        emsg  = tlm(f"<%= target_name %> CFE_EVS_LONG_EVENT_MSG MESSAGE")
        
        # Print received event message
        print ("!!! Event: " + app + " " + str(eid) + " " + etype + " " + emsg) 
            
        if app == app_name and eid == evt_id and etype == evt_type:
            print ("!!! Expected Event received")
            status = "P"
        else:
            print ("!!! ERROR - Expected Event not received")
            status = "F"
        
        if directive:
            if evt_type == "ERROR":
                rqmnt = "DTN.6.19170"
            else:
                rqmnt = "DTN.6.19190"
                
            cls.set_requirement_status(rqmnt, status)

        return status


    ##=================================================================
    ##  verify_item
    ##=================================================================
    @classmethod
    def verify_item(cls, packet_name, item_name, exp_val):
        '''
        Checks value of telemetry <item_name> against <exp_val>, prints a message 
        if not the same, and returns P/F status
        '''
        
        wait_packet(target, packet_name, 1, 6)
        
        item_val = tlm(f"<%= target_name %> {packet_name} {item_name}")
        
        if  item_val == exp_val:
            print (f"!!! {item_name}: {item_val} as expected")
            return "P"
        else:
            print (f"!!! ERROR - {item_name}: {item_val}, Expected: {exp_val}")
            return "F"
    

    ##=================================================================
    ##  update_table
    ##=================================================================
    @classmethod
    def update_table(cls, definition_file, binary_file, values_list, output_file, efs_option=False):
        '''
        Updates table binary_file with [name, value] pairs in values_list and
        creates output_file
        
        https://docs.openc3.com/docs/guides/scripting-api#table_create_binary
        
        Example usage:
            TestUtils.update_table("bpnode_contacts_def.txt",
                                   "bpnode_contacts.tbl",
                                   [
                                      ["CONTACT_0_PORT",4551], 
                                      ["CONTACT_0_CL_ADDR","10.2.11.75"],
                                   ],
                                   "test_contacts.tbl"
                                   )
        '''
        from openc3.tools.table_manager.table_config import TableConfig
        
        def_dir = f"<%= target_name %>/tables/config"
        bin_dir = f"<%= target_name %>/tables/bin"
        
        # Get the definition file 
        def_file = get_target_file(f"{def_dir}/{definition_file}")

        # Get the table name in COSMOS from definition file 
        table_name_cosmos = str(def_file.read()).split(' ')[1]

        # Access the internal TableConfig to process the definition
        config = TableConfig.process_file(def_file.name)

        # Grab the table by the table name in COSMOS
        table = config.table(table_name_cosmos)


        # Get the binary file contents
        bin_file = get_target_file(f"{bin_dir}/{binary_file}")
        table_bin = bin_file.read()


        # Copy binary file contents to table buffer for update
        table.buffer = table_bin

        # Update individual items in the table
        for item in values_list:
            table.write(item[0], item[1])
        
        # Finally write table buffer (the binary) back to storage
        put_target_file(f"{bin_dir}/{output_file}", table.buffer)


        # Write table buffer to file in efs
        if efs_option:
            print(f"Creating {output_file} in /efs/ ...")
            with open(f"/efs/{output_file}", "wb") as file:
                file.write(table.buffer)
                file.close()
            

    ##=================================================================
    ##  validate_invalid_table
    ##=================================================================
    @classmethod
    def validate_invalid_table(cls, table_filepath):
        '''
        Load and try to validate an invalid table
        
        table_filepath:  /cf/<table_filename>
        '''
       
        # Load table
        cmd_count = tlm(f"<%= target_name %> CFE_TBL_HK COMMAND_COUNTER")    

        cmd(f"<%= target_name %> CFE_TBL_CMD_LOAD with LOAD_FILENAME '{table_filepath}'")
        wait_check(f"<%= target_name %> CFE_TBL_HK COMMAND_COUNTER == {cmd_count+1}", 10)


        # Validate table - expect validation to fail
        table_name = tlm(f"<%= target_name %> CFE_TBL_HK LAST_TABLE_LOADED")
        active_table_flag = 0 # 0 for active buffer, 1 for inactive buffer

        cmd_count = tlm(f"<%= target_name %> CFE_TBL_HK FAILED_VAL_COUNTER")

        cmd(f"<%= target_name %> CFE_TBL_CMD_VALIDATE with TABLE_NAME '{table_name}', ACTIVE_TABLE_FLAG {active_table_flag}")
        if wait(f"<%= target_name %> CFE_TBL_HK FAILED_VAL_COUNTER == {cmd_count+1}", 10):
            print("!!! Table validation failed as expected")
            status = "P"
        else:
            print("!!! ERROR - Table validation did not fail as expected")
            status = "F"

        for rqmnt in ["DTN.6.19360", "DTN.6.19390"]:
            cls.set_requirement_status(rqmnt, status)
            
        return status
        

    ##=================================================================
    ##  print_mib_counts_pkt
    ##=================================================================
    @classmethod
    def print_mib_counts_pkt(cls):
        pkt = "BPNODE_NODE_MIB_COUNTERS_HK"
        
        print("**************************************************************")
        print("************** BPNode Node MIB Counters HK *******************")
        print("**************************************************************")
        print("***  ADU_COUNT_DELIVERED                    :  ", tlm(f'<%= target_name %> {pkt} ADU_COUNT_DELIVERED                    '))
        print("***  ADU_COUNT_RECEIVED                     :  ", tlm(f'<%= target_name %> {pkt} ADU_COUNT_RECEIVED                     '))
        print("***  BUNDLE_AGENT_ACCEPTED_DIRECTIVE_COUNT  :  ", tlm(f'<%= target_name %> {pkt} BUNDLE_AGENT_ACCEPTED_DIRECTIVE_COUNT  '))
        print("***  BUNDLE_AGENT_REJECTED_DIRECTIVE_COUNT  :  ", tlm(f'<%= target_name %> {pkt} BUNDLE_AGENT_REJECTED_DIRECTIVE_COUNT  '))
        print("***  BUNDLE_COUNT_ABANDONED                 :  ", tlm(f'<%= target_name %> {pkt} BUNDLE_COUNT_ABANDONED                 '))
        print("***  BUNDLE_COUNT_ACCEPTED_CUSTODY          :  ", tlm(f'<%= target_name %> {pkt} BUNDLE_COUNT_ACCEPTED_CUSTODY          '))
        print("***  BUNDLE_COUNT_CCS_RECEIVED              :  ", tlm(f'<%= target_name %> {pkt} BUNDLE_COUNT_CCS_RECEIVED              ')) 
        print("***  BUNDLE_COUNT_CUSTODY_REJECTED          :  ", tlm(f'<%= target_name %> {pkt} BUNDLE_COUNT_CUSTODY_REJECTED          '))
        print("***  BUNDLE_COUNT_CUSTODY_REQUEST           :  ", tlm(f'<%= target_name %> {pkt} BUNDLE_COUNT_CUSTODY_REQUEST           '))
        print("***  BUNDLE_COUNT_CUSTODY_RE_FORWARDED      :  ", tlm(f'<%= target_name %> {pkt} BUNDLE_COUNT_CUSTODY_RE_FORWARDED      '))
        print("***  BUNDLE_COUNT_CUSTODY_TRANSFERRED       :  ", tlm(f'<%= target_name %> {pkt} BUNDLE_COUNT_CUSTODY_TRANSFERRED       '))
        print("***  BUNDLE_COUNT_DELETED                   :  ", tlm(f'<%= target_name %> {pkt} BUNDLE_COUNT_DELETED                   '))
        print("***  BUNDLE_COUNT_DELETED_EXPIRED           :  ", tlm(f'<%= target_name %> {pkt} BUNDLE_COUNT_DELETED_EXPIRED           '))
        print("***  BUNDLE_COUNT_DELETED_HOP_EXCEEDED      :  ", tlm(f'<%= target_name %> {pkt} BUNDLE_COUNT_DELETED_HOP_EXCEEDED      '))
        print("***  BUNDLE_COUNT_DELETED_NO_STORAGE        :  ", tlm(f'<%= target_name %> {pkt} BUNDLE_COUNT_DELETED_NO_STORAGE        '))
        print("***  BUNDLE_COUNT_DELETED_TOO_LONG          :  ", tlm(f'<%= target_name %> {pkt} BUNDLE_COUNT_DELETED_TOO_LONG          '))
        print("***  BUNDLE_COUNT_DELETED_TRAFFIC_PARED     :  ", tlm(f'<%= target_name %> {pkt} BUNDLE_COUNT_DELETED_TRAFFIC_PARED     '))
        print("***  BUNDLE_COUNT_DELETED_UNAUTHORIZED      :  ", tlm(f'<%= target_name %> {pkt} BUNDLE_COUNT_DELETED_UNAUTHORIZED      '))
        print("***  BUNDLE_COUNT_DELETED_UNINTELLIGIBLE    :  ", tlm(f'<%= target_name %> {pkt} BUNDLE_COUNT_DELETED_UNINTELLIGIBLE    '))
        print("***  BUNDLE_COUNT_DELETED_UNSUPPORTED_BLOCK :  ", tlm(f'<%= target_name %> {pkt} BUNDLE_COUNT_DELETED_UNSUPPORTED_BLOCK '))
        print("***  BUNDLE_COUNT_DELIVERED                 :  ", tlm(f'<%= target_name %> {pkt} BUNDLE_COUNT_DELIVERED                 '))
        print("***  BUNDLE_COUNT_DEPLETED                  :  ", tlm(f'<%= target_name %> {pkt} BUNDLE_COUNT_DEPLETED                  '))
        print("***  BUNDLE_COUNT_DISCARDED                 :  ", tlm(f'<%= target_name %> {pkt} BUNDLE_COUNT_DISCARDED                 '))
        print("***  BUNDLE_COUNT_FORWARDED                 :  ", tlm(f'<%= target_name %> {pkt} BUNDLE_COUNT_FORWARDED                 '))
        print("***  BUNDLE_COUNT_FORWARDED_FAILED          :  ", tlm(f'<%= target_name %> {pkt} BUNDLE_COUNT_FORWARDED_FAILED          '))
        print("***  BUNDLE_COUNT_GENERATED_ACCEPTED        :  ", tlm(f'<%= target_name %> {pkt} BUNDLE_COUNT_GENERATED_ACCEPTED        '))
        print("***  BUNDLE_COUNT_GENERATED_REJECTED        :  ", tlm(f'<%= target_name %> {pkt} BUNDLE_COUNT_GENERATED_REJECTED        '))
        print("***  BUNDLE_COUNT_GENERATED_CUSTODY_SIGNAL  :  ", tlm(f'<%= target_name %> {pkt} BUNDLE_COUNT_GENERATED_CUSTODY_SIGNAL  '))    
        print("***  BUNDLE_COUNT_GENERATED_REJECTED        :  ", tlm(f'<%= target_name %> {pkt} BUNDLE_COUNT_GENERATED_REJECTED        '))
        print("***  BUNDLE_COUNT_MAX_BSR_RATE_EXCEEDED     :  ", tlm(f'<%= target_name %> {pkt} BUNDLE_COUNT_MAX_BSR_RATE_EXCEEDED     '))
        print("***  BUNDLE_COUNT_NO_CONTACT                :  ", tlm(f'<%= target_name %> {pkt} BUNDLE_COUNT_NO_CONTACT                '))
        print("***  BUNDLE_COUNT_NO_ROUTE                  :  ", tlm(f'<%= target_name %> {pkt} BUNDLE_COUNT_NO_ROUTE                  '))
        print("***  BUNDLE_COUNT_REASSEMBLED               :  ", tlm(f'<%= target_name %> {pkt} BUNDLE_COUNT_REASSEMBLED               '))
        print("***  BUNDLE_COUNT_RECEIVED                  :  ", tlm(f'<%= target_name %> {pkt} BUNDLE_COUNT_RECEIVED                  '))
        print("***  BUNDLE_COUNT_RECEIVED_ADMIN_RECORD     :  ", tlm(f'<%= target_name %> {pkt} BUNDLE_COUNT_RECEIVED_ADMIN_RECORD     '))
        print("***  BUNDLE_COUNT_RECEIVED_CUSTODY_SIGNAL   :  ", tlm(f'<%= target_name %> {pkt} BUNDLE_COUNT_RECEIVED_CUSTODY_SIGNAL   '))
        print("***  BUNDLE_COUNT_REDUNDANT                 :  ", tlm(f'<%= target_name %> {pkt} BUNDLE_COUNT_REDUNDANT                 '))
        print("***  BUNDLE_COUNT_REJECTED_CUSTODY          :  ", tlm(f'<%= target_name %> {pkt} BUNDLE_COUNT_REJECTED_CUSTODY          '))
        print("***  BUNDLE_COUNT_UNINTELLIGIBLE_BLOCK      :  ", tlm(f'<%= target_name %> {pkt} BUNDLE_COUNT_UNINTELLIGIBLE_BLOCK      '))
        print("***  BUNDLE_COUNT_UNINTELLIGIBLE_EID        :  ", tlm(f'<%= target_name %> {pkt} BUNDLE_COUNT_UNINTELLIGIBLE_EID        '))
        print("***  BUNDLE_COUNT_UNPROCESSED_BLOCKS        :  ", tlm(f'<%= target_name %> {pkt} BUNDLE_COUNT_UNPROCESSED_BLOCKS        '))
        print("**************************************************************")
        

    ##=================================================================
    ##  print_mib_reports_pkt
    ##=================================================================
    @classmethod
    def print_mib_reports_pkt(cls):
        pkt = "BPNODE_NODE_MIB_REPORTS_HK"
        
        print("**************************************************************")
        print("*************** BPNode Node MIB Reports HK *******************")
        print("**************************************************************")
        print("***  BUNDLE_COUNT_STORED             :  ", tlm(f'<%= target_name %> {pkt} BUNDLE_COUNT_STORED            '))
        print("***  BUNDLE_COUNT_IN_CUSTODY         :  ", tlm(f'<%= target_name %> {pkt} BUNDLE_COUNT_IN_CUSTODY        '))
        print("***  BUNDLE_AGENT_AVAILABLE_STORAGE  :  ", tlm(f'<%= target_name %> {pkt} BUNDLE_AGENT_AVAILABLE_STORAGE '))
        print("***  KBYTES_COUNT_STORAGE_AVAILABLE  :  ", tlm(f'<%= target_name %> {pkt} KBYTES_COUNT_STORAGE_AVAILABLE '))
        print("***  NODE_STARTUP_COUNTER            :  ", tlm(f'<%= target_name %> {pkt} NODE_STARTUP_COUNTER           '))
        print("**************************************************************")


    ##=================================================================
    ##  print_storage_pkt
    ##=================================================================
    @classmethod
    def print_storage_pkt(cls):
        pkt = "BPNODE_STORAGE_HK"
        
        print("**************************************************************")
        print("******************* BPNode Storage HK ************************")
        print("**************************************************************")
        print("***  KB_STORAGE_IN_USE  :  ", tlm(f'<%= target_name %> {pkt} KB_STORAGE_IN_USE '))
        print("***  KB_BUNDLES_IN_STOR :  ", tlm(f'<%= target_name %> {pkt} KB_BUNDLES_IN_STOR '))
        print("***  BYTES_MEM_IN_USE   :  ", tlm(f'<%= target_name %> {pkt} BYTES_MEM_IN_USE '))
        print("***  BYTES_MEM_FREE     :  ", tlm(f'<%= target_name %> {pkt} BYTES_MEM_FREE '))
        print("**************************************************************")
        

    ##=================================================================
    ##  reset_counters
    ##=================================================================
    @classmethod
    def reset_counters(cls, option):
        '''
        option  - "ALL", "ERROR" or "BUNDLE"
        
        Send RESET ALL/ERROR/BUNDLE COUNTERS command
        - Verify command acceptance and info event
        - Verify expected counts are reset
        - Set requirements status
        '''
        
        option = option.upper()
        
        pkt = "BPNODE_NODE_MIB_COUNTERS_HK"
        
        print("Counts before reset:")    
        cls.print_mib_counts_pkt()
        
        ## Verify command acceptance and info event
        RESET_ALL_CNT_EID    = 520
        RESET_BUNDLE_CNT_EID = 521
        RESET_ERROR_CNT_EID  = 523
        
        list1 = [
            "BUNDLE_COUNT_ABANDONED",
            "BUNDLE_COUNT_CUSTODY_REJECTED",
            "BUNDLE_COUNT_GENERATED_REJECTED",
            "BUNDLE_COUNT_DELETED_UNINTELLIGIBLE",
            "BUNDLE_COUNT_DELETED_UNSUPPORTED_BLOCK",
            "BUNDLE_COUNT_DELETED_NO_STORAGE",
            "BUNDLE_COUNT_DELETED_UNAUTHORIZED",
            "BUNDLE_COUNT_DELETED_TOO_LONG",
            "BUNDLE_COUNT_REJECTED_CUSTODY",
            "BUNDLE_COUNT_UNPROCESSED_BLOCKS",
        ]
        
        list2 = ["BUNDLE_AGENT_REJECTED_DIRECTIVE_COUNT"]
        
        list3 = [
            "ADU_COUNT_RECEIVED",
            "ADU_COUNT_DELIVERED",
            "BUNDLE_COUNT_ACCEPTED_CUSTODY",
            "BUNDLE_COUNT_CCS_RECEIVED",
            "BUNDLE_COUNT_CUSTODY_REJECTED",
            "BUNDLE_COUNT_CUSTODY_REQUEST",
            "BUNDLE_COUNT_CUSTODY_RE_FORWARDED",
            "BUNDLE_COUNT_CUSTODY_TRANSFERRED",
            "BUNDLE_COUNT_DELETED",
            "BUNDLE_COUNT_DELETED_EXPIRED",
            "BUNDLE_COUNT_DELETED_HOP_EXCEEDED",
            "BUNDLE_COUNT_DELETED_TRAFFIC_PARED",
            "BUNDLE_COUNT_DELIVERED",
            "BUNDLE_COUNT_DEPLETED",
            "BUNDLE_COUNT_DISCARDED",
            "BUNDLE_COUNT_FORWARDED",
            "BUNDLE_COUNT_FORWARDED_FAILED",
            "BUNDLE_COUNT_GENERATED_ACCEPTED",
            "BUNDLE_COUNT_GENERATED_CCS",
            "BUNDLE_COUNT_GENERATED_CUSTODY_SIGNAL",
            "BUNDLE_COUNT_RECEIVED",
            "BUNDLE_COUNT_RECEIVED_ADMIN_RECORD",
            "BUNDLE_COUNT_RECEIVED_CUSTODY_SIGNAL",
            "BUNDLE_COUNT_REDUNDANT",
            "BUNDLE_COUNT_REJECTED_CUSTODY",
        ]
                
        all_list = list1+list2+list3
        error_list = list1+list2
        bundle_list = list3
        
        status = "P"
        
        rqmnt_list = ["DTN.6.20010"]
        
        if option == "ERROR":
            cls.send_command("BPNODE_CMD_RESET_ERROR_COUNTERS")
            cls.verify_event("BPNODE", RESET_ERROR_CNT_EID, "INFO")
            
            counters_list = error_list
            rqmnt_list += ["DTN.6.20090"]
           
        elif option == "BUNDLE":
            ## Save non-bundle counts for verification later
            accept_dir_cnt = tlm(f"<%= target_name %> {pkt} BUNDLE_AGENT_ACCEPTED_DIRECTIVE_COUNT")
            reject_dir_cnt = tlm(f"<%= target_name %> {pkt} BUNDLE_AGENT_REJECTED_DIRECTIVE_COUNT")
            
            cls.send_command("BPNODE_CMD_RESET_BUNDLE_COUNTERS")
            cls.verify_event("BPNODE", RESET_BUNDLE_CNT_EID, "INFO")
            
            counters_list = bundle_list
            rqmnt_list += ["DTN.6.20080"]
            
        elif option == "ALL":
            print("!!! Sending BPNODE_CMD_RESET_ALL_COUNTERS command")
            cmd("<%= target_name %> BPNODE_CMD_RESET_ALL_COUNTERS")
            wait_packet("<%= target_name %>", pkt, 2, 10)
            
            if tlm(f"<%= target_name %> {pkt} BUNDLE_AGENT_ACCEPTED_DIRECTIVE_COUNT") == 0:
                print ("!!! Command accepted")
                status = "P"
            else:
                print ("!!! ERROR - Command not accepted")
                status = "F"
            
            for rqmnt in ["DTN.6.19090"]:
                cls.set_requirement_status(rqmnt, status)
                
            cls.verify_event("BPNODE", RESET_ALL_CNT_EID, "INFO")
            
            counters_list = all_list
            rqmnt_list += ["DTN.6.12150"]

        else:
            print("ERROR - option not ALL/BUNDLE/ERROR")
            wait
            
        print("Counts after reset:")    
        cls.print_mib_counts_pkt()
    
        ## Verify expected counts are reset
        for item in counters_list:
            if tlm(f"<%= target_name %> {pkt} {item}") != 0:
                print("!!! ERROR - One or more counts did not reset")
                status = "F"
                break
                
        ## Verify other counts are not reset TBD


        ## Set requirement status
        for rqmnt in rqmnt_list:
            cls.set_requirement_status(rqmnt, status)
                
        return status


    ##=================================================================
    ##  reset_counter
    ##=================================================================
    @classmethod
    def reset_counter(cls, counter):
        
        pkt = "BPNODE_NODE_MIB_COUNTERS_HK"
        
        print(counter, " - before reset: ",  tlm(f"<%= target_name %> {pkt} {counter}"))
        
        #cmd(f"<%= target_name %> BPNODE_CMD_RESET_COUNTER with MIB_ARRAY_INDEX NODE_COUNTER_INDICATOR, COUNTER {counter}")
        cmd(f"<%= target_name %> BPNODE_CMD_RESET_COUNTER with COUNTER {counter}")
        
        status = "P" if wait(f"<%= target_name %> {pkt} {counter} == 0", 10) else "F"

        for rqmnt in ["DTN.6.12120", "DTN.6.20010"]:
            cls.set_requirement_status(rqmnt, status)



    ##=================================================================
    ##  find_event_in_log
    ##=================================================================
    @classmethod
    def find_event_in_log(cls, app_name, evt_id, evt_type, last_event_time_str):        
        '''
        Example: 
            status = TestUtils.find_event_in_log("BPNODE", 541, "ERROR", "2025-08-26 11:46:45")
            
            returns True if event found in log, else False
        '''
        
        last_event_time = datetime.strptime(last_event_time_str, '%Y-%m-%d %H:%M:%S')
        
        filename = stash_get('eventlog')
        f = open(filename, 'r')
        
        for line in f:
            words = (line.strip().split(' '))
            #print (words)
            event_time_str = (words[0] + ' ' + words[1])
            event_time = datetime.strptime(event_time_str, '%Y-%m-%d %H:%M:%S')
            #print (event_time)
            if event_time <= last_event_time: 
                continue
            else:
                if words[2] == app_name and int(words[3]) == evt_id and words[4] == evt_type:
                    print(line.strip())
                    f.close()
                    return True

        f.close()
        return False

###################################################################
