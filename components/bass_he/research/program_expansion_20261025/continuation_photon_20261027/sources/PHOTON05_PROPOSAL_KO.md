# 다음 HE 물리 leaf 제안: PHOTON05

**선택:** 실제 EXFOR M0475002의 12개 입사 에너지·CM 각도 행에, 정지한 bare alpha + photon → 두 bare ground-state deuteron의 정확한 상대론적 두 입자 운동학을 연결한다. Root가 이 범위를 선택했으며 식 유도와 최종 계약을 작성한다.

## 실제 새 입력과 재사용

NIST 2022 CODATA의 공식 `allascii.txt`를 원문 그대로 확보했다. `NIST_CODATA_2022_allascii.txt`는 40,801 bytes, SHA256 `77fb90e66c40db3e6eb16630bc9c88e4c7c8beddbe5e71be406f2f26e3f67e67`이다. 원문 중앙값은 alpha rest energy **3727.3794118 MeV**, 인쇄 불확도 **0.0000012 MeV**; deuteron rest energy **1875.61294500 MeV**, 인쇄 불확도 **0.00000058 MeV**다. 질량은 측정값이며, “정확한”은 이 선택된 입력에 조건부인 운동학의 의미다. 질량 공분산을 추정하지 않는다.

공식 EXFOR 원전은 `IAEA-NDS/exfor_master@939a14d7bba1ddce51975cb5e8711ce96b3b0871/exforall/M04/M0475.x4`다. 기존 WU R3 packet의 bytes/SHA와 원행 위치를 재사용한다. 새 compiler나 과학 검사를 실행하지 않았다. M0475002는 **213/258/330 MeV × 46/61/73/87°**의 TABLE 12행이며, `DATA-CM`과 `ERR-S` 단위는 NB/SR다. `ERR-S`는 통계오차로만 기록되어 있다.

## 닫을 수 있는 최소 과학 주장

실제 source의 에너지·각도 좌표를 입력으로 받아 photon의 운동량, 두 딸핵의 유한질량과 rest-mass defect를 함께 포함한 CM→lab 에너지·운동량 사상을 계산한다. φ=0은 명시적 대표 평면으로 둔다. 두 딸핵은 수학적 ± label 또는 순서 없는 쌍으로 표현하며 실험 detector-arm label을 주장하지 않는다. EVENT03의 두 massive 비상대론적 반응물·constant compositional mass 범위와 다른 실제 연결이다.

Photon 손실, population rest-energy 변화와 material kinetic energy를 하나의 사건 원장에 둔다. Mass defect를 별도 binding RHS로 다시 더하지 않는다. 물질 핵의 개수 +1과 thermal particle count·Cv를 구분하고, species heating·deposition·thermalization은 consumer가 정해질 때까지 미할당으로 둔다.

## 측정량과 모델의 연결에서 남는 항목

입사원은 reaction-particle-tagged bremsstrahlung이고, 두 D가 coincidence/TOF로 검출되며 표적은 액체 He다. `EN`은 lab frame의 목록값이다. 선택 entry에는 bin/mean 폭, response, angular acceptance, polarization, azimuth, full/half-sphere 정규화, particle/event 계수와 detector-arm label의 완전한 정의가 없다. 이 항목들은 자료에 없다고 일반화하지 않고 현재 packet에서 미결속인 것으로 둔다.

Bare nuclear mass 입력과 액체 He의 전자 spectator·atomic binding·ionization·target motion 사이의 실험 사영도 열린다. 따라서 native DCS와 ERR-S는 원값으로 보존하고, 이번 운동학에 사건률 가중치를 붙이거나 임의 1/2·factorial, 각도 보간·전구 적분, polarization law를 만들지 않는다.

## 다른 두 후보

| 후보 | 실제 확보 입력 | 이번 선택과의 관계 |
|---|---|---|
| HD 19-state/171-edge operator | STATE04 raw EMAA 및 native1005K 전체 하향 행, level energies·weights | 다음 scalar population/energy 확장으로 가능하다. WU R5 general-N 조건부 이론을 재사용하고 서로 다른 pH2 수치 예제는 복사하지 않는다. 각분포·종별 heat/momentum은 추가되지 않는다. |
| GL2022 reactive supplement | 원 논문이 전체 reactive state-to-state rate set의 supplement 위치를 명시 | 기존 endpoint403 및 이번 numeric bytes 미회수는 접근 상태다. 데이터 부재라는 결론을 만들지 않는다. 실제 입력 취득 후 별도 state/energy/angular 연결이 필요하다. |

자세한 literal 질량·12개 원행·출처·접근 결과·R5 observer 기록은 `PHOTON05_SOURCE_OBSERVATIONS.json`에 있다. 과학식 평가, 테스트, plot, compiler, archive, publication 실행은 모두 0회다.
