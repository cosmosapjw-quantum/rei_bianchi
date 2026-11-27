# HE32 완료 pilot의 독립 물리 readback

## 판정과 근거

**PASS_SCOPED_SAVED_DATA_READBACK**. 실제 복구 실행의 392개 nominal NPZ와 각각의 receipt를 모두 읽었다. z=20→2의 201개 저장 시점, 총 78,792개 case–time에서 21개 핵종·전하 population, 전자 census, Frobenius norm 및 응력별 shear budget을 재구성했다. 이 검토는 새 IVP 0회, 성능 benchmark 0회, 과학 소스 수정 0건이다.

원 실행의 394개 IVP 및 그림은 완료 뒤 백업 호출 정지와 scratch reset 사이에 사라졌다. 이 보고서는 같은 P2 과학 코드와 입력으로 다시 만든 실제 결과 파일을 읽는다. 이전 도구 출력에 남은 요약 숫자는 JSON의 별도 비교 항목에 보존하며 원 NPZ가 복원되었다고 표시하지 않는다.

- CATALOG SHA256: `f0cce893caaedba9895b18b66ad76ba6f7238ebca87c9f10e48e0f868f516cdb`
- 과학 executor identity: `99f4a0e248d853d641393d78bcc330c4b3913ad1da1b326219e3fa3f60375314`
- readback script SHA256: `a073851a0da479a550e17606a1076b445a3bb546b57eb33440a4d9ed31679590`
- 각 NPZ/receipt의 SHA256 및 392개 case identity: `COMPLETED_PHYSICS_READBACK.json`의 `input_files`.
- 선행 이론: `HE32_THEORY_KO.md`, 원자·조성 입력: `data/ATOMIC_PHOTO_RR.json`, `data/ISOTOPE_SCENARIO.json`.
- Jacobian 독립 검토의 최초 실패와 수선: `evidence/coupled/independent_v1/` 및 `independent_v2/`; 실패 기록을 유지한다.

## 1. 계산 범위와 넓은 sweep

초기값은 Σ₀의 8개 값 `[0, 10⁻⁴, 10⁻³, 0.01, 0.03, 0.1, 0.3, 0.6]`, signed Pₘ₀의 7개 값 `[-0.0006,-0.0003,-0.0001,0,0.0001,0.0003,0.0012]`, signed Pᵣ₀의 7개 값 `[-0.0024,-0.001,-0.0003,0,0.0003,0.001,0.0048]`의 곱이다. 총392개이며, 초기 각분포의 양성성 범위 안에서 방향이 다른 stress와 shear를 함께 비교한다. 강한Σ₀=0.6은 반응이 보이는 예비 시나리오이며 관측적으로 허용된 초기 우주 값이라는 주장이 아니다.

| z=2 관측량 | 최소 | 최대 | 최대 case |
|---|---:|---:|---|
| Sigma_F | 2.18988080954e-21 | 0.0325437252084 | `s07_m06_r06` |
| signed_Sigma | -0.0004417268307 | 0.0325437252084 | `s07_m06_r06` |
| Pi_m | 0 | 2.84694755335e-05 | `s07_m00_r06` |
| Pi_r | 1.42336700418e-23 | 0.000699521107829 | `s07_m06_r00` |
| Pi_total | 1.42336700418e-23 | 0.000727442405732 | `s07_m00_r00` |
| tau_T | 0.05313868007 | 0.0532075626248 | `s03_m06_r06` |
| ne_cm3 | 5.99641720064e-06 | 5.99641720071e-06 | `s05_m06_r06` |
| elapsed_s | 9.74248166295e+16 | 9.75956004456e+16 | `s03_m06_r06` |

시간축 z는 평균 scale factor의 `z=1/a−1`이고, elapsed time은 평균 z20 이후 흐른 고유시간이다. 이는 절대 우주 나이나 모든 방향에 공통인 관측 적색편이가 아니다. LRS에서 방향별 적색편이는 방출·관측 시점의 β 차이에도 의존한다. 그림은 계산된 시점의 값을 사용하며 이산 7×7 parameter 위치를 연속 균일 격자의 좌표로 해석하지 않는다.

z20→2의 경과시간 범위는 3.08720614–3.09261796 Gyr이다. 등방 기준의 잔류Σ=2.18988e-21는 수치 대조군의 잔류로 취급하며 물리적 최소 shear로 해석하지 않는다.

## 2. shear와 응력의 부호·정규화

공간 정규직교 기저에서 $D=\mathrm{diag}(-1,-1,2)$, $\sigma=sD$, $\pi_X=p_XD$를 사용한다. 따라서

\[\Sigma_F=\sqrt6|s|/H,\qquad P_X=\kappa_T\sqrt6\,p_X/H^2,\qquad\kappa_T=8\pi G/c^2.\]

