# D9 실제 전달과 다음 작업

## 실제 전달 확인 — 20261021T141519Z

D9 과학 판정은 **PASS_SCOPED_D9**이며, 과학 코드와 결과는 아래 source commit에 고정되어 있다.

- Source commit: `407f2a30efcdd0c4c4afb180cbe7d31f90cc0401`
- Source tree: `7590e6f8a7ffcc3153d9b7595325ab24c7844783`
- Git 전체 readback: **94 / 94 파일**, **6,410,424 bytes**, SHA256 및 Git blob SHA1 일치. Tree mode도 **94 / 94 PASS**.
- 최종 archive: `REI_D9_FINAL_DELTA_20261021T141112Z.tar.gz`
- Archive 크기: **4,576,719 bytes**
- Archive SHA256: `bf3547dd6542626d011d51251e1a091d9ac0cca5480d6124c6faca09cfc3d679`
- Drive 파일 ID: `1V-aTSz2A74dgKwXmkOeBh-EcE03RVZ5V`
- Dropbox 파일 ID: `id:BSpOijBcT10AAAAAAD_hkA`
- 두 provider의 전체 GET, archive bytes / SHA256 및 모든 member 검증: **PASS**.

최종 metadata는 위 archive를 포장한 뒤 작성된 별도 기록이다. 이 metadata를 포함하는 실제 commit M은 외부 post-publication ACK에서 확인한다. M을 자기 파일 안에 미리 적지 않는다. 권위 있는 전달 기록은 `research/rei_unified_sigma_pi_20261021/D9_COMPONENT_SHEAR_BUDGET/D9_DELIVERY_ACK.json`이다.

Source CI run **39614246060**, job **119270894522**는 기존 Rust 경로의 `cargo fmt`에서 실패했고 Rust tests는 skipped다. D9는 Rust source를 바꾸지 않았으며, 이 CI 결과와 D9의 scoped PASS를 구분한다.

다음 단일 노드는 **D10_ZERO_INITIAL_MATTER_STRESS_GENERATION**이다. 상태는 **READY_FOR_THEORY_AND_SAVED_DATA_INTAKE_NOT_RUN**이며, 먼저 analytic / saved-data contract를 고정한다. 최초 허용 new IVP는 **0**이다. 완료한 pilot, D8 또는 D9를 다시 실행하지 않는다. 실제 D9 NCP 실행은 **NOT_RUN**이다.

PR198 scoped PASS, AGE convergence HOLD, Grackle bound NOT_ESTABLISHED, production scientific admission NOT_ISSUED 및 V12 제한은 그대로 유지한다.

---

# 보존한 연구 인계 본문

# 다음 연구 대화로 이어가기

