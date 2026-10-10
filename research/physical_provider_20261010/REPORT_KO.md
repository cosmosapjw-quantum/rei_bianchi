# REI-PHYSINPUT-01 — Bianchi-I 물리 입력과 첫 결합 구간

2026-10-10 · 기준 commit `17bd1cc0ce1484ee61cac60ab1bda207ae264381` (PR93).

**결론: 누락돼 있던 네 종류 입력을 명시적인 source-backed 조건부 모델로 채우고, 실제 Rust 원자율·AXI 함수에 연결한 첫 coupled interval을 실행했다. 본래 production `PhysicalHistory`의 물리 admission은 아직 해소되지 않았다.** 단순 제조 함수나 기존 성공 표지를 다시 포장한 결과가 아니다. 원저자 HM12 source bytes, 직접 유도한 비상수 Einstein 배경, 정규화한 IC, 선택한 closure를 가진 새 초기값 문제다. 다만 선택한 따뜻한 가스·test-field·primary-only 가정의 타당성과 production 연결은 남아 있다.

사용자가 지정한 Astra 연구/코딩 하네스 v4.0.0을 순차 적용했다. 하네스 선택은 실제 runtime 모델 전환·성능 검증을 의미하지 않는다. 실제 독립 reviewer의 최종 범위와 판정은 `independent_review.json`, `REVIEW_KO.md`에 보존한다. 코드·원자료·실행 증거·이 보고서·Codex 시작문은 같은 additive 연구 폴더에 속한다. 게시 identity는 별도 publication receipt를 따른다.

## 무엇을 해소했는가

| 기존 누락 | 이번 산출물 | 근거 상태와 제한 |
|---|---|---|
| Bianchi-I background/time map | Einstein dust+Λ LRS 해, proper-time→scale/redshift, 역함수, 방향별 null characteristic | derived / numerically checked. Radiation/thermal metric backreaction을 제외한 선택 모델 |
| 정상화 IC | baryon density·H/He 질량비, charge-neutral ionization-equilibrium root, thermal energy, 실제 HM12 photon IC | derived / implementation-verified. 초기 $T=50000\,K$, shear ratio $10^{-3}$는 선택값이며 REC history가 아님 |
| photon/source history | 원저자 `UVB.out`을 최초 IC에, 별도 `emissivity.out`을 시간별 source에 사용 | literature-supported / implementation-verified. 후기 UVB를 강제로 덮어쓰지 않음 |
| closure 선택 | homogeneous $C=1$, Case-A recombination escape, primary-only one-temperature H/He | explicit model choice. Diffuse/OTS 또는 완전한 재이온화 closure로 승인하지 않음 |
| 실제 consumer | `run_interval.py`→native consumer→기존 `ft03_rhs`, Verner cross section, `axisym_coupled_derivative` | implementation-verified. 연구 entry point이며 production admission enum은 그대로 닫혀 있음 |

최신 공개 AXI code에는 provider 필드를 모두 채워도 `PhysicalExecutionNotImplemented`를 반환하는 별도 구현 경계가 있다. 따라서 dataset만 추가해서 기존 gate를 GREEN으로 바꾸지 않았다. PR90의 CPU STOP 및 F09의 optional atomic common-domain 공집합과도 구분했다. 사용자가 인용한 미공개 로컬 세 번의 재검증 dossier는 이 환경에서 직접 읽은 자료가 아니다.

## 이론 계약

좌표는 gas proper seconds, signature는 $(-+++)$, 틸트·tetrad 회전은 없다. $a_\perp=ae^{-b}, a_\parallel=ae^{2b}$, $s=\dot b$이므로 $\sigma^2=3s^2$, $H_\perp=H-s, H_\parallel=H+2s$다. 선택한 dust+Λ 해는

$$
H^2=H_{\rm fid}^2(0.3a^{-3}+0.7)+s_0^2a^{-6},\quad
s=s_0a^{-3},\quad dt=\frac{da}{aH},\quad db=\frac{s_0\,da}{a^4H}.
$$

$H_{\rm fid}=70\,\mathrm{km\,s^{-1}\,Mpc^{-1}}$, $\Omega_b=0.045$, $Y_{He}=0.24$. 최초 $z_a=5.807, r=s_i/H_i=10^{-3},b_i=0$. HM12의 역사적 fiducial cosmology를 사용하며 현재 최선 적합값으로 주장하지 않는다. $z_a=a^{-1}-1$은 체적척도 label이지 방향별 관측 redshift가 아니다. 비영 shear를 추가하고 flat-FLRW $H$를 그대로 두는 constraint 위반은 피했다.

