# HE-ANG-FINITEMASS-CBA 저장 결과와 미완료 export

## 실제 실행 상태와 비용

실제 시도는 **PASS, FAIL, FAIL**이다. 첫17계약시험은 통과했고, 최초 분석은 종료코드-9로 중단됐다. 별도 repair는 완료된12generic행과2quadrature사례를 재사용해 최종 ANALYSIS.json을 저장했으나 같은 프로세스의 그림 export가 끝나기 전에 종료코드-9로 끝났다. 두 FAIL은 원문 그대로 유지한다.

| 실제 시도 | 상태 / 종료코드 | CPU s | wall s |
|---|---|---:|---:|
| 01_01_tests | PASS / 0 | 0.301362 | 0.318958372998168 |
| 02_02_analysis | FAIL / -9 | 6.135964 | 6.18461632099934 |
| 03_REPAIR01_COMBINED | FAIL / -9 | 5.445503 | 5.48240422700474 |

새 단위 합계는 CPU 11.882829s / wall 11.9859789210022s다. 원래 상한12CPU/35wall은 그대로다. PR100의4.987974CPU/5.122489414992742wall을 포함한 관측 lineage는 16.870803CPU/17.108468335995wall이며 상한20/60이다. 개별 child CPU 상한 초과 기록은 두 실패 모두 보존한다. 새 repair reserve는1사용/0잔여이고 parent reserve는 이전·초기화하지 않았다. 준비·provider·model·IO와 전체 원격CPU의 미측정값은 UNKNOWN_NOT_ZERO다. 이 합계는 end-to-end 비용 증명이 아니다.

## 저장된 유한 수치 결과

최종 ANALYSIS.json의 고정된 전체 행 수와 PASS flag를 확인했다. 이하 수치는 저장 파일의 관측치다. 독립 C9와 root는 이 유한 수치 근거와 기존 PNG를 scoped 채택했다. 실제 두 프로세스 FAIL과 C8 미완료는 그대로다.

| 항목 | 저장 범위 | 최대 관측 오차 | 고정 기준 |
|---|---|---:|---:|
| Generic binary64 F / plus / minus | 12입력 | 4.2296274872618298e-16 / 4.4638350151382825e-16 / 3.9064860756570901e-16 scaled | 2e-12 |
| mp50–mp80 | 같은12입력 | 6.72911460787351320895276846386028537381254253e-51 scaled | 1e-40 |
| 원 K 적분 | 3사례 × 두항 | 1.35371640520305340394023648214486909249760051e-50 scaled | 1e-35 |
| Tiny transfer | 12입력 | 1.7957084932658487e-15 true relative | 2e-12 |
| 에너지 shell residual | 4질량 | 1.4759244174045172e-15 | 2e-13 |
| 에너지 항등식 residual | 4질량 | 1.474514954580286e-15 | 2e-13 |
| Delta 사상 | 4질량 | 0 | 2e-13 |
| Lab branch shell | 4질량 | 8.3266726846886741e-17 | 2e-13 |
| Flux/delta-state/Jacobi 계수 | 4질량 | 8.3266726846886741e-17 scaled | 5e-13 |

Scaled는 abs(value-reference)/max(1,abs(reference))이다. Tiny는 nonzero mp80 기준의 true relative다. 최대 tiny 오차는 proton질량, transverse Delta=1e-14 사례다. 이들은 고정 fixture 관측이며 전체 입력 공간의 uniform/outward bound 또는 물리 uncertainty가 아니다. 원적분은 두 shifted q 각각에 대한 독립 parabolic K 적분이며 closed-form 미분 재생이 아니다.

| 원적분 사례 | aDelta scaled error | minus_bDelta scaled error |
|---|---:|---:|
| M=1, Delta=[0.3, 0.1, 0.2], k=[0, 0, 0.7] | 1.35371640520305340394023648214486909249760051e-50 | 9.40002073571937579979868957976930960738995716e-51 |
| M=2, Delta=[0.4, 0.2, 0.3], k=[0, 0, 0.6] | 1.01860352288037080992990195409245638662656031e-51 | 6.80950079614045544450355829097173800903665345e-51 |
| M=1836.152673426, Delta=[0.2, 0.1, 0.3], k=[0, 0, 0.8] | 0.0 | 8.22582117415251890799970013418559248688804041e-52 |

표의0.0은 저장된 mp50 관측값이며 원적분의 전역 exact certificate를 뜻하지 않는다.

## 두 양의 root를 가중한 fold

고정M1,E0=1,p_A=P/10,binding=.25의 conditional slice다. 정칙 pair sphere와 독립 h변환의 두 양의 root 합을 비교했다. 각 root에 해당 모형 W를 따로 적용했다. 단위는 a0²/p0³이며 total event sigma가 아니다.

| Gauss order | Sphere integral | Two-root h integral | chart relative difference |
|---:|---:|---:|---:|
| 24 | 2.2489961639443843 | 2.2489961599876627 | 1.7593278638928761e-09 |
| 48 | 2.248996163945002 | 2.2489961639449993 | 1.1847664757357654e-15 |
| 96 | 2.2489961639448635 | 2.2489961639448679 | 1.974610792893064e-15 |

