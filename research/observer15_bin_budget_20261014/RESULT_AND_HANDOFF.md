# OBSERVER15 R5: source-clock aware finite observer bins

Date: 2026-10-14 KST. Unit: SOURCE07-CONSUMER-OBSERVER15-R5.
Parent: f0038d987ac60eacd4010da336bcafdcd12741d9, OBSERVER14-R2. This is an additive R5 constructive result with stage-local checks, not all ten stages, not full SOURCE07-CONSUMER admission, and not a native production adapter.

## Durable full payload

The complete Korean derivation REPORT_KO.md (O15.1–25), executable Python reference/checks, exact-rational certificate, immutable source CSV and parent documents, Wolfram/xAct submitted input and actual results, failure ledger, source map, state and handoff are in:

- Drive ID: `1NFU3EFmTaTmqtwrwM27HXDKVETW4YENO`
- URL: https://drive.google.com/file/d/1NFU3EFmTaTmqtwrwM27HXDKVETW4YENO/view
- Name: `REI_OBSERVER15_R5_20261014_SOURCE.zip`
- Size: 116856 bytes; 59 ZIP members, 58 manifested payload files.
- SHA256: `3475c3372f8dfc5c45a623d660b515676992805e6400fa5402fd0d4179c3d324`
- Actual create-only upload acknowledged and Drive metadata size/parent readback matched. No restore claim.

This repository file is the result/restore entrypoint, not a claim that every archive member has been expanded into Git. Download the archive through the authorized Drive connector; verify SHA256, then read HANDOFF_KO.md. No user re-upload is necessary.

## Exact current/source-clock interface

Signature (-+++), x0=ct, u.u=-1, dx=c k ds. With q_a=c grad_a(theta), u.q=1, D=-u.k>0, A=q.k=dtheta/ds>0, a pure bulk total-free-electron current J=c N_e u/V gives

`d tau = -(sigma_T/c) J.dx = c sigma_T (N_e/V) D ds = [c sigma_T D/(V A)] N_e dtheta`.

A need not equal D. Transform q, u and k together. Spatial-current contributions or energy-dependent Klein–Nishina opacity need their own terms. HE PR42 R7 at a4874b6483e66c310b76d645b2326f3b71721b49 supplies the D/A clock distinction; CR PR53 at cc3249947a1fc93f2bacf2190604371dfde2f42f supplies the source-matched donor plus nonzero geometry-work error structure. Both compact proof texts were actually read. Their different static/moving numerical centers are NOT transplanted into this REI fixture. The obsolete 2 Delta E stopping norm is not used.

## Same-tail bin and second-order covariance

T is optical depth from the near edge to the observer, including only a separately supplied unresolved foreground contribution. B>=0 is optical depth between the far and near edges.

`P=exp(-T)*(1-exp(-B))=-exp(-T)*expm1(-B)`.

For T in [Tlo,Thi], B in [Blo,Bhi], all nonnegative:

`P in [exp(-Thi)*(1-exp(-Blo)), exp(-Tlo)*(1-exp(-Bhi))]`.

This is a valid outer-box bound even with correlated physical inputs; joint endpoint attainability is not claimed. Conditional near-edge survival gives P/exp(-T)=1-exp(-B), not a normalization of the finite bin to unity. Angular averaging must not be interchanged with this conditioning. Adjacent bins telescope with the remaining far survival.

Let T=T0+eps T1+eps^2 T2 and B=B0+eps B1+eps^2 B2, with the factorial included in the second coefficient. Then

`P2=(T1^2/2-T2)*P0 + exp(-T0-B0)*(B2-T1*B1-B1^2/2)`.

The cross-boundary term -T1*B1 is required. For an isotropic baseline with STF first-order tensors A and C,

`<P2>=P0*(tr(A^2)/15-<T2>)+exp(-T0-B0)*(<B2>-[2tr(A C)+tr(C^2)]/15)`.

Use inherited O14 moving-endpoint and event-aware cumulative coefficients once. Do not add THRESHOLD13 event terms twice.

## Pre-bin source memory

For e=N-hat N and residual r=hat N'-F(hat Y), the error in B_[a,b] is

`delta B = e(theta0)*integral_a^b w + integral_theta0^b W_ab(s)*[F(Y)-F(hat Y)-r](s) ds`,

where `W_ab(s)=integral_max(a,s)^b w` for s<=b. Pre-bin residuals s<a remain present unless e(a) has already been propagated. If the weight changes, add `integral (w-hat w)*hat N` rather than hiding geometry error in a same-source bound.

## Source-specific curvature bound, without an ODE rerun