고정 초기 momentum $q=E(t_i)$, $\mu_i$에서

$$
R=\frac{E(t)}q=\frac{\sqrt{(1-\mu_i^2)e^{2b}+\mu_i^2e^{-4b}}}{a_{rel}},\quad
\mu(t)=\frac{\mu_i e^{-2b}}{a_{rel}R}.
$$

원자료의 angle-integrated proper log-energy photon density/source는

$$
n_{\ln E}=\frac{4\pi J_\nu}{ch},\qquad
S_{\ln E}=\frac{\epsilon_\nu^{com}(1+z_a)^3}{h\,\mathrm{Mpc}_{cm}^{3}},\quad h=2\pi\hbar.
$$

각 quadrature 셀의 초기 proper-reference photon number $N_i=a_{rel}^3 n_i$는 $\dot N_i=S_{\ln E}(E_i,z_a)w_i/R_i^3-c\kappa_iN_i$를 따른다. $R^{-3}$에는 방향 Jacobian이 포함된다. 같은 흡수 사건이 광자수, ion source, threshold binding, primary heat에 각각 한 번 들어간다. 재결합 방출은 **총에너지 escape ledger만** 기록하며, 방출 광자수나 spectrum을 결정했다고 주장하지 않는다. 자세한 유도·단위·IC 유일성은 `THEORY_DERIVATION_KO.md`를 따른다.

## 실제 실행과 검증

구간은 $0\le\Delta t\le10^{11}\,s\simeq3169\,\mathrm{yr}$다. 최신 candidate는 초기 momentum $10\le q/\mathrm{eV}\le50000$, 2904개 energy-angle nodes, 17개 저장 epoch를 사용했다. 현재 lab-energy band는 방향에 따라 이동한다. Refined 실행은 11616 nodes다. 큰 시간범위나 전 재이온화 history를 실행한 것이 아니다.

| 활성 candidate의 물리량 | 시작 | 끝 |
|---|---:|---:|
| volume-redshift $z_a$ | 5.807 | 5.80698492362111 |
| $n_H\,[\mathrm{cm}^{-3}]$ | $5.9356219732\times10^{-5}$ | $5.9355825340\times10^{-5}$ |
| $x_{HII}$ | 0.999975474528 | 0.999975474564 |
| $x_{HeII}$ | 0.970083902439 | 0.970083900991 |
| $x_{HeIII}$ | 0.0298612793821 | 0.0298612808769 |
| $T\,[K]$ | 50000 | 49999.7770770 |
| $\Gamma_{HI}\,[s^{-1}]$ | $2.9135600945\times10^{-13}$ | $2.9138496109\times10^{-13}$ |
| $\Gamma_{HeII}\,[s^{-1}]$ | $1.1590497414\times10^{-18}$ | $1.1898194477\times10^{-18}$ |

- HM12 intake 10 tests, native consumer 6 tests, 기존 영향 범위 Rust regression 27 tests가 실제 통과했다. 기존 production source를 수정하지 않았다.
- Einstein constraint·volume·shear·핵수·null covector·독립 geometry ODE·FLRW 극한의 오차는 최대 약 $1.2\times10^{-15}$였다. 역 redshift 시각의 roundtrip 오차 6.86 s는 아주 짧은 구간에서 binary64 redshift 입력의 conditioning 한계 23.56 s 안에 있었다.
- 총 11 histories를 실행했다. 최초 band에서는 DOP853/tighter tolerance/RK4 32·64 steps, energy·angle refinement, FLRW 및 source-OFF controls를 수행했다. 확장 band에서는 DOP853/RK4 및 joint refinement를 실행했다.
- 활성 candidate의 DOP853–RK4 비교 최대 상대차는 $5.24\times10^{-12}$. 에너지·각도 joint refinement 최대 상대차는 $3.13\times10^{-7}$. 모든 실행의 energy ledger 최대 scaled 잔차 $2.28\times10^{-15}$, active photon-number ledger 최대 $1.84\times10^{-14}$. Fraction domain, photon positivity, 원래 FT03 온도 guard를 지켰다.
- Source-OFF에서 photon/thermal 결과가 달라지고 비영 shear에서 radiation pressure anisotropy가 발생함을 확인했다. 이는 실제 source/geometry 소비의 증거이며 관측적 비등방 효과 검출은 아니다.
- 시간 적분법 비교는 원자율·parser를 공유한다. 독립 원자물리 검증이 아니다. 짧은 구간의 시간오차는 roundoff 수준이므로 측정된 4차/8차 수렴률, 전역 continuum bound를 주장하지 않는다.

