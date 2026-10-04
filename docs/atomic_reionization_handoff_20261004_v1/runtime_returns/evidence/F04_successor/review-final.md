- **P2 — Silent event underflow erases representable fraction derivatives.** In [ft03_controlled.rs:90](/home/cosmosapjw/Dropbox/bianchi/rei_bianchi/rust/rei_microphysics/src/ft03_controlled.rs:90), volumetric rates underflow before division by nuclear density at line 111. Executed minimal trigger:

  ```rust
  let mut m = Ft03Model::controlled().unwrap();
  m.gas.n_h_cm3 = 1e-320;
  let mut s = m.initial_state();
  s.photon_cm3 = [0.0; 3];
  ```

  At `T=50000`, `ft03_rhs` returns `Ok` with `derivative[0]=0.0`; the equivalent per-capita expression gives `7.713492975272601e-16`. An implicit step with `dt=1e11` returns `FT03_NONCONVERGENCE`. The same silent loss occurs with entirely normal positive density inputs, `nH=1e-300`, `nHe=8.3e-20`: expected hydrogen derivative `7.7134929752726e-30`, observed zero.

  Smallest repair: detect and reject unrepresentable volumetric event products before returning an apparently valid RHS, preserving transactional rejection and existing tolerances. Reproducer sources: [original probe](/tmp/rei_f04_review_probe.rs), [normal-input probe](/tmp/rei_f04_review_probe_normal.rs). Exact compilation/execution commands were sent to the parent; raw output remains in the tool transcript.

No other concrete finding identified within the frozen scope. All seven scoped hashes matched before and after review. Direct execution of the existing focused test binary passed **8/8**; the `1e14` example completed with **1024 accepted steps, 10 rejected trials, zero rejected writes**. Full-suite/refinement receipts were inspected; the external validator was not rerun.

This finding concerns mutable-density inputs and does not invalidate the recorded nominal trajectory. No code or validator changes were made. Uniform bounds, root certification, physical accuracy, and scientific admission remain outside this evidence.
