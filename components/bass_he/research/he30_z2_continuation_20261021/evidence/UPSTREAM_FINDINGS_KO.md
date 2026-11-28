# 최신 upstream 조사 — 2026-10-21

## 최종 판단 갱신: z2 원자료 237건이 이미 존재한다

GitHub 조사 후 병렬 백업 조사에서 `REI_UNIFIED_D3_EXECUTION_20261021_20261021T104524Z.tar.gz` 실제 archive를 회수했다. 백업 조사 담당자의 실제 CHECK/STATUS 및 raw 검사는 z2 tail 237/237 완료, `PASS_SCOPED_PRELIMINARY`, 독립 결과 심사 pending을 확인했다. 구성은 B1 grid175 + original91 − overlap35 + guard6 =237이다. 따라서 아래 GitHub 게시 pilot의 z4 범위와 최신 백업 D3의 z2 완료 범위를 구별한다. **오늘의 권장 작업은 D3 완료237의 identity/정규화/endpoint를 확인하고 재사용하여 plots를 만드는 것이다. 새 IVP/continuation을 실행할 필요가 없다.**

- 회수 archive: `/workspace/scratch/39bb8df06b79/investigation/backup/recovered/REI_UNIFIED_D3_EXECUTION_20261021_20261021T104524Z.tar.gz`
- Dropbox: `id:BSpOijBcT10AAAAAAD_gNA`; 31,904,176 bytes; provider timestamp 2026-10-21 10:46:59 UTC.
- Drive: `1_noyMOexSIBbHdWIqkoGsvt3nBxwGZGi`.
- 이 upstream 조사 담당자는 D3 과학 실행을 하지 않았다. 원자료 세부 검사는 병렬 backup 조사 결과이며, 부모 작업의 catalog/manifest에서 다시 묶는다.

## 확인 범위
다섯 저장소의 접근 가능한 branch ref를 pagination 끝까지 열거했다. BASS_HE87, rei_bianchi255, bass262, bass_cr168, vigilode185, 합계957개다. 각 저장소의 최근 updated순12 PR을 GitHub REST로 읽고, 검색 도구의 최근12 PR도 보존했다. 선택한 관련 보고서·DAG·인계·배송 파일15개는 pinned commit의 raw 내용을 로컬에 보존했다. 모든 branch의 모든 파일 또는 모든 비공개 대화를 읽었다는 의미는 아니다.

- `GITHUB_INVENTORY.json`: 전체 branch ref와 검색 결과 PR.
- `LATEST_PRS_SORTED_UPDATED.json`: 실제 REST updated순 PR; PR198/199 최신 본문까지 포함.
- `SOURCE_MANIFEST.json`: 읽은15개 원문 위치, bytes, SHA256, Git blob SHA1.
- `sources/`: 원문 bytes. 과학 실행/벤치마크0, 기존 저장소 변경0.

## 현재 pilot들의 서로 다른 범위

| 공급 경로 | 현재 게시 head | 확보 범위 |
|---|---|---|
| BASS_HE PR82 |048a73de4246f609b1bc14854ea5c48757cb82fd|Canonical28 + independent matter12 =고유40 보고. 독립18 view는 재사용6+새12. z20→4. 현재 recovery 상태는 raw original27, split0 보존, missing13 복구 필요.|
| BASS PR176 |26f4a89a54462c4e7c5705f281f187f33f45166a|Warm C15 split729,243groups,47385행. a=.1999→.2이며 z20→2 결과가 아니다.|
| REI PR213 |d32cd99fa19c65aa1ca63dbc8aab8741834270e8|BASS split729의 REI 게시. 원 결과 commit c8e9f67aa031ffb33a9b0347bdea61dbb01fb746.|
| BASS/REI ACCEL01 PR177/214 |4f19e6eaf50e8458d59d27ff47f03e9d8c8b22ca / 98fcf3943fa54e089b0292d166c3a47becb5edb8|기존729재사용; exact massive moment cache/완료-case registry/공유 dispatcher. 새로운 full trajectory0.|
| bass_cr C21M PR91 |b78a943e5d7ae341bbfe84f742a06a4ac36d0e43|독립27점 z20→4, 새26+재사용1. 완전40상태 raw histories 및 builder.|
| REI PR198 component pilot |8bd35af5f11c7ea5945b656be1c013d1c1933498|z20→4 original625 +새600matter+6mixed=고유1231. 원40상태→불변부분공간8상태 reduction. No z2 evidence.|

GitHub 원문에서 확인한 관련 cold pilots는 z4까지만 도달했다. 이후 발견한 D3 백업의 z2 원자료237건이 이 초기 범위 판단을 보완한다. 초기의 z4→2 continuation 제안은 취소하고, 완료된 D3 원자료를 먼저 재사용한다.

## 재사용할 실제 구현

