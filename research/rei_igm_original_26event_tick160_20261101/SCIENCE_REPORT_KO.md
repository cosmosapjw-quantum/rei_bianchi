# REI original 26-event H/He source response at first-interval tick160

2026-11-01 | owner \`rei_bianchi\` | scientific status: **source-authentic, source-conditional physical rate diagnostics only**

## Verified original provenance

- REI main \`ae3402713c4b6530ab2b27f008f5f5d5c6a999ed\`, parent Draft PR #320 head \`e5836fc4b8804d1bcdcdcbb97ab33f822703fa46\`.
- Original first-interval run archive SHA256 \`a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b\`, 11,637,524 bytes. Immutable source state: 46,080 nodes and 3 accepted endpoints, tick160/131072 (0.1220703125%).
- Original 26-event H/He full-OTS source and four independent evaluation sites are read from the predecessor \`interval_discrete_map.py\` / \`reduced_interval_rhs.py\`. The new code does **not modify** these sources.
- Actual source scientific GitHub CI run [#41266308694](https://github.com/cosmosapjw-quantum/rei_bianchi/actions/runs/41266308694) at \`ea124e4fdb1947003dc0ae272fc3041fe5a21d0f\`: **SUCCESS**, 7/7 source tests, all 6×46080 source output rows finite and input archive SHA confirmed.
- Published workflow artifact ID \`13066329719\`, 30,687,257 bytes, SHA256 \`b40a4fe081ab6d84ca5319548aeebf63988665940ef08804789392839aef6b9a\`. ZIP CRC, internal six gz file SHA and independent readback **PASS**. Local duplicate file is available for user download. This GitHub Actions artifact expires on 2027-01-30: it is **not** durable permanent blob storage.

## Actual physical response (equal-node medians)

| Quantity | Start | accepted tick160 |
|---|---:|---:|
| x_HII representative | 0.9999359097360792 | 0.9999437241659213 |
| x_HeII representative | 0.9975968687160607 | 0.9968434161946291 |
| x_HeIII representative | 0.0023767184598343727 | 0.0023671067332854696 |
| T_gas [K] | 11827.779049366949 | 11828.327355246627 |
| x_e per H | 1.0790916161010082 | 1.0790617641184692 |
| d(x_e)/dt rate [s^-1] | -5.230967697496201e-18 | -7.280392611747435e-18 |
| primary+OTS photoheating [erg H^-1 s^-1] | 8.805630575148083e-30 | 8.072638999406354e-30 |
| escaped OTS energy [erg H^-1 s^-1] | 3.533077865853381e-31 | 3.5327045423610745e-31 |

Original source time from interval beginning to tick160 is \`779495799866.9248 s\`. Every original source-state SHA at tick160 is \`cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab9999e7e3508a5161edb01\`.

The six stored outputs are **276,480 lane-labelled model rate rows**, but independent gzip-decompressed numerical CSV comparisons prove identical source rates across all three lane labels. Thus there are only **92,160 distinct node/snapshot numerical records** (46,080 distinct spatial node IDs, two times), not three independent radiation models. No measured observational rows. The inherited \`ReducedIntervalModel.from_repo\` uses the primary lane under its original uncertainty envelope: do not call these three separate source-calibrated histories.

## Reusable scientific equation

Let \`N=(N_HI,N_HII,N_HeI,N_HeII,N_HeIII)\`. For original event flux matrix \`F_ij\` in particles/s, destination i, source j:

\`\`\`
dN_i/dt = sum_j (F_ij - F_ji)
dN_e/dt = dN_HII/dt + dN_HeII/dt + 2*dN_HeIII/dt
x_e = (N_HII+N_HeII+2*N_HeIII)/(N_HI+N_HII)
U_thermal/N_H = (3/2) k_B T (N_H + N_He + N_e)/N_H
\`\`\`

\`k_B = 1.380649e-16 erg/K\`. The source checks H/He elemental nuclei conservation, and interval zero inclusion of source OTS photon/energy owner identities. Each point population is explicitly constrained inside the original accepted interval and preserves H/He totals.

**Blind-referee limitation:** the midpoint of each independently bounded output flux need not correspond to one common physically coherent source/temperature realization. These are useful state-conditioned source **diagnostics**, not a newly integrated 26-event state history, whole-interval photon-number/energy conservation, non-equilibrium thermal trajectory or source-sensitivity derivative. Absence of a fully correlated source realization is a current limitation, not grounds to discard genuine source data. The 3 lanes are numerically identical and must not be counted as 3 independent physical rows.

## Real first-interval blocker and next calculation

Original [160,161] old independent full-step versus two-half logT image error \`2.1245050576368385e-4\` exceeds the unchanged \`2.0e-4\` gate. State width \`2.257243260856967e-4\` satisfies \`2e-3\`, no table knot crossed; all original ledger intervals included zero. The cross-box metric contains inherited parent box width even for two equal maps. To repair representation without weakening the original threshold, derive and certify the **same-parent, source-correlated** nonlinear
\`\`\`
D_h(x,theta) = F_h(x,theta) - F_{h/2}(F_{h/2}(x,theta),theta)
J_D = J_Fh - J_Fhalf(Fhalf(x,theta))*J_Fhalf(x,theta)
\`\`\`
including four source-evaluation sites, named owner low-rank terms, thermal implicit roots and Hummer-Seaton event partition. No point-only or independently boxed estimator is a substitute. Retry only the original [160,161] step if and when validated; then the full first interval under the same gates.

## Admission and preservation

REI central **28/88 reported**, working **33/88 reported**, new canonical \`0\`; BASS CE1 **9/15 qualified** unrelated to core. FIRST_CANONICAL_INTERVAL=BLOCKED_MINIMUM_STEP; B2C2B, B2C2C, recombination splice, C0 and CMB transfer not accepted. Production/merge HOLD, auto-next OFF. New source script, CI and tests in this isolated Draft PR; no ancestor source or production edits, no force-push, no side-branch promotion. Native subagent NOT_RUN, one same-author adversarial review and one symbolic Wolfram cross-check.

Primary references: Puchwein et al. (2019), DOI 10.1093/mnras/stz222, for distinct UVB vs RT rate authority; Neher/Jackson/Nedialkov, SIAM J. Numer. Anal. (2007), DOI 10.1137/050638448, for validated interval dependency / wrapping; neither is claimed to validate this 26-event implementation.
