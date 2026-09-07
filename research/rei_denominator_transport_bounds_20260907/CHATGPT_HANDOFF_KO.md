# REI population 분모 민감도 — 실행 완료 및 주 대화 직접 반환

WORK_UNIT: REI_POPULATION_DENOMINATOR_TRANSPORT_BOUND_V1
STATUS: PASS_DENOMINATOR_RESEARCH_CHECKS
RETURN_TO: MAIN_CONVERSATION
WORK_THREAD_REQUIRED: false

## 수령 결과와 이번 범위

PR #74의 고정 handoff, 실제 mprk22.py, STAGE_MAPPING.md, 원본 algebra log와 결과를 읽었다. 보존 Python 단계의 분모 y0,y0,yp 및 RHS 모두 y0라는 mapping을 한정된 source-level 결과로 수용한다. 기존 10개 검산을 재실행하거나 production Rust ABI가 구현됐다고 해석하지 않았다.

#74의 actual rate/thermal/rho UNKNOWN을 모두 닫은 것은 아니다. 이번에는 F0,F1과 h를 고정하고, 분모와 직접 RHS의 변화가 만들어내는 population 미분항 하나를 완결했다. 두 flux site는 독립된 고정 배열이며 서로 같다고 두지 않는다. 실제 물리 법칙에서 F0,F1도 상태에 따라 변한다는 사실은 유지한다.

## 새 수학 결과

F는 비음수 transfer count rate, B는 off-diagonal F와 음의 outgoing column sum, D(d)=diag(1/d), P=(I-hBD)^-1, x=P b로 정의한다. d,b>0, h>=0, 고정 원소별 보존 가중치와 exact-real 연산을 가정한다. 시간은 proper seconds, 상태는 원 source의 extensive counts, hBD는 무차원이다.

고정 B,h에서 다음은 정확한 항등식이다.

    x_g = P b_g + (I-P) diag(x) (d_g/d).

    ||I-P||_(1,w) = 2 max_j(1-P_jj)
                  <= 2 max_j h q_j/(d_j+h q_j) <= 2.

따라서 coefficient를 따로 미분할 때 보이는 1/d^2 항은 solve 안에서 상대 분모 변화 d_g/d로 정리된다. 절대 오차 경계에는 여전히 d>=m>0가 필요하다. 영 population에서 무조건 smooth하거나 고차 정확도가 보존된다는 뜻이 아니다.

같은 B,h인 두 유한 입력에도

    P_d b-P_e c = P_d(b-c)+(I-P_d)diag(d/e-1)P_e c

가 정확히 성립한다. 실제 예측자와 보정자에는

    dyp = Pp dy0+(I-Pp)diag(yp)(dy0/y0),
    dyc = Pc dy0+(I-Pc)diag(yc)(dyp/yp)

로 연결된다. 보정 RHS를 dyp로 바꾸거나 분모의 dyp 항을 삭제하면 다른 결과다.

완전한 증명, 단위, 시간/weight 가정, finite-pair 연결은 PROOF_AND_BOUND.md에 있다.

## 상수를 끝까지 계산한 영역과 한계

고정 원소별 기준수 NH*,NHe*와 시간 tau*로 무차원화한 별도의 대수적 영역이다. parent는 각 원소 합 1, H 각 성분>=1/4, He 각 성분>=1/6, 여섯 f0/f1 edge 각각 [0,1/16], h/tau* in [0,1/8]로 둔다. 이는 실제 REI 궤적이나 atomic/owner flux에서 추출한 enclosure가 아니다.

E=max(H-block l1,He-block l1)로 두고 두 parent의 원소별 총량이 같으면, 이 연속 영역 전체에서

    Ep <= (53/35) E0,
    Eg <= (13/11) E0,
    Ec <= (34759/18064) E0.

예측 분모 하한 mp=16/105도 incoming 항의 비음수성에서 유도했다. gamma=1-1/sqrt(2)<1/3을 해석적으로 사용했다. h/3 fixture를 실제 gamma 실행으로 세지 않는다. 이 값들은 upper bounds이며 실제 달성된 gain이나 비증폭 상한 1이 아니다.

연속 영역 전체의 근거는 증명이고, 유한 유리수 표본은 그 계산 구현의 검산이다. 실제 flux numerator의 delta_F0/delta_F1, node-owner 정규화 및 thermal feedback 항은 포함하지 않는다.

## 실제 새 실행

TESTED_SOURCE: 269259aea35e62098a605d404f9ab25af593ce37
TESTED_TREE: 052e52128353b21cb1d8cf6cf74739a4066916b2
PARENT: 032b59372e55bdbb86860e8075206bd0026f7be1
PARENT_TREE: 7220d791d614d34e63097e3115c8036fcfcb8e94
CHECKER_SHA256: 222cd6bb41addb7a730c6828b84d6997be9ff9aba6a3dc96e91a1ac22fc5b146

실행 장소는 GitHub-hosted runner다. 주 대화 container와 독립 Python probe는 process 시작 전 ClientError였다. 같은 막힌 경로를 재시도하지 않았다. Local Codex나 WORK_THREAD를 새로 시작하지 않았다.