Fine chart 차이는 1.974610792893064e-15, 48→96 refinement 차이는 6.1607856738263591e-14로 두 기준1e-9를 만족한다. Order24의 차이1.759327863892876e-9도 원문 그대로 남기며 fine-grid gate와 구별한다.

## 질량 의존성과 proton–무한질량 비교

Illustration은 E0=250/27.2, Er=5/27.2, q방향3도, oriented k각-180..180도/5도 간격73점이다. Er은 pair-relative energy이며 lab EB가 아니다. 변환은 nominal27.2eV/E_h이고 TDCS 단위는 a0²/(eV sr²)다.

세 모형의 표본 최대는 모두-50도다. M2(synthetic)는0.6501261835732014, proton은0.4562989099081967, 무한질량 parent100은0.45610407121581825다. -50도 proton의 저장 mass-trend 절대차는0.0001948386923784498이고, 저장 per-eV 값으로 계산한 상대차는0.0004271803403532207다. 반올림된 저장량의 연산 순서가 다른 절대차의 끝자리 차이는 새 물리 차이가 아니다.

73표본에서 proton–무한질량 최대 절대차는-35도에서0.0002114639219059078이다. 최대 상대차는130도에서0.0016386688645447268이다. 이들은 표본 모형 차이이며 연속각 극값의 증명·실험자료 재적합·calibrated uncertainty가 아니다.

| M | -50도 finite TDCS (a.u.) | 저장 absolute difference (a0²/(eV sr²)) |
|---:|---:|---:|
| 2 | 17.683432193191077 | 0.19402211235738312 |
| 10 | 13.423604013851575 | 0.037410782234607295 |
| 100 | 12.503849538478891 | 0.0035962794635527157 |
| 1000 | 12.415764135003778 | 0.00035784551226181839 |
| 1836.152673426 | 12.411330349502951 | 0.00019483869237844979 |
| 10000 | 12.407003582253179 | 3.5766367019185452e-05 |
| 100000 | 12.406128016632593 | 3.5764544976537976e-06 |
| 1000000 | 12.406040464977032 | 3.5764363144211002e-07 |

무한질량 기준은 같은 geometry의12.406030737070257a.u.다. 여덟 고정M점의 차이 감소를 관측했으며 이 표만으로 전체각에 대한 수렴률을 주장하지 않는다.

## Prefix 재사용과 보존

실패 partial은42613bytes/SHA256 e493132d5a1bb56112d5fb87890828949b3a0cbacbcffab634c5df67ff1da830이다. Repair는17시험,12generic행,첫2quadrature사례/4항을 재실행하지 않았다. 저장 prefix 값과 직렬화 bytes equality가 true이고 retained prefix SHA256은299fa6b711028b1951f12338754dcf2d1123f8c838575fed4aea41a443f87055다. 원 PLAN은 복원되었고 최종counts는12/3/12/4/3/73/8이다. 원 ANALYSIS_PARTIAL_AT_FAIL과 최종 ANALYSIS_AT_REPAIR_FAIL은 별도 불변 복사로 보존한다.

최종 ANALYSIS.json은136204bytes/SHA256 e62cb595be64728b30f08ccfe5c2a0eb68d941fbb325d8e81aa93251e0e586df다. 결과 CSV는 저장 데이터이며 그림은 새 과학 계산을 호출하지 않는 saved-data 경로다.

## C8 PARTIAL_EXPORT와 주장 경계

PNG는190699bytes/SHA256 d0d75f7e5422ced1b873f3e1c36e6704724357a2511a0d742e3a8b4f15f0c781이며 root와 독립 C9가 실제 시각 검토에서 유효한 scoped illustration으로 확인했다. SVG, FIGURE_METADATA.json, REPAIR01_SUMMARY.json은 없다. 이 미완료 export를 감추거나 같은 프로세스의 FAIL을 PASS로 바꾸지 않는다. C8은 in_progress/PARTIAL_EXPORT다.

R8/C7은 저장된 유한 수치 결과 범위에서 완료했고 독립 C9는 PASS_SCOPED_NUMERICAL_WITH_FAILED_PROCESSES_AND_PARTIAL_EXPORT로 완료했다. Root의 실제 ROOT_ADMISSION은 C8을 OPEN으로 유지하면서 S17/20과 실제 전달 뒤 D19/20의 partial publication을 승인한다. C8을20/20에 포함하지 않는다. 새 실행·export 재시도·다음 연구 단위는 승인되지 않았다.

HE-ANG 전체는 SOURCE_INPUT_PENDING이다. Physical provider/event sigma/physical recoil/HE-X1 empirical correction은 false, 전체완료율은null이다. 유한질량 labelled direct channel의 frozen 수치 근거와 exchange-complete physical provider·정확한3체 asymptotics·물리 uncertainty를 구별한다. 실제 채택 근거는 reviews/C9_REPORT.json과 reviews/ROOT_ADMISSION.json이며 이 결과 문서는 그 범위를 확장하지 않는다.

근거: THEORY_KO.md, FROZEN_CONTRACT.json, CONTRACT_ADDENDUM_01.json, REPAIR_CONTRACT_01.json, results/ANALYSIS.json, results/TEST_REPORT.json, 세 attempt의 START/FINISH, RESOURCE_LEDGER.json, 두 보존 partial과 RESULT_SUMMARY.json.
