# PR171 READY 실제 실행: age64 resource-stop prefix

2026-10-18 KST. 소유자의 별도30분 직접 실행 승인을 적용했다. 기존 source/physics/tolerance와 프로그램은 수정하지 않았다. Native base `35d9747a0bbedcafdb568467ce7c1e7a25f965b6`, 공급자 `57533355976fe10e574d01d338dcc0e9ab9d22a5`, launch checkout `6465ec502ee23af85cedc5cb73fbccc3254f02d4`다. Native 원본8개 prefix와 연구 소스4개 identity를 확인하고 기존 ELF를 새 NCP 경로에 복사했다. 새 build·완료된 검사 재실행은0이다.

## 실제 실행과 종료

할당은2026-10-18 **12:09:04.899 KST**에 한 번 시작했고 절대마감은**12:39:04.899 KST**다. 첫 age64 reference만 시작했다. Reference의600초 제한에서 process group을 종료해 exit**-9/WALL_CAP**, 실제시간**600.128026917s**였다. 감시 간격/종료 처리로 **0.128026917s** 초과한 사실을 그대로 보존하며,600초 이내 성공이라고 표시하지 않는다. 원1800초 allocation이나 R9/FULL005 deadline을 다시 초기화하지 않았다.

승인된 첫 실패 중단 조건에 따라 `age64_native`, `transport128_reference`, `transport128_native`는 **NOT_STARTED**다. 남은 예산으로 다른 계산을 자동 실행하지 않았다.

- 수락된 저장 상태: **35개**, 마지막 x는 목표Δln(a)=.002의 **53.90625%** 지점이다. 전체 목표 구간 완료가 아니다.
- 실제 native elapsed clock 범위: **0.004183590–0.288898304Myr**, 원점은a0=1/21이며 절대 우주 나이가 아니다.
- 저장 좌표에서 해독한 gas T: **7999.691998→7980.094764K**.
- 마지막 HII/HeII/HeIII fraction: 0.010034903742974088, 0.010035366355776688, 0.000999579849723565.
- 관측 peak treeRSS: **117641216bytes**. 관측 treeCPU: **584.49s**. Wait4의user/system은Killed Python process 범위이며 전체native serverCPU를 정확히 회수한 값으로 쓰지 않는다.
- 저장된 provider trial rejection32개, 마지막 기록calls8420. 마지막 총RHS는강제종료로 **UNKNOWN**, 관측하한8420이다. 원 positive_solver 내부 retry 정책은 그대로며 controller 새 실행/retry는0이다. 실제32개 terminal solve 실패로 해석하지 않는다.
- 본 실행은 원 single-case/단일thread 계약을 유지했다. NCP64core 전체 활용을 달성했다고 주장하지 않는다.

## 실제 그림·표와 후처리 검증

[Proper-time abundance](results/age64_Y_vs_time.png) · [Gas-temperature abundance](results/age64_Y_vs_Tgas_chronological.png) · [35-row CSV](results/age64_accepted_Y.csv). 각각의 PDF도 저장했다.

모든35개 accepted 좌표를 원 `gas_decode`의 역변환으로 읽고 원 H/He 이상기체 EOS를 대수적으로 적용했다. 시간은 저장된 native `birth_times_s`다. 새 quadrature·rate·provider·helper·RHS는0이다. 기존age32의 저장된 최종상태에 대한 한 번의 새 후처리 확인에서 gas4성분 차이는0, native 직렬화T와의 차이는9.094947017729282e-13K였다. 이는 새EOS/physics 정확도 승인이 아니다.

Y는 이 모델의 `n_H+4n_He` 분모를 쓴 H/He-only abundance다. Electron은별도이며 baryon합에 넣지 않는다. 그림은 **accepted prefix / target interval incomplete**를 명시한다. 모든 저장점을 보존하고 T로재정렬하지 않았으며, 정확한zero는mask했다. 초기t0점을 만들어 넣거나 D/나머지isotope를가짜zero로 추가하지 않았다. Max HHe baryon identity roundoff는2.220446049250313e-16다.

## 정확한 결손과 다음 전이

새endpoint/observations.json/solver_return.json이 없으므로 age32→64의frozen0.5% endpoint 기준, Gamma/heat·age-survivor·paired native/time 오차는 **NOT_EVALUABLE**다. 수락된 gas좌표의T나보존합이 이 결손을 대체하지 않는다. RUX의unknown/tail/absolute-IVP와 기존 source-age/spectral/native-time HOLD를 유지한다. 전체FLRW·signedBianchi·17/21상태coupled망 및fullEoR 완료가 아니다.

별도 source 조사에서 native `matrix_native`의 공통mesh가[8,16,32]로고정돼 있고 `trial_impl`이mesh밖birth를거부함을확인했다. age64native는 이번에실행하지않았으므로 실제COHORT_MESH_DOMAIN exit가관측됐다고주장하지않는다. 다음새계약에서는 이mesh와age32/64의시간격자공정성을 먼저 정해야 한다. 이번승인에서solver/closure/mesh/tolerance를수정하거나추가resource할당을하지않았다. 자원한도와native source/mesh 결손을해석할독립과학판정은 **NOT_ISSUED**다.

## 재현·보존

`APPROVED_EXECUTION_PACKET.json`, `SOURCE_BINDING.json`, `ALLOCATION.json`, `TERMINAL_RETURN.json`, `supervise_ready.py`에정확한argv/cwd/source/config/deadline/exit/wall/CPU/RSS를보존했다. 전체35accepted NPY와32failed-trial NPY, 원logs/setup, ELF는저장소밖 raw archive에보존한다. 공개Git에는새CSV·PNG/PDF·보고서·실행metadata와후처리코드만넣는다. 첫원실패와기존PR171기준은그대로다.

`python -m json.tool research/bass_source012_source_age_reference_20261016/pr171_ready_001/RETURN_CONTRACT.json`

Checkpoint `PAUSED_RESUMABLE`, goal미완료. 이문서는실행·후처리결과를보고하며독립과학승인을발급하지않는다.

## 게시 확인

결과 content commit `bc991fdd5e0af4504213946a43000dee081325e0`를 기존 branch에 push하고 원격 SHA 일치를 확인했다. 기존 draft PR150의 본문에 이번 실제 결과를 추가했다. 공개 결과 ZIP(350400bytes)과 비공개 원자료 archive(1310257bytes)는 각각 Dropbox 원격 readback SHA256 일치를 확인했다. 세부 영수증은 `BACKUP_RECEIPT.json`, `RAW_BACKUP_RECEIPT.json`, `PUBLICATION_RECEIPT.json`에 있다. 공개 ZIP은 content commit에 고정되며 이후 게시 영수증은 별도다. 게시 확인은 과학 승인으로 해석하지 않는다.
