# H/He + photon implicit stage — 독립 문헌·전제 지도

검색·원문 확인일: 2026-10-12 UTC. 검토자: `/root/dropbox_checkpoint`.

## 연구에 바로 쓰이는 결론

원전은 계수를 고정한 H/He 화학 해석해, photon absorption의 분모 소거, Newton 행렬의 Schur complement, 비음수 chemistry resolvent를 각각 제공한다. 이번 이론의 기여는 이 알려진 구성들을 현재 provider·사건·에너지·stage 변수에 정확히 대응시키고 그 대응을 증명하는 데서 특정하면 된다. 아래 문헌 검토는 후보나 수용 기준의 작성에 참여하지 않은 상태에서 수행했다. 최종 후보의 실제 유도는 freeze 이후 별도로 판정한다.

현재 적용 정책은 `physmath-research-loop` 내장 규약 **1.0.0**의 `RESEARCH_POLICY.md`, `THEORY_LOOP.md`, `EVIDENCE_AND_HANDOFF.md`다. 이번 읽기로 세 문서의 현재 내용을 확인했다. 이전 GPT-6 Astra harness 4.0.0 판정은 당시 결과의 provenance로 보존한다. 별도 reviewer만이 모든 연구를 수행해야 한다는 과거 기본 규칙을 이 새 이론 작업의 의무로 추가하지 않는다. 이 agent는 역할 분담에 따라 실제 독립 최종 reviewer로 남는다.

## 보존해 재사용한 프로젝트 근거

다음 문서들은 직전 루프에서 내용과 연결된 증거를 직접 검토했다. 이번 문헌 작업에서는 그 검토를 재사용했으며 native test, oracle, probe, interval을 다시 실행하지 않았다.

| 보존 자료 | SHA256 | 이번 작업에서의 역할 |
|---|---|---|
| `event_bridge_02_work/dossier/REPORT_KO.md` | `d2795ec22fded4e8a3db6d6cc470416fc6e8c084d89512b9a10293144401055b` | 실제 conditional 경로와 기존 warm Case A 물리 계약 |
| `event_bridge_02_work/dossier/CLAIMS.json` | `17394f500e780d0b67c7b946f4590ab9d5c81c43f2643ea5153c0d7b04d1e777` | C01–C05의 확보 범위와 C06의 후속 implicit 의무 |
| `event_bridge_02_work/dossier/HANDOFF_KO.md` | `5fa41db841c531654761fde1954c0fa36e47198efc2735df5931a4a464d5d805` | `HERE_RUX03_PRIMARY_PROVIDER_03`, 원 owner DAG 연결 |
| `event_bridge_02_work/dossier/review/DECISION.json` | `4df64a70f77ccf698ca31a1e7e4f95a5704a1ee70e5450162649c2bb4953d153` | 실제 독립 scoped promotion과 미완료 의무 |

재사용하는 물리 내용은 H/He CI·RR·DR·primary PI의 공통 원시 사건 ledger, Case A escape, 종별 binding과 captured kinetic energy, 동일 stage의 proper/reference-volume 변환이다. source commit `a5c958c414dea41216b445c05f58df837f05cacb`가 직전 구현의 identity다. 원 owner DAG의 RUX02/RUX03 준비와 RUX04 이후 physical RUX05 연결을 유지한다.

## 직접 읽은 1차 문헌

페이지는 별도 표시가 없으면 아래 URL에서 검색일에 읽은 **PDF의 1-based 페이지**다. 출판 PDF와 arXiv의 쪽·정리 번호를 혼용하지 않았다. 확인 범위는 PDF text의 해당 식과 주변 논증이다. PDF 전체를 읽었다는 기록으로 사용하지 않는다.

### S1 — 기존 C2-Ray의 해석적 hydrogen 화학 해

Mellema, Iliev, Alvarez & Shapiro, *C²-Ray: A new method for photon-conserving transport of ionizing radiation*, arXiv `astro-ph/0508416v2` (2005 preprint; 후속 2006 논문).

- 원문: <https://arxiv.org/pdf/astro-ph/0508416>
- 서지: <https://arxiv.org/abs/astro-ph/0508416>
- 직접 읽은 위치: §2.2, PDF pp. 7–9, 식 (8)–(14), 특히 식 (11) 직후와 식 (12)의 상수 계수 가정.
- 출처 관계: **supports** 계수 고정 화학 해; **limits** 이를 전체 비선형 시간 진화의 정확해로 쓰는 해석.