REI PR198 source:
- `research/rei_bianchi_sigma_pi_pilot_20261021/pilot.py` @8bd35af5, Git blob `0c90eabbb07ee80ba9ba32f855cb698b98b9680b`.
- `research/rei_bianchi_sigma_pi_pilot_20261021/matter_radiation_20261021/component_pilot.py`, Git blob `66a6501cff0e367cfe2263f2d25c24f1ec85f55c`.
- Reviewed source/results commit `b140170ce0c58159368b6b81be49ac35ca764851`.
- Fixed collisionless reflection-even LRS에서는 gamma와nu energy가 같고, odd modes=0, number/thermal state가 energy/geometry에 feedback하지 않는다. 8상태=(Href Δt,b,s/Href,E0,E2,E4,E6,E8). E'=b'ME, E=exp(bM)E_init. 기존 full/reduced6사례 검증 maxabs2.173e-11, L8/L12와 tighter-tolerance 검사 기록을 재사용할 수 있다. 실제 z2 결과에는 D3의 범위와 기존 검증 근거를 연결한다.
- Norm 차이: HE full Frobenius=(sqrt2)×REI PR198 half-contraction. 압력scalar도 C15 deltaP와 canonical pi_s=deltaP/3를 구별한다.

## 백업 상태

Split729 Stage5 receipt는18 ZIP+index,1715원본파일/423198268bytes의 실제 전체 readback 및 재조립 PASS를 기록한다. Stage6는109파일/2 ZIP exact readback PASS다. 이 조사에서는 pinned receipts를 읽었으며 백업 다운로드·과학 재실행은 하지 않았다. 각 provider ID와 해시는 sources/bass/.../delivery에 있다.

HE PR82의 DAG/DELIVERY는 과학 완료 보고와 게시중단 상태를 동시에 보존한다. RECOVERY_STATUS의 raw27+missing13이 현재 실제 재사용 판정의 입력이다. 보고서의40완료만으로 missing13을 현재 가용하다고 처리할 수 없다. 병렬 백업 조사는 missing13의 original/split 원자료가 당시 업로드되지 않았음을 확인했다. D3의 별도 완료237을 HE missing13의 복구라고 부르지 않는다.

C21M full delivery(17,539,759bytes; SHA e0592be2859b7db606ec5a2ca008015c5ab02a3b2ff09fdd97fafe209cfe167a)는 Library/Dropbox 성공 ACK, Drive noACK 기록이다. REI PR198 전체 component subtree archive(37,945,383bytes; SHA2c1433a92ae68c328436852b2842c9b7c51d30b9ff84a22fe2dffbd04ee4246d)는 Drive1i6x-HcPTctzSQwsxkET-CfTGfjpC-Dx7 / Dropbox id:BSpOijBcT10AAAAAAD_fYA에 양쪽 whole readback PASS를 기록한다.

## 최신 solver 선택에 주는 제약

VigilODE NCP120m 결과 @7a63876a97fc17f640771ec06658269947049994의 실제 보고서를 읽었다. 여러 제조 문제에서 scoped 결과가 있으나 broad production 승격은 HOLD, rotation 정확도 failure가 남고 내부1/2/4/...scaling은 NOT_RUN이다. 오늘의 이미 검증된 canonical DOP853를 새 VigilODE로 바꾸어 z2 pilot을 지연할 근거가 없다. 이 비교는 기존 보고서 해석이며 새 벤치마크가 아니다.

PR199는 최신 본문이 v11완료를 기록하지만 REST head는8b71c13e…이고 본문은964b2e3…를 현재HEAD로 표기한다. 해당 AGE lineage의 exact binding을 따로 확인하기 전 그 본문의HEAD를 branch authority로 채택하지 않는다. 이번 z2 collisionless 경로는 그 미정합에 의존하지 않는다.

## 권장 새 기여 3개

1. D3의 완료237 raw를 exact identity, 원 source 해시, 정규화 및 실제 z2 endpoint에 묶어 compact histories/catalog와 완료-only consumer를 만든다. 독립 Pi_m/Pi_r 및 signed 합·work/cancellation을 보존한다. 별도 새 적분은 하지 않는다.
2. 이미 존재하는 공유 CPU lease와 현 affinity/cgroup/memory를 이용해 pending만 배분한다. 다른세션 존재 자체는 중지 사유가 아니다. 완료 receipts와 실패 partial은 분리하며 case별 immutable identity lock을 사용한다.
3. 완료237에서 z2까지의 component time evolution 및 정확한 grid점 parameter sweep을 만들고 D3 원자료의 provenance를 표기한다. H/He가 꺼진 collisionless pilot과 warm native C15/HE29 thermochemical 증거를 한 물리모델로 합산하지 않는다.

## HE30 실행기 기여 완료

지정한 새 `shared_runner.py` 및 `tests/test_runner.py`만 구현했다. 기존 HE29의 CPU lease/resource 측정을 재사용하고 CPU55 고정 제외를 제거했다. affinity/cgroup quota/실제 CPU 활동과 가용 RAM을 읽어 새 worker를 동적으로 배분한다. 이미 사용된 메모리를 active worker 수로 다시 차감하지 않는다. 전역 case identity lock, per-CPU lock, one-thread 환경, immutable 완료 재사용, 실패/부분 결과 보존 및 자기 child만 timeout 정리를 제공한다. 기본 NCP 설정은 max64, reserveCPU2, reserveRAM16GiB이며 작은 host에서는 reserve를 조정한다.

최종 경량 검사: `python3 repos/BASS_HE/research/he30_z2_continuation_20261021/tests/test_runner.py -v` — 8개 PASS, 0.417초. 실제 fixture child3은 파일 I/O 성공2·의도적 실패1뿐이며 과학 계산0/벤치마크0이다. 다른 출력 root에서 완료 재사용2와 실패 보존1로 worker0을 확인했다. 이 시간은 성능 측정 결과가 아니라 검사 실행 기록이다.

