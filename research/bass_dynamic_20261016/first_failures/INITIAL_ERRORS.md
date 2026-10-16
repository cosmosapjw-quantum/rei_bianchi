# First failures and fixes

- Initial `rsync` used its default SSH transport without the NCP key and
  exited 255 (`Permission denied (publickey,password)`). A new command used
  `-e 'ssh -i /home/cosmosapjw/.ssh/ncp_key ...'`; no owner path was changed.
- The first COLD_FLRW four-step trial had photon/energy ledger parity, but the
  adaptive proposal returned `Ok(false)` after a large error. The first
  example mislabeled that as PASS. The release executor records actual
  rejection and subsequent acceptance (up to 18 rejections).
- After adding signed redshift-work test, `test-redshift-first.log` in the
  corrected evidence tar records `work=2.946867793687802e-6` versus
  `u0-u1=2.999850005e-6` eV/H. A multiline `self.background` call in
  `photon_inventory` still used AXBI geometry; routing it through
  `geometry_point` made the test pass. All physical mini-histories were rerun.
- The first Python/Rust source-table clock comparison found `7.570745e-9`
  maximum relative mismatch. The provider had used producer cumulative
  `proper_elapsed_s`; GL8 reconstruction reduced the final maximum to
  `2.888705e-16`. The earlier raw comparisons remain in the first and
  corrected evidence archives.
- NCP system `python3` initially exited 1 because NumPy was unavailable;
  the first tool output showed `ModuleNotFoundError: No module named 'numpy'`.
  The remote `python-clock.stderr` was overwritten by the later successful
  invocation; no raw first-failure log survives for this command. The
  successful comparison used an existing REI venv read-only.
- The exploratory 128-step fixed run exited 2 with `AXBI_STEP_CAP` at the
  mini executor's original 100-step cap (`step_cap_128.log`). The bounded
  diagnostic cap was raised to 512. Solver tolerance was unchanged.
- Repository-wide `cargo fmt --all -- --check` exits 1 on 16 files
  (`cargo_fmt_check.log.gz`). GitHub PR159 `verify` failed twice at this gate;
  `github_ci_fmt.log.gz` retains one exact compressed raw job log. REI PR150 base also has two
  failed `verify` jobs at the same formatting gate. The new driver/test
  additions contribute some format differences; this Draft PR does not
  claim CI PASS. No broad format rewrite was applied to the 13 inherited
  files, and the scientific source-bound checkpoint identity was not changed
  after the release calculations merely to reformat code.

The release archive and release numerical summaries are the authoritative
post-repair results. Superseded archives and comparison JSON files are kept
only as failure and repair evidence.
