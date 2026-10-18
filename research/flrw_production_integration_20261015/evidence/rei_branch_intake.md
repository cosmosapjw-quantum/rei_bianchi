# REI branch intake — 2026-10-15

권장하는 첫 production 변경은 **Rust의 국소 proper-time 증가량과 단계별 geometry 공유**이다. 기존 cold Grackle H/He·열화학과 공통 photon/event ledger는 유지한다. Python 연구 branch를 통째로 병합하거나 warm receiver를 production으로 바꾸는 작업은 필요하지 않다.

Central 기준은 `codex/rux-science-delivery-20261014`의 `0fcb2dddf5de6b583c2e00f150abff0b2afb6315`이다. 아래 8개 head와 실제 source/test/status 파일 33개를 읽었다. GitHub exact-head Contents API의 Git blob을 이후 로컬 `refs/remotes/intake/pr*`의 같은 파일과 대조했으며 **8개 head, 33개 blob 모두 일치**했다. 각 경로·blob·SHA256·API·test 이름은 [rei_branch_intake.json](rei_branch_intake.json)에 있다. 이 intake에서 solver, test, benchmark는 실행하지 않았다. 이전 실험도 재실행하지 않았다.

| PR | 실제 head | production에 가져올 수 있는 부분 | 유지할 한계 |
|---|---|---|---|
| 128 | `26177f10d2c3264189980af2de26b3f63a9227fc` | `dynamic.reactions_vector/reactions_scalar`의 공통 absorption/heat 사건과 독립 scalar control | 고정 z4 photo-only receiver; 연속 emissivity·팽창·전체 열화학 없음 |
| 130 | `10c57ed9419344d56aa9fb2d2f9feeb14b0a20a2` | `casea.rec_analytic/rec_step`의 양성 He chain·퇴화 rate 한계 및 보존 control | `CaseARates`는 **10000–24000 K**의 8-channel PCHIP; cold 출발/전체 CI·CE·freefree·Compton 대체 불가 |
| 134 | `5d940a023507a601c2c8c935bad0b0aea1dcbe9c` | **우선 이식:** source-bound `stable_dx`, `gauss_increment`, 안정적 Killing 증가량 | 5개 supplier를 전부 runtime prerequisite로 만들지 않음; CR precision은 HOLD |
| 138 | `d7d0e3ad2d6d7cccdfd70df3a0f310df93ec553d` | 원래 Rust `AxbiSource` exporter의 N/U·proper density·source ID 검사; 안정적 ray math | 주 loop는 Python/NumPy+warm C11, near-z4 manufactured IC. coalescence는 조건부이며 source의 mu clamp를 central no-clipping 정책에 그대로 복사하지 않음 |
| 143 | `af67c5314669492b07cb574170c09f70994974e4` | 기존 ledger의 photon+thermal+binding+escape+work−source 독립 readback, 실제 shear-work 식 | open external Q0 audit이며 stellar/escape 전체 Einstein Tmunu closure 아님; duplicate DOP853 shadow solve를 production에 넣지 않음 |
| 149 | `79586facd6352e7bf40cc6c7042d26923e79d7dd` | 실제 Case-A escape energy/birth 기반의 선택적 fixed-background angular-pressure envelope | spectrum/count 미상 유지; carrier 30 eV는 물리 spectrum이 아님. nonlinear Einstein 재결합 결과 아님 |
| 145 | `54e29dff5a90c0a785cb6dcfb004403614ca403b` | 나중에 필요한 경우 positive massive canonical FV의 mass-shell/continuity control | 별도 massive/Einstein 모델. 현재 FLRW cold H/He production의 prerequisite 아님 |
| 148 | `8ae94c5c5a53b1a12fffaa25ac20b7e8f4f31c99` | 실제 energy/momentum partner가 없는 damping을 거절하는 negative control | 입력 optical depth 조건부 event이며 microscopic collision rate 없음; H/He reaction 또는 물리 massive collision으로 활성화 불가 |

## 첫 Rust delta와 사전조건

원본 경로는 PR134의
`research/rei_crossrepo_integration_20261015/suppliers/bass/rei_axbi_shortstep_20261015/shortstep.py`이며 Git blob은 `9997b4fb9638770c2758781bb235ed000bd9e546`이다. 인접 `rei_axbi_background_supplier_20261015/axbi_provider.py`의 `Background.mean_hubble/shear`가 같은 physical-density-fixed `H=hypot(H_FLRW,s)`, `s=q_ref H_FLRW(a_ref)(a_ref/a)^3`를 제공한다.

`gauss_increment(bg,a0,a1,order=4,max_step_x=.0028)`의 계약은 다음과 같다.