Use the actual SHEAR12 source-free baseline, positive photon measure, u=t/t_star in [0,.5], H=1/25, k<=2/5, N_gamma<=7/10, q in [65,110] eV, h<=1 and z,v<=Y=2/25. Its specified smooth cross sections have A=(1,2,4), powers p=(3,5/2,7/2).

Exact positive rational Taylor bounds prove exp(1/50)<650/637, hence E>63.7 eV, above the highest threshold 54.42 eV. Exact rational comparisons give relative cross-section bounds (.01,.19,2.31). With I_a=k r_a integral(s_a F),

`h'=-I_H; z'=-I_HeI; v'=I_HeI-I_HeII; xi'=integral kappa F`,

`F'=-kappa F`, `xi''=integral (kappa'-kappa^2) F`,

`kappa'=k sum_a s_a [r_a'+H(p_a-3)r_a]`.

The bounds yield kappa<=.084, |kappa'|<=.053678656 and therefore

`sup |d^2 xi/du^2| <= .7*(.053678656+.084^2) = .0425142592`.

For exact source nodal values, a linear interpolation cell of length h has error <= Kmax M2 h^3/12. The bin [.20,.25] has ten h=1/200 cells, Kmax=.4, giving

`E_bin_interp/(sigma_T/sigma_*) <= 1.771427466666...e-9`.

The near history [.25,.5] gives 8.857137333333...e-9 times the same ratio. An explicitly bounded timestamp-to-rational-grid shift is added separately. This is an analytic source-model interpolation bound, not a finite-difference estimate and NOT the original ODE-node error. Extra CI/RR/source terms or nonzero-epsilon backgrounds require their own derivative terms.

## Actual saved baseline-bin result

Consumed immutable 101-node CSV SHA256 `69bceac64e356d202c4cc4cb8c3db35d9e37c632df7d37bc6219f7c53a696927`. Observer u=.5, near .25, far .20. Baseline observed redshifts are .010050167084168... and .012072288866078.... A declared positive linear reconstruction gives

`Cn=.01011097647080279076755775656577062339...`

`CB=.00204512358034008482274160680248509077...`

Return the physical normalization symbolically:

`P(r,tail)=exp(-tail-r*Cn)*(1-exp(-r*CB)), r=sigma_T/sigma_*`.

At the explicitly synthetic control r=1, tail=.25, P=.001575109595284263291801900138.... The .25 boundary-survival control is not a recovered cosmological tail at the fixed geometry endpoint.

With exact source nodes as an ADDITIONAL assumption, the proven interpolation and timestamp contributions give P in [.0015751082184131174..., .0015751109721554311...]. Full model interval remains null because source-node ODE error, physical r and physical observer tail are not bound. The separate outward interval of the exact declared interpolant is arithmetic verification, not a 60-digit physical-accuracy claim.

The bin reconstruction differs from the saved cumulative column by 6.3773465675e-12; that diagnostic difference is not used as a continuum error certificate. Twelve finite-epsilon readouts use the explicitly reconstructed xi0+eps^2 xi2 family and exact geometric roots; they are not new full coupled finite-epsilon histories.

## Actual verification and boundaries

- 97 new reference checks passed; 8 exact-rational source checks passed; a separate positive rational-series/outward Decimal reference interval was verified.
- The literal survival difference first failed the T=.25,B=1e-20 regression by returning zero. The identical focused test passed after the expm1 repair. This was a new reference negative control, not an upstream production bug claim.
- Cloud Wolfram 15.0.1 returned 17 zero scalar groups. Power::infy/Infinity::indet warnings were retained; no warning-free claim.
- Actual remote Wolfram Engine 15.0.0 with xTensor1.3.0/xCoba0.8.6 returned 9 zero CTensor/covariant-derivative residuals and exit0. xTensor.m SHA256 `04e1cf3c7e81f1eff61ca633c84537c3f3cbb0fdd42ea01441e89172086d8b36`.
- Unqualified $Version in the initial xAct metadata resolved to the package version. Raw result preserved; System`$Version queried separately; tensor work not replayed to erase the record.
- No upstream scientific suite, source ODE, atomic campaign, native adapter or HPC run. No external independent scientific reviewer/native subagent. CR/RCT/HH OFF. No main merge or force push.

BASS PR141 prelaunch-hash HOLD, BASS PR142 observer-cap ownership, HH PR58 finite-rate scope and REC PR83 FLRW-only export were read at PR metadata level and retained, not promoted or imported as new physical results.

## Next

Use this R5 result for scoped R6 review and the EXISTING SOURCE07-CONSUMER binding. Retrieve same-source supplier node-error/signed-residual evidence, physical r, observer tail and tolerance. Preserve the now-completed interpolation certificate. Do not restart atomic precision, old S12/O14 checks, all-repository synchronization or production campaigns as prerequisites. Full details, runnable code, receipts and failure ledger are in the immutable archive above.
