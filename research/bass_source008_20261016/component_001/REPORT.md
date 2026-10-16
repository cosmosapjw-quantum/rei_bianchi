# Source008 opt-in finite component observations

COLD_FLRW then SIGNED_MINUS each completed once with --inactive-hi-split: four main steps plus two replay steps. Both exit0 and meet frozen native residual/restart/domain gates. Each has52 main RHS plus26 replay RHS; total156. New wall0.10082243499346077s of120; prior008compile/test13.443409030907787s remains unchanged.

Actual runtime compiled identity72ed655e55cbac84e5cc453a07b7db0f06988876323d330f168c131cab81844d matches source008 binary25b0d35c8c338aecac75e0e888a0d467e1cf051f71f436b70360f8a1d742d37c and selected table/flag metadata. Actual launch HEAD4ad8dd1c5a3f48329fe49ae0c394c4deffcd1c9c.

| Case | Midpoint2-step passive N/H | Midpoint Uq eV/H | Midpoint populated cells | Final4-step passive N/H | Final passive physical U eV/H |
|---|---:|---:|---:|---:|---:|
| COLD_FLRW | 3.404457930662348e-12 | 4.630641903731809e-11 | 8 | 7.959007187911283e-12 | 1.082235776261859e-10 |
| SIGNED_MINUS | 3.404457521043274e-12 | 4.630641392918476e-11 | 8 | 7.959006760402061e-12 | 1.082235703022507e-10 |

Nonzero passive transfer is observed in these finite components. Native final outputs do not emit final passive Uq or populated-cell count, so those fields remain null/NOT_RECORDED; midpoint six-array checkpoint values are not relabeled final.

Source007 coarse results were reused without rerun. Actual endpoint a bits match in both cases, while several numeric endpoint observables differ. Diagnostic signed differences source008-source007 include:
- COLD_FLRW: {"photon_n_per_H": -1.9003119967912314e-09, "photon_u_eV_per_H": -2.5839082805797825e-08, "temperature_K": -2.515228914035106e-09, "x_HII": 1.9002202603579047e-09}.
- SIGNED_MINUS: {"photon_n_per_H": -1.9002152926077065e-09, "photon_u_eV_per_H": -2.5837767484503823e-08, "temperature_K": -2.5158080063647503e-09, "x_HII": 1.900123565488996e-09}.

All raw differences are preserved in SOURCE007_DIAGNOSTIC_COMPARISON.json without a new acceptance tolerance, bit-parity claim or scientific-equivalence assertion. They require independent interpretation. No new source/build/test/coarse run was performed.

Fresh independent result review is pending. Scientific admission remains NOT_ISSUED, full/adaptive/history/Bianchi admission HOLD, and source007 time-convergence HOLD unchanged.

The initial assembly draft contained generic passivezero/bitparity prose inconsistent with computed actual values. It is retained under raw/INITIAL_FACTUAL_ASSEMBLY_DRAFT for transparency and superseded by this report; native outputs were not changed.
