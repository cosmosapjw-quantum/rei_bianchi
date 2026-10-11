# Q1A 고정-q Gauss 연구 보고서 초안

**상태: GAUSS2_FINE 종료 전 초안.** 아래의 G1 결과와 독립 판정은 실제 저장된 증거이며, G2의 최종 결과·전구간 비교·최종 checkpoint는 아직 비어 있다. G2의 완료 시각이나 최종 보존오차를 예측하지 않는다. 기존 RUN002·EVENT003·Q0의 계산을 반복한 횟수는 0이다.

현재까지 새 G1 계산은 평균 적색편이 \(15.9\to4\) 전구간을 계산했지만 photon-number 보존 기준을 통과하지 못했다. 더 엄격한 G1 시간분해 계산은 마지막 구간에 도달하기 전 BDF 최소 step 실패로 중단되어, 새 격자의 전구간 시간수렴을 인증할 수 없다. 이와 별개로, 저장된 source 비교에 대한 삼각부등식만으로도 선택된 G1/G2 쌍의 129개 시점 source spectral 기준 불통과가 이미 확정된다. 이 사실은 진화된 이온·온도·Gamma 오차의 크기를 예측하는 근거가 아니다.

## 고정한 물리와 판정 기준

이번 변경은 같은 고정 covector \(q,\mu_0\)에 양의 composite Gauss quadrature를 적용한 수치 변경이다. 초기 UVB native knots와 지정된 다섯 시점의 source/threshold trajectory를 합쳐 384개 공통 log-q 패널을 정했다. Gauss 1차/2차에 각각 384/768개 energy nodes, 각도 2개를 사용했다. 동일한 노드와 가중치가 IC·source·photon·gas·heat·counter에 들어간다.

물리 범위는 비틸트 FLRW 극한에서의 prescribed dust+Lambda 배경, source-pinned HM12 초기 UVB와 실제 emissivity RHS, 물리 에너지 10–50000 eV source, 초기 \(T=20\,\mathrm K\), \(x_{\mathrm{HII}}=2\times10^{-4}\), 초기 중성 He, 기존 primary H/He Case-A 원자물리와 prescribed isotropic CMB bath다. CR/RCT·secondary cascade·diffuse 재흡수·stress backreaction을 추가하지 않았다. 적색편이는 평균 체적 적색편이이며 방향별 관측 적색편이가 아니다.

| 판정량 | 유지한 허용 기준 |
|---|---:|
| 전구간 에너지 ledger / 초기 총에너지 | \(10^{-9}\) |
| 전구간 photon-number ledger / 초기 \(n_H\) | \(10^{-9}\) |
| 같은 격자의 시간분해 field 차이 | \(2\times10^{-6}\) |
| spectral/angular field·source·radiation·heat 차이 | \(10^{-3}\) |
| geometry identity | \(10^{-11}\) |
| photon positivity·gas domain | 기존 엄격 기준, clipping 없음 |

Spectral/time 비교의 분모는 해당 공통 시점 집합에서 fine history의 최대 진폭이다. 129개와 65개 시점 집합은 별도로 보고해야 한다. Ledger는 저장 시점과 기록된 segment endpoint 양쪽의 최댓값을 포함한다. 후속 설계에서 제안하는 더 작은 local engineering 목표는 이 전구간 기준을 대체하지 않는다.

## 실제로 종료된 계산

| 항목 | GAUSS1_FINE | GAUSS1_TIGHT |
|---|---:|---:|
| 요청 rtol | \(10^{-11}\) | \(3\times10^{-12}\) |
| 완료 segment | 388 / 388 | 367 / 388 |
| 저장 시점 | 129 / 129 | 112 / 129 |
| 전구간 종료 | 예, \(z=4\) | 아니오 |
| elapsed | 1795.163 s | 2034.389 s |
| RHS / Jacobian 호출 | 405935 / 3728 | 457207 / 3258 |
| 에너지 ledger 최댓값 | \(1.0815828185\times10^{-10}\) | \(1.1338182762\times10^{-10}\), prefix만 |
| photon-number ledger 최댓값 | **\(3.5288241094\times10^{-9}\), FAIL** | \(5.9132873954\times10^{-10}\), prefix만 |
| 실제 accepted domain·photon positivity | 기록상 충족 | 실행된 prefix에서 기록상 충족 |

G1_FINE의 전구간 에너지·domain·positivity, 실제 source/native/grid identity와 저장 epoch 구조는 `review/G1_FINE_SAVED_AUDIT.json`에서 독립 확인되었다. 다만 number 오차는 허용 기준의 약 3.53배이므로 이 계산을 보존 조건을 만족한 history로 승격할 수 없다. Local native algebraic cancellation이 roundoff 수준이라는 사실은 시간적분으로 누적된 전구간 ledger 실패를 취소하지 않는다.

