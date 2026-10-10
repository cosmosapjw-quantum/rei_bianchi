# 균질 FLRW H He IGM 기준선 설계

작성일 2026-10-06. 상태: 구현 전 검토안. 이 문서는 기존 코드 감사에 근거한 설계이며 새 우주론적 계산의 완료 보고서가 아니다.

## 목표와 첫 완료 기준

균질 우주에서 모형 의존성을 명시한 비평형 H/He 이온화·열 이력을 계산한다. 먼저 FLRW 기준선을 구현·검증하고, 이후 같은 광원과 원자물리로 Bianchi I 전단·응력 비교를 수행한다. 무거운 BASS_HE·HH·CR 생산자 계산을 재실행하는 것을 선행조건으로 두지 않는다.

첫 기준선의 완료는 단순 빌드가 아니라, 초기조건과 광원을 읽어 H/He·광자·온도를 진화시키고 독립 기준해와 수렴·보존 검사를 거친 결과 CSV와 그림을 생성하는 것이다. 수치 검증, 조건부 물리 모형, 관측 보정은 별도 상태로 표시한다. 기존 FT03/S0 구간 인증은 새 모형으로 이전하지 않는다.

## 감사에서 확인한 재사용과 결손

REI 기준 commit은 2b6005fd9c88e5cb38213c5bb66baee7caf54583이다. H/He 반응, 전자 밀도와 EOS, 광자 소유권, 팽창 열일, 밀도 희석, 광자 적색편이, transaction/restart 구조는 이미 존재한다.

새로 필요한 것은 다음이다.

1. 상수 H와 fixture 초기 밀도에서 출발하는 기존 희석 대신, 우주론적 정규화의 가변 H(z), nH(z), nHe(z), CMB 온도와 일관된 시간 변환. 기존 S0에도 밀도 희석 자체는 구현되어 있다.
2. 실제로 파싱되는 모형 설정과 초기조건·광원 입력. 기존 F08의 scenario 인자는 설정 파서가 아니라 고정 바이트 일치 검사이다.
3. 저온 IGM에 맞는 별도 반응률·냉각 공급자. 기존 FT03 30000–110000 K와 S0 35000–60000 K 계약을 수정하지 않는다.
4. 중성 He, HeIII=0, 광자 0 등 경계 상태 지원. 현재 interval RHS의 엄격한 내부 영역 조건은 그대로 재사용할 수 없다.
5. 원자 냉각·CMB 에너지 교환의 일관된 장부와 독립 회귀검증. 기존 CI/RR/DR 손실 위에 같은 냉각을 중복 가산하지 않는다.

## 선택할 물리 기준선

- 평균 우주 밀도의 균질 primordial 원자 H/He, 단일 기체 온도, 비평형 반응망.
- 기준 clumping C=1. 밀도 구조·분자·금속·먼지·충격파는 포함하지 않는다.
- 기준 RCT/HH/CR OFF. 이는 불필요성의 증명이 아니라 기준 모형 선택이다.
- Case A 재결합. 방출 재결합·선·free-free 복사는 별도 탈출 에너지 장부로 보내고 상호작용 광자장으로 재주입하지 않는다. 이는 특히 중성기에 강한 현상론적 가정이다.
- 기준 광전자 처리는 primary-only이며 초과 에너지를 열로 전달한다. 경질 UV를 중성 기체에 적용할 때 이 가정의 한계를 표시한다. secondary deposition 비교 전에는 실제 우주에 대한 정량적 결론을 내리지 않는다.
- UVB의 Gamma를 직접 주는 독립 회귀 경로와, 방출률에서 광자를 진화시키는 기준 경로를 분리한다. 동일 실행에서 두 광이온화원을 중복 적용하지 않는다.

세 접근 중 방출률 구동을 주 경로로 선택한다. 외부 UVB 반응률만 주는 경로는 구현이 빠르지만 비등방 수송 확장과 광자 수지 검증을 대신하지 못한다. 처음부터 diffuse H/He 재결합광·secondary·공간적 버블까지 모두 풀면 이번 기준선 범위를 크게 넘기므로 후속 확장으로 분리한다.

## 상태와 방정식 계약

적분 좌표는 ln a로 통일하고 모든 proper-time 반응률은 1/H로 한 번만 변환한다. a=1/(1+z)이며 nH와 nHe는 a^-3을 따른다. 배경은 flat radiation+matter+Lambda FLRW로 한다.

