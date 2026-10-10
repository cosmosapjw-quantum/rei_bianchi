# HE-FLRW02A — source-bound absorption와 잔차 투영

2026-10-05 KST. 하위 노드 HE-FLRW02A_SOURCE_MAP_AND_RESIDUAL_PROJECTION는 조건부 이론·기호 검산 완료다. 상위 HE-FLRW02_SOURCE_BOUND_ABSORPTION_BUDGET는 실제 소비기 실행이 남아 partial이다. HE-F2 또는 scientific admission의 완료가 아니다.

## 입력과 현재 구현

BASS_HE 입력 commit 9df4f33577a0b07ca1d3f8ee2f770baf4c3f309c, tree 20fbb9718a2a02fec9f4baad815f3c7b6952ddea. 기존 research/shared-c64-crossrepo-20260928에 추가한다. rei_bianchi 입력 commit 9455c2a3cbf2ce5ebaba28e9bfb1dfe79aed0efa, tree 27d5c5653b6a85b43bf86f6ca5913f90b9e05106. 소비기는 읽기 전용이며 지정 경로/blob는 INPUT_PIN.json에 있다.

현재 hhe_events.rs에는 static synthetic 7변수 H/He RHS가 있고 microstep.rs에는 backward-Euler endpoint 잔차가 있다. F01 AtomicProvider는 raw reference이고 consumer_admission=false다. 합성 RHS 존재는 물리적 source-dependent history 연결의 증거가 아니다. homogeneous_rates.rs의 이전 blob는 유지되며 기존 시험에 fixed proper absorber/fixed comoving photon의 a=1 대 0.5 비교가 이미 있으므로 재실행하지 않았다.

## 새로 결속한 식

proper absorber l_s, proper photon p_g, bin-integrated comoving photon N_g와 V=(a*MPC_CM)^3에 대해, 같은 source/energy/quadrature/stage에서

    A_sg = c*l_s*sigma_sg*N_g/V = c*l_s*sigma_sg*p_g
    photon_loss_comoving = V*sum_sg A_sg.

N_g에 delta-nu, 4pi 또는 a^-3를 다시 곱하지 않는다. 두 모듈의 sigma가 같을 때의 absorption-only 동일식이며 현재 서로 다른 fixture가 이미 연결됐다는 뜻은 아니다.

새 두 scale 검사는 고정 photon energy에서의 순간적 대수 변환이다.

| 변환 | Gamma | proper event/heat/binding | comoving photon loss |
|---|---:|---:|---:|
| a->lambda*a; proper l,p 고정; N->lambda^3*N | 1 | 1 | lambda^3 |
| a->lambda*a; comoving nuclei/photons 고정; l,p->lambda^-3(l,p) | lambda^-3 | lambda^-6 | lambda^-3 |

팽창 이력 또는 자유전파 해를 주장하지 않는다.

## endpoint 잔차의 정확한 보존오차 투영

z=(x_HII,y_HeII,y_HeIII,u,p0,p1,p2), fixed proper nH,nHe, r=z1-z0-dt*f(z1)로 정의한다. C_s,R_s는 같은 endpoint의 충돌·재결합 사건률이다. 현재 retained recombination photons가 없는 synthetic escape closure에서

    delta_N = Delta(ne+sum p)-dt*sum(C-R)
            = nH*r0+nHe*r1+2*nHe*r2+r4+r5+r6.

HeIII의 전자수 계수 2는 필수다. 충돌·재결합이 켜진 상태에서 ne+sum p 자체가 상수인 것은 아니다.

b_s와 E_g를 erg로 두고 wE=(nH*bH,nHe*bHeI,nHe*(bHeI+bHeII),1,E0,E1,E2), rEsc=Delta(escaped)-dt*escape_rate라 하면

    Delta(total_energy) = wE dot r + rEsc.

HeIII 결합에너지는 두 이온화 에너지의 누적이다. 현재 synthetic capture kinetic energy q=3*kB*T/2의 열 closure에 결속하며 다른 냉각 모형으로 자동 확대하지 않는다.

실제 microstep scale을 su=max(u0,1e-30), spg=max(pg0,1e-30), sEsc=max(Etotal0,1e-30)으로 쓰면 |ri|<=epsilon*si, |rEsc|<=epsilon*sEsc에서

    |delta_N| <= epsilon*(nH+3*nHe+sum spg)
    |Delta E| <= epsilon*(nH*bH+nHe*(2*bHeI+bHeII)+su+sum Eg*spg+sEsc).

이는 삼각부등식에 따른 정확 산술의 조건부 상한이다. binary64 rounding enclosure, inverse-Jacobian 해 오차, 적분 오차 및 source/closure 오차는 별도다. 기존 check_invariants와 허용오차를 제거하거나 완화하지 않는다.

## 실제 실행과 다음 단계

python -B -W error verify_symbolic.py: exit 0, 새 exact identities 30개, nonzero witnesses 5개, 독립적으로 계산한 synthetic rational scale probes 4개 통과. Rust compile/run=0, physical fit evaluations=0, history runs=0, independent scientific review=NOT_RUN. 현재 환경에 rustc/cargo가 없다. Python 검산을 Rust 검증으로 부르지 않는다.

proposed_consumer/he_flrw02_absorption.rs의 두 시험은 PREPARED_NOT_COMPILED_NOT_RUN이다. 다음 HE-FLRW02B_OWNER_NATIVE_MATCHED_ABSORPTION_REGRESSION은 rei_bianchi owner가 최신 관련 blob를 비교하고 해당 파일을 rust/rei_microphysics/tests/he_flrw02_absorption.rs에 추가한 뒤 실행한다:

    cargo test --manifest-path rust/rei_microphysics/Cargo.toml --test he_flrw02_absorption --locked -- --nocapture

원 AtomicProvider.cross_section을 임시 test model에만 연결한다. 20/35/70 eV, a0=0.25, lambda=0.5/2를 쓰며 source/domain/units, commit/tree/blob, command/exit/log와 최대 absolute/relative residual을 반환한다. 5e-14 relative+1e-300 absolute는 roundoff regression 기준이지 물리 오차 기준이 아니다. 실패 시 tolerance 확대나 fit clamp 금지. 소규모 Rust host면 충분하다.

RCT 제외, HE-F2 WAIT_OWNER_OPT_IN_AND_PROVIDER_CONTRACT, HE-F3 WAIT_REI_F09_RESULT, HE-L1/L2/L3 PARKED_OPEN, Eq55 NOT_RUN을 유지한다. 단일 homogeneous x_HII를 Q_V로 이름만 바꾸지 않는다. full history/threshold flux와 Q_M/Q_V/Case-A/B closure는 별도다.

Git은 본 리뷰·입력 pin·반환·검산 코드·소비기 시험 제안을 보존한다. 상세 유도문, 실제 로그/개별 결과, Library에서 회수한 HE-FLRW01 두 원문은 BASS_HE_FLRW02_SOURCE_BOUND_20261005_v1.zip에 보존한다. 원래 FLRW01 ZIP 전체나 과거 원격 백업을 복원했다고 주장하지 않는다. 새 archive의 실제 게시·백업 성공 여부는 detached DELIVERY_RECEIPT가 소유한다.
