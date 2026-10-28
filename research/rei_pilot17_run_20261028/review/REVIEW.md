# Independent review of the executed three-case pilot

2026-10-28. Requested reviewer role: Astra; observed runtime model identity UNKNOWN. This lane did not author or execute the solver, cases or postprocessor. It performs one actual-run/figure review, reusing the previously completed static review at `../rei_source_history_20261028/review/`. It ran no IVP, rate evaluation, numerical regression, acceptance recalculation or plot. It opened existing NPZ arrays to read selected saved entries, inspected CSV/JSON/raw process receipts and images, and checked artifact hashes. No recursive reviewer was dispatched.

**Final decision: PASS_SCOPED_COUPLED17_PRESCRIBED_BATH**, including the actual redshift and log-elapsed-time figures. OFF_base, ON_base and ON_refined each completed their first authorized attempt. Their actual saved results satisfy the frozen numerical criteria. This admits the executed finite, illustrative, uncalibrated prescribed-bath trajectory, not a self-consistent radiative/thermal cosmology or historical physical-source qualification.

## Authorization, object and reused evidence

The new user explicitly approved the pending proposal: **"제안한 작업은 실행 승인할게."** The owner override and new BUDGET_AUTHORIZATION record the narrow current-cloud exception to NO_MORE_IVPs for exactly three cases,30 child CPU seconds/120 wall seconds each, one worker,3GiB and zero retries, plus bounded saved-output postprocessing. No renewed permission was needed. The exception does not authorize a broader sweep or an additional IVP after these cases.

PILOT_PREFLIGHT_IDENTITIES.json matches the five reviewed contract/history/solver/wrapper/postprocessor files and immutable baseline/model/config identities. The prior seven tests and static proofs are reused; they were not rerun. In particular, the accepted reaction structure, dynamic B/U coupling, exact polynomial signed-trial extension, single new-beta ownership, old n/T exclusion, and fixed M4 photon/T/electron-bath mapping remain unchanged. This review does not repeat their derivations or treat a second reading as another test.

Each saved NPZ contains t, physical, baryon_residual, charge_residual and scales. The physical array is23×361:17 visible populations, Bn/BT, Un/UT, and the two accumulated open-baryon/electron ledgers. The common361 times include all201 matched saved epochs and160 initial transient samples. The interval is elapsed proper time0 to9.742841241346858e16 seconds. It is not time since the Big Bang. Hidden Li6 remains its prescribed four-state saved history; its baryons and charge change participate in the appropriate accounting.

## Actual numerical outcomes

| Quantity | OFF base | ON base | ON refined |
|---|---:|---:|---:|
| Minimum scaled physical stock | 0 | 0 | 0 |
| Maximum open-baryon residual | 1.3040679647247089e-12 | 1.0880185641326534e-14 | 1.7763568394002505e-15 |
| Maximum heavy/free-electron residual | 6.536073223449568e-13 | 9.528890263649226e-15 | 3.3496968220025902e-15 |
| B=0 with nonzero U samples | 0 | 0 | 0 |
| Child CPU seconds | 1.731274 | 2.824727 | 3.603284 |

All saved physical variables and ledgers are finite. Minimum scaled stock0 satisfies the -1e-9 criterion without clipping. All three solver statuses are COMPLETED with exit0 and empty stderr. The code's smooth signed Newton extension permits internal trial values; the recorded nonnegative output is an observed property of these cases, not a theorem about every internal trial or every unsampled point.

The strict accumulated-balance threshold is1.0820350005000101e-8, using the initial heavy-particle stock1.0820350005000101 perHref. Every residual is below it. As admitted in the preceding review, this denominator is a sufficient stricter test than max(initial stock, absolute boundary throughput); absolute throughput is explicitly NOT_MEASURED and is not inferred from the net ledger. The ledgers were advanced as solver variables, not reconstructed by endpoint-only quadrature. For example, refined final total baryons1.2057192755038328 perHref and net outward baryon ledger0.12236072799622723 match the initial1.32808000350006 within the saved residual.

The largest normalized ON base/refined heavy-isotope difference is 9.4756292130907e-8 (He3), below the frozen 1e-5 criterion. The full mapping is:

| Isotope | Maximum normalized difference |
|---|---:|
| n | 4.483830443302148e-8 |
| H1 | 1.8946429968316747e-8 |
| D | 1.8946738844722102e-8 |
| T | 2.1797288984902233e-8 |
| He3 | 9.4756292130907e-8 |
| He4 | 9.475308241276657e-8 |
| Li7 | 7.311421630747872e-8 |

