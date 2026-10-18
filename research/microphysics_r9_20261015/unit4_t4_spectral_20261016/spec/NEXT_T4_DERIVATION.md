# T4 finite daughter spectral measure: derivation

Selected work: PhysMath 1.3.0 C1–C4, with the mathematical definition and construction needed for one T4 execution contract. The accepted Unit3 result supplies normalized parent i, normalized approximate daughter ground g, and the shared orbital matrix X in a 92-orbital finite Hilbert space. All energies below are Hartree. The atom is fixed at the origin with a point nucleus; the electron sector is (Nalpha,Nbeta)=(2,1).

## Saved-state projection and compressed Hamiltonian

Set A=g†i, P=|A|², Q=I−gg†, q=Qi, W=q†q, u=q/sqrt(W). Normalize working copies of i and g to remove serialization roundoff and record those corrections. Retain original arrays. For the saved Be+ electronic Hamiltonian H and saved daughter reference energy E0, define B=H−E0 I and K=QBQ on Ran(Q). Thus K is Hermitian, even though g is only an approximate eigenvector. Every Hamiltonian action is wrapped with Q on both sides.

The spectral measure to compute is

    dν(ω) = W <u, δ(ω−K)u> dω,
    ν(R)=W,  μ_j=<u,K^j u>,  m_j=W μ_j.

This is a finite-space, ground-projected daughter excitation diagnostic. The spectrum's nodes have units Eh and its weights are dimensionless probabilities. The conditional measure dν/W has mass one. W includes all unresolved excitation represented by q. A chosen energy cut labels a finite spectral tail; it does not identify a physical ionization channel.

The finite-model Stieltjes transform is G(z)=W<u,(zI−K)^−1u>, Im z>0. For z=ω+iη, Sη(ω)=−Im G(z)/π has units Eh^−1 and is a Lorentzian-broadened spectral diagnostic. Its integral over all real ω is W. Broadening and a finite display window are explicit diagnostics; no renormalization to that window is performed.

## Information already available without new integrals

The archived receipt gives E0, h=<i,Hi>, h2=||Hi||² and residual bound ε=||(H−E0)g||. Hence

    d=h−E0,  s=h2−2 E0 h+E0².

If g were an exact eigenvector, μ1=d/W and μ2=s/W. Use the following conservative bounds instead of silently making that assumption. Write r=Bg and i=A g+sqrt(W)u. Direct expansion gives

    d=P<g,r>+2 sqrt(W) Re[A*<r,u>]+W μ1.

Therefore

    |d−W μ1| <= ε(P+2 sqrt(PW)).

The triangle inequality applied to Bi=A r+sqrt(W)Bu gives

    L=max(0,sqrt(s)−sqrt(P)ε)/sqrt(W),
    U=(sqrt(s)+sqrt(P)ε)/sqrt(W),
    L <= ||Bu|| <= U.

Since ||Ku||²=||Bu||²−|<g,Bu>|² and <g,Bu>=<r,u>,

    max(0,L²−ε²) <= μ2 <= U².

These are residual-aware bounds for the compressed operator, conditional on the recorded Hamiltonian moments/residual and up to their numerical rounding. Set a=(d−ε(P+2sqrt(PW)))/W and b=(d+ε(P+2sqrt(PW)))/W. Let c=max(0,L²−ε²), e=U². Then a conservative variance enclosure is

    max(0,c−max(a²,b²)) <= Varν/W(ω)
        <= e−min_{x in [a,b]} x².

The right side should be nonnegative; a materially negative value diagnoses inconsistent input evidence. The lower-side clamp uses the mathematical positivity of variance, not an altered input moment. No byte identity is required for rederived floating-point scalars.

For any declared finite-model cut t>b, Cantelli's inequality gives

    ν([t,∞)) <= W v_upper/[v_upper+(t−b)²].

This needs no nonnegative-support assumption. Report cuts 5, 10 and 20 Eh as diagnostic excitation-energy cuts only. The bounds are mathematically valid for the finite compressed measure given the stated input evidence; they do not provide outgoing-channel probabilities.

Actual scalar evaluation of the recovered receipt gives d=1.1322839238743185 Eh and s=10.27623750986777 Eh². Exact-eigenvector-limit values are μ1=2.668210343338318 Eh, μ2=24.215801917076284 Eh² and variance 17.0964554807787 Eh²; the implementation must report the conservative residual-aware intervals above beside these estimates. The archived residual ε=3.189816242358533e−8 Eh makes these interval corrections small but explicit. Independent array calculation supplies P and W rather than trusting a displayed decimal.

## Nested Lanczos / Stieltjes construction

Start v1=u. For j=1,...,m compute z=K vj, αj=vj†z, and subtract αj vj and β(j−1)v(j−1). Project off g, then perform two full modified-Gram-Schmidt passes against all retained vectors, and project off g again. The norm of the remainder is βj; if it is below the frozen relative breakdown threshold, record happy breakdown rather than divide by it. Otherwise normalize it to obtain v(j+1).

Cache each Kvj along with vj. At a milestone form the actual small matrix C=V†KV, record its anti-Hermitian defect, and diagonalize J=(C+C†)/2. This explicit projected matrix avoids silently discarding finite-precision reorthogonalization corrections. In exact arithmetic J is the familiar tridiagonal Lanczos matrix. Record the off-tridiagonal defect as a diagnostic; it is not a new physical approximation.

For JY=Y diag(θ), quadrature weights are w_l=W|Y(1,l)|². They are nonnegative and sum to W. The discrete approximation is ν_m=Σ_l w_l δ(ω−θ_l); G_m(z)=Σ_l w_l/(z−θ_l). The analytic broadened CDF is

    Fη(x)=Σ_l w_l [1/2+atan((x−θ_l)/η)/π].

Use this CDF to retain tails and window mass. Do not equate integral of a sampled finite-window spectrum with total probability.

For m>=2, the first three discrete moments are compared against the direct vector moments W, W<u,Ku> and W||Ku||². These direct moments need only one action on u and provide a local scientific check distinct from comparison of two quadrature lengths. Krylov extension reuses the same basis; it never reruns the saved ground-state solve.

A Ritz value is not an exact excitation energy merely because its weight is present. For the six largest-weight nodes, explicitly compute residuals ||KV y_l−θ_l V y_l|| from cached actions, and ground leakage |g†V y_l|. Record these residuals without requiring every finite-step Ritz vector to satisfy the ground-state solver tolerance. Broadening-dependent refinement is assessed separately.

## Reconstruction and error sources

Build Be+ at the origin from the receipt's actual expanded common shell list (not a fresh named-basis lookup), with the saved X. Recompute S, h=X†(T+V_Be)X and ERI through the same PySCF conventions used in V6 `quench`. The two-electron AO integrals depend on the common AO functions and not the nuclear charge. Use the V6 `raw_action` route with triangular occupation-list links; it applies the original electronic Hamiltonian with the same determinant order. No SCF, FCI eigensolve or new metric diagonalization is needed.

Input/model error: inherited finite Gaussian basis, fixed point nucleus and nonrelativistic Hamiltonian. State error: recorded/recomputed ground residual and saved projection. Arithmetic/reconstruction error: orbital metric, reproduced energy/moments and Hermiticity. Krylov error: milestone spectra and broadened refinement. Window/broadening choice: explicit diagnostic display and transform. These remain separate; a successful internal spectral calculation does not turn basis or outgoing-boundary obligations into completed tasks.
