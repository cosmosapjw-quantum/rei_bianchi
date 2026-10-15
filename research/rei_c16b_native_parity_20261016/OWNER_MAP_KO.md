# C16B native 비교의 단위·에너지 소유권

이 단위는 PR155의 양의 manufactured-rate reference를 실제 native 연산자의
동일 상태 비교기로 연결한다. native 진화 알고리즘이나 rate provider는 바꾸지 않는다.
최종 이온 분율·실제 기체온도 이력의 과학적 승인은 별도다.

native authority는 PR150 `0e25846433170d0f420c4cda44a0bedbf02cd177`,
research base는 PR155 `f8f26710e3961609acf4d7e7930bc7b2a95bd39c`이다.
PR154 photon source는 `daf653e87a5b208ed6f51113e83d56fec4abf4f8`의
blob `db822a53da3ccdca7cf96628e9ef3bbcec83db5a`를 유지한다.

| 물리량 | native 소유자 | 비교식/단위 |
| --- | --- | --- |
| 광자 수 | `PreparedAbsorption::evaluate` | `Nstar=N/(1+dt*c*sum(n_abs*sigma))`, 광자/H |
| 세 종별 photo input | `IgmPhotoInput` | `gamma=c*nH*sum(Nstar*sigma)`, absorber당 s⁻¹ |
| 세 종별 photo heat | `IgmPhotoInput` | `c*nH*ev_erg*sum(Nstar*sigma*(E-chi))`, absorber당 erg/s |
| gas state | `IgmGasState` | fractions `[HII/H,HeII/He,HeIII/He]`, `w`는 erg/H |
| RR/CI/DR/CE/freefree 계수 | `igm_rates(T)` | 원래 Grackle 3.4.1 Case-A subset; source commit `af7939494ce65007887ada7b98d1813df6843346` |
| 반응·열·binding·escape | `igm_point_rhs` | proper cm³당 s⁻¹의 반응률 및 erg cm⁻³ s⁻¹의 에너지율 |
| CMB | `igm_point_rhs` | Thomson CODATA 식, gas 유입량의 음수가 CMB reservoir 변화 |
| 팽창 work | `igm_point_rhs` | `2*H*u`; `nH*dw/dt=thermal_micro-expansion_work` |
| redshift/shear work·source age | transport / driver / source history | 이번 frozen point fixture와 구분하여 후속 검증 |

Python reference는 현재 광자 stock에서 순간 rate를 계산한다. 따라서 `dt=0`에서는
동일 초기 stock을, 유한 `dt`에서는 Python 독립 opacity로 구한 BE survivor를 사용한다.
유한 `dt`의 native survivor rate를 초기 광자 순간 rate와 직접 비교하지 않는다.
`IgmPhotoInput`은 광자 stock을 변경하지 않는다. native transport의 photon sink를
Python photon reaction으로 다시 적용하지 않는다.

`nHe=nH*fHe`, `ne=nH*x+nHe*(y+2*z)`이다. proper absorber density는
`[nH*(1-x),nHe*(1-y-z),nHe*y]`이다. Verner fit activation
`[13.60,24.59,54.42] eV`와 실제 binding
`[13.598434599702,24.587389011,54.41776] eV`를 구별한다.

RR kinetic cooling은 native `rr_cooling*ne*n_ion`이다. manufactured `alpha`,
`beta`, `xi_RR`는 이 실험의 native 입력이 아니다. DR 저온 branch에서 반응과 cooling이
꺼지는 소스 동작 및 excluded cooling diagnostic을 그대로 둔다. CE의 밀도 prefactor는
`[ne*nHI,ne*ne*nHeII,ne*nHeII]`이고 freefree는
`ne*(nHII+nHeII+4*nHeIII)`이다.

micro ledger는
`thermal_micro + binding_micro + escape - photo_input - cmb_to_gas = 0`이다.
RR/DR binding 방출과 RR/DR/CE/freefree kinetic 방출은 bolometric escape가 소유한다.
이 ledger만으로 escaping photon spectrum·각도·source age를 정할 수 없으므로
UV photon inventory에 임의로 재삽입할 수 없다.

이번 검증은 H/He nuclei·charge·photon 수·흡수 에너지·thermal/binding/escape/CMB를
독립 식으로 확인한다. frozen `b=0,+0.1,-0.1`는 signed geometry point control이며
시간에 따른 shear work 검증이 아니다. stiff-opacity control도 고정 opacity BE 흡수의
검증이며 온도 의존 coupled solver의 stiff 정확도나 양성성 증명이 아니다.
각도·spectral·proper-time 수렴과 source-age 이력, baryon recoil, two-way Einstein work,
실제 Bianchi z=20→4 trajectory는 이 단위에서 완료로 표시하지 않는다.

기존 PR150 source005 q512/q1024 terminal receipts는 모두 z=4 도달을 기록한다.
이 작업은 해당 캠페인·epoch·checkpoint·binary를 재시작하거나 수정하지 않는다.
그 represented-interval 완료와 새 Bianchi 이력의 물리적 과학 승인은 서로 다르다.