식 (11)은 중성·이온화 hydrogen의 생성–소멸 식이고, 식 (12)–(14)는 `Γ, n_e, C_H, α_H`를 상수로 둔 exponential relaxation이다. 논문은 electron density를 반복 갱신하는 연결을 명시한다. 순수 photoabsorption만 있는 식 (8)–(10)에서는 시간 적분된 photoionization rate가 endpoint를 정한다. recombination과 collisional ionization을 함께 넣으면 그 단순한 시간 평균만으로 일반적인 계수 변화의 효과가 모두 보존되지는 않는다. 이 문헌을 사용할 때는 고정 계수 해의 정확성과 비선형 반복의 수렴을 구분한다.

### S2 — Friedrich et al.의 H/He generator와 coupled OTS

Friedrich, Mellema, Iliev & Shapiro (2012), *Radiative transfer of energetic photons: X-rays and helium ionization in C²-Ray*, MNRAS 421, 2232–2250, DOI `10.1111/j.1365-2966.2012.20449.x`.

- 읽은 원문: <https://arxiv.org/pdf/1201.0602> (`v1`, 2012-01-03, 19 pages).
- 출판 locator: <https://academic.oup.com/mnras/article/421/3/2232/1077406>
- 직접 읽은 위치: PDF pp. 2–5, §2의 식 (2)–(7), §3.1의 식 (8)–(13), §3.2와 Tables 1–2; p. 6 식 (15)–(16); p. 8 식 (19)–(20); Appendix A pp. 13–14의 식 (A1)–(A6); Appendix F p. 16의 timestep 논의.
- 출처 관계: **supports** He birth–death 구조와 nonlinear coefficient iteration; **contextual** coupled OTS와 온도 정확도.

식 (8)은 `(HeI, HeII, HeIII)`의 세 상태 생성자이고 식 (9)는 위쪽 ionization rate를 묶는다. 식 (10)–(11)은 `HeI=1−HeII−HeIII`를 사용한 affine 2변수 표현이다. §3.2는 electron density와 ionization rate 외에도 OTS 배분 계수가 상태에 의존함을 밝히며 반복을 수정한다. Table 2의 optical-depth 분율은 그 의존성을 직접 보여준다. 식 (15)–(16)의 thermal energy는 전자수 변화까지 포함하는 particle count에 연결된다. Appendix A의 eigenmode 식은 고정된 선형 계수에 대한 해다. 이 원전의 OTS 재흡수 모델은 현재 Case A escape와 서로 다른 closure이므로 현재 provider의 rate를 바꾸는 근거로 사용하지 않는다.

### S3 — RAMSES-RT의 photon 분모 식과 thermochemistry subcycling

Rosdahl, Blaizot, Aubert, Stranex & Teyssier (2013), *RAMSES-RT: Radiation hydrodynamics in the cosmological context*, MNRAS 436, 2188–2231.

- 읽은 원문: <https://arxiv.org/pdf/1304.7126> (49-page preprint).
- 출판 locator: <https://academic.oup.com/mnras/article/436/3/2188/1247446>
- 직접 읽은 위치: PDF p. 9, §3.3와 §3.3.1; Appendix A pp. 36–38, 식 (A1)–(A11), 특히 식 (A5)–(A10)과 p. 38의 RHS 평가 시점.
- 출처 관계: **supports** photon absorption의 대수적 분모 구조; **limits** 그 논문의 단계식을 fully coupled nonlinear backward Euler로 부르는 해석.

식 (A5)–(A7)은 photon 수에 선형인 absorption과 recombination source를 정의한다. 식 (A9)는

\[
N_i^{n+1}=\frac{N_i^n+\Delta t(\dot N_i+C_i)}{1+\Delta t D_i}
\]

이다. 논문은 이 update가 photon에 대해 semi-implicit이고 temperature·ion abundance에는 explicit임을 명시하며, RHS 값은 step 시작 시점의 값이다. 식 (A3), (A11)과 §3.3.1의 subcycling은 변화율에 대한 논문의 정확도 제어다. 이 수치를 현재 프로젝트의 수용 기준으로 옮기지 않았다. 현재 미지의 gas 상태를 분모 계수에 유지해 소거하는 논증은 해당 논문의 계수 고정 update와 구별해 작성할 수 있다.

