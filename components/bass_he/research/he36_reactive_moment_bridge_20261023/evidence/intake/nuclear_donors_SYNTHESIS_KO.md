# 최신 REI / bass_cr 조사와 HE36 재사용 판정

## 조사 범위와 결과

2026-10-23 UTC에 읽은 GitHub 스냅샷이다. `rei_bianchi`의 263개 브랜치(100/100/63)와 모든 PR 목록 221행(100/100/21), `bass_cr`의 175개 브랜치(100/75)와 모든 PR 목록97행을 pagination 끝까지 목록화했다. 브랜치 이름이 오래되었어도 최근 갱신된 PR96 등은 최신 head에서 읽었다. 최근 원자·핵·열 관련 단원을 우선해 49개 파일을 별도로 확보했으며 모든 파일의 Git blob ID와 실제 저장 bytes가 일치했다. 49개는 확보·해시 대조 수이며 전체 historical branch 본문을 모두 읽었다는 뜻은 아니다. 깊은 검토는 아래 계약, 물리식, 코드 및 결과에 집중했다. 완성된 IVP/test/render/benchmark 재실행, 새 IVP, 원격 변경은 모두0이다.

원격 원본 목록은 `rei_bianchi_branches.json`, `rei_bianchi_pulls.json`, `bass_cr_branches.json`, `bass_cr_pulls.json`; 파일별 pin/blob/SHA256/URL은 `READBACK_MANIFEST.json`에 있다. root의 다른 저장소·대화·백업 조사와 합쳐야 전체 접근 가능 조사 범위가 된다.

## 최신 단원에서 실제로 확보된 것

| 단원 / immutable head | 현재 재사용할 결과 | 남아 있는 물리 범위 |
|---|---|---|
| REI PR221 `9620e1fcc4bdda76e0311206f614234926600381` / `rei_coupled_isotope_sandbox_20261022` | 21개 absolute isotope-charge state, 공유 electronic blocks, 준비된 RHS, `J=B+u q^T`, zero-aware unary/binary event와 supplied-energy ledger, 156 baseline + 별도 onset2 checks | 조건부 local operator이며 실제 모든 핵 reaction rate/daughter/thermalization 또는 tensor source를 공급하지 않음 |
| 같은 pin / `rei_coupled_local_flow_20261022` | pure-H CaseA RR+온도+escaped-energy exact orbit; neutron beta+RR prescribed-T exact subflow/Strang/Bessel reference. 103check와 별도 paired timing96, 직접 DOP853 채택 | beta 총Q를 열로 놓지 않음. 전자·중성미자·recoil partition, stopping, daughter charge와 실제 coupled cosmology 미확보 |
| 같은 pin / `rei_bootstrap_energy_providers_20261022` | supplied-moment scalar thermal ledger; 6 RR derivative-of-fit adapter와 ground-target DR scalar 수치 체크 | derivative fit의 empirical thermal accuracy, DR cascade/spectrum, 낮은T CI, CX, source injection 미완료 |
| REI PR219 `6a12f3865d9ea427c1391c41caed8bb7cb7ec00d` / `rei_tritium_production_audit_20261022` | 명시한18family/34directedchannel, 82savedbackground, constant-S와1/v conditional kernels, log-domain tiny inventories, T/n fast subsystem, event Q/전자/핵수 장부 | 모든 nuclear species를 bare/instant-thermalization/passive bulk로 두는 별도 감도 모형. 실제 중성 plasma low-T data, stopping, detailed electronic daughters, nuclear photons 재처리 미확보 |
| REI PR220 `8be7533cc97b3302bf42608699d6e8313ed6af8a` | 62→33 reflection/equal-electronic invariant reduction;127cases+2full62oracle 완료,21populations출력 | gas pi_b=0, prescribed T/UV, photo/RR/DR와Thomson; source/thermal/radiative/full nuclear closure 아님 |
| REI PR222 `b4b5d289aaad9ef167f683f19418b0ff87ed8425` | 7repo kernel의 source/backup map, C3 zero/tiny source probe, 다음8개 의존성 | PR221 후속 결과와 중복되는 C3를 새 결과로 다시 세지 않아야 함. donor workflow1.3은 우리 workflow1.0.0으로 이식하지 않음 |
| bass_cr PR96 `ba39fc75521aa18705ec832d789e50dd5c6565bc` / `cr_c22d_cold_ci_20261022` | CCC H1 total CI87row finite-domain integral, 보존적 CI energy/number adapter, 새4IVP 및 C22E saved8851sample line-admission진단 | tail/interpolation physical bound, excited-state/cascade/line escape, secondary energy-sharing/source moments 및 full nuclear closure 미확보 |
| bass_cr durable branch `5750489be6ad80b4e142f5712c656c33ae07f097` | C22C archive identity/657payload 검증과 old4IVP receipt의 포인터 | evidence-only checkpoint, 실제 전체source 게시와 같은 뜻 아님 |

## HE36에 바로 가져올 파일

