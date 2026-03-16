# Receive a predefined set of bundles from NSN DTN Node
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

bundle_set_size = stash_get('bundle_set_size')
print (f"Number of Bundles to be Received: {bundle_set_size}")

if bundle_set_size is None:
    bundle_set_size = 250000
    
receive_port = stash_get('receive_port')
print (f"Receive Port Number: {receive_port}")

if receive_port is None:
    receive_port = 4556
        
max_duration = stash_get('max_duration')
print (f"Maximum Time to Wait for all Bundles to be Received (seconds): {max_duration}")

if max_duration is None:
    max_duration = 60

warnings.simplefilter("always")

print("Configuring the Data Receiver")
data_receiver = UdpRxSocket("0.0.0.0", receive_port)

print("Connecting the Data Receiver")
data_receiver.connect()

print("Receiving bundles...")
Start_Time = time.time()
print(f"Receiving Start Time = {Start_Time}")

bundles_received = 0
with disable_instrumentation():
    while (bundles_received < bundle_set_size) and ((time.time() - Start_Time) < max_duration):
        data_receiver.read_all()
        time.sleep(0.1)
        bundles_received = data_receiver.get_packets_received()
    
End_Time = time.time()
print(f"Receiving End Time = {End_Time}")

time.sleep(5)

bundles_received = data_receiver.get_packets_received()
print(f"Bundles Received = {bundles_received}")
stash_set('bundles_received', bundles_received)

print("Disconnecting the Data Receiver")
data_receiver.disconnect()
