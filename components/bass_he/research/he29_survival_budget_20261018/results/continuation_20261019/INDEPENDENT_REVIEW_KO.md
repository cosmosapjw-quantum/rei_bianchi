# HE29 실행 경계 독립 검토

## 범위와 근거

2026-10-19. publication HEAD `3f16fe525d726aaebbe9262e0e869540321209eb`에서 root가 취득한 README, DAG, 두 handoff, DELIVERY, CLOSEOUT_RECEIPT 및 AGENTS를 읽었다. 아래 코드는 GitHub에서 execution revision `1569f3718cd4b17a16936ad3d72bc7d5ed9b0f4f`를 지정하여 직접 읽었다. 기존 과학 계산·50개 테스트·native 실행·원격 접속·cloud/GitHub 쓰기는 수행하지 않았다. 최신 반환 유무는 root의 별도 census 결과를 따른다.

- HE29 `ncp/START_REFERENCES.sh`, `ncp/BOOTSTRAP_REFERENCES.sh`, `src/reference_contract.py`, `src/reference_runner.py`, `src/analyze_references.py`, provenance의 부모/입력 manifest, requirements.
- HE28 `src/execution.py`, `src/refined_source.py`; HE25 `src/reference.py`, `src/native.py`.
- `reference.py`의 실제 import owner는 HE25이다. HE28 아래 파일 lookup 404를 실행 의존성 손실로 해석하지 않았다.

## 현재 요청에 직접 영향을 주는 실행 경계

1. **기존 테스트의 무조건 재실행.** 원본 BOOTSTRAP은 `(cd "$HERE"; PYTHONPATH=src "$PY" -m pytest -q tests) > "$WORK/logs/TESTS.log" 2>&1`를 무조건 수행한다. START에는 이를 건너뛰는 옵션이 없다. 현재 사용자의 HE29 source-only 검증 반복 금지와 충돌한다. 1569의 과학/테스트 파일을 그대로 두고 별도 identity를 가진 최소 adapter에서 원본 bootstrap의 정확한 바이트를 검증한 뒤 이 한 줄만 기존 50/50 근거 재사용 receipt로 대체하는 것이 최소 조정이다. 재사용을 새 test PASS로 쓰지 않는다. 컴파일, preflight, six-point qualification, native campaign, 실패 보존은 유지한다. 복사한 bootstrap의 HERE는 원래 pinned HE29 root를 가리켜야 한다.
2. **부분 결과는 자동 분석되지 않을 수 있다.** 첫 실패로 campaign이 exit 1이면 bootstrap의 `set -e` 때문에 `analyze_references.py` 호출이 생략된다. 이 경우 저장된 성공 case는 별도 analyzer 호출로 즉시 분석할 수 있다. analyzer는 incomplete JSON을 먼저 쓴 뒤 exit 1을 내므로 이 종료 코드는 분석 실패와 구분한다.
3. **case 직접 호출에는 전체 시간 제한이 걸리지 않는다.** 실제 3600s process-group timeout은 `campaign -> run_process`가 집행한다. `case --case-wall-s 3600`은 인자를 검사하지만 case 내부 시간을 제한하지 않는다. 새 반환이 0/4이면 고정 campaign을 사용한다. 일부가 이미 완료됐으면 campaign을 다시 시작해 성공 case를 반복하지 말고, 남은 case에 기존 `run_process`의 동일한 timeout/receipt를 적용해야 한다.
4. **반환 상태 해석.** build/RECEIPT.json의 `native_run:false`는 빌드 시점 필드이며 실제 campaign 이후에도 그대로다. 실행 여부·호출 수는 case RESULT, method 파일, process receipt 및 native JSONL로 판정한다. 각 case가 저장된 6점을 새 binary로 qualification하므로 '6점'은 campaign 전체 합계라는 뜻이 아니다.

원본 bootstrap 사본: `handoff_review/BOOTSTRAP_REFERENCES.pinned.sh`; 3955 bytes, SHA256 `649b0122f6d72229568454f910c97343d8d7a6f7d8c9a13b4ae48beafbabd0df`, Git blob SHA1 `ed227e2937f554bd5ecda4bf24dd5597b73a77a4`. 직접 재계산하여 GitHub 반환 blob과 일치했다. 이 확인은 취득한 실행 경계 파일의 identity 확인이다.

### 구체 overlay 검토

root가 작성한 `delivery/research/he29_survival_budget_20261018/ncp/REUSE_SOURCE_VALIDATION_20261019.patch`를 독립적으로 읽었다. 제공된 patch SHA256은 `cd0b7ab40688b3c60ab689876690b2edd71aea5268b4e7ff285a637ca094a33e`이다. diff는 inherited pytest 한 줄만 제거하고 REUSED_SOURCE_VALIDATION/실행 tests=0, 실행 revision, 기존 evidence revision/경로, 실제 patched bootstrap SHA, Git overlay diff와 HEAD를 기록한다. compiler, six-point native qualification, campaign, archive trap은 바뀌지 않았다.

