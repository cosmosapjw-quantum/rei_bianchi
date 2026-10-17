# RUN08: 동일 유한 출생 묶음의 BASS 광자–H/He/D 공동 기준해

2026-10-17. RUN07 parent 38a2a3d1779cc110371c95ad0d0ecd26a3df5781 이후 P4-S4C-RETARDED-JOINT-REFERENCE를 실제 실행했다. 샌드박스 전용 add-only 결과다. 원본 production/main/기존 checkpoint, 사용자 local/Codex/NCP/SSH는 변경하거나 실행하지 않았다. Native independent subagent/reviewer actor NOT_RUN.

## 입력과 이론

BASS121 SIGNED_MINUS의 실제 시간가변 prescribed Einstein–Vlasov donor, X=ln(a/a_ref), a_ref=1/21, X=.7.. .7004를 사용한다. 원래 MD14/BB50k fesc=.2,48개 spectral cell mean,8개 GL 방향,graded GL4 g=2를 전체 구간에 한 번 적용한 40개 출생시각,15360개 코호트를 고정한다. 원자 Grackle/Verner/Savin/DAtomicProvider와 제조 IC T=10000 K,HII=DII=.1,He4=(.8,.15,.05),D/H2.5e-5,YHe=.245,D defect=.0037 eV를 유지했다. 외부 CMB bath=2.7255/a K. REC donor/정밀 isotope spectroscopy가 아니고 새 gas/photon stress로 Einstein 방정식을 다시 풀지 않는다.

초기 proper 부피당 comoving 상태 Y=d n,U=d u,d=(a/a0)^3를 쓰고, 출생 이후 각 코호트 P=B exp(-tau), tau_X=(c/H)sum n_lower sigma[E(X)]를 적분한다. Killing ray는 각각의 birth E,a,b,mu를 보존한다. Y_X=d G_species/H+photo, U_X=d G_heat/H+photo_heat-2U. Gas RHS의 photo는 OFF이고 공동 photo 사건이 photon/species/heat를 한 번씩 소유한다. Wgas_X=2U, Wph_X=-epsilon_eV sum P E_X로 gas/photon geometric work를 따로 기록한다. 밀도/열/광학깊이/사건에너지/총 work 대수 residual5개는 Wolfram에서0이었다.

원래 native 분할법의 emitter만 고정 묶음을 읽도록 바꾼 opt-in wrapper를 생성해 동일 입력에서 비교했다. 공동 경로와 실제 native N1/2/8/32/64가 읽은 전체 (tb,Eb,mub,Ncom) tuple은15360x32=491520bytes 동일하다. SHA256 7d29d5c9dda88befd5141a9257170f70d96bcbd6937a2de14a159ac1e3d6a134. 과거 RUN05/06은 macrostep마다 birth 묶음을 다시 생성했으므로 그 endpoint와 이번 endpoint 차이를 same-equation 시간오차로 부르지 않는다.

## 구현과 독립 검증

75개 retained Rust 파일 byte-identical,lib.rs는 exact prefix+2 module declarations. Owner12개,input12개,기존 gas Python byte-identical. New retarded_joint.rs 및 Python vectorized photo/native gas assembly의15397도함수를4개 양의 상태에서 대조한 max block-scaled 차이5.071428923839942e-14.

15360 optical depths+27gas/reservoir+10photo/work=15397ODE. 큰 벡터의 RMS local norm이 소수 gas/ledger 성분을 희석하지 않도록 rtol/atol를 sqrt(D)로 나누는 component-scaled L2 control을 사용했다. 초기 PRE_L2 진단 photon residual5.15e-9는 별도 보존한다. 이 local criterion은 global error bound가 아니다.

전체 Radau는35s budget에서 endpoint 없이 중단됐다. 무틸트 isotropic gas와 diagonal LRS에서 동일 birth/E의 +/-mu 쌍은 같은 E와 hazard를 가지므로 B를 합한 exact reflection quotient7680groups(7717ODE)를 만들었다. 이는 원래8각도 support를 그대로 나타내며 일반 angular/spectral/age compression 또는 odd current/tilt/polarization theorem이 아니다. Paired Radau는 완료했고 full tight DOP853과 비교했다. Native trial negative state는 거절하며 global positivity theorem은 주장하지 않는다.

주된48cellmean packet에는 이번 짧은 구간에서 threshold crossing0개다. 별도 near-H/D 제조 ray2개에서4개 root를 검증했다. 이것을 main campaign의 threshold-crossing convergence로 승격하지 않는다.

## 실제 수치 결과

Full tight DOP853 reference: T=9994.351242713095 K, survivor=5.107743578718741e-7 comoving m^-3, xHII=.10027983875986388,xDII=.10117089407014525,xHeII=.15026849633661468,xHeIII=.04997447929742263. HI/HeI/HeII/DI cumulative events=(5.552147445079767e-5,4.024419623824095e-6,3.395112392936548e-9,1.38673716636783e-9) comoving m^-3. Born=6.0061450281933294e-5 comoving m^-3.

