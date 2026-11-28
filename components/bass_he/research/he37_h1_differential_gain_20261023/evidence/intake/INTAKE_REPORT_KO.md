# HE36 이후 변경분 intake — HE37 시작 근거

workflow1.0.0 / approval0.2를 유지한다. 기준은 기존 HE36 intake의 2026-10-22T22:26:00Z 이후 변경분이다. 이번 수집은 2026-10-23 UTC에 수행했으며 상세 시각은 INTAKE.json과 원응답 파일에 있다. 기존 HE36 게시 pin `6403055c3d574ec0bd1ece80147f9711315902e7`은 그대로 확인됐다.

## 결론

새 관련 donor에서 H1 CI/RR의 **보정된 차등 outgoing gain/STF provider**가 닫혔다는 증거는 찾지 않았다. PHYS81의 finite CI·hazard 환원, C23A의 UVB/전자 침적·β energy coverage, ANGULAR01의 escape-probability PSTF는 각각 재사용할 수 있는 구성요소다. 각 입력의 물리 소유자와 범위가 다르므로 이들을 H1 gain tensor로 묶어 승인하지 않는다. Root가 선택한 Le–Cambier 원문의 Eq.85와 isotropic angular G는 명시적 모델 채택으로 기록하며, 경험적으로 보정된 H1 differential 자료의 확보와 구별한다.

기존 HE32의 8핵종21상태 prescribed-UV photo+caseA RR, gas pi_b=0 및 nonbaryonic matter stress 해석은 유지한다. HE36의 완료된 incoming-loss 구현·검증은 원 producer pin을 기준으로 재사용한다. 다른 donor의 이전 요약 문구로 그 완료 상태를 되돌리지 않는다.

## 실제 조사 범위

| 범위 | 이번 실제 확인 |
|---|---|
| 관련 repository | BASS_HE, WU088_HH, rec_bianchi, rei_bianchi, bass_cr, bass, vigilode 7개 |
| Branch metadata | 15페이지, 기존1276→현재1281행; 새tip5, 이동tip4, 삭제0 |
| PR metadata | updated-desc 첫 페이지 각1개, 총665행. 모든 마지막행이 cutoff 이전이므로 해당 snapshot 이후 updated행9개를 포함한다. 전체 역사927PR를 다시 열거했다고 하지 않는다. |
| 선택 본문 | 고정 commit의 Git text19개, 모두 원 Git blob SHA1과 일치; 선택 문서의 관련 계약/결론을 읽었다. 전체 source tree/모든 식의 독립 재검산은 아니다. |
| Repo 대화 | updated9PR의 issue-comment collection9개, cutoff 이후댓글5개. Review/review-comment 전수재조사 없음. |
| 개인 대화 | Personal Context 도구가 이 대화에서 unavailable을 반환했다. 대화 전문 또는 최신 모든 대화 접근을 주장하지 않는다. |
| 백업 변경분 | dossier의 ADD event29개/3페이지, 선택 PHYS81/C23A final authority2개 본문 조회. 기존4739개 inventory 및 전체 archive 재다운로드 없음. |
| 과학 실행 | model/test/IVP/render/benchmark 모두0. 읽기·해시 계산만 수행. |

Dropbox `last_modified_after` 검색은 cutoff보다 오래된 행을 반환했다. 이 검색을 최신성 판정에 사용하지 않고 event API의 시간방향/페이지 응답으로 대체했다. 마지막 event page는9행을 반환하고 cursor/has_more를 생략했다. 이 도구의 반환 범위를 넘어 다른 모든 백업의 부재를 주장하지 않는다. Producer의 archive restore/ACK는 해당 producer receipt로 인용하며 이번 intake에서 다시 복원한 것처럼 쓰지 않는다.

BASS_HE94branch/89PR snapshot에 HE37 이상 이름의 충돌은 없었다. 이 판단은 수집 당시의 관측이며 이후 동시 작업을 막는 잠금이 아니다.