### S4 — fully implicit radiation–chemistry Newton/Schur의 직접 선례

Reynolds, Hayes, Paschos & Norman (2009), *Self-consistent solution of cosmological radiation-hydrodynamics and chemical ionization*, Journal of Computational Physics 228, 6833–6854.

- 읽은 원문: <https://arxiv.org/pdf/0901.1110> (`v3`, 2009-06-12, 37 pages).
- 출판 locator: <https://www.sciencedirect.com/science/article/abs/pii/S0021999109003258>
- 직접 읽은 위치: §3.2–§3.2.1, PDF pp. 9–11, 식 (29)–(35), Schur 구성과 복원식, opacity/limiter의 lagged Jacobian 항 설명.
- 출처 관계: **supports** coupled implicit solve와 block elimination; **limits** 원전의 assembled Jacobian을 전 항의 exact Jacobian으로 간주하는 해석.

식 (33)–(35)는 local microphysics block을 먼저 소거해 `S=D−LM⁻¹U`를 풀고 나머지 Newton increment를 복원한다. 이는 구성된 선형 시스템에 대한 정확한 block 대수다. §3.2.1은 flux-limiter의 chemical-opacity 의존성 하나를 이전 Newton iterate에 둔다고 명시한다. 따라서 Schur 소거의 대수적 정확성과 assembled Jacobian의 inexactness가 함께 존재한다. 현재 문제에서는 소거 방향과 photon block 구조를 현재 식에 맞게 확인한다. 원전의 수렴·scalability 실행 결과를 현재 four-variable residual의 실행 결과로 재사용하지 않는다.

### S5 — 비음수 resolvent의 직접 정리

Blanes, Iserles & Macnamara (2022), *Positivity-preserving methods for ordinary differential equations*, ESAIM: M2AN 56, 1843–1870, DOI `10.1051/m2an/2022042`.

- 직접 읽은 **출판본**, 저자 호스팅: <https://personales.upv.es/serblaza/2022_M2AN.pdf>
- 출판 locator: <https://doi.org/10.1051/m2an/2022042>
- arXiv: <https://arxiv.org/pdf/2102.08242> (`v2`, 2022-05-02; arXiv metadata title은 *population models*).
- 출판본 직접 읽은 위치: p. **1844**의 graph Laplacian 정의; pp. **1845–1846**, Proposition 1.1/Theorem 1.2 주변 조건; pp. **1850–1852**, Propositions 3.1–3.4와 frozen-matrix 설명. 핵심 **Proposition 3.4, p. 1851**. arXiv의 대응은 Proposition 7, PDF p. 10이다.
- 출처 관계: **supports** 고정 비음수 생성자의 backward-Euler resolvent; **contextual** 비선형 positive integrator 구성.

저자의 generator convention은 off-diagonal 비음수, diagonal 비양수, **column sum zero**다. Proposition 3.4는 `h≥0`의 `(I−hA)⁻¹`이 entrywise 비음수임을 M-matrix 구조로 보인다. `1ᵀA=0`이면 같은 resolvent의 column sum은 1이다. `h=0`과 reducible/zero-rate 경계도 기본 비음성 보존에 포함된다. 비음수 보존에는 irreducibility를 더 요구하지 않는다. 이 정리는 현재 nonnegative initial species에 대한 고정 chemistry 단계와 직접 대응한다. 상태에 따른 계수 변화나 thermal coupling의 수렴은 그 정리의 행렬 역원 성질과 분리해 확인한다.

## 최종 후보에서 확인할 정리 적용 조건

이 표는 원전의 적용 조건과 현재 물리 변수의 대응을 위한 검토 메모다. 새로운 수치 tolerance나 실행 수용 기준을 설계하지 않았다.

