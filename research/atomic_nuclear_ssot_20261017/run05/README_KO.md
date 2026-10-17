# RUN05: 광학 시간척도를 반영한 양의 광자 출생 적분

2026-10-17 KST. RUN04 commit 41264bd71e400e08f89d9e4d39a5b7a53bf2f38c 다음의 P4-S4C-BIRTH-OPTICAL-LAYER 실행. 샌드박스 전용 add-only 연구이며 local/NCP/Codex/SSH, production owner 수정, main merge는 하지 않았다. Native independent subagent/reviewer actor NOT_RUN.

## 실제 물리와 적용 범위

BASS source-only Einstein–Vlasov donor와 native MD14/BB50k, Grackle/Verner/Savin, DAtomicProvider를 유지하고 동적 H/He/D의 기존 gas/photo Lie split에 새 birth quadrature를 opt-in으로 연결했다. X=ln(a/a_ref), a_ref=1/21, X=0.7..0.7004. 원래 제조 IC T=10000K, HII=DII=.1, He=(.8,.15,.05), D/H=2.5e-5 및 D defect=.0037eV 유지. REC donor 채택이 아니며, 새 gas/photon stress로 기하를 다시 풀지 않는다. CMB bath는 2.7255/a K. 원본 12 owner를 포함한 57 retained Rust 파일은 unchanged; lib.rs에는 두 module 선언만 추가했다.

## 구성적 유도와 코드

N'=j-kappa N, kappa=c sum(n_a sigma_a). 연속 출생의 생존량은 Duhamel birth integral이다. 고정 j,kappa에서 N_birth=j h Phi(tau), Phi=-expm1(-tau)/tau, tau=kappa h. 단일 고정 GL2/4는 큰 tau에서 terminal birth layer를 놓칠 수 있으며 photon conservation이 이 오류를 검출하지는 않는다.

v=(t1-tb)/h의 [0,1] 구간을 v1=min(1,1/Tseed), v_next=min(1,g*v), 1<g<=2로 분할하고 각 panel에 positive GL4를 적용한다. Tseed=0은 단일 panel. Tseed는 native optical-scale estimate이며 실제 optical depth의 exact coordinate inversion이나 전 구간 upper bound가 아니다. 모든 panel을 유지하고 photon weight 사후 normalization 또는 positive tail clipping을 하지 않는다. tau=1000,g=2는 44 birth nodes; tau=1e12는164 nodes.

고정-opacity exact arithmetic에서 panel [a,b], Delta=b-a의 GL4 오차는
0 <= Integral(exp(-tau*v))-Q4 <= Delta*(tau*Delta)^8*exp(-tau*a)/1778112000.
Wolfram monic Legendre norm coefficient 및 formula residual=0으로 확인했다. 이 상계는 가변 source/opacity/energy의 coupled trajectory에 자동 적용되지 않으며 outward-rounded floating-point certificate도 아니다.

새 birth_layers.rs, bass_optical_birth.rs와 실제 tests/examples를 code archive에 보존했다. 기존 photon_slab의 large-tau 1-(1-Phi) cancellation 취약점을 발견했으나 원본을 수정하지 않고 새 stable Phi와 독립 comparator를 분리했다. 이것이 RUN04 18% 차이의 원인이라는 주장은 하지 않는다.

## 실제 실행과 수치 결과