- 이미 반올림된 실제 endpoint에서 `dx=log1p((a1-a0)/a0)`를 계산한다.
- `panels=max(1,ceil(dx/.0028))`, 최대 2048개 panel이다. 원본은 Gauss order 2/4/6/8/12를 허용하며 production의 선택 범위는 root가 지정한 GL4/GL8이다.
- `a=a0*exp(lambda*dx)`에서 실제 `H(a),s(a)`를 평가하고, 양의 quadrature weight로 `dt=dx*sum(w/H)`, `db=dx*sum(w*s/H)`를 얻는다. `dt`는 proper seconds, `db`는 무차원이다.
- `a_ref<=a0<=a1<=a_end`; 동일 endpoint는 `(0,0)`, 진행 interval은 유한한 `dt>0`가 필요하다. q=0에서 db=0을 유지한다.

Central `AxbiBackground::point_at_scale`은 query마다 4096-panel Simpson 적분을 수행한다. `Driver::tentative`는 누적 t 두 값을 빼고, `geometry_map`, `ray`, `inject`, `moments`와 출력/validation에서 같은 geometry를 반복 요청한다. 따라서 `axbi_background.rs`에 국소 증가량 callback을 두고, `axbi_driver.rs`의 한 trial에서 endpoint/midpoint 및 angular-ray geometry를 공유하는 작은 변경이 직접 연결된다. 동일 query cache는 기존 값을 유지할 수 있지만, 누적-time 차감을 다른 quadrature로 바꾸는 부분은 **numerical method 변경**이므로 새 source/config identity와 지정된 changed-seam 검증이 필요하다. 이 intake는 speedup 수치를 주장하지 않는다.

물리 상수·scenario는 central source를 계속 사용한다. Python 실행 의존성이나 BASS checkout을 production에 새로 요구할 필요가 없다. 실제 인접 binary64 endpoint의 양의 dt, signed/zero shear, geometry와 보존 ledger를 대상으로만 변경 검증을 설계한다. 기존 byte-bound checkpoint에 새 소스를 몰래 resume하지 않는다.

## 보존할 source와 구분

Central `AxbiProvider::point -> igm_point_rhs`는 pinned Grackle `af7939494ce65007887ada7b98d1813df6843346`의 operational **1–10^6 K** 모델이다. `chemical_stage/evaluate`는 동일 point residual과 photo 사건/heat를 사용하고, `adaptive_step`은 full/two-half control을 이미 갖는다. 기존 rate/thermal channels, positivity/domain rejection, output cadence·budget, checkpoint identity를 보존한다. C10 midpoint/exponential 또는 C11 Strang을 도입하려면 그것은 별도 수치법 변경이지 같은 solver의 단순 속도개선이 아니다.

각도·단위 adapter도 필요하다. Central `p.sigma`는 signed `s/H`이고 PR145/149의 `Sigma`는 `sqrt(3)*abs(s)/H`이다. signed orientation을 별도 보존하고 `q_ref=s_ref/H_FLRW(a_ref)`와 혼용하지 않는다. PR143의 open-Q0를 닫힌 stellar EOS 또는 전체 Einstein 보존 주장으로 올리지 않는다. Case-A escape energy에서 emitted spectrum/count를 만들어내지 않는다.

## 실제 과학 prerequisite와 오래된 정책 표현

현재 사용자는 production 수정을 승인했다. `CLAUDE.md`의 Rust canonical 정책은 새 Python 연구의 수학·검증 source를 읽고 Rust로 연결하는 일을 막지 않는다. 오래된 handoff가 모든 production 변경을 무조건 unauthorized라고 쓰거나 새 연구 Python 전체를 unusable로 취급한다면, 그 문장만 현재 승인·source-native integration owner·별도 scientific admission에 맞춰 고치는 것이 최소 교정이다. 이전 receipt의 scope는 수정하지 않는다.

실제 prerequisite는 provider domain, 전체 event/thermal model, clock/geometry convention, 단일 energy/photon owner, 변경 수치법의 검증이다. 모든 branch 병합, 모든 supplier actor, massive collision 도입, 전체 Einstein/CMB closure는 첫 조건부 FLRW abundance history를 위한 blanket gate가 아니다. 반대로 unowned collision rate, warm-domain extrapolation, 누락된 energy partner는 실제 물리 결함이며 정책 문구를 바꿔 해결할 수 없다.

결론: root가 소유한 Rust driver에 **direct finite interval GL4/GL8 + shared geometry**를 먼저 연결한다. full cold native chemistry는 유지하고, 사건·source·work 검증 source만 작게 재사용한다. 나머지 coalescence/Einstein/massive/collision 연구는 요구되는 claim과 물리 owner가 생길 때 독립적으로 선택한다. 이 문서는 새 scientific admission을 발급하지 않는다.
