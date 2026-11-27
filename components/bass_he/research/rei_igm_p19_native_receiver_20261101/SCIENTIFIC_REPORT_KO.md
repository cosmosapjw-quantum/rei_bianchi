# BASS_HE → 원본 REI Bianchi IGM: P19 effective UVB 와 native H/He photon-owner 물리 비교

2026-11-01 | SOURCE-CONDITIONAL REI receiver binding diagnostic | **중앙 REI 28/88, BASS_HE 14/18, 추가 승인 0**

## 1. 원본 authority와 물리 가정

이번 과제의 실제 소유 저장소는 `cosmosapjw-quantum/BASS_HE`다. 기존 BASS_HE Draft PR #141 HEAD `4cf5cd7fe0bf3e7811ceabd1ff94e4a03354b167`의 2019 Puchwein–Haardt–Haehnelt–Madau MNRAS 485 Table D1 *fiducial non-equilibrium effective* UVB 원자료 13-row 수치 projection을 사용한다. 표의 전체 저자 ancillary 원본 바이트임을 주장하지 않는다. P19 D1 입력 전체 ZIP SHA256 `cc62c1d046be912e50e712bf2ac94d46890a472896673c2407133bca9b0e3543`, source CSV SHA256 `67a601ed4486a1ac03bc5ac08929219c3ed7fbd59f94ec40f442137bd8896124`.

원본 REI 물리 소비자는 repo `cosmosapjw-quantum/rei_bianchi`, PR #320의 **실제** 첫 canonical interval tick160 승인 H/He/T 46,080-node source와 PR #332의 **실제** original 26-event 4-group photon-owner event output이다. PR320 archive SHA256 `48ad5c6f0922ad946a10a89ce17fefd2c7241ac956b6bac194892a42810312a7`; PR332 Actions ZIP SHA256 `4f332c7a9c21f93dcfadb0d7e4e40ef4ec7ec7f150f6d4b8b39f309560155e17`; original accepted state array SHA `cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01`. Native original heating calibration CSV exact Git blob `2dbcd3db376fcfad27a19a992814fdd33aea547b`, repo original `bdf_heating_moment_calibration.csv`, 12 species×group rows. Original **PR344** (이 스레드에서 잘못 REI에 게시한 소유권) Draft/HOLD로 그대로 두며, BASS_HE 원본 자료의 authority로 승격하지 않는다.

P19 rate는 high-z EoR **neutral-weighted effective homogeneous** rate다. 원래 native REI는 46,080개 노드의 HI,HeI,HeII 원자수 합을 공통 분모로 쓰는 photo-absorber allocation의 실제 photon current를 계산한다. **두 rate를 같은 local ionized-bubble Γ 로 취급하지 않는다.** 두 물리 모형의 동일 적색편이 `z=5.95`에서의 *고정 원자수 물리 비교*이며, 이 comparison은 accepted RUX04 source scenario 또는 새로운 IGM/BI initial-value run이 아니다.

## 2. 정확한 계산식과 단위

REI 원본의 4개 주파수 group g, HI/HeI/HeII species s에서 `r_sg,i = J_g c_sg N_s,i / (E_g + Σ_t c_tg Σ_j N_t,j)`은 **atoms/s**다. 각 종의 원본 전체 중성 원자수 `S_s=Σ_j N_s,j`를 사용해 `(Γ_s)^REI = (Σ_g,i r_sg,i)/S_s`를 정의한다. native `Γ^REI`는 이 소유 모델의 *global neutral-count-weighted* 평균 사건률이며 local observational photon flux가 아니다. `E_g`는 original native external subgrid photon-absorption owner이며 P19 excess energy와 구별한다.

`P19` 로그 선형 source 보간은 `lnΓ(z)= (1-λ)lnΓ(5.81)+λlnΓ(6.14)`, `λ=(5.95−5.81)/(6.14−5.81)=0.42424242...`; `ℋ_s(z)`에도 별도로 적용한다. 대조 시나리오로 rate 선형도 계산한다. 실제 원래 원자수만 고정해서 `Ndot_s^P19 = S_s Γ_s^P19`, `Qdot_excess^P19 = ε_eV Σ_s S_s ℋ_s^P19`를 형식적으로 계산한다. 여기서 `ε_eV=1.602176634×10^{-12} erg/eV`; **binding threshold energy는 ℋ에 더하지 않음**. 필요한 photon threshold energy는 별도 진단으로만 기록한다.

REI native source 초과 광가열은 original source의 12종 heating table ε_sg 및 원본 현재 photon group 흡수량으로 `Qdot_native=ε_eV Σ_sg (J_gp_sg)ε_sg`로 재구성하여 original source owner JSON과 교차확인한다. 원래 각 node의 H 원자수는 원본 `r_HI,i / Γ_HI^REI /(1-x_HII,i)`에서 복원하고, HeI photon-owner로 독립 복원한 He/H 비가 원래 0.079인지 확인한다. HeII는 original fixed cosmic helium abundance `0.079 N_H,i x_HeII,i`를 사용해 nearly-unit helium fractions subtraction 오차를 방지한다. 이 재구성은 실제 accepted H/He/T 물리 상태를 입력으로 쓰지만 완전한 공분산의 동일 joint sample이라는 주장은 아님.

