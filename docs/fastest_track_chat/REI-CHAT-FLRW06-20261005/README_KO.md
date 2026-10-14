# REI-CHAT-FLRW06-20261005

상태: **REFERENCE_COMPLETE__NATIVE_BLOCKED**. FLRW06의 실제 native regression을 완료 처리하지 않는다.

FLRW05의 96개 node를 실제 public Rust API에 연결하는 것이 주 작업이다. 이 환경의 rustc/cargo 부재로 native preflight는 exit 78이며, compile/call은 모두 0회다. 단일 rustc용 runner와 driver를 준비했지만 Rust driver는 컴파일 미검증이다. Python 기대값과 protocol tests를 native 성공으로 바꾸지 않았다.

## 완료한 연구

정확한 binary64 입력에 대한 80자리 독립 finite-node reference 11개를 계산했다. 기존 FLRW05 baseline의 27개 field 중 18개가 비영이며, 최대 상대차는 2.3871363948098301e-15다. Node 역순, 가중치 분할 및 scale-factor의 이진 배율 변환이 나타내는 같은 measure도 확인했다. 새 원자 fit의 물리적 정확도 인증은 아니다.

고정 bin [L,R]의 양의 spectrum moment 조건은 N>=0, U-LN>=0, RN-U>=0이다. 고정 forward-Euler 방향에서 q=(N,U-LN,RN-U), d=(dotN,dotU-L*dotN,R*dotN-dotU)를 정의하면 hmax=min_{d_j<0} q_j/(-d_j)가 정확한 closed-cone timestep 상계다. 모든 방향이 비음성이면 유한 제한이 없고, zero face가 바깥을 향하면 hmax=0이다. 이 조건은 안정성, truncation error, root, interval 또는 physical certificate가 아니다. 유한 exponential reconstruction은 N>0에서 strict interior를 요구하며 경계 평균에는 explicit delta가 필요하다.

정확 반례: [10,20] eV, N=1, U=15, dN/dtau=-1, dU/dtau=-25. Count-only 제한은 1이고 cone 제한은 1/3이다. Delta tau=1/2에서 N=1/2>0이지만 평균에너지는 5 eV로 bin 밖이다. 현재 native 코드의 버그 판정은 아니다.

| bin/eV | count-only 제한/s | moment-cone 제한/s | 제한 face |
|---|---:|---:|---|
|13.6–24.59|1.113020926458034e11|9.718025354290178e10|RN-U|
|24.59–54.42|7.428367066492438e11|5.759105963788322e11|RN-U|
|54.42–100|5.132056142366495e12|3.433917399651662e12|U-LN|

같은 photo/edge measure에서 흡수 에너지=binding+heat와 전체 radiation energy/work/edge 수지를 검산했다. 독립 U는 아직 native photon_balance의 소비 범위 밖이다.

## 검증과 남은 작업

최종 네 명령은 exit 0이었다: 새 80자리 reference, stage/cone, 14개 unit/protocol tests, Python syntax. 정확 유리수 240개와 기호 항등식 4개를 검사했고 count-only helper의 red/green 로그를 보존했다. Protocol의 제조 출력은 실제 native 증거가 아니다. Native 오류 입력 6개와 scalar 비교 167개는 준비됐지만 실제 호출은 0회다. ODE, 과거 suite 재실행, 별도 reviewer dispatch도 0회다.

다음 task는 계속 FLRW06_NATIVE_SPECTRAL_STAGE_REGRESSION이다. Rust compiler가 있는 기존 repo 환경에서 ZIP을 해제한 후 다음을 실행한다.

    python research/run_native.py --repo /path/to/rei_bianchi --output /path/to/new_result_directory

Source 6개를 git show와 원 Git blob으로 고정하고 scientific module 5개는 byte 변경 없이 사용한다. 원 lib의 공통 type 정의에 최소 wrapper와 driver만 연결하여 단일 rustc compile과 단일 probe process를 실행한다. Cargo, 전체 crate, 과거 시험, network, history는 실행하지 않는다.

PhotonInput absorption은 실제 native bin0/1/2 event 반환에서만 계산한다. Python expected sink를 입력하지 않는다. Source/input/compiler/binary/stdout identity, compile/run 성공, 167개 scalar 비교와 6개 정확한 error code가 있어야 제한된 pointwise PASS다. 이 반환도 full-crate integration, expanding history, 독립 U 소비자, physical 또는 interval 승인을 뜻하지 않는다.

## 외부 상태 동기화

시작·단계 경계·게시 전 HEAD는 b553698a114fbff05640ab6ecb95d260410de492였고, 이전 chat commit 69fd2901 이후 3개 commit을 수신했다. 최신 runtime 반환은 REI-F04를 pinned static FT03 numerical domain에 한해 completed로 기록하며 다음 외부 task는 REI-F05다. 받은 checker의 최대 local bound는 9.534453118819423e-9, public width는 1.5867951486958153e-6이고 physical 상태는 HOLD다. Checker를 여기서 재실행하거나 그 인증을 expanding spectrum에 이전하지 않았다. 오래된 pending 필드는 현재 판정으로 사용하지 않는다.

## 재현 패키지

- 파일: REI_CHAT_FLRW06_20261005.zip
- 크기: 73574 bytes, 50 entries
- SHA-256: 0796a9749156cce3f1ee26e204a367bd96802672c7ff32ba1c4edd9b311efeca
- Drive: https://drive.google.com/file/d/1ZGqf78dFM4ysZeMJ062DoskvXuKQ1NaG/view?usp=drivesdk
- Dropbox: /BASS_DERIVATION_DOSSIERS_20260912/ATOMIC_REIONIZATION_HANDOFF_20261004_v1/REI_CHAT_FLRW06_20261005.zip

ZIP의 rei_chat_flrw06_20261005/ 아래에 전체 REPORT_KO.md, 코드, driver, 입력, 기준값, 실패·최종 로그와 MANIFEST.json이 있다. 이 repo 폴더는 요약·계약·반환·인계·영수증만 추가한다. 백업은 두 provider의 ID·크기를 확인한 R1 metadata 수준이며 원격 byte hash 또는 restore 검사는 하지 않았다.

원 F00/F03/FT03, CODEX_SYNC와 runtime_returns를 수정하지 않는다. Strict local<2e-4, public width<2e-3, [160,161] FAIL=2.1245050576368385e-4, tick160 및 physical HOLD를 보존한다. 새 branch, merge, force push는 없다.