G1_TIGHT의 마지막 accepted 정규화 시간은 \(u=0.8677276379189706\)이다. 실제 실패 메시지는 `Required step size is less than spacing between numbers.`이다. `review/G1_TIGHT_FAILURE_REVIEW.json`은 이를 **수치 solver step-size floor**로 분류했다. 저장된 accepted 상태에 물리적 domain 실패는 보고되지 않았다. 실패 segment의 폭은 약 \(1.17\times10^{13}\) time ulp이므로, 단순히 서로 거의 겹친 event 경계가 원인이라는 설명은 현재 증거와 맞지 않는다.

해당 segment 시작에 새 50-keV source-entry node가 활성화되었지만, 그 사실만으로 원인을 확정할 수 없다. 새 node scaling·절대오차 제약, Newton/Jacobian 수렴, coefficient floating noise 가운데 무엇이 step 감소를 유발했는지 구분할 내부 trace가 없다. 실패 prefix의 number ledger가 작아졌다고 전구간 정확도가 개선되었다고 주장하지 않는다. **새 G1 격자의 전구간 시간수렴 판정은 미완료**다.

위 elapsed는 동시 실행 환경에서 측정된 실제 시간이다. 이를 controlled 성능 비교나 grid 크기에 따른 scaling law로 해석하지 않는다.

## G2 미결 슬롯

이 초안 작성 시 마지막으로 읽은 G2 진행 자료는 304/750 segments, \(u=0.17428559253886644\), \(z\simeq9.994\), elapsed 2810.775 s였다. 이는 진행 snapshot이며 terminal result가 아니다.

최종화 시 다음 항목을 실제 terminal 산출물로 채운다.

- G2 종료 상태, 실제 전체 구간 또는 마지막 accepted 상태, 첫 실패의 정확한 분류.
- G2의 전구간 또는 prefix ledger와 domain/positivity 범위.
- 실제 저장된 공통 epoch에 한정한 G1/G2 비교. G2가 전구간을 마치지 못하면 prefix 비교를 전구간 판정으로 승격하지 않는다.
- G1 시간분해 비교의 미완료 상태를 보존하는 독립 최종 판정.
- G2 raw checkpoint와 최종 보고서 checkpoint의 실제 Drive/Dropbox receipt.

## Source 오차에서 이미 확정된 결론

독립 `review/SOURCE_PAIR_LOWER_BOUND.json`은 기존 Q0 reference를 다시 적분하지 않고 새 preflight의 수치를 읽어 다음을 확인했다. 동일한 reference \(R\)에 대해 \(e_j=\|S_j-R\|_\infty/\|R\|_\infty\)라 두면,

\[
\frac{\|S_1-S_2\|_\infty}{\|S_2\|_\infty}
\geq\frac{|e_1-e_2|}{1+e_2}.
\]

| 129개 시점의 source량 | G1 reference 오차 | G2 reference 오차 | 정식 G1/G2 차이의 하한 |
|---|---:|---:|---:|
| reference-volume number source | 0.06835466003 | 0.03448234347 | **0.03274325249** |
| reference-volume energy source | 0.05602279295 | 0.02837003181 | **0.02688989399** |

두 하한 모두 고정 spectral target 0.001을 넘는다. 따라서 이 선택된 point quadrature 쌍은 source를 포함하는 전체 acceptance를 통과할 수 없다. 저장 epoch에서 threshold와 일치하지 않는 것도 확인되어, 이 하한을 one-sided endpoint 관례의 차이로 설명할 수 없다. 129개 시점 결과만으로 65개 subset의 하한이나 evolved Gamma·온도·이온분율 오차를 대신 판정하지 않는다.

해석상 중요한 구분은 세 가지다. 초기 native UVB knots를 포함한 Gauss quadrature는 특정 IC 적분 문제를 개선한다. 그러나 시간에 따라 움직이는 source band/threshold가 패널 내부를 가로지를 때 고정 point sampling 오차는 남는다. 또한 이 source 적분 문제와 G1_TIGHT의 solver 실패는 별개의 blocker이며, 아직 하나의 원인으로 환원할 수 없다.

## 다음 결정: Q1B의 local 단계부터

