(* THEORY06: exact source-pinned coefficient/first-derivative envelopes.
   No native RHS, ODE, trajectory, parameter scan or prior-unit checks.
   N[...,80] proposes rational-power brackets; exact power inequalities certify them.
   Exponential intervals use a 64-term positive Taylor sum with an exact geometric tail. *)
rateTiming = AbsoluteTiming[
 rateResult = Catch[
  rateChecks = <||>; powerWitnesses = {}; expWitnesses = {};
  addRateCheck[name_, value_] := AssociateTo[rateChecks, name -> TrueQ[value]];
  powPoint[x_, a_] := Module[{pn, qn, grid, k, lo, hi, ok},
    If[!TrueQ[x > 0] || !MatchQ[x, _Integer | _Rational] ||
       !MatchQ[a, _Integer | _Rational],
       Throw[<|"status" -> "FAILED_INTERVAL_INPUT"|>, "rateEnvelope"]];
    pn = Numerator[a]; qn = Denominator[a];
    If[qn == 1, Return[{x^pn, x^pn}]];
    grid = 10^16;
    k = Floor[N[grid x^a, 80]];
    lo = (k - 1)/grid; hi = (k + 2)/grid;
    ok = TrueQ[0 < lo <= hi && lo^qn <= x^pn <= hi^qn];
    AppendTo[powerWitnesses, ok];
    If[!ok, Throw[<|"status" -> "FAILED_EXACT_POWER_BRACKET",
       "base" -> ToString[x, InputForm],
       "exponent" -> ToString[a, InputForm]|>, "rateEnvelope"]];
    {lo, hi}
  ];
  pb[u_, a_] := Module[{l, r},
    If[u[[1]] == u[[2]], Return[powPoint[u[[1]], a]]];
    If[a >= 0,
      l = powPoint[u[[1]], a][[1]]; r = powPoint[u[[2]], a][[2]],
      l = powPoint[u[[2]], a][[1]]; r = powPoint[u[[1]], a][[2]]];
    {l, r}
  ];
  ab[u_, v_] := {u[[1]] + v[[1]], u[[2]] + v[[2]]};
  mb[u_, v_] := {u[[1]] v[[1]], u[[2]] v[[2]]};
  db[u_, v_] := {u[[1]]/v[[2]], u[[2]]/v[[1]]};
  sb[k_, u_] := {k u[[1]], k u[[2]]};
  oneb = {1, 1};
  expNegativeBox[x_] := Module[{nn = 64, ss, next, upperTail, ok},
    ok = TrueQ[0 <= x < nn + 2];
    AppendTo[expWitnesses, ok];
    If[!ok, Throw[<|"status" -> "FAILED_EXP_TAIL_DOMAIN"|>, "rateEnvelope"]];
    ss = Sum[x^j/j!, {j, 0, nn}];
    next = x^(nn + 1)/(nn + 1)!;
    upperTail = next/(1 - x/(nn + 2));
    {1/(ss + upperTail), 1/ss}
  ];
  disp[x_] := ToString[N[x, 20], InputForm];
  strs[x_] := Map[ToString[#, InputForm] &, x, {-1}];
  tm = 45000; tp = 55000;
  kb = 1380649/10^22; eps = 1602176634/10^21;
  lightc = 29979245800; nucD = 1/1000; fhe = 2/25;
  lamVec = {315614, 570670, 1263030};
  ciAmp = {2111/100, 1619/50, 399/20};
  ciP = {-1089/1000, -573/500, -1089/1000};
  ciC = {177/500, 52/125, 553/1000};
  ciR = {437/500, 987/1000, 147/200};
  ciD = {1101/1000, 132/125, 51/40};
  rrA = 1503/1000; rrB = 1923/1000; rrQ = 47/100;
  rrC = 261/500;
  drB1 = (4049664394833662/10^14) 11605;
  drB2 = (8099328789667/10^12) 11605;
  drExponent = {drB1, drB1 + drB2};
  drFactor = {1, 3/10};
  drEnergies = kb drExponent;
  bindingEV = {13598434599702/10^12, 24587389011/10^9, 5441776/10^5};
  rrBox[i_, temp_] := Module[{l = lamVec[[i]]/temp, u, num, den, pref},
    If[i == 2, Return[sb[3/10^14, pb[{l, l}, 327/500]]]];
    pref = If[i == 3, 2, 1];
    u = pb[{l/rrC, l/rrC}, rrQ];
    num = sb[pref 1269/10^16, pb[{l, l}, rrA]];
    den = pb[ab[oneb, u], rrB];
    db[num, den]
  ];
  ciBox[i_, temp_] := Module[{l = lamVec[[i]]/temp, v, val, den},
    val = sb[ciAmp[[i]], pb[{temp, temp}, -3/2]];
    val = mb[val, expNegativeBox[l/2]];
    val = mb[val, pb[{l, l}, ciP[[i]]]];
    v = pb[{l/ciC[[i]], l/ciC[[i]]}, ciR[[i]]];
    den = pb[ab[oneb, v], ciD[[i]]];
    db[val, den]
  ];
  drBox[i_, temp_] := Module[{val},
    val = sb[drFactor[[i]] 154/10^11,
      pb[{11605/temp, 11605/temp}, 3/2]];
    mb[val, expNegativeBox[drExponent[[i]]/temp]]
  ];

  (* Symbolic derivative identities of the positive analytic factors. *)
  rrLog = aa Log[ll/tt] - bb Log[1 + (ll/(cc tt))^qq];
  rrU = (ll/(cc tt))^qq;
  rrG = -aa + bb qq rrU/(1 + rrU);
  addRateCheck["RR_log_slope_identity",
    FullSimplify[tt D[rrLog, tt] - rrG,
      Assumptions -> tt > 0 && ll > 0 && cc > 0 && qq > 0] == 0];
  addRateCheck["RR_log_slope_derivative_identity",
    FullSimplify[tt D[rrG, tt] + bb qq^2 rrU/(1 + rrU)^2,
      Assumptions -> tt > 0 && ll > 0 && cc > 0 && qq > 0] == 0];
  ciLog = -3/2 Log[tt] - ll/(2 tt) + pp Log[ll/tt] -
    dd Log[1 + (ll/(cc tt))^rr];
  ciV = (ll/(cc tt))^rr;
  ciG = -3/2 - pp + ll/(2 tt) + dd rr ciV/(1 + ciV);
  addRateCheck["CI_log_slope_identity",
    FullSimplify[tt D[ciLog, tt] - ciG,
      Assumptions -> tt > 0 && ll > 0 && cc > 0 && rr > 0] == 0];
  addRateCheck["DR_log_slope_identity",
    Together[tt D[-3/2 Log[tt] - be/tt, tt] - (-3/2 + be/tt)] == 0];
  kinResidual = D[kk tt ar[tt] (3/2 + gr[tt]), tt] -
    kk ar[tt] ((1 + gr[tt]) (3/2 + gr[tt]) + gprime);
  addRateCheck["RR_captured_kinetic_derivative_identity",
    Expand[kinResidual /. {
      Derivative[1][ar][tt] -> ar[tt] gr[tt]/tt,
      Derivative[1][gr][tt] -> gprime/tt}] == 0];
  yy = Sqrt[xx^2 + yOne^2]; ssym = Sqrt[yy/yA];
  vLog = Log[(xx - 1)^2 + yW^2] +
    (pV/2 - 11/2)/2 Log[xx^2 + yOne^2] - pV Log[1 + ssym];
  vLogDerivative = 2 (xx - 1)/((xx - 1)^2 + yW^2) +
    (pV/2 - 11/2) xx/(xx^2 + yOne^2) -
    (pV/2) xx/(xx^2 + yOne^2) ssym/(1 + ssym);
  addRateCheck["Verner_log_derivative_identity",
    FullSimplify[D[vLog, xx] - vLogDerivative,
      Assumptions -> xx > 1 && yOne >= 0 && yW >= 0 && yA > 0 && pV > 0] == 0];

  (* Monotonicity proves endpoint maxima on the entire temperature interval. *)
  ciSlopeLower = -3/2 - ciP + lamVec/(2 tp);
  ciSlopeUpper = -3/2 - ciP + lamVec/(2 tm) + ciD ciR;
  drSlopeLower = -3/2 + drExponent/tp;
  drSlopeUpper = -3/2 + drExponent/tm;
  addRateCheck["CI_and_DR_whole_interval_monotonicity",
    And @@ Thread[Join[ciSlopeLower, drSlopeLower] > 0]];
  addRateCheck["RR_whole_interval_monotonicity",
    rrA - rrB rrQ > 0 && 327/500 > 0];
  uLowerWarm = Table[
    pb[{lamVec[[i]]/(rrC tp), lamVec[[i]]/(rrC tp)}, rrQ][[1]],
    {i, {1, 3}}];
  addRateCheck["RR_kinetic_whole_interval_positivity",
    And @@ Thread[uLowerWarm > 3] &&
      3/2 - rrA + rrB rrQ (3/4) > 0 && 3/2 - 327/500 > 0];

  rrIntervals = Table[rrBox[i, tm], {i, 3}];
  ciIntervals = Table[ciBox[i, tp], {i, 3}];
  drIntervals = Table[drBox[i, tp], {i, 2}];
  rrUpper = Last /@ rrIntervals;
  ciUpper = Last /@ ciIntervals;
  drUpper = Last /@ drIntervals;
  rrCaps = {2/10^13, 2/10^13, 1/10^12};
  ciCaps = {1/10^9, 4/10^11, 2/10^14};
  drCaps = {4/10^14, 2/10^15};
  addRateCheck["RR_CI_DR_coefficient_caps",
    And @@ Thread[Join[rrUpper, ciUpper, drUpper] <
      Join[rrCaps, ciCaps, drCaps]]];
  rrDerCaps = {7/10^18, 3/10^18, 4/10^17};
  ciDerCaps = {1/10^13, 7/10^15, 7/10^18};
  drDerCaps = {8/10^18, 5/10^19};
  rrDerivativeMajorant = rrCaps {rrA, 327/500, rrA}/tm;
  ciDerivativeMajorant = ciCaps ciSlopeUpper/tm;
  drDerivativeMajorant = drCaps drSlopeUpper/tm;
  addRateCheck["RR_CI_DR_temperature_derivative_caps",
    And @@ Thread[Join[rrDerivativeMajorant, ciDerivativeMajorant,
       drDerivativeMajorant] < Join[rrDerCaps, ciDerCaps, drDerCaps]]];
  kinCaps = {2/10^24, 2/10^24, 1/10^23};
  kinDerCaps = {2/10^29, 1/10^29, 1/10^28};
  kinLogBound = (503/1000) (3/2 - rrA + rrB rrQ) + rrB rrQ^2/4;
  kinDerivativeMajorant = kb rrCaps {kinLogBound,
       (1 - 327/500) (3/2 - 327/500), kinLogBound};
  addRateCheck["RR_kinetic_value_and_derivative_caps",
    And @@ Thread[kb tp rrCaps < kinCaps] &&
      And @@ Thread[kinDerivativeMajorant < kinDerCaps]];
  drKinCaps = {3/10^24, 2/10^25};
  drKinDerCaps = {6/10^28, 4/10^29};
  addRateCheck["DR_kinetic_value_and_derivative_caps",
    And @@ Thread[drEnergies drCaps < drKinCaps] &&
      And @@ Thread[drEnergies drDerCaps < drKinDerCaps]];
  rrEscCaps = {7/10^24, 1/10^23, 1/10^22};
  rrEscDerCaps = {2/10^28, 15/10^29, 4/10^27};
  drEscCaps = {5/10^24, 3/10^25};
  drEscDerCaps = {1/10^27, 6/10^29};
  addRateCheck["RR_DR_escape_value_and_derivative_caps",
    And @@ Thread[eps bindingEV rrCaps + kinCaps < rrEscCaps] &&
      And @@ Thread[eps bindingEV rrDerCaps + kinDerCaps < rrEscDerCaps] &&
      And @@ Thread[(eps bindingEV[[2]] + drEnergies) drCaps < drEscCaps] &&
      And @@ Thread[(eps bindingEV[[2]] + drEnergies) drDerCaps < drEscDerCaps]];

  (* Source-selected velocity and post-Doppler energy domains. *)
  bMax = 49/1000; gammaCap = 501/500; gradDeltaCap = 11/10;
  dMin = 19/20; dMax = 20/19; energies = {23, 35, 70};
  eRanges = ({dMin #, dMax #} & /@ energies);
  thresholds = {68/5, 2459/100, 2721/50};
  active = {{True, True, True}, {False, True, True}, {False, False, True}};
  addRateCheck["Doppler_rational_interval_and_gradient_caps",
    dMin^2 < (1 - bMax)/(1 + bMax) &&
      dMax^2 > (1 + bMax)/(1 - bMax) &&
      gammaCap^2 (1 - bMax^2) > 1 &&
      gammaCap + gammaCap^3 (1 + bMax) bMax < gradDeltaCap &&
      41/841 + 1/10000 < bMax];
  addRateCheck["Fixed_active_matrix_and_post_Doppler_domain",
    And @@ Flatten[Table[
      If[active[[i, j]], eRanges[[j, 1]] > thresholds[[i]],
        eRanges[[j, 2]] < thresholds[[i]]],
      {i, 3}, {j, 3}]] &&
      Max[Flatten[eRanges]] < 50000 &&
      And @@ Thread[thresholds > bindingEV]];

  (* Each row is {E0,sigma0,ya,p,yw,y0,y1}. *)
  vernerPars = {
    {2149/5000, 54750, 822/25, 2963/1000, 0, 0, 0},
    {1361/100, 4746/5, 1469/1000, 797/250,
      2039/1000, 2217/5000, 267/125},
    {43/25, 13690, 822/25, 2963/1000, 0, 0, 0}};
  vernerBox[i_, j_] := Module[
    {e0, sig0, ya, pv, yw, y0, y1, xl, xu, yb, fb, val, denom, logBound},
    If[!active[[i, j]], Return[<|"sigma" -> {0, 0}, "derivative_upper" -> 0|>]];
    {e0, sig0, ya, pv, yw, y0, y1} = vernerPars[[i]];
    xl = eRanges[[j, 1]]/e0 - y0; xu = eRanges[[j, 2]]/e0 - y0;
    If[!TrueQ[1 < xl <= xu],
      Throw[<|"status" -> "FAILED_VERNER_X_DOMAIN"|>, "rateEnvelope"]];
    yb = pb[{xl^2 + y1^2, xu^2 + y1^2}, 1/2];
    fb = {(xl - 1)^2 + yw^2, (xu - 1)^2 + yw^2};
    val = mb[fb, pb[yb, pv/2 - 11/2]];
    denom = pb[ab[oneb, pb[sb[1/ya, yb], 1/2]], pv];
    val = sb[sig0/10^18, db[val, denom]];
    logBound = (2 (xu - 1)/fb[[1]] + (11/2) xu/yb[[1]]^2)/e0;
    <|"sigma" -> val, "derivative_upper" -> val[[2]] logBound,
      "log_derivative_upper" -> logBound, "x_min" -> xl|>
  ];
  vIntervals = Table[vernerBox[i, j], {i, 3}, {j, 3}];
  sigmaUpper = Table[vIntervals[[i, j]]["sigma"][[2]], {i, 3}, {j, 3}];
  sigmaDerivativeUpper = Table[vIntervals[[i, j]]["derivative_upper"], {i, 3}, {j, 3}];
  sigmaCaps = {{3/10^18, 1/10^18, 2/10^19},
               {0, 8/10^18, 2/10^18}, {0, 0, 2/10^18}};
  sigmaDerCaps = {{1/10^18, 3/10^19, 3/10^20},
                  {0, 1/10^18, 3/10^19}, {0, 0, 3/10^19}};
  addRateCheck["Verner_positive_factor_interval_caps",
    And @@ Flatten[Table[If[active[[i, j]],
      0 < sigmaUpper[[i, j]] < sigmaCaps[[i, j]],
      sigmaUpper[[i, j]] == sigmaCaps[[i, j]] == 0],
      {i, 3}, {j, 3}]]];
  addRateCheck["Verner_first_derivative_interval_caps",
    And @@ Flatten[Table[If[active[[i, j]],
      0 < sigmaDerivativeUpper[[i, j]] < sigmaDerCaps[[i, j]],
      sigmaDerivativeUpper[[i, j]] == sigmaDerCaps[[i, j]] == 0],
      {i, 3}, {j, 3}]]];

  (* Density/event product factors for the agreed zeta cube. *)
  zetaMid = {1/2, 1/50, 1/50}; zetaRadius = 1/1000;
  eElectronMax = 141/250;
  lowerMax = {501/1000, 21/500, 21/1000};
  upperMax = {501/1000, 21/1000, 21/1000};
  addRateCheck["Physical_density_and_composition_prefactors",
    Total[zetaMid {1, 1, 2}] + 4 zetaRadius == eElectronMax &&
      lowerMax == {1 - zetaMid[[1]] + zetaRadius,
        fhe - zetaMid[[2]] - zetaMid[[3]] + 2 zetaRadius,
        zetaMid[[2]] + zetaRadius} &&
      upperMax == zetaMid + zetaRadius &&
      Min[Join[zetaMid - zetaRadius,
        {fhe - zetaMid[[2]] - zetaMid[[3]] - 2 zetaRadius}]] > 0];
  addRateCheck["All_exact_interval_witnesses",
    And @@ powerWitnesses && And @@ expWitnesses];

  <|"schema" -> "bass-he-continuation-06-rate-envelope-result-v1",
    "unit" -> "HERE_RUX03_MOVING_GAS_CONTINUATION_CERTIFICATE_06",
    "status" -> If[And @@ Values[rateChecks], "PASS", "FAIL"],
    "assertions" -> rateChecks,
    "passed" -> Count[Values[rateChecks], True],
    "total" -> Length[rateChecks],
    "counting_scope" -> "New envelope/derivative expression-check groups, not independent theorems or native tests.",
    "temperature_interval_k" -> {tm, tp},
    "source_commit" -> "a5c958c414dea41216b445c05f58df837f05cacb",
    "exact_interval_method" -> "Positive rational arithmetic. Rational-power endpoint brackets certified by exact lo^q<=x^p<=hi^q. exp(-x) enclosed with n=64 positive Taylor sum and geometric tail. N[.,80] only proposes brackets; all accepted comparisons are exact.",
    "interval_witnesses" -> <|"rational_power_brackets" -> Length[powerWitnesses],
      "exp_taylor_enclosures" -> Length[expWitnesses],
      "all_exact_checks_true" -> (And @@ powerWitnesses && And @@ expWitnesses)|>,
    "cap_order" -> <|"edge_order" -> {"HI/HII", "HeI/HeII", "HeII/HeIII"},
      "DR_order" -> {"HeII_to_HeI_resonance_1", "HeII_to_HeI_resonance_2"},
      "sigma_columns_ev" -> energies|>,
    "coefficient_caps_cm3_s" -> <|"RR" -> strs[rrCaps], "CI" -> strs[ciCaps], "DR" -> strs[drCaps]|>,
    "temperature_derivative_caps_cm3_s_K" -> <|"RR" -> strs[rrDerCaps], "CI" -> strs[ciDerCaps], "DR" -> strs[drDerCaps]|>,
    "kinetic_caps_erg_cm3_s" -> <|"RR" -> strs[kinCaps], "DR" -> strs[drKinCaps]|>,
    "kinetic_temperature_derivative_caps_erg_cm3_s_K" -> <|"RR" -> strs[kinDerCaps], "DR" -> strs[drKinDerCaps]|>,
    "escape_coefficient_caps_erg_cm3_s" -> <|"RR" -> strs[rrEscCaps], "DR" -> strs[drEscCaps]|>,
    "escape_temperature_derivative_caps_erg_cm3_s_K" -> <|"RR" -> strs[rrEscDerCaps], "DR" -> strs[drEscDerCaps]|>,
    "source_endpoint_upper_display" -> <|"RR_at_45000" -> (disp /@ rrUpper),
      "CI_at_55000" -> (disp /@ ciUpper), "DR_at_55000" -> (disp /@ drUpper)|>,
    "sigma_caps_cm2" -> strs[sigmaCaps],
    "sigma_derivative_caps_cm2_per_ev" -> strs[sigmaDerCaps],
    "certified_sigma_upper_display" -> Map[disp, sigmaUpper, {2}],
    "certified_sigma_derivative_upper_display" -> Map[disp, sigmaDerivativeUpper, {2}],
    "gas_frame_energy_ranges_ev" -> strs[eRanges],
    "D_cm3" -> ToString[nucD, InputForm], "f" -> ToString[fhe, InputForm],
    "beta_norm_upper" -> ToString[bMax, InputForm],
    "gamma_upper" -> ToString[gammaCap, InputForm],
    "Doppler_gradient_norm_upper" -> ToString[gradDeltaCap, InputForm],
    "electron_fraction_upper" -> ToString[eElectronMax, InputForm],
    "lower_absorber_fraction_upper" -> strs[lowerMax],
    "upper_ion_fraction_upper" -> strs[upperMax],
    "scope" -> "Real analytic functions defined by the selected source decimals on the stated compact domain. This is not a floating-point native solver validation."
  |>,
  "rateEnvelope"
 ];
][[1]];
AssociateTo[rateResult, "kernel_elapsed_seconds" -> rateTiming,
  "kernel_version" -> $Version, "system_id" -> $SystemID];
ExportString[rateResult, "RawJSON"]
