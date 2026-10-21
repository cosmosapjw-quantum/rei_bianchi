# D8 저장 표본 late sign-crossing bracket 결과

## 범위와 결과

D8는 Sigma_F,i=0.003 조건 네 개의 저장된 153-sample raw만 읽었다. 정의는 `z=1/a-1`, `S_F=sqrt(6)*s/H`이며, z=4 표본(index 120) 이후 z=2까지 인접 표본의 strict positive-to-negative sign change를 산출했다. 새 ODE/IVP 호출은 0이고 interpolation도 하지 않았다. 표의 구간은 저장 표본 bracket이며 연속 zero-crossing의 시각 또는 위치를 확정하지 않는다.

| Case ID prefix | 초기 matter/radiation stress | 인접 index | 저장 redshift bracket | 부호 있는 S_F 표본값 | raw SHA256 prefix |
|---|---:|---:|---:|---:|---|
| `d58d4df3` | -0.0003 / -0.001 | 135–136 | 2.935305050758642 → 2.8729833462074175 | +1.0225221741549076e-6 → -2.0454133017019474e-6 | `47328036` |
| `6a9c9e40` | -0.0001 / -0.001 | 141–142 | 2.5758703348972847 → 2.519240840702928 | +7.597778575699508e-7 → -1.8922134430080407e-6 | `48f0501a` |
| `1c39be4e` | nominal 0 / -0.001 | 144–145 | 2.408658099402498 → 2.354676672233047 | +8.014231560475592e-7 → -1.6697382871660716e-6 | `d0a9b845` |
| `d98e5a31` | +0.0001 / -0.001 | 147–148 | 2.2492649202717816 → 2.197807733152119 | +9.145758167170672e-7 → -1.3906997662293442e-6 | `5624b968` |

각 행의 전체 case ID, config와 raw SHA256은 `D8_RESULT.json`에 있다. 독립 read-only Astra 검토는 `PASS_SCOPED`, 차단 finding 0으로 bracket 인덱스와 값을 원 raw에 대조했다. 분석 코드와 결과 SHA256은 각각 `b984caaedacedcfd5c2176ae2240c78d4986fbcfcd4689c60d7b131061b259b0`, `643cea016e4bf35968f947aea3519bd292c434094a6e7430e8b9c2fb203318ce`다.

## Provenance caveat

Case c의 원 실행은 `FAILED_WORKER_EXIT`, exit 124였다. 저장 raw는 이후 ODE를 부르지 않는 data-only validation으로 복구되어 결과를 만들었다. `RESULT.serialization_failure.json`와 `ATTEMPT.json` 원문을 함께 포함했다. solver 성공 관측 및 `nfev`, solver message, peak RSS, worker wall은 기록되지 않았다. 명목상 matter stress 0인 입력의 raw 관측 초기값은 -2.1111464705225449e-19다. 다른 세 case의 저장 result exit 0은 원 result receipt와 함께 보존했다.

## 판정 경계와 상위 상태

D8 `PASS_DATA_ONLY_SAMPLE_BRACKETS`; 독립 검토 `PASS_SCOPED`. 이는 네 저장 표본 bracket에만 해당한다. `NATIVE_AGE_TIME_CONVERGENCE=HOLD`, `NONLINEAR_GRACKLE_RESPONSE_BOUND=NOT_ESTABLISHED`, `PRODUCTION_SCIENTIFIC_ADMISSION=NOT_ISSUED`를 유지한다. V12 cap 180초, 누적 debit 200.39897231891518초, 잔여 100건 `NOT_AUTHORIZED`도 불변이다. PR198, 완료 AGE histories 또는 237개 history는 재실행하지 않았다.

NCP에서 새 실행을 제출하지 않았다. 기존 read-only resource observation에서 64 CPU affinity, 80 GiB available RAM, root filesystem 69 GiB free와 load 1.16/0.94/0.51을 관측했으며 cgroup quota files는 이 namespace에서 보이지 않았다. 이 결과는 저장 데이터 분석이라 NCP 실행이 필요하지 않았다.

전체 CI에 관한 기존 상태도 별도다: unchanged Rust paths의 `cargo fmt --check` 실패, Rust tests skipped. 이는 D8의 scoped Python/data-only PASS를 바꾸지 않는다.
