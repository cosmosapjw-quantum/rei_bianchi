# REI F4 | BASS193 Li II 2E1 인과적 첫 광흡수: 실제 소스 데이터

**결론 범위:** 사용한 광자방출 원전 형식은 Li II `1s2s ^1S0` 2E1이며 스펙트럼은 Drake 1969 Table II의 PR283 OCR 값에 **조건부**이다. `K_s=K-K_triplet_forced`의 가능한 모든 K 이벤트를 singlet으로 가정한 모형이다. 실제 리튬 singlet yield와 가스 열은 미정이다. 평균 FLRW redshift를 사용하므로 방향별 Bianchi transfer 아니다. 새 IVP 0. 현재 원본 Working **33/88**, Central **28/88**, fast **4/7**, canonical delta **0**.

## 신규 데이터/수치

원본 BASS21 `193`개 x/H/nb/Y와 `21`개 native ionic photo cross sections, 원본 Li I 1s event `8492`행을 사용해 다음을 생성했다: `EMISSIONS_193.csv` 193행, `FIRST_FLIGHT_KERNEL.csv` **18528**개 source–arrival epoch 간 비행/흡수 구간, `JOINT_OUTCOMES_4825.csv` **4825**개 쌍 공동 결과, `ABSORPTION_ARRIVALS_192.csv` **192** 도착 구간, `CONVERGENCE_108.csv` **108**개의 해당 조정 원본원 source control. 스펙트럼 16-point Gauss per panel, 원래 한 epoch간 4개 시간 subcells; 6개 순차 소스 구간 `0:32,32:64,64:96,96:128,128:160,160:193`를 산출한 후 **하나의 공통** 소스 스펙트럼으로 합산했다. 계산/테스트의 정확한 I/O는 ZIP에서 재현 가능하다.

### 전체 원래 BASS x 이력의 source-weighted conditional exposure

- 원래 source상 singlet 허용 사건 `3.015107560654831×10^-11 events/baryon`.
- 방출 pair 총 광자수에 대한 z=2까지 첫 흡수에 대응하는 초기 자유전자 기대수 **`5.183362629197418×10^-11/baryon`**.
- H I `3.1741304690083725×10^-11`, He I `1.8994327473928018×10^-11`, He II `1.0979906848847005×10^-12`, Li I `3.4430777276945795×10^-18` first absorptions/baryon.
- 원래 source에서 singlet일 가능성이 있는 사건의 두 광자가 모두 흡수되는 `2.1705014464243502×10^-11` events/baryon; 1개만 `8.423597363487156×10^-12`; 0개 `2.2463778817655648×10^-14`.
- 1차 광전자 kinetic `7.997916399993968×10^-10 eV/baryon`, ionization binding `9.585049280055292×10^-10 eV/baryon`, kinematic cosmological redshift work `5.5406183415292437×10^-11 eV/baryon`, z=2 boundary photon survivors `2.3177944627357497×10^-11 eV/baryon`.
- 총 photon emission energy `1.836880696047575×10^-9 eV/baryon`; reconstructed `1.836880696047576×10^-9` (residual `−8.27×10^-25` eV/baryon). **Redshift loss는 gas heat이 아니고, z=2 photon survivors는 앞으로 영원히 escape했다는 뜻이 아니다.**

PR284의 기존 정적 한-Hubble 길이 all-singlet first moments `5.189586318243342×10^-11`과 `P2=2.174514506096772×10^-11`에 비해 현재 mean-FLRW 적색편이적분은 각각 `−0.11993%`와 `−0.18455%`다. 이 작은 통합 차이는 두 근사가 물리적으로 동일하다는 뜻이 아니다. 예를 들어 종료 epoch z=2에서 새 causal 모델은 **미래 구간이 0이므로 흡수 0**, 기존 정적 모델은 인위적으로 하나의 Hubble 길이를 더 부여해 0이 아니다.

### OCR 값의 불확실성을 버린 21-knot source shape cone 조건부 bounds

원전 표의 숫자들을 모르더라도 그 21 knot가 양의 선형보간 `a0=0,aj>=0`인 family만을 고정하면, 전 193 epoch에 **하나의 공통 스펙트럼**을 넣은 전역 총 first absorption 기대수는 `[3.002703213035763,6.029055235967574]×10^-11/baryon` 생성원 극값 범위 안이다. 추가 단조성(아직 실측으로 확증된 전제 아님)을 놓으면 `[4.7207581217553184,6.029055235967574]×10^-11/baryon`. 이는 임의의 연속 spectrum에 대한 우주적 정확 범위가 아니고 원래 knot/보간 family 내부의 조건부 수치 극값이다. Source 본래 1969 OCR 기반 witness 값은 두 family 내부에 있다. 이 부분은 PR285의 구조적 발상을 인과적 비행 kernel에 물리적으로 확장한 것이다.

### 물리적 의미/정확성 판정

독립 대수적 항등식은 Wolfram에서 `{0,0,0}`, source ZIP byte identity, 원본 193 epoch/21 species 및 8492 events, 상자 모델에서 고정 hazard 해/zero opacity 해, 매 epoch 첫 흡수 확률/에너지, 전체 도착률 보존 검사를 수행했다. `CONVERGENCE.json`의 실제 12 emission-epoch 샘플에서 order16/substeps4 vs order32/substeps8의 최대 상대 차는 작은 He II threshold channel 약 `1.64%`로 수치 오류범위가 저쪽에서 지배적이다. **전 193 source의 정밀 interval certificate는 아니다.** 1969 원전 Li II Table II glyph 픽셀 검증, 관측가능 actual singlet branching, atom radiation cascade, 방향별 shear redshift, electron thermalization 및 본래 REI17/BASS21 chemical/clock common owner는 미완료다. 따라서 F4=PARTIAL, L4_ready=false, no observational τ/CMB, no production promotion.

## 백업/게시/재개

최종 검증 저장소·ZIP의 해시 및 PR/Drive/Library 위치는 `delivery/FINAL_ACK.json`과 `HANDOFF_NEXT_THREAD_KO.md`에 기록한다. 새 원본/코드 이론 및 20개의 단계 회고 JSON checkpoint는 source-inclusive ZIP 내부에서 각기 byte SHA로 고정한다. 매 기록의 canonical DAG는 **33/88,28/88,4/7**로 유지된다. 실제 다른 작성자 blind R6/C9는 `NOT_RUN`; 같은 모델 hostile review 결과는 별도 `ADVERSARIAL_AUDIT_KO.md`에 보존한다. 원래 PR285 ZIP full binary 클라우드 미백업은 해당 원본의 blocker이며 이번 백업으로 덮어쓰지 않는다.
