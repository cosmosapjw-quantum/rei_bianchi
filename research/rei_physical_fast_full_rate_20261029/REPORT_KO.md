# Physical fast F4 · source-qualified BASS 실계수와 P19 UVB의 직접 비교

2026-10-29 · PR267에서 독립된 신규 연구 단위 · PR266 Li6 lift는 읽기 전용. **결론: DERIVED + NUMERICALLY_CHECKED_SOURCE_ONLY**, original working **33/88**, central **28/88**, physical-fast **4/7**, 신규 완료 노드 **0**. `F4=PARTIAL`, `L4_ready=false`, `NO_MORE_IVPs=true`. Native independent-author R6/C9 **NOT_RUN**.

## 1. 입력과 원본성

- 기준 REI PR267 `779192ec55daf21e006b34bbc859681c9d2643ab`과 sibling PR266 `a3470c88b4bddb38a08623d37ff6aa61210e04ae`를 분리했다. PR265의 He4/H1·T inventory mismatch는 변경하지 않았다.
- BASS PR234 original SOURCE ZIP **222443 bytes**, SHA256 `6a9c84ce076a3545a992f0b364d0fd67fe1063b7a33a290dbe77d44ecee98838`; REI PR266 original master ZIP **571682 bytes**, SHA256 `ae5a774d31ae1d6f67b2dfc592d5cbb42ebd466d4f415da2a3d6b08e8`; 각각 46·53 ZIP members, 원본 자체를 복사해 보존했다.
- BASS AtomicNetwork.py SHA256 `baecce07aded483fa60006cc576feff67d068c0d70394f7095abacc6d47eaa80`, atomic_model.json SHA256 `9cc399e9e33ece544109f442f50b00c463cde96e406965e796240eaabd49c614`, REI_SAVED7 SHA256 `7653f7f75fcbe92465de1b22faabf565efee36e90d1d967499f68ff123a6bc77` 확인.
- BASS original coefficient source Git blob `2eba600a9d7a7359ca55f566f1b841a363a3e5c7`에서 129개 필수 수치상수를 추출했고, connector 읽기 결과와 로컬 binary64 배열 FNV1a64 `b8d5383717a0f023`가 **129/129 일치**. P19 PR261 Git blob `3472e57abebb55e94f8c4436f2867bfc58e9feb9`의 13×7 knot 배열 FNV1a64 `18f1eb671df4567b`도 **91/91 일치**. 이는 **수치 내용 동일성**, 원본 JSON 전체 raw-byte identity나 Puchwein 전체 59행 파일 동일성이 아니다.
- PR234 ZIP에는 원본 실행 상대경로의 provenance manifest와 native rate coefficients가 직접 함께 있지 않다. 따라서 **원본 AtomicNetwork 클래스 본문을 수정하지 않고** `_verified_inputs` loader만 위 수치 동일성 확인된 축약 테이블로 연결했다. 원래 62차원 production solver를 실행했다고 주장하지 않는다.

## 2. 물리적 정의 및 컨벤션

Metric signature (-,+,+,+), c,k_B,ħ는 자연단위로 치환하지 않는다. BASS `Y_i=n_i/n_b`, `n_e=n_b q^T Y`, 광반응 `Γ`의 단위 s⁻¹, `Gne` m³/s. BASS 원본 외부 bath는 `Q(z)=(1+tanh[(7-z)/0.8])/2`, `T_B(z)=100+11900Q(z)` K, `Γ_B(z)=Q(z)Γ_B_base`이다. 이는 REI PR259의 **300 K bath와 다른 source**이며 기존 PR259 배열/그림을 변경하지 않았다.

P19 source는 PR261 13-knot log(rate) interpolation과 nominal `β=-0.04591874303144475`, `κ=+0.0686617394805907` dex/redshift를 유지한다. H I·He I·He II의 광이온화율 세 개만 비교하며 **2.4≤z≤4.75**로 제한한다. P19을 z=20까지 외삽하거나 P19 six heating moments와 BASS의 photo energy/escape를 동일시하지 않는다. 두 source의 `z` 숫자 일치는 같은 방향별 Bianchi redshift·clock·physical trajectory를 의미하지 않는다.

