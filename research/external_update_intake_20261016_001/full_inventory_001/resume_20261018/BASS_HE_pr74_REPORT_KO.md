# HE27 실제 native 결과 — 제한된 source-cut A/B

## 판정과 원본

DERIVED / LOCAL_VERIFIED / NATIVE_VERIFIED. HE25 PR72 `eb4952af1f3d9ca99aad300ddf6db6f2b2fe1233`, HE26 PR73 `98b31fbd779ed1ade8848580c2836f32259e3ef3`에서 격리했다. HE25 physics.Model/source quadrature, HE23 total-H 밀도 계약 및 원본 Rust owner `f7830e2f55e7a1938bc3c98f61b60651f8dae474`는 변경하지 않았다. 원본·유도·실측·남은 추정을 구분한다. source donor는 공개 Git packet에서 복원·SHA 검증했다. 예전 비공개 HE26 압축파일 자체를 복원했다고 주장하지 않는다.

원본 native persistent server SHA256 `22d11447300381d5cd02d06e13f312e3e2aa3716eaecf60d3bcdb4d436a434d5`. 이 라이브러리는 선택된 Grackle3.4.1 반응률의 Rust 포트이며 upstream Grackle 직접 실행이 아니다. 실제 8K 영역에서 DR=0; 원본 채널은 유지했다.

## 유도와 명시적 근사

기존 conserved-K 및 방향 격자에 HE26 true cut-child의 양의 N/U/3종 sigma/3종 heat 조건부 모멘트를 투사했다. moving 13.6/24.59/54.42/100eV preimage에서 먼저 나눈다. 실제 birth proper time, signed q, angular Jacobian, H*dN/dln(a), BB50000K와 총 source를 유지한다. 기존 광자 remap은 없다. 원본 fixed node로 개별 child 전체 스펙트럼을 정확히 표현할 수 없어 같은 방향·활성 band 내 양의8모멘트 cubature를 사용한다. 따라서 이는 순간 photo-kernel을 보존하는 유한 스펙트럼 근사다.

원본 v1의 조건수2.82e9 때문에 adaptive source weight에 잡음이 생겼다. 물리 허용치를 늘리지 않고 원본 physical event interval 내부 양의 source table(v2), 매우 짧은 interval 전체의 source/opacity 동일 one-sided mask(v3), 정확한 birth-frame donor factorization을 통한 validation 가속(fast)을 분리 구현했다. fast는 v3와60 source vectors 및 native pilot318요청/응답·147456cohort mode에서 bitwise 일치했다. 이것은 연산 동등성 증거이며 독립 물리 인증과 구분한다.

## 실행과 회귀

108/108 source admission, 독립 QUAD sigma×1e18 scaling/잘못된 abs-tol negative control, moving-cut partition, ±mu manufactured shell positive cut-panel/negative unsplit control, native 계약 테스트를 포함한14개 통과. 이어 v2 영향4개, v3 tiny interval3개가 각각 통과했다. 중복 scientific suite는 다시 실행하지 않았다. manufactured shell GL32의0.00515는 EoR 측정이 아니다.

총30 native study 시도 중24개 완결·검증,6개 실패/미완료 원본 보존. 17개 후속 transport matrix는17/17 통과했다. v1 adaptive 두 건 정체, v2 pilot source admission8.07140905e-5 실패, 느린 v3 reference 두 건 비용 때문에 중단, fast Radau600초 한 건98.6768%에서 시간한도 중단을 결과와 분리했다. 첫 실패 raw와 고정 소스를 보존했다. Radau는 같은 물리·같은 tolerance로900초 한도 한 번만 재실행하여585.89초에 완료했다. 다른 source/rate owner 혼합은 없다. early source-only prototype 일부는 바이트 미복원으로 admission에서 제외했으며 모든 실제 native 버전은 복원 가능하다.

## 독립 시간 기준해와 첫 과학 질문

범위 z20→19.998, proper duration804804612237.4822s, q0,m4,GL4, source table512. HE25 DOP853 T=8.239220055614581K. 새 source DOP853 T=8.239220065041529K, Radau T=8.239220065041600K. 두 새 solver의 source table SHA가 동일하고 차이는7.1054273576e-14K, 최대 이온분율 차이는1.05032e-19다. 두 solver 모두 rtol3e-11, atol_scaled3e-13을 사용한다. 실행시간 각각571.79/585.89초.

동일 원본 chemistry의 실제 유한 source A/B에서 ΔT=+9.426948111e-9K, Δx_HII=+9.305419933e-14, Δx_HeII=+2.336121951e-14, Δx_HeIII=−8.029639247e-19가 관측됐다. 이는 아래 시간·source-table 정제 차이보다 크다. **유한 K 모델에서 측정 가능한 효과**이며, 연속 스펙트럼 EoR 편향이나 관측 예측 오차로 해석하지 않는다.

