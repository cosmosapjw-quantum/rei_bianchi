# WU R3 최신 공급자 additive overlay

2026-10-27 prepublication refresh에서 `research/provider-registry-20261025`의 실제 HEAD를 `80c0d758a5d5b3c030b20c874b8e1852fcb46f82`로 다시 확인했다. 최신 AGENTS를 먼저 읽고 지정된 최소8파일만 수용했다. 원전 파일132,139 bytes의 Git blob과 SHA256을 `SOURCE_MANIFEST.json`에 고정했다. 기존17 snapshot과 `CONSUMER_PROJECTION.json`은 변경하지 않았다. 기존 projection SHA256은 `e10b896d11863cfac9bb1e457bf539d4ed577fae289f3775ee957d0555bfe368` 그대로이다.

## 현재 유효한 source 범위

| 항목 | R3까지의 상태 |
|---|---|
| 종·상태 ID | 92개 그대로; 새 종0 |
| 공급자 variants | R1 102 + R2 26 + R3 4 = **132** |
| 기존 정수 사건 열 | R1 125 + R2 24 = **149**, 재사용; 새 compiler 호출0 |
| 원래 target/direction | 19개 ID / 28개 방향을 모두 유지; **28/28 primary-source references** |
| Target6 | `TARGET19:06:target_forward`의 실제 수치 원전 공백은 **COMPLETE_SCOPED** |
| 물리 계수·상태·branch·Q·energy·consumer | 승인 false, activation false; parent registry PARTIAL |

R3 composite catalog의 R1/R2 provider·species SHA가 기존 snapshot과 정확히 일치했다. R3 target6의 `before`도 기존 R2 방향과 동일하며, 바뀐 것은 원전에 선언된 source metadata5키뿐이다. 기존 두 D 정수 열 `TARGET19_PHOTONUCLEAR:06`을 재사용한다.

## 실제 추가 원전

공식 `IAEA-NDS/exfor_master@939a14d7bba1ddce51975cb5e8711ce96b3b0871`의 He4(gamma,d)D TABLE 공급자를 WU가 회수했다. 이 묶음은 그 pinned·검토된 packet을 소비한다.

| Variant | Native 수치 행 | 관측량 |
|---|---:|---|
| `EXFOR_M0011002` | 14 | SIG, listed incident energy |
| `EXFOR_M0475002` | 12 | **DA_CM angular differential** |
| `EXFOR_M0475003` | 6 | SIG, listed incident energy |
| `EXFOR_M0826002` | 4 | Incident-energy-bin SIG |

합계36행은24SIG+12DA이다. E2 7행은 별도 auxiliary이며36행에 더하지 않는다. 이 최소 overlay는 E2 원문을 다시 추출하지 않고 upstream coverage/admission의 일치하는7행 기록을 보존한다. CURVE 자료는 main에서 제외된다. Packet SHA256은 `d8b0b92f0374f73fa7f838db5ca07be45bd448696654b07c6db71c5847235ac2`이다.

실제 angular DA12행이 있으므로 현행 설명을 단순히 “각자료 없음”으로 쓰지 않는다. 다만 유한 각 표가 event-normalized 전체 DCS, 연속 joint final-state law 또는 physical runtime provider를 완성하지는 않는다. SIG와 incident-energy INT, bin SIG와 pointwise sigma를 구별한다. Identical-D event/particle counting, full-sphere convention, beam response, ionic/electronic/nuclear state, covariance, 실제 MeV photon consumer가 남아 있다. D 두 개라는 이유만으로1/2를 곱하지 않는다. M0826≤5% beam-intensity bound를 Gaussian 총오차로 쓰지 않는다. REC의 atomic/≤50keV 자료를 이 MeV 핵 photon consumer로 대체하지 않는다.

## 문서·DAG 수정과 재사용

현재 상태를 설명하는 “27/28이며 target6 수치 원전이 없다”는 문장은 **“R3에서19 target/28 directions 모두 source reference 확보; target6 measurement-to-event-rate 및 consumer binding은 OPEN”**으로 갱신한다. 현재 provider total은132이고 species92와149기존열은 그대로다. 과거87933 snapshot에 적힌128·27/28은 역사적 결과로 보존하고, 이 `OVERLAY.json`을 최신 상태로 함께 읽는다.

Source availability node만 닫는다. `TARGET6_MEASUREMENT_TO_EVENT_RATE_BINDING`, photonuclear runtime binding, 전체 rate/Q/consumer 승인은 계속 OPEN이다. HD 형성/파괴와 LiH 형성/nonphoto-destruction 같은 기존 molecular source 범위도 이 nuclear update로 닫히지 않는다. 전체 registry는 PARTIAL, global physical completion은 null이다.

Upstream Primary8/8, 독립 source9/9, static implementation PASS와 최초 auxiliary-class failure/G6 repair를 C9·admission으로 재사용했다. 이 소비자 intake에서는21개 source/hash/JSON 관계 검사가 통과했으며 rate/Q·과학 실행·compiler·기존249/과학 replay는0이다. 최초 API file text를 JSON metadata로 읽으려다 발생한 Markdown parse 오류는 `OVERLAY.json`에 보존했다. Targeted correction은 file text와 directory Git metadata의 구분뿐이었다.

원전8파일은 `raw/`, 정확한 identity는 `SOURCE_MANIFEST.json`, 합성 상태·21검사·문서 수정 지침은 `OVERLAY.json`에 있다. Upstream source commit/ZIP/dual-backup 완료 여부는 이 minimal intake에서 재구성하거나 새로 주장하지 않는다. HE101 C8 OPEN·기존 소진 예산과 다른 소유자의 완료 결과도 유지한다.
