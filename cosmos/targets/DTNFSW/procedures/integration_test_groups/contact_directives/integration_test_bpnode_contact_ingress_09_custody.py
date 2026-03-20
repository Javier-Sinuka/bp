from openc3.script.suite import Group

import os
import time
import traceback

from dtntools.dtncla.udp import UdpRxSocket, UdpTxSocket
from dtntools.dtngen.blocks import (
    AdminRecordBlock,
    PrimaryBlock,
    CustodyTransferBlock,
    PayloadBlock,
)
from dtntools.dtngen.bundle import Bundle
from dtntools.dtngen.types import (
    EID,
    BlockType,
    BundlePCFlags,
    BlockPCFlags,
    CRCFlag,
    DispositionCode,
    AdminRecordType,
    CCSData,
    BundleSequenceCollection,
    CRCType,
    CreationTimestamp,
    CTEBData,
)

# Networking Configuration: Please ensure you have port forwarding rules
BPNODE_IP   = "172.17.0.1"
BPNODE_PORT = 4501
LOCAL_IP    = "0.0.0.0"
LOCAL_PORT  = 4551

SEQ_ID  = 0
SEQ_NUM = 1

class integration_test_bpnode_contact_ingress_09(Group):
    """
    Test Group
    """

    def test_bpnode_custody01_ctebs_and_ccs(self):
        # EID Configuration
        SRC_NODE_NUM    = 100
        SRC_SERVICE_NUM = 0
        RPT_NODE_NUM    = 200
        RPT_SERVICE_NUM = 2

        data_receiver = UdpRxSocket(LOCAL_IP, LOCAL_PORT)
        data_sender   = UdpTxSocket(BPNODE_IP, BPNODE_PORT)

        # Get current tlm
        current_received_custody_signals = tlm("<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_CCS_RECEIVED")
        current_received_admin_records   = tlm("<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_RECEIVED_ADMIN_RECORD")
        current_custody_transferred      = tlm("<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_CUSTODY_TRANSFERRED")
        current_custody_rejected         = tlm("<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_CUSTODY_REJECTED")
        current_custodial_count          = tlm(f"<%= target_name %> BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_IN_CUSTODY")
        current_stored_count             = tlm(f"<%= target_name %> BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED")
        current_generated_ccs            = tlm("<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_GENERATED_CCS")

        try:
            # Connect the data sender and receiver tools
            data_receiver.connect()
            data_sender.connect()

            payload_block = PayloadBlock(
                blk_type=BlockType.AUTO,
                blk_num=1,
                control_flags=0,
                crc_type=CRCType.CRC16_X25,
                payload=bytes([0xAA] * 30),
                crc=CRCFlag.CALCULATE,
            )

            first_seq_num = 12
            first_seq_id  = 1
            num_seq_nums  = 4
            num_seq_ids   = 2
            midpoint      = int((num_seq_nums * num_seq_ids) / 2)

            cteb_seq_ids  = []
            cteb_seq_nums = []

            # Calculate expected telemetry
            expected_custodial_count = current_custodial_count + (num_seq_nums * num_seq_ids)
            expected_stored_count    = current_stored_count + (num_seq_nums * num_seq_ids)

            num_bundles = 0

            for seq_id_offset in range(num_seq_ids):
                for seq_num_offset in range(num_seq_nums):
                    primary_block = PrimaryBlock(
                                  version=7,
                                  control_flags=BundlePCFlags.MUST_NOT_FRAGMENT,
                                  crc_type=CRCType.CRC16_X25,
                                  dest_eid=EID({"uri": 2, "ssp": {"node_num": 200, "service_num": 64}}),
                                  src_eid=EID({"uri": 2, "ssp": {"node_num": SRC_NODE_NUM, "service_num": SRC_SERVICE_NUM}}),
                                  rpt_eid=EID({"uri": 2, "ssp": {"node_num": RPT_NODE_NUM, "service_num": RPT_SERVICE_NUM}}),
                                  creation_timestamp=CreationTimestamp({"time": DtnTimeNowMs(), "sequence": num_bundles}),
                                  lifetime=3600000,
                                  crc=CRCFlag.CALCULATE
                              )

                    prev_node_cte_block = CustodyTransferBlock(
                        blk_type=BlockType.AUTO,
                        blk_num=4,
                        control_flags=BlockPCFlags.REP_UNPROC,
                        crc_type=CRCType.CRC16_X25,
                        cteb_data=CTEBData(
                            {
                                "bundle_seq_num": first_seq_num + seq_num_offset,
                                "bundle_seq_id": first_seq_id + seq_id_offset,
                                "block_src_admin_eid": EID({"uri": 2, "ssp": {"node_num": 400, "service_num": 42}})
                            }
                        ),
                        crc=CRCFlag.CALCULATE,
                    )

                    cteb_bundle = Bundle(
                        pri_block=primary_block,
                        canon_blocks=[prev_node_cte_block, payload_block]
                    )

                    num_bundles += num_bundles

                    # Encode and send bundle with CTEB
                    encoded_input_bundle = cteb_bundle.to_bytes()
                    data_sender.write(encoded_input_bundle)

                    next_node_cteb        = data_receiver.read()
                    next_node_cteb_bundle = Bundle.from_bytes(next_node_cteb)

                    custody_block = next_node_cteb_bundle.canon_blocks[0]
                    cteb_seq_ids.append(custody_block.cteb_data.bundle_seq_id)
                    cteb_seq_nums.append(custody_block.cteb_data.bundle_seq_num)

            ctebs = [list(e) for e in list(zip(cteb_seq_ids, cteb_seq_nums))]

            wait_check(f"<%= target_name %> BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_IN_CUSTODY == {expected_custodial_count}", 10)
            wait_check(f"<%= target_name %> BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED == {expected_stored_count}", 10)

            primary_block.control_flags               = BundlePCFlags.IS_ADMIN_RECORD
            primary_block.dest_eid.ssp["node_num"]    = 100
            primary_block.dest_eid.ssp["service_num"] = 0

            # Accept bundles 0, 1, 2, 3
            # Reject bundles 4, 5, 6, 7
            num_accepted = 4
            num_rejected = 4

            next_node_ccs = AdminRecordBlock(
                blk_type=BlockType.AUTO,
                blk_num=1,
                control_flags=0,
                crc_type=CRCType.CRC16_X25,
                record_type = AdminRecordType.COMPRESSED_CUSTODY_SIGNAL,
                record_content = CCSData({
                    DispositionCode.CUSTODY_ACCEPTED: BundleSequenceCollection(
                                                bundle_seq_id=ctebs[0][SEQ_ID],
                                                first_seq_num=ctebs[0][SEQ_NUM],
                                                bundle_seq_range=[4]),
                    DispositionCode.CUSTODY_REFUSED: BundleSequenceCollection(
                                                bundle_seq_id=ctebs[midpoint][SEQ_ID],
                                                first_seq_num=ctebs[midpoint][SEQ_NUM],
                                                bundle_seq_range=[4])
                }),
                crc=CRCFlag.CALCULATE
            )

            ccs_bundle = Bundle(
                pri_block=primary_block,
                canon_blocks=[next_node_ccs],
            )

            # Encode and send CCS bundle
            encoded_input_bundle = ccs_bundle.to_bytes()
            data_sender.write(encoded_input_bundle)

            # Calculate expected telemetry
            expected_stored_count             -= num_accepted
            expected_custodial_count          -= num_accepted
            expected_received_custody_signals  = current_received_custody_signals + 1
            expected_received_admin_records    = current_received_admin_records   + 1
            expected_custody_transferred       = current_custody_transferred      + num_accepted
            expected_custody_rejected          = current_custody_rejected         + num_rejected

            # Wait for the expected results
            wait_check(f"<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_CCS_RECEIVED == {expected_received_custody_signals}", 10)
            wait_check(f"<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_RECEIVED_ADMIN_RECORD == {expected_received_admin_records}", 10)
            wait_check(f"<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_CUSTODY_TRANSFERRED == {expected_custody_transferred}", 10)
            wait_check(f"<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_CUSTODY_REJECTED == {expected_custody_rejected}", 10)
            wait_check(f"<%= target_name %> BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED == {expected_stored_count}", 10)
            wait_check(f"<%= target_name %> BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_IN_CUSTODY == {expected_custodial_count}", 10)

            expected_generated_ccs = current_generated_ccs + num_seq_ids
        except KeyboardInterrupt:
            pass

        except Exception:
            print(traceback.format_exc())

        finally:
            # Wait for all pending CCSs to clear out
            wait_check(f"<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_GENERATED_CCS == {expected_generated_ccs}", 86)

            # Accept rejected bundles to clear out bundles for next test
            next_node_ccs = AdminRecordBlock(
                blk_type=BlockType.AUTO,
                blk_num=1,
                control_flags=0,
                crc_type=CRCType.CRC16_X25,
                record_type = AdminRecordType.COMPRESSED_CUSTODY_SIGNAL,
                record_content = CCSData({
                    DispositionCode.CUSTODY_ACCEPTED: BundleSequenceCollection(
                                                bundle_seq_id=ctebs[midpoint][SEQ_ID],
                                                first_seq_num=ctebs[midpoint][SEQ_NUM],
                                                bundle_seq_range=[4]),
                }),
                crc=CRCFlag.CALCULATE
            )

            ccs_bundle = Bundle(
                pri_block=primary_block,
                canon_blocks=[next_node_ccs],
            )

            # Encode and send CCS bundle
            encoded_input_bundle = ccs_bundle.to_bytes()
            data_sender.write(encoded_input_bundle)

            wait_check(f"<%= target_name %> BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_IN_CUSTODY == 0", 10)
            wait_check(f"<%= target_name %> BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED == 0", 10)

            data_receiver.disconnect()
            data_sender.disconnect()


    def test_bpnode_custody02_missing_bundle_retransmit(self):
        # EID Configuration
        SRC_NODE_NUM    = 100
        SRC_SERVICE_NUM = 0
        RPT_NODE_NUM    = 200
        RPT_SERVICE_NUM = 2

        data_receiver = UdpRxSocket(LOCAL_IP, LOCAL_PORT)
        data_sender   = UdpTxSocket(BPNODE_IP, BPNODE_PORT)

        # Get current tlm
        current_received_custody_signals  = tlm("<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_CCS_RECEIVED")
        current_received_admin_records    = tlm("<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_RECEIVED_ADMIN_RECORD")
        current_custody_transferred       = tlm("<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_CUSTODY_TRANSFERRED")
        current_custody_rejected          = tlm("<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_CUSTODY_REJECTED")
        current_custodial_count           = tlm(f"<%= target_name %> BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_IN_CUSTODY")
        current_stored_count              = tlm(f"<%= target_name %> BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED")
        current_reforward_count           = tlm(f"<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_CUSTODY_RE_FORWARDED")
        current_generated_ccs             = tlm("<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_GENERATED_CCS")

        try:
            # Connect the data sender and receiver tools
            data_receiver.connect()
            data_sender.connect()

            payload_block = PayloadBlock(
                blk_type=BlockType.AUTO,
                blk_num=1,
                control_flags=0,
                crc_type=CRCType.CRC16_X25,
                payload=bytes([0xAA] * 30),
                crc=CRCFlag.CALCULATE,
            )

            first_seq_num = 16
            first_seq_id  = 3
            num_seq_nums  = 4
            num_seq_ids   = 2
            midpoint      = int((num_seq_nums * num_seq_ids) / 2)

            cteb_seq_ids  = []
            cteb_seq_nums = []

            # Calculate expected telemetry
            expected_custodial_count = current_custodial_count + (num_seq_nums * num_seq_ids)
            expected_stored_count    = current_stored_count + (num_seq_nums * num_seq_ids)

            num_bundles = 0

            for seq_id_offset in range(num_seq_ids):
                for seq_num_offset in range(num_seq_nums):
                    primary_block = PrimaryBlock(
                                  version=7,
                                  control_flags=BundlePCFlags.MUST_NOT_FRAGMENT,
                                  crc_type=CRCType.CRC16_X25,
                                  dest_eid=EID({"uri": 2, "ssp": {"node_num": 200, "service_num": 64}}),
                                  src_eid=EID({"uri": 2, "ssp": {"node_num": SRC_NODE_NUM, "service_num": SRC_SERVICE_NUM}}),
                                  rpt_eid=EID({"uri": 2, "ssp": {"node_num": RPT_NODE_NUM, "service_num": RPT_SERVICE_NUM}}),
                                  creation_timestamp=CreationTimestamp({"time": DtnTimeNowMs(), "sequence": num_bundles}),
                                  lifetime=3600000,
                                  crc=CRCFlag.CALCULATE
                              )

                    prev_node_cte_block = CustodyTransferBlock(
                        blk_type=BlockType.AUTO,
                        blk_num=4,
                        control_flags=BlockPCFlags.REP_UNPROC,
                        crc_type=CRCType.CRC16_X25,
                        cteb_data=CTEBData(
                            {
                                "bundle_seq_num": first_seq_num + seq_num_offset,
                                "bundle_seq_id": first_seq_id + seq_id_offset,
                                "block_src_admin_eid": EID({"uri": 2, "ssp": {"node_num": 400, "service_num": 42}})
                            }
                        ),
                        crc=CRCFlag.CALCULATE,
                    )

                    cteb_bundle = Bundle(
                        pri_block=primary_block,
                        canon_blocks=[prev_node_cte_block, payload_block]
                    )

                    num_bundles += num_bundles

                    # Encode and send bundle with CTEB
                    encoded_input_bundle = cteb_bundle.to_bytes()
                    data_sender.write(encoded_input_bundle)

                    next_node_cteb        = data_receiver.read()
                    next_node_cteb_bundle = Bundle.from_bytes(next_node_cteb)

                    custody_block = next_node_cteb_bundle.canon_blocks[0]
                    cteb_seq_ids.append(custody_block.cteb_data.bundle_seq_id)
                    cteb_seq_nums.append(custody_block.cteb_data.bundle_seq_num)

            wait_check(f"<%= target_name %> BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_IN_CUSTODY == {expected_custodial_count}", 10)
            wait_check(f"<%= target_name %> BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED == {expected_stored_count}", 10)

            ctebs = [list(e) for e in list(zip(cteb_seq_ids, cteb_seq_nums))]

            primary_block.control_flags               = BundlePCFlags.IS_ADMIN_RECORD
            primary_block.dest_eid.ssp["node_num"]    = 100
            primary_block.dest_eid.ssp["service_num"] = 0

            # Accept bundles 0, 1, 3
            # Reject bundles 4, 5, 6, 7
            # Bundle 2 should be automatically retransmitted

            missing_bundle_seq_num = ctebs[2][SEQ_NUM]
            num_accepted = 3
            num_rejected = 4

            next_node_ccs = AdminRecordBlock(
                blk_type=BlockType.AUTO,
                blk_num=1,
                control_flags=0,
                crc_type=CRCType.CRC16_X25,
                record_type = AdminRecordType.COMPRESSED_CUSTODY_SIGNAL,
                record_content = CCSData({
                    DispositionCode.CUSTODY_ACCEPTED: BundleSequenceCollection(
                                                bundle_seq_id=ctebs[0][SEQ_ID],
                                                first_seq_num=ctebs[0][SEQ_NUM],
                                                bundle_seq_range=[2, 1, 1]),
                    DispositionCode.CUSTODY_REFUSED: BundleSequenceCollection(
                                                bundle_seq_id=ctebs[midpoint][SEQ_ID],
                                                first_seq_num=ctebs[midpoint][SEQ_NUM],
                                                bundle_seq_range=[4])
                }),
                crc=CRCFlag.CALCULATE
            )

            ccs_bundle = Bundle(
                pri_block=primary_block,
                canon_blocks=[next_node_ccs],
            )

            # Encode and send CCS bundle
            encoded_input_bundle = ccs_bundle.to_bytes()
            data_sender.write(encoded_input_bundle)

            # Calculate expected telemetry
            expected_stored_count             -= num_accepted
            expected_custodial_count          -= num_accepted
            expected_received_custody_signals  = current_received_custody_signals + 1
            expected_received_admin_records    = current_received_admin_records   + 1
            expected_custody_transferred       = current_custody_transferred      + num_accepted
            expected_custody_rejected          = current_custody_rejected         + num_rejected

            # Wait for the expected results
            wait_check(f"<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_CCS_RECEIVED == {expected_received_custody_signals}", 10)
            wait_check(f"<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_RECEIVED_ADMIN_RECORD == {expected_received_admin_records}", 10)
            wait_check(f"<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_CUSTODY_TRANSFERRED == {expected_custody_transferred}", 10)
            wait_check(f"<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_CUSTODY_REJECTED == {expected_custody_rejected}", 10)
            wait_check(f"<%= target_name %> BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED == {expected_stored_count}", 10)
            wait_check(f"<%= target_name %> BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_IN_CUSTODY == {expected_custodial_count}", 10)

            # At this point the missing bundle should be automatically retransmitted
            # Check for it and send a CCS to accept it

            bundle = data_receiver.read()
            missing_bundle = Bundle.from_bytes(bundle)

            check_expression(f"{missing_bundle.canon_blocks[0].cteb_data.bundle_seq_num} == {missing_bundle_seq_num}")

            next_node_ccs = AdminRecordBlock(
                blk_type=BlockType.AUTO,
                blk_num=1,
                control_flags=0,
                crc_type=CRCType.CRC16_X25,
                record_type = AdminRecordType.COMPRESSED_CUSTODY_SIGNAL,
                record_content = CCSData({
                    DispositionCode.CUSTODY_ACCEPTED: BundleSequenceCollection(
                                                bundle_seq_id=ctebs[0][SEQ_ID],
                                                first_seq_num=missing_bundle_seq_num,
                                                bundle_seq_range=[1])
                }),
                crc=CRCFlag.CALCULATE
            )

            ccs_bundle = Bundle(
                pri_block=primary_block,
                canon_blocks=[next_node_ccs],
            )

            num_accepted = 1

            # Encode and send CCS bundle
            encoded_input_bundle = ccs_bundle.to_bytes()
            data_sender.write(encoded_input_bundle)

            # Calculate expected telemetry
            expected_stored_count             -= num_accepted
            expected_custodial_count          -= num_accepted
            expected_received_custody_signals += 1
            expected_received_admin_records   += 1
            expected_custody_transferred      += 1
            expected_reforwarded               = current_reforward_count + 1

            # Wait for the expected results
            wait_check(f"<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_CCS_RECEIVED == {expected_received_custody_signals}", 10)
            wait_check(f"<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_RECEIVED_ADMIN_RECORD == {expected_received_admin_records}", 10)
            wait_check(f"<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_CUSTODY_TRANSFERRED == {expected_custody_transferred}", 10)
            wait_check(f"<%= target_name %> BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED == {expected_stored_count}", 10)
            wait_check(f"<%= target_name %> BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_IN_CUSTODY == {expected_custodial_count}", 10)
            wait_check(f"<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_CUSTODY_RE_FORWARDED == {expected_reforwarded}", 10)

            expected_generated_ccs = current_generated_ccs + num_seq_ids
        except KeyboardInterrupt:
            pass

        except Exception:
            print(traceback.format_exc())

        finally:
            # Wait for all pending CCSs to clear out
            wait_check(f"<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_GENERATED_CCS == {expected_generated_ccs}", 86)

            # Accept rejected bundles to clear out bundles for next test
            next_node_ccs = AdminRecordBlock(
                blk_type=BlockType.AUTO,
                blk_num=1,
                control_flags=0,
                crc_type=CRCType.CRC16_X25,
                record_type = AdminRecordType.COMPRESSED_CUSTODY_SIGNAL,
                record_content = CCSData({
                    DispositionCode.CUSTODY_ACCEPTED: BundleSequenceCollection(
                                                bundle_seq_id=ctebs[midpoint][SEQ_ID],
                                                first_seq_num=ctebs[midpoint][SEQ_NUM],
                                                bundle_seq_range=[4]),
                }),
                crc=CRCFlag.CALCULATE
            )

            ccs_bundle = Bundle(
                pri_block=primary_block,
                canon_blocks=[next_node_ccs],
            )

            # Encode and send CCS bundle
            encoded_input_bundle = ccs_bundle.to_bytes()
            data_sender.write(encoded_input_bundle)

            wait_check(f"<%= target_name %> BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_IN_CUSTODY == 0", 10)
            wait_check(f"<%= target_name %> BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED == 0", 10)

            data_receiver.disconnect()
            data_sender.disconnect()


    def test_bpnode_custody03_missing_bundle_retransmit_timeout(self):
        # EID Configuration
        SRC_NODE_NUM    = 100
        SRC_SERVICE_NUM = 0
        RPT_NODE_NUM    = 200
        RPT_SERVICE_NUM = 2

        data_receiver = UdpRxSocket(LOCAL_IP, LOCAL_PORT)
        data_sender   = UdpTxSocket(BPNODE_IP, BPNODE_PORT)

        # Get current tlm
        current_received_custody_signals  = tlm("<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_CCS_RECEIVED")
        current_received_admin_records    = tlm("<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_RECEIVED_ADMIN_RECORD")
        current_custody_transferred       = tlm("<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_CUSTODY_TRANSFERRED")
        current_custody_rejected          = tlm("<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_CUSTODY_REJECTED")
        current_custodial_count           = tlm(f"<%= target_name %> BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_IN_CUSTODY")
        current_stored_count              = tlm(f"<%= target_name %> BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED")
        current_reforward_count           = tlm(f"<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_CUSTODY_RE_FORWARDED")
        current_generated_ccs             = tlm("<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_GENERATED_CCS")

        try:
            # Connect the data sender and receiver tools
            data_receiver.connect()
            data_sender.connect()

            payload_block = PayloadBlock(
                blk_type=BlockType.AUTO,
                blk_num=1,
                control_flags=0,
                crc_type=CRCType.CRC16_X25,
                payload=bytes([0xAA] * 30),
                crc=CRCFlag.CALCULATE,
            )

            first_seq_num = 20
            first_seq_id  = 5
            num_seq_nums  = 4
            num_seq_ids   = 2
            midpoint      = int((num_seq_nums * num_seq_ids) / 2)

            cteb_seq_ids  = []
            cteb_seq_nums = []

            # Calculate expected telemetry
            expected_custodial_count = current_custodial_count + (num_seq_nums * num_seq_ids)
            expected_stored_count    = current_stored_count    + (num_seq_nums * num_seq_ids)

            num_bundles = 0

            for seq_id_offset in range(num_seq_ids):
                for seq_num_offset in range(num_seq_nums):
                    primary_block = PrimaryBlock(
                                  version=7,
                                  control_flags=BundlePCFlags.MUST_NOT_FRAGMENT,
                                  crc_type=CRCType.CRC16_X25,
                                  dest_eid=EID({"uri": 2, "ssp": {"node_num": 200, "service_num": 64}}),
                                  src_eid=EID({"uri": 2, "ssp": {"node_num": SRC_NODE_NUM, "service_num": SRC_SERVICE_NUM}}),
                                  rpt_eid=EID({"uri": 2, "ssp": {"node_num": RPT_NODE_NUM, "service_num": RPT_SERVICE_NUM}}),
                                  creation_timestamp=CreationTimestamp({"time": DtnTimeNowMs(), "sequence": num_bundles}),
                                  lifetime=3600000,
                                  crc=CRCFlag.CALCULATE
                              )

                    prev_node_cte_block = CustodyTransferBlock(
                        blk_type=BlockType.AUTO,
                        blk_num=4,
                        control_flags=BlockPCFlags.REP_UNPROC,
                        crc_type=CRCType.CRC16_X25,
                        cteb_data=CTEBData(
                            {
                                "bundle_seq_num": first_seq_num + seq_num_offset,
                                "bundle_seq_id": first_seq_id + seq_id_offset,
                                "block_src_admin_eid": EID({"uri": 2, "ssp": {"node_num": 400, "service_num": 42}})
                            }
                        ),
                        crc=CRCFlag.CALCULATE,
                    )

                    cteb_bundle = Bundle(
                        pri_block=primary_block,
                        canon_blocks=[prev_node_cte_block, payload_block]
                    )

                    num_bundles += num_bundles

                    # Encode and send bundle with CTEB
                    encoded_input_bundle = cteb_bundle.to_bytes()
                    data_sender.write(encoded_input_bundle)

                    next_node_cteb        = data_receiver.read()
                    next_node_cteb_bundle = Bundle.from_bytes(next_node_cteb)

                    custody_block = next_node_cteb_bundle.canon_blocks[0]
                    cteb_seq_ids.append(custody_block.cteb_data.bundle_seq_id)
                    cteb_seq_nums.append(custody_block.cteb_data.bundle_seq_num)

            wait_check(f"<%= target_name %> BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_IN_CUSTODY == {expected_custodial_count}", 10)
            wait_check(f"<%= target_name %> BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED == {expected_stored_count}", 10)

            ctebs = [list(e) for e in list(zip(cteb_seq_ids, cteb_seq_nums))]

            primary_block.control_flags               = BundlePCFlags.IS_ADMIN_RECORD
            primary_block.dest_eid.ssp["node_num"]    = 100
            primary_block.dest_eid.ssp["service_num"] = 0

            # Accept bundles 0, 1, 2, 3
            # Reject bundles 4, 5, 6
            # Bundle 7 should be retransmitted after timeout passes

            timeout_bundle_seq_num = ctebs[7][SEQ_NUM]
            num_accepted = 4
            num_rejected = 3

            next_node_ccs = AdminRecordBlock(
                blk_type=BlockType.AUTO,
                blk_num=1,
                control_flags=0,
                crc_type=CRCType.CRC16_X25,
                record_type = AdminRecordType.COMPRESSED_CUSTODY_SIGNAL,
                record_content = CCSData({
                    DispositionCode.CUSTODY_ACCEPTED: BundleSequenceCollection(
                                                bundle_seq_id=ctebs[0][SEQ_ID],
                                                first_seq_num=ctebs[0][SEQ_NUM],
                                                bundle_seq_range=[4]),
                    DispositionCode.CUSTODY_REFUSED: BundleSequenceCollection(
                                                bundle_seq_id=ctebs[midpoint][SEQ_ID],
                                                first_seq_num=ctebs[midpoint][SEQ_NUM],
                                                bundle_seq_range=[3])
                }),
                crc=CRCFlag.CALCULATE
            )

            ccs_bundle = Bundle(
                pri_block=primary_block,
                canon_blocks=[next_node_ccs],
            )

            # Encode and send CCS bundle
            encoded_input_bundle = ccs_bundle.to_bytes()
            data_sender.write(encoded_input_bundle)

            # Calculate expected telemetry
            expected_stored_count             -= num_accepted
            expected_custodial_count          -= num_accepted
            expected_received_custody_signals  = current_received_custody_signals + 1
            expected_received_admin_records    = current_received_admin_records   + 1
            expected_custody_transferred       = current_custody_transferred      + num_accepted
            expected_custody_rejected          = current_custody_rejected         + num_rejected

            # Wait for the expected results
            wait_check(f"<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_CCS_RECEIVED == {expected_received_custody_signals}", 10)
            wait_check(f"<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_RECEIVED_ADMIN_RECORD == {expected_received_admin_records}", 10)
            wait_check(f"<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_CUSTODY_TRANSFERRED == {expected_custody_transferred}", 10)
            wait_check(f"<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_CUSTODY_REJECTED == {expected_custody_rejected}", 10)
            wait_check(f"<%= target_name %> BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED == {expected_stored_count}", 10)
            wait_check(f"<%= target_name %> BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_IN_CUSTODY == {expected_custodial_count}", 10)

            # Now wait for the retransmit timer to expire and trigger the retransmission
            # of the final missing bundle (this may take a minute). Accept it to remove
            # it from storage.
            bundle         = data_receiver.read()
            missing_bundle = Bundle.from_bytes(bundle)

            check_expression(f"{missing_bundle.canon_blocks[0].cteb_data.bundle_seq_num} == {timeout_bundle_seq_num}")

            next_node_ccs = AdminRecordBlock(
                blk_type=BlockType.AUTO,
                blk_num=1,
                control_flags=0,
                crc_type=CRCType.CRC16_X25,
                record_type = AdminRecordType.COMPRESSED_CUSTODY_SIGNAL,
                record_content = CCSData({
                    DispositionCode.CUSTODY_ACCEPTED: BundleSequenceCollection(
                                                bundle_seq_id=ctebs[0][SEQ_ID],
                                                first_seq_num=timeout_bundle_seq_num,
                                                bundle_seq_range=[1])
                }),
                crc=CRCFlag.CALCULATE
            )

            ccs_bundle = Bundle(
                pri_block=primary_block,
                canon_blocks=[next_node_ccs],
            )

            num_accepted = 1

            # Encode and send CCS bundle
            encoded_input_bundle = ccs_bundle.to_bytes()
            data_sender.write(encoded_input_bundle)

            # Calculate expected telemetry
            expected_stored_count             -= num_accepted
            expected_custodial_count          -= num_accepted
            expected_received_custody_signals += 1
            expected_received_admin_records   += 1
            expected_custody_transferred      += 1
            expected_reforwarded               = current_reforward_count + 1

            # Wait for the expected results
            wait_check(f"<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_CCS_RECEIVED == {expected_received_custody_signals}", 10)
            wait_check(f"<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_RECEIVED_ADMIN_RECORD == {expected_received_admin_records}", 10)
            wait_check(f"<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_CUSTODY_TRANSFERRED == {expected_custody_transferred}", 10)
            wait_check(f"<%= target_name %> BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED == {expected_stored_count}", 10)
            wait_check(f"<%= target_name %> BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_IN_CUSTODY == {expected_custodial_count}", 10)
            wait_check(f"<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_CUSTODY_RE_FORWARDED == {expected_reforwarded}", 10)

            expected_generated_ccs = current_generated_ccs + num_seq_ids
        except KeyboardInterrupt:
            pass

        except Exception:
            print(traceback.format_exc())

        finally:
            # Wait for all pending CCSs to clear out
            wait_check(f"<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_GENERATED_CCS == {expected_generated_ccs}", 86)

            # Accept rejected bundles to clear out bundles for next test
            next_node_ccs = AdminRecordBlock(
                blk_type=BlockType.AUTO,
                blk_num=1,
                control_flags=0,
                crc_type=CRCType.CRC16_X25,
                record_type = AdminRecordType.COMPRESSED_CUSTODY_SIGNAL,
                record_content = CCSData({
                    DispositionCode.CUSTODY_ACCEPTED: BundleSequenceCollection(
                                                bundle_seq_id=ctebs[midpoint][SEQ_ID],
                                                first_seq_num=ctebs[midpoint][SEQ_NUM],
                                                bundle_seq_range=[3]),
                }),
                crc=CRCFlag.CALCULATE
            )

            ccs_bundle = Bundle(
                pri_block=primary_block,
                canon_blocks=[next_node_ccs],
            )

            # Encode and send CCS bundle
            encoded_input_bundle = ccs_bundle.to_bytes()
            data_sender.write(encoded_input_bundle)

            wait_check(f"<%= target_name %> BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_IN_CUSTODY == 0", 10)
            wait_check(f"<%= target_name %> BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED == 0", 10)

            data_receiver.disconnect()
            data_sender.disconnect()


    def test_bpnode_custody04_retransmit_rejected_bundles(self):
        # ATTN: Contact 1 needs to be started up for the CCSs generated by the
        #       contact stop directive to be sent to the correct location

        # EID Configuration
        SRC_NODE_NUM    = 100
        SRC_SERVICE_NUM = 0
        RPT_NODE_NUM    = 200
        RPT_SERVICE_NUM = 2

        data_receiver = UdpRxSocket(LOCAL_IP, LOCAL_PORT)
        data_sender   = UdpTxSocket(BPNODE_IP, BPNODE_PORT)

        # Get current tlm
        current_received_custody_signals  = tlm("<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_CCS_RECEIVED")
        current_received_admin_records    = tlm("<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_RECEIVED_ADMIN_RECORD")
        current_custody_transferred       = tlm("<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_CUSTODY_TRANSFERRED")
        current_custody_rejected          = tlm("<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_CUSTODY_REJECTED")
        current_custodial_count           = tlm(f"<%= target_name %> BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_IN_CUSTODY")
        current_stored_count              = tlm(f"<%= target_name %> BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED")
        current_reforward_count           = tlm(f"<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_CUSTODY_RE_FORWARDED")

        try:
            # Connect the data sender and receiver tools
            data_receiver.connect()
            data_sender.connect()

            payload_block = PayloadBlock(
                blk_type=BlockType.AUTO,
                blk_num=1,
                control_flags=0,
                crc_type=CRCType.CRC16_X25,
                payload=bytes([0xAA] * 30),
                crc=CRCFlag.CALCULATE,
            )

            first_seq_num = 24
            first_seq_id  = 7
            num_seq_nums  = 4
            num_seq_ids   = 2
            midpoint      = int((num_seq_nums * num_seq_ids) / 2)

            cteb_seq_ids  = []
            cteb_seq_nums = []

            # Calculate expected telemetry
            expected_custodial_count = current_custodial_count + (num_seq_nums * num_seq_ids)
            expected_stored_count    = current_stored_count    + (num_seq_nums * num_seq_ids)

            num_bundles = 0

            for seq_id_offset in range(num_seq_ids):
                for seq_num_offset in range(num_seq_nums):
                    primary_block = PrimaryBlock(
                                  version=7,
                                  control_flags=BundlePCFlags.MUST_NOT_FRAGMENT,
                                  crc_type=CRCType.CRC16_X25,
                                  dest_eid=EID({"uri": 2, "ssp": {"node_num": 200, "service_num": 64}}),
                                  src_eid=EID({"uri": 2, "ssp": {"node_num": SRC_NODE_NUM, "service_num": SRC_SERVICE_NUM}}),
                                  rpt_eid=EID({"uri": 2, "ssp": {"node_num": RPT_NODE_NUM, "service_num": RPT_SERVICE_NUM}}),
                                  creation_timestamp=CreationTimestamp({"time": DtnTimeNowMs(), "sequence": num_bundles}),
                                  lifetime=3600000,
                                  crc=CRCFlag.CALCULATE
                              )

                    prev_node_cte_block = CustodyTransferBlock(
                        blk_type=BlockType.AUTO,
                        blk_num=4,
                        control_flags=BlockPCFlags.REP_UNPROC,
                        crc_type=CRCType.CRC16_X25,
                        cteb_data=CTEBData(
                            {
                                "bundle_seq_num": first_seq_num + seq_num_offset,
                                "bundle_seq_id": first_seq_id + seq_id_offset,
                                "block_src_admin_eid": EID({"uri": 2, "ssp": {"node_num": 400, "service_num": 42}})
                            }
                        ),
                        crc=CRCFlag.CALCULATE,
                    )

                    cteb_bundle = Bundle(
                        pri_block=primary_block,
                        canon_blocks=[prev_node_cte_block, payload_block]
                    )

                    num_bundles += num_bundles

                    # Encode and send bundle with CTEB
                    encoded_input_bundle = cteb_bundle.to_bytes()
                    data_sender.write(encoded_input_bundle)

                    next_node_cteb        = data_receiver.read()
                    next_node_cteb_bundle = Bundle.from_bytes(next_node_cteb)

                    custody_block = next_node_cteb_bundle.canon_blocks[0]
                    cteb_seq_ids.append(custody_block.cteb_data.bundle_seq_id)
                    cteb_seq_nums.append(custody_block.cteb_data.bundle_seq_num)

            wait_check(f"<%= target_name %> BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_IN_CUSTODY == {expected_custodial_count}", 10)
            wait_check(f"<%= target_name %> BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED == {expected_stored_count}", 10)

            ctebs = [list(e) for e in list(zip(cteb_seq_ids, cteb_seq_nums))]

            primary_block.control_flags               = BundlePCFlags.IS_ADMIN_RECORD
            primary_block.dest_eid.ssp["node_num"]    = 100
            primary_block.dest_eid.ssp["service_num"] = 0

            # Accept bundles 0, 1, 2, 3
            # Reject bundles 4, 5, 6, 7

            num_accepted = 4
            num_rejected = 4

            next_node_ccs = AdminRecordBlock(
                blk_type=BlockType.AUTO,
                blk_num=1,
                control_flags=0,
                crc_type=CRCType.CRC16_X25,
                record_type = AdminRecordType.COMPRESSED_CUSTODY_SIGNAL,
                record_content = CCSData({
                    DispositionCode.CUSTODY_ACCEPTED: BundleSequenceCollection(
                                                bundle_seq_id=ctebs[0][SEQ_ID],
                                                first_seq_num=ctebs[0][SEQ_NUM],
                                                bundle_seq_range=[4]),
                    DispositionCode.CUSTODY_REFUSED: BundleSequenceCollection(
                                                bundle_seq_id=ctebs[midpoint][SEQ_ID],
                                                first_seq_num=ctebs[midpoint][SEQ_NUM],
                                                bundle_seq_range=[4])
                }),
                crc=CRCFlag.CALCULATE
            )

            ccs_bundle = Bundle(
                pri_block=primary_block,
                canon_blocks=[next_node_ccs],
            )

            # Encode and send CCS bundle
            encoded_input_bundle = ccs_bundle.to_bytes()
            data_sender.write(encoded_input_bundle)

            # Calculate expected telemetry
            expected_stored_count             -= num_accepted
            expected_custodial_count          -= num_accepted
            expected_received_custody_signals  = current_received_custody_signals + 1
            expected_received_admin_records    = current_received_admin_records   + 1
            expected_custody_transferred       = current_custody_transferred      + num_accepted
            expected_custody_rejected          = current_custody_rejected         + num_rejected

            # Wait for the expected results
            wait_check(f"<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_CCS_RECEIVED == {expected_received_custody_signals}", 10)
            wait_check(f"<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_RECEIVED_ADMIN_RECORD == {expected_received_admin_records}", 10)
            wait_check(f"<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_CUSTODY_TRANSFERRED == {expected_custody_transferred}", 10)
            wait_check(f"<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_CUSTODY_REJECTED == {expected_custody_rejected}", 10)
            wait_check(f"<%= target_name %> BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED == {expected_stored_count}", 10)
            wait_check(f"<%= target_name %> BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_IN_CUSTODY == {expected_custodial_count}", 10)

            # Now restart contact 0 to restart the retransmission timers for the
            # rejected bundles remaining in storage. This may take a minute until
            # the retransmission timers expire.

            cmd(f'<%= target_name %> BPNODE_CMD_CONTACT_STOP with CONTACT_ID 0')
            wait_check(f'<%= target_name %> BPNODE_CHAN_CON_STAT_HK CON_STAT_RUN_STATE_0 == "STOPPED"', 10)

            cmd(f'<%= target_name %> BPNODE_CMD_CONTACT_TEARDOWN with CONTACT_ID 0')
            wait_check(f'<%= target_name %> BPNODE_CHAN_CON_STAT_HK CON_STAT_RUN_STATE_0 == "TORNDOWN"', 10)

            cmd(f'<%= target_name %> BPNODE_CMD_CONTACT_SETUP with CONTACT_ID 0')
            wait_check(f'<%= target_name %> BPNODE_CHAN_CON_STAT_HK CON_STAT_RUN_STATE_0 == "SETUP"', 10)

            cmd(f'<%= target_name %> BPNODE_CMD_CONTACT_START with CONTACT_ID 0')
            wait_check(f'<%= target_name %> BPNODE_CHAN_CON_STAT_HK CON_STAT_RUN_STATE_0 == "STARTED"', 10)

            for missing_seq_num in range(ctebs[midpoint][SEQ_NUM], ctebs[midpoint][SEQ_NUM] + num_rejected):
                # This may take a minute
                bundle = data_receiver.read()
                missing_bundle = Bundle.from_bytes(bundle)

                check_expression(f"{missing_bundle.canon_blocks[0].cteb_data.bundle_seq_num} == {missing_seq_num}")

            next_node_ccs = AdminRecordBlock(
                blk_type=BlockType.AUTO,
                blk_num=1,
                control_flags=0,
                crc_type=CRCType.CRC16_X25,
                record_type = AdminRecordType.COMPRESSED_CUSTODY_SIGNAL,
                record_content = CCSData({
                    DispositionCode.CUSTODY_ACCEPTED: BundleSequenceCollection(
                                                bundle_seq_id=ctebs[0][SEQ_ID],
                                                first_seq_num=ctebs[midpoint][SEQ_NUM],
                                                bundle_seq_range=[num_rejected])
                }),
                crc=CRCFlag.CALCULATE
            )

            ccs_bundle = Bundle(
                pri_block=primary_block,
                canon_blocks=[next_node_ccs],
            )

            num_accepted = num_rejected

            # Encode and send CCS bundle
            encoded_input_bundle = ccs_bundle.to_bytes()
            data_sender.write(encoded_input_bundle)

            # Calculate expected telemetry
            expected_stored_count             -= num_accepted
            expected_custodial_count          -= num_accepted
            expected_received_custody_signals += 1
            expected_received_admin_records   += 1
            expected_custody_transferred      += num_accepted
            expected_reforwarded               = current_reforward_count + num_accepted

            # Wait for the expected results
            wait_check(f"<%= target_name %> BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_IN_CUSTODY == {expected_custodial_count}", 10)
            wait_check(f"<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_CCS_RECEIVED == {expected_received_custody_signals}", 10)
            wait_check(f"<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_RECEIVED_ADMIN_RECORD == {expected_received_admin_records}", 10)
            wait_check(f"<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_CUSTODY_TRANSFERRED == {expected_custody_transferred}", 10)
            wait_check(f"<%= target_name %> BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED == {expected_stored_count}", 10)
            wait_check(f"<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_CUSTODY_RE_FORWARDED == {expected_reforwarded}", 10)

        except KeyboardInterrupt:
            pass

        except Exception:
            print(traceback.format_exc())

        finally:
            # No CCSs expected since CONTACT_STOP command sends them and no new bundles are created

            wait_check(f"<%= target_name %> BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_IN_CUSTODY == 0", 10)
            wait_check(f"<%= target_name %> BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED == 0", 10)

            data_receiver.disconnect()
            data_sender.disconnect()


    def test_bpnode_custody05_ccs_timeout(self):
        # EID Configuration
        SRC_NODE_NUM    = 100
        SRC_SERVICE_NUM = 0
        RPT_NODE_NUM    = 200
        RPT_SERVICE_NUM = 2

        data_receiver = UdpRxSocket(LOCAL_IP, LOCAL_PORT)
        data_sender   = UdpTxSocket(BPNODE_IP, BPNODE_PORT)

        # Get current tlm
        current_custodial_count = tlm(f"<%= target_name %> BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_IN_CUSTODY")
        current_stored_count    = tlm(f"<%= target_name %> BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED")
        current_generated_ccs   = tlm("<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_GENERATED_CCS")

        try:
            # Connect the data sender and receiver tools
            data_receiver.connect()
            data_sender.connect()

            payload_block = PayloadBlock(
                blk_type=BlockType.AUTO,
                blk_num=1,
                control_flags=0,
                crc_type=CRCType.CRC16_X25,
                payload=bytes([0xAA] * 30),
                crc=CRCFlag.CALCULATE,
            )

            first_seq_num = 30
            first_seq_id  = 9
            num_seq_nums  = 4
            num_seq_ids   = 2

            # Calculate expected telemetry
            expected_custodial_count = current_custodial_count + (num_seq_nums * num_seq_ids)
            expected_stored_count    = current_stored_count    + (num_seq_nums * num_seq_ids)

            num_bundles = 0

            cteb_seq_ids  = []
            cteb_seq_nums = []
            for seq_id_offset in range(num_seq_ids):
                for seq_num_offset in range(num_seq_nums):
                    primary_block = PrimaryBlock(
                                  version=7,
                                  control_flags=BundlePCFlags.MUST_NOT_FRAGMENT,
                                  crc_type=CRCType.CRC16_X25,
                                  dest_eid=EID({"uri": 2, "ssp": {"node_num": 200, "service_num": 64}}),
                                  src_eid=EID({"uri": 2, "ssp": {"node_num": SRC_NODE_NUM, "service_num": SRC_SERVICE_NUM}}),
                                  rpt_eid=EID({"uri": 2, "ssp": {"node_num": RPT_NODE_NUM, "service_num": RPT_SERVICE_NUM}}),
                                  creation_timestamp=CreationTimestamp({"time": DtnTimeNowMs(), "sequence": num_bundles}),
                                  lifetime=3600000,
                                  crc=CRCFlag.CALCULATE
                              )

                    prev_node_cte_block = CustodyTransferBlock(
                        blk_type=BlockType.AUTO,
                        blk_num=4,
                        control_flags=BlockPCFlags.REP_UNPROC,
                        crc_type=CRCType.CRC16_X25,
                        cteb_data=CTEBData(
                            {
                                "bundle_seq_num": first_seq_num + seq_num_offset,
                                "bundle_seq_id": first_seq_id + seq_id_offset,
                                "block_src_admin_eid": EID({"uri": 2, "ssp": {"node_num": 400, "service_num": 42}})
                            }
                        ),
                        crc=CRCFlag.CALCULATE,
                    )

                    cteb_bundle = Bundle(
                        pri_block=primary_block,
                        canon_blocks=[prev_node_cte_block, payload_block]
                    )

                    num_bundles += num_bundles

                    # Encode and send bundle with CTEB
                    encoded_input_bundle = cteb_bundle.to_bytes()
                    data_sender.write(encoded_input_bundle)

                    next_node_cteb        = data_receiver.read()
                    next_node_cteb_bundle = Bundle.from_bytes(next_node_cteb)

                    custody_block = next_node_cteb_bundle.canon_blocks[0]
                    cteb_seq_ids.append(custody_block.cteb_data.bundle_seq_id)
                    cteb_seq_nums.append(custody_block.cteb_data.bundle_seq_num)

            ctebs = [list(e) for e in list(zip(cteb_seq_ids, cteb_seq_nums))]

            wait_check(f"<%= target_name %> BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_IN_CUSTODY == {expected_custodial_count}", 10)
            wait_check(f"<%= target_name %> BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED == {expected_stored_count}", 10)

            expected_generated_ccs = current_generated_ccs + num_seq_ids

        except KeyboardInterrupt:
            pass

        except Exception:
            print(traceback.format_exc())

        finally:
            # Wait for pending CCS to timeout
            wait_check(f"<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_GENERATED_CCS == {expected_generated_ccs}", 86)

            # Accept all bundles to clear out bundles for next test
            primary_block.control_flags               = BundlePCFlags.IS_ADMIN_RECORD
            primary_block.dest_eid.ssp["node_num"]    = 100
            primary_block.dest_eid.ssp["service_num"] = 0

            next_node_ccs = AdminRecordBlock(
                blk_type=BlockType.AUTO,
                blk_num=1,
                control_flags=0,
                crc_type=CRCType.CRC16_X25,
                record_type = AdminRecordType.COMPRESSED_CUSTODY_SIGNAL,
                record_content = CCSData({
                    DispositionCode.CUSTODY_ACCEPTED: BundleSequenceCollection(
                                                bundle_seq_id=ctebs[0][SEQ_ID],
                                                first_seq_num=ctebs[0][SEQ_NUM],
                                                bundle_seq_range=[num_seq_ids * num_seq_nums]),
                }),
                crc=CRCFlag.CALCULATE
            )

            ccs_bundle = Bundle(
                pri_block=primary_block,
                canon_blocks=[next_node_ccs],
            )

            # Encode and send CCS bundle
            encoded_input_bundle = ccs_bundle.to_bytes()
            data_sender.write(encoded_input_bundle)

            wait_check(f"<%= target_name %> BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_IN_CUSTODY == 0", 10)
            wait_check(f"<%= target_name %> BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED == 0", 10)

            data_receiver.disconnect()
            data_sender.disconnect()


    def test_bpnode_custody06_ccs_size_limit(self):
        SRC_NODE_NUM     = 100
        SRC_SERVICE_NUM  = 0
        RPT_NODE_NUM     = 200
        RPT_SERVICE_NUM  = 2

        data_receiver = UdpRxSocket(LOCAL_IP, LOCAL_PORT)
        data_sender   = UdpTxSocket(BPNODE_IP, BPNODE_PORT)

        try:
            # Connect the data sender and receiver tools
            data_receiver.connect()
            data_sender.connect()

            payload_block = PayloadBlock(
                blk_type=BlockType.AUTO,
                blk_num=1,
                control_flags=0,
                crc_type=CRCType.CRC16_X25,
                payload=bytes([0xAA] * 30),
                crc=CRCFlag.CALCULATE,
            )

            first_seq_num = 34
            # num_seq_nums  = (CONT_0_CS_SIZE_TRIGGER // 2) + 1
            num_seq_nums  = 6
            num_bundles   = 0
            bundle_seq_id = 1

            for seq_num_offset in range(num_seq_nums):
                primary_block = PrimaryBlock(
                                version=7,
                                control_flags=BundlePCFlags.MUST_NOT_FRAGMENT,
                                crc_type=CRCType.CRC16_X25,
                                dest_eid=EID({"uri": 2, "ssp": {"node_num": 200, "service_num": 64}}),
                                src_eid=EID({"uri": 2, "ssp": {"node_num": SRC_NODE_NUM, "service_num": SRC_SERVICE_NUM}}),
                                rpt_eid=EID({"uri": 2, "ssp": {"node_num": RPT_NODE_NUM, "service_num": RPT_SERVICE_NUM}}),
                                creation_timestamp=CreationTimestamp({"time": DtnTimeNowMs(), "sequence": num_bundles}),
                                lifetime=3600000,
                                crc=CRCFlag.CALCULATE
                            )

                prev_node_cte_block = CustodyTransferBlock(
                    blk_type=BlockType.AUTO,
                    blk_num=4,
                    control_flags=BlockPCFlags.REP_UNPROC,
                    crc_type=CRCType.CRC16_X25,
                    cteb_data=CTEBData(
                        {
                            "bundle_seq_num": first_seq_num + (seq_num_offset * 2),
                            "bundle_seq_id": bundle_seq_id,
                            "block_src_admin_eid": EID({"uri": 2, "ssp": {"node_num": 200, "service_num": 64}})
                        }
                    ),
                    crc=CRCFlag.CALCULATE,
                )

                cteb_bundle = Bundle(
                    pri_block=primary_block,
                    canon_blocks=[prev_node_cte_block, payload_block]
                )

                num_bundles += num_bundles

                # Encode and send bundle with CTEB
                encoded_input_bundle = cteb_bundle.to_bytes()
                data_sender.write(encoded_input_bundle)

            # Read the bundles until a CCS pops out
            cteb_seq_ids  = []
            cteb_seq_nums = []

            while True:
                data        = data_receiver.read()
                data_bundle = Bundle.from_bytes(data)

                if data_bundle.pri_block.control_flags != BundlePCFlags.IS_ADMIN_RECORD:
                    custody_block = data_bundle.canon_blocks[0]
                    cteb_seq_ids.append(custody_block.cteb_data.bundle_seq_id)
                    cteb_seq_nums.append(custody_block.cteb_data.bundle_seq_num)
                else:
                    break

            ctebs = [list(e) for e in list(zip(cteb_seq_ids, cteb_seq_nums))]

            rcvd_ccs = data_bundle.canon_blocks[1].record_content
            check_expression(f'{data_bundle.canon_blocks[1].record_type} == {AdminRecordType.COMPRESSED_CUSTODY_SIGNAL}')
            check_expression(f'{list(rcvd_ccs.ccsdata.keys())[0]} == {DispositionCode.CUSTODY_ACCEPTED}')
            check_expression(f'{rcvd_ccs.ccsdata[1].bundle_seq_id} == {bundle_seq_id}')
            check_expression(f'{rcvd_ccs.ccsdata[1].dest_eid} == None')
            check_expression(f'{rcvd_ccs.ccsdata[1].first_seq_num} == {first_seq_num}')
            check_expression(f'{rcvd_ccs.ccsdata[1].bundle_seq_range} == {[1] * 11}') # CONT_0_CS_SIZE_TRIGGER + (CONT_0_CS_SIZE_TRIGGER % 2 == 0)
            check_expression(f'{rcvd_ccs.ccsdata[1].block_src_admin_eid} == None')

        except KeyboardInterrupt:
            pass

        except Exception:
            print(traceback.format_exc())

        finally:
            # No CCSs expected since lone CCS will be sent out due to size limit

            # Accept rejected bundles to clear out bundles for next test
            primary_block.control_flags               = BundlePCFlags.IS_ADMIN_RECORD
            primary_block.dest_eid.ssp["node_num"]    = 100
            primary_block.dest_eid.ssp["service_num"] = 0

            next_node_ccs = AdminRecordBlock(
                blk_type=BlockType.AUTO,
                blk_num=1,
                control_flags=0,
                crc_type=CRCType.CRC16_X25,
                record_type = AdminRecordType.COMPRESSED_CUSTODY_SIGNAL,
                record_content = CCSData({
                    DispositionCode.CUSTODY_ACCEPTED: BundleSequenceCollection(
                                                bundle_seq_id=ctebs[0][SEQ_ID],
                                                first_seq_num=ctebs[0][SEQ_NUM],
                                                bundle_seq_range=[num_seq_nums])
                }),
                crc=CRCFlag.CALCULATE
            )

            next_node_ccs_bundle = Bundle(
                pri_block=primary_block,
                canon_blocks=[next_node_ccs],
            )

            # Encode and send CCS bundle
            encoded_input_bundle = next_node_ccs_bundle.to_bytes()
            data_sender.write(encoded_input_bundle)

            wait_check(f"<%= target_name %> BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_IN_CUSTODY == 0", 10)
            wait_check(f"<%= target_name %> BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED == 0", 10)

            data_receiver.disconnect()
            data_sender.disconnect()


    # def test_bpnode_custody07_available_ccs_limit(self):
    #     # Provide several different seq IDs
    #     # EID Configuration
    #     SRC_NODE_NUM    = 100
    #     SRC_SERVICE_NUM = 0
    #     RPT_NODE_NUM    = 200
    #     RPT_SERVICE_NUM = 2

    #     data_receiver = UdpRxSocket(LOCAL_IP, LOCAL_PORT)
    #     data_sender   = UdpTxSocket(BPNODE_IP, BPNODE_PORT)

    #     try:
    #         # Connect the data sender and receiver tools
    #         data_receiver.connect()
    #         data_sender.connect()

    #         payload_block = PayloadBlock(
    #             blk_type=BlockType.AUTO,
    #             blk_num=1,
    #             control_flags=0,
    #             crc_type=CRCType.CRC16_X25,
    #             payload=bytes([0xAA] * 30),
    #             crc=CRCFlag.CALCULATE,
    #         )

    #         first_seq_id = 11
    #         seq_num      = 11
    #         num_seq_ids  = 10
    #         num_bundles  = 0

    #         for seq_id_offset in range(num_seq_ids):
    #             primary_block = PrimaryBlock(
    #                             version=7,
    #                             control_flags=BundlePCFlags.MUST_NOT_FRAGMENT,
    #                             crc_type=CRCType.CRC16_X25,
    #                             dest_eid=EID({"uri": 2, "ssp": {"node_num": 200, "service_num": 64}}),
    #                             src_eid=EID({"uri": 2, "ssp": {"node_num": SRC_NODE_NUM, "service_num": SRC_SERVICE_NUM}}),
    #                             rpt_eid=EID({"uri": 2, "ssp": {"node_num": RPT_NODE_NUM, "service_num": RPT_SERVICE_NUM}}),
    #                             creation_timestamp=CreationTimestamp({"time": DtnTimeNowMs(), "sequence": num_bundles}),
    #                             lifetime=3600000,
    #                             crc=CRCFlag.CALCULATE
    #                         )

    #             prev_node_cte_block = CustodyTransferBlock(
    #                 blk_type=BlockType.AUTO,
    #                 blk_num=4,
    #                 control_flags=BlockPCFlags.REP_UNPROC,
    #                 crc_type=CRCType.CRC16_X25,
    #                 cteb_data=CTEBData(
    #                     {
    #                         "bundle_seq_num": seq_num,
    #                         "bundle_seq_id": first_seq_id + seq_id_offset,
    #                         "block_src_admin_eid": EID({"uri": 2, "ssp": {"node_num": 400, "service_num": 42}})
    #                     }
    #                 ),
    #                 crc=CRCFlag.CALCULATE,
    #             )

    #             cteb_bundle = Bundle(
    #                 pri_block=primary_block,
    #                 canon_blocks=[prev_node_cte_block, payload_block]
    #             )

    #             num_bundles += num_bundles

    #             # Encode and send bundle with CTEB
    #             encoded_input_bundle = cteb_bundle.to_bytes()
    #             data_sender.write(encoded_input_bundle)


    #         cteb_seq_ids  = []
    #         cteb_seq_nums = []

    #         while True:
    #             data        = data_receiver.read()
    #             data_bundle = Bundle.from_bytes(data)

    #             if data_bundle.pri_block.control_flags != BundlePCFlags.IS_ADMIN_RECORD:
    #                 custody_block = data_bundle.canon_blocks[0]
    #                 cteb_seq_ids.append(custody_block.cteb_data.bundle_seq_id)
    #                 cteb_seq_nums.append(custody_block.cteb_data.bundle_seq_num)
    #             else:
    #                 break

    #         ctebs = [list(e) for e in list(zip(cteb_seq_ids, cteb_seq_nums))]

    #         rcvd_ccs = data_bundle.canon_blocks[1].record_content
    #         check_expression(f'{data_bundle.canon_blocks[1].record_type} == {AdminRecordType.COMPRESSED_CUSTODY_SIGNAL}')
    #         check_expression(f'{list(rcvd_ccs.ccsdata.keys())[0]} == {DispositionCode.CUSTODY_ACCEPTED}')
    #         check_expression(f'{rcvd_ccs.ccsdata[1].dest_eid} == None')
    #         check_expression(f'{rcvd_ccs.ccsdata[1].first_seq_num} == {seq_num}')
    #         check_expression(f'{rcvd_ccs.ccsdata[1].bundle_seq_range} == {[1]}')
    #         check_expression(f'{rcvd_ccs.ccsdata[1].block_src_admin_eid} == None')

    #         current_generated_ccs  = tlm("<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_GENERATED_CCS")
    #         expected_generated_ccs = current_generated_ccs + num_seq_ids
    #     except KeyboardInterrupt:
    #         pass

    #     except Exception:
    #         print(traceback.format_exc())

    #     finally:
    #         # Wait for all pending CCSs to clear out
    #         wait_check(f"<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_GENERATED_CCS == {expected_generated_ccs}", 86)

    #         # Accept all bundles to clear out bundles for next test
    #         for seq_id_offset in range(num_seq_ids):
    #             next_node_ccs = AdminRecordBlock(
    #                 blk_type=BlockType.AUTO,
    #                 blk_num=1,
    #                 control_flags=0,
    #                 crc_type=CRCType.CRC16_X25,
    #                 record_type = AdminRecordType.COMPRESSED_CUSTODY_SIGNAL,
    #                 record_content = CCSData({
    #                     DispositionCode.CUSTODY_ACCEPTED: BundleSequenceCollection(
    #                                                 bundle_seq_id=first_seq_id + seq_id_offset,
    #                                                 first_seq_num=seq_num,
    #                                                 bundle_seq_range=[1]),
    #                 }),
    #                 crc=CRCFlag.CALCULATE
    #             )

    #             ccs_bundle = Bundle(
    #                 pri_block=primary_block,
    #                 canon_blocks=[next_node_ccs],
    #             )

    #             # Encode and send CCS bundle
    #             encoded_input_bundle = ccs_bundle.to_bytes()
    #             data_sender.write(encoded_input_bundle)

    #         wait_check(f"<%= target_name %> BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_IN_CUSTODY == 0", 10)
    #         wait_check(f"<%= target_name %> BPNODE_NODE_MIB_REPORTS_HK BUNDLE_COUNT_STORED == 0", 10)

    #         data_receiver.disconnect()
    #         data_sender.disconnect()


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
