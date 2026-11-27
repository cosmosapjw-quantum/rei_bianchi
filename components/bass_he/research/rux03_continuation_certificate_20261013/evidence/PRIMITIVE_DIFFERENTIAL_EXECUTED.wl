ClearAll["Global`*"];
started = AbsoluteTime[];
checks = <||>;
put[name_, value_] := AssociateTo[checks, name -> TrueQ[value]];
gam = 5/3; kap = 2/3;

(* New affine chart, in eV/H energy and scaled momentum units. *)
forward = {
 {s1, 0, 0, 0, 0, 0, 0},
 {0, s2, 0, 0, 0, 0, 0},
 {0, 0, s3, 0, 0, 0, 0},
 {b1 s1/gs, b2 s2/gs, b3 s3/gs, st/gs, bs1 sm, bs2 sm, bs3 sm},
 {0, 0, 0, 0, sm, 0, 0},
 {0, 0, 0, 0, 0, sm, 0},
 {0, 0, 0, 0, 0, 0, sm}};
backward = {
 {1/s1, 0, 0, 0, 0, 0, 0},
 {0, 1/s2, 0, 0, 0, 0, 0},
 {0, 0, 1/s3, 0, 0, 0, 0},
 {-b1/st, -b2/st, -b3/st, gs/st, -gs bs1/st, -gs bs2/st, -gs bs3/st},
 {0, 0, 0, 0, 1/sm, 0, 0},
 {0, 0, 0, 0, 0, 1/sm, 0},
 {0, 0, 0, 0, 0, 0, 1/sm}};
put["PD01_affine_seven_residual_equivalence",
 Together[backward.forward] == IdentityMatrix[7] &&
 Together[Det[forward] - s1 s2 s3 st sm^3/gs] == 0];
eAnchor = (aa + gam ww) gs - kap ww/gs;
mDotAnchor = (aa + gam ww) gs (1 - 1/gs^2);
put["PD02_anchor_thermal_value",
 Together[gs (eAnchor - mDotAnchor) - aa - ww] == 0];

(* The parent's scalar inverse is reused. These are its new differential
   coefficients after composition and affine-chart chain rules. *)
