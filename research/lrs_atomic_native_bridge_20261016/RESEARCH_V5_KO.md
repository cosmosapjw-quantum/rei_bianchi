# LRS V5: Grackle Case-A 부분 공급원과 PR150 native 점 비교

## 범위와 출처

기준은 PR156 `0c2e7b2ada4fea131a5779066894589d0dda8059`; 비교한 PR150 기준 HEAD는 `a42fd7c9849306074a9f7a262628cd852ce34dea`이다. 게시 직전 갱신된 PR150 HEAD `4e2f0682fb605c6aa940bd756d9869e67b6ded0b`에서도 `igm_rates.rs`, `igm_thermal.rs`, `igm_state.rs`의 Git blob ID가 같음을 확인했다. 기존 V4 Verner 광이온화와 ray characteristic을 재사용하고, V4 기본 toy 경로는 그대로 둔 채 `atomic_rates`를 지정할 때만 물리 단위 경로로 들어간다. 원본 V4 816건 sweep은 재실행하지 않았다.

원자 donor는 Grackle 3.4.1 commit `af7939494ce65007887ada7b98d1813df6843346`의 `rate_functions.c`를 보존한 REI native `igm_rates.rs`이다. 이전 SOURCE07 C11의 129행 owner 표와 `rate_table.py`를 바이트 그대로 가져왔다. H II→H I, He II→He I, He III→He II의 radiative recombination, He II→He I dielectronic recombination 및 대응 recombination cooling만 사용한다. 각 계수는 cm³ s⁻¹ 또는 erg cm³ s⁻¹. Case A는 지면상태로 직접 재결합하는 광자까지 escape ledger로 보낸다. 표의 실제 부동소수 경계는 약 `10000.00000000001`–`24000.00000000003` K이며, 보간기는 외삽하지 않는다. He I에 hydrogenic 근사를 임의 적용하지 않는다. density fit은 없고, 낮은 밀도의 2체 반응률로만 쓴다. 원본 C literal reference의 세 내부 온도 점 차이도 최대 `8.18e-8`로 이전 native 자료에서 교차 검토했다. 이 검증은 표와 구현의 일치이며 천체물리적 정확도 인증은 아니다.