연구 run 34086905315, job 101632574078의 decoded full log를 읽었다.

- 분모 미분을 고의로 누락한 mutant: D03 1개 실제 assertion FAIL, error/skip 0, exit 1, timeout false, process 0.11404762499999777 s. 첫 성분은 잘못된 96/965 대 독립값 599961/5959840. 이는 진짜 원 production bug나 implementation-absent RED가 아니라 명시된 negative hypothesis다.
- 올바른 동일 research source: D01-D12 12/12 PASS, failure/error/skip 0, exit 0, timeout false, process 0.26448884099999503 s, unittest 본문 0.153 s.
- repository verifier: 60 main artifacts PASS, exit 0, timeout false. 같은 job의 diff와 최종 clean checkout 검사도 통과했다.
- 별도 repository run 34086905235도 completed/success로 확인했다.

독립 dual-number/Cramer's-rule 2x2/3x3 미분과 기존 Fraction Gaussian inverse 경로를 비교했다. 실제 H/He graph, 선택 source byte links, finite differences, nested corrector, 틀린 RHS/분모 생략, rare denominator, 경계/영 flux/영 step을 포함한다. #73/#74의 기존 test suite, native, XZ/GCC consumer는 실행하지 않았다. 12개 고유 검사와 1개 별도 mutant 실행을 13개 독립 물리 의무라고 세지 않는다.

기계 판독 readback은 EXECUTION_READBACK.json이다. 이것은 실제 CI 로그를 읽어 새로 작성한 기록이며 raw artifact bytes와 동일하다고 주장하지 않는다.

원본 로그/결과/commands/source artifact:
https://github.com/cosmosapjw-quantum/rei_bianchi/actions/runs/34086905315/artifacts/10005507925

GitHub upload log: 13 files, 20303 bytes.
GitHub-reported ZIP SHA-256:
ad16eef899e848a9e8e5f135e28e30cc9d98f93798a6dc5d2a7977b732c6cb3d

이 대화에서 ZIP binary를 별도 다운로드해 다시 해시한 값은 아니다. ordinary Git handoff와 readback JSON만으로 핵심 결과를 읽을 수 있으며 ZIP 수작업 왕복은 필요 없다.

## 검토, 게시 및 종료 범위

순차 math review: 고정 B/h/weights, 허용된 equal-total 비교, 유한 pair 식의 부호, 전체 box에서 predictor 하한, actual gamma enclosure를 점검했다. Code review: 독립 미분 경로, 실제 exit/실패 종류/정확 ID, helper-only import, 기존 source 불변과 새로운 결과의 주장 범위를 점검했다. 같은 assistant의 두 관점 검토이며 외부 독립 reviewer 승인이 아니다. 새 source 수정이나 재시도는 필요하지 않았다.

SciSpace 탐색과 primary-source 확인은 Patankar 양수성/안정성/영 초기성분 근처 정확도 구분의 문헌 맥락이다. Torlo–Offner–Ranocha, arXiv:2108.07347v5 (2022 journal DOI 10.1016/j.apnum.2022.07.014). 이번 source-specific 식과 box bound는 여기의 직접 유도이며 그 논문이 REI를 검증했다고 인용하지 않는다.

이 파일과 EXECUTION_READBACK.json만 추가하는 evidence commit은 위 TESTED_SOURCE와 다르다. self SHA를 반복 삽입하지 않는다. publication head/tree와 Draft PR/최종 repository check는 외부 readback으로 확인한다. evidence-only 변경은 새 denominator 계산을 자동 반복하지 않도록 workflow path filter를 설정했다. 기존 production/SSOT/허용오차/원자반응률은 변경하지 않았다.

UNKNOWN: 실제 trajectory-relevant flux envelope 및 flux numerator derivative, thermal coupled inverse bound, exact-flow rho. PRODUCTION: 실제 four-site Rust ABI 미구현이라는 #74 판정 불변. first interval/provider/runtime authority 승격 없음.

NEXT: 하나의 실제 event-free state/forcing tube에서 이번에 고정해 둔 flux numerator의 미분 경계를 source와 연결한다. 예를 들어 r_hi=phi_HI+N_HI*n_e*beta_HI(T)에서 시작할 때 phi_HI의 owner 정규화 및 전역 node 의존성을 생략하지 않는다. 물리 입력 tube가 확보되지 않으면 명시적으로 그 입력만 미확정으로 남기고 대수적 box를 대신 사용하지 않는다. 분모 결과는 재사용하고 다시 검산 루프를 만들지 않는다. 필요한 source 읽기/유도는 main에서 먼저 수행하며 실제 local-only 접근이 확인될 때만 Codex에 인계한다.

BASS/REC/HTT 접근, Snapshot GET, XZ/GCC/native replay, 설치/downgrade/rootfs/census, production lock/worker/Section-0/ref/lease, first interval/provider, ready/merge/force-push는 수행하지 않았다.
