# C2e 충돌 영역·입출력 authority 회수

원 사용자 계약은 **0.5 및 5 keV/u를 우선 조사 에너지로 지정**하고, 전자모형을 고정한 뒤 **직선·Coulomb/Rutherford·고전 결합 핵궤적을 비교**하도록 한다. 그러나 하나의 production 궤적, 공통 collision energy frame, 핵질량, 유한 충돌매개변수 구간, 시간 창 또는 production R 구간을 고정하지 않는다. 기존 코드의 선택값과 문헌의 좌표계를 조합해 빈칸을 채우지 않는다.

이 회수의 authoritative repository revision은 `67ba38b0e8665543840fcb674bb8310fd47f7266`, tree는 부모가 고정한 `865b463d56ab646507a708d57247cb43086f6609`다. `domain_inputs/INPUT_MANIFEST.json`은 실제 회수한 UTF-8 파일의 SHA-256·bytes·Git blob identity·원 경로를 보존한다. `USER_CONTRACT_ORIGINAL.txt`의 line number는 보존한 원문 기준이며 전체 1528행을 확인했다. 이번 작업은 문헌 PDF를 새로 검토하거나 과학 계산을 재실행하지 않았고, 이전 source ledger의 문헌 판정은 inherited evidence로 수입한다.

## 사용자 지정과 미지정

| 항목 | 원 사용자 계약의 명시 내용 | 회수 판정 |
|---|---|---|
| 전자 문제 | one-electron, spinless, nonrelativistic, clamped point-Coulomb, fixed finite R>0, lowest m=0 및 bright \|m\|=1, charge-center O, lines 108–125 | 기존 fixed-sector 문제의 전제. 핵 collision 궤적의 지정은 아님 |
| 우선 충돌 에너지 | 0.5 keV/u, 5 keV/u, 주변 source-native energies, lines 886–891 | 에너지 두 token은 명시. 연속 production energy interval은 미지정 |
| 에너지 frame·isotope | source별 조사 항목, lines 443–457 | source별로 회수해야 하며 하나의 lab/COM convention은 원문에서 미지정 |
| 궤적 | 전자모형 freeze 뒤 straight line, Coulomb/Rutherford, classical coupled motion 비교, lines 873–884 | 비교 후보 세 가지. production default 선택은 아님 |
| 필요한 R 범위 | collision-relevant 전체, small R, hidden crossing, closest approach, large-R tail, lines 573–582 | 수치 양 끝점·격자는 미지정 |
| b 적분 | σ_f=2π∫bP_f(b)db, small-b·support·long-tail·오차 조사, lines 710–745 | 유한 b_min/b_max·sample grid 미지정. 원식에 적분 경계가 쓰이지 않음 |
| 시간 창 | long propagation tails 및 integration 검증, lines 699–708 | t_start/t_end, z cutoff, tail tolerance 미지정 |
| 최소 coherent model | g=1s_sigma, e=2p_sigma/incoming-like, b=bright 2p_pi; 정당화하면 fourth state, lines 625–644 | D1의 최소 모형 요구. rank-5 전체 projector나 전 채널 완결성과 동일하지 않음 |
| 확대 채널·출력 | Nmax 3→4→5→필요 이상, reversible return, σ_n=1·σ_n=2·dominant subshells, lines 760–795 | Nmax=3 고정 production 요구가 아님. 2%/5%는 명시적으로 예시이며 C2 tolerance로 가져오지 않음 |
| F1 출력 | R_min, θdot, Rdot, interaction time, phase, channel probabilities, integrated cross sections, lines 895–903 | 모형 비교 시 기록할 출력 |
| support | ρ≤Re(Rc), ρ≤Re(Rc)+Im(Rc)는 diagnostic only; benchmark로 선택 금지, lines 938–946 | REAL/EXTENDED cutoff를 전체 collision b/R domain으로 승격할 수 없음 |
| convention 변경 | frame/origin·energy convention의 조용한 변경 금지, lines 1486–1487 | 새 adapter에는 명시적 입력·출처·단위가 필요 |