H는 s⁻¹, 응력은 J m⁻³이다. 저장된 signedΣ는 √6s/H이며, tensor Frobenius normΣ는 그 절댓값이다. 방사선은 `P_r=P_gamma+P_nu`를 먼저 만들고 `Pi_r=abs(P_r)`를 취한다. `Pi_total=abs(P_m+P_gamma+P_nu)`이며 서로 다른 성분의 norm을 먼저 더하지 않는다.

저장 state의 q와 H에서 재구성한 signedΣ의 최대 절대 차이는 1.11e-16, photon/neutrino E₂에서 직접 재구성한 Pγ/Pν의 최대 차이는 각각 3.469e-18/2.168e-18이다. ±10⁻¹⁵의 표시 기준 양쪽을 통과하는 signed shear 반전 case는 43개다. norm만으로는 응력에 의한 상쇄나 방향 반전을 알 수 없으므로 signed history도 함께 보아야 한다.

여기서 πₘ은 Ωₘ의10%를 차지하는 별도 collisionless nonbaryonic massive sector의 stress다. H/He/Li atomic gas는 추가 closure π_b=0을 사용한다. non-tilted라는 조건만으로 baryonic stress가0이라는 결론은 나오지 않는다. 따라서 이 결과를 각 isotope의 비등방 압력을 직접 계산한 결과라고 해석하지 않는다.

## 3. 21개 핵종·전하 상태와 전자 기여

| 핵종 | A | 전하 q | 상태 수 | 핵종/H1 초기 abundance |
|---|---:|---|---:|---:|
| n | 1 | 0…0 | 1 | 0 |
| H1 | 1 | 0…1 | 2 | 1 |
| D | 2 | 0…1 | 2 | 2.503248144e-05 |
| T | 3 | 0…1 | 2 | 0 |
| He3 | 3 | 0…2 | 3 | 1.049996333e-05 |
| He4 | 4 | 0…2 | 3 | 0.0819407011917 |
| Li6 | 6 | 0…3 | 4 | 1e-14 |
| Li7 | 7 | 0…3 | 4 | 5.36802116e-10 |

이는 선택한8개 원시 핵종의21개 중성·양이온 population이다. 짧은 수명의 모든 동위원소, 음이온, 분자까지 포함하는 총망은 아니다. n과T의 초기 abundance는0이다. Be7 late progenitor는 채택한Li7/H 조성에 포함한 초기조건이며 별도로 시간 적분하지 않는다. 동위원소의 전자율과 초기 charge fraction을 같게 놓았으므로 9개 원소별 fraction slot이21개 population으로 정확히 올라간다. 단순히 원소 목록만 저장하는 대신 모든 nonzero isotope의 전자가 photon opacity에 포함된다.

독립 재구성은 $n_e=n_{H,0}a^{-3}\sum_{A,q}qY_{A,q}$ 및 $n_b=n_{H,0}a^{-3}\sum_{A,q}AY_{A,q}$를 사용했다. 밀도 변환 m⁻³→cm⁻³의10⁻⁶을 명시적으로 적용했다. A m_u baryon census이며 mass-defect EOS는 아니다.

- nH1(z0)=0.19082106859399 m⁻³; baryons/H=1.32784437337744.
- 전자 census 최대 상대 차이: 9.992e-16.
- A-가중 baryon census 최대 상대 차이: 3.1086e-15.
- 각 핵종 inventory 최대 상대 drift: 4.2188e-15.
- 원소별 simplex 합 최대 오차: 4.1078e-15; 최소 저장 ion fraction=0.

### 등방 기준 case의 실제 z2 값

기준은 `s00_m03_r03`이다. 다음 fraction은 동일 원소의 각 isotope에 공통으로 적용되지만 핵종 abundance와 전자 기여량은 다르다.

| 이온 | z=2 charge fraction |
|---|---:|
| H_I | 1.51249556526e-06 |
| H_II | 0.999998487504 |
| He_I | 2.38275353102e-09 |
| He_II | 0.000771346274039 |
| He_III | 0.999228651343 |
| Li_I | 3.76624024735e-07 |
| Li_II | 0.999999623376 |
| Li_III | 0 |
| Li_IV | 0 |

총 ne=5.9964172007106e-06 cm⁻³에서 핵종별 전자 기여는 다음과 같다.

| 핵종 | ne 기여 / 총 ne | 기여 cm⁻³ |
|---|---:|---:|
| n | 0 | 0 |
| H1 | 0.859206570683 | 5.15216105941e-06 |
| D | 2.15080725337e-05 | 1.28971376095e-10 |
| T | 0 | 0 |
| He3 | 1.80363434006e-05 | 1.08153439805e-10 |
| He4 | 0.14075388444 | 8.44019013724e-07 |
| Li6 | 8.59207546632e-15 | 5.15216691161e-20 |
| Li7 | 4.61224429115e-10 | 2.76569410014e-15 |

