def start_contacts():
    curr_to_lab_pkt_count = tlm(f"DTNFSW-1 TO_LAB_HK RECEIVED_COUNT")
    if curr_to_lab_pkt_count is None:
        curr_to_lab_pkt_count = 0        

    exp_to_lab_pkt_count = curr_to_lab_pkt_count + 1

    # Send the command, TO_LAB_CMD_ENABLE_OUT
    to_lab_dest_ip = "127.0.0.1"
    cmd(f"DTNFSW-1 TO_LAB_CMD_ENABLE_OUTPUT with DEST_IP '{to_lab_dest_ip}'")
    Group.print(f"Sent TO_LAB_CMD_ENABLE_OUTPUT command to DTNFSW-1 with DEST_IP '{to_lab_dest_ip}'")

    # Wait for one TO packet to be received
    wait_check(f"DTNFSW-1 TO_LAB_HK RECEIVED_COUNT == {exp_to_lab_pkt_count}", 10)

    # Set up and start all contacts
    for contact_num in range(3):
        # Get current state
        cmd("DTNFSW-1 BPNODE_CMD_SEND_CHANNEL_CONTACT_STAT_HK")
        wait_check(f'DTNFSW-1 BPNODE_CHAN_CON_STAT_HK RECEIVED_COUNT >= 0', 10)
        run_state = tlm(f'DTNFSW-1 BPNODE_CHAN_CON_STAT_HK CON_STAT_RUN_STATE_{contact_num}')

        # Store the previous counter val, used to calculated expected/next value
        current_valid_cmd_count = tlm(f"DTNFSW-1 BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_AGENT_ACCEPTED_DIRECTIVE_COUNT")
        expected_valid_cmd_count = current_valid_cmd_count + 1
        
        # Get contact state to TORNDOWN
        if run_state == "SETUP":
            # Tear down contact
            cmd(f'DTNFSW-1 BPNODE_CMD_CONTACT_TEARDOWN with CONTACT_ID {contact_num}')
            wait_check(f"DTNFSW-1 BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_AGENT_ACCEPTED_DIRECTIVE_COUNT == {expected_valid_cmd_count}", 10)
            expected_valid_cmd_count += 1
        
            # Check the run state for the contact
            cmd("DTNFSW-1 BPNODE_CMD_SEND_CHANNEL_CONTACT_STAT_HK")
            wait_check(f'DTNFSW-1 BPNODE_CHAN_CON_STAT_HK CON_STAT_RUN_STATE_{contact_num} == "TORNDOWN"', 10)
        elif run_state == "STOPPED":
            # Tear down contact
            cmd(f'DTNFSW-1 BPNODE_CMD_CONTACT_TEARDOWN with CONTACT_ID {contact_num}')
            wait_check(f"DTNFSW-1 BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_AGENT_ACCEPTED_DIRECTIVE_COUNT == {expected_valid_cmd_count}", 10)
            expected_valid_cmd_count += 1
        
            # Check the run state for the contact
            cmd("DTNFSW-1 BPNODE_CMD_SEND_CHANNEL_CONTACT_STAT_HK")
            wait_check(f'DTNFSW-1 BPNODE_CHAN_CON_STAT_HK CON_STAT_RUN_STATE_{contact_num} == "TORNDOWN"', 10)
        
        # Set up contact
        cmd(f'DTNFSW-1 BPNODE_CMD_CONTACT_SETUP with CONTACT_ID {contact_num}')
        wait_check(f"DTNFSW-1 BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_AGENT_ACCEPTED_DIRECTIVE_COUNT == {expected_valid_cmd_count}", 10)
        expected_valid_cmd_count += 1
        
        # Check the run state for the contact
        cmd("DTNFSW-1 BPNODE_CMD_SEND_CHANNEL_CONTACT_STAT_HK")
        wait_check(f'DTNFSW-1 BPNODE_CHAN_CON_STAT_HK CON_STAT_RUN_STATE_{contact_num} == "SETUP"', 10)
        
        # Start contact
        cmd(f'DTNFSW-1 BPNODE_CMD_CONTACT_START with CONTACT_ID {contact_num}')
        wait_check(f"DTNFSW-1 BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_AGENT_ACCEPTED_DIRECTIVE_COUNT == {expected_valid_cmd_count}", 10)
        expected_valid_cmd_count += 1
        
        # Check the run state for the contact
        cmd("DTNFSW-1 BPNODE_CMD_SEND_CHANNEL_CONTACT_STAT_HK")
        wait_check(f'DTNFSW-1 BPNODE_CHAN_CON_STAT_HK CON_STAT_RUN_STATE_{contact_num} == "STARTED"', 10)