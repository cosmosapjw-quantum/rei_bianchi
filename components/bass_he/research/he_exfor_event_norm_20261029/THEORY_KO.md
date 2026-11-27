# HE_EXFOR_IDENTICAL_D_EVENT_NORMALIZATION: source-locked conditional angular bounds

## Source authority and conventions

Child of `BASS_HE` PR104 HEAD `89325f8510d2af3abe675326720068d0693845b8`. Existing central 28/88, HE 14/18 and predecessor conditional 2/2 are unchanged. Source: `IAEA-NDS/exfor_master@939a14d7bba1ddce51975cb5e8711ce96b3b0871:exforall/M04/M0475.x4`, Git blob `c49433293921dbb012d7f1b0387745732a598efa`, SHA256 `b2c1c52931e813dd63fb0e98edfc90088bc2eca497fd9142277e748f0935a82f`. Local bytes match both identities.

Arends et al., Phys. Lett. B 62 (1976) 411–412, DOI 10.1016/0370-2693(76)90671-7. EXFOR M0475002 lists 330 MeV CM polar DA at 46,61,73,87 degrees: 0.14±0.03, 0.16±0.05, 0.07±0.05, 0.19±0.05 nb/sr. ERR-S is statistical only. M0475003 SIG: 320 MeV 0.61±0.16 nb, 359 MeV 0.55±0.15 nb; no 330 MeV total. COINC/TOF with two outgoing D arms is recorded but full-sphere event/inclusive convention is not explicitly established by this source text.

## Conditional mathematical problem

Assume the reported DA is a nonnegative azimuthally averaged polar function f(theta) symmetric under identical-daughter exchange theta→pi−theta. This is an extra assumption on the experimental representation, not a claim of a unique measured full law. Work on theta in degrees [0,90] and impose an *externally declared* global Lipschitz L≥0 in nb/sr/degree. At measured theta_i, use literal coordinate sensitivity intervals [ell_i,u_i]=[max(0,DA_i−ERR-S_i),DA_i+ERR-S_i]. These are NOT simultaneous statistical confidence intervals and omit unprovided systematic errors/covariance.

**Sharp feasibility lemma.** A nonnegative L-Lipschitz interpolant meeting all interval constraints exists iff

    L ≥ L_min = max_(i≠j) ((ell_i−u_j)_+)/|theta_i−theta_j|.

Necessity follows from f(theta_i)≥ell_i, f(theta_j)≤u_j and the Lipschitz inequality. For sufficiency define

    f_-(theta) = max(0, max_i[ell_i−L|theta−theta_i|]),
    f_+(theta) = min_i[u_i+L|theta−theta_i|].

Both are L-Lipschitz, satisfy the pointwise intervals whenever L≥L_min, and f_-≤f_+. Every feasible f is bounded between them. Because f_- and f_+ themselves are feasible, the pointwise and any nonnegative-weight integral bounds are sharp within this class. This is not proof that either extremal is a physically realized nuclear angular law.

For the source 330 MeV rows, L_min=1/700 nb/sr/degree exactly, from 87° lower0.14 and 73° upper0.12 separated by14°. For exact central values L_min,central=3/350 nb/sr/degree. These are mathematical source-coordinate constraints, not measured derivatives.

**Sharp angular integral.** With the declared polar/azimuth and identical-D symmetry,

    I[f] = ∫_(S²) f(theta) dOmega
         = 4 pi (pi/180) ∫_0^90 f(theta_deg) sin(pi theta_deg/180) dtheta_deg [nb].

Then I[f_-]≤I[f]≤I[f_+] with both endpoints attainable in the declared class. Each envelope is piecewise affine with exact rational breakpoints, and

    ∫ (a+b theta) sin(k theta) dtheta
      = −(a+b theta)cos(k theta)/k + b sin(k theta)/k², k=pi/180.

Fraction arithmetic yields exact breakpoints/affine coefficients; the sine/cosine evaluation is high-precision numerical, not a certified outward-rounded interval. Without an angular regularity bound, finite pointwise samples alone allow arbitrarily narrow positive spikes with arbitrarily small integral and arbitrarily large nonnegative bumps away from measured angles. This is a restricted mathematical nonidentifiability, not a global physical no-go.

## Event/particle convention and source

If f is inclusive single-D full-sphere DA, I=2 sigma_event. If f is a randomly oriented one-D-per-event full-sphere DA, I=sigma_event. Both are hypothetical, not assigned to EXFOR. Actual event/particle multiplicity, coincidence efficiency, half/full-sphere normalization, polarization and target response remain unresolved. With stationary He4 target density n_He[m^-3], monochromatic photon number flux Phi_330[m^-2 s^-1], sigma_event[m²], the algebraic source R_event=n_He Phi_330 sigma_event[m^-3 s^-1] uses 1nb=10^-37m². No physical R_event without source-qualified convention, actual photon history and target-frame collision kernel. Fast-D kinetic gain and thermal stopping/deposition/Cv are separate owners. Activation=false, L4=false, production=HOLD.

The predecessor PR104 exact conditional two-D weak gain, energy bins and full-sextic-law stress trace are unchanged. HE-EXP-EXFOR11's positive Bernstein-family certificates use a different declared class and are neither overwritten nor contradicted by the Lipschitz construction. New conditional 2/2 nodes are not physical DAG nodes.
