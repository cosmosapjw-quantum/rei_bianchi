# VigilODE branch coverage

Observed 2026-10-21T21:23:32.817Z–2026-10-21T21:24:43.841Z through the GitHub connector.

The current branch collection returned **187 branches, representing 177 distinct HEAD commits**. Pages contained 100, 87, and 0 branches; the final empty page closes enumeration. Exact-SHA metadata was retrieved for all 177 HEADs, with no missing metadata. Reads occurred over an interval rather than an atomic snapshot.

## Coverage boundary

This completes branch-name and HEAD-metadata coverage. It does **not** claim that all 187 branches' source, evidence, or scientific conclusions were content-audited. The controller reported prior content reads at the three anchors below; those reads were not repeated here. The later bounded content-update section records reads of three newer HEADs; other entries remain metadata-only. Commit dates are not branch creation dates or readiness assessments. No physics, implementation, tests, benchmarks, or IVPs were run; the completed 83-IVP evidence is untouched.

## Supplied anchors and ancestry

| Role | Branch | Exact HEAD | Committer date (UTC) |
|---|---|---|---|
| main | main | 8d0c79184e09efb5bdadc24a6315c60a71a44264 | 2026-08-26T06:10:12Z |
| integrated | audit/production-reaudit-20261021 | de4c10a9f41321beef2313a3d7fb503bab35d714 | 2026-10-21T05:29:46Z |
| external_audit | audit/ncp-intensive-120m-20261021 | 7a63876a97fc17f640771ec06658269947049994 | 2026-10-21T07:29:54Z |

GitHub comparison reports the integrated anchor **794 commits ahead and 0 behind main**. The supplied external audit is **1 commit ahead and 0 behind the integrated anchor**, with the integrated anchor its direct parent. These comparisons establish ancestry only.

## Newer heads identified for bounded content intake

Three current HEADs have committer dates newer than the supplied external-audit anchor. Their commit subjects are metadata, not adopted scientific conclusions.

| Branch | Exact HEAD | Committer date (UTC) | Commit subject |
|---|---|---|---|
| research/bassrei-port-20261021 | c4d9eb9f76ac1fbcbb4a12fb920d05e4c2317fa9 | 2026-10-21T21:08:19Z | Preregister BASS/rei node P02b (supersedes L-0148) |
| results/ncp-followup-fvm-5fd6e45 | fbbc832fdf942396155c12b04c30e63dc67fefe9 | 2026-10-21T11:43:45Z | Publish NCP follow-up audit bundle for source 5fd6e459 (scoped, production HOLD) |
| research/ncp-followup-fvm-20261021 | 5fd6e459a3f67cee90e002821b9b4b740c47475b | 2026-10-21T07:58:59Z | Audit NCP evidence and implement scoped Schur, remap and Bianchi FVM follow-up |

## Complete branch inventory

Every row below was enumerated and resolved to exact-SHA metadata. Full messages, tree/parent SHAs, author/committer dates, URLs and per-row content-audit labels are in `VIGILODE_BRANCH_COVERAGE.json`.

