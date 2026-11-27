# Hex v2.02 newline importer evidence

Reviewer: `/root/source_physics`. Additional scope: one actual source function read to resolve the first real catalogue's delimiter failure. No numerical/scientific execution.

Source archive identity remains `ebb2695ff7dbf40274d329cf706a93e040d4997254c1f6677d0ccf791a9fe6ad`. Additional inspected file `hex-db/src/db.cpp` has SHA256 `5f932dfe4f985eee3560b8c466d7c5acdd16493abf3341cff01112527b2c5038`.

The actual `hex_import_` function uses `std::getline(is,cmd)` for each input line. Within the line it searches for a semicolon. If none exists, the search offset equals `cmd.size()`, so `cmd1=cmd.substr(0,cmd.size())` is the complete line and `cmd` becomes empty. The function passes `cmd1` directly into `sqlitepp::statement` and calls `st.exec()` before reading the next line. It also splits multiple semicolon-separated statements within a line. Newline-delimited statements without terminal semicolons are therefore accepted by the source importer.

The parent's bounded 65,536-byte decoded-prefix diagnosis found 937 LF bytes and no semicolons or quotes, with `BEGIN TRANSACTION` and subsequent individual `INSERT INTO tmat VALUES(...)` lines. This matches the observed importer convention. It does not establish the full dataset's tables, H1 coverage or ionf presence/absence.

**Minimal repair supported:** add an explicit source-generated line dialect; preserve semicolon mode as default and preserve the existing statement/decompressed-size caps. A successful line-dialect catalogue requires its own authorized invocation and receipt. No automatic physical or accuracy promotion follows. The real data availability status remains unknown until that catalogue completes.

The original R6 coefficient theorem, fixed-proton approximation and normalization obligations are unchanged.