## 3. 실제 새 물리 결과, z=5.95

| 지표 | ORIGINAL REI native | P19 D1 log-linear (formal frozen target) |
|---|---:|---:|
| HI source ionization [per neutral/s] | 8.979866621325626e-16 | 6.491041172084541e-14 |
| HeI source ionization [per neutral/s] | 1.2378484331061336e-13 | 4.658184761206645e-14 |
| HeII source ionization [per neutral/s] | 0 within active native high-energy channel | 8.951802738113886e-18 |
| HI event demand [s^-1] | 6.104263473411741e47 | 4.4124291820849083e49 |
| HeI event demand [s^-1] | 5.0743677284306644e48 | 1.9095506197007742e48 |
| HeII event demand [s^-1] | 0 | 3.894670521419233e48 |
| source excess photoheat [erg/s] | 8.22713274931762e37 | 5.852023364265675e38 |

P19/native HI rate ratio **72.2843829**; HeI **0.3763130**. Total P19 excess heating **7.1130776×** original. Native HI mean excess heat/event **31.26185268 eV** vs P19 **4.57844095 eV**, revealing important difference in spectral shape in addition to normalization; HeI **6.35875579 eV** vs P19 **6.68202757 eV**. P19 HeII excess heat/event **38.63598575 eV**, whereas original high-energy G3 current is IEEE binary64 minimum subnormal `5e−324 photons/s`, not a resolved HeII ionization source. If the P19 effective rate were **literally** realized on the frozen REI HeII population, it would imply `3.894670521419233e48 s^-1` HeII ionizations and ionization threshold accounting `3.3956414180571354e38 erg/s`, distinct from P19 excess heat `2.4108662341369358e38 erg/s`. **이것은 새 물리적 항성 방출률 요구 조건이나 실제 저온 가열률 측정이 아니다.**

## 4. 급변 source에 대한 interpolation 민감도

동일한 발표 두 knots의 *rate-linear / log-rate-linear* 보간 비: HI Γ=**5.42217725**, HeI Γ=**3.70529300**, HeII Γ=**1.00653503**. HI excess heat rate ratio **4.46307921**, HeI **3.11434830**. 따라서 이 한 EoR cliff 내부에서 한정 보간 choice를 단순 quadrature 정밀도 오차로 축소할 수 없다. 직전 PR141의 4.5–10.9%는 z6.14–9.99 통합 구간에 대한 숫자로 지금의 interpolation cliff와 혼동하지 않는다.

## 5. 검증, RUX 소유권, 우선 다음 연구

- Python 원본 readback 3 archives SHA + 12-row original native energy table **exact Git blob** 비교, 46,080 REI original accepted node input, 46,080 native photon data node index 1:1 대응, 세 원본 lane의 숫자 동등성 재검토.
- 원본 4 group photon event closure 및 original source primary heating `8.22713274931762e37 erg/s`와 재구성 일치. 별도 72-digit Decimal 전체 46,080-row 합산과 16개 정상/16개 optimized 테스트 통과. source ratio는 수치적으로 node별 uniform, 원소비 0.079 교차검증. 0 new measured rows, 0 new original IVPs.
- **RUX02:** P19 effective six-moment 입력을 이미 확보했으나 native local photon fields와 동등하게 admission하지 않는다. **RUX03:** 원본 G3 HeII high-energy photon current는 미해결, 13.6/24.6/54.4 eV threshold 이상의 실제 group resolved source/current/opacity, early radiation history 및 P19 effective↔native source operator map owner가 필요. **RUX04:** 동일 source/clock/IC/opacity 물리 시나리오 `NOT_ADMITTED`.
- **RUX12(BASS_HE optional HE precision):** 이 비교는 새로운 high-energy nuclear event 요구를 정당화하지 않는다. 필요한 것은 원본 photon high-energy spectral boundary와 source authority다. Fast-D 등 optional library는 보존하되 중앙의 필수 gate로 삼지 않는다.
- 더 이상의 source-only atlas/point PR보다 **원본 REI owner가 실제로 소비할 수 있는 4-group photon current/absorption + heating spectrum 및 causal source history**를 목표로 한다. 중앙 첫 interval은 원래 [160,161] `2.1245050576368385e−4 >2e−4`에서 HOLD이며 이번 계산이 그 수치 오류를 해결했다고 주장하지 않는다.

문헌: [Puchwein et al. 2019, MNRAS 485, 47](https://doi.org/10.1093/mnras/stz222) original Table D1/§3.1 neutral-weighted effective UVB; [Pawlik & Schaye 2011](https://doi.org/10.1111/j.1365-2966.2010.18032.x) multi-frequency H/He photon-conserving allocation. 문헌이 REI 코드를 검증한다고 주장하지 않음.