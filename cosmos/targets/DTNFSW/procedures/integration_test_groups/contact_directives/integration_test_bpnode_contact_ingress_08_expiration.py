from openc3.script.suite import Group

import os
import time
import traceback

from dtntools.dtngen.utils import DtnTimeNowMs
from dtntools.dtncla.udp import UdpRxSocket, UdpTxSocket
from dtntools.dtngen.blocks import (
    PayloadBlock,
    BundleAgeBlock,
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


# Networking Configuration: Please ensure you have port forwarding rules
BPNODE_IP = "172.17.0.1"
BPNODE_PORT = <%= dtnfsw_get_cla_in_port(target_name, 0) %>

class integration_test_bpnode_contact_ingress_08(Group):
    """
    Test Group
    """

    def test_bpnode_bundle_ingress_08(self):
        # EID Configuration
        DEST_NODE_NUM    = <%= $dtnfsw_globals_contact_0_dest_eid_node %>
        DEST_SERVICE_NUM = <%= $dtnfsw_globals_contact_0_dest_eid_service %>
        SRC_NODE_NUM     = 300
        SRC_SERVICE_NUM  = 1

        # Create test bundle
        payload_length = 30
        payload_data   = bytes([0xAA] * payload_length)

        data_sender   = UdpTxSocket(BPNODE_IP, BPNODE_PORT)

        primary_block = PrimaryBlock(
            version=7,
            control_flags=BundlePCFlags.MUST_NOT_FRAGMENT,
            crc_type=CRCType.CRC16_X25,
            src_eid=EID({"uri": 2, "ssp": {"node_num": SRC_NODE_NUM, "service_num": SRC_SERVICE_NUM}}),
            dest_eid=EID({"uri": 2, "ssp": {"node_num": DEST_NODE_NUM + 42, "service_num": DEST_SERVICE_NUM + 42}}),
            rpt_eid=EID({"uri": 1, "ssp": 0}), # This is equivalent to dtn:none
            crc=CRCFlag.CALCULATE,
        )

        age_block = BundleAgeBlock(
            blk_type=BlockType.AUTO,
            blk_num=2,
            control_flags=0,
            crc_type=CRCType.CRC16_X25,
            crc=CRCFlag.CALCULATE,
        )

        payload_block = PayloadBlock(
            blk_type=BlockType.AUTO,
            blk_num=1,
            control_flags=0,
            crc_type=CRCType.CRC16_X25,
            payload=payload_data,
            crc=CRCFlag.CALCULATE,
        )

        try:
            # Connect the data sender tool
            data_sender.connect()

            # Set the blocks of the bundle such that the bundle expires in 5 seconds
            age_block.bundle_age             = 5000  # 5000  milliseconds or 5 seconds
            primary_block.lifetime           = 10000 # 10000 milliseconds or 10 seconds
            primary_block.creation_timestamp = CreationTimestamp({"time": 0, "sequence": 0}) # Invalid bundle creation time; use age block

            # Build bundle with modified blocks
            bundle = Bundle(pri_block=primary_block,
                            canon_blocks=[age_block, payload_block])

            # Encode and send the bundle
            encoded_bundle = bundle.to_bytes()
            print(f"Sending Bundle of {len(encoded_bundle)} bytes")
            data_sender.write(encoded_bundle)

            # Store expired bundle count for evaluation
            current_expired_count  = tlm("<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_DELETED_EXPIRED")
            expected_expired_count = current_expired_count + 1

            print('Waiting for bundle to expire')
            wait_check(f"<%= target_name %> BPNODE_NODE_MIB_COUNTERS_HK BUNDLE_COUNT_DELETED_EXPIRED == {expected_expired_count}", 10)

        except KeyboardInterrupt:
            pass

        except Exception:
            print(traceback.format_exc())

        finally:
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