| Branch | Exact HEAD | Author date (UTC) | Committer date (UTC) |
|---|---|---|---|
| audit/adversarial-audit-20260927 | e1c3a5f14df7973ede74d77b9efc95be008f95de | 2026-09-28T11:53:42Z | 2026-09-28T11:53:42Z |
| audit/ncp-intensive-120m-20261021 | 7a63876a97fc17f640771ec06658269947049994 | 2026-10-21T07:29:54Z | 2026-10-21T07:29:54Z |
| audit/production-readiness-20261018 | da91553f019e011556ee042975f3cf05fc21a7c7 | 2026-10-19T05:14:40Z | 2026-10-19T05:14:40Z |
| audit/production-reaudit-20261021 | de4c10a9f41321beef2313a3d7fb503bab35d714 | 2026-10-21T05:29:46Z | 2026-10-21T05:29:46Z |
| audit/rvj-accuracy-speed-reaudit-20261010 | 4c643172ec488f0ae9108f574915a9bb5069fd3e | 2026-10-10T10:51:07Z | 2026-10-10T10:51:07Z |
| audit/rvj-accuracy-speed-wave1-20261010 | f5a1a7b03af55f2bd986ce439a20a709542a9a43 | 2026-10-10T19:28:05Z | 2026-10-10T19:28:05Z |
| audit/rvj-algorithmic-directions-20261008 | cfed140bf127f5aa8fcf4fe4c16689d7de062b87 | 2026-10-10T08:37:37Z | 2026-10-10T08:37:37Z |
| audit/rvj-controller-grid-ct01-20261010 | 0ce7c3275625dcac46e323dd7eaf17efa961fbdf | 2026-10-10T23:12:34Z | 2026-10-10T23:12:34Z |
| audit/rvj-native-followup-20261003 | 826fa05cc1fdaf7b1a0cf7ac45116596b4ddff65 | 2026-10-03T16:45:12Z | 2026-10-03T16:45:12Z |
| audit/rvj-reaudit-remaining-20261011 | 76e59c691845851274cf27b26678cdb128daa408 | 2026-10-12T07:55:02Z | 2026-10-12T07:55:02Z |
| audit/rvj-research-integration-20261004 | 4de1f88cbe2c3fe846c15a6e5015845a136ba2b9 | 2026-10-05T10:31:08Z | 2026-10-05T10:31:08Z |
| audit/rvj-speed-research-20261005 | a49f7e4abacfd88c6da3200055467fcd717464cf | 2026-10-07T14:44:10Z | 2026-10-07T14:44:10Z |
| bootstrap/import-v3.5-durable-baseline | a487af280507947db025570c00b87289a70de4f1 | 2026-08-18T18:44:18Z | 2026-08-18T18:44:18Z |
| bootstrap/import-v3.5-source | 3ca35390e497dd0cc9b549fad1c8c1d1b1ac4814 | 2026-08-19T00:46:57Z | 2026-08-19T00:46:57Z |
| bootstrap/import-v3.5-source-patch | e25d541b759857c26e4edf4ea72ba48697a73a84 | 2026-08-19T00:50:11Z | 2026-08-19T00:50:11Z |
| bootstrap/import-v3.5-verified-baseline | 501b15e19e888d17f4fdf0171f4a24660ea0e406 | 2026-08-19T14:56:16Z | 2026-08-19T14:56:16Z |
| chore/repo-hygiene-20261019 | 57840c749ca51642bf828ce43f5d6273d21ea05f | 2026-10-19T13:51:32Z | 2026-10-19T13:51:32Z |
| claude/jolly-wozniak-7wl15h-integration | ff84ed6c196bb0d9fbb9985b80e5d24517dbe5d2 | 2026-09-29T22:40:17Z | 2026-09-29T22:40:17Z |
| claude/jolly-wozniak-7wl15h-wu1-gcrodr-state | 5c838f5116c79ba8efee71c8e26c287e8620606e | 2026-09-28T12:06:02Z | 2026-09-28T12:06:02Z |
| claude/jolly-wozniak-7wl15h-wu2-krylov-validation | 24e4165bf0dc4839c5b2f9dcf7ed2aec6a902f3b | 2026-09-29T01:10:57Z | 2026-09-29T01:10:57Z |
| claude/jolly-wozniak-7wl15h-wu3-inner-forcing | 4d3a7c954afc01a264c8bd1ab629498a648ab9c5 | 2026-09-28T13:41:50Z | 2026-09-28T13:41:50Z |
| claude/jolly-wozniak-7wl15h-wu4-coefficient-cache | 81f27a548b9953c1e91ae4c59874ccdd67338c65 | 2026-09-28T12:15:48Z | 2026-09-28T12:15:48Z |
| claude/jolly-wozniak-7wl15h-wu5-phi-action | 51056ae58ced72627c9ed4ca53dad404aa84c3ca | 2026-09-29T01:09:12Z | 2026-09-29T01:09:12Z |
| claude/jolly-wozniak-7wl15h-wu6a-output-admissibility | 4bc37e0f1e2e9112938679c8d551c6438d2c2b13 | 2026-09-29T01:16:01Z | 2026-09-29T01:16:01Z |
| claude/jolly-wozniak-7wl15h-wu6b-clipped-controller | 73dde4aef65ef625a860e5d8ba95191b3820c223 | 2026-09-28T17:29:36Z | 2026-09-28T17:29:36Z |
| claude/jolly-wozniak-7wl15h-wu6c-interpolant-check | af24dcc84e1defbacbc649fee04da010809bc994 | 2026-09-29T15:59:55Z | 2026-09-29T15:59:55Z |
| claude/jolly-wozniak-7wl15h-wu7-work-counters | 23c1fb99c2669e50b9533cd7628ae668f01e63f3 | 2026-09-29T01:32:53Z | 2026-09-29T01:32:53Z |
| claude/jolly-wozniak-7wl15h-wu8-build-provenance | 4e55c618079d77c7867635984f56774958e8f7f5 | 2026-09-29T01:32:32Z | 2026-09-29T01:32:32Z |
| claude/jolly-wozniak-7wl15h-wu9-stage-certificate | d2a7326e6b145b5a870149f8c00e731591ffbfd6 | 2026-09-29T01:13:24Z | 2026-09-29T01:13:24Z |
| claude/jolly-wozniak-7wl15h-wu10-exponential-scaling | de679da2664d99fa5173277f585cb021ee734f1a | 2026-09-29T16:09:54Z | 2026-09-29T16:09:54Z |
| claude/jolly-wozniak-7wl15h-wu11-attempt-accounting | 08dcbeb006220c5b0afc2c05d39012ab185f2516 | 2026-09-29T09:53:24Z | 2026-09-29T09:53:24Z |
| claude/jolly-wozniak-7wl15h-wu12-causal-transaction | b0ae34b6c4bafef797ee3ffa4fa5d01d521040d0 | 2026-09-29T10:04:25Z | 2026-09-29T10:04:25Z |
| claude/jolly-wozniak-7wl15h-wu13-holdout-hygiene | 1ac1871636d88942570ab00ab5b89024f9c5c137 | 2026-09-29T15:52:33Z | 2026-09-29T15:52:33Z |
| claude/jolly-wozniak-7wl15h-wu14-order-and-dense | c57b2631c2c5fae3cf6655e22481b37d1516740e | 2026-09-29T15:50:00Z | 2026-09-29T15:50:00Z |
| claude/jolly-wozniak-7wl15h-wu15-comparator-fidelity | 41a964c58738166e037c115b491c776e673cc3b6 | 2026-09-29T15:54:28Z | 2026-09-29T15:54:28Z |
| claude/jolly-wozniak-7wl15h-wu16-research-process | 6718afbb7b6a052194480f5a8687ffea8db465ce | 2026-09-29T10:52:27Z | 2026-09-29T10:52:27Z |
| claude/jolly-wozniak-7wl15h-wu17-phi-estimate-semantics | 720a96cba697abaa28f823904cfc76b6ac445c8e | 2026-09-29T22:37:41Z | 2026-09-29T22:37:41Z |
| claude/jolly-wozniak-7wl15h-wu18-linearized-certificate | fcde4fec654a2af7f2c1d143912cf2be12978d00 | 2026-09-29T15:43:22Z | 2026-09-29T15:43:30Z |
| claude/jolly-wozniak-7wl15h-wu19-forcing-final-pass | 6197a84941e40c121b06fd204f20107c017bb6ca | 2026-09-29T15:47:18Z | 2026-09-29T15:47:18Z |
| claude/jolly-wozniak-7wl15h-wu20-common-w-parity | 7ded8ed2f8bb717f52ff2dbd44c9004a6054d564 | 2026-09-29T22:40:41Z | 2026-09-29T22:40:41Z |
| claude/jolly-wozniak-7wl15h-wu21-audit0930 | 18be15bb41b063d6bec89524a142413fd2247feb | 2026-09-30T08:53:28Z | 2026-09-30T08:53:28Z |
| claude/jolly-wozniak-7wl15h-wu22-reaudit-r2 | 6598abd0db790162ab26f50bc13943f24a0c7e4a | 2026-09-30T16:15:05Z | 2026-09-30T16:15:05Z |
| claude/jolly-wozniak-7wl15h-wu23-reaudit-r3 | 2db2b2e97f293630e7a6c7430f70493835a55551 | 2026-10-01T11:39:49Z | 2026-10-01T11:39:49Z |
| claude/jolly-wozniak-7wl15h-wu24-reaudit-r4 | 24b98c3d0b8e57bf1eac400c51ff13575c5d9054 | 2026-10-01T16:15:48Z | 2026-10-01T16:15:48Z |
| claude/jolly-wozniak-7wl15h-wu25-stiff-benchmark | 5a8d7fe9ffc681bca98a98a2f9889a2a05505783 | 2026-10-02T16:57:36Z | 2026-10-02T16:57:36Z |
| claude/nice-dijkstra-208xq0 | c03ca90f19a9e64ba7751c069325a48b54b39c2e | 2026-10-19T18:14:10Z | 2026-10-19T18:14:10Z |
| codex/vigilode-scientific-validity-v2 | 93fe348ce36859dd5f78b31267d771ea9c054677 | 2026-08-29T09:40:48Z | 2026-08-29T09:40:48Z |
| connectivity/audit2-20260829-base | bd9358bc040c62e6139f31208bbcab56d2dae673 | 2026-08-29T10:45:37Z | 2026-08-29T10:45:37Z |
| connectivity/audit2-20260829-head | 90b2d324f0947897376efd3c5b5627171ad3916b | 2026-08-29T10:25:50Z | 2026-08-29T10:25:50Z |
| connectivity/audit2-matrix-free-20260830-base | 8334762bde8ee4336e65da0a308fe450e3946afe | 2026-08-29T20:05:15Z | 2026-08-29T20:05:15Z |
| connectivity/audit2-matrix-free-20260830-head | 623e0e2aacd87713f9b69c0cc3162a5216cf7574 | 2026-08-29T22:50:04Z | 2026-08-29T22:50:04Z |
| connectivity/audit2-readiness-20260829-base | b75af7f9edec85cb243634d179a7a4df952b5ec8 | 2026-08-29T14:24:22Z | 2026-08-29T14:24:22Z |
| connectivity/audit2-readiness-20260829-head | c91007a0afdc28ad6937d246f21f5a06f72a6da1 | 2026-08-29T14:21:15Z | 2026-08-29T14:21:15Z |
| connectivity/k0-bootstrap-r2-base-20260828 | 06f0db807598a1a4e56a2dcaa593c35992440317 | 2026-08-28T02:56:05Z | 2026-08-28T02:56:05Z |
| connectivity/k0-bootstrap-r2-head-20260828 | e0abdfba50c8a14d1727fbc1d80f401597f9a74a | 2026-08-28T02:55:08Z | 2026-08-28T02:55:08Z |
| connectivity/k0-execution-transition-base-20260829 | cd03b52a07efe92d4be4043260df7d20caef0e94 | 2026-08-28T16:31:12Z | 2026-08-28T16:31:12Z |
| connectivity/k0-execution-transition-head-20260829 | 2e200eefd19db80be85cd65fdcd2ead418dba3ff | 2026-08-28T16:30:45Z | 2026-08-28T16:30:45Z |
| connectivity/k0-semantic-final-base-20260828 | a544f61e63a8a0086fafa84863a22aa4b008807c | 2026-08-28T14:00:16Z | 2026-08-28T14:00:16Z |
| connectivity/k0-semantic-final-head-20260828 | 14283c4571f397553c78aa1c2791a8d864dc6f58 | 2026-08-28T07:23:17Z | 2026-08-28T07:23:17Z |
| connectivity/k0-semantic-r3-base-20260828 | c6ec0121be11f76b86afc21f8ae7a304d35c6d83 | 2026-08-28T03:48:52Z | 2026-08-28T03:48:52Z |
| connectivity/k0-semantic-r3-head-20260828 | e486d9fb67dbe6ff173931324d70c51090c80908 | 2026-08-28T13:59:37Z | 2026-08-28T13:59:37Z |
| connectivity/k0-trust-boundary-base-20260829 | 091de7517fad334e41e22dbd1b9d662f07abfef5 | 2026-08-28T20:43:25Z | 2026-08-28T20:43:25Z |
| connectivity/k0-trust-boundary-head-20260829 | e327696d17e85cff6515f6239538466fbe09fa89 | 2026-08-28T20:43:01Z | 2026-08-28T20:43:01Z |
| connectivity/mock-base-k0-20260828 | 30e1ce63fcfdec5625c4b262bc704a79d90a61f4 | 2026-08-28T01:34:05Z | 2026-08-28T01:34:05Z |
| connectivity/mock-head-k0-20260828 | 5c0a568774cef335f4ca011a23f7a7e8ba767e0c | 2026-08-28T01:33:32Z | 2026-08-28T01:33:32Z |
| connectivity/original-target-next-20260830-base | 08d66d9903743916edbd29f3c35305f1acbe383d | 2026-08-30T01:04:01Z | 2026-08-30T01:04:01Z |
| connectivity/original-target-next-20260830-head | d07ebb28a94f07457cf684cbf666c98a32458135 | 2026-08-30T00:58:20Z | 2026-08-30T00:58:20Z |
| connector-smoke/base-20260901-1702 | 8d0c79184e09efb5bdadc24a6315c60a71a44264 | 2026-08-26T06:10:12Z | 2026-08-26T06:10:12Z |
| delivery/audit2-matrix-free-common-w-reuse-20260830 | 0d0d7d5772e90a9497c290fb5e81363c1fe6d97e | 2026-08-30T02:59:29Z | 2026-08-30T02:59:29Z |
| docs/diffsol-benchmark | 2fc61b944fe431d40ba455c373579bce00b0c39a | 2026-10-17T22:46:50Z | 2026-10-17T22:46:50Z |
| docs/k0-codex-execution-package-20260827 | 184c9d37dc678c6a06ac3294c0718ba65a0dcef7 | 2026-08-28T20:41:27Z | 2026-08-28T20:41:27Z |
| handoff/a1-inner-tolerance-parity-20260825 | bc338180c3d1bc9d6cae80e5a859b81b3e70b811 | 2026-08-25T01:17:45Z | 2026-08-25T01:17:45Z |
| handoff/a1-two-arm-authority-receipt-20260825 | a0c686d5471ff10d52fe8d2f73cb6a7914537a12 | 2026-08-25T23:02:17Z | 2026-08-25T23:02:17Z |
| handoff/a2-a3-gmres-inner-cycle-givens-20260826 | a611ea0d0828dad065f2bdcf0356c6cdec9f31d5 | 2026-08-26T01:47:53Z | 2026-08-26T01:47:53Z |
| handoff/pm4-task1-content-equivalence-final-20260824 | 203d2848e5d82db4f3f2eceb1d7c1f894ff0861f | 2026-08-24T14:20:36Z | 2026-08-24T14:20:36Z |
| handoff/pm4-task1-publication-recovery-20260824 | 87623402ee2320b85687dfc2bc275192bb83d038 | 2026-08-24T10:35:41Z | 2026-08-24T10:35:41Z |
| handoff/pm4-task1-r5-cwd-surgical-repair-20260824-canonical | aac00d9f768ae5e8db3782d71e0c5181db0f44dd | 2026-08-24T11:38:50Z | 2026-08-24T11:38:50Z |
| handoff/pm4-task1-r5-cwd-surgical-repair-20260824 | 0506064958f4d52aac9ac29e4fa60796b5e2307c | 2026-08-24T13:37:08Z | 2026-08-24T13:37:08Z |
| handoff/pm4-task1-r5-cwd-surgical-repair-final2-20260824 | aac00d9f768ae5e8db3782d71e0c5181db0f44dd | 2026-08-24T11:38:50Z | 2026-08-24T11:38:50Z |
| handoff/pm4-task1-r5-cwd-surgical-repair-final3-20260824 | aac00d9f768ae5e8db3782d71e0c5181db0f44dd | 2026-08-24T11:38:50Z | 2026-08-24T11:38:50Z |
| handoff/pm4-task1-r5-cwd-surgical-repair-final-20260824 | 017361e88c258783df10eb2f3bc2a21843720d01 | 2026-08-24T12:16:41Z | 2026-08-24T12:16:41Z |
| handoff/pm4-task1-r5-cwd-surgical-repair-stage-20260824 | aac00d9f768ae5e8db3782d71e0c5181db0f44dd | 2026-08-24T11:38:50Z | 2026-08-24T11:38:50Z |
| main | 8d0c79184e09efb5bdadc24a6315c60a71a44264 | 2026-08-26T06:10:12Z | 2026-08-26T06:10:12Z |
| mock/git-roundtrip-base-20260822 | 26e196331df66ecefc93036c931e1298ef0f33e8 | 2026-08-22T12:28:36Z | 2026-08-22T12:28:36Z |
| mock/git-roundtrip-head-20260822 | 08578c83172b0ee0f6eb8f6d2a891d1dac98c6ab | 2026-08-22T12:28:07Z | 2026-08-22T12:28:07Z |
| mock/github-import-pr-push-merge-base-20260823 | 7f6303b830f87731263433e61cc13ea632b0d71f | 2026-08-23T06:41:48Z | 2026-08-23T06:41:48Z |
| mock/github-import-pr-push-merge-head-20260823 | 4c39b0f1fac2f7d42d87f5db2cfd66ef373a77cc | 2026-08-23T06:40:49Z | 2026-08-23T06:40:49Z |
| planning/vigilode-research-coding-spiral-20260904 | 4777eae4819a7594af5299c7acd4ab8f76e8ff85 | 2026-09-04T04:00:27Z | 2026-09-04T04:00:27Z |
| pr/as04-stage-residual-telemetry | 45e96222d2cfc5821c915756b7e09be8ba41bbef | 2026-10-17T02:00:45Z | 2026-10-17T02:00:45Z |
| pr/as05-residual-gain-core | 70df29c730be08b1de4d8c57c16402139eaa8bc5 | 2026-10-17T05:10:20Z | 2026-10-17T05:10:20Z |
| pr/ex01-pexprb-own-step | ffa20a3f7678b85b620b9111a604dce6cd8cdb0f | 2026-10-17T13:33:45Z | 2026-10-17T13:35:00Z |
| pr/fix-jvp-only-direct-config | 1dd4f24ec1637281f0dd7908c1de0dc6301066fc | 2026-10-17T08:11:56Z | 2026-10-17T08:11:56Z |
| pr/ht01-homotopy-client-contract | 1f2cb84d354e20ea26a643be990f47afee274d2d | 2026-10-17T12:33:47Z | 2026-10-17T12:33:47Z |
| pr/ht02-homotopy-parallel-pilot | de6f96ef700528d70f4e513a66f010223d84eded | 2026-10-17T12:39:30Z | 2026-10-17T12:39:30Z |
| pr/lp01-collective-model | 36d6097a6eb24d6277f7a5ef7a31a31022af5818 | 2026-10-17T16:00:53Z | 2026-10-17T16:00:53Z |
| pr/lp02-packet-window | 6ed07d5412f72e25f3da5a9811a368dfc1381071 | 2026-10-17T16:20:21Z | 2026-10-17T16:20:21Z |
| pr/lp03-damped-moments | a702b3e8208bb4d9082a4a197886e365255e2197 | 2026-10-17T16:27:58Z | 2026-10-17T16:27:58Z |
| pr/lp04-packet-trajectory | 6c3c65c758013ec1b473eec018ae545d57437478 | 2026-10-17T16:37:02Z | 2026-10-17T16:37:02Z |
| pr/lp09-packet-benchmark | a7e146d553565a0e0637968d17e24ae3c1160f27 | 2026-10-17T16:47:50Z | 2026-10-17T16:47:50Z |
| pr/lp10-independent-decision | 3fce121e4796372f90bfcba3f701ffbe120e3221 | 2026-10-17T16:56:01Z | 2026-10-17T16:56:01Z |
| pr/me01-full-cost-judgement | c24679efcab2c47db7a87f2bb4626947baad917f | 2026-10-17T15:00:57Z | 2026-10-17T15:00:57Z |
| pr/pc01-right-preconditioner | 53f876772f377f3862e6f0f2187ee307576b82a8 | 2026-10-17T15:46:36Z | 2026-10-17T15:46:36Z |
| pr/py01-laguerre-component-export | 323cf8b01074423e36226a5d6b4ce3d8210172bc | 2026-10-17T06:41:12Z | 2026-10-17T06:41:12Z |
| pr/py02-laguerre-adjoint-bound | 09f7260021c8b36eabaf25a08a631db643f2480d | 2026-10-17T07:36:21Z | 2026-10-17T07:37:00Z |
| pr/py03-single-backend-router | 67a3f6d251fdca4d4a31cdff16d446942cad09b7 | 2026-10-17T09:37:14Z | 2026-10-17T09:37:14Z |
| pr/py04-fused-normalization | ae4fc80977f23cbde32c3fe4e642a3be06b07851 | 2026-10-17T10:15:46Z | 2026-10-17T10:15:46Z |
| pr/py05-leja-total-certificate | 5602156e4848877465aaed38a6f747076aab791c | 2026-10-17T11:27:56Z | 2026-10-17T11:27:56Z |
| pr/sp02-krylov-workspace-caller | d8ed7db9ad7fdee1070be2a5f87f758754ad30e7 | 2026-10-16T23:48:07Z | 2026-10-16T23:48:07Z |
| pr/sp04-zero-start-recycling | aea31df033d8111e63ec8c15ee73848fed18558b | 2026-10-17T04:00:26Z | 2026-10-17T04:00:26Z |
| probe/audit2-connectivity-base-20260830 | 0c1193d67a347f5ace61869b8f098a87f2bf928b | 2026-08-30T06:30:22Z | 2026-08-30T06:30:22Z |
| probe/audit2-connectivity-head-20260830 | 43ce100f1e22d50728d2cadfd8d38806e8920279 | 2026-08-30T06:24:29Z | 2026-08-30T06:24:29Z |
| probe/audit2-reusable-transaction-20260830-base | 5467b8d6954d7acb87385e591470670588c2f970 | 2026-08-30T10:39:47Z | 2026-08-30T10:39:47Z |
| probe/audit2-reusable-transaction-20260830-head | b1cec908cc2303eed9fe1faa03d003456ebb0eaa | 2026-08-30T10:32:31Z | 2026-08-30T10:32:31Z |
| production/a1-api | a605573e2cb4bcbb17c21db7866d4b22ab747011 | 2026-10-20T18:09:24Z | 2026-10-20T18:09:24Z |
| production/a1-defects | a8ec412affef1333ccb83b0137f50cf8cecc490e | 2026-10-20T19:08:52Z | 2026-10-20T19:08:52Z |
| production/a2-wfiltered | 7bea78c213df502aa8c21b38c925c467fdec660e | 2026-10-20T17:58:50Z | 2026-10-20T17:58:50Z |
| production/b1-lagged | 16f66319f32085f13663f71be69a947d02100d54 | 2026-10-20T17:57:19Z | 2026-10-20T17:57:19Z |
| production/b1b-gmres | 16edef2eeff2016938a6d18a64572d6e0de51757 | 2026-10-20T22:06:26Z | 2026-10-20T22:06:26Z |
| production/b1c-staleness | 129aa46de25cf6ae84f3061f7a31319a60637469 | 2026-10-20T23:57:16Z | 2026-10-20T23:57:16Z |
| production/c1-transaction | f07c4d7132133a7e19ecfa8281a047dd2c2f6ef6 | 2026-10-20T21:33:33Z | 2026-10-20T21:33:33Z |
| production/ci-docs | eabe19dd3e46a8a4e9eda6be9e7ad2fd31cff7f1 | 2026-10-21T00:09:40Z | 2026-10-21T00:09:40Z |
| production/e1-bench | 387f87a2198f0f80bed0720f66613b6f99eb6786 | 2026-10-20T22:37:57Z | 2026-10-20T22:37:57Z |
| production/e1b-dense | 3e00b94e3f3932d2de15ff4c43ae156690f3cee4 | 2026-10-21T03:06:33Z | 2026-10-21T03:06:33Z |
| production/h-checker | 4f92ec38b70799d69091006b86f1ee165e3dbd93 | 2026-10-20T22:40:44Z | 2026-10-20T22:40:44Z |
| production/h-hygiene | d41bf160673e248cc29d68e0b63d6376201e8f52 | 2026-10-20T21:49:40Z | 2026-10-20T21:49:40Z |
| production/p0-api | 49456837dc7d4e105a900ef862ea7d2f1cbe5edc | 2026-10-21T00:32:59Z | 2026-10-21T00:32:59Z |
| production/p0-atol | 997fefe9f256bf7a2ac3275a5c485e024faac571 | 2026-10-20T23:49:20Z | 2026-10-20T23:49:20Z |
| production/p0-events | f65d9686cb9cf874d5af73644237e22f28767e7b | 2026-10-21T00:02:46Z | 2026-10-21T00:02:46Z |
| production/p0-facade | a8b15bd7337c8050ec03cac69a1d146b5550b902 | 2026-10-20T22:07:12Z | 2026-10-20T22:07:12Z |
| production/p0-fastdense | 35d6604c77f2ee6cdb03bd35f8c3fe043a604838 | 2026-10-21T00:23:57Z | 2026-10-21T00:23:57Z |
| production/t-verify | f2250b75ff3638974a88fc0f82c835b2f00ded6f | 2026-10-20T17:43:43Z | 2026-10-20T17:43:43Z |
| production/vigilode-plan-20261021 | cc2e1a009ac6802ef01a289392e9715074a882ba | 2026-10-21T03:37:10Z | 2026-10-21T03:37:10Z |
| production/w2-final-fix | 08fd05243217cd075dfb052550aecc6f1f1e53ae | 2026-10-20T23:19:57Z | 2026-10-20T23:19:57Z |
| production/w3-final-fix | 5c6978d47c620f1a6e727f092215e92ab0381f6a | 2026-10-21T00:55:27Z | 2026-10-21T00:55:27Z |
| production/w3-flakes | 9b12bff4ea65aa28ce84394149ce01b57b404d65 | 2026-10-21T03:10:22Z | 2026-10-21T03:10:22Z |
| production/wave1-integration | a5a48f77e7ac7a80b8ff86cd897110790066f7ee | 2026-10-20T21:38:02Z | 2026-10-20T21:38:02Z |
| production/wave2-integration | 08fd05243217cd075dfb052550aecc6f1f1e53ae | 2026-10-20T23:19:57Z | 2026-10-20T23:19:57Z |
| production/wave3-integration | f2f20c1d8cd606e70ddbd8409c0f3b4529e928a1 | 2026-10-21T03:10:47Z | 2026-10-21T03:10:47Z |
| research/a1-inner-tolerance-parity | f8c3ad61b2e7f36860396209ca928b06e84ec85f | 2026-08-26T00:48:57Z | 2026-08-26T00:48:57Z |
| research/a1-post-a2a3-kernel-rerun | e1124586a4029f86669e7489278c61ef676d61aa | 2026-08-26T13:21:55Z | 2026-08-26T13:21:55Z |
| research/a2-a3-gmres-inner-cycle-givens | 64f5f33f7deff84678f029763306f29c690b20d9 | 2026-08-26T05:44:52Z | 2026-08-26T05:44:52Z |
| research/all-dag-completion-20261018 | ee65d4dbecf3b3cd5f4587c27f87ef297d2bb406 | 2026-10-18T15:24:55Z | 2026-10-18T15:24:55Z |
| research/audit2-bateman-local-execution-orchestrator-20260831 | 426d37ce3c0f4e5b7843b163eaf772b8e55bfa87 | 2026-08-31T09:32:59Z | 2026-08-31T09:32:59Z |
| research/audit2-matrix-free-common-w-20260830 | 17fcd447c1dadcea978f241ff3ba94635f9c2bd4 | 2026-08-30T06:22:00Z | 2026-08-30T06:22:00Z |
| research/audit2-matrix-free-w-20260830 | 981bf1bc2fa80216bad00495dd6c72b5fcf65ba3 | 2026-08-29T21:27:53Z | 2026-08-29T21:27:53Z |
| research/audit2-original-target-bridge-20260830 | c5fbd6d5703fc396bdf30eb3acfacb6c6bd2b921 | 2026-08-29T16:20:35Z | 2026-08-29T16:20:35Z |
| research/audit2-output-policy-20260829 | e77ec86376ca89850e18e99963992aeeb01055c2 | 2026-08-29T15:04:40Z | 2026-08-29T15:04:40Z |
| research/audit2-real-client-authority-construction-20260830 | 6b00a886c4eb38d3fe199e3d77852cc1eb35eb39 | 2026-08-30T15:28:03Z | 2026-08-30T15:28:03Z |
| research/audit2-reusable-preconditioner-transactional-step-20260830 | f954e39130e5141256731d0745666a872c0267ea | 2026-08-30T12:27:26Z | 2026-08-30T12:27:26Z |
| research/audit2-stage-certificate-repair-handoff-20260831 | b3e8165c8dc3b5016702821d280daea1a3f1feb7 | 2026-08-31T17:49:38Z | 2026-08-31T17:49:38Z |
| research/audit2-stage-certificate-telemetry-20260831 | 9fbdd84c64e99620805ebf634dcaf57aaad05cbc | 2026-08-31T13:46:29Z | 2026-08-31T13:46:29Z |
| research/audit2-stage-certificate-worktree-20260831 | c4c152c732e8b937181893073c315ae231eaae6f | 2026-09-28T11:49:33Z | 2026-09-28T11:49:33Z |
| research/banded-exact-reuse-20261020 | 3c0157910076ce552283c831c2be000c66671fab | 2026-10-19T19:55:38Z | 2026-10-19T19:55:38Z |
| research/bassrei-port-20261021 | c4d9eb9f76ac1fbcbb4a12fb920d05e4c2317fa9 | 2026-10-21T21:08:19Z | 2026-10-21T21:08:19Z |
| research/benchmark-results-20261019-dual | 64b9852124b67eedbb8575b42c01127e4b86283b | 2026-10-19T14:01:36Z | 2026-10-19T14:01:36Z |
| research/cloud-completion-20261018 | 86afb40adcb0eda00c017c44b3553a8479c6c640 | 2026-10-18T11:22:13Z | 2026-10-18T11:22:13Z |
| research/coupled-economy-20261020 | 6c945b6c6e0e024d8f733c21da8d35fbcc3c5f2a | 2026-10-20T02:17:20Z | 2026-10-20T02:17:20Z |
| research/coupled-matrix-free-rust-20261020 | 15c43ce76734d0a560fcec5909ac49f1e6f2d347 | 2026-10-20T00:58:06Z | 2026-10-20T00:58:06Z |
| research/cumulative-evidence-20261020 | ebb5b81ebe77314b6fee941096fd6cba6d8597fc | 2026-10-20T12:54:48Z | 2026-10-20T12:54:48Z |
| research/e4-fresh-clone-build-reproducibility | c3b94dd123f02606a91f2b9c046e14451cee096f | 2026-08-24T22:56:58Z | 2026-08-24T22:56:58Z |
| research/frozen-full-e-shadow-economics-v3.6 | 535e8f87cf09cc9752081e9e1f3d94d4fb3567bb | 2026-08-21T04:58:36Z | 2026-08-21T04:58:36Z |
| research/hybrid-structure-ad-20261020 | 9bb05bed4cd7df720f2b429c2b47e97ed76712d5 | 2026-10-20T08:00:20Z | 2026-10-20T08:00:20Z |
| research/k0-stage-telemetry-integration-20260827 | 2cf820e2ae657f194593dd468efe6fc2798c14f0 | 2026-08-27T04:45:20Z | 2026-08-27T04:45:20Z |
| research/midcheck-three-solver-20261020 | 6972f28aa4bcbe4c68dbba92e44ff58884545bca | 2026-10-20T02:59:26Z | 2026-10-20T02:59:32Z |
| research/ncp-followup-fvm-20261021 | 5fd6e459a3f67cee90e002821b9b4b740c47475b | 2026-10-21T07:58:59Z | 2026-10-21T07:58:59Z |
| research/output-policy-assessment-20260829 | 990bc0a02848f9a3a3bd774fdc8de2c97bc6bb55 | 2026-08-29T11:10:38Z | 2026-08-29T11:10:38Z |
| research/promotion-theory-20261011 | bbb8ef42ad4e9b49704b165a54a26c435c575ae3 | 2026-10-11T06:51:24Z | 2026-10-11T06:51:24Z |
| research/rvj-full-history-20261004 | 6852b4af9ecadfb8c3aa50c4d240301dd1f3a4db | 2026-10-04T07:49:10Z | 2026-10-04T07:49:10Z |
| research/timing-replication-continuation-transaction-v3.7 | 2db8436a89e1da23528c644a97fb03d9954ca81c | 2026-08-22T02:12:46Z | 2026-08-22T02:12:46Z |
| research/v37-continuation-transaction-implementation | 4384eab8397b20903377705a99b4db6e8370e2bd | 2026-08-22T07:37:09Z | 2026-08-22T07:37:09Z |
| research/v37-timing-authority-validator | 04a93676bd1d81beac9ba3a5172e97a7c7030e6d | 2026-08-23T19:40:55Z | 2026-08-23T23:46:45Z |
| research/v38d-exploratory-benchmark-substrate | 5f2e903ca5350a0f6d2329850bb7297196e469fb | 2026-08-24T15:07:43Z | 2026-08-24T15:07:43Z |
| research/v38d-high-entropy-performance-tournament-design | 88c5d3e07bdb00959b7b35f65531cc89dd48298d | 2026-08-22T16:28:05Z | 2026-08-22T16:28:05Z |
| research/v38d-high-entropy-performance-tournament-plan | 631db120926f95b499b048c2f128fbbd10eb678f | 2026-08-23T00:45:28Z | 2026-08-23T00:45:28Z |
| results/local-e1b-33e60cf | 264e9853f8babf1287463a87356d61337eee676e | 2026-10-21T02:40:57Z | 2026-10-21T02:40:57Z |
| results/local-wave2-08fd052 | 1842daaed8a3f85a3a18d25dcfd2297277dc9107 | 2026-10-21T01:11:26Z | 2026-10-21T01:11:26Z |
| results/local-wave3-4945683 | 32ff334861bc5507791731ecf832eddd7be82450 | 2026-10-21T02:31:46Z | 2026-10-21T02:31:46Z |
| results/ncp-followup-fvm-5fd6e45 | fbbc832fdf942396155c12b04c30e63dc67fefe9 | 2026-10-21T11:43:45Z | 2026-10-21T11:43:45Z |
| scratch/a1-two-arm-local-snapshot-20260826 | 79491e299dad3471ba5e8ce819e6a1a4333eef79 | 2026-08-25T17:35:49Z | 2026-08-25T17:35:49Z |
| tmp/e4-tree-api-test-20260825-b | 3186d53365fb90e9e40340f7bba52a22bcd012ee | 2026-08-24T15:38:02Z | 2026-08-24T15:38:02Z |
| tmp/e4-tree-api-test-20260825-c | 3186d53365fb90e9e40340f7bba52a22bcd012ee | 2026-08-24T15:38:02Z | 2026-08-24T15:38:02Z |
| tmp/e4-tree-api-test-20260825-d | 3186d53365fb90e9e40340f7bba52a22bcd012ee | 2026-08-24T15:38:02Z | 2026-08-24T15:38:02Z |
| tmp/e4-tree-api-test-20260825-e | 3186d53365fb90e9e40340f7bba52a22bcd012ee | 2026-08-24T15:38:02Z | 2026-08-24T15:38:02Z |
| tmp/e4-tree-api-test-20260825-f | 3186d53365fb90e9e40340f7bba52a22bcd012ee | 2026-08-24T15:38:02Z | 2026-08-24T15:38:02Z |
| tmp/e4-tree-api-test-20260825 | 3186d53365fb90e9e40340f7bba52a22bcd012ee | 2026-08-24T15:38:02Z | 2026-08-24T15:38:02Z |
| transport/audit2-matrix-free-w-20260830 | 44131313c6def97a65d4c10d4dfbcdf70f9f870a | 2026-08-29T21:42:54Z | 2026-08-29T21:42:54Z |
| transport/v37-continuation-pr4-20260822 | e65064d0cabc191b0f3639a21b9f1238cbe17988 | 2026-08-22T09:06:29Z | 2026-08-22T09:06:29Z |

