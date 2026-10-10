# REI-PHYSINPUT-01 독립 판정

**판정: `PROMOTE_SCOPED`. 전역 과학 admission은 `HOLD`, 기존 production `PhysicalHistory`는 계속 blocked다.** 후보 생성·초기 검증 설계·구현을 수행하지 않은 별도 reviewer `/root/decision_review`가 실제 코드와 원 증거를 열람했다. 사용자 지정 Astra v4 하네스를 적용한 검토이며 실제 runtime 모델 identity는 독립 관측하지 못했다. 기준 commit은 `17bd1cc0ce1484ee61cac60ab1bda207ae264381`; 검토한 고정 파일의 SHA-256·크기는 `independent_review.json`에 있다.

승격 범위는 HM12 원저자 source에 연결된 조건부 초기값 문제다. Einstein dust+Λ LRS Bianchi-I 배경, 초기 volume-redshift 5.807, shear ratio 0.001, 초기 50,000 K, homogeneous primary-only H/He와 Case-A energy escape를 선택한다. 초기 momentum support는 10–50,000 eV, 실행 구간은 proper elapsed time 0–10¹¹ s다. 온도·shear·closure는 선택한 모델 가정이지 관측에서 확정된 값이나 REC history가 아니다.

## 원래 blocker에 대한 판정

| 누락 항목 | 독립 판정 |
|---|---|
| 실제 background/time map | 선택한 Einstein 모델에서 해소. 비상수 배경·정규화 밀도·proper-time 사상·방향별 characteristic 구현과 검산이 존재한다. |
| 정상화 IC | 선택한 warm parcel에서 해소. source-bound photon IC와 charge-neutral fixed-temperature ionization-equilibrium root를 실제 계산했다. |
| photon/source history | 선택한 모델에서 해소. UVB는 최초 IC에만 사용하고 실제 emissivity source와 같은 stage의 opacity로 photons를 진화시킨다. |
| closure 선택 | 조건부 선택 자체는 완료. 정확도·전역 유효성은 미확정이다. |
| production physical admission | 미해소. 기존 contract는 모든 metadata가 있어도 `PhysicalExecutionNotImplemented`이며 선택한 escape closure를 기존 diffuse/OTS enum과 동일시할 수 없다. |

이 후보는 잔차를 맞추기 위해 source를 역산한 manufactured solution이 아니다. 원 source bytes와 독립적으로 정한 Cauchy state를 이용한 forward solve다. 그러나 이것만으로 본래 production blocker가 전부 해소되었다고 보고해서는 안 된다.

## 검토 근거

배경의 Einstein constraint·shear scaling·volume solution, 전하중성 root의 유일성, null characteristic의 부호, proper/reference-volume 및 cgs/SI 변환을 검토했다. 고정 초기 momentum 좌표에서 source에 곱한 R⁻³은 현재 각도 Jacobian과 reference volume을 함께 반영하는 올바른 인자다. 실제 native consumer는 기존 원자 RHS·cross-section·AXI coupling을 호출하며, 한 흡수 사건을 photon sink·ionization·binding·thermal ledger에 일관되게 배분한다. 이 고정 범위에서 blocking 유도·구현 오류는 발견하지 않았다.

실행 증거에서 HM12 intake 10개, native consumer 6개, 기존 영향 범위 Rust 테스트 27개가 통과했다. 원 production Rust 파일은 base에 비해 변경되지 않았다. 11개 실제 history를 열람했으며, 활성 확장 band의 DOP853–RK4 최대 상대차는 5.234×10⁻¹², joint energy/angle refinement 최대차는 3.129×10⁻⁷이다. 모든 실행에서 energy ledger 최대 scaled 잔차는 2.276×10⁻¹⁵, active-photon number 잔차는 1.840×10⁻¹⁴다. 초기 전하중성, fraction domain, photon positivity와 원래 FT03 온도 guard도 유지되었다.

이 비교는 독립 원자물리 검증이 아니다. 두 시간적분법이 같은 rates/parser를 공유하고, spectral refinement는 초기 equilibrium의 구적도 바꾼다. 짧은 구간에서 시간 차이가 roundoff 수준이므로 측정된 적분 차수나 전역 continuum certificate를 주장할 수 없다. Fraction 합 1은 제거한 neutral fraction의 구조적 항등식이며 별도 conservation 측정으로 세지 않았다.

## 검토 중 반영된 수정과 중요한 잔여 오차

최초 200 eV 상한은 native 지원 범위 안에서 초기 He II photoionization의 8.576%, primary heating의 53.945%를 누락했다. 단순 ledger 통과는 이 잘림을 정당화하지 못한다. Owner는 원 실행을 보존하고 상한을 50 keV로 확장하여 재실행했다. 정규화 초기 He III fraction이 0.02786955에서 0.02986128로 바뀌었으므로 실제 입력에 영향을 주는 수정이다.

문서의 escape-photon count 주장도 수정되었다. 현재 모델은 재결합 방출의 총에너지만 escape ledger에 기록하며, 방출 photon 수·spectrum은 결정하지 않는다. Absolute-comoving count와 초기 proper-reference count의 관계도 명시했고, 계약의 활성 band 필드를 실제 확장 실행과 맞췄다. 이 범위에 열린 blocking finding은 없다.

다음 물리 gate는 여전히 열린다. 50 keV 위 반응율·heating은 원자 provider 범위 밖이고, secondary/Compton·diffuse 재흡수·기타 cooling·fit 오차를 인증하지 않았다. 차가운 평균 IGM에는 30,000 K 아래 원자/열 provider와 별도 REC 또는 물리 IC가 필요하다. HM12 source를 Bianchi volume-redshift에 붙이는 가정과 test-field 배경의 적절성도 대상 연구에서 판단해야 한다. 장기 history·관측량·기존 F04/F08 엄격 gate는 미실행이다.

따라서 현재 산출물의 연구 보고·보존 및 명시적인 conditional production integration으로의 진행을 승인한다. 이미 닫힌 국소 검증을 추가 반복하지 말고, 다음 작업은 별도 provider/contract 연결 또는 선택한 물리 gate 하나로 한정한다. 이 판정은 push/merge 권한이나 전역 과학 승인을 새로 부여하는 문서가 아니다.
