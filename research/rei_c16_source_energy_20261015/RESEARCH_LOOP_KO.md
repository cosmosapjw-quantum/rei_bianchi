# REI C16.0: 실제 MD14 H/He 에너지 교환 및 Bianchi 전단 일 검증

2026-10-15 KST. 기준 C15 PR142: https://github.com/cosmosapjw-quantum/rei_bianchi/pull/142
불변 parent commit 435c94308c0cd7b1ba8ff6518246da061f2fc2fa. 격리된 연구 branch research/rei-c16-source-energy-20261015. 기존 C13/C14/C15 파일, 과학 Rust binary, original AX08 저장 이력 및 원래 checkout은 변경하지 않았다. Local Codex 미사용. Native AI subagent NOT_RUN (delegation unavailable).

## 이번 단계의 문제

C15는 실제 MD14 native stellar photon 방출, C11 Case-A H/He photoionization/heat/binding/escaped-radiation, C14 광자+중성미자 Boltzmann hierarchy 및 Einstein shear feedback를 짧은 a=0.1999→0.2에서 실제 실행했다. 하지만 항성 내부 에너지 공급원과 탈출한 recombination photon의 중력 에너지·운동량 및 시간 진화를 Einstein 전체 T_ab에 아직 넣지 않았다. C16.0A에서 이를 임의로 닫지 않고, 실제 수행된 국소 기하학 일과 stellar/escape 외부 source-Q를 정량적으로 검사했다.

기준 시계는 proper seconds. 계량 (-+++):
  ds² = -c²dt² + a² exp(-2b)(dx²+dy²)+a² exp(4b) dz²,
  s=db/dt, H=da/(a dt), Sigma=sqrt(sigma_ab sigma^ab/2)/H=sqrt3 abs(s)/H,
  epsilon_sigma=sign(s).

## 보존식 도출과 실제 코드의 대응

각 native 광자는 실제 C13 원본 Killing transport:
  R_i²=(1-mu_i²) exp(2 delta_b)+mu_i² exp(-4 delta_b),
  E'_i=E_i exp(-delta ln a) R_i,
  mu'_i=mu_i exp(-2 delta_b)/R_i,
  N_i per H nucleus conserved during source-free drift.

따라서 d ln R/db=1-3 mu_local², 그리고
  d U_UV / d ln a = -U_UV -2(s/H) P2_UV,
  U_UV=sum(N_i E_i),
  P2_UV=sum[N_i E_i (3 mu_i²-1)/2].

기체 adiabatic drift에서 dUthermal/dln a=-2Uthermal. 실제 현상론적 radiation/thermal geometric work는
  delta Wgeom = integral dln a [U_UV+2(s/H)P2_UV+2Uthermal]
              = (U_UV,old-U_UV,new)+(Uthermal,old-Uthermal,new).

별도 C16WorkAuditor는 실제 C15 Coupled.drift_segment를 호출한 뒤 같은 Einstein ODE의 독립 dense-output trajectory를 계산하고 Gauss4/8/16에서 integrand를 평가한다. Gauss work는 원래 C13 photon Killing endpoint와 gas adiabatic endpoint 계산을 사용하지 않는다. 화학 반응은 정확한 원래 C11 소스를 실행하고 source-stoichiometry/event/heat owner를 수정하지 않는다.

Orthonormal shear tensor sigma=diag(-s,-s,2s), traceless pi=diag(-DeltaP/3,-DeltaP/3,2DeltaP/3): sigma:pi=2s DeltaP. 분리된 시계와 단위: UV photons/gas binding/thermal/work: eV per physical H nucleus, radiation stress Pa, external Q0 physical J m^-3 s^-1. 변환 1 eV cm^-3=1.602176634e-13 J m^-3.

원본 C13 chemistry 보존식은
  U_UV + Uthermal + Ubinding + Uescape(CaseA) + Wgeom - Uemitted(MD14) = const.

C16은 저장된 실제 xHII,xHeII,xHeIII,xe,Tgas로 Uthermal과 Ubinding을 독립적으로 재구성한다. Source owner:
  Uthermal=(3/2) kB Tgas (1+nHe/nH+xe);
  Ubinding=13.6 xHII+(nHe/nH)[24.59(xHeII+xHeIII)+54.42xHeIII] eV/H.

이 원자 반응 보존에 따른 외부 관측 source-rate는
  Qext^0 = nH(a) [(delta Uemitted-delta Uescape)/delta proper time]
