# REI Patankar 분모 연구 — 중단 작업 종료 및 직접 반환

STATUS: PASS_CONDITIONAL_LOGDEN_SENSITIVITY_ORACLE
RETURN_TO: MAIN_CONVERSATION
WORK_THREAD_REQUIRED: false

## 1. 수령한 PR #74 검토

고정 parent는 `032b59372e55bdbb86860e8075206bd0026f7be1`, tree `7220d791d614d34e63097e3115c8036fcfcb8e94`다. PR #74 handoff, 단계 대응식, 실제 mprk22 source, ALGEBRA_RESULT.json과 원본 exact-stage-algebra.log를 읽었다. 보존된 Python population solve의 분모 y0,y0,yp 및 RHS 모두 y0, corrector flux (F0+F1)/2라는 mapping을 수용한다. 기존 10/10 결과는 과거 실행을 읽은 것이며 이번에 다시 실행하지 않았다.

현재 `src/rei_bianchi/source_bound_mprk_sdirk_operator.py`도 직접 읽었다. 실제 네 site를 재계산하는 native ABI가 없다는 typed failure를 보존한다. 이번 연구는 그 ABI를 구현하거나 우회하지 않는다. 실제 derivative bound, thermal coupled bound, exact-flow defect rho는 계속 UNKNOWN이다.

## 2. 중단 이전 별도 branch와 중복 범위의 명시

이번 계산의 CI source inventory에서 다음 기존 branch를 발견하고 그 commit diff와 증명을 읽었다.

- branch: `research/rei-denominator-transport-bound-20260907-r1`
- preserved publication: `3f4ccf438e387bb0734732ecf127acc594065658`
- earlier tested source: `269259aea35e62098a605d404f9ab25af593ce37`
- earlier tested tree: `052e52128353b21cb1d8cf6cf74739a4066916b2`
- proof: `research/rei_denominator_transport_bounds_20260907/PROOF_AND_BOUND.md`
- result: `research/rei_denominator_transport_bounds_20260907/CHATGPT_HANDOFF_KO.md`

이는 같은 #74 parent에서 시작된, 이미 게시된 이전 작업이다. denominator cancellation, finite relative-pair identity, frozen-flux predictor/corrector 연결은 겹친다. 이 공통 부분을 새 수학 성과로 두 번 세지 않는다. 그 branch의 파일·ref·실행 증거를 변경하거나 이번 branch와 억지로 merge하지 않았다. 그 12개 시험을 다시 실행하지 않았으며, 해당 12개와 이번 12개를 24개 독립 물리 의무라고 합산하지 않는다.

기존 branch는 추가로 선언된 합성 continuum box에서 Ep<=53/35 E0, Eg<=13/11 E0, Ec<=34759/18064 E0 및 predictor margin 16/105를 도출했다. 실제 trajectory/atomic input에서 얻은 상수가 아니라는 그 범위를 유지한다. 이 과거 box의 시험은 기존 게시 기록에 의존하며 여기서 재검산했다고 하지 않는다.

이번 branch의 추가 범위는 (a) 양수 로그 경로를 이용한 유한 변화 경계, (b) 절대 분모 미분이 발산하는 명시적 반례와 상대 미분의 구별, (c) flux/RHS 변화까지 유지한 전체 미분식 및 합성 state-dependent MPRK22 조합의 독립 dual 검산이다. 공통 식을 별도 코드로 확인한 부분은 corroboration으로만 센다. 이후에는 두 경로를 다시 병렬 개발하지 않고 이 handoff를 공통 결과 안내로 사용한다.

## 3. 이번에 실제로 실행한 소스와 결과

TESTED_SOURCE: `582e15bb15ec7e01b9b91378baac255334f36565`
TESTED_TREE: `378e5e47999da751a089701f7f1ee3ac438a79e1`
CHECKER_SHA256: `bdb425592d0f6ac8e3acbb924381fcd2654c41b21689f67a64e4ff0d437fcafc`

실행 위치: GitHub-hosted runner. 주 대화의 container/Python은 process 시작 전에 실패했고, local Codex나 WORK_THREAD를 호출하지 않았다.

실제 command:

```text
python3 -B research/rei_patankar_logden_sensitivity_20260907/verify_sensitivity.py --report <runner-temp>/rei-logden-evidence/RESULT.json
python3 -B scripts/verify_repo.py
```

- research run `34090521944`, job `101642866833`: 실제 full decoded log 판독.
- exact methods D01-D12: **12/12 PASS**, failures/errors/skips 0, unittest 표시 0.014 s.
- 같은 job의 repository verifier: 60 main artifacts PASS.
- git diff --check 및 최종 clean checkout 검사 PASS.
- 별도 repository run `34090521856`, job `101642866546`: completed/success.

보조 GnuPG/native/원자 rate/기존 #73/#74 suite는 실행하지 않았다. 의도된 mutation은 새 exact 검사 내부에서 식이 달라지는지 검증하며, 실제 production 결함의 RED라고 주장하지 않는다.

주요 machine result는 다음과 같다.

```json
{
  "status": "PASS_CONDITIONAL_LOGDEN_SENSITIVITY_ORACLE",
  "tests": 12,
  "failures": 0,
  "errors": 0,
  "skipped": 0,
  "arithmetic": "EXACT_FRACTION_AND_FORWARD_DUAL_SMALL_FIXTURES",
  "mprk22_corrector_tangent": ["601438287/7031540894", "-601438287/7031540894"],
  "production_imports": false,
  "actual_atomic_rates_evaluated": false,
  "rate_derivative_bounds": "UNKNOWN",
  "thermal_coupled_bound": "UNKNOWN",
  "exact_flow_defect_rho": "UNKNOWN",
  "first_interval_admitted": false,
  "authority_effect": "NONE"
}
```