```text
[$physmath-research-loop] [$exa] [$scispace] [$wolfram]
cosmosapjw-quantum/rei_bianchi의 통합 연구를 이어가라.
먼저 현재PRHEAD/관련새branch/접근가능handoff/Drive·Dropbox의 새 실행 결과를 조사하라.
이전 assistant 완료 문구보다 실제source/raw/receipt를 우선하며, 과거HEAD를 현재값으로 가정하지 마라.

이전 원목표인 matter/radiation 독립175점pilot과237unique z20→2history/plot은 완료되어 있다.
PR198625+606half-contraction과 B175/237full-Frobenius는 provenance가 다르다.
수치gate와완료IVP를 반복하지 마라. Norm변환은sqrt2이며 raw자동대체 근거가 아니다.

이 대화의 새 조사에서 PR199는eb8042b729051f4700bd5d88d6781c4620009bcb로 전진해 있었고,
D8 네 adjacent-sample zero brackets가 이미 다른 대화에서 완료된 것을 확인했다.
PR199D8,PR216consumer,원래B2raw4의SHA/indices/저장값이 모두 일치한다.
중앙DAG의 stale ready_not_run만 고쳤으며 D8는 재실행하지 않았다.

새로 완료한 노드D9_COMPONENT_SHEAR_BUDGET:
S_F=sqrt6*s/H, P_X=sqrt6*(8piG/c^2)*p_X/H²,
M=(a/a_i)^3*H/H_i, Q=M*S_F, I_X=integral(M*P_X dx).
정확한 identity Q=S_F,i+I_m+I_r를175nominal×153저장시점에 구현했다.
35referencealiases,5focus,새IVP/ODE/moment재계산=0.
max scaled residual1.473444875767401e-6<2e-5,
네D8 bracket endpoint의 max|R/Q|2.022140048467199e-5<0.1.
PHYS-MATH→PHYS-MATH-CODE→실제그림 검토는 PASS_SCOPED_D9.
이것은 저장samplequad의 일관성진단이며 보편superposition/연속root/수렴certificate가 아니다.

초기Sigma_F=.003,P_r=-.001의 다섯P_m={-.0003,-.0001,0,+.0001,+.0003}에서
I_r(z2)≈-.003305~-.003308. 마지막조건만 I_m≈+.00037222 덕분에 Q≈+.00006456,
S_F≈+3.36377715e-6로 남고 나머지네조건은 음수다.
P_m,i=0인 조건도 I_m(z2)=-3.614709098181205e-6을 갖는다.
초기matterstress0과 전구간matterstress0을 동일시하지 마라.

정확한 source/result publication,최종metadataHEAD,archive/providerID와readback은
research/rei_unified_sigma_pi_20261021/D9_COMPONENT_SHEAR_BUDGET/D9_DELIVERY_ACK.json
및 별도post-publicationACK를 읽어라. 포함하는Gitcommit과 실행sourceSHA를 구분하라.
최종analysisSHAac053652ee74a4e12741b9d201b21c9adef33d80ec802ee1d30cb468ebc24850.
compactNPZ SHA975a19b82f52294c73801e0d1340e4b46d050f398fccfd8098e6b41e50a45217.
코드·입력·그림·CSV·원래실패/수정기록이 Git 및새백업에 있다.

다음 단일 노드D10_ZERO_INITIAL_MATTER_STRESS_GENERATION:
exact LRS collisionless pressure-moment식을 유도하고 source에 매핑한 뒤,
기존 P_m,i=0인35조건의 저장history에서 shear에 의해 생성되는 matterquadrupole을 분석하라.
먼저 analytic/saved-data contract를 고정한다. 처음 허용newIVP=0; 기존pilot나D9재실행은 불필요하다.
현재대화의 D9종료는 D10실행완료를 뜻하지 않는다.

새로운실행근거:PR215NCPcompile+warm5cases/40gatesPASS,729reuse가 있으나
별도warm a=.1999→.2 model이며scientificadjudicationpending이다.
VigilODE새source5fd6e459.../resultsfbbc832f...는manufactured/stencil실행이며broadproductionHOLD다.
현재모형의solver를 자동교체하지 마라. Canonical24×12Gauss3과warm96×16reflectedkernel을구분하라.

이turn샌드박스Python/C++actualPASS;8CPU/8GiB. D9실행1process/1thread,
productionCPU9.233895646s,wall9.763839518s;speedupbenchmark아님.
현재D9NCPNOT_RUN,missingcase0. NCPwrapper는python3기본,compactinput포함,120s유한명령이다.
현재SSHkey/resources는실제로probe하되현재도유효한service do-not-retry는준수하라.
다른작업때문에중단하지말고가용resource를쓰되 unrelatedprocesskill/dirtyreset금지.

PR198scopedPASS,AGEHOLD/GrackleNOT_ESTABLISHED/productionNOT_ISSUED,
V12cap180/debit200.39897231891518/remaining100NOT_AUTHORIZED는보존한다.
단계별백업/게시/DAG상태를표시하고,실제새작업에한해유한검토·expectedheadFF·create-only이중백업을수행하라.
```