이고, 단위는 J m^-3 s^-1. 이것은 실제 stellar source/CaseA escape의 열린 전달량 측정이지 고유 EOS를 보유한 전체 stellar population/escaped photon 에너지 T_ab가 아니다. 개별 source fluid를 명시하지 않고 임의의 음수 항성 reservoir를 Einstein H에 더하여 전체 보존됐다고 주장해서는 안 된다.

## 축방향 운동량 보존성

현재 source의 축 반사대칭은 photon energy/number angular dipole을 0으로 만든다. 실제 모든 accepted macro state에서 UV photon P1과 BASS gamma/nu E/N l=1 값 검증. 무작위 tilted/dipolar photon source에 확장해 놓고 baryon recoil을 무시하는 것을 방지하기 위해, 양수 but asymmetric source angular weights를 넣는 adversarial fixture는 fail-closed. 따라서 현재 LRS non-tilted sector에서 Q_z=0은 물리적 대칭성에 근거한다. 일반 tilt 및 photon momentum transfer source는 추가 구현이 필요하다.

## 로컬 실제 계산 결과

소스와 부모 C15의 input SHA 동일. 사용된 실제 8X8 native spectral angular stellar photons; 32 macro time steps와 64 halfstep work samples에서 총 6 actual signed/initial radiation scenarios. 단일 공통 초기 positive radiation quadrupole kappa_gamma=kappa_nu=+.2, q 옛 signed source value는 초기 source-identity adapter로만 사용. Primary outputs are user Sigma_ref and epsilon_sigma.

대표 Sigma_ref=0.008660145786698617, epsilon_sigma=+1:
- 실제 원본 MD14 누적 방출 에너지 0.19286950329962063 eV/H;
- 실제 CaseA escaped photon 0.00213421635127003 eV/H;
- 순 외부 source 0.1907352869483506 eV/H;
- 실제 photon+thermal geometric work 0.002466445674526195 eV/H;
- 독립 Gauss8 photon P2 shear work error max 3.7987e-18 eV/H;
- 독립 Gauss8 full thermal+radiation work error max 7.4771e-16 eV/H;
- independently reconstructed native species/source energy ledger residual max 7.1054e-15 eV/H;
- max |Qext|/(H rho_background_gamma_nu)=3.29097915e-5. 이것은 open source rate ratio이므로 Friedmann constraint 위반의 상대값이 아니다.
- UV energy flux P1/E exactly 0 on saved native source states, BASS gamma/nu E/N dipole << 1e-20.
- Gauss4/8/16 변경에도 실제 원래 C15 물리 출력 f64 identical; 독립 수치 일 검증은 roundoff 수준.
- 실제 whole C16 audit 후처리 5반복 중앙 시간 0.61485 s vs 원래 C15 약 0.29051 s (2.12배 overhead). 이것은 production ODE 가속이 아니라 선택적 검산 비용.

실제 결과: results/RESULTS_C16.json, results/C16_SIGNED_PLUS_ACCEPTED_HALFSTEPS.json, results/C16_open_Q_energy_and_shear_work.png.

## 검증과 다음 DAG

Wolfram15 local CHECK_C16_CAS.wl은 photon characteristic sign, sigma:pi contraction, Qext owner algebra, axial reflection parity를 정확히 검사하여 PASS. 신규 C16 source/negative fixture 테스트 9/9, 기존 C15 11/11, C13 16/16, C14 9/9, C12 공급자 6/6: 전체 Ubuntu 직접 실행 51/51 PASS. 기존 GitHub verify.yml의 cargo fmt check는 부모의 많은 오래된 Rust 파일들 때문에 기존 PR137~139에서도 선행 실패했다. 원본 파일을 광범위하게 reformat하지 않고, 이 브랜치에 C16 source-specific Python CI workflow를 추가했다. 실제 GitHub CI 결과는 게시 후에만 판정한다.

문헌적 배경: Friedrich et al. 2012 (https://arxiv.org/abs/1201.0602) multifrequency helium/temperature timestep; Pawlik & Schaye 2010 (https://arxiv.org/abs/1008.1071) photon-conserving multifrequency thermal coupled H/He, plus actual BASS 1+3 Boltzmann dossier. 이들 문헌에서 현재 개방형 MD14 stellar source의 전체 중력 T_ab를 자동으로 도출할 수는 없다.

DAG에서 C16.0A native UV/gas/source Q0 + shear work + axial Qz=0 scoped verification은 완료. C16.0B의 실제 source star EOS/escaped photon transport/gravity momentum owner, physical case-on total Hamiltonian derivative closure는 미완료. 그 뒤 BASS E/B full polarised collision operator, 실제 massive J_i pressure, native 저온 z20→4 thermochemistry, AX11 time/frequency/angle matched errors and observer tail. 전체 scientific admission NOT_ISSUED.
