# source007: source-bound BASS provider 통합과 실제 component 결과

REI PR159와 BASS PR166의 정확한 source/table identity를 현재 source006에 선택적으로 연결했다. 기본 AXBI, ResidualContext/Jacobian, transport와 단일 photon/event/thermal owner는 보존했다. 새 표적 검사9개와 release build가 통과했다.

fixed_step 오류 경로의 실제 RHS/attempt 차감 보존을 수정했고, 미측정 adaptive 오차를0으로 출력하던 필드는 독립 검토 후 제거했다. 원래2/2 invocation은 보존하고 별도 승인된 rebuild1회를 더해 총3회20.121775초를 기록했다. 원본 binary/source와 수정 전 기록은 보존했다.

## 실제 source-on BASS 계산

| Case | 초기 Tgas[K] | 종료 Tgas[K] | 종료 s/H | 재시작 차이 |
|---|---:|---:|---:|---:|
| COLD_FLRW | 8.098143045064857 | 8.699222018473613 | 0 | 0 |
| SIGNED_MINUS | 8.098143045064857 | 8.699191616056419 | -0.009993460673205364 | 0 |

동일121-row table, main4steps×Δln(a)=1e-4와 checkpoint 이후 재시작2steps를 case당 수행했다. main52RHS와 replay26RHS, 총156RHS다. 두 실행wall0.066069/0.064635초, exit0이며 native checkpoint에서 새 compiled source7a085a...를 관측했다. photon/energy/geometry/Newton/point-owner 기준을 모두 통과해 별도 독립 검토가 component 결과 게시를 승인했다.

이는 full005의 REC-conditioned Tgas=9.306...K 시나리오와 다른 donor component IC다. source005의 연속 실행이나 같은 시나리오의 geometry 효과 측정으로 해석하지 않는다. config.q_ref=0은 analytic knob 비활성화이며 SIGNED_MINUS의 실제 shear는 비영점이다. signed s/H와 producer Σ=√3|s|/H를 구분한다.

## 정확한 다음 단계와 경계

기존 baseline 결과를 재사용하고 같은 표·IC·종점의 h/2,h/4 시간 간격 차이를 새 유한 계약에서 측정한다. GL4/GL8 차이는 이번 example이 출력하지 않아 null/NOT_MEASURED다. clock identity residual0은 quadrature 오차 상한이 아니다. adaptive/full-history 수렴, momentum/recoil/polarization, 동적 Einstein 결합과 isotope-native 완주는 미완료다.

## Git 동시 변경 보존

실제 launch HEAD3ac94bbe는 보존했다. 외부 owner의 full005 pair-diagnostics R1–R6(별도 경로) 추가 때문에 최초push가 거절됐다. 해당 변경을 fetch하고 unpublished source007 commit만 rebase하여32039b4779e79bdba464bac749443a9917e9e2e3으로 게시했다. 이전 commit은 refs/codex/checkpoints/source007-port-20261016-001에 남겼고, Rust/source bytes와 실제 compiled identity는 변하지 않았다. reset/stash/forcepush는0회다.
