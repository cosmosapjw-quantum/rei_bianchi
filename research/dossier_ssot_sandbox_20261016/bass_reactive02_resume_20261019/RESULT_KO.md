# BASS-REACTIVE-02: longer-span controlled study, not convergence admission

2026-10-19. 앞서 중단됐던 reactive01 ZIP(84805302...)을 먼저 Drive/Dropbox에 보존하고 PR201로 재개했다. 기존91개 crate 파일과12개 물리owner를 바꾸지 않고 새6개 native 연구파일을 추가했다. 완전한97file crate는 parent ZIP과 이 Git source delta에서 복원한다. 사진/기체/기하 압축이 아니라 소스 전달 형식이며, parent archive bytes 자체는 Git에 들어있지 않다. `study_controls.rs`는 개별 열람용 동일 코드 사본이다.

## 실제 실행 결과

Rust190/190(기존179+controls6+oracle5), Python6/6, strict Clippy와 새파일rustfmt PASS. 14개 planned native history 중13개,528macrosteps 완료. `cx_tight`는 rtol1e-14/atol1e-16와 기존20000attempts/2500000ratecalls에서 step1 Cx(WorkLimit),0rows. 예산/정확도기준을 바꿔 숨기지 않았다. 모든 계산 sandbox serial; native subagent NOT_RUN.

Duration8e12s는 기존8e10s의100배다. 초기 H*duration=.0009468555이며 여전히 넓은 EoR history가 아니다. 기존회귀조성,T0=10000K,제조Ddefect.0037eV,CMB20K,MD14/BB50k,one-way BASS,CI/RR/CX/CE/FF/CMB ON을 유지했다. 반응 gas/radiation을 Einstein solver로 되먹임하지 않는다.

|Ntime|surviving photons com^-3|DI photo events com^-3|
|---:|---:|---:|
|16|4.312673941466e-10|8.775858657703e-8|
|32|2.559394778750e-9|8.789701369482e-8|
|64|6.247609370061e-9|8.795333733841e-8|
|128|8.951927542721e-9|8.793623193585e-8|

N32/64/128 survivors finite self-order=.44766; DI differences change sign. No uniform second order or converged long-span state. max number/energy ledger7.91607e-15/6.94544e-16 does not rescue accuracy. Independent geometric-work gap/source energy2.41122e-6 is a different diagnostic.

Old split fixture changed spectrum AND birth GL together. New research controls independently vary them. At same N32,GL2original as Q00: spectrum-only survivor change+0.23017157%, birthGL2->4-only+228.34269324%, interaction-0.11897379%, combined+228.45389102%. For DI corresponding changes-.03097438%,-.09285093%,+.00005070%,-.12377460%. Identity Q11-Q00=(Q10-Q00)+(Q01-Q00)+(Q11-Q10-Q01+Q00) checked. These are finite numerical contrasts, not absolute truth errors.

## Mechanism and frozen oracle

For constant positive source j and opacity kappa, new photons survive as B Phi(tau), Phi=(1-exp(-tau))/tau, B=jh,tau=kappa*h. Finite interior GL nodes give Phi_GL=sum w exp[-tau(1-u)]. With delta=min(1-u)>0,0<=tau Phi_GL<=tau exp(-delta tau)->0, while tau Phi->1. Thus fixed-rule thick-limit relative error tends to-1. This is a scope-specific quadrature property, not impossibility of RT/other quadrature. Newborn photons produced in a ~1/kappa layer next to the end of the time slab are unresolved.

Native t0source384cohorts and original frozen HI/HeI/HeII/DI rates: exact total survivors1.001116864362e-8. GL2 frozen-reference biases N16/32/64/128=-95.7066%,-74.5057%,-37.7598%,-10.8159%; GL4=-50.0460%,-16.2824%,-2.35237%,-.115615%. N32tauMax46.3841;98.3226% of birth photon weight has tau>10. Both exact and GL photon inventories still close. Do not use this frozen oracle as the exact evolving HHeD history.

Independent Python uses different Legendre quadrature plus N-step recurrence on printed native rates, not Rust's closed recurrence formula. All8cases: maximum survivor/species relative discrepancy1.35386e-15. Scalar8point independent SciPy integration of Phi discrepancy8.88178e-16. Atomic rates shared, no independent atom-data validation. Wolfram returned exact identities and limit values with an intermediate limit warning, preserved rather than labelled warning-free.

Fresh directory: all190tests/lint/build/Python6 rerun; four factorial histories128steps reproduce every scientific CSV field (timing excluded); frozen8case/source384row/scalar8row are byte-identical. Not all13long histories rerun. TDD stubs and lint/import/if repairs retained, no oldsource/tolerance change.

## Reproduce and preserve

1. Download exact parent reactive01 ZIP SHA84805302269e729bf38d674cdf77f373cb78c8b31125536c2aa7281f9f7a45fd from Drive17jeNcbxux1yukNc2Jxj0-RiXe6KV_rS2 or recorded Dropbox. Then `python RESTORE_STUDY.py PARENT.zip /absolute/new-study`. The compressed packet is hash checked and full97file source manifest verified; actual local restore passed.
2. `bash /absolute/new-study/RUN_STAGE.sh /absolute/new-output` with Rust1.94.1, NumPy/SciPy. The known cx_tight WorkLimit is retained as one failed attempt, not falsely counted as a full result.
3. Full new source/data/log/evidence ZIP1716083bytes,197members,196payload hashes. SHA256 `6f50cbed0c249f840d23861bce79a9300e505ea5c69c95f19df420842b34819e`. Drive: https://drive.google.com/file/d/1WSP4HpxQZruBU-1znvQS_-pHwqX67blk/view?usp=drivesdk ; actual raw SHA256 readback MATCH. Dropbox: `/bianchi/rei_bianchi/research/REI_BASS_HIERARCHY_BACKUPS/REI_BASS_REACTIVE02_LONGSPAN_20261019_6f50cbed_FULL.zip`, id:BSpOijBcT10AAAAAAD_Pog, upload completed. Final readback levels in PUBLICATION_RECEIPT.json.

Study COMPLETE_VERIFIED; LONGSPAN_SOLUTION NOT_ADMITTED; fullP4 PARTIAL; SA01/02,FLRW-CONV,BI-SIGNED,FULL_EOR HOLD. Next unit: positive birth integration preserving exact frozen-Phi limit while retaining distinct birth-time Killing trajectories; then matched coupled convergence. The existing production birth sampler was NOT repaired in this step.

Context literature: Mackey2012,A&A539,A147,DOI10.1051/0004-6361/201117984; Fleury/Pitrou/Uzan2015,PRD91,043511,DOI10.1103/PhysRevD.91.043511. Exa/SciSpace/primary-source checks establish literature context, not this code's correctness. Full report and raw CSVs are in the verified ZIP.
