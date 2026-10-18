# PHYS63 C5–C8: tiny physical screened response를 직접 적분하는 scaled Riccati

## 원형, 범위 및 실행 목표

2026-10-18. R5 parent PR109 commit 13a9d2cacedc84d9d23cd1193837de2c75f781b5.
Original NPZ SHA256 f1bd3074950163960cc2011682d013af60f9b17c471bea72ecbc2ffb19e6855d.
원래 h=-Delta/2-1/r-S, S=(1+1/s)e^-2s, s=|x-0.7 zhat|와 real energy49/200 Hartree,
u=r psi, boundary B=27, Z=+u'(B)를 유지한다. 공간/에너지 단위는 프로젝트 원자단위다.
각도는 signed m을 고정하여 ell=|m|..L를 포함한다. m0 L21/24/28/32 및 m1/m2 L28을
실제로 실행했다. 수치문제는 r>=T의 screen을0으로 둔 truncated exterior이며 T=35/39/43,
r=T에서 중앙 Coulomb의 정확한 outgoing DtN을 부과한다. 이 finite projection은 R5의
무한 angular 정리 자체가 아니며 Galerkin/radial convergence에 대한 엄밀한 오차상계도 아니다.

## 정확한 수학-코드 변환

Q_C=diag[k²+2/r-ell(ell+1)/r²], V_ij=<Y_i,2S Y_j>.
원래 ODE U''+(Q_C+V)U=0에서 Z=U'U^-1는
Z'=-Q_C-V-Z²를 만족한다. 중앙 diagonal z_C는 z_C'=-Q_C-z_C².
Delta=Z-z_C를 매우 큰 두 행렬의 차로 구하면 원래 약1e-24 diagonal response가
부동소수점에서 사라진다. 따라서 scale=3e-23*strength, Delta=scale*Y로 놓고

Y'=-z_C Y-Y z_C-scale Y²-V/(3e-23), Y(T)=0

를 뒤로 적분한다. strength=1이 실제 원형이며 strength=0은 정확 zero-response 제어다.
다른 strength는 명시된 비물리적 구현검증에만 쓴다. 원래 V를 매 RHS 위치에서
associated-Legendre Gauss–Legendre Gram으로 직접 조립하여, 임의의 manufactured
spectral coupling으로 바꾸지 않는다. 모든 포함 ell의 중간 결합을 유지한다.
Wolfram에서 2x2 비가환 행렬 Riccati 전개 residual이 정확히0임을 검산했다.

중앙 z(T)는 mpmath CoulombG+iF와 정확 DLMF33.4 recurrence로55dps에서 구한다.
이후 SciPy DOP853가 z_C와 Y, log p의 radial primitive를 함께 적분한다.
log p'=z_C를 사용한 별도의 GL80 Born 적분을 비교하지만 이는 동일 중앙 경로를
재사용한 consistency test다. 독립 기준은 이전 PR108의 mpmath physical Born 값,
선택된 ell의 mpmath 중앙 로그미분, 아래 별도 second-order system이다.

## 실제 물리적 응답과 절단 진단

rmax39,angular GL128,rtol2e-11,m0의 Delta21,20:

| L | Re | Im |
|---:|---:|---:|
|21|2.7660422460144697e-24|4.500676730150533e-25|
|24|2.7660422460147823e-24|4.500676730148966e-25|
|28|2.7660422460146247e-24|4.5006767301497705e-25|
|32|2.7660422460142044e-24|4.500676730151974e-25|

L28,T35 gives 2.7660421598780162e-24+4.500677527607495e-25i.
L28,T43,GL192,rtol2e-12 gives 2.766042245980961e-24+4.500676730175846e-25i.
이 차이에는 반경/각도 적분/solver 오차가 섞여 있으며 인증된 truncation bound가 아니다.
physical scale nonlinear term은 약1e-23 relative이므로 f64에서 분해되지 않는다.
따라서 nonlinear equation을 구현/적분했다는 사실과 실제 nonlinear remainder를
측정했다는 주장을 구분한다. **후자는 NOT_RESOLVED**다. cutoff 일치만으로 원래
무한 angular response나 physical cross section이 수렴했다고 주장하지 않는다.

모든 포함채널 Delta는 transpose symmetric(최대 결함~1.7e-39)이며, ±m 원래
angular matrices는 byte-identical이다. diagonal z_C+Delta를 f64로 합하면 diagonal
response가 소실되므로 Delta를 별도 데이터로 보존한다.

## 독립적인 비선형 구현 제어

실제 V 형태에 strength=1e20를 곱한 **명시적 비물리적 amplified control**만
ell=(0,1),m0,r27..33에서 사용했다. 별도의 U,U' second-order ODE에
U(T)=I,U'(T)=diag z_C(T)를 주어 Z=U'U^-1를 구했다.

- scaled Riccati 대 direct fundamental Z 최대차: 9.665165470492141e-15.
- conserved current transported by U^-1 검산 residual: 4.441819159289155e-16.
- nonlinear versus first-order-only relative change: 1.671999517309308e-4.

이 제어에서 비선형 항이 실제로 분해되므로 Y² 항 누락/부호/행렬순서 오류를 검출한다.
위 정확도를 원래 strength1의 nonlinear correction에 옮기지 않는다.

## 실제 실행·검증 이력

최초 공개 seam 테스트는 screened response가0인 missing-feature baseline에서 실제
실패했다(relative error1). 실제 scaled ODE를 구현한 후 같은 테스트 PASS.
RED/GREEN stdout와 exitcode를 저장했다. 추가 테스트는 구현 후 작성한 회귀검사이므로
전체 테스트가 각각 red-first였다고 주장하지 않는다.

R5 8개 + C5-C8 16개 = 통합24/24 pytest PASS, exit0, test6.03s,
wall8.32s, max RSS210300KiB. Producer exit0, wall8.14s, max RSS145164KiB.
새 코드는 실제 source SHA gate, ±m symmetry, invalid-input/source-tamper guards,
zero-screen limit, direct Coulomb boundary check, independent amplified second-order
system/current, finite L/T/GL refinement를 포함한다. 테스트는 수치 구현을 검증하며
R5 외부 스펙트럼 문헌 정리의 자동 증명은 아니다.

모든 실행은 ChatGPT sandbox, BLAS1thread. NCP/사용자 로컬/전체 WU test/native
subagents NOT_RUN. NCP가 필요한 규모가 아니므로 실행 인계 불필요. 원래 source,
다른 저장소, REI production, HH_R10 owner는 변경하지 않았다.

## 판정 및 다음 DAG

R5에서 **질적 실수축 full screened LAP/Poisson/DtN 존재**는 문헌 가정대조와 유도로
닫혔다. C5-C8는 finite L,T의 tiny response를 보존하는 실제 적분기를 추가한다.
다음 PHYS64는 usable norm constants, 인증된 angular/radial/numerical truncation,
interior matching conditioning 및 source-driven xi 문제다. 존재성 자체를 다시
OPEN으로 되돌려 메타검산을 반복하지 않는다. xi=Fy-phi, regular origin/incoming
adjoint, sigma(E), identical neutral-H Maxwellian k_HH(T)는 아직 HOLD,
rei_bianchi HH_R10=OFF.
