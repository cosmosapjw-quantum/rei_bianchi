# R5/C6 interrupted-run recovery | 2026-10-18

Base R2 commit `7e41ab40e550a05f493c8c3ffe191569ce045732`; original native `35d9747a0bbedcafdb568467ce7c1e7a25f965b6`. Production sources and NCP jobs unchanged. Recovered README/THEORY drafts existed but their claimed code/results were absent from the current runtime; therefore the implementation and tests were recreated and executed, not inherited as PASS.

## Exact real-function comparison
For N'=j-kN, k=sum_i k_i, with nonnegative whole-slab bounds j-<=j<=j+, k_i-<=k_i<=k_i+, N-<=N(a)<=N+, h>0:

F(N,j,k,h)=N exp(-kh)+j h phi1(kh)
G(N,j,k,h)=N h phi1(kh)+j h^2 phi2(kh)
phi1(z)=(1-exp(-z))/z, phi1(0)=1
phi2(z)=(1-phi1(z))/z, phi2(0)=1/2.

Lower endpoint/exposure are F/G(N-,j-,k+,h); upper are F/G(N+,j+,k-,h). For the upper comparison, w=u-N obeys w'+k- w=(j+-j)+(k-k-)N>=0 and w(a)>=0; integrating factors give w>=0. The lower comparison follows symmetrically. Integrating the pointwise inequality gives the exposure bounds. Species events satisfy k_i- G-<=integral k_i N dx<=k_i+ G+. Physical binding energies and active fit thresholds remain distinct. This is a real-arithmetic theorem supplied with justified whole-slab coefficient bounds; endpoint samples alone do not provide those bounds. Binary64 implementation is NOT outward-certified interval arithmetic.

## Actually rerun
A behavioral RED test first failed for the missing enclosure, then GREEN. Final scalar suite: 27/27 pytest PASS including 70-digit phi functions, independent scaled Radau, two event positions, fit/binding and signed LRS energy bounds. Study: 36 configurations (2 event locations x 9 resolutions x split/unsplit), all truth-containment checks passed. Initial study-only schema error (duplicate n key) preserved and repaired without changing the scientific operator.

Manufactured j=1e-4(1+.3x), k_HI=105(1+.2x), k_HeI=85(1+.12x), k_HeII=130(1+.09(x-xstar)) 1[x>=xstar], E=80 eV. At xstar=.985 and 8 panels, survivor relative interval width 0.6440969640 unsplit versus 0.005620625341 split; HeII event widths 9.73072988864e-6 versus 1.32505670417e-8/H. The event is prescribed opacity, not a moving photon threshold. These are enclosure widths, not signed numerical errors or native accuracy.

Wolfram actual constant-flow RHS/exposure/conservation residuals: {0,0,0}.

## Next executable code repair
PR171 positive_native.rs fixes matrix common birth levels at [8,16,32]. Merely passing birth_count=64 fails native mesh-domain admission. Implement a separate opt-in native_refine command with explicit common_birth_levels and time_factor, retaining all original physical owners and old modes. Add a bounded resumable runner with source/binary/config identity, process cleanup, strict pre/post-birth matching, survivor-relative and HeI integrated-event diagnostics.

DAG: R2_RESTORED, R5_COMPARISON_COMPLETE, C6_SCALAR_27_PASS, NATIVE_REFINEMENT_OVERLAY_IN_PROGRESS. Native compile/run NOT_RUN; full source-native accuracy and PRODUCTION_SCIENTIFIC_ADMISSION remain HOLD/NOT_ISSUED.
