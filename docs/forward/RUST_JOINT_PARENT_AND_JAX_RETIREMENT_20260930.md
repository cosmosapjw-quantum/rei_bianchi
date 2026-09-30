# Shared-parent Rust development and legacy runtime retirement

The historical first-interval R2 run stopped at `[160,161]` because the
`log_T` local-error bound was `2.1245050576368385e-4`, above the strict
`<2e-4` limit. The accepted prefix ended at tick 160 and no rejected
candidate state was committed. That result and its source/judge identities
remain historical evidence; this development does not relabel it as a pass.

The Rust crate now exposes `joint_affine_difference`. Its two arguments are
affine enclosures expressed in the **same original parent coordinates**. It
subtracts coefficients before multiplying by the parent ranges and adds the
independently bounded nonlinear remainders. Inexact binary64 arithmetic is
expanded by one representable neighbor, while exact zero cancellations remain
zero; nonfinite inputs, shape/identity
mismatches, and unrepresentable finite bounds fail closed. A strict threshold
helper reports rejection without writing a candidate state. The synthetic
oracle reproduces zero difference for `F(x)=x/4+3/8` and
`H(H(x))=x/4+3/8`, despite a `1/4` cross-box extreme separation, and rejects
the `F(x)=x`, `H(H(x))=x/4` case at a `1/2` threshold.

The caller must still derive and independently certify the coefficient and
remainder bounds for the actual nonlinear, multi-site map. This primitive
cannot establish that the archived `[160,161]` attempt passes or replace its
frozen judge. The next executable science task is to version a successor map
contract, represent the common 46,080-node parent state, prove the full and
two-half affine remainders at all four source sites, and independently check
the resulting three-lane local-error certificate against the unchanged
`<2e-4` and `<2e-3` gates. No physical interval is authorized by the
synthetic tests alone.

The current branch no longer contains the retired `docs/legacy-python/`
package, its dependency lock, root-level bootstrap, executable cross-runtime
checker, or copied Python source subset from the old Rust handoff.
Historical stage source snapshots, raw receipts, and compact artifacts remain
untouched; prior
source bytes can be recovered by checking out their original Git commits.
The old `docs/forward/rust-20260922/` handoff commands describe that prior
checkout and must not be run as current development instructions.

Current acceptance commands from the repository root:

```bash
cargo fmt --manifest-path rust/rei_microphysics/Cargo.toml --all -- --check
cargo test --manifest-path rust/rei_microphysics/Cargo.toml --workspace --locked
cargo clippy --manifest-path rust/rei_microphysics/Cargo.toml --workspace --all-targets --locked -- -D warnings
python scripts/verify_repo.py
```
