# S07 — 물리적 해석과 독립 CAS

## 새로 확보한 정보

이 계산은 측정된 4개 각도에서 허용되는 비음수 짝대칭 다항식들을 하나의 최적 fit으로 고르지 않고, 선언한 유한 모형족 전체의 동일 사건 수용률을 둘러싼다. n=4와 n=8, 끝점 0 여부는 실행 전에 고정했다. ±ERR-S는 통계적 동시 신뢰구간이 아닌 민감도 창이다.

213 MeV의 n=8 CAPS 외부 enclosure는 끝점 자유일 때 약 [0.105262,0.417332], 끝점 0일 때 [0.105262,0.249466]이다. 258 MeV에서는 각각 [0.0613315,0.300073], [0.0613315,0.200458]이다. 같은 4개 측정 각도와 같은 오차 창을 사용해도 측정되지 않은 끝점 조건이 수용률 상한에 큰 영향을 준다는 결과다. 이 숫자를 실제 검출기의 efficiency calibration이나 신뢰수준으로 해석하지 않는다.

330 MeV에서는 n=4 두 가족과 n=8 끝점 0 가족의 outer가 모두 공집합이다. 따라서 그 세 유한 coefficient cone은 선언된 창과 양립하지 않는다. n=8 끝점 자유 가족에는 inner witness가 있으며 HEMISPHERES 약 [0.802884,0.843115], CAPS 약 [0.464673,0.569824]의 outer enclosure를 얻었다. 차수나 창을 사후에 바꾸지 않았다. 데이터 자체의 오류, 반응 부재, 임의 차수의 양의 함수에 대한 no-go를 주장하지 않는다.

## 정규화와 자료 해석

고정한 광자 에너지에서 모든 각도에 공통인 양의 factor K(e)는 분자·분모에서 상쇄된다. 따라서 event/inclusive의 공통 배율을 확정하지 않고도 이 조건부 수용률을 계산할 수 있다. 실제 각도 의존 액체 표적 응답과 편광 법칙, 에너지 적분 내부의 상대 가중치는 이 상쇄로 해결되지 않는다.

Rice1998의 인쇄 p114 Eq5.4는 동일한 두 deuteron에 대해 자체 총단면적 convention을 2πA0로 적는다. p115의 Arends 끝점 0 fit 설명은 후속 저자의 기록이다. Arends1976 원 논문 본문을 직접 읽은 것으로 승격하지 않는다. 공식 EXFOR M0475003 총단면적의 에너지격자와 M0475002 각분포 에너지격자는 다르므로 보간·결합하지 않았다.

## CAS의 실제 범위

새 Wolfram evaluator 1회에서 n=4→8 Bernstein degree elevation, 짝대칭, 전체 적분의 literal residual 21개가 모두 0이었다. endpoint·ratio convex weighting·ratio derivative·common scale·basis partition 등을 포함한 Boolean 8개가 모두 True였다. 정확 제출 코드와 원시 응답을 보존했다. 원격 CPU는 provider 미보고로 null, 클라이언트 왕복 시간은 8.625 s이다. context lookup SERVICE_ERROR와 evaluator PASS를 구분하며 선행 CAS를 재실행하지 않았다.

이 CAS는 상징 항등식을 확인한다. 실험 불확도 모형이나 물리 입력의 완성을 검증하지 않는다. 3개 물리 입력, 전역 physical completion null, L4=false, production=NOT_APPROVED를 유지한다. Local 10/15, Central 28/88, HE delta0.
