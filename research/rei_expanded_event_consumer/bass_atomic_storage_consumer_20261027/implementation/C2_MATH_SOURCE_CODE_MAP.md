# C2 — 수식·source field·구현

| 수학 객체 | 고정 원문 경로 | 구현 |
|---|---|---|
| N_a,N_b,d (ground,2s,2p,continuum) | finite_owners.initial_stocks/final_stocks/stock_change_from_events, 각4×1decimalstring | _source_rows,coarse_mapping |
| P와thermal전자/fastζ분리 | inventory_order, electrons_initial/electrons_final | Coarse,consume |
| A와fiveenergysectors | sector_order,event_sector_energy_J_m3 | energy_lift,mapped_apply_ports |
| 원래SIencoding | energy_unit_encoding | source_original_energy_encoding, sourcealreadyJ그대로 |
| R=Vb/V0 | right_volume_ratio | right_proper,endpoint_split |
| Common-V0와rightproperenergy | final_sector_energy_common_V0_J_m3 / final_sector_energy_J_m3 | energy_volume_encoding_residual |
| Event/work/endpoint차이 | initial_sector_energy_J_m3,geometry_work_J_m3 | energy_endpoint_minus_event_work_diagnostic |
| 실제Lyα채널 | channel_groups.Lyalpha.atomic_change/net_count | runneractualP=0andphotoncountpreservation |
| 양쪽b·R변분 | 조건부명시입력; 실제b미제공 | conditional_abundance_jvp |

SOURCE_FIELD_MAP.json은원문문자열/형태를보이는구조발췌다. 실행source는별도3554206-byte원본이며발췌를과학source로대체하지않는다. JSONfloat을str로읽고선택된원문decimal을Fraction으로해석한다. 원문JSON을다시직렬화하여덮어쓰지않는다. 원래raw4CR입력과큰정수는손대지않는다.

native25의H1I/H1II는indices1/2이며 ζ21은fast전자다. 이번source의thermalelectron을ζ로보내지않는다. 실제b/EOS미제공이므로fullnative25와logTupdate는null이다. 소유된한거래의canonicalID와sixapplyports로중복적용을방지한다.