hh = Sqrt[cc^2 + mm^2];
ff = (3 cc^2 + 2 aa cc + 5 mm^2)/(5 hh);
qq = (cc - aa)/cc; vb = mm/hh; gg = hh/cc;
ell = (1 - kap qq vb^2)/gg;
bind = (1 - (2/5) qq vb^2)/gg;
mom = 1 + (2/5) qq/gg^2;
put["PD03_composition_and_momentum_differential_coefficients",
 And @@ (TrueQ[FullSimplify[# == 0, cc > aa > 0 && Element[mm, Reals]]] & /@
 {gam D[ff, cc] - ell, D[ff, cc] + D[ff, aa] - bind,
  D[ff, mm] - mom vb})];
dww = (dtt/gs + (1/gs - bind) daa + (bs - mom vb) dmm)/ell;
put["PD04_affine_primitive_differential_identity",
 FullSimplify[(dtt + daa)/gs + bs dmm -
  D[ff, cc] (daa + gam dww) - D[ff, aa] daa - D[ff, mm] dmm == 0,
  cc > aa > 0 && gs > 0 && Element[{mm, bs, dtt, daa, dmm}, Reals]]];

(* Cancellation-free exact cold-cone remainder identity. *)
put["PD05_cold_remainder_rationalization",
 Expand[Expand[(hr - h0 - proj) (hr + h0 + proj) - (norm2 - proj^2)] /.
   hr^2 -> h0^2 + 2 h0 proj + norm2] == 0];
mv = {mx, my, mz}; hnorm = Sqrt[aa^2 + mv.mv];
hessian = Table[D[hnorm, mv[[i]], mv[[j]]], {i, 3}, {j, 3}];
put["PD06_cold_norm_Hessian",
 FullSimplify[hessian == IdentityMatrix[3]/hnorm - Outer[Times, mv, mv]/hnorm^3,
 aa > 0 && Element[mv, Reals]]];

uv = {ux, uy, uz}; gu = Sqrt[1 + uv.uv]; bu = uv/gu;
ray = {nx, ny, nz};
put["PD07_velocity_density_Doppler_Jacobians",
 FullSimplify[
  Table[D[bu[[i]], uv[[j]]], {i, 3}, {j, 3}] ==
   (IdentityMatrix[3] - Outer[Times, bu, bu])/gu &&
  Table[D[dd/gu, uv[[i]]], {i, 3}] == -dd bu/gu^2 &&
  Table[D[gu - uv.ray, uv[[i]]], {i, 3}] == bu - ray,
  Element[Join[uv, ray, {dd}], Reals]]];

(* Exact finite envelope arithmetic. Each inequality below uses a bound
   proved uniformly on the cube, not samples of its nonlinear inverse. *)
eps = 1602176634/10^21; kb = 1380649/10^22; kev = kb/eps;
fhe = 2/25; zs = {1/2, 1/50, 1/50};
bindVector = {13598434599702/10^12, 24587389011/10^9,
  24587389011/10^9 + 5441776/10^5};
bStar = bindVector.zs; bWidth = Total[bindVector]/1000;
dStar = 1 + fhe + {1, 1, 2}.zs;
dMin = dStar - 1/250; dMax = dStar + 1/250;
wStar = (3/2) kev dStar 50000;
gsExact = 841/840; bsExact = 41/841; usExact = 41/840;
aMin = 10^9; aStarMax = 1500000000 + bStar;
mWidthProof = (7/4) aStarMax/10^6;
put["PD08_exact_anchor_composition_and_thermal_constants",
 bStar < 9 && 0 < bWidth < 59/500 && dMin == 409/250 &&
 dMax == 411/250 && 10 < wStar < 11 &&
 gsExact^2 (1 - bsExact^2) == 1 && gsExact (1 - bsExact) == 20/21 &&
 gsExact (1 + bsExact) == 21/20];
put["PD09_uniform_momentum_and_cold_displacement_bound",
 3 < (7/4)^2 && mWidthProof < 2700 &&
 2700 + usExact (59/500 + gam 11) < 2701];
coldRemainderProof = 2701^2/(2 aMin);
coldUProof = usExact + (2700 + usExact (59/500 + gam 11))/aMin;
put["PD10_uniform_cold_gap_and_speed_envelopes",
 coldRemainderProof < 1/250 && coldUProof < 49/1000 &&
 1 + (49/1000)^2 < (501/500)^2];
wLoProof = (wStar - 1/4)/gsExact - 1/250;
wHiProof = (501/500) (wStar + 1/4)/gsExact;
tempCoeff = 2/(3 kev);
put["PD11_whole_cube_positive_warm_inclusion",
 wLoProof > 10 && wHiProof < 11 &&
 tempCoeff 10/dMax > 45000 && tempCoeff 11/dMin < 55000];
uDeviationProof = (2700 + usExact (59/500 + gam))/aMin;
put["PD12_enthalpy_fraction_and_anchor_velocity_distance",
 gam 11/aMin < 1/50000000 && uDeviationProof < 3/1000000];
bindSlopeProof = (49/1000) (3/1000000) +
 (2/5) (1/50000000) (49/1000)^2;
momSlopeProof = 3/1000000 + (2/5) (1/50000000) (49/1000);
put["PD13_affine_inverse_small_coefficients",
 bindSlopeProof < 15/10^8 && momSlopeProof < 3001/10^9];
wLipProof = (501/500) ((1/4)/gsExact +
 (15/10^8) (59/500) + (3001/10^9) 2700);
cLipProof = 59/500 + gam (13/50);
put["PD14_thermal_and_enthalpy_row_bounds",
 wLipProof < 13/50 && cLipProof < 14/25];
uLipProof = (2700 + (1/20) (14/25))/aMin;
put["PD15_velocity_gamma_and_proper_density_row_bounds",
 uLipProof < 271/10^8 &&
 (49/1000) (271/10^8) < 133/10^9 &&
 271/10^8 < 3/10^6 && 133/10^9 < 2/10^7 &&
 (1/1000) (133/10^9) == 133/10^12];
tLipProof = tempCoeff ((13/50)/dMin + 11 (1/250)/dMin^2);
put["PD16_temperature_and_Doppler_row_bounds",
 tLipProof < 1400 && (1 + 49/1000) (271/10^8) < 3/10^6 &&
 3/10^6 < 4/10^6];

(* The contract's actual six fixed directional photon nodes. *)
labEnergies = {23, 23, 35, 35, 70, 70};
rayDirections = {{1, 0, 0}, {-1, 0, 0}, {0, 1, 0}, {0, -1, 0},
 {0, 0, 1}, {0, 0, -1}};
anchorU = {0, 0, usExact};
deltaAnchors = (gsExact - anchorU.#) & /@ rayDirections;
energyAnchors = labEnergies deltaAnchors;
nodeIntervals = Transpose[{energyAnchors - (4/10^6) labEnergies,
 energyAnchors + (4/10^6) labEnergies}];
fitCuts = {68/5, 2459/100, 2721/50};
expectedActive = {{True, False, False}, {True, False, False},
 {True, True, False}, {True, True, False}, {True, True, True}, {True, True, True}};
observedActive = Table[nodeIntervals[[q, 1]] > fitCuts[[i]], {q, 6}, {i, 3}];
branchStable = And @@ Flatten[Table[
 If[expectedActive[[q, i]], nodeIntervals[[q, 1]] > fitCuts[[i]],
  nodeIntervals[[q, 2]] < fitCuts[[i]]], {q, 6}, {i, 3}]];
nearestCutMargin = Min[Flatten[Table[
 If[expectedActive[[q, i]], nodeIntervals[[q, 1]] - fitCuts[[i]],
  fitCuts[[i]] - nodeIntervals[[q, 2]]], {q, 6}, {i, 3}]]];
put["PD17_six_node_cutoff_cells_and_provider_guard",
 observedActive == expectedActive && branchStable && nearestCutMargin > 3/2 &&
 Min[Flatten[nodeIntervals]] > 0 && Max[Flatten[nodeIntervals]] < 74 && 74 < 50000];

result = <|
 "schema" -> "bass-he-theory06-primitive-exact-check-v1",
 "unit" -> "HERE_RUX03_MOVING_GAS_CONTINUATION_CERTIFICATE_06",
 "role" -> "author_derivation_check_not_independent_decision",
 "kernel" -> <|"version" -> $Version, "system_id" -> $SystemID|>,
 "checks" -> checks, "named_group_count" -> Length[checks],
 "passed" -> Count[Values[checks], True], "all_passed" -> And @@ Values[checks],
 "scope" -> "7 new exact identity groups and 10 exact arithmetic envelope groups; uniform cube meaning follows the linked analytic inequalities, not point sampling",
 "uniform_inputs" -> <|"mu_eV_per_H" -> {1000000000, 1500000000},
  "D_cm_minus3" -> "1/1000", "f" -> "2/25", "zeta_star" -> {"1/2", "1/50", "1/50"},
  "gamma_star" -> "841/840", "beta_star_z" -> "41/841",
  "halfwidths" -> {"1/1000", "1/1000", "1/1000", "1/4", "aStar/1000000", "aStar/1000000", "aStar/1000000"}|>,
 "exact_values" -> Association[Map[First[#] -> ToString[InputForm[Last[#]]] &,
  {"B_star" -> bStar, "B_halfwidth" -> bWidth, "w_star" -> wStar,
   "cold_remainder_upper" -> coldRemainderProof, "cold_u_upper" -> coldUProof,
   "thermal_lower" -> wLoProof, "thermal_upper" -> wHiProof,
   "w_row_proof_upper" -> wLipProof, "T_row_proof_upper" -> tLipProof,
   "u_row_proof_upper" -> uLipProof, "node_cutoff_minimum_margin_eV" -> nearestCutMargin}]],
 "display_values" -> N[<|"B_star" -> bStar, "B_halfwidth" -> bWidth, "w_star" -> wStar,
  "cold_remainder_upper" -> coldRemainderProof, "thermal_lower" -> wLoProof,
  "thermal_upper" -> wHiProof, "w_row_proof_upper" -> wLipProof,
  "T_row_proof_upper" -> tLipProof, "node_cutoff_minimum_margin_eV" -> nearestCutMargin|>, 20],
 "certified_simple_bounds_per_unit_X_infinity" -> <|
  "w_eV_per_H" -> "13/50", "T_K" -> 1400,
  "beta_Euclidean" -> "3/1000000", "gamma" -> "1/5000000",
  "n_H_cm_minus3" -> "133/1000000000000", "Doppler" -> "1/250000"|>,
 "node_intervals_exact_eV" -> Map[ToString[InputForm[#]] &, nodeIntervals, {2}],
 "node_intervals_display_eV" -> N[nodeIntervals, 20],
 "node_active_edges_HI_HeI_HeII" -> expectedActive,
 "native_builds_RHS_ODE" -> 0,
 "wall_seconds_kernel" -> N[AbsoluteTime[] - started, 8]|>;
ExportString[result, "RawJSON", "Compact" -> False]