1. **새 STF loss 계산의 수치 입력:** `readbacks/bass_cr/research/cr_c22d_cold_ci_20261022/sources/CCC_TICS_1S.txt`, SHA256 `7a87a2c9f2116ee36c0786b379dac08e1f4d92a49504fe542e6aa71cbb279bae`,5754B, Gitblob `f4091016b22f11288138c8519f55c7f07f560017`. Source energy는 electron incident eV, σ는 a0²이며 π나 추가 multiplicity가 없다. 87행, E=13.6058…968.61eV,첫 양의 표본13.64eV. 현재 finite model은 piecewise-linear σ다. 전체 physical tail·보간오차를0으로 두지 않는다.
2. **기존 finite Maxwell integral:** 같은 단원의 `ci_finite.py`, SHA256 `859cdf616ffa165c9fb3c3372d2202f5449e4b9a74a289a725fe456e26eb55b2`. 공통 Taylor moment J0–J2와 threshold-scaled exponent로 기존 scalar rate를 계산한다. 새 γ·STF 함수를 유도할 때 현재 scalar진단 전체 재실행은 불필요하며 새 모멘트만 판별해야 한다.
3. **원자·핵 사건 number/energy adapter:** `readbacks/rei_bianchi/research/rei_coupled_isotope_sandbox_20261022/code/local.py`, SHA256 `d0998261323609901f0cf9636d71282e7848bac6c00c1e5f7240ed7fc540e88a`. `ResolvedEvent`는 isotope21에서 정수stoichiometry, factorial symmetry, log coefficient, baryon conservation, explicit reservoir energy를 검사한다. `Rpart=(1+q)·ν R`이므로 핵수 변화도 포함한다. `ABSENT/UNRESOLVED/SUPPORT_ZERO`와 underflow를 구별한다. 이는 제공된 reaction계수/분기와 에너지 장부만 계산하며 물리적 daughter의 근거를 생성하지 않는다.
4. **Scalar thermal ownership:** `readbacks/rei_bianchi/research/rei_bootstrap_energy_providers_20261022/thermal/thermal_ledger.py`, SHA256 `f198552ebca8e98efad315da00a8c38053bfbba852b16dae9c22c608abd2bd96`. 이 코드는 scalar supplied moments만 갖는다. HE의 shear work 및 reactive STF를 추가하면 그 변경은 새 단원 scope다.

## CCC 원전과 finite-mass 해석

Author page `https://atom.curtin.edu.au/CCC-WWW/index.html`를 이번에 직접 읽었다(web ref turn25view0). Hydrogen complete dataset link는 `https://atom.curtin.edu.au/CCC-DB/H/I/ELECTRON_IMPACT/e-H_XSEC_LS.zip`이다. 웹 도구의ZIP읽기는 unsupported content type으로 끝났고 전체archive를 다시 받았다는 주장은 하지 않는다. 이미 Git에 게시된 선택87행을 exact pin/blob/SHA로 재사용했다. Author page와 선택 table/단원에서 명시적 permissive-license 문구는 관측하지 못했으므로 임의 license label을 부여하지 않는다. 원전 attribution은 유지한다. Bray et al.2018 DOI10.1103/PhysRevLett.121.203401와 원본 source provenance는 donor의 `evidence/theory/THEORY_PROVENANCE_AND_COVERAGE.json`에 명시돼 있다.

CCC donor 계약 자체가 finite-mass/isotope source consistency를 OPEN으로 둔다. 유한질량 유도에 이 표를 쓰려면 **source가 보장하지 않은 부분은 조건부 kinematic model**로 분리해야 한다. Table energy가 E_table=m_e g²/2인 σ(g)를 유지하면 relative kinetic energy는 E_rel=μg²/2이고 Maxwell weight의 table energy scale은 (m_e/μ)kBT다. E_table과 E_rel을 그대로 동일시하는 해석은 다른 모형이다. 전자에 비해 큰 H 질량이라는 이유만으로 그 구분을 삭제하지 않는다.

## 통합 시 충돌과 권고

- CR의 Hfamily threshold13.6058eV는 CCC source convention이다. HH의 D43K isotope defect 또는 NIST H1precision값과 자동 일치하지 않는다. HE36의 순수 incoming-loss moment에서는 CCC σ의 incident-energy convention을 유지하고, 총 CI heating·binding·PI/RR registry를 가져오지 않는 편이 scope가 명확하다.
- CR C22D REPORT의 secondary crossrepo intake에는 HE85 recovery rerun이라는 오래된 주장이 있다. 이를 HE32 authority로 채택하지 않는다. 사용자와 HE32 pin16a424...의 actual recovery record(1392payload검증·새IVP0)가 우선한다.
- REI local.py는 incoming/product pressure tensor를 갖지 않는다. 따라서 scalar Rpart/Q/Jacobian 재구현은 중복이고, **common-T/common-bulk Grad의 binary incoming-loss STF**는 현재 donor들과 다른 실질 작업이다. Product tensor moment는 explicit resolved input으로 남겨 totalreactionJ에 대한 무근거0채움을 막는다.
- 이 조사만으로 B1/B2 전체 또는 full19채널 핵망을 완료로 승격하지 않는다. 새 단원은 B2의 반응 incoming moment 하위 의존성을 닫고 제품분포·elastic exchange·closure·gas/metricfeedback의 나머지 DAG를 계속 보존해야 한다.

## 접근·실행 경계

큰 recursive Git tree 조회는 Transport closed였고 directory/file API로 필요한 내용을 확보했다. 두 개 guessed path는404였으며 실제 디렉터리목록에서 경로를 찾아 교정했다. CCC직접urllib는 sandbox Operation not permitted였다. 웹 도구의 authorpage를 읽는 데는 성공했다. 이들은 도구·접근 결과이며 물리적 no-go가 아니다. 이 child는 다른 대화 전체나 backup bytes를 읽었다고 주장하지 않는다.
