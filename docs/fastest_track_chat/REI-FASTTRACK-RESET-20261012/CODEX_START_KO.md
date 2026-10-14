# 다음 실행 인계 — FT-B1A

## 바로 수행할 일

**PR104의 고정된 reduced history·LRS 배경을 PR83의 Bianchi ray/packet API에 연결하고, 방향별 intensity와 quadrupole의 작은 실행 결과를 만든다.** 이것이 다음 필수 연구 작업이다. PHYS36이나 full native history 완성을 먼저 실행하지 않는다. 이 문서는 2026-10-12의 계획 변경으로 작성되었으며, FT-B1A 실행은 아직 하지 않았다.

현재 사용자 요청이 계획 조정인 세션에서는 여기 적힌 계산을 미리 실행하지 않는다. 사용자가 다음 연구 루프/구현을 지시한 세션에서 이 인계를 시작점으로 삼는다. 적용되는 연구 루프 하네스가 요구하는 실행·재현 절차는 그 실제 알고리즘과 산출물에 적용하되, 변경 없는 PHYS35/native 실험을 재실행하는 단계로 확장하지 않는다.

## 1. 입력과 재사용 위치

| 용도 | 고정 소스 |
|---|---|
| PR83 코드 | `6bf81d268e827942614669f2edd978e23b78b0d1`의 `rust/rei_microphysics/src/` |
| Bianchi geometry/특성선 | `bianchi_i.rs`: `GeometrySnapshot`, `GeometryBackground`, `CharacteristicRay` |
| 패킷 수송·재배치 | `angular_photons.rs`: `PhotonPacket`, `RadiationState::transport/remap` |
| FLRW proper density 참고 | `igm_background.rs`; `at_ln_a/at_redshift`는 `snapshot(t_s)` 자체가 아님 |
| reduced history 기준 | PR104 `f66929c23ea3fa6e39dd4808e5b27d136c568a03`, `research/broad_history_20261010/REPORT_KO.md` 및 `SCIENTIFIC_CONTRACT.md` |
| 실제 LRS 배경 정의 | 같은 PR104 commit의 `research/physical_provider_20261010/background.py` |
| baseline 자료 | `research/broad_history_20261010/evidence/RUN002/BROAD_HISTORY.png`, `flrw_n16384/preview.csv`, `rp01_n16384/preview.csv` |

최소한 현재 작업 브랜치와 해당 파일의 실제 상태를 확인한다. 소스 pin과 달라졌다면 관련 diff만 읽고 조정한다. 전 저장소·모든 PR·과거 archive를 재감사하는 문턱을 만들지 않는다. `paired_runtime.rs`는 현재 lib export에 없고 고정 H·좁은 에너지·원자 결합용이므로 일반 runner로 실행된다고 가정하지 않는다.

## 2. 한 번에 연결할 최소 구현

### 이력/시간 어댑터

입력 표는 적어도 `t_s, a_perp, a_parallel, H_perp_s_inv, H_parallel_s_inv, nH_proper_cm3, xe_per_H`를 갖는다. 구간과 초기/최종 시각, mean-volume z, 밀도 단위를 저장한다. ln(a)를 초 단위 함수에 전달하지 않는다. 기존 이력의 시간 좌표가 ln(a)나 z이면 고정 배경의 dt/dln(a)=1/H 또는 dt/dz=−1/[(1+z)H]로 매핑한다.

PR104의 첫 폐쇄는 평균 `ne=Q*(nH+nHe)`, `xe=(1+nHe/nH)*Q`이다. HeII, 외부 중성, residual/HeIII 미포함이라는 원래 가정을 그대로 적는다. 일반 종 분율 입력으로 바꾸는 경우에만 새 폐쇄를 설명한다.

미리보기 CSV가 필요한 정확도를 충족하는지는 새 보간 오차로 판정한다. 전체 RUN002 격자의 DOP853 비교 수치를 thinning한 CSV의 오차 보장으로 복사하지 않는다. preview가 부족하면 필요한 이력 자료만 복구하거나 같은 고정 모델에서 필요한 출력을 만든다. 그때 실제 수행한 추가 계산을 별도로 기록한다.

### 스펙트럼과 광자 대역

첫 B1A는 명시적으로 정의한 등방 초기 스펙트럼을 수송하는 기하 진단이다. CMB형 진단을 선택하면 프로젝트의 고정 배경/상수가 공급하는 초기 T_gamma에 따른 Planck 분포를 쓴다. 공급 위치를 확인할 수 없으면 T를 명시한 무차원 Planck 진단으로 한정하며, 임의 수치를 관측 CMB 예측으로 표현하지 않는다. 에너지 범위와 꼬리 오차를 관측량 목표에 맞춰 정한다.

이 CMB/기하 진단용 스펙트럼과 C에서 쓸 이온화 UV 공급자는 별개다. CMB 광자 moment를 H photoionization/heating 공급자로 재사용하지 않는다. C는 물리적으로 정의된 이온화 대역 광원·흡수·에너지 moment를 따로 사용한다. 기존 10–20 eV 실험 runner의 대역을 자동으로 CMB 또는 전체 ionizing spectrum으로 취급하지 않는다.