## 분리된 해상도 증거

TEMPORAL_CONVERGENCE_VERIFIED_SCOPED: 동일 q0,m4,GL4에서 독립 DOP853 대비 온도 절대오차:

| n | 오차 K |
|---|---:|
|16|5.514682e-9|
|32|1.650461e-9|
|64|4.450733e-10|
|128|1.151239e-10|
|256|2.886757e-11|

정제 비3.34,3.71,3.87,3.99. 이 짧은 동일 semi-discrete 입력에서의 결과이며 전역 차수 증명이 아니다.

유한 에너지 m4→8 / m8→16 차이는 n256에서−1.299081731e-9K / −5.144329407e-12K; n128에서도 각각−1.298685604e-9 / −5.083933274e-12K다. 각도 GL4→8 차이는 q−0.005에서 n128/256 각각−5.32907e-14/−7.99361e-14K, q+0.005에서는−1.04805e-13/−9.05942e-14K다. 작은 두 단계 차이로 angular order나 관측 shear를 주장하지 않는다. source-time512→1024는 q0,m4,GL4,n256에서+3.019806627e-14K.

## 물리 수지와 자원

완결24케이스의 실제 Rust point294243개를 raw에서 독립 재집계했다. 광자수 최대잔차5.505714e-21/H, 에너지8.844921e-16eV/H, 종별5.700871e-17/H. 밀도/Y 상대잔차4.440892e-16, photoevent 체적 변환6.924221e-16, micro energy 정규화8.758115e-18. 각 case photon/birth energy, HI/HeI/HeII events/heating, physical binding, gas thermal, CI/RR/DR, Case-A escape, CMB, gas work와 redshift/shear work는 ALL_RESULTS.json/CASES.csv 및 원본 스트림에 분리 보존한다. positivity 및 Newton3e-15, density1e-9, point event2e-10, microledger2e-9, number3e-15/H, energy3e-12eV/H, source moment3e-13 계약은 유지했다.

NCP 실제64core/125GiB 환경. transport worker 최대4, 각 driver와 상속된 native child에4GiB 주소공간 한도(8프로세스 이론적32GiB), 실제 driver 약100MB; 실행 자료 live disk2GiB 한도. 측정 root disk utilization adaptive2worker47.9%, transport4worker6.2%. 기존 production job/dirty worktree는 변경하지 않았다. venv Python만 numpy/scipy 보유; system Python 준비 오류는 과학 실행으로 세지 않는다.

## HOLD와 다음 의존성

연속 spectral convergence HOLD. 고정 좁은 cutoff strip의 노드 수가 m과 함께 늘지 않는다. 독립 frozen-absorber future-kernel18조건에서 survival 절대오차 약3.58e-8/photon가 m4/8/16에서 plateau한다. 순간8모멘트 일치는 미래 exp(-tau(E))를 보증하지 않는다. 더 미세한 물리 spectrum/strip 독립 설계 없이는 이번 A/B를 연속 source-cut 물리 정답으로 승격하지 않는다. 각도 전역차수, 긴 epoch/높은 이온화 상태, 완전한 z20→4, upstream Grackle 직접 동등성, Bianchi 관측 판별, CMB optical depth/관측전망은 HOLD다. 원본 CMB 교환 ledger 검증은 관측 CMB 검증과 별개다.

C9 실제 독립 read-only review는 v1에 한 차례 수행했다. 후속 repair/fast의 영향 테스트와 raw 증거가 추가됐으나 최신 전체 source를 새 독립 review했다고 주장하지 않는다. 다음 연구 의존성은 cutoff-strip spectral resolution 및 그 독립 흡수 기준해이며 이번 bounded campaign을 재실행하지 않는다.

## 게시와 복원

새 Draft PR74: https://github.com/cosmosapjw-quantum/BASS_HE/pull/74 . 원본 PR72/73 변경·병합 없음. 현재 파일과 final publication receipt는 후속 커밋으로 구분한다. 단계별7개 아카이브는 Google Drive/Dropbox 실제 전체 다운로드 SHA 및 payload 검증 완료. 전체 source-restorable Git bundle/실행 아카이브의 최종 영수증은 results/FINAL_BACKUP_RECEIPT.json에 별도 기록한다. NATIVE_CASE_BYTE_MANIFEST는 대용량 cohort 포함 원시파일을 결속한다. 비밀 인증 자료는 포함하지 않는다.