REI 동결 17상태 `y_i=n_i/nHref`에 별도로 적용하는 7개 H/D/T/He photo event stoichiometric matrix를 `S∈R^{17×7}`라 놓고 각 사건 원천 `s_j`, 도착 `d_j`를 정의한다. 3-반응률을 7사건으로 복제하는 D에 대해

`F_photo^M(y,z)=S diag(y_src) D Γ_M(z)`, `J_photo^M=S diag(DΓ_M) E_src`, `M=BASS 또는 P19`.

따라서 `ΔF_photo = S diag(y_src) D(Γ_B-Γ_P)`, `ΔJ_photo = S diag(D(Γ_B-Γ_P)) E_src`. `A17^T S=0`, `q17^T S=(1,1,1,1,1,1,1)`, `rank(S)=7`. Wolfram에서 7, 보존 0, charge 1, 전자 생성 항등식 0을 실제 반환했다. 모든 7개 저장 y의 해당 neutral/charged 출발종은 양수이고 세 원천 비율도 다르므로 이 **photo-only** 벡터 연산자는 두 model에서 같지 않다.

## 3. 원래 두 source에서 얻은 수치 결과

중앙 저장점 `z=3.603019593287379`: `Γ_B=[9.997950318600802e−13,6.224561803094644e−13,3.114250389141558e−14] s⁻¹`, `Γ_P=[7.92450298729798e−13,3.5385535519733145e−13,9.118838604265123e−17] s⁻¹`. 고정 REI 상태에서 `q17^TΔF_photo=+2.2585382717677727e−16 electron/Href/s`. 이는 **순간 counterfactual event rate difference**이고 실제 궤적에 대한 민감도·τ 차이가 아니다.

| 저장 mean z | Δelectron source (Href⁻¹ s⁻¹) | 공통 진폭 최적 max-relative 잔차 | 전자만 맞춘 진폭 u_e | 전자만 맞춘 뒤 ||ΔF17||₂ (Href⁻¹ s⁻¹) |
|---:|---:|---:|---:|---:|
| 2.404494 | +4.836587e-17 | 0.714707 | 0.731431 | 3.319844e-17 |
| 2.789073 | +8.306254e-17 | 0.914379 | 0.679950 | 4.733098e-17 |
| 3.217095 | +1.455346e-16 | 0.986346 | 0.630513 | 6.109270e-17 |
| 3.603020 | +2.258538e-16 | 0.992639 | 0.602951 | 7.329651e-17 |
| 4.024262 | +3.353231e-16 | 0.995380 | 0.594402 | 8.829531e-17 |
| 4.378370 | +4.336072e-16 | 0.996732 | 0.605520 | 1.025042e-16 |
| 4.701690 | +5.139969e-16 | 0.997685 | 0.630112 | 1.175811e-16 |

더 자세한 7개 저장점의 원 rate, source·Jacobian·부호·rescale과 residual을 `results/COUNTERFACTUAL.json`에 그대로 저장했다.

## 4. 계산 가능한 rate-shape 식별성 결과

서로 다른 두 양의 rate vector `B_j,P_j`를 단일 양의 amplitude `u`로 맞추는 문제에서 `a_j=B_j/P_j`라 하면

`min_{u>0} max_j |u a_j-1| = (a_max-a_min)/(a_max+a_min)`, `u*=2/(a_max+a_min)`.

증명: `a_min u -1`와 `a_max u-1`의 절댓값을 균등하게 만드는 양수점이 두 극값의 최솟값을 달성한다. 이는 기존 PR265의 inventory minimax의 **source-rate 적용**이며 일반 kinetics no-go의 새로운 문헌 novelty 주장은 아니다.

중앙 z에서 `u*≈0.0058346`, `max-relative residual≈0.992639`다. He II의 P19 rate가 매우 작아 이 상대 잔차는 He II가 지배하므로 아래 charge-weighted 절대 source 검산을 함께 기록한다.