`rho=0 axis regularity`(line 510)는 전자 공간의 원통축 regularity다. 이를 핵 충돌의 b=0 채택으로 읽으면 안 된다. 충돌 b=0을 수치 전파할지, 작은 b 구간을 어떤 경계로 제어할지는 별도 계약이다.

## 현재 구현·역사적 pilot에서 회수된 값

`README.md` lines 26–34와 `run_research.py` lines 211–248은 legacy pilot의 ρ={0,0.3}, E={0.5,5} keV/u 및 indexed-state probability/area 출력을 보여준다. `geometry.py` lines 54–89는 `STRAIGHT_LINE_STATIC_COULOMB_CURVES` 모형을 표시하며, 이 모형의 물리적 타당성을 계산 자체가 확립하지 않는다고 적는다. `cross_section.py` lines 5–10은 형식적인 0≤ρ<∞ 적분과 caller-controlled finite grid를 명시한다. 이 구현의 형식적 적분구간은 b가 무한대까지 가는 물리적 단면적 정의와 연결할 수 있지만, 원 사용자 계약에 없던 유한 b_max나 완결된 tail bound를 제공하지 않는다.

`eq54.py` lines 52–54의 initial index 2는 united-atom 2p_sigma, paper j=3, Nmax=3이다. Lines 84–89의 support grid는 0, 회전 matching boundaries, branch support cutoffs의 합집합이다. 이것은 그 legacy stochastic approximation의 수치구간이며 C2 또는 coherent solver의 production 구간이 아니다. Root README의 초기 exponent 두-lane 설명보다 나중 R10L 계약은 factor=2로 고정되어 있다. 두 역사층을 현재 source policy 하나로 혼합하지 않는다.

고정 revision의 `V2_MODEL_CONTRACT.json`은 다음을 구별한다.

| 역사적 lane | 명시 모형 | 권위와 한계 |
|---|---|---|
| A | Coulomb, REAL support, frozen Δ0, author cutoff | `AUTHOR_IMPLEMENTATION_REPRODUCTION_ONLY_NOT_PHYSICAL_VALIDATION` |
| B | straight, EXTENDED support, dynamic exact action, CPC cutoff | 이미 고정된 legacy 비교 lane |
| C | straight, REAL support, B와 동일 action | B와 비교한 scientific difference는 support mask. 이 문서의 C 실행상태는 해당 계약을 기록한 시점의 상태일 뿐 최신 실행 완료 판정으로 쓰지 않음 |

공통 velocity는 legacy `sqrt(2 E/(27.07*1.836153))`로 보존되어 있다(`cross_section.py` lines 23–27 및 V2 `common.velocity`). 이 수치는 기존 구현의 convention이지, 새 nuclear mass/frame adapter를 검증한 근거가 아니다. 기존 실행을 몰래 다른 상수로 바꾸지 않으며 새 연구에서는 에너지 frame·u 정의·질량을 명시해야 한다.

`DR9A_TRAJECTORY_GATE.json`의 0.5 및 5 keV/u에 대한 H R_min=0.13,0.013 a0는 문서 자체가 `SOURCE_ANCHORED_DIAGNOSTIC_NOT_REALISTIC_TRAJECTORY_CALCULATION`으로 한정한다. 해당 문서의 repulsive Coulomb accessibility proxy나 bmax 표를 C2 production cutoff로 수입하지 않는다. 특히 source의 head-on 거리값을 bare nuclear repulsion의 turning point와 같은 식의 실측값으로 동일시하지 않는다.

## 문헌·benchmark 좌표는 공통 에너지축이 아니다

다음은 최신 C1B에 포함된 `BASS_HE_BENCHMARK_MATRIX.csv`를 그대로 해석한 회수 결과다. 개별 원문을 이번에 다시 열어 independently verified primary statement로 승격한 것이 아니다.

