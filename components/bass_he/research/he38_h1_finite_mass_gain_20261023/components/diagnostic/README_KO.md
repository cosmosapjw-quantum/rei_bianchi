# HE38 유한질량 진단·공유 에너지 압축

Workflow1.0.0 / approval0.2. 저장된 HE37 radial129행의 SHA256을 확인하여 재사용하고, 새 `FiniteMassModel.evaluate(T)`를 한 번 호출한 결과다. 기존 diagnostic·provider benchmark·science suite·IVP를 재실행하지 않았다. 새 API 내부의 원본 donor 호출은 새 finite-mass 평가의 의존성으로 기록했다.

## 결과

물리 질량에서 eta=0.0005440244515373176, zeta=0.9994559755484628이다. 같은 온도의 HE37 대비 반응률은 정확한 상수 zeta^(−1/2)=1.000272123262085로, +272.123262 ppm 변한다. 입력 H 응력이0일 때 전체 STF 계수는 sqrt(zeta)=0.9997279507688392로, −272.049231 ppm 변한다.

| 온도(K) | 전자 Q/r(eV) | H 제거 Q/r(eV) | 양성자 생성 Q/r(eV) | H+p Q/r(eV) | 첫 Jacobi 가용에너지 분율 |
|---:|---:|---:|---:|---:|---:|
| 2,000 | −13.592460625 | −0.265963347 | +0.258423972 | −0.007539375 | 0.506109486 |
| 20,000 | −13.591194766 | −2.592903484 | +2.584098250 | −0.008805234 | 0.547929049 |
| 200,000 | −13.578534262 | −25.858786090 | +25.837320352 | −0.021465738 | 0.697018704 |

두 번째 Jacobi 분율은 각각 첫 분율의 여수이다. 이는 사건률로 가중한 평균 가용에너지의 분할이다. 양성자의 양의 값은 생성 입자의 kinetic-moment source이고, H 값은 제거 입자의 source다. 공통 T/bulk를 전제한 순간 source이며 이 표로 열적 평형화 속도를 정하지 않는다. Heat의 총합은 사건마다 −13.6eV다. CSV/NPZ에는 전자/H 입력별 모든6개 종별 STF 계수와 density-factor 제거 정규화를 함께 저장했다.

## 새 압축 benchmark

같은129개 온도에서 Lambda=beta−theta*alpha를, 원전 조건부 transfer의 CDF 좌표와 상대 excess energy를 실제로 적분하는 양의2차원 quadrature와 비교했다. Laguerre128×Legendre128의 최대 상대 차이는1.9984e−14이며, 가장 뜨거운 점의192×192 비교 변화는2.8866e−15다. 준비된 동일 radial inputs와 quadrature setup을 양쪽 timing에서 제외했다.

7개 timing batch의129출력당 중앙값은 압축식1.368804µs, 수치 적분22.206737ms로 비율16223.46이다. 이는 **cached-input sharing moment만의 연산 비교**다. Provider 전체 평가나 IVP 성능 향상으로 환산하지 않는다. 정확한 모든 timing sample, 반복 수, 계산식, 입력과 출력 hash는 `BENCHMARK.json`, `RESULT.json`, 실행 script copy에 있다.

## 실행과 파일

실제 진단은 CPU0.943초, peak RSS83,392KiB로 완료되었다. `LATEST_ATTEMPT.json`이 유일한 완료 diagnostic attempt를 가리키고, 그 안의 `LATEST_RENDER.json`이 최종 그림 한 쌍을 가리킨다. 원본 PNG/SVG render는 독립 actual view에서 제목 clipping이 확인되어 그대로 보존했고, manual title y만 제거한 correction render를 동일 saved input에서 수행했다. 그림 교정에는 새 모델 평가가 없다. 최종 실제 view 판정은 독립 review 기록을 따른다.

Portable 실행 예:

```sh
python components/diagnostic/run_diagnostic.py --unit-root . --implementation-root components/finite_mass --parent-csv components/diagnostic/reused/h1_gain_moments.csv
python components/diagnostic/render_diagnostic.py --attempt components/diagnostic/attempts/attempt_TIMESTAMP
```

`--implementation-root`는 `h1_finite_mass` package를 포함하는 실제 디렉터리로 지정한다. 코드에는 고정된 `/tmp` import가 없다. 실행마다 새 timestamp attempt를 만들고 기존 payload를 덮어쓰지 않는다. 이미 완료된 이번 결과를 채택할 때는 재실행할 필요가 없다.

그림 설계·정규화·해석은 `PLOT_DESIGN.md`, 원본 parent input은 `reused/h1_gain_moments.csv`에 있다. 이 구성물의 최종 연구 단원 통합·독립 판정·게시·백업은 parent가 소유한다.
