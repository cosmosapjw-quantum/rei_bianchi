# 현재 저장소와 재사용 판단

2026-10-14 04:47 UTC부터 완료된 GitHub read-only snapshot의 기계적 재서술이다. [PR_INVENTORY.json](PR_INVENTORY.json)은 100+1 두 페이지와 각 PR의 상세 metadata로 확인한 101 open PR 전체를 보존한다. 과학 실행·테스트를 이 조사에서 수행했다는 뜻은 아니다. 이후 새 PR·push가 생기면 live 상태는 달라진다.

| 경로 | 관측 head | 판단 |
|---|---|---|
| main | ae3402713c4b6530ab2b27f008f5f5d5c6a999ed | active Rust/AGENTS가 없는 이전 tree; 실행 base로 선택하지 않음 |
| PR83 / forward | c07fc7e765ce204bc3e84016cc6874612e535b86 | active 운영 정책·adopted v2·Rust geometry/packet core |
| PR104 | f66929c23ea3fa6e39dd4808e5b27d136c568a03 | reduced history retained baseline; 별도 branch의 runnable/evidence |
| PR110 | 17f8d0daa72e0f76a49cde01b110f650a6688c42 | ACCEL02 native full-history 별도 계보; v2에서 off critical path |
| PR114 | a5c958c414dea41216b445c05f58df837f05cacb | E-P receiving candidate, conditional warm Case-A event bundle |
| PR115 | 39dce6702dcadbb516fc8e25e7ba5a6991f64c22 | 제목 R5보다 실제 파일의 OBSERVER15 R8이 최신 |
| PR116 | 2df18a7238b3e52d0eb844fd45aa706dbf883ab3 | 별개의 microphysics R8; eight heavy jobs, zero ready/executed |

101 PR 중 PR84만 mergeable=false로 관측됐다. 이 값은 Git 병합 가능성일 뿐 scientific admission/merge 허가가 아니다. PR83 changed-file 목록은 3000개 제한에 닿았으므로 완전한 file inventory로 쓰지 않았고, untruncated head tree를 별도로 읽었다. PR83에 `research/`가 없으므로 PR104/114/115/116의 code/data가 그 checkout에 이미 있다고 가정할 수 없다. 전체 stacked PR 병합을 목표로 삼지 않는다.

현재 재사용 가능 Rust API는 `bianchi_i.rs`의 GeometrySnapshot/GeometryBackground/CharacteristicRay와 `angular_photons.rs`의 PhotonPacket/RadiationState/PhotonGrid/PhotonBins 및 `lib.rs` export다. `paired_history.rs`는 실제 F08 frozen-input runner지만 새 SOURCE07 observer consumer의 완성 증거는 아니다. 조사한 source에서 polarized Thomson runnable module은 확립하지 못했다. 그 기능이 필요할 때만 실제 지원 연산자/entrypoint를 작은 별도 작업으로 다룬다. Python plotting/orchestration은 Rust production kernel을 대체하지 않는다.

SOURCE07 same-event ledger, FLUENCE08 fixed-energy subflow와 SHEAR12 matched-expansion weak-shear response는 이미 기록돼 있다. 같은 초기 synthetic suite를 반복하지 않고 source/model/observer delta만 실행한다. full runnable payload가 archive에 있는 계보는 공개 Git entrypoint와 실제 code/data 복원 여부를 구분한다.

OBSERVER15 R8은 **ACCEPT_SCOPED_FINITE_GL32_CUBIC_REFERENCE**이며 같은 finite source의 R7-A cubic을 선택한다. R7-A/B는 filename이 비슷해도 proof/implementation identity가 다른 archive다. 실제 PL 소비에는 PL bound를 쓰고 cubic certificate에 PL 나머지를 추가하지 않는다. 다음은 `R9_SOURCE07_SAME_TARGET_CUBIC_RETURN_CONTRACT`다. native tolerance, continuum-energy error, finite-epsilon remainder, physical opacity 및 unrelated foreground/tail은 미확인이고 production receiver는 완료로 승격하지 않는다.

| 직접 supplier | selected PR/head | 재사용 범위와 다음 단계 |
|---|---|---|
| BASS_HE | 47 / dff95caa7fabb2a38acf73ba0946a1d88a125f3d | warm P01 2913×17 states·2904 photon nodes 회수. R3 claim/premise alignment 후 residual/tube 입력 고정; true-IVP absolute column/probability는 null |
| bass_cr | 58 / 808d11c1869c6334572554edcb24370e35c69f44 | finite-rate constructive bound; proper-time tau는 regularization이며 microscopic calibration 아님. 다음 NT_COULOMB_MATCHED_PARTITION_DECISION |
| WU088_HH | 64 / 6320b23cba96abf12b150eea439e458f86aa1d69 | warm P01 signed differential electron/thermal/column response. absolute true-IVP baseline은 null. 다음 PHYS32_TWO_CENTRE_CONTINUUM_DEFECT |

HE native/reference NPZ가 byte-identical이라고 기록된 부분을 독립 적분 두 개의 일치로 중복 계산하지 않는다. 선택 writer/archive에서 historical dense polynomial을 못 찾았다는 관측은 사용자 disk 전체 부재 주장이 아니다. 저장 상태로 새 reconstruction이 가능하더라도 그 범위를 구분한다. warm P01에 CR cold-target/SHEAR12 상계를 이식하거나 작은 HH 차분 상계를 더해 absolute baseline 인증이라고 쓰지 않는다.

우선순위는 실제 E-P entrypoint·provider delta를 선택하고, scenario/source/domain/owner 필드를 freeze한 뒤 첫 coupled FLRW interval을 얻는 것이다. source 미비는 그 물리 run만 HOLD하고 retained endpoint 보고서, source consumer 준비와 경량 plot은 진행한다. microphysics R8의 8개 미준비 heavy provider 또는 CR/HH 전체 연구를 첫 H/He baseline의 전역 gate로 올리지 않는다. full 17-state registry는 실제 donor trajectory나 완전 rate network가 아니다.

[BACKUP_STATUS_PUBLIC.json](BACKUP_STATUS_PUBLIC.json)은 current full-byte read, report text read, metadata 및 historical ACK를 구분한다. 이는 과학 결과 승인과 다르다. 실제 NCP process/checkpoint는 이 GitHub 조사에서 확인되지 않았으므로 C0에서 현재 상태와 실제 output 경로를 확인한다. 10월11일 checkpoint를 최신으로 가정하지 않는다.
