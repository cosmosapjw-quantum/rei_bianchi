# Negative results

- A thermal secant evaluated across different branch-parameter boxes produced a
  false derivative lower bound.
- Fixed 80-step bisection inside 20 outer cycles added runtime without stronger
  validation.
- Propagating a Krawczyk construction tube rather than the certified image
  produced a false trace-population cone failure.
- Margin-only stagewise containment was insufficient; direct endpoint replay was
  required.
- Partition 1024 encloses the map but fails the `2e-4` validated local-error gate.
- The first repository-wide Rust regression failed before the pinned toolchain
  was restored; the unchanged test passed after environment recovery.
