# Completed E1 plus two-photon Li I response

`code/li_e1_response.py` implements frozen `R9_UNIT7_LI_E1_RESPONSE_A2_v1` by finite weighted sums. It imports the unchanged A1 cross-section kernel and initializes its provider arrays from the A1 reconstruction, explicitly checking them against the byte-pinned A1 contract arrays. The 6,608 saved E1 transition rows are already mixture weighted; every row is summed once without an extra population factor or duplicate removal. Inputs are copied under `inputs/laneA2` with original/copied SHA256 and byte counts in `manifest.json`. A1 implementation, results and inputs remain unchanged.

The maximum actual E1 energy is 121.60088228541453 eV. Each mixture retains separate E1 and continuum support caps and their maximum combined cap, so lines above the two-photon endpoint are included. The five bands use the addendum's left-closed/right-open convention with the K edge owned by the extension. Only the first three bands are disjoint.

Continuum rows are selected by exactly 256 nodes and explicitly parsed `authoritative=True`. Their five response cells are copied directly into the completed table without recomputation; zero continuum cells changed. Combined response is the finite sum of E1 and stored continuum. There are exactly 1,440 response rows for 32 mixtures × five bands × three shells × three components. Full-source moments include subthreshold E1 photons. Summary fractions distinguish E1, continuum and inner-shell contributions to G/W/K.

One finite-sum execution and one focused validation completed in 0.06017520699970191 s measured inside the process, against the extra 5 s limit, with thread variables set to one. No A1 quadrature or convergence tests were rerun. The prior A1 authorized TEST_PLUMBING repair remains recorded as one; this new calculation required zero repairs.

```
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 timeout 5s python code/li_e1_response.py > results/laneA2/li_e1_run.log 2>&1
```

All eight focused checks passed. Maximum relative errors were 1.330565330242605e-16 for line energies and saved E1 moments, 5.978663639904903e-15 for combined source moments, and 3.7709573438479054e-16 for component/shell/band/energy algebra. Nonfinite/negative response coefficients, incorrect subedge inner response, changed continuum cells and response-row count differences were all exactly zero. At the largest actual E1 energy, the kernel gives 1s=0.9759634171183934 Mb and 2s=0.011275261325902885 Mb; 50-digit Decimal/log references give 0.9759634171183932 and 0.011275261325902883 Mb, with maximum relative discrepancy 2.27513245917183e-16.

For LiIII at n=3,5,10,12 the E1 fractions of event response are respectively 0.9664681618208092, 0.9837928739054099, 0.9946880066468861 and 0.9960950163236583. Their E1 fractions of primary kinetic energy are 0.9850484090093555, 0.9897454827314016, 0.9960377694018904 and 0.9970281360396288. All per-mixture values and source closures are preserved in the response, moments and summary files.

Requested executor: gpt-6.1-sol with high reasoning. Observed runtime model: UNKNOWN. Result status is PASS_PENDING_INDEPENDENT_AUTHORITY_REVIEW and inherits A1 admission status. The result is the completed-source smooth direct absorption, primary photoelectron kinetic energy and shell threshold bookkeeping under the same hypothetical incident normalization. It does not infer heat, relaxation yields, final charge fractions, transport, physical H(t) or NCP results.
