(* THEORY05 primitive author: exact gamma-law recovery, derivative identities,
   binding-aware finite increments and warm HI-only absorption references.
   Each named group is counted once. Global positivity and uniqueness are
   proved in PRIMITIVE_RECOVERY_AND_EXAMPLES.md, not inferred from fixtures.
   No numerical root solve, scan, ODE, native code or atomic-rate refit. *)
ExportString[
 Module[
  {put, checks = <||>, residuals = <||>, begin, rr,
   ar, cap, ss, dH, z, totE, q, pp, alpha, b2,
   gm = 5/3, kap = 2/3, ww, ee, nn, th, pres, gam, vel,
   ass, nder, e0, gap, fpress, cpress, upperAtQ, wforward,
   mx, my, mz, jx, jy, jz, labInc, bindInc, mvec, jvec,
   initialR, theta0, r0, eta, xi, energyPhoton, ionEnergy,
   rap, ratio, den, ell, thetaPlus, rPlus, gamPlus, velPlus,
   eosE, eosM, d0, kb, ev, tzero, thetaPrime, velPrime,
   cLight, neutralFrac, sig, lambdaA, lambdaB,
   step, count, incoming, outgoing, pairTheta, texc,
   exactEv, exactKb, chiH, exactTexc, heatMargin,
   exprEnergy},
  begin = AbsoluteTime[];
  put[name_, expr_, assumptions_:True] := Module[{v},
   v = (FullSimplify[Together[#], Assumptions -> assumptions] & /@
       Flatten[{expr}]);
   AssociateTo[checks, name -> And @@ (TrueQ[# === 0] & /@ v)];
   AssociateTo[residuals, name -> (ToString[InputForm[#]] & /@ v)];
  ];

  ass = ar > 0 && cap >= ar && ss >= 0 && dH > 0;
  ww = Sqrt[cap^2 + ss];
  ee = (3 cap^2 + 2 ar cap + 5 ss)/(5 ww);
  gam = ww/cap;
  nn = dH cap/ww;
  th = 3 (cap-ar)/(5 dH);
  pres = 2 cap (cap-ar)/(5 ww);
  vel = Sqrt[ss]/ww;
  put["primitive_forward_recovery",
   {nn gam-dH, gam^2 (1-vel^2)-1,
    kap nn th-pres,
    nn (ar/dH+gm th) gam^2-pres-ee,
    nn (ar/dH+gm th) gam^2 vel-Sqrt[ss]}, ass];

  nder = 3 cap^3+cap ss+2 ar ss;
  put["energy_first_derivative",
   D[ee,cap]-nder/(5 (cap^2+ss)^(3/2)), ass];
  put["energy_second_derivative",
   D[ee,{cap,2}]-ss (7 cap^2-6 ar cap+ss)/
     (5 (cap^2+ss)^(5/2)), ass];
  put["inverse_parameter_derivatives",
   {D[ee,ss]-(7 cap^2-2 ar cap+5 ss)/(10 ww^3),
    D[ee,ar]-2 cap/(5 ww),
    D[ee,cap] (5 ww^3/nder)-1,
    D[ee,cap] (-(7 cap^2-2 ar cap+5 ss)/(2 nder))+D[ee,ss],
    D[ee,cap] (-2 cap ww^2/nder)+D[ee,ar]}, ass];

  e0 = Sqrt[ar^2+ss];
  gap = z (6 ar+z)/(5 (Sqrt[(ar+z)^2+ss]+e0))+
    2 z^2 (ar+z) (2 ar+z)/
      (5 Sqrt[(ar+z)^2+ss] (Sqrt[(ar+z)^2+ss]+e0)^2);
  put["positive_term_gap",
   gap-((ee /. cap->ar+z)-e0), ar>0 && z>=0 && ss>=0];
  put["gap_boundary_slope_and_rest_limit",
   {gap /. z->0,
    (D[ee,cap] /. cap->ar)-3 ar/(5 e0),
    (ee /. ss->0)-(3 cap+2 ar)/5,
    (gap /. ss->0)-3 z/5}, ar>0 && cap>=ar && z>=0 && ss>=0];

  cpress = Sqrt[q^2-ss];
  fpress = q-totE-(2/5) (q-ss/q-ar Sqrt[1-ss/q^2]);
  put["pressure_root_and_derivative",
   {fpress-(3 q^2-5 totE q+2 ss+2 ar cpress)/(5 q),
    D[fpress,q]-(3-2 ss/q^2+2 ar ss/(q^2 cpress))/5},
   ar>0 && ss>=0 && q>Sqrt[ss]];
  upperAtQ = fpress /. totE->(3 q+2 ar)/5;
  put["pressure_upper_bracket_factorization",
   upperAtQ-2 (q-cpress) (q+cpress-ar)/(5 q),
   ar>0 && ss>=0 && q>Sqrt[ss]];

  wforward = ar/Sqrt[1-b2]+alpha pp/(1-b2);
  put["forward_jacobian_positive_factor",
   wforward^2 ((D[wforward,pp]-1) wforward
     -2 b2 D[wforward,b2])-
    wforward^2 (ar (alpha-1)/(1-b2)^(3/2)+
      alpha pp ((alpha-2)/(1-b2)^2+1/(1-b2))),
   ar>0 && pp>=0 && 0<=b2<1 && alpha>=2];

  mvec = {mx,my,mz}; jvec = {jx,jy,jz};
  put["causal_increment_margin",
   (totE+labInc)^2-Total[(mvec+jvec)^2]-(ar+bindInc)^2-
    (totE^2-Total[mvec^2]-ar^2+
      2 (totE labInc-mvec.jvec)+labInc^2-Total[jvec^2]
      -2 ar bindInc-bindInc^2)];
  initialR = r0+theta0;
  put["single_beam_rest_binding_margin",
   (initialR+energyPhoton xi)^2-(eta energyPhoton xi)^2-
    (r0+ionEnergy xi)^2-
    (theta0 (2 r0+theta0)+
      2 xi (initialR energyPhoton-r0 ionEnergy)+
      ((1-eta^2) energyPhoton^2-ionEnergy^2) xi^2)];

  den = rap^2+5+2 ratio rap (rap^2-1);
  ell = (rap^2-1) (5 (rap^2+1) initialR-4 rap r0)/(2 den);
  thetaPlus = 3 (rap^2+1) (initialR (rap-ratio (rap^2-1)/2)-r0)/den;
  rPlus = r0+ratio ell;
  gamPlus = (rap^2+1)/(2 rap);
  velPlus = (rap^2-1)/(rap^2+1);
  eosE = (rPlus+gm thetaPlus) gamPlus-kap thetaPlus/gamPlus;
  eosM = (rPlus+gm thetaPlus) gamPlus velPlus;
  put["single_beam_rational_endpoint",
   {eosE-initialR-ell,eosM-ell,
    thetaPlus-(rap initialR-r0-ratio ell)/(1-kap velPlus)}];

  lambdaA = cLight (dH/gamPlus) neutralFrac sig/rap;
  lambdaB = cLight dH neutralFrac (1-velPlus) sig;
  put["single_beam_norm_doppler_dilution",
   {gamPlus^2 (1-velPlus^2)-1,
    gamPlus (1-velPlus)-1/rap,
    (dH/gamPlus) gamPlus-dH,lambdaA-lambdaB}];
  thetaPrime = (D[thetaPlus,rap]/(D[ell,rap]/energyPhoton)) /. rap->1;
  velPrime = (D[velPlus,rap]/(D[ell,rap]/energyPhoton)) /. rap->1;
  put["single_beam_small_fluence_derivatives",
   {(ell /. rap->1),(thetaPlus /. rap->1)-theta0,
    (D[ell,rap] /. rap->1)-(r0+gm theta0),
    thetaPrime-energyPhoton (1-ratio),
    velPrime-energyPhoton/(r0+gm theta0),
    ((D[2 thetaPlus/(3 kb (d0+ell/energyPhoton)),rap]/
       (D[ell,rap]/energyPhoton)) /. rap->1)-
      2 (energyPhoton (1-ratio)-theta0/d0)/(3 kb d0)}];
  put["single_beam_positive_factorization",
   {5 (rap^2+1) initialR-4 rap r0-
       rap (6 r0+10 theta0)-5 initialR (rap-1)^2,
    D[rap-ratio (rap^2-1)/2,rap]-(1-ratio rap),
    ((rap-ratio (rap^2-1)/2) /. rap->1)-1}];

  incoming = count (1+step lambdaA)/(step lambdaA);
  outgoing = count/(step lambdaA);
  put["endpoint_BE_inventory_event",
   {outgoing-incoming/(1+step lambdaA),
    step lambdaA outgoing-count,incoming-outgoing-count}];

  pairTheta = theta0+(energyPhoton-ionEnergy) xi;
  texc = 2 (energyPhoton-ionEnergy)/(3 kb);
  put["paired_exact_energy_temperature",
   {r0+ionEnergy xi+pairTheta-initialR-energyPhoton xi,
    2 pairTheta/(3 kb (d0+xi))-
      (d0 (2 theta0/(3 kb d0))+texc xi)/(d0+xi)}];

  exactEv = 1602176634/10^21;
  exactKb = 1380649/10^22;
  chiH = 13598434599702/10^12;
  exactTexc = 2 exactEv (23-chiH)/(3 exactKb);
  heatMargin = 23-chiH-3 exactKb 50000/(2 exactEv);
  put["warm_23ev_exact_margins",
   {If[50000<exactTexc<110000,0,1],
    If[heatMargin>0,0,1],
    If[chiH<1360/100<23<2459/100<50000,0,1]}];

  <|"schema"->"theory05_primitive_exact_checks_v1",
    "unit"->"HERE_RUX03_MOVING_GAS_SOURCE_05",
    "role"->"Primitive proof author; not independent decision reviewer",
    "method"->"Exact Wolfram Language differentiation, rational identities and exact decimal-as-rational warm-fixture inequalities",
    "kernel"-><|"version"->$Version,"system_id"->$SystemID,
       "machine_precision"->$MachinePrecision|>,
    "elapsed_seconds"->N[AbsoluteTime[]-begin],
    "check_count"->Length[checks],
    "checks"->checks,"residuals"->residuals,
    "all_pass"->And@@Values[checks],
    "warm_reference"-><|
      "lab_photon_energy_ev"->23,"initial_temperature_k"->50000,
      "HI_binding_ev_exact"->ToString[InputForm[chiH]],
      "HI_activation_ev_exact"->ToString[InputForm[1360/100]],
      "epsilon_erg_per_ev_exact"->ToString[InputForm[exactEv]],
      "kb_erg_per_k_exact"->ToString[InputForm[exactKb]],
      "T_exc_k_exact"->ToString[InputForm[exactTexc]],
      "T_exc_k_decimal_20"->ToString[InputForm[N[exactTexc,20]]],
      "initial_temperature_slope_bracket_ev_exact"->ToString[InputForm[heatMargin]],
      "initial_temperature_slope_bracket_ev_decimal_20"->ToString[InputForm[N[heatMargin,20]]],
      "scope"->"Absorption-only HI channel reference; full FT03 rates remain the adopted physical model outside this reference"|>,
    "new_native_or_ODE_executions"->0,
    "reexecution_of_previous_units"->0|>
 ],
 "RawJSON"
]
