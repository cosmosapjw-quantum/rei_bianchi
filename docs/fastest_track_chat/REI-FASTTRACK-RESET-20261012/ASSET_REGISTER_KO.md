# 과학 fast track 자산 등록부

2026-10-12. 기존 세 자산 노트의 사실·자격을 통합했다.

## 1. 고정 기준

| 자산 | 고정 commit | 자격 |
|---|---|---|
| PR104 reduced | `f66929c23ea3fa6e39dd4808e5b27d136c568a03` | `PROMOTE_SCOPED_REDUCED_HISTORY`; S0/S1/S2 DONE |
| PR83 수송 | `6bf81d268e827942614669f2edd978e23b78b0d1` | 확인한 public API·소스 재사용 후보 |
| PR110 native | `17f8d0daa72e0f76a49cde01b110f650a6688c42` | `ALLOCATION_EXHAUSTED`; 전구간 HOLD/NOT_EVALUATED |
| PR112 stepper | `2cae28f8d156d33511d38de9725983f59c03549c` | 조건부 synthetic implicit/adaptive |
| PR113 rate | `efb63623c4ed0f6c270a677fab3eb0a81ce80e34` | RCT-OFF 저장 이력의 nominal number-rate |

PR110/112/113은 07:05:29Z snapshot에서 open/draft/unmerged다. [R-D] [T-L] [N] [S112] [S113]

## 2. PR104: 즉시 활용할 reduced 기준선

공통 경로: `research/broad_history_20261010/`.

RUN002는 **mean-volume z20→4+의 14개 경우, 각 16,384 steps**다. FLRW τ=0.03744182127, 초기 r=s/H=.1의 τ=0.03741570902, Δτ=−2.61122e−5다. **τ20→4+는 부분 구간 기여**이며 전체 CMB τ가 아니다. 엄격한 DOP853 비교는 **FLRW/r=.1 두 경우**에 입증되었다: 최대 |ΔQ|=1.08065e−8, |Δτ|=1.78572e−10. 8192→16384 차이는 3.24195e−8, 4.9860e−10이다. 나머지는 scenario sensitivity다. 물리모형 오차·continuum certificate는 아니며 RUN001 실패도 보존한다. [R-R] [R-D]

고정 R15 emissivity·HG97 case-B·ionized-zone T=20,000 K·HeII closure의 **background-only 결과**다. 같은 평균 a·baryon/source 조건의 평균 H shear 효과이며, 방향별 수송·spectrum·편광은 없다. He photon budget·HeIII·열진화·관측 적합도 미포함이다. mean z와 directional observed z를 구분한다. [R-C]

| 공통 경로 아래 자산 | 실제 확인 범위 |
|---|---|
| `evidence/RUN002/BROAD_HISTORY.png` | 287,752 bytes |
| `evidence/RUN002/flrw_n16384/preview.csv` | 77,009 bytes |
| `evidence/RUN002/rp01_n16384/preview.csv` | 77,127 bytes |
| 두 case의 `COMPLETE.json`, `STARTED.json` | 실제 존재 |

위는 Git metadata 확인이며 PNG·CSV 본문과 raw bytes는 읽지 않았다. 배경 경로는 `research/physical_provider_20261010/background.py`, 계약상 SHA256은 `b80f1d2ca8b4ab251d93447ff746428e6230130bee9b87500b7960bbc3a0076d`다. 배경 소스도 재실행하지 않았다. [R-E] [R-F] [R-P] [R-C]

**현재 재사용 결정:** 기존 PNG·두 preview·보고서의 Q/τ 및 source/C/T/IC 민감도 표를 pin·단위·경계·closure·기존 합격 수치와 연결한다. 적분·검증 반복은 필요 없다. 정량 prescribed 입력에 사용할 CSV 열/샘플링은 미확인이고, preview 보간 오차를 full-grid 수렴 오차와 같다고 가정하지 않는다. Bianchi-specific 신호나 CAMB/CLASS 비교 완료는 아직 없다. [R-R] [R-D]

확인한 listing에는 full `history.npz`, `*_BASS_CELLS.csv`, PDF가 없다. DECISION의 NPZ/BASS hash·검토 기록과 bytes 확보를 구분한다. C01 `REI_ACCEL01_C01_BROAD_RUN_20261010.zip`은 30,524,325 bytes의 pinned base background 필요 overlay이며 full remote restore 미실시다. 이 receipt만으로 최종 RUN002 raw 포함을 단정하지 않는다. 정밀 cell 후처리의 delivery/member/hash 미확인은 남지만 기존 그림·표·compact 활용을 archive 전체 복구로 막지 않는다. N4는 S2에만 의존하며 새 BASS/native 수신·CR/RCT/HH·관측 admission은 기존 결과 활용의 선행조건이 아니다. [R-B] [R-D] [R-E] [R-F] [R-P] [R-G]

