Module[{nodes, edges, g, paths, requiredPath, bypassEdges, lock, lockJSON, stream, file, lockHash},
 nodes = {"HistoricalAttemptLedger", "SourcePacketBackup", "Section0Successor", "GlobalLease", "LocalLease", "NativeAttempt", "RuntimeResultAudit", "FirstIntervalEligibility", "ProviderReview"};
 edges = {
   "HistoricalAttemptLedger" -> "Section0Successor",
   "SourcePacketBackup" -> "Section0Successor",
   "Section0Successor" -> "GlobalLease",
   "GlobalLease" -> "LocalLease",
   "LocalLease" -> "NativeAttempt",
   "NativeAttempt" -> "RuntimeResultAudit",
   "RuntimeResultAudit" -> "FirstIntervalEligibility",
   "FirstIntervalEligibility" -> "ProviderReview"
 };
 g = Graph[nodes, edges, DirectedEdges -> True];
 paths = FindPath[g, "HistoricalAttemptLedger", "ProviderReview", Infinity, All];
 requiredPath = {"HistoricalAttemptLedger", "Section0Successor", "GlobalLease", "LocalLease", "NativeAttempt", "RuntimeResultAudit", "FirstIntervalEligibility", "ProviderReview"};
 bypassEdges = {
   "HistoricalAttemptLedger" -> "NativeAttempt", "SourcePacketBackup" -> "NativeAttempt",
   "Section0Successor" -> "NativeAttempt", "GlobalLease" -> "NativeAttempt",
   "NativeAttempt" -> "FirstIntervalEligibility", "NativeAttempt" -> "ProviderReview",
   "RuntimeResultAudit" -> "ProviderReview"
 };
 lock = <|
   "rustc_sha256" -> "ef6d716e5d1c6c93def277c0afa037c21e7a74f7de3aed4ee0700646c3301b1d",
   "rustc_version" -> "rustc 1.94.1 (e408947bf 2026-03-25)",
   "rustc_driver_sha256" -> "e51e2f6796ac2730a11744a0d3e126e6b1e60d43e2e602a091551b1ad1a9ba2f",
   "llvm_sha256" -> "158c711c64147bb127a2a5174df22718d26b755560a1487945e7c788c947986f",
   "stdlib_closure_sha256" -> "1d6d31c8f1c99b69b120c91fcff14220bbfcf0e8f976096f0c4992b7e2edc799",
   "python_sha256" -> "a92f0f95e883390c7256b2e441484aac06b1002dbe1d924141a77c8d82f96223",
   "mpfr_sha256" -> "2156351fa3dedd04a7381c6ac7a8a26efa2d6fb08b80f8a2d644ccdd653710ae",
   "gmp_sha256" -> "0ccdfb6d6f5c039465f6d002cf7e4c072d48ac6a2cffc8dd6c748dec31592804",
   "cc_sha256" -> "6117c52522997d2aaccb2b52b3c6bf42c0a6c5edb1d718431fed6b2fc5fec234",
   "ld_sha256" -> "5b674ea1d7017c2929f3c52c43487478bb240ecdd7197a25cce3813a70329a5c",
   "target" -> "x86_64-unknown-linux-gnu", "precision_bits" -> 256,
   "rounding_policy" -> "MPFR_RNDD_RNDU"
 |>;
 lockJSON = ExportString[KeySort[lock], "RawJSON", "Compact" -> True];
 file = CreateTemporary[];
 stream = OpenWrite[file, BinaryFormat -> True];
 BinaryWrite[stream, ToCharacterCode[lockJSON, "UTF8"]];
 Close[stream];
 lockHash = IntegerString[FileHash[file, "SHA256"], 16, 64];
 DeleteFile[file];
 ExportString[<|
   "status" -> If[And[AcyclicGraphQ[g], Length[paths] == 1, First[paths] === requiredPath,
      And @@ (MemberQ[#, "Section0Successor"] & /@ paths),
      And @@ (MemberQ[#, "GlobalLease"] & /@ paths),
      And @@ (MemberQ[#, "RuntimeResultAudit"] & /@ paths),
      Intersection[EdgeList[g], bypassEdges] === {}], "PASS", "FAIL"],
   "acyclic" -> AcyclicGraphQ[g], "path_count" -> Length[paths],
   "required_path_exact" -> (First[paths] === requiredPath),
   "all_paths_through_section0_successor" -> And @@ (MemberQ[#, "Section0Successor"] & /@ paths),
   "all_paths_through_global_lease" -> And @@ (MemberQ[#, "GlobalLease"] & /@ paths),
   "all_paths_through_runtime_audit" -> And @@ (MemberQ[#, "RuntimeResultAudit"] & /@ paths),
   "forbidden_bypass_edges_absent" -> (Intersection[EdgeList[g], bypassEdges] === {}),
   "semantic_toolchain_lock_sha256" -> lockHash,
   "semantic_toolchain_lock_hash_method" -> "SHA256_CANONICAL_UTF8_JSON_BYTES",
   "authority_effect" -> "NONE"
 |>, "RawJSON"]
]
