# rei_bianchi P4/S8: 중단 복구와 gas/photo 공동 시간중심화

2026-10-17. 이번 source lineage는 원격 P6 PR188 HEAD `9f9837c0587e616ec351980fdbaab6dea799d027`와 원래 전달한 P7 archive SHA256 `c8303179c468431638a6a09eb43e73b6acf34ef7e913611445ba254de1736712`다. P7은 당시 원격 게시되지 않았으므로 이미 게시된 PR로 가장하지 않는다. 원래 production PR150 `da4bd0b9d112cadb2ec78c49d7dc3e7ab4761ea7` 및 P6 branch는 그대로 유지한다. 이 directory만 add-only로 게시한다.

## 구현과 선택

기존 full_network의 gas Euler + CX Lie 순서가 남기는 시간오차를 분리했다. 추가 `midpoint_gas.rs`는 원 CI/RR/CE/freefree/CMB source 식을 동일 중간상태에서 평가하며, `midpoint_coupled.rs`는 예측한 gas midpoint를 opacity 및 non-photo 반응에 공통으로 쓴다. 예측 단계의 photon/source/energy ledger는 폐기한다. 보정 단계만 source를 한번 반영한다.

비교 모드는 Legacy, OpacityOnly, GasOnly, Joint, JointCxSplit이다. 선택한 JointCxSplit은 원래 adaptive thermal CX의 half-step을 앞뒤에 보존하고, 가운데 photo/non-CX 단계를 공동 midpoint로 평가한다. 단순 Euler subsolver에 Strang 순서만 붙인 것이 아니다. raw explicit CX-midpoint가 거친 timestep에서 나빠지는 반례도 보존했다. 원 physical owner12개와 P7 파일은 lib export 이외 바뀌지 않았다. 별도 copy의 opt-in 모듈이다.

## 실제 완료한 검증

- Rust1.94.1 release/offline/locked all-target **132 tests PASS**, Python 분석6개 PASS, strict Clippy -Dwarnings 및 new-source rustfmt PASS.
- Coupled native33행,1152macrosteps + gas-only70행 + 독립 DOP853 time integrator4회. DOP853은 native RHS를 사용한다. 원자율까지 독립 구현한 검증은 아니다.
- 같은 spectral/angle/source 설정의 N32/64/128에서 DI 누적 photo-event observed order는 legacy1.0176573076에서 JointCxSplit2.0078550620으로 개선된다. HI/HeII 차수는 각각1.26287/1.74444이며 일부 차분 부호가 바뀌므로 전체 관측량2차를 승인하지 않는다.
- OpacityOnly는 DI를 개선하지만 온도는 약1차다. GasOnly는 온도를 개선하지만 DI는 약1차다. 공동 centering 필요성을 실제 비교했다.
- T0=40000K gas-only에서 DOP853 대비 N32 온도 절대오차: legacy_tight0.2608829524K, CX-preserving midpoint0.0001118520K. N128에서는0.0651795629K와0.00000698570K다.
- T0=10000K,N8 gas-only의 DII 절대오차는 raw all-CX midpoint0.0147261m^-3으로 기존보다 나빠졌다. 원 CX flow 보존 후4.5669e-9m^-3으로 감소했다. 이 결과를 지우지 않고 후보 선택 근거로 남겼다. 미세 격자 DII 오차바닥의 원인은 아직 분리하지 않았다.
- Native photon inventory 최대9.7944546605e-15, total-energy ledger8.1007969656e-16. Gas energy ledger1.1760511261e-15.
- 새 디렉터리 복원에서132tests/6analysis/build/lint 통과. Native대표3행의 scientific fields 동일, gas70행 bytes 동일, DOP8534회 reference JSON 동일. Native33행 전체를 재실행했다고 주장하지 않는다.

## 가정과 남은 범위

Metric(-,+,+,+), proper time[s], photon energy[eV], gas density[m^-3], energy ledger[J/reference-comoving m^3]. 원 MD14/BB50k 광원, H-equality D opacity와 manufactured D defect0.0037eV, test CMB bath20K 및 constant prescribed Bianchi-I를 유지했다. Tight native CX tolerance를 적용한 campaign임을 개별 입력에 기록했다. BASS on-shell 기하/관측적 EoR IC가 아니다.

명시적 midpoint는 무조건 양성 또는 stiff 안정성을 보장하지 않는다. 실패 상태는 clip하지 않고 reject한다. Smooth regime 및 정확한 midpoint predictor, 충분히 정확한 CX flow 조건에서2차 consistency를 유도했으나, 전체 photon angular/spectral discretization과 rare-channel global error는 별도다. FullP4 PARTIAL; SA01/02, FLRW-CONV, BI-SIGNED, FULL_EOR HOLD. NextP4/S9는 timestep error-control, rare-channel 및 innerCX error 분리다.

## GitHub source backup 표현과 복원

Github에는 67개 native 파일을 **고정 P6 source57개 + exact source delta11개**로 보존한다. 압축은 source 전달 형식일 뿐 photon compression이 아니다. 세 part의 SHA와 decoded source manifest를 검증한 후 새 디렉터리로만 복원한다. 이 delta에는 P7 추가 경로도 포함돼 누락된 remote source lineage를 메운다. 원본 P6 files는 수정하지 않는다. 로컬에서 이 스크립트를 실제 실행하여 전체67file SHA256 일치를 확인했다.

Repository checkout root에서 실행:

```bash
ROOT=research/dossier_ssot_sandbox_20261016
STAGE=$ROOT/iso_couple_p4_s8_recovery_20261017
BASE=$ROOT/iso_couple_p4_s6_20261017/rei_iso_couple_p4_s6
python "$STAGE/RESTORE_SOURCE.py" --base "$BASE" --out /tmp/rei_p8_restored
# Rust1.94.1 환경을 설정한 다음:
cd /tmp/rei_p8_restored
cargo test --offline --locked --release --all-targets
cargo clippy --offline --locked --all-targets -- -D warnings
```

Full source/evidence ZIP은576887bytes,183entries,182payload hashes다. SHA256 `63618bb44cea7832273cefe3cd07053a3272d0b664a7efc797a100897f680a45`. 이 ZIP에는 이전 원본 P7 ZIP도 그대로 포함했다. 전체 CSV/logs/research report는 이 ZIP에 있고, GitHub에는 source reconstruction와 compact scientific evidence를 보존한다.

Google Drive FULL: https://drive.google.com/file/d/1cQxLE4cC_xu8tj88iQLm5FkNAlMQBXY9/view
Dropbox FULL: `/bianchi/rei_bianchi/research/REI_BASS_HIERARCHY_BACKUPS/REI_ISO_COUPLE_P4_S8_20261017_FULL.zip`.
업로드와 raw readback 검증 수준은 별도 PUBLICATION_RECEIPT.json에 기록한다.

Mackey2012 A&A539,A147 DOI10.1051/0004-6361/201117984는 time-centred opacity의 비교 배경이다. 이 논문의 결과를 새 gas algorithm의 검증으로 대신 사용하지 않았다. 원 식/원 코드, 직접 행렬 유도, Wolfram algebra check, 독립 time integrator, 실제 native convergence를 구분한다.
