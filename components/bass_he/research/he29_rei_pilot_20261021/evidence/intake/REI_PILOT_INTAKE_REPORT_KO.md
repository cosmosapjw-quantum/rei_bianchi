# REI 최신 intake와 HE29의 당일 pilot 기여

## 실제 조사 범위
- 완료 시각: 2026-10-21 05:22:58 UTC.
- GitHub branch search 100/100/53/0 및 REST branches 100/100/53/0으로 현재 접근 가능한 253 branch/250 unique HEAD를 읽었다.
- 250 unique HEAD의 Git commit metadata를 모두 실제 읽었다. 실패0. 2026-10-19 UTC 이후 committer-date HEAD는16개다. Git 날짜는 native 실행 날짜가 아니다.
- 최근 PR query updated:>=2026-10-19 all states topn100은15개를 반환했다. Sigma/Pi, sweep, PHYS73 query도 읽었다. REI PHYS73 PR 검색은0이며 다른 repo나 미게시 실행 부재를 뜻하지 않는다.
- 재사용에 필요한 PR147/141/150/198/199/210/211/212 실제 메타데이터8개와 표적 source/results를 읽었다.
- git ls-remote는 browser-proxy 접속 실패 exit128. GitHub connector REST/파일 조회로 해당 조사 범위를 완료했다.
- 과학 적분, benchmark, 이전 tests 재실행, NCP 연결, remote mutation 각각0.

## 현재 결과와 실행 queue
- PR198 HEAD3360a345f8e0f2f9d2b6bdd42d21e584446ec9b8: 현재 SSH handoff 수정. 기존246jobs144done/100notrun/2blocked, V12 44/144, V13/SSPRKdone. 원 debit와 unresolved allocation 상태는 보존한다. 최신 사용자 shared-resource 승인은 종전 process-presence blanket hold와 구분하여 상위 controller가 반영한다.
- PR199 HEAD964b2e3c098f6e475999a4eddc7a6aa0f8f053cc: native time8/16/32 완료, next_ready=[], native age/time convergence HOLD. 완료 job 재배정0.
- PR210 HEADe4c8133288614638792888367ca10b2ded3138ff: BRPERF01 exact-EOS-T prepared bundles, Direct-default, source-bound compact table, SIMD, persistent photon pool. 현재 완결된 bounded optimization을 재사용한다.
- PR211 HEADc9deb933761a8d2593d1176aee028cd423bdbc05: RUN19 prepared direct/batch native sharing 및 guarded table. 현재 물리 owner/closure와 구분한다.
- PR212 HEADa23c65ab261a0ad54e410944acdf471d21274a57: 기존6repo orchestration receipt를 현 최신 반환으로 덮어 쓰지 않는다.

## 오늘 이미 저장된 데이터로 만들 수 있는 그림
PR141 HEAD80825585f9fe31d2ee0d5af545ada3fa1f52be72의
research/rei_c15_sigma_pi_feedback_20261015/C15_STUDY_RESULTS.json:
907665B, SHA25640c0ae6325fdba5cf47f8240ee655769c1f236351a2c9004e7f3488d16647b7e,
Git blob5f1ac55a2aabb73897fc8d0c2674032237d75ad0.
원8개 scenario x64steps =512 saved rows, 각 H,s_inv_s,Sigma,Pi_gamma/nu/massive/UV,gasT,HHe fraction.
7개 physical scenario와 GRAVITY_PI_DISABLED_CONTROL 1개다.
원 warm a=.1999→.2, near-z4, native C13 HHe/MD14/CaseA + gamma/nu + massive + Einstein feedback 범위다.
full-cold-EoR 또는 최신 RUN19/default production 실행으로 소급 표시하지 않는다.
최초 saved row는 a=.199901562...로 이미 첫 step 후다. exact initial Pi라고 쓰지 않는다.
CSV는 H를 생략하므로 전체 JSON을 정규화의 SSOT로 사용한다.