| 대상 | 확인할 수학적 내용 | 현재 작업에서의 의미 |
|---|---|---|
| 광자 소거의 정확성 | 주어진 gas 미지수에서 photon 방정식이 해당 photon 수에 선형인지, 소거 분모가 0이 아닌지, 복원한 photon을 원래 방정식에 대입하면 같은 잔차를 얻는지 | 상태 의존 opacity를 현재 gas 미지수의 함수로 유지하면 대수적 소거와 계수 고정 근사를 구별할 수 있다. |
| 광자 비음성 | 흡수 계수와 stage 계수의 부호, numerator의 비음성 | 양의 분모만으로 photon 해의 비음성이 따르지는 않는다. known source/predictor가 음의 numerator를 만들 수 있는 scheme이면 그 경우를 해당 명제의 가정으로 다룬다. |
| reduced Jacobian | 소거된 photon의 gas 의존성에 대한 chain rule과 full block Schur 대응 | 항을 생략한 Jacobian은 그 생략을 드러내는 iteration/preconditioner로 평가하고, 원잔차의 정확성은 별도로 유지한다. |
| He chemistry의 비음성 | 세 상태 generator와 fraction simplex의 대응 | Friedrich 식 (11)의 reduced off-diagonal `n_e α_HeIII−U_HeI`는 음수일 수 있다. M-matrix 정리는 식 (8)의 전체 세 상태에 적용하거나 그 resolvent를 정확히 축약한 식으로 연결한다. |
| frozen coefficients의 의미 | 고정한 `T, n_e, Γ`와 갱신하는 변수, 각 rate의 차원 | 각 고정 단계의 비음성·질량 보존을 직접 확보할 수 있다. 비선형 반복의 convergence 또는 contraction은 별도의 추정이 있을 때 그 범위에서 판정한다. |
| rate-zero 경계 | `n_e=0`, 특정 photon group 비활성, channel rate=0에서도 유효한 식 | generator resolvent는 rate 자체로 나누지 않는다. eigenvector/평형 비율식을 쓸 경우 0으로 나누는 표현의 극한을 확인한다. |
| thermal 결합 | particle count와 전자수의 EOS 의존성, thermal source의 부호, 채택한 temperature interval에서의 rate 유효성 | chemistry simplex 보존은 temperature interval의 self-map 성질을 대신하지 않는다. 후보가 고정점 존재·유일성을 주장하면 thermal 성분의 실제 경계 추정까지 확인한다. |
| 공통 사건 budget | 종·전자·photon·binding·heat·escape가 같은 stage 사건 수와 같은 시간/volume 정규화를 쓰는지 | 이전 ledger를 implicit stage에 옮길 때 새 provider 평가값과 구값을 섞어 동일 사건을 다른 수로 소비하지 않는지 확인한다. |

이 표에서 특정 가정이 필요한 것은 constructive theorem의 정의역을 정하는 일이다. 아직 읽지 않은 최종 후보에 오류나 불가능성을 부여하지 않는다. 현재 문헌 조사에서 새 strong no-go 성과를 제안하지 않았다.

## 실제 읽기·실행·접근 상태

- 과학 실행, native build/test, symbolic/numerical candidate 실행: **0회**.
- 후보 코드·후보 유도·acceptance threshold 수정: **0회**.
- 위 다섯 논문의 지정 부분을 primary PDF text로 읽었다. 검색에는 두 검색 engine을 사용했고, 근거에는 논문 원문과 저자 호스팅 출판본만 채택했다.
- OUP 두 논문 HTML과 ESAIM 출판사 PDF의 직접 open은 도구의 Internal Error였다. 각각 arXiv 저자 manuscript와 저자 호스팅 출판본의 실제 내용을 읽어 필요한 식을 확인했다.
- Burchard–Deleersnijder–Meister (2003)의 Patankar 논문은 저자 기관 repository에서 서지·초록만 확인했고 본문은 restricted였다. 그 논문의 세부 정리나 식을 근거로 채택하지 않았다.
- screenshot endpoint는 실제 image bytes 대신 `ImageDisplayed` 표식만 반환했다. 시각적 원본 대조를 완료했다고 기록하지 않았으며, 문헌의 수식 번호와 주변 text가 읽힌 범위를 위에 한정했다.
- 조사 범위는 위 직접 관련 원전 다섯 편이다. 최종 후보의 구체적인 대응식을 받은 뒤 해당 식의 주장·전제·보존 연결을 검토한다. 전면적 novelty 조사나 새로운 과학 실행은 이 문헌 작업의 완료 조건에 포함하지 않았다.

## 다음 독립 검토 재개점

Root가 고정한 four-variable implicit residual, full/reduced 식의 동등성 유도, constructive chemistry map, 실제로 주장하는 존재·유일성·수렴 범위와 자료 identity를 받는다. 원잔차 대입, 단위·부호·보존, 원전 정리의 적용 조건을 읽고 그 확보 범위를 판정한다. 현재 정리의 완결성이 실행에 의존하지 않으면 미수행 numerical test를 추가적인 증명 완료 조건으로 붙이지 않는다.
