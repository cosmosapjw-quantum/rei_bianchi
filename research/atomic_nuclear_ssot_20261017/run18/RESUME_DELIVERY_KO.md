# RUN18 최종 재개 지점 — VigilODE/Rust 결과와 백업 확인

기준: 2026-10-19 UTC / 2026-10-20 KST. 이 문서는 완료된 과학 계산의 전달 기록이다.

## Git와 실제 검증된 source

- 저장소: https://github.com/cosmosapjw-quantum/rei_bianchi
- 작업 브랜치: `research/rei-run18-vigilode-c0-repair-20261020`
- RUN18 science commit: `6c0ae2a2ba63d42e23c7b79f989fa64639f4c942`
- RUN18 science tree: `5896dab499d82b53a1e76da4315b5bd28bf94983`
- 실제 직접 부모 / RUN17 delivery: `0e23addf4fefa69287d4626622bf97505677ea43`
- RUN17 science: `589ffbaff7b74a6cf1dbaf797285f15a58131dbd`
- RUN18 PR: https://github.com/cosmosapjw-quantum/rei_bianchi/pull/209
- RUN17 PR: https://github.com/cosmosapjw-quantum/rei_bianchi/pull/207

두 PR은 draft로 게시했고 merge하지 않았다. 이 문서와 `DELIVERY.json`은 위 science commit 뒤에 추가한다. 자기 commit SHA를 자기 파일에 넣지 않는다. 다음 재개 시 원격 branch ref를 조회해 실제 최신 HEAD를 선택한다.

RUN18 원격 Git의 130개 파일, 7,241,027 bytes를 실제로 다시 읽었고, canonical 원본과 SHA-256·Git blob·mode·manifest가 모두 일치했다. 부모 대비 변경은 정확히 RUN18 130개 추가이고 수정·삭제 0이다. Science manifest SHA-256은 `4362a1cc976e5075d7946aa4a1518413917d121d54705fe8cfc80e64465d1221`이다.

## 완료된 최신 과학 결과

RUN17 B의 첫 birth 구간, DOP853 23 pieces, gas5+depth252를 그대로 사용했다. Exact rational로 보면 gas 내부 값 jump는 0/110, depth는 세 경계의 431/5,544 좌표 항목이 비영이었다. 최대 개별 jump는 `2^-55`다. `J_i = 다음 piece 시작값 - 이전 정확 다항식 종단`, `c_(i+1)=c_i+J_i`, `tau_tilde_i=tau_i-c_i`인 새 재구성은 모든 22개 내부 경계에서 정확히 연속이고 23개 depth piece 모두 비음수다.

```text
Gamma = 9/288230376151711744
beta  = 9/288230376151711735
beta 표시값 = 3.122502256758253e-17
```

같은 gas·geometry, 고정된 비음수 weights의 survivor/channel에 대한 **이 표현 보정만**의 상대 변화 상한이다. 정확한 IVP, opacity feedback, 전체 sub-H 성분 또는 spectral continuum 해의 오차 상한이 아니다. 상쇄되는 net gas rate에는 상대 beta 대신 절대 channel allowance를 사용한다. 원래 8개 passive ledger는 수정하지 않았다.

실제 새 Rust crate는 `num-rational 0.4.2`, `num-bigint 0.4.6`과 원문 그대로인 VigilODE `directed.rs`를 빌드·사용했다. 실제 4 tests PASS, 독립 Python reference와 5,911개 exact cases 일치, VigilODE의 오른쪽 종단 값·도함수 각각 5,911개 exact rational 포함을 확인했다. 원래 실행 로그와 source·binary를 보존했다. RUN18의 native gas RHS·IVP·quadrature·과거 m2 재실행은 모두 0이다. 중단 후 전달 복구에서 Rust build/test도 반복하지 않았다.

VigilODE 최종 ref 확인은 2026-10-19 19:58:24–25 UTC다. source branch HEAD는 `c03ca90f19a9e64ba7751c069325a48b54b39c2e`로 진행됐지만, 재사용 원문의 17,215 bytes와 SHA `2adadb6a5d77073e0a7d3d60aedfbf37e124d15a586a880d7d5a8c8d5307a814`는 동일했다. PR71 `64b9852124b67eedbb8575b42c01127e4b86283b`, PR72 `57840c749ca51642bf828ce43f5d6273d21ea05f`는 이전과 같았다. 다른 최신 solver 파일이나 전체 benchmark를 새로 검증한 것은 아니다.

