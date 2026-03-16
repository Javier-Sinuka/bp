from openc3.script.suite import Group

import os
import time
import traceback

from dtntools.dtncla.udp import UdpRxSocket, UdpTxSocket
from dtntools.dtngen.blocks import (
    PayloadBlock,
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
    CTEBData,
    AdminRecordType,
    DispositionCode,
    CCSData,
    BundleSequenceCollection
)


# Networking Configuration: Please ensure you have port forwarding rules
BPNODE_IP = "172.17.0.1"
BPNODE_PORT = <%= dtnfsw_get_cla_in_port(target_name, 0) %>
LOCAL_IP = "0.0.0.0"
LOCAL_PORT = <%= dtnfsw_get_cla_out_port(target_name, 0) %>

class integration_test_bpnode_contact_ingress_01(Group):
    """
    Test Group
    """

    def test_bpnode_bundle_ingress_01(self):
        """
        Nominal test
        """

        # EID Configuration
        DEST_NODE_NUM = <%= $dtnfsw_globals_contact_0_dest_eid_node %>
        DEST_SERVICE_NUM = <%= $dtnfsw_globals_contact_0_dest_eid_service %>
        SRC_NODE_NUM = 300
        SRC_SERVICE_NUM = 1
        LOCAL_NODE_NUM =  <%= $dtnfsw_globals_channel_dest_eid_node %>

        LOCAL_EID = EID(
            {
                "uri": 2,
                "ssp": {
                    "node_num": LOCAL_NODE_NUM,
                    "service_num": 0
                }
            }
        )

        TEST_EID = EID (
            {
                "uri": 2,
                "ssp": {
                    "node_num": SRC_NODE_NUM,
                    "service_num": SRC_SERVICE_NUM
                }
            }
        )

        data_receiver = UdpRxSocket(LOCAL_IP, LOCAL_PORT)
        data_sender = UdpTxSocket(BPNODE_IP, BPNODE_PORT)

        # Prompt the user for a payload length, to add a little spice to the test
        # payload_length = ask("Enter a payload length, in bytes (min: 0, max: 3018, exception: 8):")
        # payload_length = int(payload_length)
        payload_length = 20
        payload_data = bytes([0xAA]*payload_length)

        og_cteb_data = CTEBData(
            {
                "bundle_seq_num": 10,
                "bundle_seq_id": 2,
                "block_src_admin_eid": EID({"uri": 2, "ssp": {"node_num": 400, "service_num": 42}})
            }
        )

        new_cteb_data = CTEBData (
            {
                "bundle_seq_num": 0,
                "bundle_seq_id": 1,
                "block_src_admin_eid": LOCAL_EID
            }
        )

        # Store the previous counter val, used to calculated expected/next value
        current_valid_custodial_count = tlm(f"<%= target_name %> BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_IN_CUSTODY")
        expected_valid_custodial_count = current_valid_custodial_count + 1

        current_generated_ccs  = tlm("<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_GENERATED_CCS")

        try:
            # Connect the data sender and receiver tools
            data_receiver.connect()
            data_sender.connect()

            encoded_input_bundle = bpnode_create_test_bundle_util(dest_node_num=DEST_NODE_NUM,
                                                            dest_service_num=DEST_SERVICE_NUM,
                                                            src_node_num=SRC_NODE_NUM,
                                                            src_service_num=SRC_SERVICE_NUM,
                                                            crc_type=CRCType.CRC16_X25,
                                                            prev_node_eid=None,
                                                            age=None,
                                                            hop_count=None,
                                                            cteb_data=og_cteb_data,
                                                            payload_bytes=payload_data
                                                            )

            expected_output_bundle = bpnode_create_test_bundle_util(dest_node_num=DEST_NODE_NUM,
                                                            dest_service_num=DEST_SERVICE_NUM,
                                                            src_node_num=SRC_NODE_NUM,
                                                            src_service_num=SRC_SERVICE_NUM,
                                                            crc_type=CRCType.CRC16_X25,
                                                            prev_node_eid=None,
                                                            age=None,
                                                            hop_count=None,
                                                            cteb_data=new_cteb_data,
                                                            payload_bytes=payload_data
                                                            )

            deserialized_input_bundle = Bundle.from_bytes(expected_output_bundle)

            print(f"Sending Bundle of {len(encoded_input_bundle)} bytes: {Bundle.from_bytes(encoded_input_bundle).to_json()}")
            data_sender.write(encoded_input_bundle)
            print("Waiting for bundle to be returned...")

            wait_check(f"<%= target_name %> BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_IN_CUSTODY == {expected_valid_custodial_count}", 10)

            looped_back_bundle = data_receiver.read()
            print(f"Received Bundle of {len(looped_back_bundle)} bytes: {Bundle.from_bytes(looped_back_bundle).to_json()}")

            received_bundle = Bundle.from_bytes(looped_back_bundle)

            primary_block = PrimaryBlock(
                            version=7,
                            control_flags=BundlePCFlags.IS_ADMIN_RECORD,
                            crc_type=CRCType.CRC16_X25,
                            dest_eid=EID({"uri": 2, "ssp": {"node_num": 100, "service_num": 0}}),
                            src_eid=EID({"uri": 2, "ssp": {"node_num": SRC_NODE_NUM, "service_num": SRC_SERVICE_NUM}}),
                            rpt_eid=EID({"uri": 2, "ssp": {"node_num": 600, "service_num": 0}}),
                            creation_timestamp=CreationTimestamp({"time": DtnTimeNowMs(), "sequence": 0}),
                            lifetime=3600000,
                            crc=CRCFlag.CALCULATE
            )

            ccs = AdminRecordBlock(
                blk_type=BlockType.AUTO,
                blk_num=1,
                control_flags=0,
                crc_type=CRCType.CRC16_X25,
                record_type = AdminRecordType.COMPRESSED_CUSTODY_SIGNAL,
                record_content = CCSData({
                    DispositionCode.CUSTODY_ACCEPTED: BundleSequenceCollection(
                                                bundle_seq_id=received_bundle.canon_blocks[0].cteb_data.bundle_seq_id,
                                                first_seq_num=received_bundle.canon_blocks[0].cteb_data.bundle_seq_num,
                                                bundle_seq_range=[1]),
                }),
                crc=CRCFlag.CALCULATE
            )

            ccs_bundle = Bundle(
                pri_block=primary_block,
                canon_blocks=[ccs],
            )

            # Send a CCS to complete custody transfer of bundle
            encoded_ccs = ccs_bundle.to_bytes()
            data_sender.write(encoded_ccs)

            # Since all blocks should be preserved, we can do these general checks first:
            check_expression(f"'{len(looped_back_bundle)}' == '{len(expected_output_bundle)}'")

            # Check primary block fields
            check_expression(f"{received_bundle.pri_block.version} == 7")
            check_expression(f"{received_bundle.pri_block.control_flags} == 4")
            check_expression(f"{received_bundle.pri_block.crc_type} == {CRCType.CRC16_X25}")
            check_expression(f"{received_bundle.pri_block.is_crc_valid()}")

            # the received EIDs should match what we sent in the original bundle.
            bpnode_check_eid_equality(received_bundle.pri_block.dest_eid, deserialized_input_bundle.pri_block.dest_eid)
            bpnode_check_eid_equality(received_bundle.pri_block.src_eid, deserialized_input_bundle.pri_block.src_eid)
            bpnode_check_eid_equality(received_bundle.pri_block.rpt_eid, deserialized_input_bundle.pri_block.rpt_eid)

            # Check the canonical blocks
            check_expression(f"{len(received_bundle.canon_blocks)} == 2")

            # Check the payload block
            check_expression(f"{received_bundle.canon_blocks[1].blk_type} == {BlockType.BUNDLE_PAYLOAD}")
            check_expression(f"{received_bundle.canon_blocks[1].is_crc_valid()}")

            # Check the custody transfer block
            custody_block = received_bundle.canon_blocks[0]
            check_expression(f'{custody_block.blk_type}                     == {BlockType.CUST_TRANS_EXT}')
            check_expression(f'{custody_block.blk_num}                      == 4')
            check_expression(f'{custody_block.crc_type}                     == {CRCType.CRC16_X25}')
            bpnode_check_eid_equality(custody_block.cteb_data.block_src_admin_eid, new_cteb_data.block_src_admin_eid)
            check_expression(f'{custody_block.is_crc_valid()}')

            expected_generated_ccs = current_generated_ccs + 1
        except KeyboardInterrupt:
            pass

        except Exception:
            print(traceback.format_exc())

        finally:
            # Wait for all pending CCSs to clear out
            wait_check(f"<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_GENERATED_CCS == {expected_generated_ccs}", 86)

            data_receiver.disconnect()
            data_sender.disconnect()


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
        pass