## 3. PR83: 수송 코드의 재사용 범위

공통 경로: `rust/rei_microphysics/`.

| 소스 | 확인한 API·경계 |
|---|---|
| `src/bianchi_i.rs` | public `GeometrySnapshot/GeometryBackground/ConstantHubbleBackground`, `CharacteristicRay::{pullback,derivative,solid_angle_jacobian}`. 대각 Bianchi-I 에너지·방향 이동과 occupation 보존; 제공 배경은 상수 H, Einstein 일관성은 외부 책임 |
| `src/angular_photons.rs` | `PhotonPacket`, `RadiationState::{transport,remap}`, `PhotonGrid/PhotonBins`. comoving count·에너지·경계 밖 수량; intensity/multipole·충돌·Stokes 없음 |
| `src/lib.rs` | 확인한 public module/export |
| `src/igm_background.rs` | `FlatFlrwBackground::{at_ln_a,at_redshift}`; proper 밀도·시간 미분. proper-time 역변환이 없어 `snapshot(t)`는 아님 |
| `src/paired_runtime.rs` | `PairedConfig/PairedState/paired_trial` 존재. 고정 H·q-ray·10–20 eV·원자 결합·per-H count이며 lib export 없음; 일반 수송 runner로 등록하지 않음 |
| `tests/bianchi_i.rs` | characteristic·미분·역변환 시험 코드; 실행 안 함 |

출처: [T-G] [T-A] [T-L] [T-F] [T-P] [T-T]

**현재 collisionless 수송은 xe에 반응하지 않는다.** prescribed xe의 τ를 별도 기록해도 intensity를 재이온화 산란 결과라 부를 수 없다. **Polarized Thomson: NOT_LOCATED**는 확인한 파일/공개 export에서 Stokes·screen 운반·편광 충돌 연산자를 찾지 못했다는 범위다. 다른 branch/repo 전체의 부재 판정이 아니며 “기존 kernel 즉시 실행”은 미확인이다. [T-G] [T-A] [T-L]

occupation–packet weight 연결과 관측량 투영은 호출자 책임이다. 방향별 intensity에는 proper `V ΔE ΔΩ`와 광속, 현재 tetrad의 각도 가중치를 명시하며 packet count에 Jacobian을 중복 적용하지 않는다. attenuation은 Thomson 산란이 아니고 intensity와 편광 완성을 구분한다. [T-G] [T-A]

### Reduced–수송 입력의 의미

prescribed 계약은 `t_s,a_i,H_i,nH_proper_cm3,xe_per_H`·초기 스펙트럼·tetrad·출력 epoch다. ln(a)를 초로 전달하지 않는다. `xe=n_e/n_H`에서
`n_e=n_H[xHII+yHe(xHeII+2xHeIII)]`, `yHe=n_He/n_H`다. **PR104 closure에 한해 ne=(nH+nHe)Q, xe=(1+yHe)Q**다. Q 자체를 일반 xe로 쓰지 않으며 He/residual·분율 분모·proper/comoving 단위를 고정한다. [R-C] [T-L] [T-F]

cosmic-time `τ(t,tobs)=∫t^tobs c σT ne dt`의 시작시간 미분은 음수이고 conformal time에는 a 인자가 필요하다. 균질·comoving·cold 전자의 같은 cosmic-time 경계에서 τ는 방향독립이다. 수송 대조군은 같은 H(t)·평균 a=(a1 a2 a3)^(1/3)·ne·스펙트럼·광원·경계에서 방향 차이만 제거하며 같은 물질의 Einstein-FLRW 해라 주장하지 않는다. [R-C] [T-G]

Thomson의 탄성·전자 정지계 및 thermal/recoil/bulk-motion 보정 제외, 편광 screen/Stokes convention을 별도로 유지한다. 유한 ±shear의 정확한 parity·모든 scalar의 보편적 차수·Bianchi 고유성·관측 식별성은 미확립이다. 

## 4. PR110: 보존할 상태와 선택적 native 자산

공통 경로: `research/accel02_20261011/q1b/c12/`.

