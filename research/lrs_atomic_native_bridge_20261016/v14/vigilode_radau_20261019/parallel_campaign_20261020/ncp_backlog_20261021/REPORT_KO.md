# 독립 LRS NCP backlog 실행 보고서 — 2026-10-21

## 실행 identity

- 저장소/PR: `cosmosapjw-quantum/rei_bianchi`, PR #198 (open draft)
- 이번 작업 대상 branch의 기준 전달 HEAD: `a6f13a53b45df46a68bd66e4930eb557651e662e`
- 실제 실행 snapshot/source: `d234243a79e4e8e611aaf4ac61949c5ef9111468`
- Radau 과학 source 맥락: `5248822167e3fbe374f4333f7f2efdcdbfdaeeaf`
- 보존된 VigilODE pin 맥락: `8a8bd409b1d96c7b7421f496d229e119fd3d284e`
- 실제 실행은 인증된 root agent가 `/tmp/rei_lrs_backlog_source_20261021`에 스테이징한 snapshot에서 수행했다. stage의 source 1,537개 모두 d234 commit 내용과 일치했다. 최종 metadata commit a6와의 차이는 후속 metadata/publication 파일이며 실행 source로 소급하지 않는다.
- 이전 checkout은 branch `research/flrw-production-integration-20261015`, HEAD `fef2baf960f57f37b838004fbb8a7d37b3824852`였다. 시작/종료 dirty 상태는 34,725 entries, SHA256 `866f2800ef7f011cfeb66cf0daad27c8518e70e3d114849ea226fab0b6d446e9`, tracked dirty 0으로 동일하다. 현재 checkout을 변경하지 않았다.

## Host, 자원, 명령

- Host `s1a0e5abed09`, Ubuntu 24.04.1 LTS, x86_64 Linux 6.8.0-124-generic
- `rustc 1.99.0 (b940084d7 2026-09-28)`, `cargo 1.99.0 (5f94df478 2026-08-27)`; `/root/.cargo` offline cache를 사용했다.
- affinity CPU 0–63, cgroup 조상 cpu/memory limit은 관측상 unlimited, 당시 MemAvailable 약 131.4 GB. 20% reserve 뒤 사용 가능 메모리 105,154,091,417 bytes, 64 worker admission. 각 build 1 GiB nominal, native 512 MiB/slot, thread 1. Nominal reservation은 측정 RSS가 아니다.
- 요청 및 실행 명령은 다음과 같다. 단 한 번 실행했고, exit 1 / `INCOMPLETE_OR_FAILED`, phase wall 105.042322 s였다.

```sh
env -u CARGO_TARGET_DIR python3 research/lrs_atomic_native_bridge_20261016/v14/vigilode_radau_20261019/parallel_campaign_20261020/campaign_cli.py all --input-root research/lrs_atomic_native_bridge_20261016 --work-root /tmp/rei_lrs_parallel_20261020 --cargo cargo --build-jobs 64 --max-workers 64 --nominal-job-memory-mb 512
```

실제 cwd `/tmp/rei_lrs_backlog_source_20261021`, PATH prefix `/root/.cargo/bin`, CARGO_HOME `/root/.cargo`. 이 historical V12/V13/SSPRK crate들은 VigilODE를 링크하지 않는다. 따라서 VigilODE pin은 해당 binary의 dependency라고 주장하지 않는다.

## DAG와 결과

정확한 246개 job 중 144 완료, 100 V12 native가 원래 aggregate cap 때문에 미실행, V12 merge와 saved-reference analysis 2개가 dependency-blocked다. Prepare 3, build+targeted test 6, native 131, merge/analysis 4가 완료됐다. Native 신규 실행은 V12 44/144, V13 84/84, SSPRK 원래 3명령 3/3; native 실패 0, 완료 재사용 0이다. 전체 완료로 표현하지 않는다.