참조: [Verner et al. 1996](https://arxiv.org/abs/astro-ph/9601009), [Friedrich et al. 2012](https://arxiv.org/abs/1201.0602), [Pawlik & Schaye 2011](https://arxiv.org/abs/1008.1071), [Grackle 3.4.1 문서](https://grackle.readthedocs.io/en/grackle-3.4.1/Parameters.html), [Grackle 원본](https://github.com/grackle-project/grackle/blob/af7939494ce65007887ada7b98d1813df6843346/src/clib/rate_functions.c). Grackle의 Case-B switch는 이 연구에서 사용하지 않는다.

## 물리식과 owner

`X=ln(a/a0)`, `dt/dX=1/H`, `n_proper=n_star exp(-3X)`이다. comoving stock은 초기 `n_star`로 정규화한다. 광이온화 계수는 `c n_star 10^-18 cm² sigma_Mb exp(-3X)/H`; 재결합 계수는 `alpha(T) n_star exp(-3X)/H`. native 점 입력의 `gamma_s=c n_proper sum(N_ray sigma_cm²)`와 `heat_erg_per_absorber_s=c n_proper sum(N_ray sigma_cm²(E-chi) eV_erg)`를 만들었다. native `IgmGasState` ordering은 `(HII, HeII, HeIII)` fraction이고 V5 stock ordering은 `(HI,HII,HeI,HeII,HeIII)`이다. `n_e=n_HII+n_HeII+2n_HeIII`에 동일 proper 변환을 적용한다.

광자 흡수 에너지는 단 한 번 `photoheat + binding`으로, RR/DR에 따른 열 손실은 donor cooling/alpha를 각 사건에, 결합에너지 `chi`는 탈출 복사에 넣는다. recombination photon 수를 기존 ray population에 합치지 않는다. 따라서 올바른 전자 회계는 `Δne=photo−recomb`; 단순 photon+electron 불변량을 적용하지 않는다. expansion의 gas work와 ray redshift/shear work도 각각 한 owner를 가진다. Native `igm_point_rhs`의 CI/CE/freefree/CMB 항은 선택 비교에서 대수적으로 분리했고, production에서는 제거하거나 0으로 만들지 않았다.

PR150의 `igm_rates.rs`, `igm_thermal.rs`, `igm_state.rs` Git blob은 이전 PR157 point parity 기준과 같았다. 실제 native 경로는 `axbi_covariant_transport.rs::CovariantTransport::{add_delta,prepare}` → `PreparedAbsorption::evaluate` → `IgmPhotoInput`; 광원 `inject(per_h_s*dt_s)`가 따로 있다. 이번 것은 이 경로의 **점 반응 입력 및 선택한 ledger 항**과의 비교다. native transport/source/history를 결합 실행한 증거는 아니다.

## 재현과 수치 결과

NCP `s1a0e5abed09`, 2026-10-16 00:01–00:09 UTC (09:01–09:09 KST), 64 logical CPU/125 GiB RAM, 실행 전 가용 RAM 122 GiB, root 여유 19 GiB. 별도 `/root/REI_LRS_ATOMIC_NATIVE_BRIDGE_20261016_000210Z`, Python 3.12.3, Rust 1.99.0, NumPy 2.5.4, SciPy 1.18.1, pytest 9.1.1. OMP/BLAS 1 thread, Cargo 최대 4 jobs. 기존 R9 12-core worker와 BASS 실행을 건드리지 않았다. 최초 Rust build는 원본의 상대경로 `include_str!`가 빠진 디렉터리 깊이 때문에 exit 101; 첫 로그를 보존하고 동일 독립 복사본에 원래 `rust/rei_microphysics` 계층과 세 참조 계약을 설치하여 build exit 0으로 복구했다.

검증 기준: donor/native rate 및 선택 점 항 최대 상대차 `2e-7`; 저밀도 finest Radau 온도 `1e-3 K`, 전자수 `1e-10`; 원자/광자/전자 잔차 `1e-11`, 총에너지 `1e-11 eV`. 테스트 실패 후 완화하지 않았다. NCP Python 25/25 PASS, native Rust `igm_foundation` 9/9과 `igm_thermal` 11/11 PASS. 최종 재검증 Python 4.22 s/92 MB, 5-case×4 timestep Radau study 2.17 s/83 MB, 4-angle/energy refinement 0.99 s/81 MB, 고밀도 진단 0.69 s/82 MB. Release 예제 두 개 Cargo build PASS.

129-node table과 다른 native 121점×8 계수의 최대 상대차는 `1.298072427e-7`. `X=.02`, `T=15000 K`, `n_star=1e-6 cm^-3`, `H=1e-16 s^-1`에서 native 선택 점 항 최대 상대차: photo events `1.69e-16`, RR `6.38e-11`, DR `8.46e-8`, RR cooling `3.62e-10`, DR cooling `8.46e-8`, total photo input `0`, selected thermal `1.70e-15`, binding `9.69e-15`, escaped radiation `5.82e-11`. eV↔erg, Mb↔cm², proper/comoving 및 `H^-1` 인자가 이 점에서 일치한다.

H-only, He-only, mixed FLRW, mixed LRS `s/H=±.04`의 20개 timestep 결과에서 finest Radau 최대 온도 차이 `8.568745e-4 K`, 전자수 차이 `7.88e-12`. 최대 |energy| `1.25e-14 eV`, photon `1.85e-18`, electron `6.86e-17`, H `1.00e-15`, He `4.31e-16`; 최종 population 모두 비음수. 8→16 angular node 온도차 `5.63e-8 K`, 2→4 band-energy node `7.21e-6 K` (같은 band 정의와 timestep). ±shear 결과는 작은 shear에서 near-even이며 정확한 ± 대칭 법칙이라고 주장하지 않는다.

고밀도 재결합 지배 진단 `n_star=.1 cm^-3`, `H0=1e-16 s^-1`, `X_end=.01`, photon=0의 독립 Radau 최종 `T=14744.794774 K`에 대해 `ΔX=.0025,.00125,.000625,.0003125` 온도 오차는 `.0125253,.00627693,.00314200,.00157188 K`. 1차 비율로 감소한다. 현 forward pair map의 온도 의존 alpha/cooling은 각 부분단계에서 동결되므로 **일반 2차 Strang 수렴 주장은 HOLD**. 에너지 ledger가 0이라도 정밀도 결론이 되지 않는다.

## 추가 PR150 source-on FLRW 한 단계

별도 NCP 복사본에 GitHub PR150 `4e2f0682fb605c6aa940bd756d9869e67b6ded0b`의 실제 Rust crate를 고정하고 `native_pr150_source_step.rs`를 example로 컴파일했다. 이는 V5/Python 표 대신 PR150의 실제 `AxbiSource::inject` → `CovariantTransport::prepare` → `PreparedAbsorption::evaluate` → `igm_point_rhs`를 차례로 호출한다. `a=.05, z=19`, `dt=1e10 s`, `nH=1.518558760571221e-3 cm^-3`, gas `15000 K`, Case-A native owner로 한 번의 명시적 Euler 상태 갱신을 수행했다. NCP exit 0, source 주입 `4.951273748616365e-8` photon/H, 흡수 `2.572236103809841e-8` photon/H, 갱신 온도 `14998.84953918 K`, prepared node 2432개. source count/energy 상대잔차 `1.34e-16/1.69e-15`, 흡수 photon count/energy `2.71e-15/2.20e-16`, electron `1.23e-16`, micro energy `6.13e-16`. transport→chemistry 접속부의 종별 photo event 및 총 photo energy 상대잔차는 `2.60e-15/1.32e-15`. 최종 warmed example은 0.24 s/120 MB, 첫 build는 7.39 s/341 MB. 원래 cargo 복사본의 여섯 `include_str!` 계약 누락으로 난 첫 exit 101 로그를 보존하고 원본 계약을 추가한 뒤 재실행했다. 이 실행은 **고정 geometry/밀도의 실제 native source-on 단일 단계**의 보존 회계이며, photon 감쇠는 backward Euler, gas 갱신은 explicit Euler이다. redshift/shear work와 implicit production whole-history 수렴의 증거가 아니다.

이 추가 source→transport→chemistry 접점은 구현하지 않은 독립 reviewer가 NCP 원시 결과와 PR150 코드를 읽고 위의 **고정 geometry 한 단계 회계**에 한해 scoped PASS로 판정했다.

## 과학적 채택과 다음 일

채택은 엄격한 10–24 kK 내부, Case-A RR/DR+recombination cooling, 지정된 낮은 밀도/균일 background, native **점 항**과 위의 source-on **단일 단계 회계**까지다. native transport+source의 다단계 시간 이력 수렴, CI/CE/freefree/CMB를 포함한 V5/Python 총 RHS 동등성, escaping recombination photon spectrum, Case B on-the-spot, 재이온화 우주론적 이력 및 observational accuracy는 HOLD. 다음 최소 연구 단위는 동일 frozen initial state에서 PR150 owner의 source-on 다단계 FLRW 짧은 구간을 time-step refinement와 함께 실행하고, photon·species·heat·binding·escape를 연속 step으로 비교하며 dense recombination 1차 결손을 해결하거나 명시적으로 제한하는 것이다.

원시 archive `REI_LRS_ATOMIC_NATIVE_BRIDGE_20261016_000210Z.tar.gz`는 606,203 bytes, SHA-256 `d5d37a6f680bd900336c40ba9e3e02e7f936cbf2bb64d9df28e989b4c692bcfd`. [Google Drive 객체](https://drive.google.com/file/d/1ICEmIEoBHV4zCLdT-wDlCyVns3PGJxBn/view)와 Dropbox `bianchi/research_backups/rei_bianchi/REI_LRS_ATOMIC_NATIVE_BRIDGE_20261016/` 객체 `id:BSpOijBcT10AAAAAAD9ixg` 모두 원격 readback SHA-256 일치. 객체별 크기와 경로는 `V5_DELIVERY.json`에 기록했다. 백업의 성공과 위의 제한적 과학 채택은 서로 다른 판정이다.

추가 source-on 단계의 보충 archive `REI_LRS_ATOMIC_NATIVE_BRIDGE_20261016_SOURCESTEP_000210Z.tar.gz`는 343,625 bytes, SHA-256 `3661408083d45904d12cdafeb3eae7bfc06680afaaea5018ea48017932a1590d`. [Google Drive 객체](https://drive.google.com/file/d/1DkYVMJAwb2qg6ntYDmyULDOsQhDZO79w/view), 같은 Dropbox 폴더의 객체 `id:BSpOijBcT10AAAAAAD9kGA` 모두 별도 원격 readback SHA-256이 일치했다. 첫 archive는 변경하지 않았다.
