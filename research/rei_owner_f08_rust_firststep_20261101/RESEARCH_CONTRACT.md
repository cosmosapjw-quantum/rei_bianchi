# REI F08 Rust owner first-step photon/HI physical consequence
Date 2026-11-01. Fixed science unit, selected physmath R5/R6/R7/R8 + Rust C5/C6/C9/C10 (cross-repo owner consumption, no unrelated R/C loops).

## Scientific question
In original REI F08 S0 prescribed BI and matched FLRW, what is the first-step HI photoabsorption-event and photoelectron excess-energy impact of original fixed-grid hat remapping versus exact 13.7 eV redshifted null characteristic, on the **same original first-step HI density**, source birth, implicit absorption rule and Verner1996 AtomicProvider source?

## Locked inputs
- REI owner F08 #349 HEAD 58f7ffb685c3758f1fed1113ff8134a24478c3df, BASS #321 HEAD 178d93c380a0e868a22869c3160d81c0aa643098. Owner current F08 PR #358 HEAD 5ba12e8c7f66315024f5d71dcc5fb168310b0865.
- Full source archive exact SHA256 530370df21fd40e57165bd0882c17c25f684d571788c5c2db70f2c3105a48cfb, retained read-only under /home/cosmosapjw/archives/BASS_REI_F08_S0_ORIGINAL_HAT_SUPPORT_20261101.zip.
- Original source Rust atomic_provider.rs SHA256 b0b572d3940a7a1f740e09d5f43c60236ec61511e8bdbcc68e60395ec7e107d3. Original paired runtime source b6c1d2a07ab51ff02318139ae18387b77f61859c08037347f788524df770ebe7.
- Original BI/FLRW S0 16,001 proper electron histories, 16,000-step S0 gas curves, 8x16 original null directions, 17 native energies; hash-check exact header/history before using.

## Fixed physical model
Metric ds2=-c2 dt2 + sum ai2 dxi2, H BI=(1.01,0.99,1)e-14/s, FLRW=(1,1,1)e-14/s, first dt=6.25e8 s, original source 0.05 photon/H at E0=13.7 eV + 5e-15 photon/H/s injected at endpoint. Compare no-scattering characteristic E'(q)=E0 sqrt(sum qi2 exp(-2Hi dt)) with original positive linear hat fixed-grid projection to E-=13.675 and E+=13.7 eV. Original frozen native nHI(t1) extracted from original electron/history pair. Use original *implicit* per-node absorption fraction A(E)=lambda(E)/(1+lambda(E)), lambda=c dt nHI sigma_Verner(E). Compare physical H I event and photoelectron excess-energy per H; use chemical binding chi_H=13.598434599702 eV as an explicitly chosen independent physical ledger. No new H/He IVP, no continuum error claim and no observed CMB.

## Acceptance
Exact original hashes; 128 actual q per branch; native original Rust AtomicProvider verbatim, no new atomic fit; explicit first-step source and photon number/energy invariants; independent Python stdlib oracle with disjoint implementation; precise signed difference and physical scope; tests normal/release; no changes outside additive research subtree; Git backup and isolated PR comment/commit; no merge, original F05 tick161 no promotion.

## DAG at selected checkpoints
REI Central 28/88, Working 33/88, Physical Fast 4/7; canonical delta0; production HOLD. Stage R5 start: research contract and immutable Git branch. Drift watchdog: only advance physically interpretable HI absorption/heat, not more support-only restatement.
