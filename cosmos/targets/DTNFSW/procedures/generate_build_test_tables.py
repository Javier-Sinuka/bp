#######################################################################
# generate_build_test_tables
#
# Script(s) may need to be edited for different instances
#######################################################################

def generate_build_test_tables(table):
    
    load_utility('DTNFSW-1/procedures/build_tests/test_utils.py')

    prompt("Script(s) may need to be edited for different instances")
    
    set_line_delay(0)

    table = table.upper()
    
    if table == 'CONTACT' or table == 'ALL':
        generate_contact_tables()

    if table == 'CHANNEL' or table == 'ALL':
        generate_channel_tables()

    if table == 'MIB' or table == 'ALL':
        generate_mib_tables()


def generate_contact_tables():
    print("Generating contact tables ...")

    # contact definition and default binary files
    def_file = "bpnode_contacts_def.txt"
    bin_file = "bpnode_contacts.tbl"

    ## Edit as needed for local/test cosmos instance
    CONT_0_REMOTE_ADDR="10.2.11.172" # local
    bin_dir=""

    #CONT_0_REMOTE_ADDR = "10.2.8.151" # test
    #bin_dir = "target_node/"


    ## contact_nominal.tbl
    out_file = bin_dir+"contact_nominal.tbl"
    values_list = [
           ["CONT_0_REMOTE_ADDR",CONT_0_REMOTE_ADDR],
        ]
    TestUtils.update_table(def_file, bin_file, values_list, out_file)


    ## contact_rx_only.tbl
    out_file = bin_dir+"contact_rx_only.tbl"
    values_list = [
           ["CONT_0_DEST_ID_PAT_0_MAXNODE",0], 
           ["CONT_0_DEST_ID_PAT_0_MINNODE",0], 
           ["CONT_0_DEST_ID_PAT_0_MAXSERVICE",0], 
           ["CONT_0_DEST_ID_PAT_0_MINSERVICE",0], 
        ]
    TestUtils.update_table(def_file, bin_file, values_list, out_file)


    ## cont_irate_lim.tbl
    out_file = bin_dir+"cont_irate_lim.tbl"
    values_list = [
           ["CONT_0_DEST_ID_PAT_0_MAXNODE",0], 
           ["CONT_0_DEST_ID_PAT_0_MINNODE",0], 
           ["CONT_0_DEST_ID_PAT_0_MAXSERVICE",0], 
           ["CONT_0_DEST_ID_PAT_0_MINSERVICE",0], 
           ["CONT_0_INGRESS_BITS_PER_CYCLE",1000],
        ]   
    TestUtils.update_table(def_file, bin_file, values_list, out_file)


    ## cont_erate_lim.tbl
    out_file = bin_dir+"cont_erate_lim.tbl"
    values_list = [
           ["CONT_0_REMOTE_ADDR",CONT_0_REMOTE_ADDR],
           ["CONT_0_EGRESS_BITS_PER_CYCLE",10000],
        ]
    TestUtils.update_table(def_file, bin_file, values_list, out_file)
    

    ## cont_bad_dst1.tbl
    out_file = bin_dir+"cont_bad_dst1.tbl"
    values_list = [
           ["CONT_0_DEST_ID_PAT_0_IPNSSPFORMAT",3],
        ]
    TestUtils.update_table(def_file, bin_file, values_list, out_file)
    

    ## cont_bad_dst2.tbl
    out_file = bin_dir+"cont_bad_dst2.tbl"
    values_list = [
           ["CONT_0_DEST_ID_PAT_0_IPNSSPFORMAT",1],
        ]
    TestUtils.update_table(def_file, bin_file, values_list, out_file)
    

    ## cont_bad_dst3.tbl
    out_file = bin_dir+"cont_bad_dst3.tbl"
    values_list = [
           ["CONT_0_DEST_ID_PAT_0_SCHEME",1],
        ]
    TestUtils.update_table(def_file, bin_file, values_list, out_file)
    

    ## cont_bad_dst4.tbl
    out_file = bin_dir+"cont_bad_dst4.tbl"
    values_list = [
           ["CONT_0_DEST_ID_PAT_0_SCHEME",3],
        ]
    TestUtils.update_table(def_file, bin_file, values_list, out_file)
    

    ## cont_bad_dst5.tbl
    out_file = bin_dir+"cont_bad_dst5.tbl"
    values_list = [
           ["CONT_0_DEST_ID_PAT_0_MAXNODE",100], 
           ["CONT_0_DEST_ID_PAT_0_MINNODE",200], 
        ]
    TestUtils.update_table(def_file, bin_file, values_list, out_file)
    

    ## cont_dup_dst.tbl
    out_file = bin_dir+"cont_dup_dst.tbl"
    values_list = [
           ["CONT_0_DEST_ID_PAT_1_MAXNODE",200], 
           ["CONT_0_DEST_ID_PAT_1_MINNODE",200], 
           ["CONT_0_DEST_ID_PAT_1_MAXSERVICE",64], 
           ["CONT_0_DEST_ID_PAT_1_MINSERVICE",64], 
        ]
    TestUtils.update_table(def_file, bin_file, values_list, out_file)
    

    ## cont_rx_lg_trg.tbl
    out_file = bin_dir+"cont_rx_lg_trg.tbl"
    values_list = [
           ["CONT_0_DEST_ID_PAT_0_MAXNODE",0], 
           ["CONT_0_DEST_ID_PAT_0_MINNODE",0], 
           ["CONT_0_DEST_ID_PAT_0_MAXSERVICE",0], 
           ["CONT_0_DEST_ID_PAT_0_MINSERVICE",0], 
           ["CONT_0_RETRANSMIT_TIMEOUT", 60000],
           ["CONT_0_CS_TIME_TRIGGER", 60000],
           ["CONT_0_CS_SIZE_TRIGGER", 85],
        ]
    TestUtils.update_table(def_file, bin_file, values_list, out_file)


    ## cont_rx_cstime_60.tbl
    out_file = bin_dir+"cont_rx_cstime_60.tbl"
    values_list = [
           ["CONT_0_DEST_ID_PAT_0_MAXNODE",0], 
           ["CONT_0_DEST_ID_PAT_0_MINNODE",0], 
           ["CONT_0_DEST_ID_PAT_0_MAXSERVICE",0], 
           ["CONT_0_DEST_ID_PAT_0_MINSERVICE",0], 
           ["CONT_0_RETRANSMIT_TIMEOUT", 600000],
           ["CONT_0_CS_TIME_TRIGGER", 60000],
           ["CONT_0_CS_SIZE_TRIGGER", 85],
        ]
    TestUtils.update_table(def_file, bin_file, values_list, out_file)


    ## cont_rx_cssize_min.tbl
    out_file = bin_dir+"cont_rx_cssize_min.tbl"
    values_list = [
           ["CONT_0_DEST_ID_PAT_0_MAXNODE",0], 
           ["CONT_0_DEST_ID_PAT_0_MINNODE",0], 
           ["CONT_0_DEST_ID_PAT_0_MAXSERVICE",0], 
           ["CONT_0_DEST_ID_PAT_0_MINSERVICE",0], 
           ["CONT_0_RETRANSMIT_TIMEOUT", 600000],
           ["CONT_0_CS_TIME_TRIGGER", 300000],
           ["CONT_0_CS_SIZE_TRIGGER", 63],
        ]
    TestUtils.update_table(def_file, bin_file, values_list, out_file)


    ## cont_timeout_min.tbl
    out_file = bin_dir+"cont_timeout_min.tbl"
    values_list = [
           ["CONT_0_RETRANSMIT_TIMEOUT", 0],
        ]
    TestUtils.update_table(def_file, bin_file, values_list, out_file)
    

    ## cont_timeout_max.tbl
    out_file = bin_dir+"cont_timeout_max.tbl"
    values_list = [
           ["CONT_0_RETRANSMIT_TIMEOUT", 60002],
        ]
    TestUtils.update_table(def_file, bin_file, values_list, out_file)


    ## cont_time_trg_min.tbl
    out_file = bin_dir+"cont_time_trg_min.tbl"
    values_list = [
           ["CONT_0_CS_TIME_TRIGGER", 0],
        ]
    TestUtils.update_table(def_file, bin_file, values_list, out_file)
    

    ## cont_time_trg_max.tbl
    out_file = bin_dir+"cont_time_trg_max.tbl"
    values_list = [
           ["CONT_0_RETRANSMIT_TIMEOUT", 100000],
           ["CONT_0_CS_TIME_TRIGGER", 100002],
        ]
    TestUtils.update_table(def_file, bin_file, values_list, out_file)


    ## cont_size_trg_min.tbl
    out_file = bin_dir+"cont_size_trg_min.tbl"
    values_list = [
           ["CONT_0_CS_SIZE_TRIGGER", 63],
        ]
    TestUtils.update_table(def_file, bin_file, values_list, out_file)

    ## cont_size_trg_max.tbl
    out_file = bin_dir+"cont_size_trg_max.tbl"
    values_list = [
           ["CONT_0_CS_SIZE_TRIGGER", 86],
        ]
    TestUtils.update_table(def_file, bin_file, values_list, out_file)


    '''
    CONT_0_DEST_ID_PAT_0_SCHEME	
    CONT_0_DEST_ID_PAT_0_IPNSSPFORMAT	
    CONT_0_DEST_ID_PAT_0_MAXALLOCATOR	
    CONT_0_DEST_ID_PAT_0_MINALLOCATOR	
    CONT_0_DEST_ID_PAT_0_MAXNODE	
    CONT_0_DEST_ID_PAT_0_MINNODE	
    CONT_0_DEST_ID_PAT_0_MAXSERVICE	
    CONT_0_DEST_ID_PAT_0_MINSERVICE	

    CONT_0_DEST_ID_PAT_1_SCHEME	
    CONT_0_DEST_ID_PAT_1_IPNSSPFORMAT	
    CONT_0_DEST_ID_PAT_1_MAXALLOCATOR	
    CONT_0_DEST_ID_PAT_1_MINALLOCATOR	
    CONT_0_DEST_ID_PAT_1_MAXNODE	
    CONT_0_DEST_ID_PAT_1_MINNODE	
    CONT_0_DEST_ID_PAT_1_MAXSERVICE	
    CONT_0_DEST_ID_PAT_1_MINSERVICE	

    CONT_0_DEST_ID_PAT_2_SCHEME	
    CONT_0_DEST_ID_PAT_2_IPNSSPFORMAT	
    CONT_0_DEST_ID_PAT_2_MAXALLOCATOR	
    CONT_0_DEST_ID_PAT_2_MINALLOCATOR	
    CONT_0_DEST_ID_PAT_2_MAXNODE	
    CONT_0_DEST_ID_PAT_2_MINNODE	
    CONT_0_DEST_ID_PAT_2_MAXSERVICE	
    CONT_0_DEST_ID_PAT_2_MINSERVICE	

    CONT_0_CLA_TYPE	
    CONT_0_LOCAL_ADDR	
    CONT_0_REMOTE_ADDR	
    CONT_0_LOCAL_PORT	
    CONT_0_REMOTE_PORT	
    CONT_0_DEST_LTP_ENG_ID	
    CONT_0_SEND_BYTES_PER_CYCLE	
    CONT_0_RECV_BYTES_PER_CYCLE	
    CONT_0_RETRANSMIT_TIMEOUT	
    CONT_0_CS_TIME_TRIGGER	
    CONT_0_CS_SIZE_TRIGGER
    CONT_0_INGRESS_BITS_PER_CYCLE 
    CONT_0_EGRESS_BITS_PER_CYCLE 
    '''


