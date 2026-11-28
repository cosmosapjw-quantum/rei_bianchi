# QUARTIC12 독립 검토 — 실제 primary validation

**판정: PASS_VALIDATION_SCOPED. 차단 사항 0, 요청 수정 0.** 실행 전 검토와 같은 단일 비작성자 검토의 연속이다. 고정된 CAS 1회와 saved-only 그림 단계로 진행할 수 있다. 최종 과학 admission은 두 단계의 실제 증거와 최종 해석 검토 뒤에 판단한다.

## 실제 실행과 identity

실제 S05 source commit은 `2f66fbe31e6d52adb19f6701f58c14c67f6ac204`, tree는 `92f2941c65e890eab31adc3043e1cb169abf2e00`다. 실제 S05 ACK, 실행 pin, START, 내부 resource, 전체 subprocess resource의 source identity가 일치한다. pin의 여섯 새 Python·계약·다섯 상속 모듈 hash는 현재 bytes와 같고, 공식 입력과 이전 saved result hash도 그대로다. S05 Dropbox ACK 시각 06:30:35Z가 primary 시작 06:30:49Z에 앞선다. 이전 EXFOR11 degree4 비교 객체는 이전 saved JSON의 정확한 복사이며 재계산되지 않았다.

원시 stderr에는 **7 controls PASS, 0 FAIL, 0 ERROR**, stdout과 TEST_REPORT에는 **단일 campaign·12 cases·132개 저장 정점·12개 nested inclusion 확인**이 기록돼 있다. 정점은 inner66/outer66이다. 실제 공유 행렬군 7개에서 inverse attempts **24,810개**, singular **1,026개**, RHS candidates **71,691개**가 저장됐다. 이 수치는 preexecution 상한과 구분한다.

전체 runner와 기다린 자식의 CPU **4.093938s**, wall **4.132059788s**, peak subprocess RSS **17,812KiB**다. exit0, timeout=false, CPU·wall cap 모두 충족했다. 내부 worker 측정 CPU4.047864266s/wall4.077105496s와 혼용하지 않는다. 외부 orchestration CPU0.008362128s는 별도 범위이며 모델·provider 전체 비용이 아니다. prior receipt와 targeted retry는 없다.

Saved data SHA256: `a8fbe269d3941706a510796963f059d7404f3f4655a6a3163042e85011aa0d45`. 마지막 PARTIAL_PROGRESS는 최종 saved bytes와 동일하다.

## 실제 case와 판별

| 에너지 MeV | Case | Inner 정점 | Outer 정점 |
|---:|---|---:|---:|
| 213 | free_N1 | 8 | 10 |
| 258 | free_N1 | 6 | 4 |
| 330 | free_N1 | 0 | 4 |
| 213 | free_N4 | 10 | 10 |
| 258 | free_N4 | 6 | 4 |
| 330 | free_N4 | 4 | 4 |
| 213 | free_N16 | 10 | 10 |
| 258 | free_N16 | 10 | 8 |
| 330 | free_N16 | 4 | 4 |
| 213 | endpointzero_exact | 4 | 4 |
| 258 | endpointzero_exact | 4 | 4 |
| 330 | endpointzero_exact | 0 | 0 |

330MeV의 N4/N16에는 동일한 실제 inner witness가 있다. 표시용 근삿값은

q(z) ≈ 0.14083830297670927 − 0.3081175124578271 z + 0.752692956161764 z².

저장된 exact certificate의 minimum은 z≈0.2046767609125921에서 **qmin≈0.10930605576155263>0**, D≈0.37734211344623947이다. 네 nominal-angle 값의 저장 포함구간은 모두 원래 sensitivity 창 안에 있다. 특히61°,73°,87°는 각각 경계 가까운 값이며 exact interval이 창을 넘지 않는다. old folded 좌표 a1≈**−0.6118546531850547**은 음수다. 따라서 이 witness는 현재 full nonnegative quartic 가족에 속하면서 EXFOR11의 이전 sufficient coefficient cone 밖에 있다. 이전의 정확히 한정된 EMPTY는 오류로 바꾸지 않는다.

330MeV N1의 inner0/outer4는 이 resolution만으로는 존재 여부를 결정하지 못했다. N4와 N16이 실제 feasible witness를 공급한다. 이들과 달리 endpoint-zero의 outer0은 정확한 endpoint cone와 고정 데이터 창을 만족하는 그 조건부 가족을 배제한다. 이는 더 일반적인 각분포·반응·생산·우주론의 no-go가 아니다.

330MeV N4/N16의 CAPS outer enclosure는 약 [0.5691057691147171, 0.5748029722465772], HEMISPHERES는 [0.8426907819000204, 0.84492143556458]이다. 각각의 실제 최소·최대는 저장된 inner-witness bracket으로 더 좁게 포함된다. 모두 exact fraction이 권위 값이며 여기의 소수는 표시용이다.

258MeV N16에는 여전히 의미 있는 최소값 bracket 폭이 남는다. CAPS 최소는 [0.060675724442147666, 0.06112027086968309], HEMISPHERES 최소는 [0.6183761009029307, 0.6185538316867235]에 포함된다. 이를 정확한 curved-family 극값 또는 보편적 수렴 오차로 표시하면 안 된다.

실제12case 중 EMPTY_PHYSICAL_INTERSECTION은 없었다. 해당 분기는 사전에 정한 manufactured control에서만 검사됐다. FULL=1은 nonempty outer에 대해 표시되며, inner가 없는 case에서 그 값만으로 존재를 주장하지 않는다.

## 검토 범위와 남은 단계

검토자는 실제 로그·saved field·exact witness scalar·source/pin/resource를 읽었다. 독립 saved certificate reader는 원래 primary invocation의 일부로 실행된 증거이며, 검토자가 이를 재실행하거나 별도 optimizer를 만들지 않았다. 새/이전 과학 모듈 import·테스트·캠페인·CAS·그림은 모두 0회다.

Actual CAS, 실제 PNG/SVG와 최종 해석, admission, 중앙 candidate 및 publication ACK/readback 검토가 같은 pass에 남아 있다. 현재 Local **11/16**, Central **28/88**, HE delta0. 물리 입력3개, global physical completion=null, L4=false, production=NOT_APPROVED와 모든 미공급 thermal/binding port는 유지된다.
