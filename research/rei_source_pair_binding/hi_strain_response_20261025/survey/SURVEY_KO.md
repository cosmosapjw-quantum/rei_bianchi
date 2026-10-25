# R1–R2 저장소 조사: 새 물리 결과와 HI 입력 결속

## 결과

이번 fresh survey에서 **CR105의 H1 바닥상태 spontaneous RR 소비자, REC136의 동일 stable source K_s 인증, BASS189의 양의 각도 적분 제어, HE101의 유한질량 direct CBA, PHYS90의 공분산 표시-cell 경계**를 실제 원문으로 확인했다. 이전의 “RR 공급 미확보”나 “same-source K_s 미결속” 상태를 그대로 반복하지 않는다. 각각의 새 결과를 실제 source·단위·대상에 맞춰 재사용한다.

현재 읽은 **9개 PR 본문과 23개 immutable source 파일의 관련 부분**에서는 native HI z=2.479의 실제 n_HI/time/source history·initial stock/epoch·geometry/frame/clock·collision/stopping/photon 공급이 한 단위로 결속된 입력을 찾지 못했다. 이는 읽지 않은 모든 branch나 private archive에 대한 부재 명제가 아니다. 기존 HI 4,368 atoms와 massive-stress S/D 완료 근거는 그대로 재사용한다. 이번 source intake의 새 과학 실행·tests·CAS·rendering·Git/provider 변경은 모두 0이다.

## 범위와 실제 종료점

Owner inventory는 51개로 이전과 같으며 추가·삭제 저장소가 없다. 51개 저장소의 branch collection을 실제 빈 terminal까지 읽었다. 관련 7개 저장소의 PR는 이전 latest10 표본을 넘어 state=all collection을 끝까지 열거했다. PR collection에 함께 반환된 모든 본문을 의미적으로 읽었다고 주장하지 않는다.

| 항목 | 이번 관측 |
|---|---:|
| Owner 저장소 / metadata 읽기 | 51 / 51 |
| Owner inventory pages / 실제 empty terminal | 2 / 1 |
| 모든 branch heads | 2,262 |
| Branch collection pages / 실제 empty terminals | 116 / 51 |
| Branch duplicate / 오류 | 0 / 0 |
| 이전 2,252 heads 대비 | 신규 10, 삭제 0, 기존 head 변경 5 |
| 관련 7개 저장소 branch heads | 1,349 |
| 관련 전체 PR metadata | 993 |
| PR collection pages / 실제 empty terminals | 21 / 7 |
| PR duplicate | 0 |
| 최신10 PR 별도 projection | 70 |
| 선택 PR 본문 | 9 |
| 고정 source 파일 / 실제 local Git blob 일치 | 23 / 23 |
| 선택 PR changed-path 전체 목록 | CR105 125, REC136 126, REI228 7 |

Branch batch는 2026-10-25 03:11:10–03:11:12 UTC에 기록됐다. rei_bianchi 첫 page는 이보다 앞선 같은 turn의 discovery GET을 재사용했으며 정확한 earlier fetch timestamp는 별도 포착하지 않았다. 해당 page의 projection 시각을 fetch 시각으로 쓰지 않았다. Repository/PR metadata batch는 03:11:30–03:11:34 UTC, source closeout은 03:16:21 UTC다. 이것은 원자적인 동시 snapshot이 아니며 이후 freshness resweep은 수행하지 않았다.

| 관련 repo | Branch heads | 전체 PR | Open / closed |
|---|---:|---:|---:|
| rei_bianchi | 269 | 227 | 213 / 14 |
| bass_cr | 183 | 105 | 104 / 1 |
| BASS_HE | 106 | 101 | 101 / 0 |
| WU088_HH | 156 | 147 | 147 / 0 |
| rec_bianchi | 154 | 136 | 102 / 34 |
| bass | 274 | 189 | 159 / 30 |
| vigilode | 207 | 88 | 58 / 30 |

전체 51개 owner 이름·원 metadata·관련 없는 branch 이름은 private/에 보존한다. 공개 표는 연구 의존성이 있는 7개 repo로 한정했다.

## 권위와 중앙 변경

