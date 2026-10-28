# 관측 입력을 연결한 물리적 fast route와 ON_refined 단일 축 그림

2026-10-28 KST. 기존 PR249 `c23836847261851757caef50913be1c08379d4f0`에서 이어진 연구다. 사용자가 지정한 physmath-research-loop 내장 규약 1.0.0을 적용했다. 이번에 실제 수행한 것은 관측 공분산을 이용한 UVB 진폭 보정, 실제 공개 Lumina 이력의 입력 adapter, ON_refined 기본 선택, 저장된 17상태의 단일 축 그림이다. 새 IVP는 실행하지 않았다. 독립 판정은 **PASS_SCOPED_CONDITIONAL_UVB_ADAPTER_AND_FIGURE**이며 blocker·수리·추가 실행은 없다. 판정 근거는 `review/DECISION.json`, 최종 원격 상태는 `delivery/`의 추가 영수증을 따른다.

## 실제 결과와 물리적 의미

Becker–Bolton 2013의 Lyα forest로 추론한 H I 광이온화율 7개와 전체 통계 공분산을 Puchwein 2019 fiducial UVB 표의 H I 모멘트에 연결했다. 공분산은 논문 Table 2의 100C 표기에서 dex²로 변환되었고 대각 성분만으로 대체하지 않았다. 유효한 보정 영역은 2.4≤z≤4.75이다.

| 계산 | 실제 결과 | 해석 |
|---|---:|---|
| 고정 template의 log10 진폭 β | −0.0474269561 dex | 주어진 모양과 통계 공분산에 조건부 |
| 진폭 A=10^β | 0.8965469634 | H I 자료가 정하는 공통 template 진폭 |
| 고정 EOS의 통계 σβ | 0.0298820584 dex | 전체 계통·EOS를 주변화한 오차가 아님 |
| 보정 전 χ² | 21.90074447 | 7개 원자료와 고정 template 비교 |
| 진폭 보정 후 χ² | 19.38173684 / 6 nominal dof | 진폭 하나로 redshift별 모양 차이가 충분히 해소되지 않음 |
| EOS box profile | θ=+1, γ=1.6, A=1.073999833, χ²=15.72147478 | 허용 구간 경계에 도달; 내부 최적점/주변 posterior로 해석하지 않음 |

EOS의 구간 밖 자유 최적 θ≈9.00을 채택하지 않았다. Jeans/history 계통 오차의 전체 상관 모델은 이번 적합에 포함되지 않았다. 이 결과는 원자료와 template의 가정에 조건부인 재보정이며, 관측자료로부터 독립인 held-out 검증이나 Bianchi shear의 관측 제약이 아니다. 큰 χ²를 보편적 불가능성이나 새 no-go 정리로 주장하지 않는다.

실제 59행 UVB 표에서 H I/He I/He II의 이온화율과 heating, 총 6개 모멘트를 읽는다. 공통 A를 6개에 적용하는 것은 고정된 스펙트럼 모양을 유지하는 모델 가정이며, 여섯 독립 관측 보정이 아니다. 원본 표의 영역 0≤z≤15.1과 보정 영역을 구별한다. z=20 prehistory, Li rate, MeV photon, CR, inverse-weak bath, stopping, T, n_e, H, shear는 이 표로 결정되지 않으며 missing 상태를 반환한다. 0과 missing을 바꾸어 쓰지 않는다.

## 세 축의 구별

| 축 | 이번에 확보한 대응 | 남은 물리 의무 |
|---|---|---|
| 대칭성·게이지·프레임 | Γ와 heating은 국소 normal tetrad에서 정의한 scalar; 평균 a로 정의한 z와 관측 sightline z를 구별 | 상당한 shear를 가진 기존 Bianchi donor의 방향별 관측 전달, angular spectrum/stress |
| 불변량·수지 | target별 event rate yΓ, heat yε, ionization 내부에너지 IyΓ; 흡수에너지=(ε+IΓ)y; 기존 charge/baryon event 수지 보존 | source·sink·입자 bath 전체를 결합한 에너지·입자 수지의 forward 검증 |
| 실제 관측가능량 | Lyα 추론 Γ_HI와 공분산; conditional UV 모멘트; Lumina global simulation history를 별도 취급 | 국소 ion abundance→sightline 흡수/방출 관측량, Bianchi τ 및 n/T 관련 관측 대응 |

통합된 rate 표에는 이미 각도·스펙트럼 적분이 들어 있으므로 4π 또는 c를 다시 곱하지 않는다. proper-volume rate에는 동일한 proper nHref가 필요하다. UV Γ 하나를 고정해도 두 photon energy bin 사이의 가중치를 바꾸면 heating이나 핵반응 모멘트가 달라지는 구성을 유도했다. 따라서 이번 UV 자료만으로 n/T 생성률을 정하지 않는다.

## Lumina 실제 공개 수치 자료의 적용

사용자 지정 논문: https://academic.oup.com/mnras/article/552/4/stag1469/8971942

