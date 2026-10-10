# REI fresh intake — 2026-10-10

Read-only intake of current public GitHub refs/source and the posted PHYS22/23 reports. No private ChatGPT chats were accessed; repository/report returns do not establish a recipient's execution ACK. No scientific solver run was performed for this intake.

## What changed since the supplied pins

PR96 `528bb69a24ce9345efec78c6d406d3c392e2671d`, PR97 `00903cb4433276ad5d8233aca1f9e0c2b6834523`, and PR102 `69541be1a88f32468494e33158a96d5341e4572c` remain unchanged. PR103, branch `research/cr-phys03-fs10-xi01-20261010`, is new at `8d9526a75e85202764e845c7d5d79d7f903e7c55`. Its exact delta from PR102 is seven files, 158 insertions and 6 deletions: it adds a separately pinned xi=0.1 packet, explicit exact-knot selection, probe/test changes, and scoped receipts. It adds no solver interval.

PR83's original owner branch `forward/rust-reion-kernels-20260922` is now `e334866a4ac1be963f573c0b35182d25eb4d666b`: an additive PHYS22 documentation return. Its source input is `3dc42c64ab32075f0a59c96af3ddf7435d9b7f97`, scientific Rust subtree `cb69b4736dd046e4675557577eb8e0ead037d1f3`. The new result closes local initial-time shear-response coefficients, not a finite-time history. PHYS23 proposes the next spectral sign diagnostic. Both explicitly preserve no new gas IVP/native history.

## Which branch to use

There is no single merged newest owner integration branch: main remains `ae3402713c4b6530ab2b27f008f5f5d5c6a999ed`. The latest physical component stack is PR96 → PR97 → PR101 → PR102 → PR103. PR101 supplies a clean source/binary prelaunch receipt gate; PR102/103 supply the local CR receiver. Use exact PR103 head as the additive reduced-history research base if retaining all these inputs is wanted. Preserve the separate PR83 PHYS22 result as an input/return; merging its large divergent branch is unnecessary to implement the new lane.

## Actual broad-history code and evidence

The current warm source-bound run has 2,904 momentum-angle nodes and 17 output epochs but covers only 0..1e11 s, z=5.807 to approximately 5.80698492362111. `research/physical_provider_20261010/run_interval.py` hardcodes the duration and warm 50,000 K IC. `rust/rei_microphysics/src/axisym_conditional.rs` independently rejects time outside [0,1e11], binds six immutable source identities, and calls the existing FT03 machinery. This is not a broad-redshift history.

The original IGM branch PR84, `forward/rem-hhe-igm-20261006` at `39c39eab1cc2f1a215723680accc123e67ef13b6`, has genuine `igm_*` Rust modules, low-temperature rates, continuous/reference runners, and a z12→10 long FLRW pilot. Its selected source is manufactured constant emission, not HM12 or a cosmological source population. The stored long-grid comparison still fails 8 of 37 fields; native/physical admission remains unresolved. It is not a ready physically sourced broad-history solver. The low-T module is explicitly a separate operational Grackle 3.4.1 Case-A subset, T in [1,1e6] K, with floor/cap/DR diagnostics; it must not be described as missing entirely or as FT03 low-T validation.

## The actual blockers

- FT03's selected production temperature domain remains 30,000..110,000 K. This blocks simply integrating the warm native gas path through ordinary IGM temperatures.
- The CR receiver binds a fixed 100 K snapshot, exact source/time/geometry/density, and xHII=xHeII=xi, xHeIII=0. Exactly xi=.01 or .1 are available; interpolation or arbitrary evolving composition is deliberately rejected. Causal delay, full CR loss physics, and a coupled CR history remain open. The source-bound HM12 warm lane keeps CR/RCT/HH OFF.
- Full physical radiation closure remains unresolved: recombination diffuse fate, secondary/Compton terms, high-energy boundary and uncertainty are not made correct by a longer runtime.
- Production source/binary build receipts become stale after source changes. PR101 closes the missing launch guard only; it does not approve all future binaries or run a history.
- The HM12 author tables themselves cover z=0..15.93. z20 cannot be obtained by silently extending this parser; its extrapolation rejection is correct.

## Shortest scientifically meaningful execution candidate

An additive, explicitly selected volume-filling-factor model with published ionizing emissivity, Case-B recombination and specified ionized-zone temperature can execute across reionization now, without claiming that the full coupled transport/CR model is complete. Use z20→4 only with a newly pinned published source extending there, or use z15.93→4 with the existing author HM12 table. Report Q_HII(z), z50/z90, segment optical depth, source/recombination budgets and a matched shear response. This is a new reduced physical model and must be named as such, with CR/RCT/HH history completion explicitly unresolved.

Reuse `research/physical_provider_20261010/background.py`: `BianchiBackground(r, z_i=..., t_max=...)` already supports the required epoch change. It computes dust+Lambda LRS Bianchi-I H²=D+B/a³+C/a⁶, s=s0/a³, proper nH/nHe and `time_of_redshift`. r means initial s/H; same r at different start redshift is not the same s0. Radiation stress/backreaction is excluded. Hfid at nonzero shear is not automatically present-day H.

Reuse `hm12_data.py` and pinned `sources/emissivity.out` SHA256 `88743ec9041a47fd12f47bf50a75a06903089e1afd992b5460a4af471249469b`. `emissivity.moment(Emin,Emax,z,proper_photons=True)` analytically integrates the declared piecewise interpolation and yields proper photons cm^-3 s^-1. Divide by proper nH for a per-H source. A declared energy band still selects which photons count and does not solve He/secondary transport. Never impose the UVB table as both initial photons and independent later source. `UVB.out` SHA256 is `a708586ead551202c068b049d48afa87b96695c5a5d12253e9b9bbb74efd75dc`.

## Inspection pointers

Exact source inspected in the local read-only clone: `reion_acceleration_20261010/repos/rei_intake`, detached at PR103. Relevant current files: `axisym_cr_deposition.rs`, `axisym_cr_deposition_pin.rs`, `axisym_conditional.rs`, `ft03_rates.rs`, physical-provider CONTRACT/DAG/background/parser/runner, and CR-PHYS03 REPORT/HANDOFF. PR84 files were read by immutable git object path, including `igm_rates.rs`, `igm_config.rs`, and `long-flrw/ASSESSMENT.json`. `rei.json` retains current PR bodies, refs and update timestamps plus machine-readable decisions.
