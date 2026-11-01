# REI 26-event: 전역 광자 source의 정확한 유한 변화 및 remainder, 2026-11-01

**Owner:** `cosmosapjw-quantum/rei_bianchi`; 독립 원본 PR #332 HEAD `2e3305c8ba9bff5d00412c5d79d9c1aa1e6f6e9a`. 원본 accepted tick 160/131072, 46,080 H/He 셀, 원본 frozen archive SHA-256 `a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b`; source state array SHA-256 `cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab9999e7e3508a5161edb01`. 원본 REI 26-event MPRK22(1)+Alexander SDIRK2와 4개 광자군·3개 공유 중성종 소유권을 변경하지 않는다.

## 물리 질문 및 정확한 적용 범위

기존 연구의 한 점 또는 네 개 부모 방향만으로는 엄격한 전체-X 부동소수점 검증을 인정할 수 없다. 대신 원본 모델 `_explicit_photo_fields`의 비선형 *전역 분모*가 원본 부모 상자에서 얼마나 변할 수 있는지를 정확한 유리수 산술로 bound한다. 이 source submap의 수학적 상태는 `derived/exact-in-represented-inputs`이며, 원래 26-event **전체** step-doubling 차이 연산자의 판정은 `UNRESOLVED`다.

한 source 시간과 광자군에서 `S_s=Σ_i N_{s,i}`는 원본 46,080개 셀의 중성종 수, `E`는 source owner가 정의한 외부 광자 sink, `C_s(z)`는 원본 BASS/REI 물리 소유자의 cross-section, abundance/geometry normalization에 따른 유효 계수다. `A=(C_HI S_HI,C_HeI S_HeI,C_HeII S_HeII,E)`, `D=Σ A_j>0`, `p_j=A_j/D`. `p`는 해당 광자군의 종별 흡수와 외부 sink 비율이며, 원본 `J_g`의 일부를 이들로 분배한다. 26-event 독립 반응 전체를 직접 대표하지 않는다.

원본 source box `A_j∈[A_j^-,A_j^+]`와 그 내부 참조점 `A0`에서 `δ_j=(A_j-A0_j)/D0`, `η=Σδ_j`, `p0_j=A0_j/D0`, `L_j=δ_j-p0_jη`라고 놓으면 **정확히**

`Δp_j = L_j/(1+η)`, `R_j=Δp_j-L_j=-L_jη/(1+η)`.

`η∈[η-,η+]`, `η->-1`이 배제된 경우, `L_j∈[L_j-,L_j+]`를 동일한 4변수로부터 구해

`|Δp_j| ≤ max(|L_j-|,|L_j+|)/(1+η-)`,
`|R_j| ≤ max(|L_j-|,|L_j+|) max(|η-|,|η+|)/(1+η-)`.

`L_j=(1-p0_j)δ_j-p0_jΣ_{k≠j}δ_k`의 부호 구조를 보존한다. `p_j`의 범위도 다른 모든 A 경계와 자기 A의 단조성을 사용해 별도로 계산한다. **구조적 0은 수학적으로 0**으로 유지하고, 마지막 수치 출력 상계는 정확 유리수를 IEEE float로 올림한다. 이 산술 보존은 원본 source의 실수 산술로 해석한 *표현된* 이진 부동소수점 계수/구간에 대한 조건부 주장이지 원래 전체 solver의 반올림 오차 인증이 아니다.

## 실제 물리 결과 및 재현

`finite_remainder.py`: 외부 응답을 포함한 정확 유리수 formula, 총 광자 수 보존, 수동 16-corner 전수검사와 100개 내부 유리수 경로를 포함한 자기 적대적 테스트.

`run_original_source.py`: PR #332의 원본 SHA-locked source 코드로 실제 accepted 46,080 셀을 읽고 neutral species S의 원본 outward interval을 사용한다. tick160 시작·중간·끝 등 5개 **frozen-parent clock probes**에서 원본 네 광자군 p, `Δp` 상계, 1차 remainder 상계, photon absorption/heat rate의 bounded source-share change를 계산한다. 이 다섯 시간점은 **실제 원본 full/half 단계 상태를 역으로 복원한 것이 아니다**. `source time`과 `stage population`은 구분한다.

`RESULT.json`은 성공한 원격 과학 실행에서만 생성되며, 결과와 status를 합치지 않는다. 외부 photon current 자체가 변하는 효과, 셀별 중성 입자 numerator 변화, thermal SDIRK roots, MPRK stage transport, Hummer–Seaton event 분기와 전구간 IVP는 이 결과의 scope 밖이다. 과학적 구간 인증은 owner source/상관관계가 보존된 전체 D_h derivative+uniform remainder 후에만 가능하다.

## 원래 병목 및 DAG

기존 원본 `[160,161]` logT cross-box 상계 `2.1245050576368385e-4`, strict gate `2e-4`, public-width gate `2e-3`; 모두 **그대로**다. 이전에 인정된 endpoint=3, accepted tick=160, REI CENTRAL=28/88, WORKING=33/88, FAST=4/7, canonical Δ=0. 이 unit은 accepted canonical node를 만들거나 기존 CI/원장 기록을 바꾸지 않는다. `NO_MERGE`, `NO_FORCE_PUSH`, `PRODUCTION=HOLD`, `AUTO_NEXT_NODE=false`.

문헌: Neher, Jackson & Nedialkov (2007), DOI 10.1137/050638448 (validated ODE의 wrapping/dependency), Pawlik & Schaye (2011), DOI 10.1111/j.1365-2966.2010.18032.x (multi-frequency H/He photon conserving thermochemistry). 양 논문은 이 실행을 독립 검증하지 않는다.
