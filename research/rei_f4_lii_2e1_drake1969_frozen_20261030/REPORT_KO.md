# REI F4 Li II 2E1: 실제 스펙트럼 × BASS193 물리 데이터 보고

## 결론
1969년 Drake–Victor–Dalgarno의 Li II `1s2s ^1S_0 -> 1s^2 ^1S_0 + 2γ(E1)`의 21점 분광률을 원본 BASS21 193 epoch, 8,492 Li 1s 사건 행, 21개 이온의 실제 native 광이온화 단면적과 결합했다. **새로운 원본 이력 기반 물리 데이터**: 4,053 epoch×spectral-rate 표, 193 epoch 조건부 이온화광자/정적 흡수·전자 에너지 장부, 원본 사건별 8,492 표, 3개 실제 데이터 그림. 원본/조건부 구분 유지.

이전 PR280은 임계값만으로 이온화 가능 광자수를 상·하한으로 제한했다. 이번에는 출처가 있는 2E1 에너지분포 `p(y)`로 이를 개선했다. 각 singlet 2E1 pair에서 이온화 가능 광자의 평균은 H I **1.72127500256**, He I **1.26646376473**, He II **0.06661043780**이다. 1969 Table II의 piecewise-linear 적분률은 **1945.475 s^-1**로 독립 Li II 정밀 계산 **1940 s^-1**와 0.2822% 일치. 원전 스캔의 광학문자 번역 일부를 직접 픽셀 확인하지 못했으므로 특정 숫자들의 출처 확실성은 `PARTIAL_VISUAL_SOURCE_QUALIFICATION`이다. 별도의 실제 2E1 자발붕괴 총률은 503±26 μs 실험과도 동일 자릿수이다.

## 조건부 원본 BASS193 방출 장부
원본 Li I K-광전자 사건은 **3.4426556153037163e-11 사건/baryon**, 첫 활성 bin이 허용하는 triplet-forced subset은 **4.27548054648883e-12 사건/baryon**이다. 실제 singlet yield는 미확정이므로 진공 복사붕괴 완료를 조건으로 H I 광자 **[3.4426556153e-11,5.6173773288e-11]**, He I **[3.4426556153e-11,4.2460725270e-11]**, He II **[6.2838568926e-12,3.4426556153e-11]** 개/baryon이 방출 가능하다. 원본 저장 이력에 대한 Simpson `dx/H` 후처리이며 IVP 신규 생성 0.

## BASS-native 21-ion 정적 흡수 진단
원본 epoch를 통과하는 **모든 비강제-triplet 사건을 singlet로 둔 명시적 시나리오**에서, 각 epoch의 `κ(E)=n_b Σ Y_iσ_i(E)`, `P_abs=1−exp(−cκ/H)`를 사용해 *one frozen Hubble path* 기대값을 계산했다. 시간변화·광자 이력·비등방 경로 적분은 하지 않았다. 원본 이력의 적분 결과 [baryon당]:

| 정적 조건부 출력 | 저장 이력 적분값 |
|---|---:|
| 첫 광흡수 가능한 사건 수 | 5.189586318243344e-11 |
| H I 첫 흡수 | 3.172816103001298e-11 |
| He I 첫 흡수 | 1.905891995109763e-11 |
| He II 첫 흡수 | 1.108708124729548e-12 |
| Li I 첫 흡수 | 7.407659335954014e-17 |
| 첫 광전자 초기 운동에너지 | 8.012038195401590e-10 eV |
| 새로운 이온화 결합에너지 | 9.604981271744398e-10 eV |
| 흡수되지 않은 광자 에너지 | 7.517874933297772e-11 eV |
| 흡수된 광자 총에너지 | 1.761701946714599e-9 eV |

흡수 에너지의 두 원천 `electron + binding` 합은 총 흡수 에너지와 일치하며, 이 값들과 광자 미흡수 에너지의 합이 원본 조건부 2E1 총 방출 에너지와 일치한다. **이 수치는 실제 이온화수, 관측 광학깊이, 온도 응답이나 deposited heat가 아니다.** 실제 2E1 방출의 angular/time correlations와 방사 전달, Li singlet branching, plasma quenching, 2차 전자 cascade가 없음.

## 동일 source와 검증
BASS owner `cc602e209e7deeb511ab2a1f3b2268d55206c43c`. 부모 PR282 `6739f37460caf802f045dcd64e1a3b225e54c4dc`; 원본 source-inclusive ZIP SHA256 `a0f15cab2a283c1cfdf5c2a1fa8d2bc1fe9e232c1754cdaf4625ca0ff65107c0` (10,533,802 bytes), nested PR278 and PR280 binary exact. Original trajectory SHA `37d1bab173e81449cf474b21a678077edd0150cf0b2cb386d014764580678086`. 원래 계수 소스의 전체 raw JSON SHA 검증을 따로 하지 않았고, 원본 native 129 수치 projection에 국한한다. Python targeted tests 17/17 PASS (새 데이터 검증), Wolfram 독립 threshold 숫자 3/3 일치, Gauss–Legendre 4/8/16 수렴, 원본 PR282 M1 κ 및 PR280 Li1s event rate 재생 검사. 4/8/16 불일치 버그는 각 native 이온 문턱에서 적분을 쪼개 해결했다. 초기 한 테스트의 부동소수점 exact comparison 실패는 부적절한 테스트를 엄밀한 절대오차 비교로 고쳤다. 총 0 신규 IVP. 본 보고서의 17/17은 **이 연구의 테스트**이며 전체 Rust CI가 PASS라는 뜻이 아니다.

## 인계 및 DAG
이 단위는 새 소스 기반 auxiliary physical-data `1/1 SCOPED`다. REI Working **33/88**, Central **28/88**, Physical fast **4/7**, canonical physical delta **0**; original `F4=PARTIAL, L4_ready=false, PRODUCTION=HOLD`. 서로 다른 작성자의 R6/C9 **NOT_RUN**, native subagent **NOT_RUN**. 유도된 스펙트럼은 기존 PR282의 M1 라인과 병렬 보존, 형제 PR281의 static F/J와는 물리적 동일성을 주장하지 않음.

후속은 (1) 1969 Li II Table II의 원전 페이지 직접 픽셀/최신 계산 데이터 대조, (2) **실제** Li I 광이온화 singlet/triplet 편미분 단면적, (3) photon two-time/two-direction transport와 재흡수, (4) REI17/BASS21 공통 state/clock/electron 및 secondary energy deposition에만 thermal port binding. 새로운 IVP, CMB/τ, production, merge, force push는 하지 않는다.