진화 변수는 xHII, xHeII, xHeIII, H 원자핵당 열에너지 w=u/nH, 광자 수송 상태이다. 기체 에너지 단위는 erg, 시간 s, 밀도 cm^-3로 통일한다. 광자 eV 변환은 단일 상수를 사용한다.

ne=nH*xHII+nHe*(xHeII+2*xHeIII), T=2u/[3 kB (nH+nHe+ne)]로 재구성한다. 전자 밀도나 평균 분자량을 별도 독립 변수로 고정하지 않는다. HeI=1-xHeII-xHeIII이며 원소별 fraction에는 -3H 희석항을 추가하지 않는다.

열 방정식은 dw/dt=-2H*w+(photoheat-atomic_cooling+CMB_exchange)/nH이다. 이는 proper 열밀도 방정식 du/dt=-5H*u+동일 체적 열원과 동등해야 한다. CMB 교환은 T−TCMB의 부호에 따라 가열 또는 냉각하며, 비음수 탈출복사 장부와 분리한다.

각 광자 흡수는 같은 적분값으로 HI/HeI/HeII의 사건 수, 광자 손실, 결합 에너지와 열을 배분한다. HeII 문턱 이상의 광자도 H와 HeI에 흡수될 수 있다. 광자 아래쪽 경계로 빠지는 수와 에너지, 적색편이 에너지 손실을 기록한다.

## 저온 원자물리와 냉각

기존에 핀된 Grackle 3.4.1 원자 H/He 계수 부분집합과 Verner 단면적을 새 IGM 공급자로 연결한다. Grackle 기준 commit은 af7939494ce65007887ada7b98d1813df6843346이다. 전체 외부 시뮬레이션 설치는 요구하지 않는다.

선택하는 항은 전자 충돌 이온화, Case-A 복사 재결합, HeII dielectronic 재결합, 충돌 여기 냉각, free-free, CMB Compton 교환이다. 화학의 RR/DR와 냉각의 RR/DR 분리는 원문 구현과 대조하여 단 한 번 계상한다. 화학 사건 없는 metastable CI 냉각은 첫 모형에서 제외하고 누락 항으로 기록한다. 일부 He 여기 항은 ne^2*nHeII 계수이므로 모든 항을 이체 반응으로 취급하지 않는다.

새 모형의 운영 범위는 1–10^6 K로 제안한다. 이는 각 fit의 실험적 정확도 보장 범위가 아니다. 공개 패키지의 저온 분기·근사·수치 floor를 그대로 식별하고 source parity와 기여량을 검사한다. 기존 raw wrapper의 100 K 하한도 수정하지 않고, 새 공급자에 독립 계약을 둔다. 범위 이탈은 계산을 중단하며 온도나 종 분율을 조용히 clipping하지 않는다.

## 광원과 스펙트럼

주 입력은 escaping emissivity, 시간변화, SED, 유한 에너지 support와 초기 광자 분포이다. escape fraction을 포함한 방출률에 이를 다시 곱하지 않는다. HI/HeI/HeII의 실제 단면적 cutoff와 결합 에너지 경계를 구분해 적분한다.

첫 구현은 FLRW moving packet characteristic과 source birth-time quadrature를 재사용한다. 광자수는 H 원자핵당 수로 보관하고 에너지는 a^-1로 이동한다. 새 유한체적 redshift solver를 동시에 개발하지 않는다. 시간 적분, source birth quadrature, 에너지 적분 refinement를 각각 검사한다. packet 크기 증가가 제한을 넘으면 저장·병합 방식을 별도 검증한 후 변경한다.

스펙트럼은 cutoff들을 분할한 양수 quadrature로 적분하며 개별 문턱을 가로지르는 사건을 검사한다. 상한을 넘는 실제 SED를 자르면 누락 photon/energy 적분을 기록한다. 3개 대역만으로 정확도가 확보됐다고 가정하지 않는다.

## 설정과 최초 실행의 의미

필수 입력은 H0, Omega_r/m/b/Lambda, He 질량비, TCMB0, 시작/종료 z, 초기 분율·온도·광자 분포, 광원과 support, 공급자·closure, 수치 허용오차이다. 설정 누락에 숨은 물리 default를 넣지 않는다. 같은 설정과 소스 해시가 아니면 체크포인트 재개를 거부한다.

