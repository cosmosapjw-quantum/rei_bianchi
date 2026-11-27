# Conditional kinetic birth gain and full-law stress trace

## Definition, conventions and reused inputs

Use a local He4 target-rest orthonormal frame, signature(-,+,+,+), proper time t, nuclear rest energies A=3727.3794118MeV and M=1875.612945MeV, incident photon energy ε=330MeV. These are frozen inputs, not a new mass evaluation. Let s=A²+2Aε, q*=sqrt(s/4-M²) [MeV=p*c], β=ε/(A+ε), γ=(A+ε)/sqrt(s). The channel is open when ε≥(4M²-A²)/(2A). Define E0=(A+ε)/2, K0=E0-M and B=εq*/sqrt(s)>0. At threshold B=0 the energy pushforward degenerates to a delta at K0; this unit's frozen330MeV input is above threshold.

For incident direction n, an oriented CM mark u with μ=u·n gives

    E±=E0±Bμ,
    c p±=±q*(u-μn)+(ε/2±γq*μ)n,
    K±=K0±Bμ.

Each daughter satisfies E±²-|cp±|²=M². Their sum is E++E-=A+ε and c(p++p-)=εn. K0 is the mean lab kinetic energy per daughter for an even mark law; the pair kinetic energy is2K0 for every event. Directional energy splitting is retained.

## Weak source and exclusive-event multiplicity

Let R be exclusive unordered events/(m³ s), with ∫W(dΩ)=1 an oriented CM mark probability. Define f_D by dN=f_D d³x d³p in this local frame, and define only its collision gain C_D, without expansion/streaming/stopping:

    ∫ψ(p) C_D(p) d³p = R ∫[ψ(p+(Ω))+ψ(p-(Ω))] W(dΩ).

This defines a positive measure even when no ordinary density exists. Relabeling Ω→-Ω exchanges the two daughters and leaves the gain invariant. No evenness assumption is needed for this invariance, nor is an extra1/2 applied after R has counted each exclusive event once. Event/particle and identical-state normalization belong to the experimental cross-section convention; they remain unbound for physical admission here.

Test functions1,p,E give number gain2R, total momentum gainRεn/c and total energy gainR(A+ε). Subtracting two rest energies gives kinetic gain2RK0. Add the He4 loss-R, photon loss-R and their rest/energy/momentum changes to recover total baryon, charge, energy and momentum conservation. Multiply MeV by1.602176634×10^-13J for SI. The gain is not a fast-to-thermal transfer; thermal heat requires its own stopping/deposition operator.

## Exact energy-bin computational form

Choose the predecessor's conditional even sextic family

    q(μ)=(1-μ²)(a0+a1μ²+a2μ⁴)/Z,
    Z=4a0/3+4a1/15+4a2/35>0,
    a0+a1z+a2z²≥0 for0≤z≤1.

q is a probability density per dμ after azimuthal marginalization. It is a selected reference law, not the unique law inferred from four measured angles. At fixed ε its energy marginal is independent of the unresolved azimuthal distribution. For x=(K-K0)/B, the inclusive per-event density is g(x)=q(x)+q(-x)=2q(x), -1≤x≤1. Equivalently dN/(dK per event)=2q((K-K0)/B)/B.

For a partition -1=x0<...<xJ=1, store binned reduced moments

    G_j^(k)=2/Z Σ_(l=0,2,4,6) c_l [x_(j+1)^(l+k+1)-x_j^(l+k+1)]/(l+k+1),
    (c0,c2,c4,c6)=(a0,a1-a0,a2-a1,-a2).

All values are rational for rational coefficients and reduced edges. Number isG_j^(0), kinetic energy isK0G_j^(0)+BG_j^(1), and centered second energy moment isB²G_j^(2). Keeping reduced first moments avoids rounding B in conservation checks. Across the full partition ΣG^(0)=2, ΣG^(1)=0, ΣG^(2)=2m2, hence total kinetic2K0 exactly. Number-weighted midpoint assignment would replaceG^(1) and need not conserve energy on an asymmetric partition; retain the integrated first moment. The full vector source still requires W(dΩ), which the scalar energy marginal does not determine.

The frozen FULL witness is(a0,a1,a2)=(1411/10000,-1/4,33/25), read directly from the predecessor saved candidate. It yields m2=24377/71485. Arbitrary even moments are

    m_(2k) = 2/Z Σ_(l=0,2,4,6)c_l/(l+2k+1).

## Full-law finite-mass trace enclosure

The per-event kinetic stress trace is

    T(μ)=Σ±(c p±)²/E±=2E0-2M²E0/(E0²-B²μ²).

It has energy units. After multiplication by R it is the collision gain of tr(P), in J m^-3 s^-1, not a static pressure. Set r=B²/E0²∈(0,1), D=2M²/E0 and x=μ²∈[0,1]. Then

    E[T]=2E0-D E[(1-rx)^-1],
    S_N=Σ_(k=0)^N r^k m_(2k),
    E[(1-rx)^-1]-S_N = r^(N+1) E[x^(N+1)/(1-rx)].

For a nonnegative integer N, since1≤1/(1-rx)≤1/(1-r), the positive remainder lies between r^(N+1)m_(2N+2) and that value/(1-r). Therefore

    L_N=2E0-D[S_N+r^(N+1)m_(2N+2)/(1-r)],
    U_N=2E0-D[S_N+r^(N+1)m_(2N+2)],
    U_N-L_N=D r^(N+2)m_(2N+2)/(1-r).

L_(N+1)-L_N=D r^(N+2)(m_(2N+2)-m_(2N+4))/(1-r)≥0 and U_N-U_(N+1)=D r^(N+2)m_(2N+4)≥0. The intervals are nested and their widths contract by at most r. This is an exact rational truncation bound; arithmetic roundoff is absent in the Fraction lane. Exported decimal centers are illustrative approximations to rational intervals. No optimality over the family is claimed.

At N=0 the raw upper endpoint exceeds the Jensen upper by D r² m2²/(1-r m2). Return the intersection[max(L_N,L_J),min(U_N,U_J)] with the universal interval, while preserving the raw endpoints and remainder width. This intersection is nested and cannot widen the universal bound. At threshold r=0 the constant trace is handled separately; the energy density formula with1/B is used only above threshold.

The predecessor m2-only Jensen/secant interval remains valid for every nonnegative law with that moment. The intersected full-law interval conditions on the whole selected sextic law. Its added information is explicit; it does not turn the fitted witness into a measured full angular law.

## Literature, data and physical admission

Rice et al., PRC61,064612(2000), DOI10.1103/PhysRevC.61.064612 measures150–250MeV and supplies no330MeV normalization. IAEA EXFOR M0475002 from Arends et al., Phys.Lett.B62(1976), DOI10.1016/0370-2693(76)90671-7 contains actual330MeV DA at46,61,73,87deg CM. Its provenance is already pinned by WU source contract to IAEA-NDS/exfor_master@939a14d7bba1ddce51975cb5e8711ce96b3b0871. Sparse DA values, separately tabulated integrated SIG at different energies, and a normalized full law are distinct inputs. Event normalization, photon history, target-state mapping, uncertainty/covariance and named physical fast-D pool/stopping remain unresolved. R=null, activation=false, L4=false, production=HOLD.