## RUN18 백업 — 실제 full GET까지 확인

```text
REI_RUN18_VIGILODE_C0_REPAIR_20261019_195758Z.zip
2,203,737 bytes
SHA-256: 4c4eee0773b5388bcb7429114934557e308d73416140269186335041ef442e15
Archive manifest SHA-256:
58803ca21b9743d5a098c9aad293651df9d370abf77691662276aed0b1ab5ecc
```

- Google Drive: https://drive.google.com/file/d/13RpLPJhTIlkDvNqwsNesBe1Gi_mBAann/view
- Dropbox: `/BASS_DERIVATION_DOSSIERS_20260912/REI_RUN18_VIGILODE_C0_REPAIR_20261019_195758Z.zip`
- Dropbox file ID: `id:BSpOijBcT10AAAAAAD_SBg`

ZIP을 새 디렉터리에 실제 복원해 134개 파일의 bytes/mode를 확인했다. 두 원격 backup에서 각각 GET 200으로 2,203,737 bytes 전체를 내려받았고 위 SHA-256, CRC, 내부 manifest, Git blob 및 mode와 일치했다. 실제 기록은 `delivery/PACKAGING_RECEIPT.json`, `delivery/LOCAL_RESTORE_RECEIPT.json`, `delivery/BACKUP_READBACK.json`이다. 백업 검증 과정에서 과학 binary를 실행하지 않았다.

ZIP에는 RUN18 source·결과·Rust adapter binary·공식 crate archive가 포함된다. 원래 gas 실행 파일과 전체 역사적 Git/toolchain을 새로 포함한 archive는 아니다. Portable hex fixture와 reference로 Rust 검증 단위를 재현할 수 있다. 정확한 명령은 `runtime/REPRODUCE.md`, 원본 reference의 재현은 `REPRODUCE_KO.md`에 있다.

## RUN17 보존과 백업

```text
REI_RUN17_FIRST_BIRTH_RESIDUAL_20261019_125500Z.zip
4,247,502 bytes
SHA-256: 2392f298e8c93aaba0bd802a14c0b34c142bf2c848fbae83d6aa80302de1f523
```

- Google Drive: https://drive.google.com/file/d/165NpTCLSTJemPQJELIwsoJbXUiYBoxQm/view
- Dropbox: `/BASS_DERIVATION_DOSSIERS_20260912/REI_RUN17_FIRST_BIRTH_RESIDUAL_20261019_125500Z.zip`
- Dropbox file ID: `id:BSpOijBcT10AAAAAAD_Q1Q`

이 ZIP도 양쪽 full GET과 116개 local restore를 실제 확인했다. Clean Git에서 RUN17 science 111개 및 delivery 추가 44개가 원본과 일치했다. 기존 raw transport에서 원본 332개 manifest 항목과 사용한 112개 source/input/evidence identity를 복원·확인했다. 전체 gas executable+toolchain의 독립 Git-only 재현은 별도 미완료 항목이다.

## 바로 이어갈 미완료 노드

원래 **P4-S4C-SPECTRAL-EDGE-SUPPORT / SUBTHRESHOLD-SURVIVOR-RESOLUTION**에서 원본 HHeD physical owner의 **continuous interval RHS extension**을 구현한다. 전체 admissible gas/depth tube에서 rate/thermal branch, photo/heating, depth RHS와 Jacobian을 포함하고 같은 invariant lift·scaling으로 coupling과 logarithmic norm을 제한해야 한다. Whole-time polynomial derivative−RHS, prefix 초기 오차, 실제 event, source spectral forcing을 각각 포함한다.

VigilODE `ContinuousResidualProvider`는 whole-box RHS와 Euclidean mu2를 요구한다. RUN17 sampled mu-infinity 또는 점별 native f64 값을 그 자리에 넣지 않는다. 저장된 degree-7 DOP853을 private RODAS5P quartic으로 재해석하지 않는다.

RUN13 m2 standard/tight 전체 완료 이력, RUN16 prefix A/B/C, RUN17 A/B, RUN18 exact adapter는 다시 실행하지 않는다. checkpoint3071은 과거 fallback provenance다. Uniform native m4는 NOT_RUN이고 spectral continuum bound는 NOT_ESTABLISHED다. 원래 45-node/26-node DAG, continuous spectral refinement, angular convergence, birth-time continuum, whole donor domain, full EoR, Einstein feedback, FLRW-CONV, BI-SIGNED, ISO-COUPLE full, Li/Be 및 nuclear T1–T8 의무를 보존한다.
