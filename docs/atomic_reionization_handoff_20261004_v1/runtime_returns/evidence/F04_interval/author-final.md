Implemented the bounded interval/Jet2 prerequisite in [interval_math.rs](/home/cosmosapjw/Dropbox/bianchi/rei_bianchi/rust/rei_microphysics/src/interval_math.rs), [interval_ad.rs](/home/cosmosapjw/Dropbox/bianchi/rei_bianchi/rust/rei_microphysics/src/interval_ad.rs), [interval_probe.rs](/home/cosmosapjw/Dropbox/bianchi/rei_bianchi/rust/rei_microphysics/examples/interval_probe.rs), and the additive exports in [lib.rs](/home/cosmosapjw/Dropbox/bianchi/rei_bianchi/rust/rei_microphysics/src/lib.rs).

The **frozen Sage/MPFI validator passed**: 5 Rust tests, 32 scalar/Jet cases, 408 interval reference checks, and 4 invalid-domain records. Frozen input hashes matched their recorded values. A separate probe check enclosed `exp(-1000)` in `[0, 4.94e-324]` and rejected `exp(1000)`.

This qualifies only the finite primitive prerequisite. Actual H/He residual, root, remainder, and full F04 scientific admission remain **HOLD**.

<oai-mem-citation>
<citation_entries>
MEMORY.md:2995-2996|note=[preserved prior interval claim boundary]
</citation_entries>
<rollout_ids>
01a04c37-05d9-7503-bd24-47a66006dcf5
</rollout_ids>
</oai-mem-citation>