총 전자 생성 source만 맞추려면 `u_e=(Σ y_src,j Γ_P,j)/(Σ y_src,j Γ_B,j)`를 선택한다. 그러면 순간적으로 `q17^TΔF=0`이지만, 7개의 독립 source reaction과 다른 세 rate ratios 때문에 `ΔF≠0`이다. 중앙 z에서 `u_e≈0.6029511`, `||ΔF_photo||₂≈7.3297e−17 Href⁻¹ s⁻¹`. 7개 저장상태 모두 같은 구조의 scalar observable degeneracy와 nonzero chemistry-vector defect가 확인된다. 이는 `n_e(t)`, 물리 τ나 CMB posterior의 동등성을 의미하지 않는다.

## 5. 실행 검증, 오류 보존, 자원

- 원본 BASS `AtomicNetwork.rates/evaluate`를 **실제로 실행**하되 공급 계수 로더만 source 고정 투영본으로 대체했다. Native H photo normalization과 Li 80eV cross-section reference, H/D/T 및 He/Li isotope equality, 21×21 Jacobian, 8 directional FD checks, baryon/charge/event, 13 photo index, positive/invalid input, P19 3.6 nominal anchor, numerical fingerprints, minimax와 electron matching을 검증했다.
- 최초 Python unittest `test_native_rate_calibration`은 원본의 photo indices 13을 14로 예상한 test-only FAIL. source/허용오차/방정식은 수정하지 않고 기대값만 정정해 10/10 PASS. 이후 129/91 numeric identity 보강 12/12 PASS, minimax 및 electron degeneracy 보강 최종 **14/14 PASS**. 원 실패 stderr와 수정 내역 보존.
- 측정된 4개의 bounded Python test jobs CPU(user+system) = 1.14 + 1.36 + 1.28 + 1.25 = **5.03 s**. 추가 결과·패키지 생성/authoring/host/network 비용 UNKNOWN_NOT_ZERO. `ulimit -t 8`, 0 new IVP, 0 prior full campaign replay. 별도 native independent-author R6/C9 리뷰 NOT_RUN, full CI PASS NOT_CLAIMED.
- Thread-local temporary double ceiling의 original main600→1200 CPU s를 누적 미초기화로 적용하며, 기존 main 누적 약614.010604+이번 측정 5.03=**최소619.040604 s**(추가 미계측 비용은 더해지지 않음)이다. Presentation 70.36>double60, planning20.819>double20 때문에 새 그림·별도 planning numerical run은 실행하지 않았다. 작업 종료 후 original ceiling600/30/10 복원, historical debt 보존.

## 6. 최신 관련 저장소·claim gate

REI #266(Li6 BASS internal lift), #267(rank-one), BASS #254(Ce1-N source polynomial cache), BASS_HE #110(DD angular), bass_cr #124(Ferrers), rec_bianchi #157(HD adapter), WU088_HH #162(molecular ionization), vigilode #114(source certificate), htt_base #564(report route)를 최신 PR 목록에서 확인했다. 이전 51 repo/2503 branch census를 참조했지만 이 세션에 51 repo 전체 branch·commit을 재열거한 것은 아니다. 이들 연구는 현재 두 UV source를 동일하게 해주는 clock/rate/geometry/initial-state 계약을 공급하지 않는다.

**원본 node 증가 0**. source-shape 차이는 이 두 source/세 광반응률/동결 저장점이라는 범위에서 반증됐고, 전체 REI↔BASS 물리적 모델 일치 불가능성을 증명한 것은 아니다. 실제 동일 원천 21/17 chemical rate config와 Li6/T/fast reservoirs, nHref/nb, H,K, full J, directional redshift, physical τ, true different-author R6/C9가 남았다.

**다음 최소 노드:** `COMMON_SOURCE_RATE_AND_INVENTORY_ALIGNMENT`: user-authorized same physical source/initial isotope inventory와 rates를 source-qualified로 지정하고, 그 모델에만 full chemistry projection defect를 계산한다. 원래 입력을 몰래 보정하거나 새 IVP를 돌리지 않는다.

원전: Puchwein, Haardt, Haehnelt & Madau (2019), MNRAS 485, DOI 10.1093/mnras/stz222; Tóth, Li, Rabitz & Tomlin (1997), SIAM J Appl Math 57, DOI 10.1137/S0036139995293294. 여기의 수치 source mismatch는 원전의 직접 주장 인용이 아니라 제공된 원본 코드·입력을 결합한 **새로운 계산 결과**다.
