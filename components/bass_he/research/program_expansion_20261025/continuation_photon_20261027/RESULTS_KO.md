# PHOTON05: 광자 입사와 두 유한질량 딸핵의 상대론적 반동

**새 조건부 수치 검증은 24/24 PASS다. 저장자료 그림은 생성됐지만 CPU 한도 초과로 FAIL이며 전체 workflow는 partial이다.** 기존 STATE04와 HE101의 완료·실패·예산을 그대로 보존했다. 실제 raw outcome은 `evidence/validation/` 및 `evidence/plot/`, 독립 판정은 `review/`를 따른다.

## 새로 제공하는 계산

정지 bare ground-state alpha에 광자가 입사하여 두 bare ground-state deuteron을 만드는 exclusive 사건에 대해, 두 생성물의 lab 에너지·운동량·상대론적 응력 및 단일 에너지 원장을 구현했다. 입력은 NIST의 2022 CODATA nuclear rest-energy 중앙값과 기존 EXFOR M0475002의 12개 native 에너지·CM 각도 좌표다.

질량 입력은 alpha `3727.3794118 ± 0.0000012 MeV`, deuteron `1875.61294500 ± 0.00000058 MeV`이며 MeV 표기가 canonical이다. 공분산을 확보하지 않았으므로 두 오차를 독립이라고 가정하거나 결합 physical error band를 만들지 않았다. 원문은 [NIST allascii](https://physics.nist.gov/cuu/Constants/Table/allascii.txt), 관측·해시는 `sources/SOURCE_MANIFEST.json`과 `PHOTON05_SOURCE_OBSERVATIONS.json`에 있다. EXFOR 원전은 [고정 IAEA-NDS M0475](https://github.com/IAEA-NDS/exfor_master/blob/939a14d7bba1ddce51975cb5e8711ce96b3b0871/exforall/M04/M0475.x4)다.

이 계산은 선택한 질량값과 bare-nuclear·stationary-target 계약에 조건부인 운동학 사상이다. 측정의 liquid-He 표적, 전자 spectator, 표적 운동·beam response·angular acceptance·polarization·particle/event normalization을 실제 소비자에 결속하는 일은 남아 있다. Native DCS 및 통계 ERR-S는 그대로 보존하고 사건 flux로 사용하지 않았다. phi=0은 명시적인 대표 평면이다.

## 문턱과 사건의 에너지 소유권

에너지 단위의 4-vector를 `q=(E,c p)`로 쓰고, target rest energy를 A, 각 daughter rest energy를 M, 광자 에너지를 e라 하면

\[
s=A^2+2Ae,\qquad
\Delta=2M-A,\qquad
e_{\rm th}=\Delta+\frac{\Delta^2}{2A}.
\]

저장된 중앙값 계산은 `Delta=23.846478200000092 MeV`, `e_th=23.922758940396797 MeV`다. 단순 정지에너지 결손 외에 약 76.281 keV의 문턱 반동이 있다. 합성 대조군 A=M=2, e=3에서는 CM momentum이 0이어도 각 daughter의 lab E=2.5, cp_z=1.5, K=0.5가 남는다. 이 검사는 photon momentum을 지우는 잘못된 문턱 모델을 구분한다.

한 사건의 원장은

\[
-e+\Delta+(K_++K_-)=0
\]

이다. Nuclear binding은 이미 물리 rest mass에 포함되어 있으므로 `population_rest_energy_witness`만 rest/binding을 소유한다. 별도 binding RHS를 추가하지 않는다. Photon count −1, alpha count −1, deuteron count +2이며 baryon number와 nuclear charge가 보존된다. 물질 핵의 수는 +1이지만 `Gamma_thermal`, Cv, species heating, thermal deposition은 null이고 birth pool은 UNASSIGNED다.

Adapter의 사건 flux는 호출자가 명시하는 유한·비음수 입력이다. Native 저장 예제의 flux0은 입력 검증과 per-event 출력 보존을 위한 예시값으로, 실제 물리 사건률0을 의미하지 않는다. 데이터로부터 physical rate를 산출하거나 승인한 적이 없다. SI 경계에서 1 MeV=1.602176634e−13 J와 cp/c를 명시적으로 적용한다.

## Native 12좌표의 저장 결과

아래 수치는 `evidence/validation/SAVED_PLOT_DATA.json`에서 읽었다. 두 딸핵의 +/−는 수학적 label이다.

| 입사 MeV | CM 도 | K+ MeV | K− MeV |
|---:|---:|---:|---:|
| 213 | 46 | 116.899871154 | 72.253650646 |
| 213 | 61 | 110.156301960 | 78.997219840 |
| 213 | 73 | 103.972236543 | 85.181285257 |
| 213 | 87 | 96.258596708 | 92.894925092 |
| 258 | 46 | 146.841333031 | 87.312188769 |
| 258 | 61 | 137.849779013 | 96.303742787 |
| 258 | 73 | 129.604240686 | 104.549281114 |
| 258 | 87 | 119.319240673 | 114.834281127 |
| 330 | 46 | 195.890497988 | 110.263023812 |
| 330 | 61 | 182.956932941 | 123.196588859 |
| 330 | 73 | 171.096446303 | 135.057075497 |
| 330 | 87 | 156.302372173 | 149.851149627 |

12좌표의 저장된 4-momentum residual은 모두0이다. 가장 큰 normalized mass-shell residual은 `6.094243921453634e-17`로, 고정된 256epsilon scale 기준 안에 있다. 이 수치는 source physical uncertainty가 아니라 구현 수치 검사다.

공간 응력은 `S_ij=q_i q_j/E`이며 raw momentum second moment와 다르다. 첫 좌표의 net stress에는 photon loss가 포함되어 zz가 약 −29.3538853 MeV이므로 net source에 양의 준정부호성을 요구하지 않는다. 각 daughter의 stress와 trace, 모든 성분의 공간 회전 및 daughter 교환을 확인했다. 이 가중치는 선택 lab의 equal-time moment weight이며 전체 kinetic tensor의 Lorentz 변환에는 분포·측도도 함께 필요하다.

같은 정확한 운동량에 비상대론적 에너지식을 대입한 상대 초과 `(K_NR-K)/K=K/(2M)`는 저장 좌표에서 약 **1.926–5.222%**다. 별도 비상대론 solver를 실행한 결과가 아니다.

## 검증·그림·실패의 구분

독립 Decimal80 reference는 literal masses와 각도, 별도 삼각함수 급수, 직접 Lorentz matrix로 구성했다. Native 전체, mass shell·보존·회전·교환·azimuth, 정확한 synthetic threshold와 작은 excess, 숫자·벡터·표현 범위, SI 및 count/energy ownership을 검사했다. Photon momentum·threshold recoil·두 번째 daughter를 누락하거나 binding을 중복하는 잘못된 모델의 판별 잔차도 기존 24 methods 안에 두었다.

실행 전 발견한 여섯 사항은 첫 START 전에 교정했다. 초기 HOLD와 교정 이력은 `review/CODE_REVIEW_PREEXEC.json`에 남아 있다. 이는 실행 실패나 repair reserve 사용으로 세지 않는다.

| 실행 | 판정 | CPU s, child+runner | wall s | cap CPU/wall | 새 science 호출 |
|---|---|---:|---:|---:|---|
| 24-method 검증 1회 | PASS | 0.241060162 | 0.239336358 | 4 / 15 | 새 조건부 검증만 |
| 저장자료 그림 1회 | **FAIL, CPU 초과** | **4.407265040** | 4.406950156 | 4 / 15 | 0 |

그림 child는 exit0으로 PNG·SVG를 만들었으나 CPU cap을 초과했다. `PLOT_DATA.json`은 검증 saved data와 byte-identical이다. Root는 실제 PNG를 열어 판독했고 `evidence/PLOT_READ_KO.md`에 해석과 한계를 기록했다. 생성 파일·START·FINISH·stdout·stderr를 보존하며 plot의 FAIL을 PASS로 바꾸지 않는다. Matplotlib의 쓰기 불가능한 기본 config/임시 cache 경고는 관측됐으나 초과의 확정 원인을 측정한 것은 아니다. 재실행·추가 profiling·검증 잔여 예산의 전용은 없다.

원 INTAKE runner와 EVENT03의 ContractError/product를 그대로 재사용했다. EVENT03 비상대론 fixed-mass kernel은 호출하지 않았다. 기존 과학 suite·HE101·physical campaign START는 모두0이며, 준비·모델·네트워크 I/O 비용은 UNKNOWN_NOT_ZERO다. End-to-end CPU cap을 주장하지 않는다.

## 연구 및 전달 상태

Local DAG는 **4개 scoped node 완료, 검증 종합 node 1개 partial, 물리 입력 3개 open**이다. Partial node는 수치·시각 확인을 보존하되 plot resource gate가 실패한 상태다. 기존 STATE04의 5/8은 그 단위의 역사적 범위이며 변경하지 않았다.

전역 species inventory는 기존 source-only 104 IDs/138 variants/155 event references를 재사용한다. 신규 global ID나 완전한 physical differential provider를 추가하지 않았다. `ALL_SPECIES_PROGRESS_KO.md`는 기존 군별 의무와 이번 기여를 연결한다. Physical provider/global consumer admission=false, production=NOT_APPROVED, activation=false, global physical completion=null, L4_ready=false를 유지한다.

GitHub의 다섯 번째 동일 tree 제출은 `user rejected MCP tool call`로 끝났으며 추가 사유는 제공되지 않았다. 새 remote tree/commit/ref update는 없다. 원격 HE는 관측 시 ac6042a6…이고 local source/delivery SHA는 실제 commit과 archive receipt에서 결속한다. Source ZIP·Git bundle·Dropbox/Drive ACK와 중앙 observation candidate는 별도 delivery 단계로 기록한다. 중앙 WU nuclear lead의 계약·status·예산이나 다른 owner의 완료 상태는 이 HE 결과로 변경하지 않는다.

## 실제 source 전달과 중앙 후보

실제 S05는 `251c6baa6c3359b1d6997dbce51cea65500b53d6`, tree `80c880cc3881e1e539156d8e077d443f7bd945a5`다. Source ZIP은 `BASS_HE_HE_EXP_PHOTON05_SOURCE_20261027_251c6baa.zip`, 20,425,864 bytes/434 members, SHA256 `d3b574ec5d4b2657d63cc23afd221d1ce6aec59b79192676ffb54fb43af26a90`다. 원179 dependency filename set과 full program expansion, root AGENTS 및 ac6042 prerequisite의 실제 Git bundle을 포함한다. ZIP/committed member identity 검증은 PASS다.

Dropbox `id:BSpOijBcT10AAAAAAEDHdw`와 [Drive source ZIP](https://drive.google.com/file/d/1IyO2X5mAfHA4y7aC9oi-iIR5ECccRJxc/view?usp=drivesdk)의 실제 upload ACK 및 별도 metadata ID/name/size 확인을 마쳤다. Full remote download SHA256는 검증하지 않았다. `delivery/BACKUP_ACK.json`을 따른다.

중앙 후보 16개 upsert는 실제 base `1a38f94fa50c763bb9df6ccc8ba569f287fe97d5`에서 5개 node의 observation만 바꾼다. 나머지83개, 원계약·상태·예산·lead·의존성 및 CR proper-injection을 보존한다. 독립 판정은 `APPROVED_LOCAL_METADATA_DELTA_ONLY`, review SHA256 `628dca1183886e548851c01b1b0cd2a29dfdf63abf5acd6f90fc4b726038f6a1`이다. **후보는 로컬이며 중앙에 게시되지 않았다.**

이후 D05는 소스 이후의 전달 metadata만 담는다. D05의 실제 최종 SHA, delta ZIP/bundle와 그 dual ACK는 commit 후 생성하는 외부 `BASS_HE_PHOTON05_CLOSEOUT_20261027.json`과 보고서에 기록한다. D05 안에서 자기 archive/backup을 미리 인증하지 않는다. Source ZIP 뒤에 D05 delta를 적용하거나 각각의 actual Git bundle을 사용한다. 원과학 및 plot FAIL의 상태는 변경하지 않는다.
