# R118-C2L: tighter q32 continuation

Parent e93661d3b83beb4cb2c381339dde6e860c28e7c1. Same byte-identical C2K checkpoint/config/source identity; no changed controller or rates. The initial attempt with lower-than-config attempt cap was rejected before outputs; successful command used original caps and 220 s segment wall cap. Exact executable SHA in ACCEPTANCE. Command:

```
D=/home/cosmosapjw/Downloads/rei_r118c2k_segments
"$D/segment_v2" "$D/fresh32tight/config.cfg" "$D/fresh32tight" /home/cosmosapjw/Downloads/rei_r118c2l_tight 220
python3 research/r118c2l_tight_continuation/audit.py /home/cosmosapjw/Downloads/rei_r118c2l_tight "$D" /home/cosmosapjw/Downloads/rei_r118c2j_reduced
```

136580 additional accepted states, total 257197; z 14.25374333798 -> 13.00567266225. STOPPED_SEGMENT_WALL_CAP, not full interval. All new states satisfy existing N/E/parity/charge/local gates; raw history hashes and compressed checkpoint/config retained. Prefix matched-redshift comparisons separate observed local-target sensitivity and q32/q64 sensitivity, not a global error bound. Thin npz is visualization only. Next: continue this exact checkpoint under original resource caps (additional step cap changes, if needed, must be explicit); obtain full z=4 tighter q32 before interpreting HeIII discrepancy. Do not promote scientific admission.
