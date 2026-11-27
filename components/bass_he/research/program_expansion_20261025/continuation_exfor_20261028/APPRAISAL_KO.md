# S08 — 저장 결과 시각화와 주장 범위 평가

그림은 검증이 저장한 SAVED_PLOT_DATA.json만 읽어 PNG/SVG로 각각 한 번 저장했다. 입력 SHA-256은 5a13b55d1e8f9a0960cddb7c8c06ae08fcb6212425d71642e41d5a311a9b2243이다. 과학 module import 0, 재계산 호출 0, 재시도 0이다. 실행 코드는 바뀌지 않은 S05 pin을 유지한다.

전체 plot subprocess CPU 2.353290 s, wall 2.373904069 s, peak RSS 78,536 KiB로 CPU10 s / wall30 s / AS768 MiB 계약을 통과했다. stderr는 비어 있다. 내부 CPU 2.307750 s는 전체 측정에 포함되므로 더하지 않는다.

그림의 상단은 공식 12 DCS 점과 ERR-S, 하단은 각 에너지·차수·끝점 선택의 HEMISPHERES/CAPS 수용률 enclosure이다. 색 선은 outer, 검정 선은 inner 가족의 기하 enclosure다. 둘은 표시 해상도에서 거의 겹치지만 유리수값은 별도로 보존하며 동일한 exact set이라고 하지 않는다. 330 MeV의 공집합 가족은 실제 null 결과를 'empty outer family'로 표시한다.

Root가 실제 PNG를 열어 12점·모든 모형 행·빈 가족·축·단위·주석이 식별됨을 확인했다. 330 MeV 패널의 첫째/마지막 empty 문구가 축 경계에 닿지만 읽을 수 있고 수치를 가리지 않는다. 계산이나 추가 렌더링이 필요한 과학 결함으로 보지 않는다.

## 평가

새 기여는 실제 sparse DCS를 이용하는 양의 finite-family certificate와 조건부 검출 수용률이다. 두 endpoint 선택의 차이는 측정되지 않은 영역의 외삽 가정을 드러낸다. 이 결과로 실제 full angular/polarization law, event normalization, photon history 또는 열화 입력이 확보된 것은 아니다.

ERR-S window를 서로 독립인 확률 오차로 가정하지 않는다. 선택한 직교 부등식 제약은 통계적 독립성이나 신뢰구간 coverage를 뜻하지 않는다. degree4/8 coefficient-positive cone 바깥의 양의 함수에 관한 결론도 없다.

Strong no-go 대상이 아닌 유한 모형/창 판정으로 남긴다. 앞선 KINEMATIC08 및 PHOTON05 workflow PARTIAL과 HARMONIC10 최초 실패/targeted PASS 이력을 보존한다. 완료된 과학·CAS·그림·백업의 재실행은 하지 않는다.

S08 Local 10/15, Central 28/88, HE delta0. 새 노드의 admission은 동일 독립 심사의 최종 과학 판단 뒤에만 갱신한다.
