# XZ index compatibility repair

Current layer: validate. Existing public consumer unchanged; donor `_unpack_index` now processes every concatenated XZ stream and aligned null padding under the existing per-decoder memory and total output limits.

The exact acquired Packages.xz has two streams: the first returns 4,225,206 bytes, followed by a 32-byte empty stream. The old EOF/unused-data predicate rejected it. XZ format sections 2 and 2.2 permit this structure (https://tukaani.org/xz/xz-file-format.txt).

A new frozen public synthetic fixture reproduced one intended X01 assertion failure with zero errors/skips. The unchanged new suite then passed all 16 methods and 17 separately counted subcases. Existing test files and consumer bytes remain protected.

The original one-GET / one-consumer failure records are preserved. This repair authorizes offline validation of changed source; it creates no new Snapshot budget. Regressions and the exact real tuple run are next. Return is directly to MAIN_CONVERSATION without a WORK_THREAD prerequisite. No full census or host admission is implied.

Validation complete at candidate `744f684367375e546a30ce4d672d39cda50a0e18` / tree `abc953a7535b1be515fdcbc13ce0406ab6b9d489`: XZ 16 (17 subcases separately), donor 18, member 15, join 5, compatibility 7 methods PASS; repository verifier exit 0. Existing consumer and test bytes are unchanged.

The repaired real public consumer ran once offline in 1.0524 seconds under its 180-second outer limit, exit 0, no timeout. It returned `PASS_H1B1_AUTHENTICATED_DEB_MEMBERS`, actual signature evidence and the expected GCC control identity. Member `usr/bin/x86_64-linux-gnu-gcc-13` is a regular file, 1,023,032 bytes, SHA-256 `6117c52522997d2aaccb2b52b3c6bf42c0a6c5edb1d718431fed6b2fc5fec234`.

One PHYS-MATH provenance pass and one subsequent PHYS-MATH-CODE diff/evidence pass by the same LOCAL_CODEX assistant found no in-scope defect. This is sequential review, not independent review. No post-review source repair was needed. The original single-GET/single-call failure remains unchanged; new GETs are zero. `authority_effect=NONE`, `installed_files_verified=false`, `full_census_complete=false` remain unchanged. Publication/return readback is recorded in the external return, directly to MAIN_CONVERSATION.