def generate_channel_tables():
    print("Generating channel_tables ...")

    # channel definition and default binary files
    def_file = "bpnode_channel_def.txt"
    bin_file = "bpnode_channel.tbl"

    ## chan_no_extblk.tbl
    out_file = "chan_no_extblk.tbl"
    values_list = [
           ["CHAN_IN_0_PREVNODEBLKCONFIG_INCLUDEBLOCK","FALSE"], 
           ["CHAN_IN_0_AGEBLKCONFIG_INCLUDEBLOCK","FALSE"], 
           ["CHAN_IN_0_HOPCOUNTBLKCONFIG_INCLUDEBLOCK","FALSE"], 
           ["CHAN_IN_0_CUSTODYTRANSFERBLKCONFIG_INCLUDEBLOCK","FALSE"], 
        ]
    TestUtils.update_table(def_file, bin_file, values_list, out_file)


    ## chan0_no_cteb.tbl
    out_file = "chan0_no_cteb.tbl"
    values_list = [
           ["CHAN_IN_0_CUSTODYTRANSFERBLKCONFIG_INCLUDEBLOCK","FALSE"], 
        ]
    TestUtils.update_table(def_file, bin_file, values_list, out_file)


    ## chan_bad_crc.tbl
    out_file = "chan_bad_crc.tbl"
    values_list = [
           ["CHAN_IN_0_CRC_TYPE",0], 
        ]
    TestUtils.update_table(def_file, bin_file, values_list, out_file)


    ## chan_dup_serv.tbl
    out_file = "chan_dup_serv.tbl"
    values_list = [
           ["CHAN_IN_1_LOCAL_SERVICE_NUMBER",42], 
        ]   
    TestUtils.update_table(def_file, bin_file, values_list, out_file)


    ## chan_bad_sspdst.tbl
    out_file = "chan_bad_sspdst.tbl"
    values_list = [
           ["CHAN_IN_0_DESTINATION_EID_ALLOCATOR",1],
        ]
    TestUtils.update_table(def_file, bin_file, values_list, out_file)


    ## chan_bad_ssprep.tbl
    out_file = "chan_bad_ssprep.tbl"
    values_list = [
           ["CHAN_IN_0_REPORT_TO_EID_IPNSSPFORMAT",3],
        ]
    TestUtils.update_table(def_file, bin_file, values_list, out_file)
    

    ## chan_prev_crc_0.tbl
    out_file = "chan_prev_crc_0.tbl"
    values_list = [
           ["CHAN_IN_0_PREVNODEBLKCONFIG_CRC_TYPE",0],
        ]
    TestUtils.update_table(def_file, bin_file, values_list, out_file)

    '''
    CHAN_0_ADD_AUTOMATICALLY                   
    CHAN_0_REQUEST_CUSTODY                     
    CHAN_IN_0_ADU_WRAPPING                        
    CHAN_OUT_0_ADU_UNWRAPPING                      
    CHAN_0_REG_STATE                           
    CHAN_0_IN_HOP_LIMIT                           
    CHAN_0_IN_CRC_TYPE                            
    CHAN_0_SPARE                               
    CHAN_0_INGRESS_BITS_PER_CYCLE              
    CHAN_0_EGRESS_BITS_PER_CYCLE               
    CHAN_0_IN_LOCAL_SERVICE_NUMBER                
    CHAN_0_IN_BUNDLE_PROC_FLAGS                   
    CHAN_0_IN_LIFETIME                            
    CHAN_0_IN_DESTINATION_EID_SCHEME              
    CHAN_0_IN_DESTINATION_EID_IPNSSPFORMAT        
    CHAN_0_IN_DESTINATION_EID_ALLOCATOR           
    CHAN_0_IN_DESTINATION_EID_NODE                
    CHAN_0_IN_DESTINATION_EID_SERVICE             
    CHAN_0_IN_REPORT_TO_EID_SCHEME                
    CHAN_0_IN_REPORT_TO_EID_IPNSSPFORMAT          
    CHAN_0_IN_REPORT_TO_EID_ALLOCATOR             
    CHAN_0_IN_REPORT_TO_EID_NODE                  
    CHAN_0_IN_REPORT_TO_EID_SERVICE               
    CHAN_0_IN_PREVNODEBLKCONFIG_INCLUDEBLOCK      
    CHAN_0_IN_PREVNODEBLKCONFIG_CRC_TYPE          
    CHAN_0_IN_PREVNODEBLKCONFIG_SPARE             
    CHAN_0_IN_PREVNODEBLKCONFIG_BLOCK_NUM         
    CHAN_0_IN_PREVNODEBLKCONFIG_BLOCK_PROC_FLAGS  
    CHAN_0_IN_AGEBLKCONFIG_INCLUDEBLOCK           
    CHAN_0_IN_AGEBLKCONFIG_CRC_TYPE               
    CHAN_0_IN_AGEBLKCONFIG_SPARE                  
    CHAN_0_IN_AGEBLKCONFIG_BLOCK_NUM              
    CHAN_0_IN_AGEBLKCONFIG_BLOCK_PROC_FLAGS       
    CHAN_0_IN_HOPCOUNTBLKCONFIG_INCLUDEBLOCK      
    CHAN_0_IN_HOPCOUNTBLKCONFIG_CRC_TYPE          
    CHAN_0_IN_HOPCOUNTBLKCONFIG_SPARE             
    CHAN_0_IN_HOPCOUNTBLKCONFIG_BLOCK_NUM         
    CHAN_0_IN_HOPCOUNTBLKCONFIG_BLOCK_PROC_FLAGS  
    CHAN_0_IN_PAYLOADBLKCONFIG_INCLUDEBLOCK       
    CHAN_0_IN_PAYLOADBLKCONFIG_CRC_TYPE           
    CHAN_0_IN_PAYLOADBLKCONFIG_SPARE              
    CHAN_0_IN_PAYLOADBLKCONFIG_BLOCK_NUM          
    CHAN_0_IN_PAYLOADBLKCONFIG_BLOCK_PROC_FLAGS   
    CHAN_1_ADD_AUTOMATICALLY                   
    CHAN_1_REQUEST_CUSTODY                     
    CHAN_IN_1_ADU_WRAPPING                        
    CHAN_OUT_1_ADU_UNWRAPPING                      
    CHAN_1_REG_STATE                           
    CHAN_1_IN_HOP_LIMIT                           
    CHAN_1_IN_CRC_TYPE                            
    CHAN_1_SPARE                               
    CHAN_1_INGRESS_BITS_PER_CYCLE              
    CHAN_1_EGRESS_BITS_PER_CYCLE               
    CHAN_IN_1_LOCAL_SERVICE_NUMBER                
    CHAN_IN_1_BUNDLE_PROC_FLAGS                   
    CHAN_IN_1_LIFETIME                            
    CHAN_IN_1_DESTINATION_EID_SCHEME              
    CHAN_IN_1_DESTINATION_EID_IPNSSPFORMAT        
    CHAN_IN_1_DESTINATION_EID_ALLOCATOR           
    CHAN_IN_1_DESTINATION_EID_NODE                
    CHAN_IN_1_DESTINATION_EID_SERVICE             
    CHAN_IN_1_REPORT_TO_EID_SCHEME                
    CHAN_IN_1_REPORT_TO_EID_IPNSSPFORMAT          
    CHAN_IN_1_REPORT_TO_EID_ALLOCATOR             
    CHAN_IN_1_REPORT_TO_EID_NODE                  
    CHAN_IN_1_REPORT_TO_EID_SERVICE               
    CHAN_IN_1_PREVNODEBLKCONFIG_INCLUDEBLOCK      
    CHAN_IN_1_PREVNODEBLKCONFIG_CRC_TYPE          
    CHAN_IN_1_PREVNODEBLKCONFIG_SPARE             
    CHAN_IN_1_PREVNODEBLKCONFIG_BLOCK_NUM         
    CHAN_IN_1_PREVNODEBLKCONFIG_BLOCK_PROC_FLAGS  
    CHAN_IN_1_AGEBLKCONFIG_INCLUDEBLOCK           
    CHAN_IN_1_AGEBLKCONFIG_CRC_TYPE               
    CHAN_IN_1_AGEBLKCONFIG_SPARE                  
    CHAN_IN_1_AGEBLKCONFIG_BLOCK_NUM              
    CHAN_IN_1_AGEBLKCONFIG_BLOCK_PROC_FLAGS       
    CHAN_IN_1_HOPCOUNTBLKCONFIG_INCLUDEBLOCK      
    CHAN_IN_1_HOPCOUNTBLKCONFIG_CRC_TYPE          
    CHAN_IN_1_HOPCOUNTBLKCONFIG_SPARE             
    CHAN_IN_1_HOPCOUNTBLKCONFIG_BLOCK_NUM         
    CHAN_IN_1_HOPCOUNTBLKCONFIG_BLOCK_PROC_FLAGS  
    CHAN_IN_1_PAYLOADBLKCONFIG_INCLUDEBLOCK       
    CHAN_IN_1_PAYLOADBLKCONFIG_CRC_TYPE           
    CHAN_IN_1_PAYLOADBLKCONFIG_SPARE              
    CHAN_IN_1_PAYLOADBLKCONFIG_BLOCK_NUM          
    CHAN_IN_1_PAYLOADBLKCONFIG_BLOCK_PROC_FLAGS   
    '''
    

