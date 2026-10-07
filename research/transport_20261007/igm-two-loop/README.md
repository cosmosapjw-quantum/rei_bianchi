# IGM two-loop result — 2026-10-07

**두 연구 루프를 실행하고 독립 검토를 통과했다. 생산 IGM solver의 장시간 검증은 아직 완료되지 않았다.** 이 디렉터리는 `forward/rem-hhe-igm-20261006`의 `39c39eab1cc2f1a215723680accc123e67ef13b6`에서 시작한 독립 research crate다. 기존 소스·실패·허용오차는 변경하지 않는다.

## 첫 루프: 실제 blocker를 재현하고 수정

- V2는 양의 underflow tail을 식별하지만 다음 characteristic에서 거절했다. 새 `tail.rs`는 source·흡수·redshift·export의 모든 양의 owner를 유지한다. empty와 작은 양수는 다르다.
- 큰 감쇠 지수와 매우 작은 panel amplitude에서 단일 로그가 유효 정보를 잃는 실패를 각각 재현했다. 보상된 `(log_hi, log_lo)`를 저장·소비하여 수정했다. `log_value()`는 표시용이다.
- ordinary/right-front panel의 실제 부모 밀도를 부분구간에 적분한다. 개수·에너지 shape와 amplitude를 분리하고, 얇은 구간의 정규화 평균을 직접 계산한다. 순간 적분점을 영구 광자 packet으로 저장하지 않는다.
- subnormal 구간 기하가 평균을 잘못 계산하는 실제 반례를 발견했다. 해당 미지원 기하는 fail-closed로 거절한다. 부분구간에 표현 가능한 내부 node가 없으면 stock quadrature도 거절한다.

`evidence/loop1_freeze/`와 `evidence/independent_review/LOOP1_INDEPENDENT_DECISION.json`이 둘째 루프 이전 상태·판정을 보존한다.

## 둘째 루프: 비영 유출과 수학적 확장

- `LeftFront = y exp(beta*y)`를 추가했다. source-on lower edge의 내부 taper를 표현하며, child를 새 front로 잘못 만드는 retapering을 하지 않는다.
- 물리 cutoff에 도달하는 명시적 API가 에너지 왕복 반올림 때문에 정상 event를 거절하던 문제를 해결한다. cutoff와 band-exit energy continuity 오차를 별도로 기록하고 ledger 잔차로 보정하지 않는다.
- 투명한 FLRW stock의 실제 swept measure와 source birth→band exit→cutoff history를 적분했다. source export의 quadratic onset, 비영 유출, 완전 stock export, positive zero-readout tail export를 포함한다.
- 같은 광자 수와 에너지를 가진 양의 스펙트럼의 `E^-3` observable 상·하한을 구현했다. 평균 에너지 `mu`, support `[a,b]`에 대해 `N/mu^3 <= integral E^-3 dN <= N[(b-mu)/a^3+(mu-a)/b^3]/(b-a)`. 이것은 실제 Verner 함수의 인증된 경계가 아니다.

## 최종 검증

| 검증 | 실제 결과 |
|---|---:|
| Native Rust tests | 32/32 |
| Panel Decimal160 oracle | 903 cases, 3,612 comparisons |
| Tail Decimal800 oracle | 86 cases, 1,118 owners |
| Cutoff-anchor Decimal160 oracle | 48 cases, 1,248 owners including export |
| Continuous stock/source oracle | 138 cases, 1,794 owners |
| Continuous owner 최대 상대오차 | 4.4571e-13 < 3e-12 |
| 실제 Rust readout의 최대 N/E 예산 비율 | 0.00197661 / 0.00156111 < 1 |
| 실제 band-exit continuity 오차 | 1.7764e-15 < 2e-12 |
| 세 family의 E^-3 envelope | 18 refinement cases 모두 포함관계 만족 |

