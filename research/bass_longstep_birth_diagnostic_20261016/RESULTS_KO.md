# PR167: BASS 481-point / REI H/He 장구간 시간수렴 인과 분해

기준은 REI PR162 `6f0864e017e2d1df8cae932263b7eebc917df302`와 PR159 native source `64a6dc33873e8be494f78e580a577c8083064eb1`이다. BASS 입력 CSV SHA-256은 `1104845a34658b7c99ba4d7731a955c11457cf5c9ab92b1cf49117de462b663f`, producer receipt는 `32b9690e3842c5eeeb64e453fabc1895ab6bf5e27678975521e9f945dc5cc67e`이다. 두 case의 초기 H/He, 광자 stock, source spectrum, 481-point geometry와 총 `Δln a=4e-4`를 고정했다. 각 mode가 바꾸는 연산자는 [NATIVE_CONTRACT.md](NATIVE_CONTRACT.md)에 명시했다.

## 원본 재현과 A/B 결과

원래 PR159 실행 파일과 원래 Newton 허용오차 `1e-11`을 유지한 4/8/16/32/64/128단계 행렬을 COLD_FLRW와 SIGNED_MINUS에서 실행했다. 84/84 사례가 exit 0이고, PR159 4/8/16의 T, H/He 및 photon source 수치가 정확히 일치한다. 온도 연속 차이의 4/8/16 비율은 각각 `0.6518532699667154`, `0.6518567733578488`이다. 원래 mode의 8/16/32, 16/32/64, 32/64/128 비율은 COLD에서 `0.577373828682692`, `0.5901945944709525`, `0.6545480815728852`; SIGNED에서 `0.5773594037777817`, `0.5902089947254489`, `0.6545507416053857`이다.

Newton만 `1e-13`으로 조인 lane의 최종 온도 변화 최대치는 `5.41e-10 K`이다. 동일 BE를 유지하며 old/newborn quadrature를 분리한 `split_be`와 legacy의 차이 최대치는 `1.62e-7 K`이다. 같은 분리 표현에서 newborn만 uniform proper-birth의 frozen-opacity `φ₁(-τ)`로 바꾸면 최종 온도가 최대 `6.93e-4 K` 달라진다. 따라서 이 구간에서는 Newton 종료오차가 관측된 온도 차이의 지배항이 아니고 birth operator가 큰 영향을 준다. 이는 **정확도 개선이나 전체 수렴 이상 원인의 증명은 아니다.**

59개 사례의 양의 accepted optical node에서 frozen-opacity counterfactual의 old-BE−exponential photon bias는 모두 양수, newborn-BE−uniform bias는 모두 음수였다. COLD 16-step `split_be`의 누적 값은 각각 `+3.4010246061301896e-8`, `−3.6551214065289944e-8 photons/H`, 합 `−2.5409680039880486e-9 photons/H`이다. 이 양은 frozen-slab 진단이며 nonlinear native H/He 오차 분해와 동일시하지 않는다. 72개 사례에 compact optical 분포가 있고 원래 compiled binary의 12개 사례는 optical node 진단이 `NOT_MEASURED`이다.

혼합 연산자는 고정 slab의 정상 stock도 바꾼다. `τ>0`에서 `N*_{BE-old+uniform-new}=(S/τ)(1+τ)φ₁(-τ)>S/τ=N*_{exact-old+uniform-new}`이며 부등식은 `exp(τ)>1+τ`에서 따른다. 양쪽 시간 kernel을 같은 frozen opacity에서 일치시키는 `full_exponential_frozen` 대조 mode를 추가했다. 7개 `τ`와 세 H/He species의 광자수, 사건, 에너지, photo-rate 및 정상 stock 테스트가 통과했다. 이는 고정 slab의 수학적 성질이며 변화하는 불투명도의 native 참값 정확도를 보증하지 않는다.

## 세분화와 종료시각

