# REI-F02 frozen reference evidence

`decimal-oracle.json` stores independent Decimal(1100) endpoint and four event-count references for 103 cases. `verify_decimal.py` compiles a direct Rust consumer of the built crate and compares those stored values at relative 4e-14 plus two minimum-subnormal units. These are finite checks, not an interval enclosure or atomic accuracy claim.

Run from the repository root with the recorded Rust toolchain (the verifier uses `/home/cosmosapjw/.cargo/bin/rustc`):

```sh
cargo test --manifest-path rust/rei_microphysics/Cargo.toml --locked
mkdir -p .cuh/fastest-track/REI-F02
cp -n docs/atomic_reionization_handoff_20261004_v1/runtime_returns/evidence/F02_reference/decimal-oracle.json .cuh/fastest-track/REI-F02/
cp -n docs/atomic_reionization_handoff_20261004_v1/runtime_returns/evidence/F02_reference/verify_decimal.py .cuh/fastest-track/REI-F02/
python3 .cuh/fastest-track/REI-F02/verify_decimal.py
python3 docs/atomic_reionization_handoff_20261004_v1/runtime_returns/evidence/F02_reference/verify_helper.py docs/atomic_reionization_handoff_20261004_v1/runtime_returns/evidence/F02_reference/helper-source-003.rs
```

If those local files already exist, compare them with the archived references before using them; retain any different historical copies. The first two managed helper candidates failed their external checks; the third passed seven Decimal(90) points and the zero identity. `helper-attempts.json` retains actual candidate requests, responses, inference identities and known usage; placement is not broad role qualification. The initial first generation preceded freezing the helper oracle; repaired candidates used the frozen oracle.

`hydrogen_step.frozen.rs` is the initial test source. The committed test has formatting-only changes, recorded in `formatting_identity.json`. Source comment closeout after independent review changes no arithmetic. Full test and clippy logs precede that comment-only/formatting closeout; the final targeted six tests and fmt check follow it.