실제 공개 페이지 https://lumina-simulation.com/data-access/ 에서 SFRD, H I neutral fraction, He III fraction, cumulative CMB τ의 네 수치 표를 확보했다. 이전에 추정한 `/data` 주소의 실패는 공개 자료 부재의 근거가 아니며 이번 실제 취득이 그 부분을 교정한다. full snapshots와 이 공개 global table의 가용성을 혼동하지 않는다.

| 자료 | 행 수 | adapter 처리 |
|---|---:|---|
| SFRD | 246 | 명시된 comoving 단위, 실제 z 영역의 선형 보간 |
| H I | 258 | volume-weighted median; z=4,3은 원본 영역 밖 |
| He III | 294 | median 사용; 203행에서 percentile label 순서 이상 검출 |
| 누적 CMB τ | 981 | 마지막 값 0.0543742529; 원 논문의 simulation/cosmology 가정 유지 |

He III의 raw 15.87th가 median보다 크고 84.13th가 작으며 min>max인 사례를 발견했다. 보수적으로 raw 열을 유지하고 band는 `UNRESOLVED_QUANTILE_LABELS`로 반환한다. complement 변환의 percentile 역전이 가능한 설명이지만 확인 없이 sorting/수정하지 않았다. subbox 분산은 관측 공분산이 아니다.

SFRD는 고적색편이 source history의 실제 입력이다. 이를 국소 Γ로 바꾸려면 spectral photon yield, stellar-age/metallicity 가정, escape, proper/comoving 변환, transport가 필요하다. global ion fraction은 모든 국소 parcel의 초기 ion fraction이 아니다. 현재 확보된 history를 그대로 기존 n/T 또는 17상태의 보정된 해라고 부르지 않는다.

## 기본 옵션과 그림

새 `implementation/current_entrypoint.py`의 기본은 ON_refined이다. 명시적인 OFF_base/ON_base/ON_refined 선택은 유지한다. ON_refined는 ON source/escape 모델과 같은 물리 정의에서 더 엄격한 수치 허용오차 rtol=2e−8, scaled atol=2e−12를 사용한다. 이 이름 자체가 물리적으로 보정됐다는 뜻은 아니다. 기존 결과와 초기 300 K 재현 profile을 보존했고, 이전 cold 8 K 후보를 자동 적용하지 않았다.

`figure/pilot17_single_axis.png`와 SVG는 저장된 ON_refined 결과의 17상태를 하나의 log/log 축에 표시한다. n; H I/II; D I/II; T I/II; ³He I/II/III; ⁴He I/II/III; ⁷Li I/II/III/IV를 포함한다. 같은 isotope의 charge state에는 같은 고정 배율을 사용한다.

| isotope | 표시 배율 |
|---|---:|
| n | 10²² |
| H | 1 |
| D, ³He | 10⁴ |
| T | 10¹⁸ |
| ⁴He | 10 |
| ⁷Li | 10⁹ |

y 표시 범위는 배율 적용 후 10⁻⁸–2이다. 범위 아래 양수 999 state-time sample을 숨김 처리한 사실과 원값을 CSV에 모두 남겼다. 위쪽 범위 밖은 0개다. t=0은 로그축에서만 제외하며, abundance floor 또는 새 시간 샘플은 만들지 않았다. 색은 isotope, 선·marker는 ion stage이다. 배율 때문에 서로 다른 isotope의 세로 순서는 원래 abundance 순서가 아니다. x축은 source turn-on 이후 경과 고유시간이며 cosmic age나 BBN 시기 자체가 아니다. 이번에 구한 A로 기존 population을 곱하지 않았다.

## 실제 source 조사와 통합

접근 가능한 GitHub 51 repo, 현재 branch ref 2,429개를 terminal pagination까지 조사했다. 이전 snapshot 대비 26 new + 8 moved branch의 이력에서 268 unique delta commit을 읽었고, 모든 repo의 PR 목록을 cutoff 이전/말단까지 읽어 7 repo의 25 updated PR을 확인했다. 모든 과거 blob이나 private 대화를 읽었다는 뜻은 아니다. 변하지 않은 source는 identity를 확인해 재사용했다.

BASS의 collisionless Einstein–Vlasov 및 feedback, REC incoming derivative, CR He event measure, WU memory, BASS_HE endpoint 결과의 적용 조건을 취합했다. 이들은 UV 관측 보정이나 MeV/CR source 전체를 자동으로 제공하지 않는다. 별도 담당자의 예약·예산·미완성 gate를 본 lane으로 이전하지 않았다. PR247의 최신 exact HEAD `9a5eaf4336e873bed3bcf3d321c0861a22796fc0`에서는 numerical C6/C7/C8/C9 근거가 실행 후 갱신됐지만 figure를 포함한 전체 단계는 17/20이다. 예전 15/20 NOT_RUN 문구를 현재 상태로 인용하지 않았다.

Dropbox 6,492 distinct returned ID의 관련 preservation metadata를 확인했다. Drive는 folder metadata 554개, 문서 metadata 992개, 추가 mixed-MIME 1,654행을 확인했으며 최신 archive 60개를 찾았다. 이 수치는 중복 없는 합계로 더하지 않는다. Drive 한 root가 1,000개 cap이고 다음 cursor가 없어 전체 역사 archive의 완전성은 입증되지 않았다. Personal Context는 이 대화에서 unavailable을 반환했다. 첨부 실패 13개는 `intake/UNAVAILABLE_ATTACHMENTS.md`에 기록했다. 자세한 적용 범위는 `delivery/SOURCE_SURVEY_COVERAGE.md`에 있다.

