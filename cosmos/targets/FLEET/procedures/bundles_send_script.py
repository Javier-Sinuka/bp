# Send a predefined set of bundles to the Lunar Relay DTN Node from a Lunar User
#

# Setting Script Runner line delay
set_line_delay(0.000)

import codecs
import time
import traceback
import warnings

from dtntools.dtngen.blocks import (
    BundleAgeBlock,
    CanonicalBlock,
    CompressedReportingBlock,
    CustodyTransferBlock,
    HopCountBlock,
    PayloadBlock,
    PayloadBlockSettings,
    PrevNodeBlock,
    PrimaryBlock,
    PrimaryBlockSettings,
    UnknownBlock,
)
from dtntools.dtngen.bundle import Bundle
from dtntools.dtngen.types import (
    EID,
    BlockPCFlags,
    BlockType,
    BundlePCFlags,
    CRCFlag,
    CRCType,
    CreationTimestamp,
    CREBData,
    CTEBData,
    HopCountData,
    StatusRRFlags,
    TypeWarning,
)

from dtntools.dtncla.udp import UdpRxSocket, UdpTxSocket

dest_number = stash_get('dest_number')
print (f"Destination Node Number: {dest_number}")

if dest_number is None:
    dest_number = 103

dest_service = stash_get('dest_service')
print (f"Destination Service Number: {dest_service}")
    
if dest_service is None:
    dest_service = 1

payload_size = stash_get('payload_size')
print (f"Payload Size (bytes): {payload_size}")
    
if payload_size is None:
    payload_size = 1000
    
lifetime_in_sec = stash_get('lifetime_in_sec')
print (f"Bundle Lifetime (seconds): {lifetime_in_sec}")
    
if lifetime_in_sec is None:
    lifetime_in_sec = 3600
    
total_send_loops = stash_get('total_send_loops')
print (f"Total Send Loops (50 bundles each): {total_send_loops}")
    
if total_send_loops is None:
    total_send_loops = 1
    
send_to_ip = stash_get('send_to_ip')
print (f"Send To IP Address: {send_to_ip}")
    
if send_to_ip is None:
    send_to_ip = '127.0.0.1'

send_to_port = stash_get('send_to_port')
print (f"Send To IP Port: {send_to_port}")

if send_to_port is None:
    send_to_port = 4556
        
rate_limit = stash_get('rate_limit')
print (f"Sending Rate Limit (Mbps): {rate_limit}")

if rate_limit is None:
    rate_limit = 1

warnings.simplefilter("always")

print("Defining new primary and payload blocks")
primary_block_settings = PrimaryBlockSettings(
    version=7,
    control_flags=BundlePCFlags.MUST_NOT_FRAGMENT,
    crc_type=CRCType.CRC16_X25,
    dest_eid=EID({"uri": 2, "ssp": {"node_num": dest_number, "service_num": dest_service}}),
    src_eid=EID({"uri": 2, "ssp": {"node_num": 101, "service_num": 1}}),
    rpt_eid=EID({"uri": 2, "ssp": {"node_num": 100, "service_num": 1}}),
    creation_timestamp={
        "time": "current",
        "sequence": {"start": 0},
    },
    lifetime=(lifetime_in_sec * 1000),
    crc=CRCFlag.CALCULATE,
)

payload_block_settings = PayloadBlockSettings(
    blk_type=BlockType.AUTO,
    blk_num=1,
    control_flags=0,
    crc_type=CRCType.CRC16_X25,
    payload={"min_size": payload_size, "max_size": payload_size},
    crc=CRCFlag.CALCULATE,
)

print("Creating the new set of bundles")
generated_bundles = Bundle.generate(
    num_bundles=50,
    pri_settings=primary_block_settings,
    canon_settings=[payload_block_settings],
)

print("Converting bundles to bytes")
bundle_data = [x.to_bytes() for x in generated_bundles]
    
print("Configuring the Data Sender")
data_sender = UdpTxSocket(send_to_ip, send_to_port, bps_limit=(1000000 * rate_limit))

print("Connecting the Data Sender")
data_sender.connect()

loops = 0
Start_Time = time.time()
print(f"Sending Start Time = {Start_Time}")

print("Sending bundles...")
with disable_instrumentation():
    while loops < total_send_loops:
        loops = loops + 1

        for x in bundle_data:
            data_sender.write(x)

End_Time = time.time()
print(f"Sending End Time = {End_Time}")

time.sleep(5)

bundles_sent = data_sender.get_packets_sent()
print(f"Bundles Sent = {bundles_sent}")
stash_set('bundles_sent', bundles_sent)

print("Disconnecting the Data Sender")
data_sender.disconnect()
