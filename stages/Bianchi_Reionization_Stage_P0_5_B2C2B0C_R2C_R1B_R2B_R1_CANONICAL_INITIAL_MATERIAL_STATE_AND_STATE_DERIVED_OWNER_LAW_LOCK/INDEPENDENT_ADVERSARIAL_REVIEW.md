# Independent adversarial review

## Attacks performed

1. Repeated identical evaluation must produce identical node hashes.
2. Any negative material-state component must fail closed.
3. Negative authoritative opacity must fail closed.
4. A nonzero target on exact-zero physical support must fail closed.
5. `EFFECTIVE_HI_SUBGRID` must have the exact resolved source vector `(0,0,0)`.
6. The primary subgrid lane must be named before inspecting results.
7. No result-dependent lane selection is allowed.
8. Explicit He II opacity must use `N_HeII/N_He`, not a hydrogen denominator.
9. Large optical depth must approach zero transmission without a physical-state clipping branch.

All attacks pass. A truncated code inspection briefly suggested an He II
denominator error; a direct formula regression test showed the implementation
already used the helium denominator. This false positive is retained as an
attempt receipt rather than rewritten as a discovered bug.

## Remaining vulnerabilities

- The external effective-HI global amplitude is not derived from the node state.
- The fixed hierarchy is an inherited representation choice, not a theorem of uniqueness.
- Thermal evolution, cooling, and unresolved-to-resolved energy exchange remain unintegrated.
- The large TV envelope between subgrid lanes must be propagated through the next history rerun.
