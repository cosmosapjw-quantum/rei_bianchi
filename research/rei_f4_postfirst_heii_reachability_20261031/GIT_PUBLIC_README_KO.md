# REI F4: CCC6 post-first energy and He II source reachability (Physical Fast)

Bounded new research unit on immutable original PR313 HEAD `47f34ccb68f02262f40cd3dfd198aa97abd35183`.

Full **source-free** code, 192 new physical state rows, 3840 source-band rows, 1544 monoenergetic rows, 4 plots, tests, stage records, and exact SHA manifest are bundled in `REI_F4_POSTFIRST_HEII_20261031_SOURCE_FREE.zip`. Read `SCIENTIFIC_REPORT_KO.md` and `HANDOFF_NEXT_THREAD_KO.txt`. All code is in the archive and original numerical input is intentionally not included. This public release is NOT a source-inclusive rerun package.

To verify the public payload without private source: extract release ZIP and run `python code/verify_release.py --root EXTRACTED_DIR`. To re-run the source-backed physical calculation, provide the **previously existing** exact 3,813,471-byte original PR313 master, SHA-256 `4e8d4602cd2a8105c957fbda90eff23dede3eb7688013eb9d987fa58f870cdd4`, and extract the original into a directory. Run `python code/compute.py --source-root EXTRACTED_PR313 --grid 2100 --out RELEASE_DIR`. For physics tests also set `REI_F4_PARENT_ROOT` and `REI_F4_PARENT_ZIP` and execute `bash VERIFY.sh`. Previously recorded: original parent 32/32 tests +15 output +79 manifest, new scoped tests 24/24, grid 900 vs2100 PASS. No original Curtin He II σ(E) file was used; He II rows are **source-support kinematic eligibility**, NOT collision yields.

`WORKING=33/88; CENTRAL=28/88; PHYSICAL_FAST=4/7; CANONICAL_DELTA=0; F4=PARTIAL; L4_READY=false; PRODUCTION=HOLD; NO_MERGE; NO_FORCE_PUSH; NO_BUDGET_RESET; NO_NEW_IVP; AUTO_NEXT_NODE=false`.

Primary original source author database: https://atom.curtin.edu.au/CCC-WWW/index.html. Use the public 2026 complete Curtin He II ZIP, HI ZIP and HeI ZIP for the next scientifically novel channel rate construction, without interpreting CHIANTI's Maxwellian effective collision strength as energy-resolved σ(E).