## 스펙트럼 잘림에서 발견한 실질적 수정

첫 10–200 eV 실행은 numerical ledger를 통과했으나 원자료 tail 감사에서 중요한 누락이 드러났다. 200–50000 eV는 초기 He II photoionization의 **8.576%**, primary-heating의 **53.945%**를 차지했다. 따라서 회계 보존만으로 spectral completeness를 승인할 수 없다.

이 실패를 보존하고 단면적 provider의 원래 지원 상한 50 keV까지 확장했다. 초기 HeIII fraction이 0.02786955에서 0.02986128로 변했다. 이는 무시할 수 없는 IC 수정이다. 원자료 UVB의 서로 다른 값이 같은 파장에 기록된 19쌍도 평균화하지 않고 한쪽 값이 다른 점프로 보존했다. 모든 native nodes와 threshold를 나눈 양의 quadrature를 사용했다.

50 keV 위에도 원 UVB/source는 존재한다. 그 부분은 현재 원자 provider의 구현 범위 밖이며 반응율·heating을 외삽하지 않았다. 원 표의 ionizing energy 중 이 상한 바깥 비중은 UVB 약19.58%, source 약4.26%지만, 이 energy 비율을 gas heating 비율로 대체해서는 안 된다. Secondary electron deposition, Compton 등도 이번 primary-only 모델에 포함되지 않았다.

## 남은 경계와 다음 실제 작업

**운영 입력의 부재는 이 조건부 모델에서 해소됐고, 물리 admission blocker는 구체적인 항목으로 좁혀졌다.** 첫 구간의 성공만으로 다음을 승인하지 않는다.

1. Production의 별도 `SourceBoundConditional` 실행 계약/provider interface에 이 dataset을 연결해야 한다. 기존 `PhysicalHistory`나 `CaseAExplicitDiffuse` enum을 형식적으로 재사용해 열면 안 된다.
2. 원하는 연구가 차가운 평균 IGM/REC→REI 초기조건이라면 실제 REC 출력을 지정하고, FT03의 30000 K 하한 밖 원자율·열모델을 검증해야 한다. Warm parcel의 온도를 낮춰 넣거나 clamp하지 않는다.
3. Global photon history에는 diffuse escape/재흡수, secondary/Compton, source-spectrum·atomic-fit 오차 및 고에너지 경계 정책을 결정해야 한다. Dust+Λ 배경의 test-field 근사와 HM12 source의 Bianchi 이식도 선택한 물리 가정이다.
4. 이 후보의 $\Delta t=10^{11}s$ 밖 장기 안정성·전 history·균일 시간오차 certificate·$Q_V$·관측 재현은 미실행이다. 기존 F04/F08 엄격 gate 및 과거 실패는 그대로 유지한다.

동일한 부재 검색을 반복하기보다는 `CODEX_HANDOFF_KO.md`와 `RESEARCH_DAG.json`의 다음 실행 단위를 사용한다. Native Rust compiler가 처음 없어서 시스템 패키지 설치가 환경 권한 때문에 실패했으며, 공식 hash를 확인한 독립 toolchain으로 build/test를 완료했다. Cargo-fmt는 설치되지 않아 실행되지 않았다. Git CLI 인증은 없으므로 게시에는 연결된 GitHub Git-object API를 사용한다. CI는 실제 관측된 별도 receipt 없이 통과했다고 주장하지 않는다.

## 근거 파일과 원전

- `CONTRACT.json`: 고정 모델·가정·numerical criterion·D01 수정.
- `evidence/VALIDATION.json`, `input_audit.json`, `background_validation.json`: 실제 수치와 한계.
- `evidence/extended.json`, `extended_dataset.npz`: 활성 candidate의 history와 전체 상태.
- `native/validation/EXECUTION.json`: 테스트 명령·exit·toolchain/source identity.
- `SOURCE_MANIFEST.json`: immutable 원자료·코드·evidence identity. Hash는 과학적 admission을 대신하지 않는다.
- 원저자 [CUBA 배포](https://www.ucolick.org/~pmadau/CUBA/DOWNLOADS.html), [HM12 원 논문](https://arxiv.org/abs/1105.2039), [Puchwein et al. 2019](https://doi.org/10.1093/mnras/stz222), [Bianchi-I shear 구조](https://arxiv.org/abs/1003.3491). 원문 열람 범위와 supports/limits 구분은 `THEORY_SOURCE_LEDGER.json`에 있다.