LiI fraction은 저장 시점 기준 평균z=8.0955117에서 최대 0.005686493941가 되고 z2에는 3.766240247e-07까지 내려간다. LiII는 z2에 0.999999623376이다. LiIII/IV는 전체392개 history에서 정확히0이다. 선택 UV 상한60eV가 LiII/LiIII의 다음 photoionization 문턱보다 낮고, 초기 high-charge population과 electron-impact CI를0으로 놓았기 때문이다. 이0은 해당 시나리오의 해이며 우주에서 해당 이온이 항상 없다는 주장이 아니다.

## 4. 물리 반응과 외부 closure의 영향

온도는 $T_g=20000\,K$, $\Gamma_{HI}=10^{-12}\operatorname{expit}[(6-z)/0.3]\,s^{-1}$로 고정한 외부 입력이다. photon-number spectrum은 E⁻²⋅⁵, support는5.392–60eV이다. Photoionization과 total RR(caseA)만 계산한다. CI/DR/charge exchange 누락의 작음을 입증한 오차계산은 아니다. 광원 및 열균형을 자체적으로 진화시키지 않으므로 H/He의 ionization 시점이나 τ를 관측 재이온화의 적합값으로 취급하지 않는다. Γ의 중심z6은 ion fraction의 중간값 위치와 동일하지 않다.

| Σ₀=0.6 case | 등방 대비 ne history 최대 상대 변화 | 해당 평균z | z2 ne 상대 변화 | τ(z20→2) 차이 |
|---|---:|---:|---:|---:|
| `s07_m00_r00` | 0.0042814126 | 9.731501 | -1.1955659e-11 | -6.8833675e-05 |
| `s07_m03_r03` | 0.0042556666 | 9.731501 | -1.0131007e-11 | -6.7213126e-05 |
| `s07_m06_r06` | 0.0042040185 | 9.731501 | -6.4573902e-12 | -6.3955992e-05 |

끝점의 ne가 거의 같은 경우에도 ionization 전이 도중 targetH와 경과시간의 변화가 누적되어 history와 optical depth가 달라진다. 따라서 z2 한 점만으로 화학·팽창 결합의 크기를 판단하지 않는다. 이 비교는 선택한 UV/temperature/입력 조성에 대한 결과다.

## 5. source budget, 보존량과 검증의 범위

$\eta=\ln(a/a_{20})$, $q=s/H_{ref}$에서 $I_s=e^{3\eta}q$를 정의했다. 진화방정식과 함께 적분한 성분은 $I_X'=e^{3\eta}(H/H_{ref})P_X/\sqrt6$이며

\[I_s=I_{s,0}+I_m+I_\gamma+I_\nu\]

이다. 저장 state의 세 budget을 다시 더했을 때 최대 절대 residual은 1.73910144619e-09 (기존 gate3×10⁻⁸)이다. 이는 저장 history의 사후 trapezoid 적분이 아니다. 다만 단일 conservation residual이 각 성분의 독립 정확도를 모두 인증하지는 않는다.

샘플 brightness 최소=0.0420981387024, τ의 최소 증가분=2.70368213235e-07. 양성성은201개 저장 시점과257개 각도에서 확인한 것이며 전 시간·전 각도의 증명과 구별한다. L16/L24의 두 강한-shear corner 비교는 `results/ANGULAR_GUARDS.json`에 보존하며 전체 sweep의 엄밀한 resolution bound가 아니다.

proper baryon density 최대=0.00234655849836 cm⁻³<0.01, 경과시간 최대=9.75956004456e+16 s<1.1×10¹⁷ s로 theory의 freezeout density/time 조건 안에 있다. 핵융합 감소의 S(E)≤10⁶keV barn envelope와 온도 조건은 여전히 명시적 가정이다. 이 결과를 arbitrary19-channel fully reactive nuclear network 실행으로 재표시하지 않는다.

## 6. 재현 및 다음 DAG

다음 명령은 저장된 데이터를 읽고 이 두 보고서를 다시 만든다. 과학 solver를 import하거나 IVP를 실행하지 않는다.

```bash
python research/he32_sandbox_primordial_20261021/evidence/physics/code/completed_physics_readback.py
```

현재 DAG는 `F.C8 실제 recovery pilot → F.C9 saved-data 물리 readback/그림 검토 → F.C10 최종 evidence/backup/publication`이다. 이 분담 검토의 산출물은 두 보고서와 readback 스크립트이며 외부 push·백업 성공 여부는 parent의 publication/backup receipt를 따른다. 사용자가 선택한 광원·열·충돌 closure를 확장할 때는 해당 의존성을 새로운 연구 단위로 다룬다.