Paired Radau vs full tight DOP853: |DeltaT|=5.4569682106375694e-12 K, survivor relative=8.706237704674618e-15, HI/DI event relative=2.8100243043603576e-12/2.805162881638616e-12. Same native RHS/atomic data: different time integration and exact representation, not independent atomic data or rigorous reference enclosure.

Actual retained-native split versus SAME finite source joint reference:

| N | DeltaT K | Delta survivor/reference | Delta xDII |
|---:|---:|---:|---:|
|1|-.0492643756897451|-.000304336360788324|+5.03568271859045e-7|
|2|-.0237492255546385|-.000159954312763431|+3.12054934836770e-7|
|8|-.00579153167382174|-3.59041296303730e-5|+1.30189357169797e-7|
|32|-.00141162359432201|-7.11493735825695e-6|+3.99673589640548e-8|
|64|-.000716678432581830|-3.11846183614105e-6|+2.10743907463895e-8|

All4event errors are retained in NATIVE_FIXED_ERRORS.csv. These include native Euler/CX,frozen opacity and photo/gas/expansion splitting,not one isolated term. Separate controlled splitter uses union of birth and uniform nodes: its N1 already has41segments and is not native N1.15completed scientific configurations=10joint/pair/controlled+5native. PRE_L2 diagnostic1 and interrupted full Radau1 are excluded. Completed integration wall sum53.923726854s excludes installation,tests,interruptions,analysis,restore. Full tight DOP3.8347s; paired Radau31.7369s. No generic full EoR speedup claim.

Reference photonledger1.99228e-12,energy/initial2.23607e-15,energy/source1.24075e-12. Conservation is not accuracy. Max tau334.875 is outside exponential underflow range; no universal underflow treatment certified.

## Tests and clean restore

145/145 Rust all-target tests(138retained+7new),8/8newPython,strictClippy,new-code rustfmt PASS. Original failed assertions/compiles/RMS diagnostic/fullRadau timeout preserved. Core adiabatic-work zero-stub test observed red then green; not every test was TDD.

Final full ZIP restored into a fresh directory:198payload hashes,145Rust+8Python,strictClippy and representative full15397D DOP853+nativeN2 re-executed. Joint endpoint binary64 exact equality, nativeN2 CSV field equality and all15360source tuple bytes matched. Full15campaign not repeated. Restore build maxRSS253012KiB,one Cargo job,4GiB sandbox.

## Durable artifacts and next node

Git implementation delta: REI_RUN08_IMPLEMENTATION_DELTA.tar.xz,16912bytes,13members.
SHA256 d6d84c1570e2a6d43a40bcf4d1755a6d5e7bbb949bac4d336484b86044c4cfb9
Gitblob e9997d57aa7648bc84243f5c3f40c38fff68dc49
Actual scientific code/tests/packet and wrapper generator/numerical comparison. Requires RUN07 full source and RUN08 finite packet/native exporter. Not a complete standalone Git checkout or RUN06 Git backfill.

Full recovery: REI_ATOMIC_NUCLEAR_RUN08_RETARDED_JOINT_20261017.zip,5929312bytes,199entries,198hashedpayloads.
SHA256 d67ecd6d1f75b5617f6bcc05f8764779f9055eba977770c032db1372476f5b39
Drive https://drive.google.com/file/d/1VFhF5DkAGUP9T87h1QgYOuQZEewCWyMQ/view?usp=drivesdk :upload completed and authenticated full download SHA matched.
Dropbox /BASS_DERIVATION_DOSSIERS_20260912/REI_ATOMIC_NUCLEAR_RUN08_RETARDED_JOINT_20261017.zip :id:BSpOijBcT10AAAAAAD-oKQ,upload completed,provider hash82c3b9cc76d4c7f69d82ddcebcfb6a26dba6b23a265298aa3c4d828200b3c649 matches local Dropbox hash. Independent raw download attempted but blocked by runtime URL gate. No raw-download/restore claim for Dropbox.

Run scripts/REPLAY_OFFLINE.sh verify|build|tests|lint|reference separately with externally supplied Rust1.94.1 and Python dependencies. No toolchain,target,fonts,credentials bundled. External DELIVERY_RECEIPT.json records actual remote IDs,readback/restore levels without recursively modifying final archive.

Admission PASS_SCOPED_SAME_FINITE_NATIVE_BIRTH_BASS_JOINT_PHOTO_GAS_REFERENCE. Next P4-S4C-SOURCE-SUPPORT-CONVERGENCE: independently refine finite birth support while keeping geometry/atomic data/IC fixed; solve each support jointly before native time comparisons. Continuous source/spectrum/angle,whole donor domain,full EoR,FLRW-CONV,BI-SIGNED,ISO-COUPLE full,Einstein reaction feedback and unfinished Li/Be/nuclearT1-T8 remain HOLD. Original45/26DAG preserved in ancestors. No next automatic research cycle.

Methodology references: Reynolds et al.arXiv0901.1110/DOI10.1016/j.jcp.2009.06.006;PawlikSchaye arXiv1008.1071/DOI10.1111/j.1365-2966.2010.18032.x;SciPy1.17.0 solve_ivp official docs. They do not certify this construction's novelty or its numerical results.
