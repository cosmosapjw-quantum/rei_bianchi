# Original REI 26-event photon source | new actual finite response (2026-11-01)

**Draft PR #339** source-science HEAD `8a75ef0e0e0fdf287de45882cb45761a929ab02b`, immutable parent PR332 HEAD `2e3305c8ba9bff5d00412c5d79d9c1aa1e6f6e9a`. Original archived tick160 46,080-node source SHA256 `a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b`; source state SHA256 `cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab9999e7e3508a5161edb01`. Original central first-interval [160,161] error `2.1245050576368385e-4 > 2e-4` remains blocked.

## Actual implemented physics and exact result

Four original photon groups share THREE neutral atom sums `S=(N_HI,N_HeI,N_HeII)` over 46,080 nodes, with original H/He source normalization. At one original photon clock for fixed group `J_g,E_g,c_sg`, original node event source is `F_isg=J_g c_sg n_is / (E_g+Σ_t c_tg S_t)`. For initial vs accepted tick160 state representative at the **same photon clock**, let `D1=D0+δD`. Then `δF=L+R` **exactly** with `L=(J c /D0)(δn-n0 δD/D0)`, `R=-(δD/D1)L`. This shared-denominator rational identity and its accepted marginal whole-population-box SOURCE-ONLY analytic upper bound are DERIVED and Wolfram checked (residual zero). The bound is over the independent source population box at **fixed** original forcing, not the full original multistage thermal operator or forcing interval.

## Genuine frozen model data: same-clock counterfactual, NOT time-integrated history

Original actual `_explicit_photo_fields` + inherited excess photon energy; new nodewise source CSV **46,080 rows × 25 columns**, SHA256 `3516fb67993d1ad89f616f6a3dd9abcc295df2b866e57278dc02b8f87d0e2e14`.

| Derived original source quantity | Value | Unit |
|---|---:|---|
| Initial material photoheat at tick160 photon clock | 5.738106677340924e37 | erg/s |
| Accepted material photoheat at SAME source clock | 8.22713274931762e37 | erg/s |
| Exact finite source photon photoheat change | +2.489026071976695e37 | erg/s |
| Source Jacobian first-order term | +2.227205697394987e37 | erg/s |
| Exact original source nonlinear remainder | +2.6182037458170965e36 | erg/s |
| Conditional source-only all-parent-box photoheat remainder upper | 4.927163855442824e37 | erg/s |
| Original H I photoevent change | -2.3058996749749963e47 | events/s |
| Original He I photoevent change | +3.7875642516283944e48 | events/s |

The exact nonlinear term is 10.518988833804432% of finite photoheat change. Group 2 denominator changes 104.2899%, group1 5.1549%. The source all-X upper bound is conservative, source-only, fixed forcing and *NOT* an MPFR/MPFI/whole-step certificate.

## Validated computation and explicit failure correction

- Original source GitHub Actions [science #41281844433](https://github.com/cosmosapjw-quantum/rei_bianchi/actions/runs/41281844433) **SUCCESS**, [repo verify #41281843553](https://github.com/cosmosapjw-quantum/rei_bianchi/actions/runs/41281843553) **SUCCESS**. Nine normal and nine optimized source unit tests PASS. Original 46k source photo rates and photoheat independently compared with frozen PR332 source `do_case`, 46k source remainder bounds PASS.
- [Original Actions physical artifact #13072769613](https://github.com/cosmosapjw-quantum/rei_bianchi/actions/runs/41281844433/artifacts/13072769613) 8,981,204 bytes SHA256 `1e32d01e777f92fc5a6472ecdb43e5995c407c728d1e59722bfd3c536d446b03`; ZIP CRC PASS. Source-free pre-original artifact from PR332 SHA256 `83d94b5383ac7c1f36d89486e83bf8b4a56dd1993a25af3ae1f8fed06a695ba9`.
- Source-free complete local verification ZIP `REI_IGM_PR339_SOURCE_FREE_EXACT_PHOTON_REMAINDER_20261101.zip`: 12,972,935 bytes SHA256 `6b844a48be7110eef14d29fffb33c868b76ab9555d6daee7e2762d7ecb1c2272`, 36 ZIP entries, **35/35 payload SHA/CRC PASS in fresh isolated clean restore**, includes full original-source-derived model CSV, both original source-free GitHub Actions ZIPs, Decimal75, independent checker, plot, Korean report, R/C 20-stage records and executable handoff. Original private accepted-state archive is excluded: an original fresh IVP run needs the original source owner repository.
- Failure 1: naive difference of huge close photon rates caused cancellation in a small synthetic source scaling test; fixed by correlated finite formula and separate machine-epsilon-scaled check. Failure 2: malformed 63-character original accepted state hash in CI assertion, fixed by matching exact original 64-character SHA. These are implementation/verification errors, not physical nonexistence.
- Native subagent NOT_AVAILABLE; same-author hostile review and independent Decimal75, **NOT** separate author.

## Parallel sibling reconciliation and non-duplication (2026-11-01)

Concurrent source submap PRs from identical PR332:
- [PR337](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/337) science CI SUCCESS: four actual original photon/heat source evaluation sites and **conditional** low-rank implicit-stage Woodbury/Schur formula. This is *closer to the central full map* than this single-clock study.
- [PR338](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/338) and [PR342](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/342): equivalent exact finite source rational identities with their own source proof/clock scopes; science CI SUCCESS.
- [PR340](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/340): sharper independent-rectangle `(u,r)` source-only remainder extrema, science CI SUCCESS. **Do not compare numeric bounds before matching baseline, source-time, and box**.
- [PR341](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/341): exact 3×3×3 log-source-moment Hessian and source-only curvature bound, science CI SUCCESS.

Consequently PR339 **does not claim exclusive priority or a new canonical node**. Its bounded contribution is the original *initial-vs-tick160-accepted same-clock material counterfactual* source photon and photoheating 46,080-node numeric result, with independent source-owner crosscheck and tested finite remainder. All five PRs remain independently Draft/unmerged and have NOT certified full original source-correlated MPRK/SDIRK `D_h`.

## Scientific handoff and authority

The next actual scientific advance is to combine PR337 four source-evaluation-site structure (with photon population+implicit roots), PR340 sharp finite source remainder bounds, PR341 curvature, PR339 original photoheating and PR332 exact photon owner in ONE mathematically valid **joint same-parent and same-forcing** full-minus-two-half MPRK22/SDIRK2 difference map `D_h(X,Θ)` with rigorous interval Jacobian and uniform remainder, including source-time correlation/Hummer–Seaton events. Under unchanged original local-error `2e-4`, public width `2e-3`, retry ONLY original [160,161] when certificate valid, not a fresh entire IVP or another same-source source-only PR.

Reported central DAG **28/88**, working **33/88**, Physical Fast **4/7**, canonical delta **0**, full first interval **BLOCKED_MINIMUM_STEP**, production **HOLD**, no merge/force-push/tolerance relaxation/budget reset/auto-next. Source and H/He original parent branches immutable. **Google Drive readback-verified native text secondary backup**: [REI PR339 physics and 20 stage ledger](https://docs.google.com/document/d/1EJzwYkzdGIZyAlgkQDDiWFIUAfD_5B9F_1Dw1qQXOlY/edit). **Drive binary ZIP mirror NOT VERIFIED.**
