# REI-F05: actual original 26-event tick160 two-energy-matched-parent nonlinear source science (2026-11-01)

Original owner: cosmosapjw-quantum/rei_bianchi, protected PR #328 HEAD `a85312cde63e5c0b0a7c0e5d182e79fe593bcf53`. Exact original blocked run archive SHA256 `a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b`, accepted state array SHA256 `cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab9999e7e3508a5161edb01`, kernel `579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644`. Parent accepted 160/131072 ticks. This is a source-authentic fixed-micro-interval analysis, not a new astronomical observation nor a new integrated original F05 interval.

## Actually executed ORIGINAL 26-event physical maps
GitHub Actions [source CI](https://github.com/cosmosapjw-quantum/rei_bianchi/actions/runs/41273672432) all three lane jobs SUCCESS, [verify](https://github.com/cosmosapjw-quantum/rei_bianchi/actions/runs/41273672367) SUCCESS. Each lane executed two element-conserving, *input-material-energy-conserving* parent points using unchanged MPRK22(1) population and Alexander SDIRK2 thermal four source evaluation sites, one full step and consecutive two halves on original [160,161]. No original code, source, gates, or history state changed. Each lane produced 92,160 model rows (two points × 46,080 spatial nodes); the three lane numerical results are almost identical and NOT three independent observational histories.

The energy-matched input comparison uses ideal kinetic + NIST H/He atomic ionization reference energy only, not the complete photon+OTS+expansion ledger; energy is **not assumed conserved during time evolution**. Source path maximal input material-energy relative residual 7.011886184170497e-16, median change electron/H (+ minus -) 9.127062909461115e-9, median logT change -5.334806685297622e-8.

| Original full versus two-half model quantity | CHEM_MINUS | CHEM_PLUS |
|---|---:|---:|
| max logT independent-output-box difference bound | 5.947156651586739e-7 | 5.949608823385689e-7 |
| max abs logT box-center defect | 4.810196685411938e-11 | 9.85975745493306e-11 |
| max xHII output box difference bound | 3.1843395031927464e-8 | 3.185841723762906e-8 |
| max xHeII output box difference bound | 1.804535096905369e-7 | 1.813766060676514e-7 |

The maximum variation between two local logT box-center defects across 46,080 nodes is 1.1159162482954342e-10. All per-point independent-output-box upper bounds are below fixed 2e-4; **but these point results do not prove the F05 all-parent local error test**. Full original independent-box failed 2.1245050576368385e-4 > original strict 2e-4; final state remains BLOCKED_MINIMUM_STEP, 160/131072 ticks, and the physical owner has not accepted tick161.

## Provenance and backup
Three original GitHub Actions artifacts: PRIMARY #13070570629 SHA256 bf1e9c05e27b01f6794669bc4ecbde6c1e35db7c5e5eefceb3873cecdd16453e; RECOMB #13070520182 SHA256 e2f789bcf16009c499ae08e9d5f35b1c998cac91f737b7d0cb2a57f5c31b4eaf; SCRIPT #13070735233 SHA256 5ba60f6594d4d9f37fc248a8e53421e54cde6a949371b75c7e374dde7aa8b9ba. Downloaded and independently checked ZIP CRC, per-result CSV SHA, 92,160 rows/lane and data finiteness.

Tests: inherited 6, new 5 normal + 5 Python -O, all PASS per lane. First CI 41273543895 was pre-physics FAIL due a 63-character duplicate SHA literal; the load-bearing source check was fixed to reuse PR328 authoritative SHA, not by changing source bytes/physics. Final normal CI PASS. Original physical stage data and generated science archive are not replicated in Git text files; use the immutable workflow artifact IDs and separate source archive.

## One-pass adversarial review
1. **INVALID promotion**: two points in an independent coordinate box are not necessarily in the jointly physically reachable parent set, and cannot certify `D_h(X,theta)` across original correlated parent and photon/source.
2. **Independent interval subtract**: `[F_h]-[H_h]` can include inherited parent box width even for identical maps. These numbers are independently enclosed **point-source image comparisons** not true joint remainder certificates.
3. **Wrong energy owner**: preserving ideal material E between two input points does not conserve the full photon/chemical/thermal/gravitational energy during evolution; original four-event-site source-ownership and native ledgers unchanged.
4. **Double counting**: three lane-labelled outputs carry near identical state values; source evaluations not three independent astrophysical realizations.
5. **Implementation failure preserved**: initial CI rejected pre-physics from copied malformed source SHA; repaired with parent verified source SHA. One unused declaration of the original malformed constant remains in the source text, with no effect on live data authentication. Remove only in future bounded code cleanup if needed, not another physics stage.
6. **Budget/authority**: repo-wide verify and all 3 source CI jobs PASS on corrected code; separate author blind referee NOT_RUN and original F05 full-interval solver NOT_RUN; cannot count any canonical delta.

Canonical REI **28/88 (+0)**, working REI **33/88 (+0)**, physical REC H5 **0/313 (+0)**, REI physical fast **4/7 (+0)**. No main merge, force-push, production or original tolerance relaxation. Next science: actual joint derivative and rigorous remainder for source- and parent-correlated 26-event nonlinear `D_h=F_h-G_1\circ G_0`, including implicit thermal roots and four source sites; only then original [160,161] all-X retry under original gate.

Primary method references: Makino & Berz (2009), DOI 10.1145/1577190.1577206, validated Taylor models, and guaranteed interval Runge–Kutta literature; do not mistake literature support for independent code validation.
