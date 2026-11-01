# REI Physical Fast | REI owner accepts original-source F08 H I photoionization/photoelectron-heat angular PSTF

2026-11-01 (Asia/Seoul). **One scientific source-conditional unit** derived from original frozen REI S0 H/He photon model, not a new 26-event F05 IVP, complete F08 native Rust source transport or observed sky.

## Owner authority and science inputs

* Parent original REI F08 owner PR #359, immutable parent head `2b44b1cbedd5ad2fd17e5f47cb32d95d967d14de`; parent includes previously verified first-step original Rust HI absorption comparison and original 128-ray off-grid support evidence. Parent is not modified or merged.
* Source donor BASS PR #323 frozen head `c0e965ba21892346feef9ecb2389932c34f3fc82`, original REI F08 S0 fixed original H/He matter and 15 proper-time epochs, original 8×16 q directions and Verner H I photoelectric rates. Its specific source CI #41316296033 SUCCESS. Original BASS source bytes: angular `370abc5b57c25497d8adfb2931428d04fcc84ff29a8621a8348e01d90a9c6a54`; history `df1acb1bf78f2fc0e6d3a852cdfacedf1bc44e0909b870bebbacf8ce1cb302c4`. GitHub Actions confirmed both bytes exactly before calculation.
* Source columns are sums **per original hydrogen atom** across each 128-direction grid, not observed specific intensity or sky measurement. BASS source H/He background remains frozen through all computed rays.

## Constructed physical result

At each original epoch define `Q_ij[X]=sum_d X_d(q_di q_dj-m_ij)/sum_d X_d`, where `m_ij=(1/128)sum_d q_di q_dj`. The original midpoint grid has `m_xx=m_yy=0.3359375`, `m_zz=0.328125`. This discrete-grid centering eliminates the false isotropic quadrupole from naively subtracting δij/3. Four original source fields: rate of H I photoionizations per original H per second; photoelectron excess-heat production in eV per original H per second; cumulative absorbed photons per original H; cumulative photoelectron excess heat in eV per H.

**Actually executed** 3,840 original BASS direction rows + 30 history rows → 120 new physical PSTF rows, 4 physical observables × 15 original epochs × 2 original matched S0 backgrounds (BI and FLRW); each has six normalized symmetric-traceless tensor components.

The source-matched BI `Qxx-Qyy` is:

| Original tick | BI t [s] | instantaneous H I rate | instantaneous photoelectron heat |
|---|---:|---:|---:|
| 1 | 6.25e8 | +4.479569818784322e-8 | -2.2056382828404314e-6 |
| 800 | 5e11 | +2.362867580691986e-5 | -4.8286655205255595e-3 |
| 1600 | 1e12 | -1.422109593575342e-3 | -1.8871857835574693e-3 |
| 16000 | 1e13 | -1.1751255026461673e-3 | -1.5816192294270696e-3 |

At final BI tick16000 the actual donor cumulative photon absorption is `0.05299885834091917/H`, cumulative photoelectron excess heat is `0.003248155427589853 eV/H`. The associated cumulative quadrupoles are `Qdiff(abs)=-0.0013372806000970514`, `Qdiff(excess_heat)=-0.0016566298896876367`. These are *conditional physical photon statistics*, not new evolved electron fraction/thermal histories.

Physical interpretation: at first step the original Verner σ(E) logarithmic slope `-2.6887263918990483` gives the BI H I rate a positive x/y quadrupole while the very near-threshold excess-energy factor `(E-χ_H)` contributes an opposing log-slope `+132.1997293204128`, yielding negative photoheat quadrupole. The first-order analytic predictor at t=6.25e8 s is rate `+4.482167943038498e-8`, heat `-2.2037995038231047e-6`, matching the signs and scale. The original model **samples** a sign change of HI rate Qdiff between tick800 and tick1600; neither a unique continuous zero nor the physical cause of late-time sign reversal is proven here. The heating quadrupole remains negative at these sampled ticks.

## Explicit independent numerical/computational evidence

Original two donor gzip files SHA256 verified in Github workflow before computation, source-original 15×2×128 membership checked. Rust binary 3/3 unit tests passed: exact q-grid baseline/κ=2185/8192, FLRW/isotropic null, and first-order opposite signs. Full original 3,840/30 input was consumed by **Rust**; separate **pure Python** independent audit computed all 120 source-normalized PSTF records and checked original physical history. Github Actions run **#41318797174 SUCCESS** on tested HEAD `187b8a06c6fa34d611caa2cecd965938749aadce`. Repository verify run #41318797182 SUCCESS.

