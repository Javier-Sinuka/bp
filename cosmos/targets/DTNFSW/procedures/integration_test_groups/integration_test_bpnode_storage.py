from openc3.script.suite import Group

from dtntools.dtncla.udp import UdpRxSocket, UdpTxSocket
from dtntools.dtngen.blocks import (
    PayloadBlock,
    PrevNodeBlock,
    PrimaryBlock,
    AdminRecordBlock,
)
from dtntools.dtngen.bundle import Bundle
from dtntools.dtngen.types import (
    EID,
    BlockType,
    BundlePCFlags,
    CRCFlag,
    CRCType,
    CreationTimestamp,
    DispositionCode,
    CreationTimestamp,
    AdminRecordType,
    CCSData,
    BundleSequenceCollection,
    CTEBData
)

LOCAL_NODE_EID = EID(
    {
        "uri": 2,
        "ssp": {"node_num": <%= $dtnfsw_globals_channel_dest_eid_node %>,
                "service_num": <%= $dtnfsw_globals_local_service_num %>}
    }
)

import traceback

# Group class name should indicate what the scripts are testing
class integration_test_bpnode_storage(Group):
    """
    Test cases for ingesting an ADU, routing it to storage, and then sending it back
    out on a new contact
    """

    def test_bpnode_adu_to_stor_to_egress(self):
        """
        FSW ADU Ingest
        - Send an ADU (SB Statistics packet), watch it become a stored bundle, then
          enable a contact to egress it
        """

        # Port / Address Configs
        LOCALHOST_RX = "0.0.0.0"
        PORT_NUM_RX = <%= dtnfsw_get_cla_out_port(target_name, 0) %>
        BPNODE_IP   = "172.17.0.1"
        BPNODE_PORT = 4501

        # Make sure port numbers were set properly
        check_expression(f"{PORT_NUM_RX} != 0")

        # Connect to CLA #0 Out sockets
        data_receiver = UdpRxSocket(LOCALHOST_RX, PORT_NUM_RX)
        data_sender   = UdpTxSocket(BPNODE_IP, BPNODE_PORT)

        # Store the previous counter val, used to calculated expected/next value
        current_valid_adu_count = tlm(f"<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK ADU_COUNT_RECEIVED")
        expected_valid_adu_count = current_valid_adu_count + 1
        current_bundle_delvr_count = tlm(f"<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_FORWARDED")
        expected_bundle_delvr_count = current_bundle_delvr_count + 1
        current_bundle_stored_count = tlm(f"<%= target_name %> BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED")
        expected_bundle_stored_count = current_bundle_stored_count + 1        

        try:
            # Connect the data receiver tool
            data_receiver.connect()
            data_sender.connect()

            # Send the command
            cmd(f"<%= target_name %> CFE_SB_CMD_SEND_SB_STATS")

            # Wait for the bundle to reach storage
            wait_check(f"<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK ADU_COUNT_RECEIVED == {expected_valid_adu_count}", 10)
            wait_check(f"<%= target_name %> BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED == {expected_bundle_stored_count}", 10)

            # Enable contact 0 to egress bundle from storage
            cmd(f'<%= target_name %> BPNODE_CMD_CONTACT_SETUP with CONTACT_ID 0')
            cmd(f'<%= target_name %> BPNODE_CMD_CONTACT_START with CONTACT_ID 0')

            wait_check(f"<%= target_name %> BPNODE_CHAN_CON_STAT_HK CON_STAT_RUN_STATE_0 == 'STARTED'", 10)
            wait_check(f"<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_FORWARDED == {expected_bundle_delvr_count}", 10)

            # Wait for data to be sent back by CLA Out task
            Group.print("Waiting for bundle to be returned...")
            received_data = data_receiver.read()
            Group.print(f"Received bundle of {len(received_data)} bytes")

            # Check that the right data was returned by the CLA Out task
            check_expression(f"{received_data} != None")
            print(f"Received bundle of size: {len(received_data)}.")
            received_bundle = Bundle.from_bytes(received_data)
            print(f"Received bundle: {received_bundle.to_json()}")
            check_expression(f"{received_bundle.pri_block.version} == 7")
            check_expression(f"{received_bundle.pri_block.control_flags} == 4")
            check_expression(f"{received_bundle.pri_block.crc_type} == {CRCType.CRC16_X25}")
            check_expression(f"{received_bundle.pri_block.is_crc_valid()}")

            # these EIDs are set via channel / bplib configurations
            expected_dest_eid = EID({"uri": 2, "ssp": {"node_num": 200, "service_num": 64}})
            expected_src_eid = EID({"uri": 2, "ssp": {"node_num": 100, "service_num": 42}})
            expected_rpt_eid = EID({"uri": 1, "ssp": 0}) # dtn:none
            bpnode_check_eid_equality(received_bundle.pri_block.dest_eid, expected_dest_eid)
            bpnode_check_eid_equality(received_bundle.pri_block.src_eid, expected_src_eid)
            # TODO add me back once EID test tool logic is fixed
            #bpnode_check_eid_equality(received_bundle.pri_block.rpt_eid, expected_rpt_eid)

            exp_new_hop_count = 1
            exp_new_hop_limit = 10

            # Note: See the default channel config table for the source of these configs

            # Check the canonical blocks
            check_expression(f"{len(received_bundle.canon_blocks)} == 5")

            # Check the prev node block
            check_expression(f"{received_bundle.canon_blocks[0].blk_type} == {BlockType.PREVIOUS_NODE}")
            check_expression(f"{received_bundle.canon_blocks[0].blk_num} == {2}")
            check_expression(f"{received_bundle.canon_blocks[0].control_flags} == {0}")
            check_expression(f"{received_bundle.canon_blocks[0].crc_type} == {CRCType.CRC16_X25}")
            check_expression(f"{received_bundle.canon_blocks[0].is_crc_valid()}")
            bpnode_check_eid_equality(received_bundle.canon_blocks[0].prev_eid, LOCAL_NODE_EID)

            # Check the age block
            check_expression(f"{received_bundle.canon_blocks[1].blk_type} == {BlockType.BUNDLE_AGE}")
            check_expression(f"{received_bundle.canon_blocks[1].blk_num} == {3}")
            check_expression(f"{received_bundle.canon_blocks[1].control_flags} == {0}")
            check_expression(f"{received_bundle.canon_blocks[1].crc_type} == {CRCType.CRC16_X25}")
            check_expression(f"{received_bundle.canon_blocks[1].is_crc_valid()}")

            # Check the hop count block
            check_expression(f"{received_bundle.canon_blocks[2].blk_type} == {BlockType.HOP_COUNT}")
            check_expression(f"{received_bundle.canon_blocks[2].blk_num} == {4}")
            check_expression(f"{received_bundle.canon_blocks[2].control_flags} == {0}")
            check_expression(f"{received_bundle.canon_blocks[2].crc_type} == {CRCType.CRC16_X25}")
            check_expression(f"{received_bundle.canon_blocks[2].is_crc_valid()}")
            check_expression(f"{received_bundle.canon_blocks[2].hop_data.hop_limit} == {exp_new_hop_limit}")
            check_expression(f"{received_bundle.canon_blocks[2].hop_data.hop_count} == {exp_new_hop_count}")

            # Skip CTEB checking

            # Check the payload block
            check_expression(f"{received_bundle.canon_blocks[4].blk_type} == {BlockType.BUNDLE_PAYLOAD}")
            check_expression(f"{received_bundle.canon_blocks[4].blk_num} == {1}")
            check_expression(f"{received_bundle.canon_blocks[4].control_flags} == {0}")
            check_expression(f"{received_bundle.canon_blocks[4].crc_type} == {CRCType.CRC16_X25}")
            check_expression(f"{received_bundle.canon_blocks[4].is_crc_valid()}")

            # Send a CCS to clear custodial bundle

            SRC_NODE_NUM    = 100
            SRC_SERVICE_NUM = 0
            RPT_NODE_NUM    = 200
            RPT_SERVICE_NUM = 2

            primary_block = PrimaryBlock(
                            version=7,
                            control_flags=BundlePCFlags.IS_ADMIN_RECORD,
                            crc_type=CRCType.CRC16_X25,
                            dest_eid=EID({"uri": 2, "ssp": {"node_num": 100, "service_num": 0}}),
                            src_eid=EID({"uri": 2, "ssp": {"node_num": SRC_NODE_NUM, "service_num": SRC_SERVICE_NUM}}),
                            rpt_eid=EID({"uri": 2, "ssp": {"node_num": RPT_NODE_NUM, "service_num": RPT_SERVICE_NUM}}),
                            creation_timestamp=CreationTimestamp({"time": DtnTimeNowMs(), "sequence": 0}),
                            lifetime=3600000,
                            crc=CRCFlag.CALCULATE
                        )

            next_node_ccs = AdminRecordBlock(
                blk_type=BlockType.AUTO,
                blk_num=1,
                control_flags=0,
                crc_type=CRCType.CRC16_X25,
                record_type = AdminRecordType.COMPRESSED_CUSTODY_SIGNAL,
                record_content = CCSData({
                    DispositionCode.CUSTODY_ACCEPTED: BundleSequenceCollection(
                                                bundle_seq_id=received_bundle.canon_blocks[3].cteb_data.bundle_seq_id,
                                                first_seq_num=received_bundle.canon_blocks[3].cteb_data.bundle_seq_num,
                                                bundle_seq_range=[1])

                }),
                crc=CRCFlag.CALCULATE
            )

            ccs_bundle = Bundle(
                pri_block=primary_block,
                canon_blocks=[next_node_ccs],
            )

            encoded_input_bundle = ccs_bundle.to_bytes()
            data_sender.write(encoded_input_bundle)
            
            # Verify bundle is deleted
            expected_bundle_stored_count = expected_bundle_stored_count - 1
            wait_check(f"<%= target_name %> BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED == {expected_bundle_stored_count}", 20)

        except KeyboardInterrupt:
            pass
        except Exception:
            print(traceback.format_exc())

        finally:
            # Clean up connections
            data_receiver.disconnect()
            data_sender.disconnect()

    def test_bpnode_bundle_to_stor_to_egress(self):
        """
        Nominal test
        - Send a bundle to contact 0 over UDP, get stored, then egressed over the SB CLA
          on contact 1
        """

        # Port / Address Configs
        DOCKER_LOCALHOST_TX = "172.17.0.1"
        PORT_NUM_TX = <%= dtnfsw_get_cla_in_port(target_name, 0) %>

        # EID Configuration
        DEST_NODE_NUM = <%= $dtnfsw_globals_contact_1_dest_eid_node %>
        DEST_SERVICE_NUM = <%= $dtnfsw_globals_contact_1_dest_eid_service %>
        SRC_NODE_NUM = 300
        SRC_SERVICE_NUM = 1

        # Make sure port numbers were set properly
        check_expression(f"{PORT_NUM_TX} != 0")

        # Store the previous counter val, used to calculated expected/next value
        current_recv_count = tlm(f"<%= target_name %> SB_CLA_OUT RECEIVED_COUNT")
        current_recv_count = 0 if current_recv_count is None else current_recv_count
        expected_recv_count = current_recv_count + 1
        current_bundle_recv_count = tlm(f"<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_RECEIVED")
        expected_bundle_recv_count = current_bundle_recv_count + 1
        current_bundle_delvr_count = tlm(f"<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_FORWARDED")
        expected_bundle_delvr_count = current_bundle_delvr_count + 1
        current_bundle_stored_count = tlm(f"<%= target_name %> BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED")
        expected_bundle_stored_count = current_bundle_stored_count + 1        

        wait_check(f"<%= target_name %> BPNODE_CHAN_CON_STAT_HK CON_STAT_RUN_STATE_1 == 'TORNDOWN'", 10)

        # Set up contact for ingress
        cmd(f'<%= target_name %> BPNODE_CMD_CONTACT_SETUP with CONTACT_ID 0')
        cmd(f'<%= target_name %> BPNODE_CMD_CONTACT_START with CONTACT_ID 0')
        wait_check(f"<%= target_name %> BPNODE_CHAN_CON_STAT_HK CON_STAT_RUN_STATE_0 == 'STARTED'", 10)


        # Create out test bundle
        primary_block = PrimaryBlock(
            version=7,
            control_flags=BundlePCFlags.MUST_NOT_FRAGMENT,
            crc_type=CRCType.CRC16_X25,
            dest_eid=EID({"uri": 2, "ssp": {"node_num": DEST_NODE_NUM, "service_num": DEST_SERVICE_NUM}}),
            src_eid=EID({"uri": 2, "ssp": {"node_num": SRC_NODE_NUM, "service_num": SRC_SERVICE_NUM}}),
            rpt_eid=EID({"uri": 1, "ssp": 0}), # This is equivalent to dtn:none
            creation_timestamp=CreationTimestamp({"time": 755533838904, "sequence": 0}),
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

        # Encode the bundle
        encoded_bundle = bundle.to_bytes()

        # Connect to CLA #0 In/Out sockets
        data_sender = UdpTxSocket(DOCKER_LOCALHOST_TX, PORT_NUM_TX)

        try:
            # Connect the data sender and receiver tools
            data_sender.connect()

            # Write data to the CLA In task
            data_sender.write(encoded_bundle)
            Group.print(f"Sending bundle of {len(encoded_bundle)} bytes")

            # Wait for the bundle to reach storage
            wait_check(f"<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_RECEIVED == {expected_bundle_recv_count}", 10)
            wait_check(f"<%= target_name %> BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED == {expected_bundle_stored_count}", 10)

            # Send a duplicate bundle (should not be stored)
            data_sender.write(encoded_bundle)
            Group.print(f"Sending bundle of {len(encoded_bundle)} bytes")
            expected_bundle_recv_count = expected_bundle_recv_count + 1
            wait_check(f"<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_RECEIVED == {expected_bundle_recv_count}", 10)
            wait_check(f"<%= target_name %> BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED == {expected_bundle_stored_count}", 10)

            # Enable contact 1 to egress bundle from storage
            cmd(f'<%= target_name %> BPNODE_CMD_CONTACT_SETUP with CONTACT_ID 1')
            cmd(f'<%= target_name %> BPNODE_CMD_CONTACT_START with CONTACT_ID 1')

            wait_check(f"<%= target_name %> BPNODE_CHAN_CON_STAT_HK CON_STAT_RUN_STATE_1 == 'STARTED'", 10)
            wait_check(f"<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_FORWARDED == {expected_bundle_delvr_count}", 10)

            # Wait for data to be sent back by CLA Out task
            wait_check(f"<%= target_name %> SB_CLA_OUT RECEIVED_COUNT == {expected_recv_count}", 10)

            bundle_arr = tlm(f"<%= target_name %> SB_CLA_OUT DATA")

            # Validate contents of bundle
            received_bundle = Bundle.from_bytes(bytes(bundle_arr))
            print(f"Received bundle: {received_bundle.to_json()}")
            check_expression(f"'{received_bundle.to_json() == Bundle.from_bytes(encoded_bundle).to_json()}' == 'True'")

            # Verify bundle is deleted
            expected_bundle_stored_count = expected_bundle_stored_count - 1
            wait_check(f"<%= target_name %> BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED == {expected_bundle_stored_count}", 20)


        except KeyboardInterrupt:
            pass
        except Exception:
            print(traceback.format_exc())

        finally:
            # Clean up connections
            data_sender.disconnect()


    def setup(self):
        """
        Test Group Setup
        - Runs when Group Setup button is pressed
        - Runs before all scripts when Group Start is pressed
        """
        wait_check(f"<%= target_name %> BPNODE_CHAN_CON_STAT_HK CON_STAT_RUN_STATE_0 == 'STARTED'", 10)
        wait_check(f"<%= target_name %> BPNODE_CHAN_CON_STAT_HK CON_STAT_RUN_STATE_1 == 'STARTED'", 10)

        cmd(f'<%= target_name %> BPNODE_CMD_CONTACT_STOP with CONTACT_ID 0')
        cmd(f'<%= target_name %> BPNODE_CMD_CONTACT_TEARDOWN with CONTACT_ID 0')
        cmd(f'<%= target_name %> BPNODE_CMD_CONTACT_STOP with CONTACT_ID 1')
        cmd(f'<%= target_name %> BPNODE_CMD_CONTACT_TEARDOWN with CONTACT_ID 1')

        wait_check(f"<%= target_name %> BPNODE_CHAN_CON_STAT_HK CON_STAT_RUN_STATE_0 == 'TORNDOWN'", 10)
        wait_check(f"<%= target_name %> BPNODE_CHAN_CON_STAT_HK CON_STAT_RUN_STATE_1 == 'TORNDOWN'", 10)

        wait(10)

    def teardown(self):
        """
        Test Group Setup
        - Runs when Group Teardown button is pressed
        - Runs after all scripts when Group Start is pressed
        """

        cmd(f'<%= target_name %> BPNODE_CMD_CONTACT_SETUP with CONTACT_ID 0')
        cmd(f'<%= target_name %> BPNODE_CMD_CONTACT_START with CONTACT_ID 0')
        cmd(f'<%= target_name %> BPNODE_CMD_CONTACT_SETUP with CONTACT_ID 1')
        cmd(f'<%= target_name %> BPNODE_CMD_CONTACT_START with CONTACT_ID 1')

        wait_check(f"<%= target_name %> BPNODE_CHAN_CON_STAT_HK CON_STAT_RUN_STATE_0 == 'STARTED'", 10)
        wait_check(f"<%= target_name %> BPNODE_CHAN_CON_STAT_HK CON_STAT_RUN_STATE_1 == 'STARTED'", 10)

        # Reset counters
        cmd(f"<%= target_name %> BPNODE_CMD_RESET_ALL_COUNTERS")

        # Wait for the expected results
        wait_check(f"<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_AGENT_ACCEPTED_DIRECTIVE_COUNT == 0", 10)

        wait(10)