### 실행·투영

`GeometryBackground` 시간 어댑터를 공개 특성선과 패킷 상태에 연결한다. 초기 등방 분포·tetrad·각도 convention과 관측 epoch를 고정한다. 패킷의 comoving 수량을 proper volume, ΔE, ΔΩ로 변환해 `I_E`를 구성하고, 광속 및 단위 환산을 포함한다. 이미 패킷에 반영한 Jacobian을 투영에서 다시 적용하지 않는다.

축대칭에서는 μ=cosθ와 명시한 구면조화 정규화로 I20/I00을 계산한다. 표준 FLRW 기준, 실제 Bianchi, **같은 평균 H의 등방 수송**을 분리한다. 마지막 대조군은 동일 ne·광원·초기 스펙트럼·시간 경계에서 방향별 팽창만 제거한 진단이다. 같은 물질 내용의 Einstein-FLRW 해라는 주장은 하지 않는다.

## 3. 작은 실행 행렬과 완료 조건

필수 pilot는 FLRW/zero shear, 고정 PR104 Bianchi 사례, 해당 Bianchi의 같은 H 등방 수송 대조군이다. 작은 ±shear 추가 사례는 선형 응답을 해석하는 데 필요할 때만 넣는다. 유한 shear의 정확 parity나 모든 scalar의 차수를 가정하지 않는다. 격자 refinement는 새 시간/각도/에너지 투영의 관측량 오차를 판정하는 범위에서 한다.

실행 전에 결과 파일의 간단한 metadata에 목표 관측량, 최소 목표 진폭, 10% 출발 수치 예산과 near-zero 절대 floor를 적는다. 별도 계약 PR을 만들 필요는 없다. 검사할 것은 다음이다.

- 입력 시간·배경·proper density 단위 및 이력 보간의 일관성.
- zero shear와 같은 H 대조군의 의도한 극한, intensity/multipole 투영 정규화.
- 패킷의 수량·경계 outflow·팽창에 의한 에너지 변화를 포함한 장부.
- 목표 ΔI 또는 quadrupole의 해상도 비교와 절대 오차. 기존 ray 정리·PHYS35 증명 전부를 반복하지 않는다.

완료 산출물은 실행 코드, 실제 입력/명령, 관측량 표, 방향별 그림, 짧은 결론이다. 그림에는 **collisionless transport diagnostic**을 표시한다. 같은 cosmic-time 경계의 τ는 `∫cσTne dt`로 별도 기록한다. collisionless intensity의 xe 독립성을 해석에서 유지한다. 광학깊이 전체 CMB값, Thomson 산란, 관측 C_ell, 통계적 검출로 승격하지 않는다.

## 4. 이어서 할 일과 막혔을 때의 분기

- B1A 후 B1B: 기존 Thomson 이론/커널의 알려진 위치를 제한적으로 확인하여 연결하거나, 강도가 보존되는 out-scattering+in-scattering 연산자를 구현한다. zero-opacity와 등방 극한, prescribed xe 변화, 새 관측량 수렴을 확인한다. 단순 attenuation만으로 산란을 대신하지 않는다.
- 편광을 구현하면 Stokes convention, screen 기저 운반, 산란 행렬과 물리적 상태 조건을 포함한다. 현재 조사한 PR83 파일에서는 polarized kernel이 `NOT_LOCATED`다. 발견되지 않은 자산의 존재나 부재를 전체 repo에 일반화하지 않는다.
- 편광 구현이 길어지면 B1A intensity 결과를 남기고, 비편광 moment로 가능한 C의 최소 피드백을 병행한다. C에는 A와 B1A가 필요하며 full native나 B1B 편광 완성이 필요하지 않다.
- 현재 환경에 필요한 도구가 실제로 없을 때 그 작업만 로컬 Codex로 넘긴다. NCP는 독립 사례 비용을 측정한 후 선택한다. 이력 하나의 적응 step을 64코어로 나눌 수 있다고 가정하지 않는다.
- native C12/정밀 원자/PHYS36으로 돌아가려면 목표 관측량의 지배 오차와 그 작업이 줄일 오차의 관계를 먼저 제시한다. 단순히 다음 번호라는 이유로 실행하지 않는다.

## 5. 보존할 상태

PHYS35와 이전 증거 파일을 수정하지 않는다. PHYS36은 `DEFERRED_NONBLOCKING / NOT_RUN`이다. PHYS35 first 1/replay 1은 소진 상태이며 이 인계로 재발급되지 않는다. Physical HOLD, [160,161] FAIL, tick160, auxiliary escape FAIL, HH/RCT/CR OFF, precision atomic PARKED와 native C12의 미평가 범위를 유지한다. `Q→xe` 어댑터나 새 수송 결과를 이유로 이 상태를 자동 승격하지 않는다.

이번 계획의 정확한 자산 범위와 출처는 같은 폴더의 `README_KO.md`, `ASSET_REGISTER_KO.md`, `SOURCE_MAP.json`을 따른다. 이후 보고는 관측량과 그림을 먼저 제시하고, 새 가정·수치 오차·남은 한계를 바로 연결해서 설명한다.
