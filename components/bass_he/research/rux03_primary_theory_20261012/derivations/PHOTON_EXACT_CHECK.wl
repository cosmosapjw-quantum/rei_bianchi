ClearAll["Global`*"];
zeroQ[expr_] := And @@ (TrueQ[Together[#] === 0] & /@ Flatten[{expr}]);
lam = {op0, op1, op2};
avail = pold + dt sref;
den = 1 + dt Total[lam];
ph = avail/den;
absorb = dt lam ph;
jac = Table[D[absorb[[a]], lam[[b]]], {a, 3}, {b, 3}];
jexpected = Table[dt avail/den (KroneckerDelta[a, b] - dt lam[[a]]/den), {a, 3}, {b, 3}];
inverse = absorb/(dt (avail - Total[absorb]));
redistribution = {{1, 0}, {-1, 1}, {0, -1}};

xx = {xh, xhe1, xhe2};
lower = {nh (1 - xh), nhe (1 - xhe1 - xhe2), nhe xhe1};
sig = {sig0, sig1, sig2};
lamx = light sig lower;
totalx = Total[lamx];
denx = 1 + dt totalx;
phx = avail/denx;
absx = dt lamx phx;
gphx = Table[D[phx, xx[[j]]], {j, 3}];
gexpected = Table[-dt avail D[totalx, xx[[j]]]/denx^2, {j, 3}];
hphx = Table[D[phx, xx[[j]], xx[[k]]], {j, 3}, {k, 3}];
hexpected = Table[2 dt^2 avail D[totalx, xx[[j]]] D[totalx, xx[[k]]]/denx^3, {j, 3}, {k, 3}];
habsx = Table[D[absx[[a]], xx[[j]], xx[[k]]], {a, 3}, {j, 3}, {k, 3}];
haexpected = Table[
 -dt^2 avail (D[lamx[[a]], xx[[j]]] D[totalx, xx[[k]]] + D[lamx[[a]], xx[[k]]] D[totalx, xx[[j]]])/denx^2
 +2 dt^3 avail lamx[[a]] D[totalx, xx[[j]]] D[totalx, xx[[k]]]/denx^3,
 {a, 3}, {j, 3}, {k, 3}];

newH = (oldH + dt ionH)/(1 + dt (ionH + rrH));
oldZ = 1 - oldHe1 - oldHe2;
newHe1 = (oldHe1 + oldZ aa/(1 + aa) + oldHe2 dd/(1 + dd))/(1 + bb/(1 + aa) + cc/(1 + dd));
newHe2 = (oldHe2 + cc newHe1)/(1 + dd);
newZ = (oldZ + bb newHe1)/(1 + aa);

productDelta = enew nnew - eold nold;
etheta = (1 - theta) eold + theta enew;
npartner = theta nold + (1 - theta) nnew;
endpointWork = dt nu enew phx;
geometryCorrection = -(enew - eold) pold - endpointWork;

checks = <|
 "photon_BE_reverse_substitution" -> zeroQ[ph - pold - dt (sref - Total[lam] ph)],
 "reference_photon_budget" -> zeroQ[ph + Total[absorb] - avail],
 "photon_input_derivatives" -> zeroQ[{D[ph, pold] - 1/den, D[ph, sref] - dt/den, D[ph, dt] - (sref - Total[lam] pold)/den^2}],
 "allocation_jacobian" -> zeroQ[jac - jexpected],
 "allocation_column_sums" -> zeroQ[Total[jac] - ConstantArray[dt avail/den^2, 3]],
 "allocation_inverse" -> zeroQ[inverse - lam],
 "allocation_response_modes" -> zeroQ[Join[Flatten[(jac - dt avail/den IdentityMatrix[3]).redistribution], jac.lam - dt avail/den^2 lam]],
 "allocation_jacobian_determinant" -> zeroQ[Det[jac] - (dt avail)^3/den^4],
 "photon_fraction_gradient" -> zeroQ[gphx - gexpected],
 "photon_fraction_hessian" -> zeroQ[hphx - hexpected],
 "allocation_fraction_hessian" -> zeroQ[habsx - haexpected],
 "differentiated_photon_budget" -> zeroQ[Table[D[phx + Total[absx], xx[[j]]], {j, 3}]],
 "proper_reference_conversion" -> zeroQ[((ph /. {pold -> vold nproperold, sref -> vstar sproper})/vstar) - ((vold/vstar) nproperold + dt sproper)/den],
 "per_H_reference_conversion" -> zeroQ[((ph /. {pold -> nh0 pperH, sref -> nh0 sperH})/nh0) - (pperH + dt sperH)/den],
 "conditional_H_balance" -> zeroQ[newH - oldH - dt (ionH (1 - newH) - rrH newH)],
 "conditional_He_balances_and_normalization" -> zeroQ[{newZ - oldZ + aa newZ - bb newHe1, newHe1 - oldHe1 - aa newZ + (bb + cc) newHe1 - dd newHe2, newHe2 - oldHe2 - cc newHe1 + dd newHe2, newZ + newHe1 + newHe2 - 1}],
 "endpoint_energy_product_rule" -> zeroQ[productDelta - enew (nnew - nold) - (enew - eold) nold],
 "general_energy_product_rule" -> zeroQ[productDelta - etheta (nnew - nold) - npartner (enew - eold)],
 "geometry_correction_derivative" -> zeroQ[Table[D[endpointWork + geometryCorrection, xx[[j]]], {j, 3}]]
|>;
<|"method" -> "Exact symbolic Together and D; rational identities",
  "checks" -> checks,
  "group_count" -> Length[checks],
  "all_pass" -> And @@ Values[checks],
  "scope" -> "Algebraic formula verification; no ODE, native binary, calibration, or history campaign"|>