Fast Bn/BT and Un/UT normalized differences are also small: respectively 3.0151245825108735e-8, 2.1091048605086793e-8, 3.019815195276386e-8 and 2.4391181318007053e-8. These are a two-tolerance numerical comparison, not an absolute error theorem or model-calibration uncertainty.

At t=0 all thermal n/T, fast B/U and ledgers are exactly zero. At the read-back sample t=26351.999999999996 seconds, refined n=7.324651248346152e-23 perHref is already near its driven level, while TI=6.58784514328267e-25 and TII=1.9798392790296393e-24 are still building. Refined Bn=8.2386284701104e-24 and BT=2.6454007367878282e-23 are distinct fast populations. These actual samples demonstrate the different relaxation histories rather than merely replotting frozen QSS substitutions. The OFF samples retain exact zero n/T and fast B/U.

At the final time, refined n=7.324624081649258e-23, TI=1.40155845939593e-20, TII=4.501833369307673e-19, Bn=8.238597542861187e-24 and BT=7.281448215189358e-20 perHref. Un=8.250224449652884e-18 and UT=8.315580385481575e-14 eV/Href are the actually evolved energy stocks. H/D/He/Li daughter states are integrated together with these stocks; the prior exact event checks establish the n→HII, TI→He3II, TII→He3III and fast-T→He3III routes. No channel-resolved cumulative daughter attribution was measured, so the difference of a plotted daughter population is not assigned solely to beta decay.

## Physical interpretation and figures

The model replenishes illustrative photon/CR/injection fields while evolving the heavy targets and capture nonlinearity. Old photon, temperature and electron histories are prescribed; neither the evolved electron ledger nor new kinetic powers feed back into that bath. The same old bath is used in OFF and ON. OFF's visible difference from the saved donor is allowed by the contract: hazard reconstruction and a fixed electron bath make it a control for this new finite system, not an exact donor-reproduction test. The source branch is used at its pinned identity without claiming it has been merged.

The existing redshift PNG was directly viewed. Its seven panels show all17 visible populations, including the explicit Li7 IV legend/curve. Units are particles/Href, so stable abundances are not silently renormalized to an evolving total baryon number. The companion CSV includes hidden Li6 baryons and Bn+3BT in total baryons. Raw zeros and any signed data are retained; log axes mask only their unavailable plotting domain and introduce no positive floor. In these cases no negative saved physical stock exists. OFF n/T and saved-donor n/T are exact zeros and hence absent on the log axes.

The redshift image compresses the physically distinct n/T turn-on into its leftmost column. To meet the requested BBN-like time-view utility, one supplementary all17 log-elapsed-time figure from the same raw output was authorized as a bounded presentation correction. It did not rerun any case or replace the redshift PNG. Its first bounded render completed with exit0 in 2.001746 child CPU seconds. The existing 360 positive-time samples per case are plotted; t=0 is explicitly omitted from the logarithmic axis without an epsilon replacement, and all 361 raw samples remain preserved.

The reviewer viewed the delivered supplement at both preview and original resolution. The actual native PNG has the full neutron 10^-23 tick and n/particles-per-Href label visible; apparent clipping in the resized preview is not a file defect. All seven panels, 17 states including Li7 IV, line-style legend and captions are legible. Initial neutron and tritium growth is now resolved, OFF exact-zero n/T is explicitly annotated, and the axis correctly says elapsed proper time after source turn-on. This is a BBN-like presentation format, not a BBN calculation. Both figures receive PASS_SCOPED at their delivered size; no additional render is needed. The original postprocess used 2.050327 child CPU seconds, also within its bound.

## Scope of completion and positive transition

The approved phenomenological F5 trajectory/numerical-validation and F6 figure/review obligations are COMPLETE_SCOPED. Together with reused F0–F3 and the previously admitted phenomenological F4 subobligation, the approved phenomenological fast route is **7/7 COMPLETE_SCOPED**. Historical F4 physical-source qualification remains distinct. Original working 33/88 and central 28/88 gain no invented completion from this pilot; the inherited physical fast-route counter is not silently changed from 4/7. The new 7/7 statement is explicitly the phenomenological route, not physical/global completion.

No numerical repair or further case is required. Preserve the three raw cases, first-attempt receipts, numerical acceptance and figure artifacts; integrate the scoped decision and deliver the authorized result. Restore original policy ceilings while retaining actual cumulative debits and UNKNOWN_NOT_ZERO costs. Outside the consumed narrow exception, NO_MORE_IVPs remains in force. Calibration, self-consistent photon/temperature coupling, original global DAG closure and a new IVP campaign are not claimed or silently required for this completed finite result.