## Read sources

- https://api.github.com/repos/cosmosapjw-quantum/vigilode/branches?per_page=100&page=1
- https://api.github.com/repos/cosmosapjw-quantum/vigilode/branches?per_page=100&page=2
- https://api.github.com/repos/cosmosapjw-quantum/vigilode/branches?per_page=100&page=3
- https://github.com/cosmosapjw-quantum/vigilode/compare/8d0c79184e09efb5bdadc24a6315c60a71a44264...de4c10a9f41321beef2313a3d7fb503bab35d714
- https://github.com/cosmosapjw-quantum/vigilode/compare/de4c10a9f41321beef2313a3d7fb503bab35d714...7a63876a97fc17f640771ec06658269947049994

Exact-HEAD metadata endpoints use `https://api.github.com/repos/cosmosapjw-quantum/vigilode/git/commits/<SHA>`; each resolved URL is preserved in the JSON. This bounded inventory does not open a new execution or audit campaign.


## Bounded content update for the three newer HEADs

The initial enumeration-only scope was extended by the controller to 13 selected report/result/manifest/handoff files. This is a bounded content intake, not full source or raw-trajectory audit. No new execution occurred.

### research/ncp-followup-fvm-20261021 — 5fd6e459a3f67cee90e002821b9b4b740c47475b

