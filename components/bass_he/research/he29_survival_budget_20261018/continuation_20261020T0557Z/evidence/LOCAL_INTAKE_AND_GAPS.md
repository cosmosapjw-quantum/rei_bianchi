# HE29 local intake와 남은 분석 연결 — 2026-10-20 05:57Z continuation

## 판정

현재 local Git HEAD는 `1765522318438e966e61d8a72f12084550da399d`다. ABI2 실행 code pin은 `a5d4711460c09b310b78c9692aa62534b7a843d3`, 원래 과학 source·tests는 `1569f3718cd4b17a16936ad3d72bc7d5ed9b0f4f`다. 현재 workspace의 반환 후보와 최근 보존 영수증을 읽은 범위에서 **새 HE29 기준해 0/4, 새 packed canary 0건, 새 HE29 부분 method/native-stream 반환 0건**이다. 다른 오래된 HE27 stream과 합성 최적화 결과는 새 HE29 반환에 포함하지 않았다. 원격 NCP 프로세스는 여전히 미관측이다. 반환 파일의 부재로 미보고 실행의 부재를 단정하지 않는다. [E1–E4]

이 intake는 코드 읽기와 기존 결과·영수증 읽기만 수행했다. 원래 분석기, solver, HE28 transport, HE29 source-only suite, Rust build, 기존 최적화 benchmark는 실행하지 않았다. 파일 변경은 이 보고서와 동명의 JSON, 원본 audit의 byte 복원본과 그 provenance뿐이다.

## 완료 근거의 재사용

| 항목 | 실제 읽은 현재 근거 | 해석 |
|---|---|---|
| 코드 게시 | a5d commit, 82/82 readback | 실행 code pin |
| 문서 게시 | 1765522 commit, 39/39 readback | 코드와 별개인 후속 문서 HEAD |
| 완전 보존 | `77f1c73e…`, 4,719,121 bytes, 양쪽 raw + 91개 payload PASS | 이전 완료 검증 재사용 |
| 후속 closeout | `3380c7c4…`, 1,714,101 bytes, 양쪽 raw + 47개 payload 및 nested checkpoint 21개 PASS | 최신 actual closeout 영수증 재사용 |
| 게시 builder | 146.65029773499919 s compile PASS | native 실행이 아니며 다시 build하지 않음 |
| 합성 성능 결과 | `optimization_runs/assembly_first/RESULT.json`, `optimization_runs/ffi_final/RESULT.json` | native owner 호출 0, 실제 HE29 속도 개선량 미측정 |

Standalone checkpoint Drive 응답은 미확인, Dropbox standalone upload는 미시행이라는 이력과 **같은 checkpoint 원본이 후속 양쪽 closeout archive 안에서 실제 검증됐다는 최신 상태**를 구분한다. 이전의 미확인 상태로 되돌리지 않는다. measured library `8299915d…`와 published compile-only library `80219060…`도 구분한다. [E2–E5]

## 이미 구현돼 있어 다시 수행하지 않을 분석

`src/analyze_return.py:23–46`은 기존 여섯 HE28 결과의 n32→64 시간차, strip 혼합차, 부호 변화를 이미 계산한다. 일반 파일로 풀린 audit JSON은 현재 없었지만 원래 `a70` archive 안에서 다음 저장 결과를 읽었다. [S1]

- Member: `BASS_HE_HE29_RESUME_COMPLETE_20261018/research/he29_survival_budget_20261018/results/NATIVE_RETURN_AUDIT.json`
- 크기: 1,934 bytes
- SHA256: `2bcd94edde08854599597ea8b962683a86cb5ca4af1ad0e1c3bec09b9e3c20cc`
- `results/recovery/NATIVE_RETURN_RECHECK.json`도 같은 바이트다.
- 이 새 lane의 `evidence/reused/NATIVE_RETURN_AUDIT.json`에 원본 bytes를 그대로 복원했다. archive/member/검증 범위는 `evidence/reused/PROVENANCE.json`에 기록했다.
- 저장된 r2→4 혼합차는 `−9.199059292086531e-10 K`, r4→8 혼합차는 `+3.729461184320826e-11 K`다. 이 값은 새 계산이나 새 연구 성과가 아니다.

원래 `src/analyze_references.py:8–43`도 완료된 case의 부분 집계, 네 job 확인, 원래 admission, 동일 identity 집단 확인, Radau 기준의 세 strip/table 대비를 이미 구현한다. 이를 새로 개발할 필요는 없다. [S2]

## 남은 첫 번째 연결: 공유 기준해에 조건부인 signed decomposition

현재 `reference_runner.parent_comparisons`는 table512에서 `|T_transport−θ_Radau|`만 저장한다. analyzer는 그 절대 차이를 전달하고 strip/table Radau 차이에 두 method spread의 합을 덧붙인다. 같은 기준해 후보를 여러 식에서 공유하는 부호 있는 분해와 finite-candidate hull은 없다. [S2–S4]

