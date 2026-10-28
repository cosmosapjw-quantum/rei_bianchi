# BASS_HE 확장 연구 성격 — 2026-10-25

BASS_HE는 목표 원자·이온·동위원소·분자·전자 사이 충돌의 유한질량 event kinematics, differential source, 운동량·에너지·응력 전달, thermalization과 species-to-gas closure를 소유한다. 외부 nonthermal distribution, cascade, stopping evolution은 bass_cr가 lead하고 HE는 differential energy-transfer kernel을 공급한다. H1 ionization angular 작업을 보존하며 일곱 핵종의 모든 전하 상태와 source가 선택된 분자 동위원소체까지 연구 책임을 확장한다. 저장소 이름이나 기존 He–H 논문의 범위가 새 연구 임무의 한계는 아니다.

## 현재 실제 기준

확장 branch base는 PR101의 `28a26f4db951ab9085180e2ecc5d600d981a1f71`, branch `research/he-ang-finitemass-cba-20261025`다. 기존 owner branch를 변경하지 않는다. 현재 finite-mass labelled direct C1 Born 모형의 theory·finite numerics는 scoped PASS, 전달19/20/C8 PARTIAL_EXPORT다. 원 science `9fc8185437f145a6ba4569e1b38aa2e12d15acd9`의 수치/실패/원장은 그대로다. actual child PASS/FAIL/FAIL, exit0/-9/-9이며 reserve0이다. SVG/producer figure metadata/원 repair summary 미존재를 사후 PASS나 가짜 영수증으로 바꾸지 않는다.

전체 HE-ANG은 SOURCE_INPUT_PENDING, physical_provider_admitted=false다. PR97 PWBE의 당시19/20 표시는 PR98의 실제 saved-output continuation으로 scoped20/20이 됐다. PR101 C8은 별도 현재 열린 의무다. PR94–100의 finite source/model 성과를 preparation-only로 되돌리거나 물리 full provider로 확대하지 않는다.

## 모든 목표 species

| 목표 | charge coverage | 추가 변수 |
|---|---|---|
| H1,D,T | q=0,1 | isotope mass, bound state, projectile/target label |
| He3,He4 | q=0,1,2 | isotope mass, internal state, exchange/spin |
| Li6,Li7 | q=0,1,2,3 | isotope mass, shell/final-state branching |
| neutron/electron | n와 free e 별도 | nuclear versus electronic process, thermal/nonthermal |
| 분자 동위원소체 | source-selected charge/states | H/D/T families, He3/4–H/D/T,Li6/7–H/D/T, rotational/vibrational/spin state |

21개 현재 nucleus/ion state는 REC PR119의 실제 manifest에서 확인했다. electronic equality 근사는 isotope-resolved rate 측정이 아니다. 새 연구는 전체목록을 명시적으로 추적하고 각 source의 실제 범위를 보존한다. 모든 가능한 pair를 동시에 계산해야 다음 단위가 열리는 구조를 만들지 않는다.

## 확장 임무와 최적 책임

1. 모든 목표에서 elastic/momentum transfer, excitation/deexcitation, impact ionization, recombination-related energy exchange, charge exchange, ion–neutral/ion–ion/electron collision의 실제 differential source와 validity를 받는다. WU088_HH의 amplitude/atomic structure, WU의 elementary event branching과 bass_cr의 external cascade을 원 supplier로 유지한다.
2. event1/electron2/ion1처럼 count를 고정하고 outgoing joint law, exchange/spin, complete support, lab/COM/Jacobi frame, recoil를 한 사건으로 결속한다. inclusive electron marginal만으로 ion STF를 완성하지 않는다.
3. 외부 electron/ion/neutral/cosmic-ray/decay daughter beam의 source와 thermal target에 대해 bass_cr가 소유한 stopping/secondary evolution에 differential recoil와 anisotropic energy-momentum transfer kernel을 공급한다. source의 birth energy와 실제 heat deposition을 분리한다. stopping의 제거 항과 REC thermal의 유입 항은 같은 energy owner의 반대 부호다.
4. photon-produced photoelectron/ion pair의 joint event를 받아 bass_cr의 nonthermal evolution에 collision kernel을 공급한다. 직접 photon absorption/emission spectrum과 level populations는 REC, elementary channel과 branching은 WU에 유지한다. inverse Compton 등 kinetic particle–radiation exchange는 선택한 공통 event contract로 REC photon source와 결속한다.
5. species별 T_s,bulk velocity,pressure/STF 또는 kinetic distribution에서 total baryon stress와 reduced closure를 만든다. relaxation/source/Hubble timescale과 observable error로 reduction을 판단한다.
6. nuclear source를 선택하면 WU nuclear/weak elementary channel과 bass_cr external daughter distribution의 momentum,charge,level,Q,neutrino와 cutoff를 받아 differential energy exchange와 thermalization을 연구한다. HE의 비상대론 kernel 바깥 relativistic energies는 source-domain failure로 분리하고 relativistic kinetic owner와 연결한다. 원 He–H indexed-state survival을 physical elastic cross section으로 사용하지 않는다.

