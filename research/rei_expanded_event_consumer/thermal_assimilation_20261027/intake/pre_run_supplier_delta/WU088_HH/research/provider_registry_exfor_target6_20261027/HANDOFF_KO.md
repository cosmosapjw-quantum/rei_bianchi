# WU088_HH: EXFOR target6 source R3 인계

## 즉시 읽을 현재 권위

이 leaf의 REPORT_KO.md, SCIENTIFIC_ADMISSION.json, reviews/C9_FINAL.json, DAG.json, EXECUTION_LEDGER.json과 delivery/PUBLICATION_AND_BACKUP.json을 읽는다. Root AGENTS의 현재 priority가 R3를 가리킨다. 사용자가 지정한 고정 인계 `program_expansion_20261025/HANDOFF_KO.md@34dd7d1d018abff8a0a4ebd1d3f3579ac46d2fad`는 그대로 보존한다.

## 완료한 과학 입력

공식 EXFOR `939a14d7bba1ddce51975cb5e8711ce96b3b0871`에서 target6 `⁴He(γ,d)D`의 TABLE 공급자4개, 수치36행을 회수했다. Main 공급자는 M0011002(14 SIG), M0475002(12 DA_CM), M0475003(6 SIG), M0826002(4 energy-bin SIG)다. E2 7행은 auxiliary, CURVE3subentry는 main에서 제외한다.

Packet SHA256: **d8b0b92f0374f73fa7f838db5ca07be45bd448696654b07c6db71c5847235ac2**. Manifest SHA256: **a1c5d4009d0bfacc4edcb248a6878eef6cdafa9690b4ea0d0826dd5356052d06**.

이로써 원19 ID·28명시방향 모두에 실제 primary-source 참조가 생겼다. R2 target6forward의 source metadata5key만 추가/갱신했다. 모든 기존 물리 필드는 그대로다. Composite catalog는 R1 102variant/92identity, R2 26variant, R3 4variant를 원파일/SHA로 이어준다. 저장된125개 R1 열 및24개 R2 열, 특히 target6 +2D 열을 재사용했다. 새 compiler 호출0이다.

최종 source 수용은 **ACCEPT_SCOPED_EXFOR_TARGET6_SOURCE_REFERENCE_CLOSURE**다. Primary8/8, 독립 source9/9 합성, 별도 static implementation PASS이며 blocking finding0이다. 최초 independent01의 auxiliary-class 기대값 실패는 immutable raw/JSON으로 남아 있다. 이미 통과한8군을 다시 실행하지 않고 G6만 11조건+5reuseguard로 교정했다.

## 확대하면 안 되는 승인

28/28은 원 명시 방향의 **source-reference availability**다. 실제 rate/Q/state/branch/energy/consumer admission은 모두 false, activation=false다. SIG와 DA, incident-energy bin SIG와 INT, source isotope label과 bare-state binding, exclusive channel identity와 branching fraction을 구분한다. M0826≤5%는 beam intensity 상한이며 Gaussian 총오차가 아니다. 공분산·신뢰확률·Q·branch fraction은 null이다.

원 실험의 identical-D event/particle/full-sphere 규약 및 response, actual MeV photon consumer가 미결속이다. D 두 개를 이유로 기존 SIG에 1/2를 적용하지 않는다. 기존 REC 원자/≤50keV 자료를 이 MeV 핵 반응의 consumer로 임의 연결하지 않는다. Synthetic249check도 물리 rate나 핵Q 승인이 아니다.

## 재사용·복구·DAG

재개 시 로컬 runtime artifact가 없었고 정확한 R2 metadata87933da와 sourceZIP을 원격에서 복구했다. ZIP 7,084,911bytes, SHA43845ea085797a6d628b722d58197a64a0af6f0a34a708f3dc981a5274faa906, CRC 및380memberhash를 실제 확인했다. 완료한 과학 계산은 재실행하지 않았다.

최신 중앙 REI a5db4bac…의27/88과 미병합 PR236 ee94bef8…의32/88을 구분한다. 다른 owner의 종 사영·normalized beta·native PW19/25좌표 source 결과를 재사용하며 중앙ACK를 가정하지 않는다. R3 DAG는 이전19로컬노드를 보존하고 source하위노드1개를 더했다. Parent 전체 registry는 PARTIAL, 새 중앙 완료 주장은0이다.

R3 source 단계5bounded child의 CPU0.920505s, wall2.053690392s는 일부 비용의 계측이다. 미측정 비용은0이 아니다. PHYS91 primary/reference/Wolfram remaining0, global historical CPU/money/remaining=null을 유지한다. HH_R10=OFF, production=NOT_ISSUED, L4_ready=false다.