새 lane의 읽기 전용 확장은 case identity로 묶은 같은 `θ_(r,M)`를 공유 변수로 두고 다음을 표현하면 된다.

$$b_{r,n}=T_{r,n}-\theta_{r,512},$$

$$T_{b,n}-T_{a,n}=(\theta_{b,512}-\theta_{a,512})+(b_{b,n}-b_{a,n}).$$

각 θ의 후보는 그 case에 실제 저장된 Radau/DOP853 두 값이다. `L=C+Σ c_i θ_i`의 hull을 계산하기 **전에 동일 θ의 계수를 합친다**. 그 다음 남은 각 `c_i θ_i`가 취할 두 값의 최솟값·최댓값으로 지정된 유한 후보 조합 전체의 hull을 구한다. 같은 θ가 상쇄되는 식에서 존재하지 않는 method 불확실성이 다시 생겨서는 안 된다. n32/n64 혼합차는 이 상쇄가 이미 확인된 오래된 audit 값으로 재사용한다.

이 hull은 두 solver의 유한 출력 후보 집합에 대한 범위다. 정확한 finite-model 해의 오차상한, 확률 신뢰구간, 기체온도 전체 오차상한, 연속 스펙트럼 적분 오차가 아니다. table1024는 r4에만 있으므로 현재 네 job은 table 효과 한 개와 table512에서 strip 효과 두 개를 제공한다. strip×table interaction이나 연속극한 추정은 현재 설계로 식별하지 않는다.

기준해가 0/4인 지금은 reference-dependent row를 빈 목록/HOLD로 유지한다. 제조계 fixture는 새로운 대수와 분류만 검증할 수 있고 물리 기준해를 대체하지 않는다.

## 남은 두 번째 연결: RESULT 이전의 부분 반환 분류

원래 analyzer는 `RESULT.json`, `IDENTITY.json`, `TABLE.json` 중 하나라도 없으면 같은 missing 상태로 처리한다. `Radau.json`만 저장된 경우는 분석하지 않으며, 존재하는 잘못된 한 case는 최종 aggregate JSON을 쓰기 전에 예외를 일으킨다. 원래 runner는 method 결과를 admission 후 저장하므로 실패한 method의 최종 상태가 항상 남는 것도 아니다. [S2, S4]

새 분류기는 실제 있는 파일의 hash와 `COMMAND/RECEIPT/SUMMARY/FAILURE`, point qualification, individual method record를 보존하며 `NOT_OBSERVED`, 준비됨, 한 method 저장, pair 있으나 final receipt 없음, admitted, identity/admission 거절, 실패/timeout을 구분할 수 있다. 한 method 또는 final completion receipt가 없는 pair를 완료 기준해로 승격하지 않는다. 오류 후보는 별도 항목으로 남기고 신원이 맞는 admitted subset에 가능한 대비만 분석한다. 이것은 원래 four-job admission을 변경하는 작업이 아니다.

원래 campaign은 first failure에서 중단하고 resume-aware하지 않다. 새 실행이 허용될 때는 남은 case만 선택하되 `run_process`의 process-group timeout을 유지해야 한다. direct `case` 호출의 `--case-wall-s`는 자체 timeout을 강제하지 않는다. 이번 intake는 새 controller를 만들거나 어떤 job도 시작하지 않았다. [S4, S7]

| 실제 반환 | 가능한 새 분석 |
|---|---|
| 0 admitted pair | local/remote 반환 inventory와 저장 audit 재사용; 참조 의존 계산 HOLD |
| 한 method | 원래 gate 결과·실패·시간 기록을 partial로 표시 |
| table512 한 admitted pair | 동일 r의 n32/n64 signed bias 및 두 method 후보 |
| 인접 strip 두 admitted pair | 해당 strip 대비의 shared-reference 분해와 후보 hull |
| r4의 table512/1024 두 pair | 같은 r의 table 대비; 새 table1024 transport 시간오차는 없음 |
| 네 pair 전부 admitted | 세 대비 완성 및 기존 one-thread packed canary preflight 가능 |

## 동일성 및 성능 기록의 연결

원래 analyzer는 완료 case 사이의 binary/source/parent/input/thread map을 비교한다. 이 map 자체를 protected Git source, actual binary/build receipt와 독립적으로 연결하고, 반환된 모든 reference runtime을 비교하는 절차는 분석 출력에 직접 들어 있지 않다. 반면 기존 packed runner의 preflight에는 원래 source gate와 모든 네 pair의 Python/NumPy/SciPy 일치 확인이 이미 있다. 새 반환 loader는 이 계약을 재사용하면서 raw case·method·qualification·process 파일 hash를 명시해야 한다. 반환 runtime끼리의 비교와 분석 host의 runtime 비교는 구분한다. [S2, S4–S6]