* Max |Rust − independent Python Q-component| = `1.7051487668246727e-16`.
* Max original 30-group source history relative-sum discrepancy = `4.2165327946590795e-16`.
* Max FLRW null tensor component = `3.926064346894655e-15`; max PSTF trace in downloaded 120-row CSV `2.2150266053974303e-16`.
* 120 physical CSV SHA256 = `823138a11f5b51e07a0e8a95a4cfd7b49a82747f609298babf5d2c1e5d1270c7`.
* Independent JSON SHA256 = `f54e48fbea6c06eaeceba063a29f2a3319fb9501a15a2612c38c7b5774c2e954`.

Failure preserved: initial code CI run #41318601515 **FAIL** Rust E0308, a synthetic test attempted to coerce closure capturing slope variables into a plain `fn` pointer. A scoped generic-`Fn` signature repair was committed `187b8a06...`; the second run **PASS**. This was an implementation defect, not a change to the physical equations or to any tolerance.

## Actual preservation

Three distinct evidence levels:
1. GitHub stage commits: theory `65ce2fefda7d1b1e5e917925aac13d1675dc60ff`; Rust source `0531f59f8a5f1149bbf4225911973afe4e9dc50d`; Python independent audit `0809305fdc262320c8c8c389de9c28b18c2484b4`; physical CI `d715a4181c249f8ea99cf7d4975a4832c2ba16fb`; repaired tested head `187b8a06c6fa34d611caa2cecd965938749aadce`. Original donor repo and all other source/worker files unchanged.
2. GitHub artifact #13088193443 (run #41318797174), 12,329 bytes, ZIP SHA256 `c086bde3c6cfd69017d31299288d9872074b21dc19585eaef0668b21e0015c73`. Independently downloaded ZIP CRC PASS, CSV and JSON SHA above exact. CI artifact retention 30 days, not permanent.
3. Confirmed **durable Google Drive backup**: `rei_bianchi_research_backups/REI_F08_PSTF_SOURCE_120_20261101.zip`, Drive file ID `1LMyY9EPvMBMKXWffFfISa5nomjqnb9WD`, verified size 12,329 bytes at `https://drive.google.com/file/d/1LMyY9EPvMBMKXWffFfISa5nomjqnb9WD/view`. This was an actual upload from the same GitHub artifact file identity. Local authorized desktop terminal became safety-blocked; no current-turn local-machine cold archive is claimed.

## Owner scientific admission and drift watchdog

**ACCEPT for exactly this use:** source-conditional BASS #323 original F08 frozen-HHe physical angular *ionization and photoelectron-heat* driver and 120-row Rust/Python-confirmed PSTF response. **HOLD for** original coupled native F08 photon/H-He/OTS/thermal evolution, Einstein-solved Bianchi metric, real observer Thomson/CMB/τ sky, full original F05 26-event Rust parity and canonical production. Preserve BASS #315 upstream unrelated strict CI failure. F05 BASS_HE #146/REC #190 project-owner source-conditional consumers accepted previously on REI #357, not imported here; BASS_HE #147 PW19 spectral donor is source-incompatible with F08 S0 and not spliced. REC #193 Rust migration is separate; VigilODE optimization is noncritical.

REI Central **28/88**, Working **33/88 nonadditive**, Physical Fast **4/7**, current canonical delta **0**. F05 official tick **160/131072**, tick161 NONAUTHORITATIVE, F09 provider BLOCKED, PRODUCTION HOLD. No merge, no force push, no source/tolerance/history mutations. Same-author hostile audit used exact q-grid null, source history, original hashes and independently implemented Rust/Python; native subagent and distinct-author blind referee NOT_RUN.

**Next mission-critical physical work:** use this verified F08 H I angular source in a *source-matched coupled* native Rust photon + H/He/OTS/thermal/14-ledger evolution, preserving Verner cutoff-vs-binding potential and actual photon number/energy ledger. Alternatively resolve original F05 0→64 historical parent parity for source-owner tick161 admission, or F09 provider domain. Do not manufacture a new observer sky or a fourth auxiliary spectral atlas.