## 전체 DAG 위치와 단계별 근거

이번 단위는 기존 physical F4 안의 관측 UV source-input 의무를 수행했다. original physical fast **4/7**, global working **33/88**, central **28/88**, 이전 phenomenological pilot **7/7**을 그대로 유지한다. 10단계 이론/코딩 표의 완료를 원래 DAG 노드의 완료로 더하지 않는다.

| 단계 | 실제 근거·gate | 전체 working / physical fast |
|---|---|---|
| R1 연구 위치·계약 | PR249 source, 기존 승인/소유자, F4 범위 고정; CHECKPOINT_KO | 33/88 · 4/7 |
| R2 근거·재사용 | Git/backup delta, 실제 관측 covariance·UVB·Lumina 자료와 provenance | 33/88 · 4/7 |
| R3 주장·전제 | local tetrad·redshift·관측/모델·영역·EOS/Jeans 구별 | 33/88 · 4/7 |
| R4 표현 탐색 | amplitude GLS와 observation-only 보간, spectral moment 비유일성 구성 | 33/88 · 4/7 |
| R5 구성적 유도 | β와 EOS box profile, event/energy mapping 실제 유도 | 33/88 · 4/7 |
| R6 독립 검증 | Wolfram 항등식 및 별도 작성자의 scoped review | 33/88 · 4/7 |
| R7 판별 검증 | 실제 7개 자료 적합; θ 경계/χ² 잔차가 범위를 판별 | 33/88 · 4/7 |
| R8 결과 판정 | conditional UV 입력으로 제한; 전체 F4 PARTIAL | 33/88 · 4/7 |
| R9 코딩 연결 | PHYSICAL_NEXT_CONTRACT와 CODE_AND_PROVIDER_MAP | 33/88 · 4/7 |
| R10 종료·재개 | STATE·HANDOFF·budget closeout·publication receipt | 33/88 · 4/7 |
| C1 목표·baseline | 동결된 PR249와 additive unit, ON_refined 기본 | 33/88 · 4/7 |
| C2 식–데이터–코드 | 단위·covariance·column·source identity 연결 | 33/88 · 4/7 |
| C3 수치 설계 | Cholesky, domain 검사, zero 명시, interpolation 규약 | 33/88 · 4/7 |
| C4 실행 DAG·자원 | 분리된 calibration/render 병렬, 각각 1회·유한 예산 | 33/88 · 4/7 |
| C5 구현 | calibration·Lumina adapter·default selector·single-axis renderer | 33/88 · 4/7 |
| C6 구현 검증 | 실제 suite 9/9 PASS, raw stdout/stderr와 exit0 | 33/88 · 4/7 |
| C7 과학 검증 | 실제 covariance fit·event energy·missing field·domain·quantile anomaly | 33/88 · 4/7 |
| C8 수치·재현성 | explicit residual/GLS identity·equivariance·범위 검사; 기존 IVP 재사용 | 33/88 · 4/7 |
| C9 독립 검토 | 작성자와 다른 검토자의 1회 판정; review/DECISION.json | 33/88 · 4/7 |
| C10 판정·인계 | scoped 판정과 다음 물리 입력, 원본 보존·게시·백업 영수증 | 33/88 · 4/7 |

R6/C9의 최종 상태와 publication/backup 완료 여부는 해당 실제 영수증으로 판정한다. 이 표는 pending 기록을 미리 PASS로 승격하지 않는다. 사전 체크포인트 `6edca2f9258384d1b7679ccfc0aa73486c787841`에 명세와 예산을 게시한 뒤 실행했다. 각 하위 산출물은 원본 파일로 보존하고 최종 scoped review 후 함께 게시·백업한다.

## 자원·다음 실행점

calibration child+관측 wrapper CPU는 0.162924 s, render는 0.956201 s였다. 새 tail reserve를 유지한 cumulative main은 606.634374 s, presentation은 63.924256494 s, planning은 20.819461885 s이다. 원래 policy cap 600/30/10으로 복귀하되 누적 debit은 지우지 않는다. authoring/intake/tool/host/전송 등 미관측 비용은 UNKNOWN_NOT_ZERO이므로 이 숫자가 전체 세션 비용은 아니다. 이번 단위에 IVP, 자동 retry, foreign ledger transfer는 없다.

다음 유용한 연구는 (1) Lumina SFRD의 spectral yield·escape·transport를 명시해 matched local bath로 연결, (2) 별도의 hard photon/CR 및 n/T·stopping channel source를 자료에 묶기, (3) 기존 IC·Bianchi tensor 후보와 양립하는 T/n_e/H 및 관측 redshift 전달을 구성하는 것이다. 이 의무를 고정한 다음에만 새 물리 forward solve의 실행 명세를 만든다. 현재 관측 adapter를 기존 population에 곱하거나 완료된 IVP를 반복하지 않는다.
