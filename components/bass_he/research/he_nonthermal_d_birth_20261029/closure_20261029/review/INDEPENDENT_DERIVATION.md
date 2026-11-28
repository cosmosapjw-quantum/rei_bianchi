# Independent R6 derivation, 2026-10-29

Reviewer: `/root/independent_he_review`. This is a separate subagent review, not a claim of a distinct model. The source modules and tests were read before three targeted input probes; the previous 28-test suite was not rerun. All 15 source-manifest entries matched exact bytes, size and SHA-256.

Write A=m_He c², M=m_D c² and ε=E_gamma, retaining these as energy variables. In the local He target-rest frame with metric (-,+,+,+), the total four-momentum has energy A+ε and momentum ε n/c. Hence s=-c² P_aP^a=A²+2Aε. The two-D channel is kinematically allowed when s>=4M², or ε>=(4M²-A²)/(2A). The frozen 330 MeV input lies above that threshold. This is a kinematic statement; it supplies no cross section or actual event rate.

The CM daughter energy and energy-scaled momentum are E*=sqrt(s)/2 and q=p*c=sqrt(s/4-M²). Boosting with beta=ε/(A+ε), gamma=(A+ε)/sqrt(s), and mu the cosine between the first CM daughter and n gives E_plus/minus=E0 +/- B mu, where E0=(A+ε)/2 and B=ε q/sqrt(s). The kinetic energies are K_plus/minus=K0 +/- B mu with K0=E0-M. Thus K0 is the arithmetic mean of the two daughter lab kinetic energies in each event, and is the mean of either label if the label law is even. The exact pair kinetic total is 2K0. Calling each daughter monoenergetic with K0 would be incorrect.

An exclusive event density rate R has units m^-3 s^-1 in this local frame. Its count sources (-R,2R,-R) for He,D,gamma preserve baryon number -4R+2(2R)=0 and charge -2R+2R=0. Its rest, daughter kinetic and photon energy sources sum to [-A+2M+2K0-ε]R=0. Photon momentum loss is -ε R n/c and the daughter total momentum source is the opposite. Multiplication by 1MeV=1.602176634e-13J converts an energy source to J m^-3 s^-1 and momentum source to kg m^-2 s^-2=N m^-3. Missing R remains undefined; manufactured R only tests this conditional map.

For a number distribution f(p) defined per d³p, the spatial stress tensor is P_ij=Integral p_i p_j c²/E(p) f(p) d³p. For a newborn pair the trace mark is therefore

T(mu)=Sum_plus/minus[(p_plus/minus c)²/E_plus/minus]
     =2E0-M²(1/E_plus+1/E_minus)
     =2E0-2M²E0/(E0²-B² mu²).

This mark has energy units. R<E[T]> is a collision gain contribution to the time derivative of the stress trace, with units J m^-3 s^-1; it is not a static pressure. Scalar isotropic pressure would be one third of the trace, after the distribution and any loss/transport terms are specified. No isotropy is used here.

Set x=mu² in [0,1], a=E0² and b=B². Physical daughter energies ensure 0<=b<a; at the frozen input b>0. Direct differentiation gives T''(x)=-4M²E0 b²/(a-bx)³<0. The graph of T is concave, so its endpoint chord is below T and Jensen gives <T><=T(<x>). With m=<x>,

(1-m)T(0)+mT(1) <= <T(x)> <= T(m).

These are exactly the implemented lower and upper expressions. Their gap is 2M²E0 b²m(1-m)/[a(a-b)(a-bm)]>=0. This proof only needs a nonnegative probability measure and its second angular moment, not evenness. Even sharpness witnesses are available: mu=+/-sqrt(m) with half weights attains the upper bound; mu=0 with weight1-m and mu=+/-1 with weightsm/2 attain the lower. At m=0 or1 the gap vanishes. At b=0 (threshold/zero boost limit) T is constant. Sharpness over this probability-measure class does not establish sharpness within a sextic-polynomial family.

No new strong no-go is admitted. This is a direct conditional moment enclosure and its computational consequences; literature novelty was not assessed by this review.

The next weak kinetic-source construction is useful. For a normalized CM event-mark law W and f_D per d³p, define its gain by Integral psi(p) C_gain(p)d³p=R Integral[psi(p_plus)+psi(p_minus)]W(dOmega). Testing psi=1, p, E yields the required 2R, εRn/c and (A+ε)R; testing p_i p_jc²/E gives the actual stress gain. R counts an unordered exclusive pair once, so no extra factor1/2 belongs in this gain: an identical-particle convention must already be contained in the event cross section. This construction can be completed conditionally while R and W remain missing physical inputs; physical pool admission remains a separate unresolved obligation.
