# REI F4 primary-source verification, 2026-10-30 (one bounded node)

**Scientific source event, not production admission.** Source parent: Draft PR #286 at `4532f24218d9c36dd3f470474e4dd9caa40699c0`; PR #285 overlaps and PR #284 has immutable head `661f34c5216aa52402be6f9db5c16ab2e55ecfb3`. This branch adds primary-source evidence only. No original science code change and no IVP.

## Drake 1969: first input provenance blocker closed

G.W.F. Drake, G.A. Victor & A. Dalgarno, *Physical Review* **180**, 25–32 (1969), DOI [10.1103/PhysRev.180.25](https://doi.org/10.1103/PhysRev.180.25), **printed p.29 Table II Li II**; inspect the publisher-scan image (uploaded by user). Original 8-page PDF SHA256 `213a9a620dbb9b5cc63ccdab246e6564018cc3262629d13303879ac133b59b95`. All **21/21** printed ordinates `A(y)` match exact existing `A_TAB` from PR #283 HEAD `e6b026757ddceb7fcd227229c0eb71391751e771`, code Git blob `5ae1d79bf3bbe62ac8a4b3d4cf356c5a20505200`. Unlike prior OCR transcription, this is a direct visual scan inspection. Data: [drake1969_tableII_LiII_21.csv](drake1969_tableII_LiII_21.csv). A second re-typeset 16-page PDF SHA256 `0f47cea95cc6dfe20f94cac3e35cea77c7e1072ac4d64f34a6871508c69288eb` is supplementary, not original.

For singlet `Li II (1s2s 2^1S -> 1s² 1^1S)`, `y=E_gamma/E_pair` on [0,1/2] and `A(y)` is in s^-1 per unit y. `A(0.025)=379`, `A(0.5)=5420`. Piecewise-linear integral `∫_0^{1/2} A(y)dy=1945.475 s^-1` exactly matches existing PR #284 tabulation and differs by only -0.2321% from the paper's Table I rounded `1.95e3 s^-1`. Half-domain **pair** density is `A(y)/1945.475`; the full labeled-photon density on [0,1] is `A(y)/(2*A_total)`. Scanned 21-knot monotonicity does not imply a physical continuum no-go or universal monotonicity.

## Ferrett 1987 and Langer 1991: source-bound local constraint, no invented global yield

Original Ferrett et al., *PRA* **36**, 3172 (1987), DOI [10.1103/PhysRevA.36.3172](https://doi.org/10.1103/PhysRevA.36.3172): supplied PDF SHA256 `37b1b988798aee21b14d1d1cb018b8b1052da130e094c60f04ef1b347ea48711`, printed p.3175 Table II, p.3176 Table IV. Define `R=σ(1s2s ^3S)/[σ(1s2s ^1S)+σ(1s2p ^{1,3}P)]`, `Rp=σ(1s2p ^1P)/σ(1s2s ^3S)`. At **77.5 eV**, both ratios were reported in the directly measured `hν <80 eV` range: `R=1.66(5)`, `Rp=0.085(7)`. Thus within the **n=2** Li II residual-state manifold:
```
f_3S = R/(1+R) = 0.6240601504
f_1P = Rp*f_3S = 0.0530451128
0 <= f_1S <= 1-f_3S-f_1P = 0.3228947368 (central)
```
If both printed ±1σ ranges are used as independent interval bounds, the conservative max is `0.3350268199` (not a confidence interval). This constrains **direct 2^1S residual production among n=2 events at 77.5 eV**, not a total K-shell source or any cosmological photon yield. The 1s2p ^1P satellite does not itself equal a direct 2^1S 2E1 event. At 77.5 eV, Table IV's `σ(n2)=1.90(8) Mb`, `σ(^3S)=1.19(10) Mb`, and unresolved `σ(^1S+^3P)=0.60(5) Mb` are compatible at their precision; additionally total photoabsorption absolute scale has 20% uncertainty. Keep 80-eV `Rp` on its measurement/derivation boundary, and do not use higher-energy assumed values as direct measurements.

Langer et al., *PRA* **43**, 1652 (1991), DOI [10.1103/PhysRevA.43.1652](https://doi.org/10.1103/PhysRevA.43.1652): supplied PDF SHA256 `b92587d22c8698c4f46bd9069ffe5fe1f3cdd170da253653ada16f770d73fd02`. Resolves 1s2s ^1S and neighboring 1s2p ^3P (about 360 meV), reporting branching curves over 74–150 eV, but no machine-readable exact `f_1S(E)` table was extracted. Authors identify theory failure for the ^3P satellite; do not replace this with relaxed-HF values.

## CHIANTI: documentation supported, raw unverified

[Official CHIANTI TWO_PHOTON documentation](https://www.chiantidatabase.org/doc/continuum.html) attributes the **He-like distribution** to Drake et al. (1969) **and the total A rates** to Drake (1986), *PRA* 34, 2871. It states the old Table II values are divided by Drake (1986) A: direct raw-file ordinate equality would be the wrong comparison without normalization. NASA public mirror indexes list `continuum/heseq_2photon.dat`, but direct binary download and SHA verification failed in this session. `CHIANTI_RAW=NOT_ACQUIRED; CHIANTI_Z3_NUMERIC_CROSSCHECK=NOT_RUN`.

## Verdict and immutable boundaries

Verified source provenance: `DRAKE1969_PRINTED_LI_II_21=21/21`. New derived, measured-local n=2 branching upper bound: `f_1S(77.5 eV)<=0.3228947368` central. Parent PR #286 BASS193 computed outcomes **not rerun** and cannot be reinterpreted as actual heating, electron deposition, optical depth or CMB. Live CI at parent commit: workflow run `41034936220` FAIL at inherited `cargo fmt`; subsequent Rust test skipped; targeted source verifier independent.

`WORKING_DAG=33/88; CENTRAL_DAG=28/88; PHYSICAL_FAST=4/7; CANONICAL_DELTA=0; SOURCE_AUX=1/1_SCOPED; F4=PARTIAL; L4_READY=false; PRODUCTION=HOLD; R6_C9_DISTINCT_AUTHOR=NOT_RUN; NATIVE_SUBAGENT=NOT_RUN; NO_NEW_IVP=true; NO_MERGE=true; NO_FORCE_PUSH=true; NO_BUDGET_RESET=true; AUTO_NEXT_NODE=false; STOP_AFTER_ONE_BOUNDED_NODE=true.`

**Next separate gated node only on later approval:** obtain CHIANTI raw and state-resolved energy-dependent `σ(1s2s ^1S; E)` with provenance; then evaluate complete REI17/BASS21 radiation/electron/thermal source-clock consistency. Do not treat this one bounded document-level node as enabling those calculations.

Conversation Library source-inclusive *report* backup (not publisher PDFs): `/REI_F4_LII_LI1S_SOURCE_CHECK_20261030/REI_F4_LII_LI1S_SOURCE_CHECK_20261030_FULL.zip`. Local source manifest and standalone `verify_sources.py` retained in this backup.
