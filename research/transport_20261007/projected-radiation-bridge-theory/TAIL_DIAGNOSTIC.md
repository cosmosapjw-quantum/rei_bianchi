# Source-off underflow diagnostic, not a coupled history

2026-10-07. This calculation directly substitutes the unchanged manufactured initial state into the inspected background and Verner HI formulas. It integrates no ODE and does not extrapolate an accepted new gas trajectory. The estimate is a diagnostic falsifier of the assumption that four short intervals necessarily stay in V2's normal-only lane.

Sources: the unchanged manufactured configuration in `../../../docs/research_program/igm_next_nodes_20261007/long-flrw/radau-p128-o2/config.cfg`; baseline `../../../rust/rei_microphysics/src/{igm_background,atomic_provider,hhe_events,igm_photo}.rs`; saved admitted `../short-hhe-coupling/results/reference_tighter.csv`. This note preserves the original source-bound calculation; it introduces no new numerical evidence.

At z=12, xHII=0.0002 and E=13.7 eV:

- nH=4.147707615519384e-4 cm^-3;
- nHe=3.274506012252144e-5 cm^-3;
- H=5.662042684402864e-17 s^-1;
- sigma_HI=6.22255406204696e-18 cm^2;
- lambda_HI=c nH (1-xHII) sigma_HI/H=1.3662730718869406e6 per unit ln(a);
- q_s=Q_t/[C E H]=20.46520339304923 photons/H/deta/ds.

Choose eta=s0+ln(13.7)+u with u=1e-5. Its source is active from s0 to s0+u, then off. Its HI exit is only at s0+u+ln(13.7/13.6), so it remains tracked throughout 8e-4. The characteristic starts at E=13.7 exp(u) rather than exactly 13.7 eV. Hold q and lambda at the displayed initial-gas, 13.7 eV values solely for this near-edge frozen estimate. Then f_off=q(1-exp(-lambda u))/lambda=1.4978835469122068e-5 and ln(f_off)=-11.108872321940957. For elapsed t>=u,

ln f(t)=ln(f_off)-lambda(t-u).

| elapsed ln(a) | source-off optical depth | ln f | ln(erg/H/deta) | physical E (eV) |
|---:|---:|---:|---:|---:|
| 2e-4 | 259.59188 | -270.70076 | -295.24321 | 13.697397 |
| 4e-4 | 532.84650 | -543.95537 | -568.49802 | 13.694658 |
| 6e-4 | 806.10111 | -817.20998 | -841.75284 | 13.691919 |
| 8e-4 | 1079.35573 | -1090.46460 | -1115.00765 | 13.689181 |

Binary64's smallest positive normal has log -708.3964185322641. The ideal round-to-nearest zero threshold is half the smallest subnormal, with log -1075 ln(2)=-745.1332191019412; a transcendental library's exact cutoff may differ by rounding details. Count density therefore reaches the normal floor near t=5.203573806422966e-4 and zero readout near t=5.472457101611829e-4 in this frozen estimate, before the third base endpoint. The energy readout is approximately 24.54 log units smaller and fails earlier; a geometric integration weight 0<w<1 reduces the weighted count/energy further. Source stock remains physically positive. Rust identifies f64 as binary64 and exposes the normal/subnormal distinction in its official documentation: https://doc.rust-lang.org/std/primitive.f64.html#associatedconstant.MIN_POSITIVE .

This is not a proof of the future coupled path. To avoid a zero count readout by t=8e-4 for this starting stock, its mean source-off opacity would need to be below about 9.291447427594941e5, roughly 68.0% of the initial value. The saved admitted first-interval continuous reference ends at xHII=0.00287353454613754, xHeII=0.008953843410726704, xHeIII=1.0927762016436629e-5, T=375.65375562359856 K. This supplies evidence that the earliest gas stays nearly neutral; it does not establish the other three intervals. Redshift changes 13.7 eV by only about 0.08% over the proposed window. Inference: underflow is strongly plausible already on this four-step problem and cannot be postponed as only a cosmological-long-history concern.

The witness does not have to equal a particular candidate quadrature node. It is a physical characteristic inside the low-edge source-off wake; continuous panel integration must represent the measure around it. An overly broad projection can smear a tiny physical wake into a larger readout, but that changes spectral shape and cannot be used as an underflow remedy. The exact eta at the lower endpoint is empty; interior eta with u>0 are not.

The inline Python arithmetic used only math, csv and json; no candidate executable, provider solver, ODE library, numerical integration history, or compilation was run. It transcribed the inspected formulas, read the saved reference endpoint, and printed these scalar values. No speed or runtime result is inferred.