ordinary fixture의 가능한 `E^-3` 범위 폭은 기준값 대비 21.493%에서 32개 부분구간의 0.02097%로 줄었다. 이는 두 moment 보존만으로 photo-rate를 인증할 수 없는 이유와 spectral refinement의 정량적 기준을 제공한다. gas feedback 또는 실제 원자 cross-section 오차의 보증으로 사용하면 안 된다.

소스와 입력을 고정한 마지막 통합 재현은 numerical CPU 11.31 s, compilation CPU 3.24 s였다. subprocess 누적 RSS high-water 상한은 170,024 KiB이며 compiler와 numerical process를 분리해서 receipt에 기록했다. 이는 전체 IGM history 속도나 총 연구 시간의 추정이 아니다. 전체 개발 시도·환경 실패·선행 미계측 작은 실행의 한계는 `RESOURCE_SUMMARY.json`에 있다.

## 재현과 읽기 순서

Rust 1.94.1, Python 표준 라이브러리만 사용한다. crate 폴더에서:

```sh
python scripts/reproduce.py --output /tmp/igm-two-loop-replay
```

출력 디렉터리는 새 경로여야 한다. 기존 evidence는 덮어쓰지 않는다. 네트워크나 외부 atomic package 설치가 필요 없다. 실행 전후 source hashes를 비교하며, `cargo test --offline`, 세 primitive oracle, continuous transport 및 observable oracle을 순서대로 실행한다. `--loop 1`은 현재 crate의 panel/tail 부분만 재현한다. 과거 Loop1의 정확한 원본은 별도 frozen source에 있다.

가벼운 모델은 `HANDOFF.json` → `DAG.json` → `RESULTS.json` 순서로 읽으면 된다. 자세한 유도·정확한 endpoint convention은 `theory/PREIMPLEMENTATION_REVIEW.md`, `LOOP2_SPEC.md`, 독립 review를 확인한다. `evidence/integrated_final/`이 최종 source-bound 결과이며 이전 결과는 역사적 기록이다.

## 남은 blocker와 다음 연구 순서

1. paired-log parent state를 실제 inverse N/M closure·split/merge에 연결하고, sharp wake를 고정 beta 범위 안에서 적응 분할한다. 본 모듈은 beta inversion을 구현하지 않았다.
2. 실제 IGM Verner provider, `q~1/(EH)` source 및 prescribed gas stage로 owner 비교를 수행한다. 이번 source control의 q는 log-energy당 상수다.
3. immutable old state와 같은 owner를 사용하는 H/He midpoint residual에 연결한다. rejected trial과 projection failure는 gas/radiation을 함께 rollback해야 한다.
4. four-base interval `Delta ln(a)=8e-4`와 별도 비영 export-onset 구간을 각각 검증한다. 전자는 원래 source의 첫 export 이전이다.
5. 그 뒤 기존 z12→10, 37-field 기준을 그대로 재실행한다. 현재 기록된 8/37 실패는 미해소 상태로 유지한다.

병렬 가능한 IGM 작업은 `DAG.json`에 분리했다. 실제 Verner kernel의 threshold별 envelope 유도와 coupled receiver의 ownership/rollback contract는 production solver 변경 없이 병렬 진행할 수 있다. CR의 fixed-energy BE와 He의 source-free 이력은 provenance를 확인했으나 이번 exporter의 해결책으로 이식하지 않았다.

## 출처와 적용 한계

기존 IGM 연구: `../projected-radiation-bridge-theory/`, `../continuous-boundary-prototype-v2/`, `../short-hhe-midpoint/`. 실제 provider 문헌은 [Verner et al. (1996)](https://arxiv.org/abs/astro-ph/9601009). 본 `E^-3` theorem은 그 fitting formula를 대체하지 않는다.

조건부 positive quadrature의 수치 수렴과 독립 고정밀 비교이지, 전 domain에 대한 interval arithmetic proof는 아니다. 저정밀 readout의 손실 경계는 전체 부동소수점·quadrature·projection·IVP 오차를 인증하지 않는다. 실제 생산 경계 exporter를 교체하거나 full cosmological history를 승인하는 PR이 아니다.