C15 tensor convention:
sigma^i_j=diag(-s,-s,2s).
Pi_*는 DeltaP=P_parallel-P_perp 단위J/m^3(Pa), pi^i_j=diag(-DeltaP/3,-DeltaP/3,2DeltaP/3).
물리 총stress는 signed species 합을 낸 후 norm을 구한다.
반수축 norm은 |sigma|=sqrt3|s|, |pi|=|DeltaP|/sqrt3.
Frobenius norm은 두 값의 sqrt2배.
H가s^-1이고 pressure가J/m^3이므로 dimensionless stress는
(8piG/c²)|pi|/H² = (Einstein kappa_E*c²)|pi|/H².
GRAVITY_PI_DISABLED_CONTROL에서는 physical species sum이 남지만 Pi_total_source=0다.
physical stress와 enabled Einstein RHS를 구분한다.
원기록을 이용한 좌표 재표현/그림이지 새수치적분이나 원래 미완료 regular 2D sweep completion은 아니다.

## 새 solver 없이 준비할 수 있는 정규 2D pilot
PR147 HEAD3b85dedce84d37b3e165da00685a8a984950aafe의 원 source:
1. research/rei_bass_hierarchy_backreaction_20261015/canonical_fv_20261015/canonical_fv.py
2. research/rei_bass_hierarchy_backreaction_20261015/species_hierarchy.py
3. research/rei_bass_hierarchy_backreaction_20261015/lrs_boltzmann.py
4. research/rei_bass_hierarchy_backreaction_20261015/suppliers/bass/rei_axbi_background_supplier_20261015/source/REI_BACKGROUND_FAMILY_LOCK.json

SourceLock은 위 JSON에서 직접 초기화 가능하다. run_hierarchy.py를 import하면
불필요한 BASS comparison/electron donor import가 따라오므로 canonical modules만 사용한다.
CanonicalFVSpecies(...).integrate(n=...,rtol=3e-11,atol=3e-13)는 기존DOP853/원rhs를 사용한다.
부모 PR145 canonical source SHA25691c1641b851aa9580141d4423e2579ced5f11b95aa716b3fc2cb0137df344cc5.
여기서는 호출하지 않았다.

PR147 diagnostics의 Pi_gamma_J_m3/Pi_nu_J_m3/Pi_matter_J_m3는 C15 DeltaP가 아니라 pi_s=DeltaP/3이다.
따라서 여기서 totalpi_s의 normhalf는 sqrt3*abs(totalpi_s)다.
원 source Pi 변수명을 새normalized Pi와 혼동하지 않는다.
두norm만으로 일반Bianchi I initial tensors/relative orientation/species stress partition이 정해지지 않는다.
당일 pilot의 LRS/coaxial slice, signs, gamma/nu/massive partition 및 finite source positive domain을 명시해야 한다.

최신 main ae3402713c4b6530ab2b27f008f5f5d5c6a999ed,
RUN19 c9deb933761a8d2593d1176aee028cd423bdbc05,
BRPERF01 e4c8133288614638792888367ca10b2ded3138ff에서 위 canonical_fv.py exact path는
각각 실제404였다. PR147 source를 최신 native closure로 조용히 대체하지 않는다.
별도 historical branch source를 명시적으로 vendor/import하는 contribution으로 취급한다.

## PR147 저장 결과의 한계
PARALLEL.json은16 IC와 timing/drift aggregate만 보존하여 개별16endpoint를 복구할 수 없다.
RESPONSE_INITIAL.json은baseline 및Jacobians와 일부physicalsummary를 보존하며 각 ±pair endpoints는 없다.
NONLINEAR_DEGENERACY.json에는2개의121point saved observable traces와initialspeciesstress가 있다.
따라서16점새scatter를데이터없이그리지않는다. C15의512행이현실적인saveddata 첫그림SSOT다.

## 재사용 및 읽기 identity
LOCAL_SOURCE_COPY_READBACK.json:12개다운로드source/doc file 실제Gitblob일치.
LOCAL_RESULT_COPY_READBACK.json:6개saved output/source file 실제Gitblob일치.
SOURCE_READBACK_INDEX.json, SAVED_RESULT_INDEX.json은다운로드경로/핀을제공한다.
실제수치검증재실행PASS가아니라현재읽은bytes의copyidentity다.
현재latestREI AGENTS의anti-bureaucracy/tiereddelegation/trustedresearch 정책을읽었다.
