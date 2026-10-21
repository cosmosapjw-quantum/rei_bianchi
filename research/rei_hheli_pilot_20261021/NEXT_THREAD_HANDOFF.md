# 다음 대화에 복사할 handoff prompt

$physmath-research-loop $exa $scispace $wolfram

cosmosapjw-quantum/rei_bianchi의 통합 연구를 이어가라. 새 H/He/Li sandbox pilot은 draft PR218, branch research/rei-hheli-sandbox-pilot-20261021, task research/rei_hheli_pilot_20261021/에 있다.

Scientific delivery S는 2fd46785ef2e7af8c25c01387c89e00b3edf9e9b, tree는 51ef238f3d3fc0a14c6018c4674ab6a636977158이다. 이후 metadata commit이 있으므로 최신 head, UNIFIED_STATUS.md, UNIFIED_DAG.json, PUBLICATION_RECEIPT.json과 terminal delivery capsule ACK를 실제로 읽고 시작하라. 과거 SHA를 현재 head라고 추정하지 마라.

이미 완료한 신규 계산은 79 nominal+3 controls=82 IVPs, 각각257samples, z20→2, 실패0이다. 실제 wall66.031348s/childCPU250.578735s였다. PNG/PDF10종, raw, CASE_PROVENANCE_LEDGER, 독립 PHYS-MATH/CODE/RAW/FIGURE 감사가 있다. 최종 판정은 PASS_SCOPED_PRELIMINARY_ATOMIC_TEST_FLUID다. 완료된82개나 PR198/B175/D9를 근거 없이 재실행하지 마라.

Git419변경 파일은 전체 byte/hash를 대조했고, 상속 경로까지494개 tree identity를 검증했다. P2 archive는23591727bytes/501members, SHA256 ea6eafef3e982a8983cf4cf46dcbb9924bd3d6dc43cdba0e087bdaacb6d05841이다. Drive ID1yVhYWgDxirGL533iFzrZzvN1AMnWZ6tY, Dropbox ID id:BSpOijBcT10AAAAAAD_hnw에서 각각 전체 GET/byte/SHA/member PASS였다. 분리한 디렉터리의 실제 CLI audit도 exit0/0신규IVP, raw/core 불변, PNG/CSV/summary 동일로 통과했다.

물리 core SHA256은30dd7fef781a51ddfc9ea763be55679f690caa5ddc3efff34c4bd771e7f5f77b, contract SHA256은dd3950150be8718d1bb60eed4f1ba3f4cd7447b377adc92476abf28ba8369dee다. HE32 donor는 BASS_HE e8bb035d31f59e34734947b9082bdbd60128b799다. 실제 실행은 샌드박스 file hash로 식별한다. 나중 publication commit을 실행 당시 commit으로 소급하지 마라.

Linux/Python3.12와 pilot/requirements.txt의 NumPy2.3.5/SciPy1.17.0/Matplotlib3.10.8 환경에서 다음은0신규IVP로 원자료를 확인하고 그림을 재생성한다:
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 -B research/rei_hheli_pilot_20261021/pilot/code/run_pilot.py --audit-existing
기존 raw의 재검증이 새 과학 계산으로 집계되지 않도록 하라. 결과 없는 ATTEMPT의 불명 CPU debit를 지우거나 덮어쓰지 마라.

선택 모형은21heavy-particle상태(n, H1/D/T q0..1, He3/He4 q0..2, Li6/Li7 q0..3)와 별도 electron charge closure다. 같은 원소의 동위원소에 같은 electronic rates를 쓴다. n/T는 초기0이고 생성 핵반응이 없다. UV5–60eV와 초기조건에서 LiIII/IV는 해석적으로0이며 수치 잔차를 clipping하지 않았다. Verner photo+totalRR, HeI a행을 사용한다. CI/DR/CX, 분자/음이온,19핵반응 및 닫힌 열·복사 에너지는 미구현·미확립이다. Atomic21상태 census를 “19핵반응 전체 완료”라고 부르지 마라.

Sigma와 Pi는 full Frobenius다. Signed tensor를 합친 후 norm을 취한다. PR198 half-contraction×sqrt(2)는 축 변환일 뿐 trajectory reuse 허가가 아니다. pi_m은 nonbaryonic massive10% 성분이며 원자 baryon은 isotropic pi_b=0이다. 계산된 ne가 photon Thomson 산란에 연결되고 neutrino는 collisionless다. 초기 totalPi가 상쇄된 실제 두 case에서 z2 signed shear −1.1093244e−4와+5.5461860e−5가 발생했다. 유한 모형 결과이며 보편적 중첩 정리는 아니다.

연구 전에 다른 branch/repo/접근 가능한 대화/Drive·Dropbox의 새 결과를 조사하고, 문서 주장과 실제 raw를 구분하라. 이전 조사는798refs/38sourceblobs였으며 Drive100개 cap이라는 한계가 있었다. Runtime은 실제 probe하고 다른 세션의 dirty checkout/process를 건드리지 마라. 가용 자원 안에서 작업하라.

다음 단일 과학 노드는 harder UV의 LiI inner-shell/Auger 및 RR/DR energy-moment에 관한 원본 source·유효범위·daughter·energy bookkeeping 계약 확정이다. 이를 통과하기 전에 새 전체 grid를 실행하지 마라. Nuclear19는 독립 lane으로 유지하라. PR198 scopedPASS, B175 완료, D9 closed, PR199 AGE convergence HOLD, Grackle bound NOT_ESTABLISHED, production NOT_ISSUED를 보존하라.

매 단계 DAG/게시/백업/다음 노드를 기록하라. Additive expected-head fast-forward만 허용하며 no force, no merge, draft 유지다. 실제 upload ACK와 full GET/byte/SHA/member 검증으로 백업을 닫아라. 기존 Rust cargo fmt CI 실패와 Python pilot PASS를 구분하라. 마지막에 복사 가능한 Codex 및 다음 대화 handoff를 갱신하라.