첫 end-to-end fixture는 모든 값이 명시된 제조된 입력으로 작성하고 물리 보정 결과로 부르지 않는다. H/He 광이온화를 모두 자극하는 유한-support 광원, 중성 He와 잔류 전자를 가진 초기조건, 짧은 z 구간을 사용하여 연결과 장부를 먼저 검증한다. 이후 과학 실행의 cosmology·광원·초기조건은 별도 설정 파일에서 출처 또는 현상론적 선택임을 표시한다. 이 두 실행은 같은 코드를 쓰되 서로 다른 model ID와 주장 범위를 갖는다.

중성 시작을 위한 선택지는 명시된 잔류 이온화율과 열적 decoupling 근사, 또는 출처가 확인된 REC 이력이다. 초기 온도 100 K로 자동 올리는 우회는 허용하지 않는다. z=20에서 시작해야 한다는 고정 가정은 없으며 사용자 목표에 맞는 구간을 실제 scientific manifest에서 선택한다.

## 구현 구조

기존 모듈을 수정해 S0를 바꾸기보다 별도 igm 모델과 runner를 추가한다. 배경, chemistry+cooling provider, emissivity, state/ledger, integrator, diagnostics를 얇은 인터페이스로 분리한다. 원소 상태와 단위 변환·단면적 상수는 기존 소유자를 재사용한다.

기존 primary implicit step의 구조를 재사용하되 FT03 함수가 숨은 경로로 호출되지 않도록 공급자 경계를 만든다. zero/neutral 상태를 유지할 수 있는 point solver를 먼저 검증한다. interval enclosure는 별도 후속 단계이며, point 결과에 기존 public-width 인증 명칭을 사용하지 않는다.

## 시험과 산출물

1. source parity: 선택한 C 함수와 Rust의 분기·경계·저온 reference 값 일치, 포함 항/제외 항 목록.
2. 해석적 극한: 고정 종 무광원 단열 T∝a^-2, 밀도 a^-3, 광자 에너지 a^-1, 광자수/H 보존, TCMB에서 Compton=0.
3. 경계·보존: HeIII=0/광자=0/zero opacity, 원소·전하·광자 소유권, PI binding+heat, CI와 RR 에너지, 음수 상태의 transaction rejection.
4. 독립 회귀: 같은 입력과 반응률의 Python 독립 적분기 비교. 별도의 출처 고정 UVB table이 확보되면 external-rate 경로를 비교하되 emissivity 모델 일치를 주장하지 않는다.
5. 수렴과 재개: 시간·에너지·birth quadrature를 각각 refinement, 누적 장부와 IC/설정 hash, 중단 후 재개와 연속 실행 비교.
6. 결과: xHII, xHeII, xHeIII, ne/nH, T, Gamma, photon/energy budgets, 수치오차·closure 가정을 담은 CSV와 그림. 균질 fraction을 버블 체적분율 QV로 이름 바꾸지 않는다.

기존 142개 테스트와 S0 증거는 회귀 대상으로 보존한다. 이번 감사에서는 새 물리 실행을 하지 않았다. 구현의 정확한 테스트 허용오차와 실행 명령은 승인된 설계의 구현 계획에서 원래 목표를 약화하지 않는 방식으로 고정한다.

## 다음 검토 사항

이 설계의 핵심 선택은 Case-A escape, C=1, primary-only, 별도 저온 IGM 공급자, emission-driven reference와 UVB regression 분리이다. 이것을 검토한 뒤 구현 계획과 첫 코드 단위를 확정한다. 외부 push, PR 변경, 기존 과학 gate 승격은 이 문서의 범위가 아니다.

## 근거

- REI 소스 https://github.com/cosmosapjw-quantum/rei_bianchi/tree/2b6005fd9c88e5cb38213c5bb66baee7caf54583/rust/rei_microphysics
- Grackle 핀 소스 https://github.com/grackle-project/grackle/blob/af7939494ce65007887ada7b98d1813df6843346/src/clib/rate_functions.c
- Smith et al. Grackle https://arxiv.org/abs/1610.09591
- Hui and Gnedin 반응률과 열 진화 https://arxiv.org/abs/astro-ph/9612232
- Verner 단면적 https://www.pa.uky.edu/~verner/photo.html
- Haardt and Madau UV 배경 https://arxiv.org/abs/1105.2039
- Furlanetto and Stoever secondary deposition https://arxiv.org/abs/0910.4410