성능 정보도 일부는 이미 존재한다. Radau/DOP853 method JSON은 각 적분의 시간과 native call delta를 기록한다. TABLE은 `diagnostics.build_wall_s`를 기록한다. packed segment에는 attempts, linear iterations, native JVP, prepare/cache, Python callback count가 있다. 현재 packed 결과의 `wall_s`는 preflight·model/table·적분·출력을 포함하는 case 총시간이며 solve-only/segment wall timer는 없다. native stream의 `monotonic_ns`는 response 뒤에 기록되어 다음 점 사이의 solver·기록 작업까지 섞인다. [S4–S9]

따라서 baseline method 적분 시간과 packed 총시간을 나눠 native 최적화 배율을 만들면 안 된다. 두 method가 포함된 baseline case 시간과 한 canary 시간의 비도 같은 해석을 허용하지 않는다. 실제 결과가 돌아오면 측정 범위를 별도 열로 유지하고 없는 항목은 `NOT_MEASURED`로 표시한다. 서로 다른 적분기의 비용 비교와 native legacy/packed JVP의 통제된 비교도 구분한다. 기존 합성 배율은 그대로 재사용하고 단계별 배율을 곱하지 않는다. table allocation 추정과 packed workspace 크기는 whole-process RSS 측정값이 아니다.

## 다음 handoff에 보존할 정체성

1. Repository/PR78/branch, 실제 문서 HEAD `1765522…`, 실행 a5d, science1569를 분리한다.
2. HE28 parent `a41dd371…`, 원본 owner `f7830e2f…`, VigilODE `a21d5739…`, Rust/Cargo 및 ABI2 정체성을 남긴다.
3. 두1569 overlay SHA `cd0b7ab4…`와 `71f16bc8…`, repaired INPUT manifest `28917c4c…`, PARENT manifest `7c3262d5…`, 원래 a70 input archive를 보존한다. archive 코드는 실행하지 않고 DATA만 사용한다.
4. 실제 NCP binary/build receipt와 six-point qualification, 각 table/source/input map, Python/NumPy/SciPy 및 single-thread 환경, scaled tolerances와 불변 gate를 보존한다.
5. raw method/case/identity/table/qualification/process 파일 및 native partial stream의 hash와 첫 실패를 남긴다. 오래된 saved binary `c4bf20bb…`와 실제 새 build의 byte identity를 혼동하지 않는다.
6. measured829와 compile-only802 library를 분리하고, complete77 및 closeout338 archive의 actual dual readback 상태와 provider ID를 보존한다. 전체 SHA와 ID는 동명의 JSON에 있다.
7. 기준해 0/4, canary NOT_RUN, NCP 프로세스 미관측·quota no retry, 기존 transport/source/optimization 반복0을 명시한다. 연속 스펙트럼·전체 EoR·기체온도 전체 오차상한·upstream Grackle 전체 동등성·관측 Bianchi/CMB HOLD를 유지한다.

## 실제 읽은 근거

- **E1:** `DAG_STATUS.json`, `NEW_CHAT_HANDOFF_KO.md`, `CODEX_HANDOFF_PROMPT_KO.md`, `optimization_20261020/{DAG_STATUS,DELIVERY}.json`.
- **E2:** workspace `closeout_backup_20261020/FINAL_CLOSEOUT_RECEIPT.json` 및 `PR78_FINAL_READBACK.json`.
- **E3:** workspace `complete_backup_20261020/LOCAL_ARCHIVE.json`, `closeout_backup_20261020/LOCAL_ARCHIVE.json`.
- **E4:** workspace JSON 완료 status 및 method/native/partial filename census; 새 HE29 일치0.
- **E5:** workspace `optimization_runs/{assembly_first,ffi_final}/RESULT.json`; 기존 합성 결과만 읽음.
- **S1:** `src/analyze_return.py:23–46` 및 a70 내 원본 `NATIVE_RETURN_AUDIT.json`.
- **S2:** `src/analyze_references.py:8–43`.
- **S3:** `src/reference_contract.py:6–38`.
- **S4:** `src/reference_runner.py:42–164`.
- **S5:** `optimization_20261020/src/run_packed.py:43–58, 61–155, 194–208`.
- **S6:** `vigilode_20261019/src/run_vigilode.py:28–47`, `optimization_20261020/src/packed_reference.py:37–53, 169–212`.
- **S7:** `research/he28_strip_refinement_20261018/src/execution.py:62–90`.
- **S8:** `research/he28_strip_refinement_20261018/src/refined_source.py:164–201`.
- **S9:** `research/he25_proper_birth_20261016/src/{reference.py:17–118,native.py:67–74,169–191,213–259}`.

모든 읽은 source/receipt의 SHA256은 동명의 JSON `source_evidence`와 `read_receipt_identities`에 기록했다. 원본 과학 파일 수정0, 새로운 코드 구현0, solver/native/test/build 실행0이다.
