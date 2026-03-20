from openc3.script.suite import Group
from dtntools.dtncla.udp import UdpTxSocket, UdpRxSocket
from dtntools.dtngen.blocks import (
    PayloadBlock,
    PrimaryBlock,
)
from dtntools.dtngen.bundle import Bundle
from dtntools.dtngen.types import (
    EID,
    BlockType,
    BundlePCFlags,
    CRCFlag,
    CRCType,
    CreationTimestamp
)
import traceback

<% require 'dtnfsw_get_port_nums.rb' %>
<% require 'dtnfsw_globals.rb' %>


class integration_test_bpnode_sb_contact_flow(Group):
    """
    Test cases for the BPNode "contact_flow" command
    - Methods beginning with script_ or test_ are added to Script dropdown
    """

    def test_bpnode_sb_contact_downlink(self):
        """
        Nominal test
        - Send a bundle to contact 0 over UDP and see it returned to contact 1
          over the SB CLA
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

            # Wait for data to be sent back by CLA Out task
            wait_check(f"<%= target_name %> SB_CLA_OUT RECEIVED_COUNT == {expected_recv_count}", 10)

            bundle_arr = tlm(f"<%= target_name %> SB_CLA_OUT DATA")

            # Validate contents of bundle
            received_bundle = Bundle.from_bytes(bytes(bundle_arr))
            print(f"Received bundle: {received_bundle.to_json()}")
            check_expression(f"'{received_bundle.to_json() == Bundle.from_bytes(encoded_bundle).to_json()}' == 'True'")


        except KeyboardInterrupt:
            pass
        except Exception:
            print(traceback.format_exc())

        finally:
            # Clean up connections
            data_sender.disconnect()

    def test_bpnode_sb_contact_uplink(self):
        """
        Nominal test
        - Send a bundle to contact 1 over the SB CLA and see it returned to contact 0
          over the UDP CLA
        """

        # Port / Address Configs
        LOCALHOST_RX = "0.0.0.0"
        PORT_NUM_RX = <%= dtnfsw_get_cla_out_port(target_name, 0) %>

        # EID Configuration
        DEST_NODE_NUM = <%= $dtnfsw_globals_contact_0_dest_eid_node %>
        DEST_SERVICE_NUM = <%= $dtnfsw_globals_contact_0_dest_eid_service %>
        SRC_NODE_NUM = 300
        SRC_SERVICE_NUM = 1

        # Make sure port numbers were set properly
        check_expression(f"{PORT_NUM_RX} != 0")

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

        # Store the previous counter val, used to calculated expected/next value
        current_bundle_recv_count = tlm(f"<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_RECEIVED")
        expected_bundle_recv_count = current_bundle_recv_count + 1
        current_bundle_delvr_count = tlm(f"<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_FORWARDED")
        expected_bundle_delvr_count = current_bundle_delvr_count + 1

        # Encode the bundle
        encoded_bundle = bundle.to_bytes()

        # Connect to CLA #0 Out socket
        data_receiver = UdpRxSocket(LOCALHOST_RX, PORT_NUM_RX)

        try:
            # Connect the data receiver
            data_receiver.connect()

            Group.print(f"Sending bundle of {len(encoded_bundle)} bytes")

            # Send bundle over SB CLA
            cmd(f"<%= target_name %> BPNODE_BUNDLE_RX with DATA {list(encoded_bundle)}")

            # Check that the BPNode telemetry incremented as expected
            wait_check(f"<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_RECEIVED == {expected_bundle_recv_count}", 10)
            wait_check(f"<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_FORWARDED == {expected_bundle_delvr_count}", 10)

            received_bundle = data_receiver.read()

            # Validate contents of bundle
            print(f"Received bundle: {Bundle.from_bytes(received_bundle).to_json()}")
            check_expression(f"'{Bundle.from_bytes(received_bundle).to_json() == Bundle.from_bytes(encoded_bundle).to_json()}' == 'True'")


        except KeyboardInterrupt:
            pass
        except Exception:
            print(traceback.format_exc())

        finally:
            # Clean up connections
            data_receiver.disconnect()


    def setup(self):
        """
        Test Group Setup
        - Runs when Group Setup button is pressed
        - Runs before all scripts when Group Start is pressed
        """
        pass

    def teardown(self):
        """
        Test Group Setup
        - Runs when Group Teardown button is pressed
        - Runs after all scripts when Group Start is pressed
        """
        # Reset counters
        cmd(f"<%= target_name %> BPNODE_CMD_RESET_ALL_COUNTERS")

        # Wait for the expected results
        wait_check(f"<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_RECEIVED == 0", 10)