def generate_mib_tables():
    print("Generating mib_tables ...")

    # MIB definition and default binary files
    def_file = "bpnode_mib_pn_def.txt"
    bin_file = "bpnode_mib_pn.tbl"

    ## mib_pn_blen_0.tbl
    out_file = "mib_pn_blen_0.tbl"
    values_list = [
           ["PARAM_SET_MAX_PAYLOAD_LENGTH",0], 
           ["PARAM_SET_MAX_BUNDLE_LENGTH",0], 
        ]
    TestUtils.update_table(def_file, bin_file, values_list, out_file)
    

    ## mib_pn_blen_200.tbl
    out_file = "mib_pn_blen_200.tbl"
    values_list = [
           ["PARAM_SET_MAX_PAYLOAD_LENGTH",100], 
           ["PARAM_SET_MAX_BUNDLE_LENGTH",200], 
        ]
    TestUtils.update_table(def_file, bin_file, values_list, out_file)


    ## mib_pn_invplen.tbl
    out_file = "mib_pn_invplen.tbl"
    values_list = [
           ["PARAM_SET_MAX_PAYLOAD_LENGTH",4096], 
           ["PARAM_SET_MAX_BUNDLE_LENGTH",4000], 
        ]
    TestUtils.update_table(def_file, bin_file, values_list, out_file)


    ## mib_short_life.tbl
    out_file = "mib_short_life.tbl"
    values_list = [
           ["PARAM_SET_MAX_LIFETIME",60000], 
        ]
    TestUtils.update_table(def_file, bin_file, values_list, out_file)



    '''
    INSTANCE_EID_SCHEME                 
    INSTANCE_EID_IPNSSPFORMAT           
    INSTANCE_EID_ALLOCATOR              
    INSTANCE_EID_NODE                   
    INSTANCE_EID_SERVICE                
    PARAM_BUNDLE_SIZE_NO_FRAGMENT       
    PARAM_SET_MAX_SEQUENCE_NUM          
    PARAM_SET_MAX_PAYLOAD_LENGTH        
    PARAM_SET_MAX_BUNDLE_LENGTH         
    PARAM_SET_NODE_DTN_TIME             
    PARAM_SET_BEHAVIOR_EVENT_REPORTING  
    PARAM_SET_MAX_LIFETIME            
    '''
#######################################################################

## main
#generate_build_test_tables('all')
#generate_build_test_tables('contact')
#generate_build_test_tables('channel')
generate_build_test_tables('mib')
