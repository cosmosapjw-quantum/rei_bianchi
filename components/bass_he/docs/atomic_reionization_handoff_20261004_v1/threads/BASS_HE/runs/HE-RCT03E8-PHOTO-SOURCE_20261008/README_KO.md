# RCT03E8: E7 선택형 photo-electron source 분해

상태: `PINNED_E7_PHOTO_ELECTRON_SOURCE_AND_SYMMETRIC_ATTRIBUTION_PASS__OWNER_LIVE_AND_HEAT_OPEN`.
E7의 385시각 × OFF/KF96/GM25 세 조건에서 실제 저장된 Gamma per absorber, x_HII/y_HeII/z_HeIII, nHe/nH를 함께 사용했다. 새 native/coupled 실행0, 기존 RCT03E6/E7 과학 suite 재실행0.

전자 광이온화 source [electrons/(H s)]: `(1-x)*Gamma_HI + (nHe/nH)*[(1-y-z)*Gamma_HeI+y*Gamma_HeII]`.
대칭 finite attribution `delta(nu*Gamma)=mean(nu)*deltaGamma+mean(Gamma)*delta(nu)`. 이것은 인과적 유일 기여율이 아닌 exact bilinear identity.

최종 공통시각 step384에서 KF-OFF `+5.438774410948304e-22`, GM-OFF `+9.243278362850567e-21` electrons/(H s). 각각 occupancy term 약 87.96%; rate term 약 12.04%. 저장 node 숫자에 대한 3080 exact decomposition + 2310 species/전자 identities; 새 Python 16 tests와 75 Decimal same-input comparisons PASS. 실제 연속해 오차 인증은 아니다.

Owner의 기존 25행 native 짧은 이력은 E7의 385행과 시계가 달라 명시 거절했다. Owner 모양으로 투영한 synthetic fixture의 schema-PASS는 native adoption이 아니다. 소스 첫 에너지 모멘트가 없으므로 photo heating은 null이며, E7 35eV RCT closure를 흡수열로 바꾸지 않는다.

교차참조: bass_cr R12는 저장 상태/분광 모멘트 귀속, WU088_HH XTHREAD01은 Gamma 증가와 neutral-weighted absorption 감소가 양립, rei_bianchi BRIDGE12는 고온 첫 cell의 조건부 continuous defect. 다른 모형/시계/온도 guard의 수치 인증을 HE로 이전하지 않는다.

전체 코드 `code/electron_transfer.py`, `code/consumer_rates.py`, `code/verify_science.py`, tests, source histories/sidecar, 770 paired rows, RED/GREEN evidence와 전체 보고서는 immutable ZIP에 있다. Git projection은 실행 코드 전체가 아니며, root/consumer 원본 코드를 수정하지 않았다.

다음: `RCT03E9_OWNER_NATIVE_OUTPUT_IDENTITY_AND_SOURCE_TRANSFER`. Baseline RCT OFF, photon/heat/recoil moments null, physical HOLD, HE-F2/F09 global OPEN.