전구간 binding·24-field 출력·재개 계약은 구현됐으나 전구간 이력은 미완료다. gen96·193-state prefix·cursor102=accepted96+rejected6·별도 failed debit3으로 cap105 소진; PILOT 이후 신규100회=93수용+4거부+3실패다. **ALLOCATION_EXHAUSTED는 예산 종료**이며 새 성공·수치 실패가 아니다. active failure 없음, z=15.8309489031, **1/129는 초기 epoch0만**이다. z=4·time9/spectral24의 65/129 비교는 NOT_EVALUATED/HOLD이며 Bianchi·새 BASS admission도 없다. 외부 job 관찰·중지 없음. [N]

저장 attempt67–102에서 h는 15.360배 감소했다. HI cell24(13.6–14.6507733 eV)의 **99.908401%는 마지막 full–two-half GammaHI signed 차이의 기여**이며 전체 이력 오차 비율이 아니다. hκ=8.059/5.311은 stiff splitting/order reduction의 단서이고 인과·error floor·Zeno는 미증명이다. h/h2/h4는 DESIGN_ONLY_NOT_EXECUTED, 19.777 s/attempt는 국소 측정이므로 전구간 ETA를 주장하지 않는다. [N]

| 재사용 자산 | 유지 조건 |
|---|---|
| HM12 source·양쪽 경계 moment arithmetic | N/U·band·reference/proper volume·시간; heating tail 무근거 절단 금지 |
| K0/KE → species Gamma·primary heat | 같은 gas의 감쇠 measure·단위·흡수종 밀도; 출력 N/U로 native Gamma 대체 금지 |
| positivity·realizability·ABI heat | clamp/floor 없이 도메인 유지; N/U fit만으로 opacity/heat 정확도 주장 금지 |
| source/event·energy/photon ledger | 중복 방지·초기 분모·signed exchange; native 1e−9 기준 보존 |

r=0·조건부 IC·primary-only Case A·등방 CMB 범위이며 새 closure·비영 shear·전구간 PASS는 아니다. D는 A/B/C의 선행조건에서 해제하되 checkpoint·실패·기준을 보존한다. 기존 재개 계약은 새 control identity·create-only child·193-state/cursor/3 failure debits·누적 할당/중단 기준이다. 목표량의 지배적 모델 오차를 정밀 원자물리가 줄일 근거 없이 핵심 경로에 복귀시키지 않는다. adaptive 시간축은 순차 의존적이며 코어 증가로 stiffness 해소·선형 가속을 가정하지 않는다. [N]

## 5. PR112/113: RCT 공급 자격

PR112 `rust/rei_microphysics/tests/rct_step01.rs`와 같은 ref의 `rust/rei_microphysics/src/ft03_controlled.rs`는 synthetic FT03/RCT implicit/adaptive 경로다. `research_input_ev`, `CALLER_SUPPLIED_NO_ATOMIC_MOMENT`, `physical_closure_admission=false`가 명시되어 **물리 에너지 공급자가 아니다**. [S112]

PR113 `research/rct_rate_only_p01_20261011/REPORT_KO.md`는 **RCT-OFF warm P01 저장 17 epochs**의 KF96 nominal number-rate 진단이다. 선형 exposure 보간 오차는 미평가이며 RCT-ON·thermal power·spectrum·N5 materiality가 아니다. [S113]

물리 source의 유효 상태영역·escaping photon energy/moment·불확실성·energy/event 계약·소비자 observable budget은 아직 별개다. 임의 평균광자 에너지로 승격하지 않으며 공급 미완료는 A/B/C를 막지 않는다. [S112] [S113]

## 6. PHYS35: 보존하는 수학적 자산

PR83 고정 commit의 `docs/fastest_track_chat/REI-PHYS35-20261012/report/PHYS35_REPORT_KO.md`를 기존 채택 기록으로 유지한다. 고정 source/kernel과 서로 다른 두 A에서 얻은 root-gap 제약은 해당 영역의 moment/shape 폐쇄 진단에 한해 재사용한다. 이를 Δτ 또는 물리적 예측으로 변환하지 않는다. PHYS36의 J/계수 구조 안정성 후속은 관측량 오차와의 필요성이 드러날 때까지 DEFERRED_NONBLOCKING / NOT_RUN이다. PHYS35 first 1/replay 1 소진, remaining 0과 기존 HOLD/FAIL을 보존한다. [P35]

## 7. 확인 범위