128/256/512/1024단계의 동일 종료시각을 위한 마지막 단계 보정은 최종 `a` 차이를 최대 `6.94e-18`, COLD proper-time 차이를 최대 `1.8711 s`, SIGNED를 최대 `1.8736 s`로 제한했다. 보정 전 4–128 행렬의 시간차 최대치는 약 `71.3 s`였다. 종료시각 보정은 output identity와 epoch에 묶여 있다. 보정 후 COLD legacy 온도는 128/256/512/1024에서 `8.699152054508284`, `8.699114622456744`, `8.699075805079607`, `8.699043678460669 K`이다. 128/256/512 및 256/512/1024 차이 비율은 `0.964311715560193`, `1.2082621333716959`다. Uniform-birth의 같은 비율은 `0.428418902805573`, `1.0897720168394585`이다. SIGNED case도 각각 legacy `0.9643276560996257`, `1.2082808003903722`; uniform `0.4284891805507607`, `1.089808942120431`이다. Uniform-birth의 32/64/128 차이 비율 약 2는 128/256/512에서 유지되지 않는다. 여기까지 어느 lane에도 점근 차수나 참값 오차 개선을 승인하지 않는다.

2048-step probe도 COLD/SIGNED 두 case의 legacy 및 혼합 uniform mode 4/4가 exit 0, 모든 보존량과 restart 조건을 통과했다. COLD의 512/1024/2048 온도 차이 비율은 legacy `1.4616785905130196`, uniform `1.4961266420916333`; SIGNED는 `1.4616952740300073`, `1.496147531164568`이다. 여전히 점근 1차 비율 2에 도달하지 않았고 2048단계의 두 mode 간 온도 차이는 약 `1.35e-4 K`다. 원시 결과와 판정은 [REFINED_ANALYSIS.json](evidence/ncp_refined/REFINED_ANALYSIS.json)에 있다.

`full_exponential_frozen`의 COLD/SIGNED 두 case, 4/8/16/32/64/128/256/512/1024/2048 총 20/20 실행도 통과했다. 이 mode의 4/8/16 온도 차이 비율은 COLD `0.6186295106077384`, SIGNED `0.6186079320878725`로 여전히 비점근이다. 128/256/512, 256/512/1024, 512/1024/2048의 COLD 비율은 `1.2336875894938668`, `1.5432858419462692`, `1.7495861376151771`; SIGNED는 `1.2337134791330542`, `1.5433020650744875`, `1.7496017862637943`이다. 마지막 triplet은 legacy `1.46168`, mixed uniform `1.49613`보다 점근 1차 비율 2에 가깝다. 이것은 **같은 입력에서 관측한 수렴 경향 개선**이며 아직 극한값이나 절대 정확도 개선의 증명은 아니다. COLD 2048-step 온도는 legacy `8.699021699197138 K`, mixed uniform `8.698886573646663 K`, full exponential `8.699008816710384 K`이다. 서로 다른 mode의 값 차이를 참값 오차로 간주하지 않는다.

## 물리·실행 판정

84개 행렬의 최대 절댓값: photon residual `3.5575383784680614e-20 photons/H` (분모 `max(source_n,1)=1 photons/H`, 원래 정규화 tolerance `1e-8`), energy residual `7.761595186006609e-13 eV/H` (분모 `max(source_u,1)=1 eV/H`, tolerance `1e-8`), Hamiltonian normalized `6.142855769477296e-16` (tolerance `3e-12`), Raychaudhuri normalized `6.258029058584578e-16`, instantaneous gas owner normalized `2.5138640689914633e-16` (tolerance `1e-12`), step source residual `3.8116482626443515e-21 photons/H`, restart max absolute difference `0`. 모든 gas temperature는 양수이고 최소 `8.100923426668817 K`이다. 실제 midpoint source emissivity의 초기값 대비 최대 상대 변화는 약 `0.00116`으로 단일 초기시각에 고정되지 않았다.

독립 Python binary64 재계산의 원시 기하 잔차·분모·단위·허용오차는 [GEOMETRY_RESIDUAL_RECOMPUTE.json](evidence/GEOMETRY_RESIDUAL_RECOMPUTE.json)에 있다. 예를 들어 SIGNED_MINUS 최대 정규화 Hamiltonian 행은 `1.3684555315672042e-48 / 6.183858845644455e-33 s^-2 = 2.2129475554427692e-16`, 해당 원시 허용오차 `1.8551576536933364e-44 s^-2`다. 최대 정규화 Raychaudhuri 행은 `1.232595164407831e-32 / 2.8818799486665023e-17 s^-1 = 4.277052432313063e-16`, 원시 허용오차 `1e-26 + 3e-12|dH/dln a| = 1.0086456398459995e-26 s^-1`다. Rust와 Python의 부동소수점 연산 순서 때문에 최대 행의 마지막 비트는 다를 수 있으므로 Rust 최대값과 Python 원시 행을 동일한 하나의 행으로 취급하지 않는다. Signed `s/H` 검사 tolerance는 `2e-12`; 독립 최대 원시 차이는 두 case 모두 `0`이고 SIGNED의 `Σ−√3|s/H|` 최대 차이는 `3.469446951953614e-18`이다.