V12의 44개 raw history는 각 exit 0이다. supervisor charged process wall 200.39897231891518 s로 계약 180 s cap을 20.39897231891518 s 초과했다. raw history final elapsed의 합은 4.538247207 s다. scheduler는 process를 wait/reap한 시점까지 wall을 charge하고 launch/binding/flush 작업 중에는 이미 끝난 child를 polling하지 않을 수 있다. 따라서 이는 관측된 supervisor accounting/cap 제한이며 solver 실패 증거가 아니다. 반대로 raw 내부 elapsed로 charge를 소급 대체하거나 cap을 재설정할 근거도 아니다. V12 전체 coverage, merge, saved SciPy reference 연결 분석 및 admission은 HOLD다. reference IVP 3개를 재적분하지 않았다.

V13은 각 X에서 42 histories, 3,528 rows, 31 columns, cells 32 및 선언한 tolerance 1e-15로 exact merge했다. 원본 step/row coverage와 constituent raw rows를 검증했고 기존 stdlib analyzer를 수행했다. 최대 energy residual은 X=1e-5에서 3.4638958368304884e-14 eV/H, X=1e-4에서 4.884981308350689e-15 eV/H다. 분석 상태는 `FINITE_SOURCEON_EXPERIMENT_SCOPED`; continuum source-on reference `NOT_RUN`, global source-on second order `HOLD`다.

SSPRK의 원래 transport/fixed/birth 명령 세 개는 모두 완료했다. transport는 52 unique rows; coupled는 16 histories / 2,488 macro / 6,456 segments / 3,968 births / 2,048 cells다. Alias와 raw SHA, coverage, zero shape errors, disabled nonzero births, negative cells, strict cone violations 0을 검증했다. 독립 reviewer가 Decimal60으로 `e=x+Y(y+2z)`와 full-energy maximum을 재평가해 저장 audit와 일치했다: 2.8500357805459846e-17 및 2.9234139193974344e-14. 이는 이 finite/mechanical scope의 증거이며 과학적/production admission이 아니다.

기존 완료된 current-source NCP19, borrowed fixed-N2, original V14 NCP84, local native23, process21 tests, build64 targeted test는 재실행하지 않았다. 새 과학 모델 수 0. Source, physics, tolerances, finite caps, concurrency, thread limit 변경 없음. 추가 retry 없음.

## 독립 리뷰 및 판정

구현/실행에 참여하지 않은 fresh Astra-tier reviewer가 전체 raw tree, 1,537 source files, attempts, binaries, merge/analysis/audit를 read-only 검토했다. 판정은 `PASS_SCOPED_FACTUAL_PUBLICATION`; 전체 backlog 및 과학적 수용은 `HOLD`. analyzer의 기존 “sandbox, not NCP” 문자열과 SSPRK historical reviewer/no-new-NCP 문자열은 원래 도구의 고정 historical labels다. 원본을 보존하고 현재 실행 provenance로 재사용하지 않는다.

허용되는 주장은 이번 authenticated host 실행과 관측한 V12 부분 raw, V13 exact finite coverage/diagnostics, SSPRK finite mechanical audit다. 전체 backlog 완료, V12 reference 검증, NCP64 scaling, solver speedup, peak RSS 개선은 입증하지 않는다. 일반 source-on 차수/stiff/positivity, Case B/full EoR/signed Bianchi, 넓은 CMB/boundary/global certificate, 완전 photon ledger는 HOLD; production `NOT_ISSUED`.

## Evidence

- 원격/로컬 실행 archive: `NCP_BACKLOG_EVIDENCE_20261021.tar.gz`, 79,452,611 bytes, SHA256 `85c0469ba8449bf71c277c99ebe0ae698fad5d41ec832f8e82df0c95e8bd4cdc`.
- 추출 evidence manifest: 3,052 files, `EVIDENCE_FILES_MANIFEST.json`, SHA256 `a36cfb7f1324fcb9d18a58c3bda0f13866c8ba0656b3a53eb9ad7c6c2f61ded6`.
- Archive에는 host preflight/postrun, source snapshot/archive, full input/argv/stdout/stderr/exit/outcome/raw/sidecar, targets/binaries, exact merges, analysis가 보존돼 있다. 별도 V12 charge diagnostic과 reviewer/root publication decision은 companion ACK/archive에 포함한다.