## 새 과학 donor와 채택 경계

### PHYS81 — WU088_HH PR137

고정 pin `b3ec271a96cb67e583bffa9b61533802838236f9`, 단원 `research/hh_phys81_atomic_nuclear_source_contract_20261023`이다. PR 본문은 초기 S1/ODE0 문구가 남아 있었지만, 같은 pin의 FINAL_REPORT와 Dropbox 최종 authority는 S2/S3의 실제 완료를 기록한다. 새 isolated CI parcel은3시도/3완료, rate profile27개, 독립 원자15논리군·핵663assertions, PNG/PDF3쌍이다. 이 숫자는 donor의 완료 근거이며 이번 실행 수가 아니다.

Bell1983 Table5 H B1=−0.0186의 원전 정정과 분석함수 양성 증명, H1/He4/Li7의 finite stationary-target CI 계약, 정확한7→3 neutral-hazard 좌표와 rank≤2 Jacobian을 제공한다. 활성 registry는 `source_data/ADMITTED_FINITE_CI_REGISTRY.json` v2다. 초기 PHYS81_ATOMIC_CI_SOURCE_REGISTRY v1을 활성 입력으로 재사용하지 않는다. Li7 chemical defect는 isotope별 원전에서 교정됐고, 표의 incoming-energy 축은 유지됐다.

He4 window24.6–60eV와 Li7 window6–15eV는 선택한 ground-product finite 모델이다. 구간 밖0은 이 finite operator의 정의다. Li7의 threshold→6eV gap과 He 원자료 정확도 한계가 남는다. Common thermal bath에서 CI net heat=−I×event-rate이고 mean incoming energy를 다시 빼지 않는다. 이는 outgoing 에너지의 완전 열화를 가정한 scalar closure이며 differential gain/STF 자료를 제공하지 않는다.

Bare n+p→d+γ, n+d→t+γ, p+d→helion+γ에는 cold-COM photon/recoil ledger와 supplied ζ 분할이 있다. 실제 rate, finite-T reaction-weighted parent energy, normal-frame angular source, stopping과 thermal/fast particle 수는 OPEN이다. ζ로 열 입자수 membership을 결정하지 않는다.

향후 재사용 후보는 `source/finite_ci.py`, `source/parcel.py`, `source/nuclear_recoil.py`다. 이번에는 코드를 이식하거나 실행하지 않았다.

### C23A — bass_cr PR96의 새 commit

pin `7643af28c671a7473754a3c2cd0c6e523bd61aac`는 기존 C22D `ba39fc75521aa18705ec832d789e50dd5c6565bc` 위에 `research/cr_c23a_external_supply_20261023`214파일을 추가한다. 과거 C22D provider/4IVP를 다시 계산할 이유가 없다.

Puchwein v1 fiducial Γ/H 표를 읽는 명시적 H/He5상태 frozen photo subflow는0≤z≤15.1에 한정된다. Γ와 excess-heating H만으로 photon/electron spectrum을 유일하게 복원하지 않으며 z20로 외삽하지 않는다. 새로운 source-response826행은 우주론적 trajectory가 아니다.

FS2010 finite response는10–9937.21eV,14×258node이며 양의 PL electron spectrum을 미리 적분하는 연산자를 제공한다. 고정 spectrum에서 energy/ionization 채널의 반복 적분을 준비 단계로 옮긴다. 실제 원자료 axis/header 충돌, 최대3.9e−5 energy closure defect를 보존한다. xHII=xHeII, HeIII=0 제한과 He/H normalization, 실제 primary electron spectrum, low/high-energy continuation, loss-time/locality가 열린다. 21상태를 임의의 xe 하나에 투영하여 physical provider로 승인하지 않는다. H1 angular gain moment는 공급하지 않는다.