24개 동일 종료시각 실행은 모두 exit 0이고 photon normalized 최대 `2.710505431213761e-20`, energy normalized 최대 `2.2234818153332725e-14`, restart 차이 `0`, geometry clock residual `0 s`였다. 원래 수치 tolerance는 변경하지 않았다. 새 연구 mode의 checkpoint는 `BASS_REI_CHECKPOINT_V2`로 algorithm/Newton tolerance와 원래 source/geometry/config/state/output/epoch를 묶으며 V1과 교차 사용을 거부한다. 기존 production 기본 mode와 checkpoint는 수정하지 않았다.

Full-exponential 20개의 최대 photon normalized는 `3.7269449679189215e-20`, energy normalized는 `7.818411716653539e-13`, Hamiltonian normalized는 `6.142855769477296e-16`, Raychaudhuri normalized는 `6.258029058584578e-16`, restart 차이는 `0`이다. Newton accepted 최대 잔차는 `9.173208976207481e-12`로 원래 `1e-11` 안이다. Source midpoint 및 instantaneous H/He owner 검사는 [REFINED_ANALYSIS.json](evidence/ncp_refined/REFINED_ANALYSIS.json)의 개별 run acceptance에 포함한다.

NCP Rust 대상 테스트는 최종 `axbi_bass_dynamic` 13/13, `axbi_covariant_transport` 7/7, `axbi_driver` 13/13, Python replay는 22/22 통과했다. 최종 13개에는 독립 검토에서 발견한 direct `chemical_stage` 무신생광자 경로의 FullExponential operator 누락을 수정한 회귀 테스트가 포함된다. 20개 full-exponential history는 이 API 수정 전 바이너리로 실행했으며, 모든 history가 newborn 인자를 전달하므로 그 경로의 연산자는 동일하다. 이전 binary SHA와 최종 수정 소스 identity는 구분해 보존한다. GitHub CI는 상속된 `cargo fmt --check`에서 실패하여 native CI 테스트가 실행되지 않았다. 이는 NCP의 Rust 테스트 결과와 별도로 기록한다. 첫 NCP build에서는 이전 staging의 `include_str!` 원본 파일 누락으로 exit 101이었고 정확한 원본 복원 후 성공했다. 1024-step 첫 세분화는 예제의 512-step 상한에 걸려 exit 2였고 상한만 입력 단계 수로 수정한 뒤 512-step 원본 parity가 0차이, 1024-step 실행이 성공했다. 원본 실패 로그를 보존했다.

NCP에서 owner 작업과 분리한 캐시 및 본 연구의 재생성 가능한 build target을 정리했다. 마지막 target 삭제 전후 사용 가능 공간은 `8,462,286,848 → 8,787,877,888 bytes`로 `325,591,040 bytes` 증가했다. 별도로 본 연구의 중복 staging 약 412 MiB를 원본 checksum 검증 후 삭제하고 inactive npm/pip cache 약 1.17 GB를 정리했다. owner source/checkpoint/result는 삭제하지 않았다. 최종 디스크와 1/2/4/8/16-worker 실측은 [NCP_RESOURCE_AND_DISK_CLEANUP.json](evidence/NCP_RESOURCE_AND_DISK_CLEANUP.json)에 있다.

## 과학적 범위

`DERIVED`: frozen opacity, uniform proper-birth scalar 식, old/newborn BE bias의 반대 부호 가능성 및 혼합 mode의 잘못된 정상 stock과 full-exponential frozen-slab 정상 stock. `NUMERICALLY_CHECKED`: 84개 native A/B, optical counterfactual, 동일 종료시각 24개, 2048-step probe 4개, full-exponential 20개 및 위 잔차. `IMPLEMENTATION_VERIFIED`: opt-in mode, source-bound V2 restart, 원래 lane parity 및 대상 Rust 테스트. `HOLD`: 절대 정확도 향상, 점근 수렴 차수, native 장구간 이상의 유일 원인, gas momentum counterpart `Qᵃ`, stellar recoil, polarization, full Einstein–Boltzmann EoR admission.
