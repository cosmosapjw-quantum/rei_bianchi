# Local Codex resume prompt — Git-small authority intake

Continue the stacked REI-LOCAL-01 handoff from the exact remote head of
`agent/implementation/rei-git-authority-transport-20260831-r1` in a new
isolated worktree. Verify Git object integrity plus the parent handoff's
`MANIFEST.sha256` and this directory's `MANIFEST.sha256` before using their
contents.

The four small exact input bytes are already Git-resident under
`small_inputs/`; do not ask the user to download them. Ask only for one
absolute, real non-symlink directory containing this downloaded Rust archive:

```text
08-rust-1.94.1-x86_64-unknown-linux-gnu.tar.xz
size        192287020
SHA-256     294b3d81fa72e62581276290c60c81eb8b58498d333d422ca1dfc432877d0c40
```

Run `materialize_small_plus_rust.py` first to construct a fresh staged source
root and byte-bound mixed-source receipt. Then pass that staged root to the
existing `../materialize_authority.py`, require its idempotent replay, and
continue only if the 36-path `INPUT_LOCK.json` replay succeeds. Do not extract,
execute, source, import, or otherwise consume any authority member before
those gates. If the Rust archive locator or its exact bytes are absent, record
`RUST_ARCHIVE_SOURCE_MISSING` or the precise digest failure, push a durable
stacked draft checkpoint, and stop all successors.

`LOCAL_CODEX_JOB_PROMPT.md` and `LOCAL_EXECUTION_PROMPT.md` one directory up
remain the full normative procedure. The claim ceiling is unchanged:
`STOP_INVALID` and `NO_PASS_FIRST_CANONICAL_INTERVAL`; do not run the
46,080-by-3 canonical pilot or a JAX/jaxlib path.
