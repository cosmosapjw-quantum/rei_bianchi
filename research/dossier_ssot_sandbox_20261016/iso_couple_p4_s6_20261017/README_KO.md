# rei_bianchi ISO-COUPLE P4/S6: 광자를 버리지 않는 reflection trace 재사용

2026-10-17. Parent PR187 HEAD `cb748a3983007f69cfaf95b2f137ff64d400b9c5`. Original production PR150 owner `da4bd0b9d112cadb2ec78c49d7dc3e7ab4761ea7`. 기존 branch, production, owner source 및 checkpoint 변경 없음. 이 directory만 add-only로 게시하며 merge하지 않는다.

## 실제 구현

`rei_iso_couple_p4_s6/src/reflection_pool.rs`는 non-tilted, energy-only homogeneous absorption과 prescribed diagonal axisymmetric Bianchi-I에서 방향 부호 반전으로 동일해지는 scalar ray/slab 계산을 재사용한다. 동일 birth time, geometry, energy, photon weight, 방향 성분 절댓값을 정확한 f64 bits로 식별한다. Cache lifetime은 한 gas-midpoint transaction뿐이다.

광자를 제거하거나 합치지 않는다. 원래 cohort 수, 방향, 출생시각, 스펙트럼 index, weight를 모두 보존한다. 각 slab의 종별 사건수와 열/에너지/work 기여를 원래 순서대로 재생해 부동소수점 합산 순서도 유지한다. 기본 workspace는 256 trace/8192 slab이며 FIFO로 오래된 항목만 제거한다. Cache가 비활성 또는 부족하면 재계산하며 물리적 수락 조건은 바뀌지 않는다.

## 실행 결과

- Rust 1.94.1, offline locked: **112/112 tests PASS** (inherited100+new12); strict all-target Clippy PASS; changed-files-only rustfmt PASS.
- 12 original physical owner와 lib export 외 inherited crate51개 파일 SHA256 동일.
- 10조건 x3회 = **30 paired runs /60 native histories /540 paired time steps**. 모든 AgeStep, gas state, photon cohort, source inventory, event budget 필드를 bit 단위로 비교해 일치했다. HeII 사건수 역시 동일하다.
- 표준 source quadrature의 비영 ray trace **50% 재사용**, 제거한 비영 photon=0, 병합한 phase-space record=0.
- 같은 샌드박스, 단일 worker, 3회 교대 순서, advance만 timing: median speedup photo-low N32=1.4495, full FLRW N16=1.3888, full BI+ N32=1.4573, D-edge split GL4/op8 N8=1.6376, photo-thick N12=1.2941. 범용 가속률이 아니라 이 입력과 이 host에서의 측정이다.
- max photon ledger relative=1.4194339755428995e-14; max total energy ledger relative=4.629026161535518e-16.
- 독립 Python closed-form ray96점: energy relative 및 direction absolute max=2.220446049250313e-16.
- 새 디렉터리에서 복원/build/tests/Clippy 및 scientific CSV 재생 일치. 일괄 호출은 tests/lint/build 성공 뒤4/30행에서 중단되어 보존했고, fresh executable로 미완료 campaign/ray만 재실행해30/30행을 완성했다. 하나의 uninterrupted runtime으로 보고하지 않는다.

P5 `p5_tail_campaign.rs`는 collisions/CX/CMB가 OFF인 photo-only 실험이었다. 그 HeII pruning 반례는 이 범위로 보존한다. P6에서는 photo-only와 full thermochemistry ON을 별도 실행하고 ON의 RR/CX/freefree/CMB budget이 실제 비영인지 검사한다. ON도 제조된 D defect0.0037eV, CMB bath20K 및 off-shell geometry이므로 관측적 EoR 초기조건이 아니다.

## 적용 범위와 다음 DAG

**PASS_SCOPED_DISCRETE_REFLECTION_TRACE_REUSE**. Full P4 PARTIAL; SA01/02, FLRW-CONV, BI-SIGNED, FULL_EOR HOLD. 원래 midpoint gas freezing/Lie split, spectral/angle discretization error는 그대로다. O(Ntime^2) source-age complexity와 cohort storage를 해결한 것이 아니다. Tilt, anisotropic scattering/polarization, spatial inhomogeneity, nondiagonal geometry에는 이 cache를 적용하지 않는다. Adjoint truncation certification도 수행했다고 주장하지 않는다.

P4/S7에서는 이 정확한 재사용 경로를 기준으로 actual source-matched BASS intake 또는 분리된 time/age/spectrum/angle convergence 중 다음 bounded unit을 선택한다. 매 턴 GitHub, Google Drive, Dropbox backup을 실행하고 upload ACK, content identity, raw restore를 별도 기록한다.

## 재현: 이 GitHub directory만으로 실행 가능

Cargo.toml/lock, 모든57개 Rust 파일을 포함한다. Cargo 외부 dependency 없음. compiler bundle은 포함하지 않는다.

```bash
export RUST_1_94_1_PREFIX=/mnt/data/rust-1.94.1-prefix
export PATH="$RUST_1_94_1_PREFIX/bin:$PATH"
export LD_LIBRARY_PATH="$RUST_1_94_1_PREFIX/lib:${LD_LIBRARY_PATH:-}"
export CARGO_BUILD_JOBS=1
cd rei_iso_couple_p4_s6
cargo test --offline --locked --all-targets
cargo clippy --offline --locked --all-targets -- -D warnings
cargo build --offline --locked --release --example p6_matched --example p6_ray_witness
mkdir -p ../replay
target/release/examples/p6_matched all > ../replay/p6_matched.csv
target/release/examples/p6_ray_witness > ../replay/p6_ray_witness.csv
cd ..
python scripts/validate_p6.py replay
```

全57-file crate Git tree SHA `d0532b4bd495f30404becbccb895b354bf513faa`는 실제 검증한 sandbox crate의 `git write-tree`와 동일하다. Git blob identity와 source ZIP SHA256은 별개다.

## 전체 증거와 백업

FULL ZIP: 214626bytes,103members,102 payload SHA256. SHA256 `99eba3f035fbc08adc2fe6135d120a461d2579bc832fb2878d1a6a249f025c62`.
Google Drive: https://drive.google.com/file/d/1DbRrl6UmIYCwtwaUl7kLwRnjlOUfr506/view ; raw file 재다운로드 SHA256 일치.
Dropbox: `/bianchi/rei_bianchi/research/REI_BASS_HIERARCHY_BACKUPS/REI_ISO_COUPLE_P4_S6_20261017_FULL.zip`, id `id:BSpOijBcT10AAAAAAD-nWw`; upload completed,214626bytes, server content_hash `7827930d2478da1329dc4533791074787ff302c38b4b3ecb57936c7412cbc0ee`와 로컬 Dropbox algorithm hash 일치. Raw readback은 sandbox DNS failure로 미완료이며 full restore verified로 부르지 않는다.

FULL ZIP에는 전체 theory, source contracts, 실제 CSV, test/lint/build/failure/restore logs가 들어 있다. 본 GitHub stage에는 complete native crate, compact measurements, direct proof 및 재현 validator를 개별 파일로 게시한다.
