# Run state

- Audited implementation base: `ddf125732854f4365e000b013c4bb78970ac6fcd`.
- First repaired common state: coarse k12, fine k24, tail k12; `ln(a)=-2.5644493574615366`, `z=11.993501624729198`.
- Additional accepted state: coarse k13, `ln(a)=-2.5644410241282034`.
- First unresolved state: coarse k14, paired weighted N/E readout.
- Original checkpoint trees under `numeric/{coarse,fine,tail}` are unchanged. New runs are under `repair_20261008/runs`.
- Next minimum action: design one authoritative paired per-node N/E value plus uncertainty that survives segment weighting, density storage, observer use and checkpoint roundtrip. Begin with the captured coarse k14 operands and preserve structural zero separately.
- Full 0.0008 suffix, longer horizons, z=12→10, continuum validation and physical admission remain incomplete.