Decision: **ADOPT_REPORT_LESSONS; DEFER_SOLVER_AND_FVM_SWAP**.

- One commit ahead of external-audit anchor; compare reports 104 changed files. Opt-in analytic heat Jacobian, band/border Schur preconditioner, conservative remap and LRS scalar cold-Thomson oracle are implemented upstream.
- Upstream report states 9/9 scoped commands, 19 Rust and 15 Python tests. These are read reports, not checks run here.
- Corrected archived rotation acceptance is 7/140, all seven at internal rtol=1e-10; this does not establish general production accuracy.
- Shared electron/rank structure and explicit operator-work accounting are compatible design lessons. Frozen REI finite Legendre transport, atomic closure, exact quadrature and Radau solver remain unchanged.

### results/ncp-followup-fvm-5fd6e45 — fbbc832fdf942396155c12b04c30e63dc67fefe9

Decision: **ADOPT_SCOPED_COST_AND_ACCURACY_EVIDENCE; NO_SPEED_OR_PRODUCTION_PROMOTION**.

- One commit after 5fd6e459; tree diff is additive audit evidence, with no modified or deleted blobs.
- README and report v2 describe periodic_heat n=128 with 41 outputs and original application rtol=1e-6/atol=1e-9; analytic-stencil and basis-JVP trajectories agree bitwise. Total RHS including derivative work drops 5712 to 336, removing 5376 derivative RHS calls.
- 489 paired blocks report descriptive median STEN/BASE warmed 0.586, process-wall 0.620, CPU 0.616; timing remains diagnostic_only/STATISTICAL_AUTHORITY_HOLD because simultaneous one-host blocks are not independent. No REI speed ratio follows.
- Manifest report records 102/102 matching source artifacts; not independently rehashed here. Broad production HOLD; manufactured Schur probe is not an ODE/BASS benchmark; multiple sizes, matrix-free/banded heat, allocation and tightened-tolerance arms remain unrun.