권장 고정 절차는 새 checkout의 clean 상태, HEAD1569 및 원본 bootstrap blob을 먼저 확인하고, 별도 publication에서 취득한 patch SHA를 확인한 다음 apply-check/apply하는 것이다. 이는 Git의 원본 과학·테스트 revision을 유지하면서 checkout의 실행 경계 overlay를 명시하는 방식이다. 기존 파일 위치를 유지하므로 HERE/RESEARCH 경로 계산도 유지된다. 문맥상 필요한 변경이며 구체 diff에서 material blocker를 찾지 못했다. 실제 apply·drift 거절·Bash syntax 검사는 root 담당이며, 이 검토는 해당 실행 성공을 주장하지 않는다.

## 정확한 작업과 admission

고정 m=8, angles=4, q=0. 각 줄에서 Radau 다음 DOP853을 수행한다. case는 한 번에 하나이며 첫 실패에서 종료한다.

| 순서 | strips | table nodes | 상대 출력 경로 |
|---|---:|---:|---|
| 1 | 2 | 512 | references/m8_r2_table512 |
| 2 | 4 | 512 | references/m8_r4_table512 |
| 3 | 8 | 512 | references/m8_r8_table512 |
| 4 | 4 | 1024 | references/m8_r4_table1024 |

기존 BOOTSTRAP의 실제 campaign 명령은 다음과 같다. adapter가 이 부분을 유지하면 된다.

```sh
"$PY" "$HERE/src/reference_runner.py" campaign \
  --binary "$WORK/build/he29_owner_server" \
  --receipt "$WORK/build/RECEIPT.json" \
  --out "$WORK/references" --case-wall-s 3600
```

`WORK`는 새 경로여야 한다. 원본 Rust owner는 `rei_bianchi@f7830e2f55e7a1938bc3c98f61b60651f8dae474`; HE25 owner_server와 함께 edition2021, opt-level2로 컴파일한다. fast-math는 사용하지 않는다. numpy=2.3.5, scipy=1.17.0 요구 파일이 있으며 실제 runtime과 pip freeze를 기록한다. 수치 스레드는 OPENBLAS/OMP/MKL/NUMEXPR/BLIS 각각 1, OMP_DYNAMIC=FALSE, OMP_PLACES=cores, OMP_PROC_BIND=close이다.

| 대상 | 실제 구현된 조건 |
|---|---|
| 원본 입력 | archive 전체 SHA256 및 22개 DATA manifest, 불일치 overwrite 금지 |
| source/build | 부모 20개 파일 SHA256, 입력 22개 SHA256, owner commit, binary SHA256, server source SHA256 검증 |
| native 저장점 | 6점, nonzero 상대 오차 <=5e-13, 원본 zero는 정확히 zero; binary byte equality는 기록이지 전체 동등성 gate가 아님 |
| table512 | 각 r에 대응하는 저장 HE28 table SHA와 정확히 일치해야 적분 진행 |
| table1024 | 별도 유한 모델의 table sensitivity; table512 transport error로 혼용하지 않음 |
| table 자원 | 예상 table allocation <=2 GiB, table 생성 loop 시간 600s; 전체 RSS의 강제 2 GiB 제한은 아님 |
| case 자원 | table 생성과 두 적분기를 합친 case 전체 3600s; process group SIGTERM 뒤 최대 3s 종료 유예 |
| ODE | rtol=1e-10, atol=1e-12는 z=y/scale의 scaled absolute tolerance; proper-time integration |
| 각 solver 결과 | 모든 검사 값 finite; photon number defect <=3e-15/H; energy defect <=3e-12 eV/H; 최대 species defect <=3e-12; min photon >=0; gas_positive true; T>0 |
| solver pair | 온도차 <=1e-9 K, 첫 세 gas fraction 절대차 <=1e-11; empirical stability, certified radius 아님 |

parent transport와 reference의 fraction/temperature 차이는 오류분리 측정값으로 저장된다. `admit_pair`의 <=1e-11 gate와 reference-to-transport 차이를 같은 gate로 오독하지 않는다.

## 반환할 실제 증거

`WORK.tar.gz`와 `.sha256`는 bootstrap EXIT trap이 성공·실패 모두 생성한다. 이 안의 다음 파일을 보존한다.

