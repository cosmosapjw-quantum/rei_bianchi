# He RCT source 선택과 provider 근거

작성 시각: 2026-10-05 KST. 공급기 기준은 BASS_HE `research/shared-c64-crossrepo-20260928`, commit `21d5b8075429903d195d6e0e0c24a10c00b21063`이다. 직전 `97b38bbd...` 이후 변화는 HE-FLRW02의 DELIVERY_RECEIPT 추가 하나이며 원자 공급기 내용은 변하지 않았다. 정확한 Git blob과 로컬 SHA-256은 REMOTE_IDENTITIES.json, SOURCE_IDENTITY_CHECK.json에 남겼다.

이번 사용자 요청은 선택·provider·closure 코딩 연구를 시작하는 owner opt-in이다. 기존 registry의 `default_source_id=null`, production baseline RCT off, 원자 자료의 물리 정확도 미인증을 소급 변경하지 않는다. 다음 선택은 **명시된 연구 실행 인스턴스의 선택**이며 전역 자동 선택이 아니다.

## 선택 결론

| 항목 | 이 루프에 권고하는 선택 | 근거 상태 |
|---|---|---|
| 반응 | HeIII + HI(1s) → HeII(1s) + HII + 광자 1개 | W82 mechanism 및 기존 공급기 계약; literature-supported |
| 기본 연구 provider | KF96_HEIII_HI_RCT_NOMINAL_V1 | 공개 nominal prescription, 넓은 수치 호출 범위; 물리 정확도 우선순위라는 뜻 아님 |
| 교차 비교 provider | GM25_W82_RCX_CONSTANT_200_10000_K_V1 | 저자 재적분의 상수 근사; 공통 온도에서 별도 실행 |
| 두 자료 비교 범위 | 1000 ≤ T/K ≤ 10000 | 두 API 범위의 교집합 |
| photon/heat closure | provider와 별도로 명시하여야 함 | 양쪽 rate packet의 해당 moment=null |
| 물리 EoR 채택 | 보류; 선택한 근사와 수치 구현의 검증부터 가능 | physical_accuracy_certified=false 유지 |

KF96를 기본 연구 경로로 택하는 것은 폭넓은 온도에서 같은 계약으로 구현을 확인하기 위해서다. GM25보다 정확하다고 판정한 것이 아니다. 현재 F03의 제어점 T=10000 K에서는 양쪽을 비교할 수 있다. 과거 FT03 guard [30000,110000] K는 별도 과거 모델이며 현재 선택을 그 guard 하나로 정당화하지 않는다. 그 과거 guard에서는 GM25가 범위를 덮지 않는다는 기록만 유지한다.

## 1. 반응과 다른 채널의 분리

선택된 반응 ID는 `R_CX:He2+_H1s:He+1s_H+`이다. HeII+HI→HeI+HII인 다른 반응, 분자 결합 상태를 생성하는 radiative association, 광자 없는 nonradiative CT를 이 rate에 추가하거나 대체하지 않는다. W82 논문은 ⁴He²⁺와 바닥상태 H 충돌에서 분리된 He⁺와 H⁺를 만드는 radiative charge transfer를 다룬다. 공개 초록에서 계산 에너지 범위 0.1–1000 eV와 optical-potential 계산을 확인했다. 이는 곧바로 임의 Maxwell 온도 범위를 인증하는 정보가 아니다.

species 순서 (HI,HII,HeI,HeII,HeIII,e)에 대한 사건 벡터는 (-1,+1,0,+1,-1,0)이다. 직접 free-electron 변화는 0이며 H/He 핵수와 전하를 보존한다. 광자 1개는 명시한 single-photon RCT mechanism의 사건수 규약이다. 이것만으로 광자 평균 에너지나 선 스펙트럼은 정해지지 않는다.