- Rust1.94.1 offline all-target 118/118 PASS: retained108 + new kernel6 + new coupled4. Strict Clippy, new-code rustfmt PASS. Main kernel와 cancellation test는 실제 red/green 기록이 있으며 모든 신규 테스트를 TDD로 썼다고 주장하지 않는다.
- MP70 constant-opacity 165 rows, optical seed0..1e12. Uniform2/4 최대 survivor relative error1; graded g2=1.120622292488e-6, g1.5=1.6386341915e-8, g1.25=5.42965550812853e-10. 명시한 roundoff allowance 내 remainder-bound violations0. Finite sampled evidence, universal binary64 theorem 아님.
- 실제 native 48 spectral cells의 frozen gas/source, redshift OFF 240 rows. Exact Phi(MP70) 대비 aggregate survivor relative errors: uniform GL2=.526098022759121, GL4=.09575033192468319, graded2=5.505779900372166e-7, graded1.5=9.675957293445432e-9, graded1.25=1.0287765547248681e-10. Graded2 max species error4.111838032553128e-8, heat error3.5585840106614846e-8. 이 comparison은 saved native coefficients의 quadrature 확인이며 independent atomic continuum validation이 아니다.
- Source-native coupled 13 unique completed cases. SIGNED_MINUS N16→32 상대 차이 (분모N32): survivor9.11762124322646e-6 =0.0009117621243%, T1.5117712237611158e-7, HII6.492670956426139e-9, DII3.486285202747297e-7, HIevents1.1926189791289232e-7, HeIevents4.6918521334760044e-7, HeIIevents3.0475022757436854e-5, DIevents1.9527155741716484e-5. Parent RUN04 survivor18.2008% 비교는 historical retained result다.
- Same N8 birth grid g2→1.5 survivor relative difference5.37218292406827e-7, g1.5→1.25 difference9.508960840953762e-9. Same N8 opacity slices2→8 survivor5.003808478676319e-11, HeIevents2.1673910657327156e-6. Source cell mean→D-edge split survivor3.302124664229522e-4; angle refinement NOT_RUN.
- Temperature successive-difference ratios2.0088/2.0120/2.0172: 기존 global Lie split의 1차 경향. GL4를 추가했다고 global 4차 또는2차라고 부르지 않는다. 모두 adjacent-grid differences이며 continuum error bounds 아님.
- Max ledgers13 cases: photon5.415464498756704e-15, baryon1.1102230246251565e-15, augmented step energy4.442320617764325e-16. Max cohorts263424. Completed campaign sum119.3338839s는 interrupted partial과 duplicate pilot을 제외한다. 전체 비용은 O(B*M*N^2), storage O(B*M*N)이며 full solver speedup 주장 없음.

초기 큰 batch의45s outer timeout, helper-cancellation failure, Python HeII binding fixture 오독은 failure ledger에 보존했다. HeII는 실제 owner54.41776eV로 parser를 교정한 뒤 postprocessing만 다시 실행했다. 원래 source/physics/tolerance를 바꾸지 않았다.

## 최종 복원 검증

아래 immutable final ZIP을 새 directory에 풀어 152 payload hashes,118 Rust tests,strict Clippy를 확인했다. CONSTANT_KERNEL.csv,FROZEN_NATIVE.csv,대표 SIGNED_MINUS N2 coupled CSV와 numerical summary를 재생성하여 byte equality를 확인했다. 23.31s, maxRSS240688KiB, exit0. 전체13-case campaign을 clean restore에서 다시 반복했다고 주장하지 않는다.

## 저장과 재개

REI_RUN05_CODE_AND_RESULTS.tar.xz: 15116bytes,11members. Actual new Rust source/tests/examples + numerical summary/campaign + DAG delta, full standalone checkout은 아님.
SHA256 5e65e4581ed55b2c9ea080e096a1df46d0066dd2fc230a346f5e1045781c3ac6
Git blob SHA1 2889dc3b697a141a025976dd3b9f17e4d7b6adac

Full recovery ZIP REI_ATOMIC_NUCLEAR_RUN05_OPTICAL_BIRTH_20261017.zip:1977519bytes,153entries,152hashed payloads.
SHA256 2d7ac5310978c0cdff9d08da585d5c149a72e87a4e46e3c8ae1443c63e8ac543
Google Drive https://drive.google.com/file/d/1V7CVqJia1dCHD3BonivjAJcr4LcSLFb3/view?usp=drivesdk : upload complete,authenticated full download SHA256 matched.
Dropbox /BASS_DERIVATION_DOSSIERS_20260912/REI_ATOMIC_NUCLEAR_RUN05_OPTICAL_BIRTH_20261017.zip : object id:BSpOijBcT10AAAAAAD-njg,upload complete,provider content_hash2e13e41d455909512747cf8f69ffe0f4583ef87e9b16e1e3915e2325a9a786b3 equals local Dropbox hash. Independent full Dropbox byte download BLOCKED by runtime URL gate and direct DNS; not misreported as restored.

Full ZIP has source,inputs,raw failures,logs,SSOT and RUN04 archive. Unpack and run bash scripts/REPLAY_OFFLINE.sh with separate Rust1.94.1 and Python NumPy/mpmath. Toolchain/target not bundled.

Admission PASS_SCOPED_CONSTANT_OPACITY_ORACLE_AND_NATIVE_DONOR_COUPLED_BIRTH_REFINEMENT. Next P4-S4C-TIME-GAS-REFERENCE: same source/IC, independent nonlinear thermochemistry reference and depletion/opacity/Lie split error. Global time/spectral/angle,fullEoR,FLRW-CONV,BI-SIGNED,ISO-COUPLE full,Einstein reaction feedback and nuclear T1–T8 unfinished remain HOLD. Original45/26-node DAGs preserved. No extra automatic research cycle.