### research/bassrei-port-20261021 — c4d9eb9f76ac1fbcbb4a12fb920d05e4c2317fa9

Decision: **ADOPT_LATEST_STATUS_AND_REFERENCE_UNCERTAINTY_DISTINCTION; DEFER_INTEGRATION**.

- Six commits ahead of 5fd6e459; new fixed-grid LRS photon FV Rust adapter, analytic partial-time support, tests and P02/P02b materials.
- P02 stored full result and DAG say FAIL: C1-C5 and C7-C10 pass, C6 fails at gamma=1e6 because u_ref compares the method's own tight-tolerance result with Radau. Stored method-v-reference difference about 1.2e-11 is not solely reference uncertainty; Radau 1e-13 versus 1e-14 is about 3.59e-13.
- Post-verdict diagnosis does not rescore P02. P02b preregistration changes reference uncertainty to Radau self-comparison and records method floor separately; it discloses known prior outcomes and supplies no new blind evidence.
- Exact P02b tree contains only PREREGISTRATION.md and run_p02b.py, with no results.json/raw/DAG_STATUS.json. Hence no observed P02b PASS; P03-P06 remain blocked in available DAG and production HOLD.
- This fixed-grid photon-FV port is separate from the frozen REI isotope-quotient/Radau pilot. Do not infer validation of the latter from P02, or reject its existing 83 IVPs because P02 failed.

The complete recursive-tree comparisons are untruncated: the result branch adds 2,516 blobs and changes/deletes none; the BASS/rei port adds 120 blobs, modifies 3 and deletes none relative to 5fd6e459. The results compare endpoint returns only 300 file rows, so it was not treated as exhaustive.

Read sources are pinned by exact HEAD, path and blob SHA in the JSON. The latest BASS/rei P02 outcome is independent of this project's completed isotope-quotient pilot and does not alter its frozen claim or solver.
