from openc3.script.suite import Group

from dtntools.dtncla.udp import UdpRxSocket, UdpTxSocket
from dtntools.dtngen.blocks import (
    PrimaryBlock,
    PayloadBlock,
)
from dtntools.dtngen.bundle import Bundle
from dtntools.dtngen.types import (
    EID,
    BlockType,
    BundlePCFlags,
    CRCFlag,
    CRCType,
    CreationTimestamp,
)

# Networking Configuration: Please ensure you have port forwarding rules
BPNODE_IP   = "172.17.0.1"
BPNODE_PORT = 4501
LOCAL_IP    = "0.0.0.0"
LOCAL_PORT  = 4551

class integration_test_bpnode_set_registration_state(Group):
    """
    Test cases for the BPNode "set_registration_state" command
    - Methods beginning with script_ or test_ are added to Script dropdown
    """

    def test_bpnode_set_registration_state(self):
        """
        Nominal test
        """

        # Test 1: Set registration state to passive-abandon

        # Store the previous counter val, used to calculated expected/next value
        current_valid_cmd_count = tlm(f"<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_AGENT_ACCEPTED_DIRECTIVE_COUNT")
        expected_valid_cmd_count = current_valid_cmd_count + 1

        # Send the command
        cmd(f"<%= target_name %> BPNODE_CMD_SET_REGISTRATION_STATE with CHAN_ID 1, REG_STATE 'PASSIVE_ABANDON'")
        wait_check(f"<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_AGENT_ACCEPTED_DIRECTIVE_COUNT == {expected_valid_cmd_count}", 10)

        current_valid_adu_count = tlm(f"<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK ADU_COUNT_RECEIVED")
        expected_valid_adu_count = current_valid_adu_count + 1
        current_adu_delvr_count = tlm(f"<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK ADU_COUNT_DELIVERED")
        current_delete_count = tlm(f"<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_DELETED")
        expected_delete_count = current_delete_count + 1

        # Send the command to generate an ADU for channel 1 to ingest, 
        # create a bundle, and then delete the bundle
        cmd(f"<%= target_name %> CFE_TIME_CMD_SEND_DIAGNOSTIC")
        wait_check(f"<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK ADU_COUNT_RECEIVED == {expected_valid_adu_count}", 10)
        wait_check(f"<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK ADU_COUNT_DELIVERED == {current_adu_delvr_count}", 10)
        wait_check(f"<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_DELETED == {expected_delete_count}", 10)


        # Test 1: Set registration state to passive-defer
        
        # Store the previous counter val, used to calculated expected/next value
        current_valid_cmd_count = tlm(f"<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_AGENT_ACCEPTED_DIRECTIVE_COUNT")
        expected_valid_cmd_count = current_valid_cmd_count + 1

        # Send the command
        cmd(f"<%= target_name %> BPNODE_CMD_SET_REGISTRATION_STATE with CHAN_ID 1, REG_STATE 'PASSIVE_DEFER'")
        wait_check(f"<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_AGENT_ACCEPTED_DIRECTIVE_COUNT == {expected_valid_cmd_count}", 10)

        current_valid_adu_count = tlm(f"<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK ADU_COUNT_RECEIVED")
        expected_valid_adu_count = current_valid_adu_count + 1
        current_adu_delvr_count = tlm(f"<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK ADU_COUNT_DELIVERED")
        expected_adu_delvr_count = current_adu_delvr_count + 1
        current_stor_count = tlm(f"<%= target_name %> BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED")
        expected_stor_count = current_stor_count + 1

        # Send the command to generate an ADU for channel 1 to ingest, 
        # create a bundle, and then store the bundle
        cmd(f"<%= target_name %> CFE_TIME_CMD_SEND_DIAGNOSTIC")
        wait_check(f"<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK ADU_COUNT_RECEIVED == {expected_valid_adu_count}", 10)
        wait_check(f"<%= target_name %> BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED == {expected_stor_count}", 10)

        # Set registration state back to active to trigger delivery of bundle
        cmd(f"<%= target_name %> BPNODE_CMD_SET_REGISTRATION_STATE with CHAN_ID 1, REG_STATE 'ACTIVE'")
        wait_check(f"<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK ADU_COUNT_DELIVERED == {expected_adu_delvr_count}", 10)

    def test_bpnode_set_registration_state_abandon_incoming_bundle(self):

        # EID Configuration
        SRC_NODE_NUM     = 300
        SRC_SERVICE_NUM  = 5
        DEST_NODE_NUM    = 100
        DEST_SERVICE_NUM = 53

        data_receiver = UdpRxSocket(LOCAL_IP, LOCAL_PORT)
        data_sender   = UdpTxSocket(BPNODE_IP, BPNODE_PORT)

        # Setup contact 0
        # Get current state
        cmd("DTNFSW-1 BPNODE_CMD_SEND_CHANNEL_CONTACT_STAT_HK")
        wait_check(f'DTNFSW-1 BPNODE_CHAN_CON_STAT_HK RECEIVED_COUNT >= 0', 10)
        run_state = tlm(f'DTNFSW-1 BPNODE_CHAN_CON_STAT_HK CON_STAT_RUN_STATE_0')

        # Store the previous counter val, used to calculated expected/next value
        current_valid_cmd_count = tlm(f"DTNFSW-1 BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_AGENT_ACCEPTED_DIRECTIVE_COUNT")
        expected_valid_cmd_count = current_valid_cmd_count + 1
        
        # SETUP contact if it's torndown
        if run_state == "TORNDOWN":
            # Set up contact
            cmd(f'DTNFSW-1 BPNODE_CMD_CONTACT_SETUP with CONTACT_ID 0')
            wait_check(f"DTNFSW-1 BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_AGENT_ACCEPTED_DIRECTIVE_COUNT == {expected_valid_cmd_count}", 10)
            expected_valid_cmd_count += 1
            
            # Check the run state for the contact
            cmd("DTNFSW-1 BPNODE_CMD_SEND_CHANNEL_CONTACT_STAT_HK")
            wait_check(f'DTNFSW-1 BPNODE_CHAN_CON_STAT_HK CON_STAT_RUN_STATE_0 == "SETUP"', 10)

            run_state = "SETUP"

        if run_state != "STARTED":
            # Start contact
            cmd(f'DTNFSW-1 BPNODE_CMD_CONTACT_START with CONTACT_ID 0')
            wait_check(f"DTNFSW-1 BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_AGENT_ACCEPTED_DIRECTIVE_COUNT == {expected_valid_cmd_count}", 10)
            expected_valid_cmd_count += 1
        
        # Check the run state for the contact
        cmd("DTNFSW-1 BPNODE_CMD_SEND_CHANNEL_CONTACT_STAT_HK")
        wait_check(f'DTNFSW-1 BPNODE_CHAN_CON_STAT_HK CON_STAT_RUN_STATE_0 == "STARTED"', 10)


        # Store the previous counter val, used to calculated expected/next value
        current_valid_cmd_count = tlm(f"<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_AGENT_ACCEPTED_DIRECTIVE_COUNT")
        expected_valid_cmd_count = current_valid_cmd_count + 1

        # Send the command
        cmd(f"<%= target_name %> BPNODE_CMD_SET_REGISTRATION_STATE with CHAN_ID 1, REG_STATE 'PASSIVE_ABANDON'")
        wait_check(f"<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_AGENT_ACCEPTED_DIRECTIVE_COUNT == {expected_valid_cmd_count}", 10)


        try:
            # Connect the data sender and receiver tools
            data_receiver.connect()
            data_sender.connect()

            # Create out test bundle
            primary_block = PrimaryBlock(
                version=7,
                control_flags=BundlePCFlags.MUST_NOT_FRAGMENT,
                crc_type=CRCType.CRC16_X25,
                dest_eid=EID({"uri": 2, "ssp": {"node_num": DEST_NODE_NUM, "service_num": DEST_SERVICE_NUM}}),
                src_eid=EID({"uri": 2, "ssp": {"node_num": SRC_NODE_NUM, "service_num": SRC_SERVICE_NUM}}),
                rpt_eid=EID({"uri": 1, "ssp": 0}), # This is equivalent to dtn:none
                creation_timestamp=CreationTimestamp({"time": 755533838914, "sequence": 0}),
                lifetime=3600000,
                crc=CRCFlag.CALCULATE,
            )

            payload_block = PayloadBlock(
                blk_type=BlockType.AUTO,
                blk_num=1,
                control_flags=0,
                crc_type=CRCType.CRC16_X25,
                payload=b"\x00\x00\x00\x00\x00\x00\x00\x0chello world\n",
                crc=CRCFlag.CALCULATE,
            )

            # Use them to create a bundle object
            bundle = Bundle(
                pri_block=primary_block,
                canon_blocks=[
                    payload_block,
                ],
            )

            current_abandoned = tlm(f'<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_ABANDONED')
            expected_abandoned = current_abandoned + 1

            # Encode the bundle
            data_sender.write(bundle.to_bytes())
            
            wait_check(f"<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_ABANDONED == {expected_abandoned}", 10)
            
        except KeyboardInterrupt:
            pass

        except Exception:
            print(traceback.format_exc())

        finally:
            data_receiver.disconnect()
            data_sender.disconnect()


    def setup(self):
        """
        Test Group Setup
        - Runs when Group Setup button is pressed
        - Runs before all scripts when Group Start is pressed
        """
        # Set up channel 1
        cmd(f"<%= target_name %> BPNODE_CMD_ADD_APPLICATION with CHAN_ID 1")
        cmd(f"<%= target_name %> BPNODE_CMD_START_APPLICATION with CHAN_ID 1")
        wait_check(f"<%= target_name %> BPNODE_CHAN_CON_STAT_HK CHAN_STAT_STATE_1 == 'STARTED'", 10)


    def teardown(self):
        """
        Test Group Setup
        - Runs when Group Teardown button is pressed
        - Runs after all scripts when Group Start is pressed
        """
        # Tear down channel 1
        cmd(f"<%= target_name %> BPNODE_CMD_STOP_APPLICATION with CHAN_ID 1")
        cmd(f"<%= target_name %> BPNODE_CMD_REMOVE_APPLICATION with CHAN_ID 1")
        wait_check(f"<%= target_name %> BPNODE_CHAN_CON_STAT_HK CHAN_STAT_STATE_1 == 'REMOVED'", 10)

        # Reset counters
        cmd(f"<%= target_name %> BPNODE_CMD_RESET_ALL_COUNTERS")

        # Wait for the expected results
        wait_check(f"<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_AGENT_ACCEPTED_DIRECTIVE_COUNT == 0", 10)