고정 authority는 0f9d9df825be1dac9ca9bdf73cdc2e8908bcba17의 research/orchestration_longterm_20261023/assembly/HANDOFF_rei_bianchi_KO.md다. AGENTS blob은 429a5a13ee75b1222bc50627f8d5973d01dd21c4다. ANGTHERM02 research/rei-coupled-isotope-contract-20261022 @ 8d10231b1f0f788164d5eadbe1bcee0b802cceca의 READ_ONLY 예약을 유지한다.

기존 HI massive-stress Science S=42f5984a78f123ce26950cec0e0b8505da3e7ce4, Documents D=ecbb3124b49e75d8a7e948705b3894307d628349를 재실행하지 않았다. 현재 중앙 research/orchestration-sandbox-20261022 @ 8e946b46aa44581f09141184f193223277f2ec88은 D보다 정확히 1 commit 앞서며 세 경로만 달라졌다.

- assembly/DAG.json: +120/−1.
- assembly/HANDOFF_WU088_HH_KO.md: +23.
- assembly/returns/WU_PHYS90_COVARIANCE_CELL_AND_CONSUMER_ENVELOPE_20261025.json: 신규 1,276줄.

이는 새 PHYS90 관측이다. REC136의 중앙 관측 PR228 @ 256a152eff42fdd6daf317e7bf7ea0daffad728d는 별도의 open draft이며 현재 canonical HEAD에 합쳐졌다고 취급하지 않는다. [중앙 PHYS90 return](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/8e946b46aa44581f09141184f193223277f2ec88/research/orchestration_longterm_20261023/assembly/returns/WU_PHYS90_COVARIANCE_CELL_AND_CONSUMER_ENVELOPE_20261025.json), [REC PR228](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/228).

관련 신규 branch는 HE100/101, PHYS90, BASS189, CR105, REC136, 중앙 REC-KS 관측, VigilD5의 8개다. 기존 PHYS89·BASS188·CR104·중앙·VigilD4 head도 바뀌었다. 정확한 branch/head 대응은 HEADS_RELATED.json과 LATEST10_DELTA.json에 있다.

## 실제 읽은 새 과학과 입력 범위

### CR105: H1 ground spontaneous RR가 기존 finite chain에 들어왔다

Science head는 bdfd34499153575305871bd68a139e2878f5f49f다. 고정된 PR104의 8개 전자 에너지 사슬과 세 개 384-atom C23D source를 재사용하고, 기존 C23B PI fit 및 REI PR151의 ground-channel Milne 관계를 결속했다. 이번 원문 snapshot은 R1–R9/C1–C9의 18/20이며 actual Science S 게시를 확인했다. Final document/central/canonical delivery는 아직 진행 중이다.

새 소비자에서 E와 I는 eV, sigma는 cm², v는 cm/s, target density는 cm⁻³, hazard는 s⁻¹다. I=13.60 eV, g_H=2, g_p=1, d=1이며
sigma_RR(E)=sigma_PI(E+I)(E+I)²/(d m_e c² E),
lambda_RR(E)=n_HII v(E) sigma_RR(E)다.
Target은 n_HII=.1 cm⁻³이며 thermal n_e=.14 cm⁻³와 구별한다. 저장 H I 10,000 K ground alpha=1.5893516133029456e−13 cm³/s는 이미 존재하는 REI 결과다. 기존 질량 convention 사상 후 1.5893516165481638e−13 cm³/s이며 새 thermal 적분으로 세지 않는다.

Owner의 scoped 결과는 active electron당 RR 확률 1.26101–1.59845×10⁻⁹, 평균 종료시간 감소 0.37017–0.45707 ms다. 160 primary RHS와 40 independent RHS 결과를 보고한 source를 읽었고 이번 조사에서 이 계산을 재실행하지 않았다.

