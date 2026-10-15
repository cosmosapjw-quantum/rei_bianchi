# Covariant transport: HI cut-cell native variant

현재 unit은 **PASS_SCOPED_CUT_CELL_IMPLEMENTATION_AND_FRESH_SHORT_PILOT**다 (`CUT_CELL_REVIEW.json`). 새 partition4개와 driver7개, 총11개 고유 검증이 통과했다. 기존28검증과 Unit1의22개는 재사용했고 반복하지 않았다. Component 게시와 실제 NCP fresh short q128 pilot은 승인되었지만 full-history admission은 완료된5case screen까지 보류한다. 실제 fresh q128은 `raw/ncp002_q128_poll_001.json`에서 실행 중으로 확인되었다: 시작13:28:44Z, 관측13:29:23Z, native1thread/CPU0, V4checkpoint1320accepted와 sourceidentity 일치. Endpoint와5case screen은 아직 완료되지 않았다.

선택한 `inactive_hi_split=true`는 기본 false인 명시적 variant다. 현재 H/He-only의 qref=0, forward·비증가 photon energy에서만 활성화한다. 기존 positive closure를 실제 HI fit edge13.60eV의 양쪽으로 제한해 같은 q-cell/ray에 active N/Q/support와 passive N/Q를 저장한다. Passive는 버린 photon이 아니라 계속 redshift하고 radiation inventory/work/stress에 포함되는 stock이다. Source와 cold BE/Newton chemistry는 active만 한 번 소유한다. 두 pool의 transfer는 boundary loss나 absorption이 아니다.

Adaptivity는 대응 cell마다 |ΔNactive|+|ΔNpassive|와 같은 U 차이를 기존 total denominator/floor로 정규화한다. Gas/thermal 항과 physical tolerances는 유지했다. V4 checkpoint는6arrays이고 outer exact source/config binding이 authoritative하다. History25/spectra12 format과4pool VALUE ledgers를 보존한다. General anisotropic/blueshifting mode와 향후 lower-threshold absorber의 passive 분류는 이 단위의 admission이 아니다.

첫 driver test는6PASS/1FAIL이었다. Substring selector가 `inactive_photon...` 안의 `active_photon...`까지 세어 생긴 false FAIL이다. Exact CSV ledger-name 비교로 test만 고쳤고 production source는 바꾸지 않았다. Focused 두 번째 실행에서 고친 output test와 새 passive merge helper가 통과했다. 앞서 통과한 driver6/partition3은 반복하지 않았다. 원시 실패·repair 영수증은 `INACTIVE_DRIVER_RESULT.json`에 연결된다. 그 파일의 review-pending 상태는 완료된 `CUT_CELL_REVIEW.json`으로 갱신했다.

사전 고정 candidate control은 보존한12000-step state에서3comparisons·9tentative·63RHS를 실행했다. h의 total/strong metric≈2.648206e−7은 baseline3.963479e−6보다 약14.966655배 작고 사전 factor5 bound를 통과했다. Gas/domain/augmented ledgers와 stronger split norm도 통과했다. 이는 국소 discrepancy 감소이며 end-to-end runtime speedup이나 full-history convergence가 아니다. `CUT_CELL_THEORY.md`는 해당 preimplementation 단계의 기록이고 현재 구현 판정은 `CUT_CELL_REVIEW.json`이 소유한다.

Actual NCP stage002는 source hash 검증과 offline release build를 완료했다 (`raw/ncp002_stage_build_receipt.json`). 관측된 fresh q128은 기존 z20→19.8 한도600s/20k accepted/65k tentative/5M RHS/256MiB output/8GiB AS를 따른다. 먼저 q128을 완료한 다음 나머지 q256/q512/time/angle cases를 최대2개씩 수행한다. 완성된 실제 screen과 review 전에는 full campaign gate를 열지 않는다.

보존된 baseline q128은20000accepted cap,z19.97343215826658,466.2802s에서 멈췄다. Ledgers/source binding은 통과했지만 목표19.8은 미완료다. Full raw/diagnostic은 `PILOT_BACKUP_RECEIPT.json`의23,427,127-byte ZIP으로 실제 Drive/Dropbox 이중 backup되었다. Unit1 구현·D point provider는 commit a71052cec02c48c08d6823e00331fab1db654a76와 PR150에 게시되었고 영수증은 `DELIVERY_RECEIPT.json`이다. 새 cut-cell unit의 게시 완료는 별도 실제 기록 전까지 주장하지 않는다.

D atomic 모델 `GRACKLE_3_4_1_H_EQUALITY_D_ATOMIC_V1`의8개 검증과 standalone review는 Unit1 범위로 재사용한다. H-equality approximation과 명시적 χD/defect, conditional H1/D/He4 fixed-nb helper이며 matched REC/새 BBN donor가 아니다. D cosmological coupling은 아직 없다. 3He/Li actual source 후보와 Li photo/RR tables는 확보했지만 sub-Lyman source/transport, CI/DR/CX와 thermal moments는 별도 입력이다.

우선순위는 FLRW fresh short screen → full production/refinement → signed Bianchi±0.005/±0.01과 실제 proper-time/Tgas plots → D coupled isotope network다. `HANDOFF.json`의 unit_history는 Unit1/첫 실패를 보존하고 current_unit·next_node가 현재 실행을 가리킨다. `CODING_LOOP.json`은 이 cut-cell unit의 정확한 C1–C10 관측을 별도 기록한다. 요청 worker model과 실제 runtime model의 미관측 상태를 구분한다.


현재 다음 unit은 사용자22:31KST 지시에 따른 `NCP64_HPC_PARALLEL_IMPLEMENTATION`이다. 실제64CPU/128GB를 활용하는 구현을 요구했으므로 과거의 인위적 동시2case/1native-thread 제한을 앞으로의 전역 정책으로 재사용하지 않는다. 새 HPC addendum과 명시적 자원·소유권 계약을 고정한 뒤 실제 병렬 구현·변경 검증·측정을 수행한다. 현재 NCP002 실행과 frozen NATIVE_CONTRACT/compiled identity는 그대로 보존한다. 이 요청은 아직 구현·성능 완료가 아니며 physical/localerror/ledger/refinement와 full-history admission 조건을 완화하지 않는다. 이 문서의 기존2case/1thread·600s 한도는 이미 시작된002 및 해당 frozen short-pilot 계약의 역사적 범위다.
