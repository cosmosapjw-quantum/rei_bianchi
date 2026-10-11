# C12 source-band 경계 실패와 명시적 재개

최초 전구간 연결은 PILOT02 gen3에서 시작하여 새 macro 36개를 수용했다. 마지막 정상 상태는 C2_FULL001 gen39, t=11419941379473.664 s, 79-state prefix이다. 다음 attempt42의 첫 coarse map은 저장된 50000 eV source-band/cell158 교차 시각 11498309373145.336 s에서 `SOURCE_ENTRY_CELL_MOMENT_DOMAIN`으로 중단됐다. 이 실패에는 native gas/opacity 호출이 없었다. 원래 실패 journal, 정확한 입력, 소스 파일과 마지막 정상 checkpoint는 보존한다.

이 사건은 누락된 hard stop이 아니다. 이 시각은 이미 고정 일정에 정확히 들어 있으며, 저장된 R과 cell edge의 정확한 곱은 source 상한보다 작다. binary64 곱이 50000 eV로 반올림됐다는 이유로 source를 0으로 만들 수 없다. 실제 극미량의 양의 N에 대해 독립 계산된 Q가 aN보다 1 ULP 작아 strict moment cone을 위반했다.

새 arithmetic은 같은 HM12 profile, source band, background 및 원래 N을 유지하고, 양의 offset moments를 이용한다. 셀 [a,b]에서

\[
D=\int(q-a)s(q)\,d\log q\ge0,\qquad
E=\int(b-q)s(q)\,d\log q\ge0,
\]

를 직접 적분하여 가까운 경계에서 Q=aN+D 또는 Q=bN−E를 조립한다. E를 bN−Q의 작은 차이로 얻지 않는다. 역방향 log coordinate에서 양의 exponential basis를 적분하므로 작은 경계 잔여량을 뺄셈으로 소실시키지 않는다. raw Q와의 기존 10⁻¹² 상대 일치 검사 및 aN≤Q≤bN strict 검사를 모두 유지한다. clamp, floor, nextafter, 임의 endpoint 이동은 없다.

첫 lower-face-only 후보는 실제 실패 구간을 통과했지만, 새 후보의 전구간 source-band endpoint 검사에서 upper-face 세 곳을 통과하지 못했다. 해당 후보와 실패 증거를 보존했고, 양쪽 경계 공식을 적용한 최종 후보는 관련 56개 endpoint를 통과했다. 추가로 실제 실패 구간의 16/32 source 적분 비교는 최대 2.92990×10⁻¹⁵, source pairing은 2.31025×10⁻¹⁶이었다. 새 upper-offset basis의 독립 MP80 비교 6건은 최대 5.40719×10⁻¹⁶이었다. 이들은 새 arithmetic에 대한 범위가 제한된 증거이며 전체 evolved history 검증이 아니다.

극미량 endpoint N 자체는 MP80 식과 약 0.001218의 상대 차이를 보였다. 이를 높은 상대 정확도 PASS로 표시하지 않는다. 이 진단은 거의 0인 support width의 conditioning 한계를 드러낸다. 기존 cell별 10⁻¹⁰ 기준은 시간 적분의 지정 order-pair 비교이며 rigorous quadrature bound도 아니다. 이 사건에서 막 태어난 cell의 시간 적분 dN은 endpoint 점값을 impulse로 넣지 않고 정확히 0이었다. 후속 positive-source interval, incident reconstruction, native opacity/heat, gas residual 및 원래 IC 기준 누적 ledger 검사는 실제 continuation에서 계속 적용한다.

`repair/production_v2`는 원래 53개 dependency를 덮어쓰지 않는 새 lane이다. gen39의 9개 배열, 전체 prefix, cursor, kernel history와 출력 기록을 보존하고 source 및 control identity만 명시적으로 전환한다. 기존 초기 output0의 기록과 BEGIN/DONE receipt를 그대로 복사하며 h=0 재평가를 하지 않는다.

실패한 옛 attempt42는 완료된 controller attempt가 아니다. 따라서 `attempts=accepted+rejected`라는 기존 invariant를 훼손하지 않도록 cursor 41/39/2를 유지하되, 외부 실패 비용 1회를 기록하고 완료 attempt cap을 105에서 104로 줄인다. 새 lane의 첫 run-local attempt 번호는 다시 42이지만 물리적 실행 순번은 43이고 source identity가 다르다. 원래 실패를 성공으로 덮어쓰거나 예산을 되돌리는 처리가 아니다. 남은 새 완료 attempt는 63회이다.

최종 후보와 재개 경로의 검토 여부는 `review`의 repair decision을, 실제 실행 여부와 최신 결과는 `STATE.json` 및 새 child의 chunk 결과를 읽는다. 검토만으로 실제 native map 통과를 선언하지 않는다. 원래 65/129 전구간 시간·spectral 수렴 및 과학적 허용은 여전히 별도 의무이다.