원전: West, Lane & Cohen (1982), [Phys. Rev. A 26, 3164](https://journals.aps.org/pra/abstract/10.1103/PhysRevA.26.3164). 공개 초록은 이번 루프에서 직접 읽었지만 유료 원문을 새로 취득하지 않았다. 사용자가 제공했던 PDF의 존재를 근거로 이 루프에서 원문 재분석을 완료했다고 주장하지 않는다.

## 2. 실제 사용 가능한 두 scalar provider

### KF96 nominal

Eq. (7)의 형식은 k=10⁻⁹ a T₄ᵇ [1+c exp(d T₄)] cm³ s⁻¹, T₄=T/(10⁴ K)이다. He²⁺ 표 행은 a=10⁻⁵, b=c=d=0이므로 k=1.00×10⁻¹⁴ cm³ s⁻¹=1.00×10⁻²⁰ m³ s⁻¹이다. 기존 BASS_HE 코드와 별도로 공개 [저자 Fortran ct.f](https://sites.physast.uga.edu/ugacxdb/cx/hydrogen/rates/ct.f)의 `CTRecomb(i,2,2)` 행을 직접 읽어 계수와 [10³,10⁷] K 수치 범위를 교차 확인했다. 원문 하한의 ~ 표기는 기존 packet에서 보존한다.

이는 표의 nominal prescription이다. 정확한 total CT rate나 온도 기울기의 측정이 아니다. dk/dT=0은 채택한 상수식에 대한 도함수다. source uncertainty, fit-error bound, spectrum은 주어지지 않는다. 계수 식은 같은데도 공개 Fortran은 범위 밖 온도를 clamp하는 반면 기존 BASS_HE API는 범위 밖 호출을 거부한다. 새 adapter는 기존 엄격한 거부 계약을 계승한다. 따라서 전체 원본 Fortran 프로그램을 byte 또는 behavior 그대로 사용했다고 쓰면 안 된다.

원전: Kingdon & Ferland (1996), [ApJS 106, 205, DOI 10.1086/192335](https://uknowledge.uky.edu/physastron_facpub/150/). 대학 저장소는 공개 게시 허가를 명시하지만 all-rights-reserved도 표기한다. 논문·코드를 “조건 없는 재배포”로 분류하지 않는다. 여기서는 사실인 계수/출처와 사용자의 기존 provider 구현을 이용하며 외부 논문 전체를 재게시하지 않는다.

### GM25 저자 근사

García Muñoz et al. [arXiv:2511.21966v1, Appendix B.3](https://arxiv.org/html/2511.21966v1)은 He²⁺+H→He⁺+H⁺ 채널을 추가하고 W82 단면적으로부터 직접 구한 rate가 200–10000 K에서 k=1.70×10⁻¹³ cm³ s⁻¹로 근사된다고 보고한다. 해당 절은 He⁺를 바닥 전자상태로 취급한다고 명시한다. 이번 루프에서 이 절을 직접 열어 기존 packet의 계수와 온도 범위를 확인했다. arXiv HTML은 CC BY 4.0을 표시한다.

이 결과는 공개되어 재사용 가능한 저자 근사이며, 우리 쪽에서 원 단면적을 다시 적분한 결과가 아니다. raw σ(E) 배열, 광자 에너지 분포, quantified fit error가 이 scalar packet에 포함되어 있지는 않다. 같은 T에서 KF96와 비율은 17이지만 두 rate를 더하지 않으며, 17배의 폭을 확률적 신뢰구간으로 해석하지 않는다. GM25의 [200,10000] K를 고온까지 자동 연장하지 않는다.

## 3. provider 입력/출력 계약

기존 공급기는 다음을 검사한다: 명시적 source_id; `acknowledge_source_conflict=true`; Kelvin 단위; 공통 온도 Maxwell 분포 및 상대 drift=0; H1s; `SOURCE_W82_4HE_H`; `SPONTANEOUS_SINGLE_PHOTON`; 유한한 온도; 포함된 양 끝점의 온도 범위. KF96 자체는 isotope-resolved fit이 아니므로 W82 ⁴He–H 상태 연결을 명시적 시나리오로 보존하며 임의 질량 재척도는 하지 않는다.

반환값은 scalar k, 해당 상수식의 dk/dT, 정확한 species stoichiometry, source identity이다. 밀도 곱 k n_HI n_HeIII, proper/comoving 변환, cosmological clock, 방출·흡수·열 closure는 소비기 책임이다. photon_energy_moment, heat_moment, recoil_moment, inverse_reaction_rate의 null을 숫자 0으로 덮어쓰지 않는다. closure가 0을 택했다면 “원자 데이터 값”이 아니라 그 closure의 명시적 근사로 별도 기록한다.

같은 반응에 대한 thermal_rate와 event_count_coefficients는 두 view이며 additive process가 아니다. GM25와 KF96도 동일 반응의 대안이다. 같은 RHS에 둘을 동시에 더하는 것은 double counting이다.

## 4. 바로 가능한 것과 남는 것

지금 가능한 것은 (i) 명시적 source 선택과 온도/domain 거부를 갖춘 native provider, (ii) 종/전하/사건수 ledger, (iii) 추가 근사를 명시한 closure와 analytic fixture, (iv) 원자 공급기와 native 구현의 제한된 교차 확인이다. 새로운 산란 계산이나 Eq55 실행은 필요하지 않다.

아직 증명하지 않은 것은 진짜 rate 정확도, RCT spectrum·열 moment, nonzero drift/non-Maxwell gas 적용, 실제 EoR에서 중요도, 최종 생산 모델의 admission이다. Mono-Q를 쓰더라도 Q=χ_HeII−χ_HI는 chemical binding budget이라는 사실과 평균 photon energy를 Q로 놓는 근사라는 사실을 구분한다. 수치 보존만으로 이 근사의 물리 정확도가 입증되지는 않는다.

자료 반입은 8개 파일의 byte identity까지 확인했다. 이 하위작업은 read-only 외부 조회이며 원자율 실행 0, 산란 재계산 0, 외부 mutation 0이다. native 구현/시험 결과는 coding/evidence 산출물에서 별도로 판정한다.

