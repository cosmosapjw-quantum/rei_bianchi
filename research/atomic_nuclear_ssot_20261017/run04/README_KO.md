# RUN04: source-only BASS 기하와 동적 H/He/D 열화학 연결

2026-10-17. DAG P4-S4B-ON_SHELL의 제한된 실행 결과. 샌드박스에서만 실행했으며 Codex/local/NCP/SSH 사용, production owner 변경, main merge는 하지 않았다. PR185 parent d239fc2e5e9402801f3cca2523425a9ddf2a1504 위의 add-only 연구 기록이다.

## 물리와 새 코드

실제 BASS164/165 source-only Einstein–Vlasov CSV의 Hermite b(X), log H(X), GL8 proper-time 변환을 Rust로 연결했다. H>0 및 구간 전체 -1/2<db/dX<1이면 모든 축이 팽창하고 광자 에너지가 단조 감소하므로 각 문턱을 최대 한 번 교차한다. b_X는 이차식이므로 끝점과 내부 stationary point를 검사한다. 이는 부동소수점 여유를 포함한 수치 guard이며 outward-rounded interval certificate는 아니다.

새 bass_geometry.rs, bass_source_bridge.rs, bass_retarded.rs는 기존 MD14/BB50k source, Verner, Grackle Case-A CI/RR/DR/CE, Savin CX, DAtomicProvider 및 native mixture EOS를 재사용한다. photon event는 한 번만 적용하고 gas-only thermal transaction에는 use_photo=false를 준다. CMB bath는 명시적으로 2.7255/a K이다. 원본 owner 12개와 49개 retained Rust 파일의 byte identity를 보존했다.

실제 계산은 X=0.7..0.7004의 짧은 구간이다. 초기 T=10000 K, HII=DII=0.1, He charge fractions=(0.8,0.15,0.05), D/H=2.5e-5는 외부 제조 initial-state prescription이며 REC donor 채택이 아니다. D binding defect 0.0037 eV도 기존 제조값이다. Gas는 동적이지만 공급받은 기하는 새 gas/photon stress로 다시 풀지 않는다. 따라서 self-consistent Einstein–reaction–radiation solution, 정밀 isotope history 또는 full EoR 주장은 하지 않는다.

## 실행된 검증과 미통과 수렴

- Rust 1.94.1 offline all-target tests 108/108 PASS: inherited 99 + geometry 6 + coupling 3. Strict Clippy와 new-code-only rustfmt PASS. 원본 실패/수정 logs 보존. Native independent subagent NOT_RUN.
- 원본 Python receiver와 독립 구현 비교 128점: max H relative 1.4211e-14, clock relative 4.5853e-15, b absolute 8.6736e-19.
- 실제 source-native dynamic H/He/D campaign 22행 완료. Max photon residual 2.4828e-15, baryon residual 1.3323e-15, step augmented-energy residual 5.5514e-16.
- SIGNED_MINUS N16→32: T 상대 차이 7.6934e-7이지만 survivor 차이 18.2008% (N32 denominator). N8/slices8에서 birth GL2→GL4 survivor 차이 47.1825% (GL4 denominator). 보존 잔차나 온도 일치가 광자 정확도를 증명하지 않는다.
- 같은 N8에서 donor121→241 survivor 차이는 최대 1.1125e-11. 이 짧은 문제의 큰 birth/time 오차를 donor-grid 오차로 돌릴 근거는 없다.
- 새 디렉터리에서 payload manifest, 108 tests, strict Clippy, 128-point Python comparison과 대표 SIGNED_MINUS N2를 재실행했다. 두 CSV는 byte-identical. 전체 22 campaign을 다시 실행했다고 주장하지 않는다.

판정: PASS_SCOPED_SOURCE_ONLY_BASS_GEOMETRY_DYNAMIC_HHED_COUPLING. Global birth/time convergence, FLRW-CONV, BI-SIGNED, ISO-COUPLE full, FULL_EOR 및 미완료 원자/핵물리 T1–T8은 HOLD. 다음 노드는 P4-S4C-BIRTH-OPTICAL-LAYER이며 동일 source/cosmology/IC에서 optical-boundary-layer-aware birth 적분을 구성한다.

## 소스와 복원

이 디렉터리의 REI_RUN04_SOURCE_DELTA.tar.xz는 실제 새 Rust 소스, 테스트, 실행기, 22행 CSV, 수치 결과, 출처 및 다음 DAG를 담은 source/evidence delta이다. 단독 full checkout은 아니다.

Delta SHA256: fe6aa8db7f63e396e538f4c94c2e5122e169e95fd23ed397ed5b193334a8b93b
Delta Git blob SHA1: e635c7b1bb9e6694b76975f81cf509790c65b8d5

전체 복원 ZIP: REI_ATOMIC_NUCLEAR_RUN04_BASS_COUPLED_20261017.zip (1174295 bytes, 157 entries, 156 payload hashes)
SHA256: fc9f56e0febd51097429fcbed24a19bd58032137e8ebb66963bdadc523c09b13

Google Drive: https://drive.google.com/file/d/1Do_D_J7FAKj3jYI9iAn7q7UvKUvL7yN8/view?usp=drivesdk
Drive upload 완료 및 authenticated full download SHA256 일치 확인.
Dropbox: /BASS_DERIVATION_DOSSIERS_20260912/REI_ATOMIC_NUCLEAR_RUN04_BASS_COUPLED_20261017.zip
Dropbox object id: id:BSpOijBcT10AAAAAAD-nWg. Upload 완료, provider content_hash 9666faf5a88faa2b86ad1220c45959c8002e9b22254fb70f5acfbeee6056aaf5가 local Dropbox hash와 일치. 독립 Dropbox byte download는 NOT_RUN.

전체 ZIP을 새 폴더에 풀고 scripts/REPLAY_OFFLINE.sh를 실행한다. Rust toolchain은 별도 입력이며 archive에 포함하지 않았다. 메모리 상한 4GiB, build job 1. 이후 이 스레드의 연구 턴마다 GitHub source delivery와 Drive/Dropbox full backup을 실제 수행하고 업로드·checksum·download·restore 상태를 구분한다.
