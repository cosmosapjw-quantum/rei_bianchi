# HE29 VigilODE 확장: 독립 C6 callback·Python FFI 검토

## 판정

**수정 후 고유 96개 테스트 메서드 PASS**: callback 71개, Python FFI·identity·canary admission 25개. 기존 HE28/HE29 연구 결과와 원래 source-only suite는 실행하지 않았다. 이 검토에서 실제 shared library 로드, Rust solver 실행, Grackle 호출, HE29 table 생성은 모두 0회다. Rust 컴파일·실제 작은 FFI smoke는 별도의 검토 담당자가 수행하므로 여기의 테스트 수에 포함하지 않는다.

검토자는 새 테스트 두 파일과 이 검토 문서만 작성했다. 검토 대상인 root 작성 source 세 파일은 수정하지 않았다. 물리식·반응률·허용치·baseline 4개 쌍·기존 transport 6개는 이 검토의 수정 대상이 아니다.

## 실제 발견과 수정 확인

최초 의미 있는 callback 실행에서 고유 70개 중 **물리 상태 overflow 관련 2개가 실패**했다. 유한한 z와 양의 유한 scale이어도 z*scale이 Inf가 될 수 있는데, 모델이 이를 내부에서 무시하고 유한한 상수를 반환하면 adapter가 RHS/Jac 호출 전에 잘못된 물리 상태를 거부하지 못했다. root에 재현 조건과 수정 위치를 전달했다.

root는 RHS·JVP에서 z*scale을 모델 호출 전에 검사하고, JVP 방향 scale*v도 유한한지 확인하도록 수정했다. 이를 확인하는 기존 70개와 새 방향 overflow 검증 1개가 모두 통과했다. 초기 unittest 생성기에는 TestCase 별칭이 남아 같은 70개를 두 번 발견하는 문제가 있었다. 첫 로그의 140 tests / 4 failures는 **70개를 두 번 실행한 것으로, 고유 실패는 2개**다. 생성기 별칭을 제거한 뒤 최종 71개를 실행했다. 반복 실행은 새 테스트 수에 더하지 않는다.

최초 pytest 호출은 설치 부재로 실행되지 않았으며, 이후 stdlib unittest로 전환했다. 중간 ENOSPC는 실행 환경 문제로서 의미 있는 테스트 수는 0이며, root가 자신의 임시 데이터를 정리한 뒤 동일 검토를 이어갔다. 최초 실패 로그를 보존한 상태에서 수정본을 재검증했다.

FFI 검증은 root의 non-object JSON 처리 수정 이후 첫 실행에서 25개가 모두 통과했다. valid JSON인 [], null, true, 정수, 문자열도 성공으로 인정되지 않고 VigilODEFailure 증거에 보존된다.

## 검증 범위

| 대상 | 검증한 계약 | 결과 |
|---|---|---|
| 좌표 변환 | RHS의 dt/S, JVP의 dt/S·J·S·v, 고정 scaled state의 시간 편미분 dt²/S | PASS |
| 시간 차분 | 양 끝점, 비단위 구간, 2^60의 큰 proper time에서 1/2/3/8 ULP 폭, 표현 가능한 경계 내부 표본 | PASS |
| Jacobian cache | 시간과 상태 bytes의 정확 일치, 상태 1 ULP 변경·시간 변경 시 무효화, dense/sparse 반환 행렬의 복사 | PASS |
| 입력·출력 | 차원, 비유한 값, interval·scale·breakpoint 계약, 상태 및 JVP 방향 overflow | PASS |
| build identity | 고정 revision·ABI·library bytes·정확한 4개 bridge source 경로와 해시 | PASS |
| 로드 순서 | identity 실패 시 CDLL 미호출, ABI 실패 시 solve binding 미진행 | PASS |
| ctypes 경계 | RHS/JVP/time callback의 실제 ctypes 객체 및 배열, null/arity, 첫 Python 예외 보존 | PASS |
| solver 반환 admission | return code, ABI/status/dimension/final_u/output_samples, pin/tolerances/dense flag, 비유한 endpoint | PASS |
| 시간 구간 연결 | 원래 cutoff 경계, scaled state 전달, 실패 시 마지막 완료 physical state와 관측 partial scaled state 보존 | PASS |
| baseline 선행조건 | 4/4 완료 판정, 동일 source/binary/input/thread/runtime, 조건 실패 시 bridge 검증 미진행 | PASS |
| canary admission | 새 table hash 불일치 시 solve 미진행, admission 실패 전에 RAW 결과 보존, 저장 Radau+DOP853 모두 비교 | PASS |
| 범위 표기 | canary 완료가 새 baseline pair를 생성하지 않음, source-only/transport replay 0, 주요 HOLD 유지 | PASS |

Python FFI 테스트의 native 대역은 Python callable이다. 실제 ctypes callback 포인터와 C-layout 구조체·buffer는 사용하지만 컴파일된 solver·ABI 구현의 건전성이나 native integration 정확도를 증명하지 않는다. synthetic canary 성공은 테스트 fixture 내부 결과이며 실제 HE29 4/4 기준해 완료나 새 native 반환으로 집계하면 안 된다.

## 재현 명령과 증거

작업 디렉터리: /workspace/scratch/bafb5630fc40/bass_work

```bash
python3 -m unittest discover -s research/he29_survival_budget_20261018/vigilode_20261019/tests -p test_callbacks.py -q
python3 -m unittest discover -s research/he29_survival_budget_20261018/vigilode_20261019/tests -p test_reference_contract.py -v
```

각각 exit 0이며 unittest 측정 시간은 0.012초와 0.085초다. Python 3.12.14, NumPy 2.3.5, SciPy 1.17.0을 사용했다.

- CALLBACKS_FIRST_RUN.txt: pytest 설치 부재; 실행 테스트 0.
- CALLBACKS_SEMANTIC_FIRST_RUN.txt: 수정 전 실제 실패, 고유 70개/실패 2개; 발견 중복이 포함된 원문 보존.
- CALLBACKS_FINAL_RUN.txt: 수정 후 고유 71개 PASS.
- FFI_CONTRACT_FIRST_RUN.txt: 새 FFI 검증 25개 PASS.
- CALLBACK_AND_FFI_REVIEW_RECEIPT.json: 대상 source·test·로그 SHA256, 실행 명령·결과·범위.

## DAG·게시·백업 상태

이 담당자 범위의 **C6 검증은 PASS_SCOPED**다. 테스트와 증거는 공유 작업 디렉터리에 저장되어 root가 게시·백업 묶음에 포함할 수 있다. 이 담당자는 Git push, 외부 업로드, NCP 제출을 수행하지 않았으며 해당 상태를 완료로 표시하지 않는다. R2/C3의 Rust 패키지 조사와 synthetic Schur 대수 검증은 별도 기존 산출물을 재사용한다. 새로운 solver 연구·전체 격자 확대·기존 과학 계산 재실행은 없다.

## skill_context_used

- physmath-research-loop 1.3.0: SKILL.md와 POLICY_INTEGRATION.md를 이전 동일 작업에서 실제로 읽었다.
- THEORY_LOOP.md R2, CODING_LOOP.md C3/C6의 선택적 작업 범위를 적용했다.
- 기존 상태·증거 재사용, 고정 물리 계약, 최초 실패 보존, 독립적인 새 코드 검증, 범위를 넘는 과학적 해석의 HOLD를 적용했다.
- 이 C6는 parent가 작성한 callback/FFI 코드를 검토한다. 본인이 작성한 Schur 검증 코드의 독립 심사로 주장하지 않는다. 재귀 subagent·재심사 루프는 생성하지 않았다.
