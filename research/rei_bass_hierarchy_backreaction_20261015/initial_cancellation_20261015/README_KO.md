# Initial Sigma and Pi_ab independent Einstein-Vlasov source research

Actually authored/executed directly in ChatGPT on the user's Ubuntu workstation. Selected new constructive source-bound initial-condition sensitivity / C8 numeric research step, NOT a resumed old AX08 chemical solver run. Actual original rei_bianchi owner checkout and AX08 full saved checkpoint/source bytes untouched. Native AI subagents were not available (NOT_RUN); real Python 1/2/4 processes are ordinary local CPU parallelism.

Parent REI massive gamma/nu finite radial hierarchy PR140 HEAD b1cba753083ad83049c23ff538834564b49b7b6e. Original BASS160 parent source 9e50f936f3289cb0c7c8127772cf9fb8d172d7a8, sigma_matter.py SHA1857567475b1c8586298f868e5420aae7a72e8e1ba69cce6a5b21bfca4fdd790. Original REI source cosmology and proper zbar20 to zbar4 interval unchanged. Fixed sign/normalization: user Sigma=sqrt(3)abs(s)/H, separate orientation sign(s); physical shear sigma=diag(-s,-s,2s); pi=diag(-pi_s,-pi_s,2pi_s), pi_s=(p_parallel-p_perp)/3 [Pa]. Original q_ref is an internal signed IC adapter only.

Physical independently calculated objective: with strictly positive source-locked gamma/nu/massive angular quadrupoles W=1+A P2, find signed initial q_ref such that terminal signed s/H=0, not nonnegative Sigma alone. Despite this cancellation, b_end remains nonzero, proving an explicit source-specific integrated metric and photon directional-redshift memory.

Key files:
- initial_cancellation.py: real Einstein/PR140 active massive velocity-index ODE and signed brentq shooting. 8 source cases with and without original saved ZERO HHe electron donor for gamma-only Thomson. Exact source IDs frozen. Never edits owner solver.
- trajectory_memory.py: three complete Einstein source histories 3x401=1203 physical samples and collisionless Killing photon transverse/axial redshift ratio.
- export_rei_background.py: actual 24 Einstein physical/sensitivity histories x161=3864 row typed CSV with H,s,Sigma,sign,b,t, H_perp/H_parallel, individual Pi_gamma/Pi_nu/Pi_massive, positive photon/neutrino number, energy sector, original one-way ne. This is a RESEARCH supplier; the stressfree native AxbiBackground with s~a^-3 CANNOT consume it unmodified.
- rust_pi_supplier_consumer.rs: actual independently compiled no-deps native Rust streaming 3864 rows, verifies Einstein H constraint, shear/Pi tensor normalizations and physical source/clock; validate_native_intake.py runs three real altered-source rejection paths exit3, leaves original CRC/SHA untouched.
- benchmark_parallel.py: 8 full signed root solves each repetition, actual 1/2/4-process independent run, 4-process ~3.58x root-search throughput on 8 cases, bitwise identical physical roots (not full H/He/RT solver speed).
- benchmark_memory.py: 768 real source finite-mass J0/J2/J4 moments, fair once-per-all-moments original scalar reference and vector chunk4/8/16/32/64/128. Chunk16 2.31x faster, peak2.878MB traced vs chunk32 2.33x,peak5.647MB.
- wolfram_sigma_pi.wl: actual native Wolfram15 seven exact zero source tensor, Green identity, signed q/Sigma and positive-P2 normalization checks; original xAct covariant checks are inherited from PR136/PR140.
- test_initial_cancellation.py: 30 new source/physics/independent gravity/negative and real output tests PASS; original parent test_massive_radial.py 13 PASS.
- REPORT_KO.md full Korean derivation/results/gates; provenance JSON with source hashes, actual commands and science claims.
- figures: compensation roots with no/saved real HHe electron Thomson, signed s/H(zbar), and separate b(zbar) metric memory.

Actual CUDA/GPU not used or claimed faster. Original HHe ne donor is a separate user-owned 312238-row original ZERO source and is intentionally not rebundled in this research capsule. For Thomson OFF results the pinned public source files are enough. The real donor SHA in the evidence is 4f6852c3a5152b91224ce5fecad6ccdfe9f7ece4c8a6d39825c6f5e5ca8ae92f and source interpolation uncertainty remains ~1.9755e-4, much larger than isolated numerical ODE error.

Under the repository root:
  OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 research/rei_bass_hierarchy_backreaction_20261015/initial_cancellation_20261015/initial_cancellation.py --output /tmp/initial_pi_no_thomson.json
  OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 -m pytest -q research/rei_bass_hierarchy_backreaction_20261015/initial_cancellation_20261015/test_initial_cancellation.py
  python3 research/rei_bass_hierarchy_backreaction_20261015/initial_cancellation_20261015/validate_native_intake.py --output /tmp/initial_pi_rust_validation.json
  python3 research/rei_bass_hierarchy_backreaction_20261015/initial_cancellation_20261015/plot_initial_cancellation.py

Warning: the controller/reionization native driver and old checkpoints are still source-frozen for stressfree s∝a^-3, NOT a physically admissible Einstein-Pi driver. This new bridge is explicitly opt-in, not a merged or background-replaced full AX08 scientific run.