`NEXT_DESIGN.md`의 고정 q-cell 두 모멘트 \((N,U)\) 방식을 다음 수치 후보로 제안한다. 실제 HM12 interpolation의 cell source number/energy를 각각 정확히 적분하고, native opacity를 threshold에서 분할하여 같은 \(K_0,K_1\)을 photon sink·ionization·heat·counter에 사용한다. \(U=RQ\)에서 \(\dot U=R\dot Q-\lambda U\)를 유지하면 photon number와 radiation energy의 저장-state 합이 각각 선형이 된다.

`review/Q1B_PROPOSAL_REVIEW.json`은 이 보존식·단위·부호와 내부 moment Jacobian 유도를 **derived proposal** 범위에서 받아들였다. 구현이나 ODE 실행 준비가 끝났다는 판정은 아니다. 빈 cell·source entry·endpoint realizability 처리, positive reconstruction의 안정적 역변환, 실제 native integrated-photo-input ABI, 새로운 N/U Jacobian이 미완성인 동안 다음 비싼 ODE는 **NO_GO**다.

Machine-readable 계획은 `Q1B_LOCAL_DAG.json`에 있다. 계약 고정 후 새 cell source/IC, opacity·reconstruction, native adapter·Jacobian 검증을 병렬로 진행하고, 해석해가 있는 새 source-only·expansion-only·grey-opacity 검증을 합친 뒤 전구간 후보 쌍으로 넘어간다. Source precheck에서 이미 실패하는 후보를 또 장시간 적분하지 않는다. 이 과정은 기존 Q0·RUN002·EVENT003 재실행을 요구하지 않는다.

별도 선택 사항인 `PERFORMANCE_NEXT.md`의 Schur block solve는 현재 point Jacobian에 대한 대수적 등가성 제안이며, spectral 오류의 해결책이 아니다. 실제 속도 향상은 측정되지 않았다. N/U representation에서는 cell 내부 2×2 coupling이 생기므로 기존 diagonal-photon 증명을 그대로 전용할 수 없다. G1_TIGHT의 BDF 진단도 새 first failure의 기록과 제한된 instrumentation을 대상으로만 진행하며, 관측되지 않은 원인을 단정하거나 무변경 전구간 재실행으로 대체하지 않는다.

## 이 초안에서 확인한 durable checkpoint

다음 항목은 로컬 receipt에 기록된 두 provider의 실제 성공 응답을 근거로 한다. 모두 **UPLOAD_VERIFIED**, 이 세션의 다운로드 복구 검증을 뜻하는 RESTORE_VERIFIED는 아니다.

| 단계 | archive SHA-256 | bytes | Drive object ID | Dropbox object ID |
|---|---|---:|---|---|
| C08A 구현 | `e1934b173eb97ad2749a135bc302d786a96dcdacbd25a3f55db098a951996803` | 2520985 | `1ZPpKPK43caNvJ-T4RCQYNa_9PboJnsve` | `id:BSpOijBcT10AAAAAAD36cg` |
| C08A2 실행 중 | `3f5bb3ad5db3827eef83bdc10e144ba420358090b078bee91f63d2d3b6b5efcb` | 2721627 | `1NUGnIiU62C671V3ZnarAtWo1VZOHoTiC` | `id:BSpOijBcT10AAAAAAD37bg` |
| C08B G1_FINE raw | `e9ce0eddbb15e09531318ae8d97f382062cb940819615eacb25813ee50cff593` | 3153793 | `1kIDt6b6Agro3aMOAmsbBYQ06W65okbFb` | `id:BSpOijBcT10AAAAAAD38Hw` |
| C08B G1_TIGHT first failure/raw | `87886a45ff4c20f0e7c40955a2bd9ae4c3066f293928162a7ceba0b55edd71eb` | 3570303 | `1Eum7f-l7Fy4QF6U12fZnPxRuXng0unc0` | `id:BSpOijBcT10AAAAAAD38MA` |

`receipts/C08B_PUBLICATION.json`은 REI commit `79ea8affa098c24d7e62f01b003ec69be74da13c`, tree `8050bdee9789d515ac0bc59acce9f2e95610073e`와 BASS commit `aa09f3db8424db8db7b518faa37695adf7daec5b` 게시를 기록한다. BASS로 전달한 것은 gate 상태이며 **새 native receiver 호출은 0**이다. 이 초안 자체의 게시·백업과 G2 terminal checkpoint는 아직 주장하지 않는다.

이 보고서 작성 작업은 저장된 파일 읽기와 문서 작성만 수행했다. 추가 ODE, 테스트, native 호출, reference 적분, Git/remote 변경을 수행하지 않았다. 최종 결론은 G2 terminal 증거를 받은 뒤 위 미결 슬롯을 닫아 작성한다.