## 다음 작업과 전달

NEXT_SOURCE_INTAKE_KO.md에서 실제 새 source 또는 consumer 입력이 필요한 부분을 시작한다. 모든 노드 전에 실제 최신 AGENTS·HEAD·병렬 작업·backup을 확인한다. 완료한 R1/R2/R3 추출·계산·검증은 identity가 유지되면 재사용한다.

사용자가 자동 게시와 Dropbox/Drive backup을 명시적으로 승인했다. source snapshot 작성 시 기대 부모는87933da5654bb2e4d93f7de4341df5e0fa0f8716, target은 기존 draft PR150 branch `research/provider-registry-20261025`다. 실제 source 게시 뒤 sourceZIP을 만들고 양쪽 actual bytes를 대조한 영수증을 별도 metadata자식에 넣는다. **현재 전달 완료 여부와 실제 SHA는 delivery/PUBLICATION_AND_BACKUP.json을 읽어야 한다.** 이 source snapshot의 계획문을 실제 ACK로 취급하지 않는다.

## 다음 대화에 복사할 인계

```text
$physmath-research-loop로 cosmosapjw-quantum/WU088_HH 연구를 이어가라.
최신 AGENTS와 research/provider_registry_exfor_target6_20261027/HANDOFF_KO.md,
SCIENTIFIC_ADMISSION.json, DAG.json, EXECUTION_LEDGER.json, delivery/를 먼저 읽어라.
공식 EXFOR target6의4TABLE/36행으로 원19target/28방향 source-reference 공백은 닫혔다.
R1/R2/R3 및249check/PHYS91/REI의 완료 계산을 재사용하고 source-reference 승인을 rate/Q로 확대하지 마라.
SIG/DA/bin/E2, isotope/isomer/ionic/electronic/molecular state, branching/Q/uncertainty를 보존하라.
NEXT_SOURCE_INTAKE_KO.md의 실제 다음 입력에서 이어가고 매 노드의 최신 HEAD·병렬 작업·백업을 확인하라.
기존 예산을 보존하고 최소 변경 검증·독립 검토 후 expected-SHA non-force로 게시하며 sourceZIP과
Dropbox/Drive actual-byte backup 및 DAG를 갱신하라. 기존 자동 게시·백업 승인은 지속한다.
```

## 실제 전달 완료 기록

- Source commit: **80c0d758a5d5b3c030b20c874b8e1852fcb46f82**, tree **dcf5af4136b3160a3a4a7488d4ec779b67409c0c**.
- 기대 부모 **87933da5654bb2e4d93f7de4341df5e0fa0f8716**에 대한 expected-SHA non-force 게시 및 원격 readback이 성공했다. 78개 변경 경로를 반영한 결과의 전체 Git tree가 staged tree와 정확히 일치한다.
- Source ZIP: **WU_PROVIDER_REGISTRY_R3_EXFOR_TARGET6_SOURCE_20261027_80c0d758a5d5.zip**, **7,274,563 bytes**, Git 파일 **467개** + manifest = **468 members**. 로컬 CRC 및 모든 파일 바이트 대조 PASS.
- ZIP SHA256: **f83ea212e17318ea80d368f99f56a7e7dc0f908f2578392136acc434e22195ed**.
- Dropbox **id:BSpOijBcT10AAAAAAEC3dA**, [Drive](https://drive.google.com/file/d/1Glyh10AUFixjz4cTWJPNx6ypm-3ErnuX/view?usp=drivesdk)의 저장 완료 ACK를 받았다. 양쪽 실제 HTTP200 다운로드가 각각 같은 바이트 수와 SHA256으로 확인됐다.
- Package child CPU **3.909058s**, wall **4.029770229s**. Source단계5개 child와 합한6개 측정 child는 CPU **4.829563s**, wall **6.083460621s**다. 전체 세션/원격 비용을 뜻하지 않는다. 과거 과학 예산·계산은 그대로다.
- 현재 전달 권위: delivery/PUBLICATION_AND_BACKUP.json, GIT_READBACK.json, SOURCE_ZIP_MANIFEST.json, FINAL_BACKUP_ACK.json, CLOUD_READBACK.json.
- 이 완료 기록을 담는 metadata자식은 backed source commit과 다르다. Metadata의 정확한 identity는 이 파일을 포함하는 Git commit으로 해석하고, 기대 부모source **80c0d758a5d5b3c030b20c874b8e1852fcb46f82**에 non-force 게시한 뒤 최종 HEAD를 별도로 확인한다. Source ZIP에 자기 자신의 후속 전달 metadata가 포함돼 있다고 주장하지 않는다.