ENDF 중앙 Q/mean과 같은-frame positive support 가정 아래 neutron β kinetic energy의 FS구간 coverage 상한은2.053246%다. 이것은 조건부 energy-domain 경계이며 heat yield가 아니다. Fermi function1의 illustrative spectrum은 평가 spectrum과 별도다. 실제 β spectrum/boost/recoil/daughter/stopping은 여전히 후속이다.

향후 코드 후보는 `photo_subflow.py`, `deposition/fs2010_operator.py`, `nuclear/beta_domain_coverage.py`다. 이번 원문 조회와 코드 이식/실행은 구별한다.

### REC127 ANGULAR01와 REC126 C2

ANGULAR01 pin `5185c396b7e07076565ca2f5044a5ccd193e6ee1`은 고정 등방 line emitter와 모든 방향의 양의 expansion 아래 escape-probability monopole/PSTF를 계산한다. Thick-limit error gate와 실제405행은 재사용 가능하다. Q는 확률 모멘트이며 photon stress가 아니다. Population/Einstein/number·energy injection의 소유자 연결이 필요한 후속이므로 H1 reaction gain source로 직접 채택하지 않는다. 향후 후보는 `research/rec_bianchi_escape_moments_20261022/code/escape_moments.py`다.

REC126 pin `12068893fab749ae1efb513563d0a86cc1cf649f`는 기존 저장 Compton diagnostic512상태의 비용·중복 경로를 조사했다. 이는 새 gain microphysics나 구현된 가속 최적화의 완료 근거가 아니다.

## 변경 없는 과학과 solver 변경분

REC125 `407a280aff51abefc10374cb6e21c4224140328c`→`b28b387fecd6cc71fddb98e95f336eba5f8a647f`는10개 delivery/DAG/handoff 파일의1commit이다. REI221 `9620e1fcc4bdda76e0311206f614234926600381`→`73c5e00cac26b4efc782446975bd6b6762555997`는 DELIVERY.json1개다. 두 경우 과학 source/data/results의 새 실행으로 집계하지 않는다. REC119/REI220의 updated timestamp는 THERM02/ANGULAR01 반환 댓글과 연결되며 branch tip은 unchanged다.

WU135/136, REC121/124, REI219/222, CR97, BASS181, VigilODE79의 지정 pin은 유지된다. 정확한 SHA는 INTAKE.json에 있다.

VigilODE는 PR79 외 별도 explicit branch가 `fbc3c272fa06b443de148631ea78bfa6a34f1b2b`로 이동했고, production-hardening branch `14c74978b93339a79d7228a324fa77552dae548e`가 추가됐다. 전자는 diffsol/Julia 외부 비교, 후자는 opt-in DOPRI5 sampled dense output·affine physical WRMS·극소 step/거절 재착지 수정과 별도288실행 측정이다. 현재 H1 gain 연구의 physical provider가 아니므로 solver를 자동 교체하지 않는다. 향후 affine/source-aware coupled IVP에서 해당 native 경로의 조건을 따로 채택할 후보로 기록한다.

## 보존 및 다음 연결

Public용은 `public/`의 요약·정확 pin·blob binding만 사용한다. Raw Git metadata/선택 문서와 producer authority의 보존 대상은 `ARCHIVE_ELIGIBLE.json`에 명시한다. 무관한 오래된 Dropbox 검색 행, 개인 context unavailable 응답, actor가 포함된 raw event 응답은 raw archive 대상에서 제외했고 관련 실패 요약 및 project event명/시각은 별도로 보존했다. Parent가 승인된 checkpoint 절차에 따라 raw archive를1회 백업한다. 이 agent는 원격 쓰기·게시·업로드를 수행하지 않았다.

다음 N1/R2에는 Le–Cambier native Eq.85 energy-sharing과 명시적 isotropic angular G의 모델 계약을 결속한다. CI fixed-heavy-target/finite-mass, total σ와 source floor/chemical threshold, number·heat·STF normalization을 같은 kernel로 대조하고, 보정된 차등 H1 자료·실제 stopping·유한 anisotropy closure는 별도 열린 의존성으로 유지한다.
