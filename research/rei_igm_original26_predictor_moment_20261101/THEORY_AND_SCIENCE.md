# Original REI 26-event MPRK predictor: shared photon moment derivatives

Source: frozen original first-canonical-interval tick 160, 46080 nodes and 26-event source in rei_bianchi. Original source archive SHA256 a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b. Original accepted state SHA256 cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01. Original interval map Git blob ca2676c84b3c93766c59aa3ef81740565226dad9. Base immutable PR #337 includes the exact frozen original code; PR #332 established three shared neutral moments; PR #338-342 already derive the source-only finite remainder. This is NOT another source-only remainder computation.

## Actual new implicit physical operator

The original predictor population-step at one frozen H/He source parent is a positive block-diagonal implicit linear system

  A(p,T,S;h) y = p

where A has separate H 2x2 and He 3x3 MPRK blocks. Its off-diagonal entries are minus h times the original event-box source-to-destination rates divided by the original source-species parent population; each diagonal adds all the corresponding outgoing transfers. All original event-box rates are retained: H/He photoionization, collisional ionization, recombination and original OTS/branching feedback. At the chosen actual source point, A is a representative in the ORIGINAL interval MPRK matrix enclosure; y must lie inside the ORIGINAL Krawczyk population-step certificate.

Let three nonnegative global neutral sums be S_k=sum_i p_{ik}, with k=HI,HeI,HeII. Original four photon currents J_g and original photoionization source rates r_isg=J_g C_sg p_is / (E_g+sum_k C_kg S_k). Define q_kg=C_kg S_k/(E_g+sum_t C_tg S_t). Holding the local population numerator, original 26-event non-photo fluxes, forcing and source temperature fixed, derive exact derivatives for the independent LOG global source-moment coordinates ell_k=ln S_k:

  d_k r_isg = -r_isg q_kg
  d_kl r_isg = r_isg (2 q_kg q_lg - delta_kl q_kg).

At fixed MPRK parent denominators, A is linear in the event rates. Hence the *exact conditional derivatives* A_k and A_kl are obtained from r_k and r_kl using equal-and-opposite destination and source columns, preserving hydrogen and helium nuclear inventories.

The new derived predictor responses are

  y_k = -A^{-1} A_k y
  y_kl = -A^{-1} (A_kl y + A_k y_l + A_l y_k).

These propagate the established photon-source global susceptibility through the ACTUAL original 2x2+3x3 implicit MPRK predictor. They are not the original SDIRK thermal roots, MPRK corrector or full-minus-two-half D_h. They must not be identified with the total derivative under a physically realizable global perturbation because that would also change the local numerator and other collisional/OTS rates. That separate direct term is a known uncompleted obligation.

## Exact finite conditional test

For a log-moment delta vector the original photon-source denominator obeys

  D_g(delta)/D_g(0) = 1 + sum_k q_kg expm1(delta_k).

Keeping all other local event rates fixed, replace the three original photoionization transfers inside A by their source exact finite response. An independent batched 2x2+3x3 matrix solve yields the exact conditional predictor y(delta). Compare to y(0)+J delta+0.5 H[delta,delta] at five selected points inside the ORIGINAL marginal global three-moment bounds. The five samples diagnose but DO NOT rigorously bound the entire moment box. No opacity perturbation causes a new cosmological IVP; it is a single implicit predictor at frozen original clock.

## Original physics delivered by real source execution

46,080 original source-conditioned predictor rows with xHII, xHeII, xHeIII, free electrons per H, one-tick delta xe, fixed-T thermal and ionization binding energy, three logarithmic source-moment first derivatives and nine electron second derivatives. Compare the original interval Krawczyk enclosure against the chosen representative. Check H/He nuclear conservation at state, first and second derivative levels, positivity under exact conditional finite source perturbation, source fraction normalization, fixed gate identities, no table-owner mutation. Output CSV and comprehensive JSON are artifacts, not a new global IVP.

## Adversarial limitations

1. Independently enclosed 26-event flux midpoints are an interval-model representative; they need not be a jointly realized physical reaction history. This output is SOURCE_CONDITIONAL.
2. Global source log moments varied at fixed local population are *formal independent coordinates*, not automatically dynamically reachable shared electron/ion population perturbations. The full parent derivative includes the local numerator term and derivatives of other original events.
3. The source and MPRK predictor Hessian are not an entire-X rigorous interval/taylor remainder for the original 26-event four-site full-half difference D_h. At that next level include MPRK predictor/corrector, SDIRK thermal roots, branch events, four source sites per map, parent/forcing correlation and global 46k coupling.
4. The 3 shape lanes share numerically identical original 46,080-node accepted states; avoid multiplying independent observed data.
5. Original rejected one-tick full-X 2.1245050576368385e-4 > strict 2e-4 and original public width 2e-3 remain LOCKED, with first interval 160/131072 accepted. No main merge, production, force push or tolerance reset.

REI original central 28/88 REPORTED, working 33/88, Physical Fast 4/7, canonical delta 0 for all R1-R10 and C1-C10 receipts. One scientific unit, not 20 physics nodes. No external-author review or native subagent where tools are unavailable.

Related literature: Izgin Kopecz Meister, A Stability Analysis of Modified Patankar–Runge–Kutta methods for a nonlinear Production–Destruction System, PAMM 2022, DOI 10.1002/pamm.202200083. Wilczak and Zgliczynski, C^r-Lohner algorithm, arXiv:0704.0720, motivates shared interval derivatives but does NOT certify the original REI algorithm.