이 JSON 발췌는 실제 decoded log에서 기록한 readback이며 원본 전체 RESULT.json과 byte-identical하다고 주장하지 않는다. 원본 결과/log/HEAD/TREE/manifest는 다음 artifact에 있다.

https://github.com/cosmosapjw-quantum/rei_bianchi/actions/runs/34090521944/artifacts/10006657584

GitHub upload 기록: 6 files, 3284 bytes.
서버 보고 ZIP SHA-256: `480afcc344b65c46eb03ed70ac9634a0045eb81e6916d0fb1b6dc630d8927684`.
이 대화의 로컬 컨테이너에서 다운로드·재해시한 값은 아니다. 핵심 결과는 이 일반 Git 텍스트로 직접 읽을 수 있으므로 수동 ZIP 왕복이 필요 없다.

## 4. 과학 결과의 정확한 범위

P=(I-h K(F) diag(d)^-1)^-1, v=Pb, d>0, b>=0, h>=0와 고정 양수 보존 가중치 w를 둔다. F의 단위는 count/s, d와 b는 population count, h는 proper seconds다.

고정 F,b,h에서 r=delta d/d이면

    delta_d v=(I-P)diag(v)r,
    ||delta_d v||_(1,w)<=2 sum_j w_j v_j(1-P_jj)|r_j|<=2M||r||_infinity.

이는 coefficient의 1/d^2를 따로 bound하기 전에 conservative solve의 상쇄를 사용한다. d/e와 log(e/d)는 무차원이다. 같은 F,b,h의 양수 denominator 쌍에는

    ||P_e b-P_d b||_(1,w)<=2M min(1,||log(e/d)||_infinity)

가 성립한다. 증명은 양수 경로 d(theta)=d exp(theta log(e/d))에서 미분 경계를 적분하고 같은 질량의 두 양수 상태 사이 2M 경계와 결합한다. 이 결과는 임의의 flux 변화나 전체 nonlinear flow를 제어하지 않는다.

전체 미분은

    delta v=P delta b+h P K(delta F)diag(d)^-1 v
            +(I-P)diag(v)(delta d/d)

이며, delta F 및 corrector의 delta yp/yp를 빼면 다른 연산이다. 새 checker는 독립 two-state closed form의 forward-dual 미분과 matrix-resolvent 미분을 비교했다. actual tableau의 합성 flux fixture이지 실제 원자반응률 평가가 아니다.

작은 분모 반례 두 개를 epsilon=1,10^-3,10^-6,10^-12,10^-18에서 정확 계산했다.

- One-way F10=1,F01=0,b=(1,1),d=(epsilon,1),h=1:
  relative response=2epsilon/(1+epsilon)^2. 기존 coarse bound 4/epsilon은 커지지만 실제 응답은 작아진다.
- Symmetric F10=F01=1,b=(1/2,1/2),d=(epsilon,epsilon),h=1:
  relative response=1/(epsilon+2), absolute response=1/[epsilon(epsilon+2)]. 상대 민감도 유계가 절대 미분의 경계 발산을 없애지는 않는다.

유한 Fraction fixture는 해석적 정리의 일반성을 증명하는 enumeration이 아니며, 부호·실제 단계 연결·경계 반례를 검산한 것이다. 실제 재이온화 불안정, 높은 차수 정확도, full-map contraction은 주장하지 않는다.

## 5. 검토와 다음 한 단계

같은 assistant의 순차 PHYS-MATH / PHYS-MATH-CODE 검토다. 고정 F와 full derivative, 엄격한 양수 denominator와 영 한계, 상대/절대 norm, 고정 h, source RHS, equal-weight edge 조건을 구별했다. I-P를 binary floating point에서 안정적으로 평가하는 production 구현도 아직 검증하지 않았다. 기존 physics/tolerance/source/authority는 그대로다.

SciSpace 탐색과 primary arXiv:2108.07347v5의 abstract는 작은 초기 성분 근처의 정확도·안정성 문제가 별도라는 방법론 맥락으로만 사용했다. 이 논문이 위 REI 항등식이나 current checkout을 검증했다고 인용하지 않는다.

NEXT: 실제 event-free positive state/forcing tube에서 아직 남은 flux-response 항을 bound한다. 기존 두 denominator 결과는 재사용하고, 같은 generic 증명을 다시 시작하지 않는다. 실제 atomic rate와 owner normalization의 모든 관련 의존성, branch/floor/active-set 경계, norm scaling을 명시해야 한다. 물리 입력 tube가 없으면 합성 box로 대체하지 말고 해당 입력만 UNKNOWN으로 남긴다.

주 대화에서 가능한 source 읽기·유도는 여기서 수행한다. 보존된 local input 또는 interval/CAS 실행만 필요할 때 이 디렉터리의 LOCAL_CODEX_HANDOFF_KO.md를 사용한다. Codex는 범위 내 연구 오류를 자율 수정·검증하고 Git-published handoff 링크로 직접 반환한다. 지금 자동 local 실행을 시작한 것은 아니다.

BASS/REC/HTT 접근, BG02 변경, XZ/GCC/native 재실행, 새 Snapshot GET, 설치/rootfs, production source/lock/Section-0/ref/lease/worker, first interval/provider, ready/merge/force-push는 수행하지 않았다. 증거 전용 이 handoff commit과 위 tested source는 구별한다. 최종 publication SHA/tree는 commit 생성 뒤 원격에서 읽어 보고하며 파일에 자기 SHA를 다시 삽입하지 않는다.
