# XZ index compatibility repair

Current layer: validate. Existing public consumer unchanged; donor `_unpack_index` now processes every concatenated XZ stream and aligned null padding under the existing per-decoder memory and total output limits.

The exact acquired Packages.xz has two streams: the first returns 4,225,206 bytes, followed by a 32-byte empty stream. The old EOF/unused-data predicate rejected it. XZ format sections 2 and 2.2 permit this structure (https://tukaani.org/xz/xz-file-format.txt).

A new frozen public synthetic fixture reproduced one intended X01 assertion failure with zero errors/skips. The unchanged new suite then passed all 16 methods and 17 separately counted subcases. Existing test files and consumer bytes remain protected.

The original one-GET / one-consumer failure records are preserved. This repair authorizes offline validation of changed source; it creates no new Snapshot budget. Regressions and the exact real tuple run are next. Return is directly to MAIN_CONVERSATION without a WORK_THREAD prerequisite. No full census or host admission is implied.
