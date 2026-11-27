# HE38 최종 독립 과학·수치·그림 검토

**최종 판정: PASS_SCOPED. F1·F2·F3는 모두 닫혔고, 현재 검토 범위에 열린 지적은 없다.** 이 문서는 원래 Jacobi 좌표에서 균일 방향분포를 채택한 유한질량 H1 CI 순간 source, 저장된 독립 raw quadrature, 129개 온도 진단, 새 sharing-only benchmark와 최종 그림을 검토한다. Workflow1.0.0 / approval0.2를 유지한다.

검토자는 /root/he38_independent_review이며 해당 source·이론·kernel·oracle·diagnostic·그림의 저자와 별개다. 이전 이론·코드 검토와 두 interface probe는 THEORY_REVIEW.md, CODE_REVIEW.md, REVIEW.json, REVIEW_CLOSURE.json에 그대로 보존했다. 이번 추가 검토에서는 저장된 파일·코드·receipt와 이미지 두 개만 읽었다. 수치 모델, test suite, IVP, benchmark 또는 render를 새로 실행하지 않았다.

## 1. 독립 raw 적분과 오차 주장

raw_oracle.py는 production의 닫힌 종별 heat/STF 계수나 transfer 평균을 부르지 않는다. Incoming Maxwell/Grad 원정의, original Jacobi inverse-CDF transfer, 각 출력 속도의 mass-weighted dyad를 직접 적분한다. run_oracle.py는 네 raw 결과를 저장한 뒤 production을 import하여 비교한다. 양쪽 numerical path의 분리가 실제 코드에서 확인된다.

COM GH3³와 incoming GL3×azimuth8은 pressure×Grad에 필요한 4차 Gaussian/angular 다항식까지를 다룬다. Outgoing signed-axis6×6은 채택한 등방 Jacobi 법칙의 이차 모멘트 observable에 대한 cubature다. 이를 임의의 differential observable이나 empirical angular distribution에 대한 exactness로 확대하지 않았다.

| 저장된 검증 | 범위와 관측값 |
|---|---|
| Base grid | 2,000 / 20,000 / 200,000K, radial48×transfer32 |
| 사전 지정 refinement | 200,000K 한 점, 72×48 |
| 반응 STF 응답 | 두 incoming species × 두 STF 방향 × 세 output species × 네 grids = 48 tensor blocks |
| 전체 네 grids의 최대 보고된 상대차 | 1.3463789241×10⁻⁹ |
| 고온 refinement를 사용한 세 온도의 최대 STF 상대차 | 5.4811646593×10⁻¹² |
| Frozen gate | scaled 및 nonzero relative 10⁻⁸ |
| 실제 상태 | 최초 attempt 완료, PASS_SCOPED, exit0 |

Raw 계산은 유한 quadrature와 binary64에서 확인한 수치 근거다. 고온 두 grid의 차이를 continuum upper bound로 표현하지 않았고, 세 온도의 검사를 129개 온도 전체의 독립 raw 검증으로 표현하지 않았다. 작은 H+p 합, 구조적 0, event momentum/energy를 별도 정규화한 방식도 실제 관측량의 규모에 맞는다.

저장된 네 NPZ는 모두 receipt SHA256과 일치했다. Parent의 최종 패키지 복원과 원격 저장 검증은 별도 작업이다.

## 2. 129개 온도 진단과 물리 해석

새 FiniteMassModel.evaluate 호출 한 번으로 129개 온도를 평가했다. HE37 저장 CSV는 SHA256 7e6103b1f2a2aca36608e5d2fa99b94d3494ecb52f98377ae2e0b4b29e9ed745로 재사용되었고, 기존 diagnostic이나 provider benchmark는 재실행하지 않았다.

같은 T에서 rate correction은 ζ⁻¹ᐟ²이고, neutral input stress가0일 때 total electron-STF correction은 √ζ다. 저장된 결과의 변화는 각각 +272.123262ppm와 −272.049231ppm이다. 둘을 같은 prefactor로 처리하지 않은 점이 이론과 일치한다. 이 수치는 채택한 모형 내부의 질량비 보정이며 empirical model uncertainty를 뜻하지 않는다.

종별 Q/r의 단위는 eV이고 signed kinetic source다. 양성자의 양수 값은 생성 입자의 energy moment이며, 기존 proton fluid의 독립적인 가열률이나 평형화 속도로 해석하지 않는다. Neutral H 제거와 electron net source를 합하면 전체가 −13.6eV/event가 된다. 진단의 최대 보존 잔차는5.3291×10⁻¹⁵eV다.

작은 H+p 합은 −7.5394meV에서 −21.4657meV까지 변하며 direct combined formula로 저장된다. Figure는 이 값을 두 큰 항의 차감으로 다시 만들지 않는다. STF는 모든 여섯 계수를 저장했고, incoming-e 열에 nH, incoming-H 열에 ne를 곱하는 정규화가 문서화되었다. 교차 계수의 부호 변화와 product-birth 응답은 total-gas scalar relaxation closure와 구별된다.

Diagnostic receipt의7개 output hash, 실행 source hash, saved-parent input hash와 CSV129행/양 끝 온도를 readback했다. 기록은 FINAL_READBACK.json에 있다.

## 3. Sharing-only benchmark의 공정성과 범위

두 경로가 계산하는 출력은 같은129개 온도의 Λ다.

