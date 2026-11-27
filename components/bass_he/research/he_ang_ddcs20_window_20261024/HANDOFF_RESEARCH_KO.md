# 다음 스레드 인계: HE-ANG-DDCS20-WINDOW

## 재개에 필요한 현재 상태

이번 단위의 과학 상태는 COMPLETE_SCOPED다. R6 PASS와 C9 PASS_SCOPED,
8 tests/11 checks 및 실제 3개 invocation이 근거다. Root 계약·THEORY·source,
코드·수치·검토 파일을 재사용한다. 실제 과학·중앙·backup identity는
delivery/PUBLICATION.json 및 delivery/FINAL_BACKUP_ACK.json에 연결했다.
현재 delivery 문서를 포함하는 D의 자기 SHA는 미리 적지 않으며,
current-file-commit으로 식별하고 게시 후 외부 postdelivery receipt가 실제 D를 기록한다.

## 고정 게시와 실제 backup

| 역할 | 고정 identity |
|---|---|
| Science S | `d8bae9f7e24ad3494e399f7ab46c4167a5623d48` |
| Central observation C | `6cf7c53757ce4049046a3463c57f36bece555830` |
| Central backup ACK E | `3fba7cd91f84b4687cf6356f87400056ca32e37e` |

[Draft PR94](https://github.com/cosmosapjw-quantum/BASS_HE/pull/94)는 merge/activation 없이 Science S를 게시한다.
[고정 science 결과](https://github.com/cosmosapjw-quantum/BASS_HE/blob/d8bae9f7e24ad3494e399f7ab46c4167a5623d48/research/he_ang_ddcs20_window_20261024/RESULTS_KO.md),
[최신 중앙 handoff의 고정 E](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/3fba7cd91f84b4687cf6356f87400056ca32e37e/research/orchestration_longterm_20261023/assembly/HANDOFF_BASS_HE_KO.md),
[고정 중앙 ACK](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/3fba7cd91f84b4687cf6356f87400056ca32e37e/research/orchestration_longterm_20261023/assembly/returns/BASS_HE_HEANG_DDCS20_BACKUP_ACK_20261024.json)를 재사용한다.

B2 `HEANG_DDCS20_20261024_d8bae9f7_6cf7c537.tar.gz`는441890 bytes,
local SHA256 `bca49013628469f7d149366d651a1a004f936ad15fc1e5d74f8029ba3799223e`다.
Dropbox ID `id:BSpOijBcT10AAAAAAD_8YA`, 경로
`/BASS_DERIVATION_DOSSIERS_20260912/HEANG_DDCS20_20261024_d8bae9f7_6cf7c537.tar.gz`와
[Drive ID 1myTzgvqhm3Dfz9mUH805ASoRNnJhUW64](https://drive.google.com/file/d/1myTzgvqhm3Dfz9mUH805ASoRNnJhUW64/view?usp=drivesdk)의
metadata readback은 양쪽441890 bytes를 확인했다. 독립 remote SHA256는 제공되지 않았다.
B2는 고정 S의56file, C의3file, post-S metadata9file만 담는다.
그 archive 자체의 미래 ACK, E 또는 이후 D를 포함했다고 주장하지 않는다.

20개 stage의 과학 게시와 B2 backup은 완료됐다. 마지막 D/E의 실제 handoff/status를
담는 작은 외부 postdelivery capsule은 게시 직후 보충본이다. 자기 upload ACK를
같은 archive 내부에 넣을 수 없는 순환 관계 때문에 그 시점의 pending을 보존하며,
이미 완료된 C10의 scoped evidence/게시/backup을 다시 차단하지 않는다.

Childers et al. PRA69,022709(2004), DOI10.1103/PhysRevA.69.022709 TableIV의
E0=20 eV, E=3–6 eV, theta=15–120 degree 창이다. 전체40값 보존, 주32값 사용.
CSV SHA256 d9889cbf9f330dd195fce9ec78bf8d77f8d35e247c58e705df609efdd9cee8c4.
mu/E의 양의 hat 보간과 축대칭 가정에서 N_W=1.918935932462322e-21m²,
mean(mu)=0.5215950231699314, mean(P2)=0.1799846901344856,
mean(E)=4.581073268756349eV다. Box 범위는 deterministic sensitivity이며
통계 신뢰구간, covariance 추정, reference 오차 또는 interpolation error bound가 아니다.

## 예산과 재사용

이번 local scientific 누적 CPU1.957005s/wall2.104758352987119s, cap20/60,
3회 실행과 미사용 repair1회. ledger와 실패 보존 규칙을 초기화하지 않는다.
Wolfram은 timeConstraint10s 호출1회, 관측 toolwall13.307s, remoteCPU
UNKNOWN_NOT_ZERO다. 이전 HEANG-CONTRACT CPU0.592202/wall0.516821 및 Hex
CPU18.434312/wall18.739399, HE-X1/HE38/D10의 비용/unknown을 그대로 보존한다.
남은 예산을 다음 새 물리 노드로 전용하지 않는다.

HE-X1 science eb03981d15ad291375dd6d574a9c28809f85fc02의 이론·32fixtures·review,
HE-ANG-CONTRACT science896e5427100ad48d017deff2697b6f992ba029cd,
Hex intake science15053fe4445a32e0544d644e864fe27780d08743는 재실행하지 않는다.

## 첫 열린 의무와 DAG

HE-ANG parent는 SOURCE_INPUT_PENDING이다. 첫 열린 입력은
HE-ANG-SOURCE-PAYLOAD: 동일 source의 joint outgoing electron angular/momentum
law 또는 amplitude/event sampler와 count·spin/exchange·support·lab/COM·recoil
convention이다. 기존 NEXT_SOURCE_CONTRACT는
../he_ang_source_hex_20261024/NEXT_SOURCE_CONTRACT.json이다.
이번 finite-window DDCS marginal의 확보를 intake에 추가하고 joint 입력 의무로
연결한다. 한 표의 외부 영역이나 상대 전자를 보간·상수배로 만들어 채우지 않는다.

HE-X1 → HE-ANG, 그리고 HE-ANG/HE-EXCHANGE/HE-RESERVOIR → HE-CLOSURE →
HE-FEEDBACK의 원래 의존성을 유지한다. 전체 물리 목표의 숫자 완료율은 없다.
다른 repo의 최신 owner/hold는 evidence/survey/SURVEY.json을 참고하되
새 노드 전에 실제 HEAD와 병렬 변경을 다시 읽는다.

C9 NB-01은 미래 부분 mu_window API의 theta_degrees metadata 교정이다.
현재 고정 full-window 결과에는 영향이 없고 재실행 사유가 아니다.

## 복사 가능한 다음 지시

```text
$physmath-research-loop와 SciSpace/Wolfram으로 BASS_HE 연구를 이어가라.
고정 Science S=d8bae9f7e24ad3494e399f7ab46c4167a5623d48,
Central observation C=6cf7c53757ce4049046a3463c57f36bece555830,
Central backup ACK E=3fba7cd91f84b4687cf6356f87400056ca32e37e를 구분하라.
최신 중앙 고정 handoff는
https://github.com/cosmosapjw-quantum/rei_bianchi/blob/3fba7cd91f84b4687cf6356f87400056ca32e37e/research/orchestration_longterm_20261023/assembly/HANDOFF_BASS_HE_KO.md 이다.
Draft PR94 https://github.com/cosmosapjw-quantum/BASS_HE/pull/94 는 merge/activation하지 않았다.
먼저 위 중앙 HANDOFF_BASS_HE_KO.md와 BASS_HE의 현재 delivery 문서인
research/he_ang_ddcs20_window_20261024/HANDOFF_RESEARCH_KO.md,
delivery/PUBLICATION.json, delivery/FINAL_BACKUP_ACK.json을 읽어라.
이 문서의 delivery D는 current-file-commit이며 자기 SHA를 추정하지 마라.
실제 D와 postdelivery capsule ACK는 게시 후 별도 receipt로 확인하라.
B2=HEANG_DDCS20_20261024_d8bae9f7_6cf7c537.tar.gz,441890 bytes,
SHA256=bca49013628469f7d149366d651a1a004f936ad15fc1e5d74f8029ba3799223e,
Dropbox=id:BSpOijBcT10AAAAAAD_8YA,Drive=1myTzgvqhm3Dfz9mUH805ASoRNnJhUW64.
20stage 과학게시/두provider backup은 완료했고 B2에는 미래 E/D/자기ACK가 없다.
HE-ANG-DDCS20-WINDOW는 R1–R10/C1–C10 완료 근거와 R6/C9 검토를 재사용하라.
Childers2004 TableIV의40값/주32값, 양의mu/E보간, finite-window moments와
deterministic box extrema만 승인됐으며 전체HE-ANG은 SOURCE_INPUT_PENDING이다.
HE-X1의 이론·32fixtures·검토와 HE-ANG-CONTRACT/HE38/Hex도 다시 실행하지 마라.
다음은 HE-ANG-SOURCE-PAYLOAD의 실제 joint law/amplitude/event 입력과
count/spin/exchange/support/frame/recoil 공급자 의무다.
이 window를 전체 event sigma, recoil law 또는 X1의 경험적 각분포 보정으로 확대하지 마라.
각 새 노드 전에 AGENTS·실제HEAD·병렬변경·백업ACK를 확인하고,
모든 이전CPU/wall/실패/UNKNOWN_NOT_ZERO를 보존하라.
Astra 계약 → lower-tier 구현/실행 → 별도 Astra 검토로 R1–R10/C1–C10을 수행하라.
동결된 노드별 예산과 stopping rule을 따르고 완료된 같은 계산을 재탕하지 마라.
독립 검토 뒤 expected SHA/force=false로 draft branch에 게시하고
DAG·claim gate·단계별 게시/Dropbox/Drive ACK와 복사 가능한 다음handoff를 갱신하라.
```
