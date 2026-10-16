# PR #150 source-on 단계의 시간 배치: 다음 계산을 위한 코드 판독

고정 소스는 `6ea2b1b4b3875c9163cafc45efe720afded43fc4`이다. 이번 RR/DR-only 직접 비교가 검토된 뒤 원본 `rust/rei_microphysics/src/axbi_driver.rs`와 `igm_thermal.rs`를 읽었다. 아래는 **코드의 시간 배치**이며, 각 항이 기존 source-on 전체계의 관측된 1차 오차에 기여하는 비율을 수치적으로 분리한 결과는 아니다.

| 항목 | 고정 소스의 실제 경로와 시간 배치 | 미측정 구분 |
|---|---|---|
| Photon birth | `Driver::tentative`가 시작 상태를 기하 중점까지 보낸 뒤 `inject(&mut s, dt)`를 한 번 호출한다. `inject`는 중점 기하에서 `transport.inject`에 전체 proper `dt`를 전달한다. | source-age와 birth quadrature 단독 시간 오차는 이 실행에서 측정하지 않았다. |
| Opacity와 absorption | `chemical_stage`는 중점 기하에서 `transport.prepare`를 한 번 만든다. `ResidualContext::evaluate`가 각 trial species의 absorber 밀도로 `evaluate_for_cell_count(..., dt)`를 평가한다. 광자와 화학은 같은 nonlinear residual 안에 있지만 preparation은 Newton 전 고정된다. | opacity 시간 보간 및 photon state의 단계 내 변화에 의한 오차를 별도 분리하지 않았다. |
| Collisional chemistry | `ResidualContext::evaluate`의 residual은 `unknown - old - dt × point.rhs`이다. `AxbiProvider::point` → `igm_point_rhs`는 trial EOS와 density에서 CI, RR, DR를 계산한다. 이것은 해당 단계의 endpoint RHS 평가다. | 이 backward-Euler 형태는 1차 시간 오차의 후보이나 실제 full source-on 오차의 지배 원인으로 판정하지 않았다. |
| CE, free-free, CMB | 같은 `igm_point_rhs`는 trial EOS에서 CE 및 free-free 냉각과 CMB exchange를 계산한다. `ResidualContext`가 CMB 온도 `2.7255 / a_mid`를 전달한다. | 각 thermal 항의 time-centering 기여는 미측정이다. |
| FLRW work | `tentative`는 `geometry_map(mid)`와 `geometry_map(to)`로 gas adiabatic work와 photon geometry work를 각각 회계한다. 화학 단계의 `igm_point_rhs`는 `h=0`을 받아 중복 expansion work를 넣지 않는다. | 이 split과 source/chemistry의 교환자 오차는 미측정이다. |

`fixed_step`도 이 `tentative` 경로를 사용하므로 기존 source-on refinement의 owner를 바꾸지 않고 시험할 수 있다. 다음 최소 실행 단위는 **고정 입력의 동일 구간**에서 `N=8,16,32,64,128`을 유지한 채 항을 하나씩 분리하는 독립 experimental branch다. 먼저 원본 전체 chemistry에서 source/photon만 0으로 둔 제어군과, source-on에서 photon birth·opacity operator만 분리한 제어군을 만들고, 각 군의 Tgas, species, photon count/energy, chemical/thermal/escaped ledger를 같은 시간점에서 비교한다. 이후에야 CI/CE/free-free/CMB의 평가 시점을 하나씩 바꿔 원인별 시간 오차를 측정한다. 어떤 제어군도 원본 production branch나 checkpoint를 수정하지 않는다.

이번 native RR/DR-only PASS는 이 항들의 source-on 2차 수렴을 뜻하지 않는다. 전체계의 특정 1차 원인은 `HOLD: NOT_ISOLATED`다.
