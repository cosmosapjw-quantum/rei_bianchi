#!/usr/bin/env python3
"""Create a fixed throughput batch by repeating four actual-source channels."""
import hashlib,json,struct
from pathlib import Path
unit=Path(__file__).resolve().parents[1]
source=unit/'verification/source_benchmark_grid/SOURCE_GREEN.bin'
raw=source.read_bytes();tasks,nodes=struct.unpack('<QQ',raw[8:24]);copies=16
assert raw[:8]==b'HHG73V01' and tasks==4 and nodes==129
target=unit/'verification/BENCHMARK_INPUT.bin'
with target.open('xb') as f:f.write(raw[:8]+struct.pack('<QQ',tasks*copies,nodes)+raw[24:]*copies)
receipt=dict(schema='PHYS73_BENCHMARK_PAYLOAD_V1',source=str(source.relative_to(unit)),
 source_sha256=hashlib.sha256(raw).hexdigest(),copies=copies,independent_tasks=tasks*copies,
 radial_nodes=nodes,distinct_physical_channels=4,
 purpose='replicated same-payload kernel throughput; not 64 distinct physical angular modes',
 output_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),HH_R10='OFF')
with (unit/'verification/BENCHMARK_INPUT.json').open('x') as f:json.dump(receipt,f,indent=2);f.write('\n')
print(json.dumps(receipt,indent=2))
