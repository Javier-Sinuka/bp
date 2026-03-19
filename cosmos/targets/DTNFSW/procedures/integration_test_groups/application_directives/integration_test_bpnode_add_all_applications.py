from openc3.script.suite import Group

class integration_test_bpnode_add_all_applications(Group):
    """
    Test cases for the BPNode "add_all_applications" command
    - Methods beginning with script_ or test_ are added to Script dropdown
    """

    def test_bpnode_add_all_applications(self):
        """
        Nominal test
        """
        # Store the previous counter val, used to calculated expected/next value
        current_valid_cmd_count = tlm(f"<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_AGENT_ACCEPTED_DIRECTIVE_COUNT")
        expected_valid_cmd_count = current_valid_cmd_count + 1

        # Send the command
        cmd(f"<%= target_name %> BPNODE_CMD_ADD_ALL_APPLICATIONS")

        # Wait for the expected results
        wait_check(f"<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_AGENT_ACCEPTED_DIRECTIVE_COUNT == {expected_valid_cmd_count}", 10)

        for chan_id in range(<%= $dtnfsw_globals_num_channels %>): 
            wait_check(f"<%= target_name %> BPNODE_CHAN_CON_STAT_HK CHAN_STAT_STATE_{chan_id} == 'ADDED'", 10)

    def setup(self):
        """
        Test Group Setup
        - Runs when Group Setup button is pressed
        - Runs before all scripts when Group Start is pressed
        """
        
        # Remove any running applications
        for chan_id in range(<%= $dtnfsw_globals_num_channels %>): 
            cmd(f"<%= target_name %> BPNODE_CMD_STOP_APPLICATION with CHAN_ID {chan_id}")
            cmd(f"<%= target_name %> BPNODE_CMD_REMOVE_APPLICATION with CHAN_ID {chan_id}")
            wait_check(f"<%= target_name %> BPNODE_CHAN_CON_STAT_HK CHAN_STAT_STATE_{chan_id} == 'REMOVED'", 10)

        wait(5)

    def teardown(self):
        """
        Test Group Setup
        - Runs when Group Teardown button is pressed
        - Runs after all scripts when Group Start is pressed
        """
        # Remove the added applications
        for chan_id in range(<%= $dtnfsw_globals_num_channels %>): 
            cmd(f"<%= target_name %> BPNODE_CMD_REMOVE_APPLICATION with CHAN_ID {chan_id}")
            wait_check(f"<%= target_name %> BPNODE_CHAN_CON_STAT_HK CHAN_STAT_STATE_{chan_id} == 'REMOVED'", 10)

        # Reset counters
        cmd(f"<%= target_name %> BPNODE_CMD_RESET_ALL_COUNTERS")

        # Wait for the expected results
        wait_check(f"<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_AGENT_ACCEPTED_DIRECTIVE_COUNT == 0", 10)