원본 PR104: 본문 5개+directory metadata 3개. PR83: module 목록+7 targeted reads(6파일 성공, `tests/angular_photons.rs` 404). PR110/112/113: snapshot+8 reads; C12 HANDOFF/NEXT_DAG/STEP_SIZE_TREND/REPORT 일부, PR112 test·ft03_controlled 일부와 changed-filenames, PR113 보고서 전체다. raw/ZIP 복구·native import/main·시험 실행은 없었다. 이번 통합은 세 로컬 노트만 읽었고 새 과학적 승격 판정은 없다.

[R-R]: https://github.com/cosmosapjw-quantum/rei_bianchi/blob/f66929c23ea3fa6e39dd4808e5b27d136c568a03/research/broad_history_20261010/REPORT_KO.md
[R-C]: https://github.com/cosmosapjw-quantum/rei_bianchi/blob/f66929c23ea3fa6e39dd4808e5b27d136c568a03/research/broad_history_20261010/SCIENTIFIC_CONTRACT.md
[R-D]: https://github.com/cosmosapjw-quantum/rei_bianchi/blob/f66929c23ea3fa6e39dd4808e5b27d136c568a03/research/broad_history_20261010/independent/DECISION.json
[R-G]: https://github.com/cosmosapjw-quantum/rei_bianchi/blob/f66929c23ea3fa6e39dd4808e5b27d136c568a03/research/broad_history_20261010/DAG.json
[R-E]: https://github.com/cosmosapjw-quantum/rei_bianchi/tree/f66929c23ea3fa6e39dd4808e5b27d136c568a03/research/broad_history_20261010/evidence/RUN002
[R-F]: https://github.com/cosmosapjw-quantum/rei_bianchi/blob/f66929c23ea3fa6e39dd4808e5b27d136c568a03/research/broad_history_20261010/evidence/RUN002/flrw_n16384/preview.csv
[R-P]: https://github.com/cosmosapjw-quantum/rei_bianchi/blob/f66929c23ea3fa6e39dd4808e5b27d136c568a03/research/broad_history_20261010/evidence/RUN002/rp01_n16384/preview.csv
[R-B]: https://github.com/cosmosapjw-quantum/rei_bianchi/blob/f66929c23ea3fa6e39dd4808e5b27d136c568a03/research/broad_history_20261010/CHECKPOINT_RECEIPTS.json
[T-G]: https://github.com/cosmosapjw-quantum/rei_bianchi/blob/6bf81d268e827942614669f2edd978e23b78b0d1/rust/rei_microphysics/src/bianchi_i.rs
[T-A]: https://github.com/cosmosapjw-quantum/rei_bianchi/blob/6bf81d268e827942614669f2edd978e23b78b0d1/rust/rei_microphysics/src/angular_photons.rs
[T-L]: https://github.com/cosmosapjw-quantum/rei_bianchi/blob/6bf81d268e827942614669f2edd978e23b78b0d1/rust/rei_microphysics/src/lib.rs
[T-F]: https://github.com/cosmosapjw-quantum/rei_bianchi/blob/6bf81d268e827942614669f2edd978e23b78b0d1/rust/rei_microphysics/src/igm_background.rs
[T-P]: https://github.com/cosmosapjw-quantum/rei_bianchi/blob/6bf81d268e827942614669f2edd978e23b78b0d1/rust/rei_microphysics/src/paired_runtime.rs
[T-T]: https://github.com/cosmosapjw-quantum/rei_bianchi/blob/6bf81d268e827942614669f2edd978e23b78b0d1/rust/rei_microphysics/tests/bianchi_i.rs
[N]: https://github.com/cosmosapjw-quantum/rei_bianchi/tree/17f8d0daa72e0f76a49cde01b110f650a6688c42/research/accel02_20261011/q1b/c12
[S112]: https://github.com/cosmosapjw-quantum/rei_bianchi/blob/2cae28f8d156d33511d38de9725983f59c03549c/rust/rei_microphysics/tests/rct_step01.rs
[S113]: https://github.com/cosmosapjw-quantum/rei_bianchi/blob/efb63623c4ed0f6c270a677fab3eb0a81ce80e34/research/rct_rate_only_p01_20261011/REPORT_KO.md


[P35]: https://github.com/cosmosapjw-quantum/rei_bianchi/blob/6bf81d268e827942614669f2edd978e23b78b0d1/docs/fastest_track_chat/REI-PHYS35-20261012/report/PHYS35_REPORT_KO.md
