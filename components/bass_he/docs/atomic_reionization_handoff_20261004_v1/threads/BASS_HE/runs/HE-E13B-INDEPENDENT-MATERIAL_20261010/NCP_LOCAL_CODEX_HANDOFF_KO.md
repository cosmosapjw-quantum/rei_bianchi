# NCP E13B 수신 / E13C 실행 경계

ROLE=BASS_HE_SOURCE_PINNED_POST_E13B_CONSUMER

E13B의 독립 low-T material RHS는 원 E13A 여섯 midpoint에서 완료됐다. 별도 재구현이나 동일 science 반복을 다음 선행조건으로 만들지 않는다. 현재 Git HEAD/AGENTS와 같은 폴더 README/RETURN/INPUT_PIN/DELIVERY_RECEIPT를 먼저 읽는다. 정확한 archive는 BASS_HE_E13B_INDEPENDENT_MATERIAL_20261010_v1.zip, 126638bytes, SHA2563dd8d8c17cb65182289755015d9d66cec7d446cb62688168db5c5d874d47f757이다. 기존 cache/rclone/인증된 cloud를 사용하고 사용자 수동 업로드를 기본 요구하지 않는다. 한 provider bytes만 복원하고 다른 provider는 metadata를 대조한다.

Drive file ID 18VuV1vOs7p5CbRSYjP2bq7SF5Zbm3s9T. Dropbox 경로 /BASS_DERIVATION_DOSSIERS_20260912/BASS_HE_E13B_INDEPENDENT_MATERIAL_20261010_sha_3dd8d8c17cb6.zip. 봉인 ZIP을 새 디렉터리에 풀면 BASS_HE_E13B_20261010_v1/ 안에 전체 Python source/tests/input/evidence가 있다. 기본 `python3 -B -W error reproduce.py --output NEW_DIR`는 파일·입력 검증만 수행하며 native0/material신규계산0이다. 호스트 재현이 실제 필요한 경우에만 별도 NEW_DIR와 --recompute로 새22tests+같은6profile 평가를 한다. mpmath1.3.0, symbolic만 SymPy1.14.0. Rust/MPI/3x384가 필요하지 않다.

다음 과학목표는 HE-E13C_PHOTON_TRANSACTION_INPUT_AND_INDEPENDENCE_GATE다. 같은6transaction에 대한 photon node/weight/initialdensity, sourcebirth/cutoff 분할, subsegment stage endpoints/gas interpolation/frozen opacity/energy evolution 및 A/B reduction 순서를 기존 E13A/E12/source에서 read-only로 조사한다. 현재 aggregate A/B와 stage count만으로 독립 photon oracle 입력이 완전하다고 하지 않는다. C1 frozenkernel·E4/E6 observer 성공을 이름만 바꿔 새로운 source certificate로 쓰지 않는다.

E13C의 독립 photon evaluator/계측은 아직 본 패키지에 없다. 준비되지 않은 새 full3x384를 launch하거나 이미 통과한 E12/E13A를 단순 복제하지 않는다. 필요한 최소 원시입력 계약을 PHOTON_INPUT_READINESS.json으로 반환하면 ChatGPT 연구자가 그 계측과 독립 evaluator를 먼저 완성한 뒤 별도 bounded 계약으로 넘긴다. 이것은 E13B 결과를 OPEN으로 되돌리는 것이 아니다.

BaselineRCTOFF, momentsnull, physical/productionHOLD, HE-F2/F09OPEN, Gammaalias3.543295FAIL과 원 GMstep7 near-gate를 유지한다. source/단위/clock/mean35eV/CI floor/CE cap/DR guard/TOL을 바꾸지 않는다. 다른 HH/CR/REI 과학을 자동 dispatch하지 않는다. Receiver 원격 및 default에 무단 mutation금지. Source Debug는 restart codec가 아니다.

수신 명령/exit/SHA, 실제 입력 준비 상태와 다음 최소계약을 기존 BASS_HE branch additive/non-force와 Drive+Dropbox create-only로 남긴다. ACK/메타데이터와 실제 복원, 과학 PASS/물리 승인을 분리한다.