- 압축 경로: 이미 resident인 α,β,θ에 대해 Λ=β−θα.
- 참조 경로: positive relative-energy Laguerre128 × conditional-transfer-CDF Legendre128.
- 양쪽에서 radial input 및 quadrature setup 비용을 제외했다.
- 7개 batch에서 압축식은500회/배치, quadrature는1회/배치로 실행하여 출력129개당 시간으로 환산했다.
- 최대 상대 차이1.9984×10⁻¹⁴, 최고온도192×192로 바꾼 변화2.8866×10⁻¹⁵.

중앙값은 약1.37µs와22.2ms이고, 선택한 참조 경로 대비 시간 비율은 약1.6×10⁴다. 이는 cached-input의 추가 sharing moment 연산에 대한 국소 비교로 적절하다. Provider 전체나 IVP의 speedup, 최선의 모든 수치 적분법에 대한 우위를 주장하지 않는다. 현재 정확도 비교와 비용 표기는 실제 실행 범위에 맞는다.

## 4. 실제 그림 검토와 F3 종료

원본 PNG와 수정 PNG를 각각 실제로 열어 보았다. 최초 저장본의 main suptitle 윗부분은 잘려 있었다. Manual y=1.015를 제거한 수정본에서는 전체 제목이 표시되고, 네 패널의 제목·축·범례·곡선이 저장된 수치와 일치한다.

| 패널 | 검토 결과 |
|---|---|
| (a) 종별 kinetic energy/event | eV 단위, H 제거 음수·proton 생성 양수, 총합 −13.6eV 표기가 일치 |
| (b) 작은 finite-mass shift | meV 단위와 electron/heavy 반대 부호가 일치, direct small-combination 사용 |
| (c) Incoming electron STF | M_s,e/α의 부호와 범위가 CSV와 일치 |
| (d) Incoming neutral-H STF | M_s,H/α의 부호 변화와 proton birth 응답이 일치 |

최종 설계는180mm×150mm, PNG300dpi와 SVG 한 쌍이다. Temperature는 log x축, 아래 두 패널은 symlog y축이며 이중 축이 없다. 이 검토는 전달된180mm 설계에 대한 것이며90mm 판형의 별도 가독성 검증을 주장하지 않는다.

**F3 CLOSED.** 최종 PNG:
ee6291275bb24ed76989adc89add7747a7b72b77db214ce6dfd40ea2a0c243c7

최종 SVG:
7b2cd735cdc6ee8db7a446d528411a7c2f16af519f1f8144f125a837433ede03

원본과 수정본의 CSV/metrics 입력 hash는 동일하다. 둘 다 새 model evaluation0이다. 논리적 신규 figure pair는1개이고, 실제 render attempt는원본1+수정1이다. 최초 warning은 environment note에 보존되었고, 수정 renderer는 writable temporary Matplotlib cache 및 stdout/stderr capture를 명시했다. 원본 render/script/receipt는 유지되었다.

## 5. F2 재현 경로 종료

원래 실행 runner의 /tmp/he38_implementation 경로와 launcher의 attempt_001은 해당 실행의 역사적 identity로 남겼다. 별도 portable launcher/runner가 implementation root, output root와 attempt 이름을 인자로 받는다. Existing attempt를 거부하고 exclusive reservation, CPU30s/address-space512MiB/one-thread/wall90s 제한과 실패 보존을 유지한다.

원래 실행 source·contract·receipt15파일의 hash를 확인했고, portable runner의 세 scientific loop는 원본과 AST가 같았다. 새 entry는 PREPARED_NOT_SCIENCE_EXECUTED이며, compile/help/static 검토만 수행했다. 완료 결과를 복원·읽을 때 재실행하지 않는다는 handoff도 명확하다. Diagnostic과 renderer 역시 명시 path argument를 받아 복원 단원에 연결할 수 있다.

**F2 CLOSED.** 이 판정은 portability boundary의 준비를 승인한다. 실행되지 않은 새 entry를 별도의 성공 과학 실행으로 세지 않는다.

## 6. 실제 비용과 최종 수용

| 실행 근거 | 기록된 CPU | 집계 주의 |
|---|---:|---|
| 독립 raw oracle launcher child 전체 | 5.977551s | 내부 runner timer5.135024s와 더하지 않음 |
| 새 diagnostic 및 sharing benchmark | 0.942977s |129T API 평가1회와 timing batches를 포함 |
| 최초 render | 8.785669s | title clipping이 있는 원본도 실제 비용에 포함 |
| 수정 render | 7.549285s | 같은 saved data, 새 model evaluation0 |

이번 최종 reviewer의 추가 과학 실행은0이다. 앞선 reviewer의 두 interface probes는 별도 PROBE_RESULT.json에 보존된 기존 실행이다. F1은 REVIEW_CLOSURE.json에서 닫혔으며 이번 최종 검토에서는 같은 검사를 반복하지 않았다.

현재 수용 범위는 선언한 finite-mass instantaneous source와 위 수치·그림·재현 근거다. Final20stage archive ACK, Git remote readback, science manifest와 최종 handoff의 일관성은 parent의 남은 delivery 검증 대상이며, 이 문서가 그 완료를 주장하지 않는다. 추가 과학 테스트나 그림 수정이 필요한 열린 finding이 없으므로 이 검토를 종료한다.