| source row | 회수된 native 좌표·frame | 사용 경계 |
|---|---|---|
| P03 | E_cm(eV)={20,50,100,200,600,1000,1600,2000,4000}, quantum nuclear partial waves | 4000 eV_cm를 자동으로 exact 5 keV/u로 바꾸지 않음; isotope/mass adapter 없음 |
| P04 | keV/u native impact energy, lab/COM 명시되지 않음 | native 5 token은 있으나 frame/state provenance 한계 유지; 0.5 row 없음 |
| P07 | relative nuclear velocity a.u.; no native energy column | implicit exact energy row를 생성하지 않음 |
| P08 | alpha projectile laboratory keV | native 20 keV가 조건부 A=4 변환 대상이나 adapter 미실행; exact 5-keV/u native row가 아님 |
| P09 | relative impact velocity, target-rest representation | velocity-to-keV/u adapter 미실행 |
| P10 | explicit projectile/incident keV/amu, 10–1000; z=vt, z window −150..150 a.u. | 이 source의 propagation window를 프로그램 공통 시간 창으로 채택하지 않음; 0.5/5 모두 source 범위 밖 |
| P22 | incident total laboratory energy in 3He convention | 3He/4He equal-velocity convention 유지; native 5 keV는 5 keV/u가 아님 |
| D-LIU24 | keV/u지만 raw CSV frame/isotope·단위 미확정, 요청 exact rows 없음 | interpolation·frame inference 없이 기존 blocked admission 유지 |

Matrix는 He2+ projectile와 H(1s) target의 중심 연구맥락을 보존하지만 H(2s) rows 및 잘못된 projectile의 excluded rows도 함께 가진다. 모든 row를 동일 입사 채널로 합치지 않는다. `SOURCE_MAPPING_DECISION.json`은 shell consistency와 별개로 subshell 출력에 C_S_AT mapping이 계속 필요함을 보존한다. 채널 label, shell 합, physical ionization, sink의 의미를 새로 동일시하지 않는다.

현재 `C1B_CONVENTIONS.json`은 전자 단위 a_A, E_A, charges={1,2}, charge-center O, nuclear repulsion 제외, static charge-center electronic frame을 고정한다. **이 electronic origin O는 nuclear center of mass도 collision energy frame도 아니다.** 따라서 이 파일만으로 핵의 isotope mass나 lab→relative/COM 변환을 얻을 수 없다.

## C2e 계약으로 전달할 값과 빈칸

회수 가능한 값은 우선 에너지 tokens {0.5,5} keV/u, 비교 대상 trajectory 세 종류, 입출력의 기존 물리·channel semantics, static electronic conventions이다. 회수되지 않은 공통 항목은 `energy_frame`, `nuclear_isotope_and_masses`, `selected_collision_trajectory`, finite `b_min/b_max`, finite propagation window, production R endpoints와 tail/error budget이다. 이 값들을 `null`과 `UNSPECIFIED`로 유지한다.

이는 C2e의 수학적 target 정의나 조건부 domain mapping까지 중지해야 한다는 뜻은 아니다. 다만 straight-line의 R_min=b, Rutherford의 turning point, finite time/window로부터 얻는 R interval은 **각각의 궤적·frame·mass 가정이 명시된 조건부 식**으로만 계약에 넣는다. 기존 x={32,64}의 수치 수렴을 충돌 전체 large-R tail bound로, b=0 표본을 R=0 핵충돌의 production 승인으로, 양끝 몇 점을 모든 중간 R의 인증으로 해석하지 않는다.

`full_C2_closed=false`, `scientific_PROMOTE=HOLD`, `Eq55=NOT_RUN`, `production_default_change=NOT_AUTHORIZED`는 이 source 회수로 바뀌지 않는다. `DOMAIN_AUTHORITY.json`은 위 결론과 원문 line/key references를 machine-readable 형식으로 제공한다.
