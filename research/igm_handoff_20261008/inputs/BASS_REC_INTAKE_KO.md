# BASS·REC 후속 IGM intake — 2026-10-08

최신 원격 branch/PR/commit와 실제 계약·source 파일을 읽었다. 이 intake는 수치 시험 재실행이 아니다. 정확한 조회 내용과 source 사본은 `REMOTE_SNAPSHOT.json`, `sources/`에 있다.

| lane | 현재 공개 head | 실제 판정 |
|---|---|---|
| BASS PR132 / forward | `e57064934bb176b08d2072aa537e5f71a430ae5e` | 10월 7일 SYNC03 문서 반환만 추가. native 소비 source pin `1e45e0f48cd83dcb21c23d4087fa5526195331d7` 유지 |
| BASS PR133 / gain research | `548c9f71304d4dd0b6df3565e2d25229429f64d3` | 10월 7일 SYNC03 문서 반환만 추가. source pin `1c5db6ddc32c16cacf4ef548f0f6839415ee950a` 유지 |
| REC PR81 / forward | `d74fc9e78d1cf707eef2d16fe771b4d8eb72cd7f` | 10월 7일 SYNC03 문서 반환만 추가. parent/source `73ed56b2383e21014fcb70cd8f87f1d010731c60` 유지 |

BASS는 214개 branch를 3 page로, REC는 전체 branch를 마지막 빈 page까지 확인했다. 확인 시점에 SYNC03 이후의 새 BASS/REC science commit은 이 두 repo에서 관찰되지 않았다. 두 repo가 사용자가 말한 “다른 네 스레드”의 어느 채팅을 뜻하는지는 GitHub만으로 확정하지 않는다. repo publication과 실제 ChatGPT recipient ACK는 다르다.

REC PR81 맨 위 Task8 설명은 낡았다. **현재 파일** `FORWARD_STATUS.json`은 V11/F1 repaired/reviewed이며 source/tested `d3cc6e0120061f113d28e7a3a55a2e3dd561e81e`에서 fmt, Rust 76/76, Python 251 records/3027 components/111 expected errors PASS를 기록한다. Gate P도 scoped fixed-input review PASS다. 그러나 Gate I는 여전히 DEFERRED_CONSUMER이며 consumer integration 허용은 false다. 따라서 “REC source import 자체가 아직 미실행”을 blocker로 재등록하면 안 된다.

REC-PB02의 순수 H, one-temperature Peebles pointwise reference 및 SYNC02 실제 REC→REI benchmark는 재사용 가능한 완료 자산이다. late-IGM의 two-temperature/source-driven chemistry로 자동 전환되지 않으며 He/E1C gate와 구별한다.

BASS의 실제 F08 소비는 이미 SYNC03에서 여섯 이력 112,000셀과 Decimal70 784,054 scalar 비교를 기록했다. 조건부 endpoint-linear Δτ 부호의 의미를 보존한다. full BASS build, 실제 EoR/observer-tail, continuum sign의 판정으로 확장하지 않는다. PR133의 gain은 frozen-frame·zero-tilt opt-in primitive이고 큰 exposure에서 G(G(f))로 간다. IGM cutoff/gas owner의 대체물이 아니다.

이번 IGM 연결에서 가장 작고 겹치지 않는 작업은 **실제 accepted short IGM state의 read-only export → 기존 BASS visibility**다. 반드시 proper `n_e[cm^-3]`에 `1e6`을 한 번 적용하고, `q=cσ_T n_e D`에 D도 한 번 적용한다. 이미 proper인 density에 a^-3를 다시 곱하지 않는다. normal-time edges, species denominator, endpoint/whole-cell reconstruction과 caller-owned observer tail을 같이 보내야 한다. z만으로 time을 추측하지 않는다.

source endpoint boxes가 주어질 경우 declared endpoint-linear density의 positive weighted sum으로 τ bounds를 전달하고, survival은 exp(-τ)의 단조성으로 변환할 수 있다. common tail b는 τ+b 및 mass·survival의 exp(-b) 배율이다. 이는 reconstruction 아래의 conditional observable 연구로 가능하며 continuous/physical certification과 별도다.

병렬 REC 작업은 late-IGM initial handoff의 epoch·proper nuclear/electron density·species fraction·Tgas/Trad·clock/frame 소유권을 schema로 고정하는 것이다. 실제 matched history 또는 radiation payload가 없으면 명시적으로 NOT_PROVIDED로 둔다. 이미 끝난 Peebles/clock/F08 수신 캠페인을 다시 수행하지 않는다.

상세 DAG 입력·reserved owner·금지 추론·수신 계약은 `INTAKE.json`에 있다. source/header 기준을 확인했으며 이 intake에서 외부 저장소나 PR는 수정하지 않았다.