## 식·단위·검증

PR101은 a0=hbar²/(m_e g), p0=hbar/a0,E_h=hbar²/(m_e a0²), nucleus mass=M m_e로 무차원화했다.
mu=M/(M+1),nu=(M+1)/(M+2), B=mu/2, epsilon=nu E0-mu/2다.
Delta=qi-q이고 recoil potential Fourier phase는
exp(i mu Delta·r)-exp(-i Delta·r/(M+1))다.
D_M=L_mu(mu Delta,k)-L_mu(-Delta/(M+1),k).
W=4|F_M|²/(|P|Delta⁴), Jacobi density=mu nu q k W다.
각 positive lab root에는 해당 root의 W를 각각 평가한다. Er은 pair-relative energy이며 lab outgoing-electron energy로 relabel하지 않는다. TDCS physical unit a0²/E_h, W는a0² E_h/p0^6이다. 이 유도는 labelled/direct C1, 비상대론/특정 continuum closure이며 exchange-complete atomic provider가 아니다.

species stress를 common baryon bulk u_b에서 합성하면
pi_b=sum_s[pi_s+rho_s (u_s-u_b)_{<i}(u_s-u_b)_{j>}].
bulk drift tensor를 생략하려면 common bulk assumption의 물리적 근거가 필요하다.
species pair의 momentum/total energy 교환은 합계0이며 상대 drift의 열전환을 포함한다.
thermal monatomic U_th=sum_s(3/2)n_s k_B T_s; molecular internal energy와 nonthermal energy는 별도다.
입자 생성은 C_V와 binding을 동시에 바꾸므로 positive kinetic injection만으로 dT/dt나 isotropization rate를 선언하지 않는다.

필수 gate는 source의 threshold/support/normalization/count/frame consistency, finite-mass momentum-energy closure, positive moment cone, source-calibrated uncertainty, 변경된 input의 independent witness다. model/quad/roundoff error와 source uncertainty를 분리한다. HE-X1 PSD는 필요조건이며 event law가 아니다. identity probability tail은 elastic sigma가 아니다. optical/infinite-nucleus source를 isotope recoil law로 자동 변환하지 않는다.

## DAG와 PASS 이후

HE-X1 완료 → HE-ANG source 입력. HE-ANG,HE-EXCHANGE,HE-RESERVOIR의 선택된 채널 gates → HE-CLOSURE → HE-FEEDBACK. 특정 채널에서 불필요한 supplier의 완료를 대기하지 않는다. 새 전종 coverage node는 source inventory/단위검증 단계이며 모든 전종 physics PASS를 의미하지 않는다. 원HE35 pair·HE38·DDCS·CCC·TDCS·CBA 완료 suite는 재실행하지 않는다.

PR101 현재 11.882829 CPU s/11.985978921 wall s, CBA lineage16.870803/17.108468335994985를 보존한다. 개별 child CPU cap overshoot와 kill source NOT_OBSERVABLE도 남긴다. reserve0이므로 export 또는 science 재시도는 기존 allocation에서 자동 시작하지 않는다. 확대 branch로 옮겨 비용을 초기화하지 않는다.

요청 authority는 Astra-tier이고 실제 runtime 모델은 NOT_OBSERVABLE이다. actual AGENTS의 paper-derived independent implementation, physics/approximation/test/pilot 분리, no unchanged reruns, no source PDF redistribution 및 measured HPC parity 지침을 적용한다. 새 Fortran/OpenMPI 구현은 같은 workload 측정과 explicit budget 이후 선택하며 물리 오차를 speedup과 교환하지 않는다.


## 공통 소유권 정합

lead object는 ROOT_SCOPE_AND_ASSEMBLY_CONTRACT.md를 따른다. WU는 species identity와 elementary atomic/molecular/nuclear/weak branching/energy, REC는 level populations/spectra/history, HE는 differential collision/thermalization/particle-count·heat-capacity closure, CR는 external nonthermal distribution/injection/cascade/stopping, BASS는 geometry/background/covariant coupling, REI는 selected scenario/assembly를 소유한다. HE의 isotope/pair manifest는 WU identity의 consumer projection이다. TASK_ASSIGNMENT의 외부 lead task는 협력 의무이며 HE가 해당 산출물을 중복 구현하지 않는다.

현재의 일곱 동위원소 목록은 WU의 확장 가능한 target catalog에서 실제 확인한 초기 view다. 미래 scope의 상한이나 모든 intended target의 완전 열거가 아니다. 새 (Z,A,isomer), 분자 isotope composition, signed charge, internal state, collider, electron-pool ID는 실제 source로 확장하고 missing data는 coverage gap으로 남긴다.