- `logs/ENVIRONMENT.txt`, `PYTHON_FREEZE.txt`, build/campaign/preflight/analysis 로그 및 `EXIT_CODE.txt`; adapter identity와 기존 test evidence 재사용 receipt.
- `build/RECEIPT.json`, `librei_microphysics.rlib`, `he29_owner_server`, 원본 owner checkout; 별도로 고정 BASS execution commit 및 adapter revision/SHA를 기록한다. 기존 WORK archive는 BASS Git source 전체를 자체 포함하는 구조가 아니므로 원본 Git identity와 반환 artifact identity를 함께 보존한다.
- `preflight/PREFLIGHT.json`, `references/DESIGN.json`, `references/SUMMARY.json`.
- case별 `IDENTITY.json`, `SAVED_POINT_PARITY.json`, `TABLE.json`, `Radau.json`, `DOP853.json`, `RESULT.json`; 실패 시 `FAILURE.json` 및 `.partial`도 보존.
- case에 대응하는 `<case>_process/COMMAND.json`, `RECEIPT.json`, stdout/stderr 로그; `native.jsonl.gz` 또는 실패 `.partial`.
- 성공 시 `REFERENCE_ANALYSIS.json`; 불완전 반환에서는 새 파일명으로 별도 부분 분석을 수행한다.

IDENTITY에는 owner source, parent/input/source manifest, binary hash, build receipt, Python/NumPy/SciPy runtime, numerical thread environment가 있다. 서로 다른 case를 대비할 때 binary/source/parent/input/thread identity가 일치해야 한다. 표 SHA는 각각의 유한 model/table에 대응한다.

## 부분·전체 반환에서 가능한 분석

| 확보한 admitted pair | 가능한 분석 |
|---|---|
| 한 개의 table512 pair | 해당 r의 method spread; 저장 n32/n64 transport에 대한 같은-r/same-table temperature 및 absolute fraction 차이 |
| (r2,512)+(r4,512) | 앞의 시간 적분 오차분리에 더해 r2→4의 reference strip sensitivity |
| (r4,512)+(r8,512) | r4→8의 reference strip sensitivity |
| (r4,512)+(r4,1024) | 고정 r4에서 table512→1024 sensitivity |
| 네 pair 전부 | 위 세 sensitivity와 세 r의 저장 transport 비교를 한 source/binary identity 아래 종합 |
| Radau 파일만 있는 실패 case | 원인·ledger 진단에 사용; pair stability 및 reference admission은 아직 성립하지 않음 |

정상 analyzer는 RESULT/IDENTITY/TABLE 세 파일과 두 solver admission을 확인하고 갖춰진 대비만 출력한다. `sum_method_spreads_K`도 empirical 비교량이다. 연속 스펙트럼, nonlinear gas-temperature 상한, 전체 EoR, upstream Grackle 전체 동등성, 관측 Bianchi/CMB는 이 작업에서 승격하지 않는다.

## 권장 NCP 인계문

최신 Git/백업 census에서 새 반환이 없는 것이 확인되면 별도 checkout의 과학·테스트 revision을 1569f3718cd4b17a16936ad3d72bc7d5ed9b0f4f에 고정한다. 준비된 최소 evidence-reuse adapter로 입력 22개를 자동 복원하고 원본 Rust owner/server를 컴파일한다. 기존 50개 테스트는 보존된 identity-matched 근거를 재사용한다. 저장 native 6점 qualification을 유지한 채 위 네 case만 순서대로 실행하고, case3600s/table600s/예상 table2GiB 및 기존 모든 admission을 그대로 둔다. 첫 실패에서 원본을 보존하고 허용된 작은 환경·실행 경계 교정만 한다. 중간·최종 결과는 기존 source/binary/table identity와 실제 호출 수를 붙여 별도 결과 branch/Draft PR 및 create-only 이중 백업에 반환한다. 원격 quota blocker는 이 검토에서 재시도하지 않았다.

### 원본 코드 링크

- [고정 bootstrap](https://github.com/cosmosapjw-quantum/BASS_HE/blob/1569f3718cd4b17a16936ad3d72bc7d5ed9b0f4f/research/he29_survival_budget_20261018/ncp/BOOTSTRAP_REFERENCES.sh)
- [고정 reference runner](https://github.com/cosmosapjw-quantum/BASS_HE/blob/1569f3718cd4b17a16936ad3d72bc7d5ed9b0f4f/research/he29_survival_budget_20261018/src/reference_runner.py)
- [고정 acceptance](https://github.com/cosmosapjw-quantum/BASS_HE/blob/1569f3718cd4b17a16936ad3d72bc7d5ed9b0f4f/research/he29_survival_budget_20261018/src/reference_contract.py)
- [고정 analyzer](https://github.com/cosmosapjw-quantum/BASS_HE/blob/1569f3718cd4b17a16936ad3d72bc7d5ed9b0f4f/research/he29_survival_budget_20261018/src/analyze_references.py)
