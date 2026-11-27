# BASS_HE EOR_C0 실행 기록

## 판정

CONTRACT_READY_FOR_THEORY__PHYSICAL_DOMAIN_BLOCKED.

첫 EOR DAG node의 반응/질량/단위/오차/source 계약과 실행 가능한 검사기, 제한 대수/산술 시험을 만들었다. 전체 C0 물리 적용영역 동결은 완료하지 않았다. 실제 T/n/조성/기간/분포/E/R/b/tail, 관측량 절대오차 및 승인된 수치 source는 미확인이다. 제조 fixture로 대신하지 않았다.

## 결정과 근거

- 직접 NR_CX/R_CX/ION, 조건부 EXC/reverse NR/elastic moments, 기존 receiver의 PI/EI/RR/DR를 포함하여 반응 16개를 명시했다. imported baseline 표시는 새 numerical source admission이 아니다.
- West, Lane & Cohen (1982), DOI 10.1103/PhysRevA.26.3164의 primary abstract는 4He2++H(1s)의 0.1–1000 eV CM 방사성 전하교환을 다루며 저에너지에서 방사 기여의 중요성을 보고한다. 원 수치표나 inclusive final-state sum을 이번에 회수한 것은 아니다. R_CX는 별도 외부 provider 또는 소비기 가중 제외 상한을 요구하며 비방사 Coulomb solver에서 자동 생성하지 않는다.
- NR/R CX는 화학량론(-1,+1,0,+1,-1,0), 직접 ionization은(-1,+1,0,0,0,+1)이다. 종 순서는 HI,HII,HeI,HeII,HeIII,e. 전자 증분은 각각0/0/1이며 photon-primary absorption ledger와 분리한다.
- NIST CODATA2022 alpha mass/u=4.001506179129, NIST 1H mass/u=1.00782503223을 입사 translational kinematics에 핀했다. physical-mass-u convention의 E_cm/epsilon=mu/u=0.8050611795851188. 정수4:1 계수0.8과 상대 차이는 약0.62867%다. 원자료 per-u 정의가 actual mass인지 mass number인지 먼저 확인하며 부모 electronic Hamiltonian을 변경하지 않는다.
- reference engineering rate budget은 atol+1e-3*preregistered_scale, 분배 .5/.2/.2/.1이다. 달성 정확도나 cosmological tolerance가 아니다. source/model uncertainty는 별도다.
- absolute response budget에는 양성 비교 propagator의 모든 성분을 포함했다. A=[[0,1],[0,0]], b=[0,1]에서 직접 첫 source=0이지만 response=(t^2/2,t)여서 성분 간 전달을 버릴 수 없다. Xi의 실제 유효 bound는 별도 consumer 입력이다.
- R2-N 및 R2-T 전체 reference 보고서를 새로 회수했다. R1 G7의 후속 O(S^2) 수정과 R2-T kinematic-only/thermal-bulk OPEN 범위를 보존한다. 과거 PASS를 현재 runtime 재실행 PASS로 상속하지 않았다.

## 구현과 실제 검증

stdlib Python checker는 명시적 energy conversion, 조건부 tail coverage, tolerance allocation, parent/gate/source/owner audit, durable create-only JSON과 CLI를 구현한다. 이것은 미래 full cross_sections/rate/network API가 아니다.

최종 53 tests passed. 최초46개 missing-behavior red와 추가6개 negative-behavior red를 보존했다. CLI 시험은 구현 후 작성했다. 첫 green 시도의 잘못 전사한 test oracle은 Decimal60자리/Wolfram40자리로 교정했고 생산 식을 바꾸거나 tolerance를 완화하지 않았다. CAS warning과 clean reformulation도 구별한다.

구조검사 exit0, 물리검사 exit2/physical_ready=false, 중복 output 생성 exit2. 분자 solve, 단면적/physical rate, cosmological history, 새 MPI/NCP benchmark, 독립 심사는 실행하지 않았다. 이번 계약 작업에는 hot loop가 없어 Fortran kernel을 변경하지 않았다. binary64/no-fast-math/no-reassociation/explicit backend 정책은 보존한다.

## 기계판독 상태

```json
{
  "node": "EOR_C0",
  "whole_C0_complete": false,
  "theory_contract_ready": true,
  "physical_ready": false,
  "scientific_PROMOTE": "HOLD",
  "full_C2_closed": false,
  "continuum_certificate": false,
  "full_H_gap_certificate": false,
  "atomic_correlation_established": false,
  "Eq55": "NOT_RUN",
  "production_default_change": "NOT_AUTHORIZED",
  "tests_passed": 53,
  "physical_rates_computed": 0,
  "next_single_theory_node": "EOR_T1_SELECTED_STATE_AND_OBSERVABLE_ERROR_CONTRACT"
}
```

원16-node DAG의 requires는 그대로이며 C0→T1/T2/T4 이론 edge는 theory_contract_ready 산출물을 소비한다는 typed-readiness를 명시했다. 전체 C0 physical binding은 OPEN이고 물리 launch 의존성은 닫지 않았다.

## 전체 실행/근거 패키지

BASS_HE_EOR_C0_CONTRACT_LOCK_20261002_v1.zip

- bytes: 121289
- SHA256: 19e38c8935456e3063f450bd5c6bb060d494466655a9f16c82fabce2b878682b
- 73 files; 72 manifest payload hashes and ZIP CRC verified locally.
- Drive object: 1ITzAkJ8TZqCybQid8n3s-du2G4SAUy8d, upload success + size121289 observed.
- Dropbox object: id:BSpOijBcT10AAAAAADxlEw, /BASS_DERIVATION_DOSSIERS_20260912/BASS_HE_EOR_C0_CONTRACT_LOCK_20261002_v1.zip, completed + size121289 observed.
- Library archive: libfile_f5179c0640dc819186f295bbcd4a14c9.

전체 코드·계약·시험·유도·원 receiver 보고서와 실패 근거는 SHA-bound ZIP에 있다. 이 public namespace는 상태·결정·검증·배포 기록만 게시하며 전체 runtime source를 개별 Git 파일로 모두 게시했다는 뜻이 아니다. Raw copyrighted papers는 배포하지 않는다. Cloud RESTORE_VERIFIED는 주장하지 않는다.