T=10,000 K, n_HI=.9 cm⁻³ 및 다른 bath density는 prescribed stationary isotropic common-temperature closed box다. 10,000 proper seconds는 impulsive population 정의다. 이 값들을 native 4,368-atom HI의 실제 밀도·history로 옮길 결속은 없다. 실제 photon occupation·stimulated/total RR·post-capture feedback는 null/open이다. 이는 새로 확보된 scoped collision component이며 source-complete stopping/thermalization을 의미하지 않는다. [FROZEN_CONTRACT](https://github.com/cosmosapjw-quantum/bass_cr/blob/bdfd34499153575305871bd68a139e2878f5f49f/research/cr_n5_rr_milne_20261025/FROZEN_CONTRACT.md), [RESULTS](https://github.com/cosmosapjw-quantum/bass_cr/blob/bdfd34499153575305871bd68a139e2878f5f49f/research/cr_n5_rr_milne_20261025/RESULTS_KO.md), [COVERAGE_DELTA](https://github.com/cosmosapjw-quantum/bass_cr/blob/bdfd34499153575305871bd68a139e2878f5f49f/research/cr_n5_rr_milne_20261025/COVERAGE_DELTA.json).

### REC136: same-source K_s와 실제 원 history admission이 완료됐다

Current head는 f9edbfe7b56ad002f1b7fb35d4c5aec4970682a4, immutable science S2는 309776ec263f10853a7ed4c404387c1474994e96다. 현재 전달된 한정 workflow는 20/20이다. 같은 stable M_s,B_s,T_s,P_s에 대한 K_s 314×313의 represented-operator infinity norm은 [1.17562722922718, 1.1756272292401908]이며 rho=3.458800151575591e−12다. THERMO J_s 314×6은 수치 검증된 기존 primitive derivative로 재사용한다. 이전 native K_0 norm을 K_s에 전용해야 한다는 옛 의무는 이 직접 인증으로 해소됐다.

원 data/pr05b2_source_history_v060.npz는 35,239,470 bytes, Git blob de43b1a2642fa0aa049abbfd1b0a7d775d684b1b, SHA256 d4f82542e13fed4ff0bb60b17865d8b9de5e090a2366108169c3da7a21fcb4b1이다. 7,489 knots, h=8.49e−5, z_start=1700.4825068138662, target z=1099.9986525171403에서 prefix 5,127과 313 queries가 실제 원 payload에 결속됐다. n_H0=.18745798773143102 m⁻³, T_0=2.728 K이며 photon occupation/Wien-departure gain에 대한 K_s다. Source-unit primitive 값은 eV, cm⁻³, s⁻¹ convention을 쓴다.

이 입력은 재결합 epoch의 실제 저장 자료다. Native HI z=2.479에 적용할 proper-time source history가 아니며, H6의 actual incident trace·Bianchi geodesic/direction/frame·measure/volume/clock/source/query owner는 계속 OPEN이다. H5 physical epsilon/reference/endpoint/curvature/absolute history bound도 null이다. 읽은 기록은 3.219042386314642e−15의 reconstruction agreement를 physical uncertainty로 사용하지 않는다. [NEXT_INPUT_CONTRACT](https://github.com/cosmosapjw-quantum/rec_bianchi/blob/f9edbfe7b56ad002f1b7fb35d4c5aec4970682a4/research/rec_history_ks_20261025/NEXT_INPUT_CONTRACT.md), [OPERATOR_BINDING](https://github.com/cosmosapjw-quantum/rec_bianchi/blob/f9edbfe7b56ad002f1b7fb35d4c5aec4970682a4/research/rec_history_ks_20261025/OPERATOR_BINDING_CLARIFICATION.md), [HANDOFF](https://github.com/cosmosapjw-quantum/rec_bianchi/blob/f9edbfe7b56ad002f1b7fb35d4c5aec4970682a4/research/rec_history_ks_20261025/HANDOFF_FINAL_KO.md).

### BASS189·HE101·PHYS90

| 새 결과와 source | 단위·실제 대상 | HI 적용을 위해 아직 필요한 결속 |
|---|---|---|
| BASS189 @ 6c933f324fe54d1f590bc8ab121032702659e00a: source moment 기반 positive angular endpoint selector, Loewner tail bound | H Lyα line card E_b=10.198714553953742 eV=1.6340142155180418e−18 J. n_b=1 m⁻³는 diagnostic. T_phys=E_b n_b det(R) T_shape. | 실제 B3c birth S/R history와 native receiver incident trace가 없음. Endpoint code는 duration/source-rate/history를 생성하지 않는다. |
| HE101 @ 9fc8185437f145a6ba4569e1b38aa2e12d15acd9: 같은 Jacobi Hamiltonian의 finite-M direct C1 Born | TDCS a0²/Eh, invariant W a0² Eh/p0⁶, conditional slice a0²/p0³. Target COM initially lab rest, incoming beam +z. | physical_provider/event_sigma/physical_recoil_distribution=false; HE-ANG SOURCE_INPUT_PENDING. 과학 snapshot17/20, C8 partial export와 실제 PASS/FAIL/FAIL 보존. |
| PHYS90 @ 9d32d115c0b8c5d5b2ce3a66ebc4a7f277334fcc: conditional covariance-cell pair threshold 및 shared consumer envelope | Fractional covariance, halfULP, t는 무차원. 0.5006839145935373<t_pair≤0.5006839145944469. | Full153 PSD unresolved; 실제 rate weights r,a 및 nuclear consumer ACK=null. 실제 mass/state/kernel/tail·clock·reference-density 결속 OPEN. |

세 단위의 실제 원문 경로·blob·단위와 방법의 자세한 비교는 donor_physical/DONOR_PHYSICAL_FINDINGS_KO.md와 SOURCE_RECEIPT.json에 있다. [BASS189 report](https://github.com/cosmosapjw-quantum/bass/blob/6c933f324fe54d1f590bc8ab121032702659e00a/research/bass_b3e_positive_angular_20261025/REPORT_KO.md), [HE101 theory](https://github.com/cosmosapjw-quantum/BASS_HE/blob/9fc8185437f145a6ba4569e1b38aa2e12d15acd9/research/he_ang_finitemass_cba_20261025/THEORY_KO.md), [PHYS90 theory](https://github.com/cosmosapjw-quantum/WU088_HH/blob/9d32d115c0b8c5d5b2ce3a66ebc4a7f277334fcc/research/hh_phys90_covariance_cell_20261025/theory/COVARIANCE_CELL_AND_CONSUMER_KO.md).

Vigil D4 @ 3c8877ea0409495752dcfab42426e679e3ba92d3는 owned journal/pending-batch/ACK protocol을, D5 @ a01f1c5c78e6b06e23565cd4e482716f99efbe97은 strict full-write RHS/Jacobian boundary와 represented-time stencil을 공급한다. 실제 native owner/source·BASS/model binding은 미해결이며 HI 물리 공급물로 취급하지 않는다. D4 실제 report와 D5 PR88 본문을 읽었다. [D4 report](https://github.com/cosmosapjw-quantum/vigilode/blob/3c8877ea0409495752dcfab42426e679e3ba92d3/research/d4_effect_journal_20261025/REPORT_KO.md), [D5 PR88](https://github.com/cosmosapjw-quantum/vigilode/pull/88).

## 다음 연구 선택에 전달할 판단

완료된 HI source/massive stress로부터 새 한정 constitutive response를 구성하는 데 이 조사 결과가 실제 history 부재를 불가능성으로 바꾸지 않는다. 다만 현재 native HI의 실제 밀도·proper-time history, epoch/stock normalization, 선택 Bianchi geometry/frame/clock, collision/stopping/radiation feedback를 확보했다고 가정할 근거는 이번 원문에 없다. 새 R3 이후의 물리적 대상·정규화·응답 가정은 root가 별도 동결한다.

원문이 지정한 별도 병렬 owner REC_HISTORY02_C5_CHECKPOINT_20261025_f7e85025fa2e는 Bianchi-I retarded-crossing/direction/fixed-cell tangent의 구현-present/검증-pending checkpoint다. 해당 H6 작업을 선택할 경우 최신 owner receipt를 받아 완료·진행 작업을 재시작하지 않는다. 이 조사는 새 theory나 code를 저술·admit하지 않았다.

현재 source를 다시 가져오는 무한 freshness loop는 종료했다. 실제 실행 경계에서 root가 필요한 branch/AGENTS/병렬 변경을 한 번 확인하면 이 고정 R2 자료를 재사용할 수 있다. 모든 기존 실패·비용·UNKNOWN_NOT_ZERO, C23E 조건부 D43K, HE94 부분창, PHYS85 준비 이력, ANGTHERM02 예약, L4/global 활성화 경계를 보존한다.
