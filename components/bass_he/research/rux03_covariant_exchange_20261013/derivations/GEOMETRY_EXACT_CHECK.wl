(* THEORY04 geometric half: local-frame tensor algebra, paired beams,
   directional redshift, and exact endpoint-stage energy identities.
   No xAct dependency, numerical integration, atomic fit evaluation, or code mutation.
   General differential projection is proved in GEOMETRY_AND_PAIRED_BEAMS.md.
   This script checks the displayed algebraic reductions exactly. *)
ExportString[
 Module[
  {check, checks = <||>, cLight, rho, theta, dRho, divSpatial,
   ax, ay, az, qx, qy, qz, pxx, pyy, pxy, pxz, pyz,
   sxx, syy, sxy, sxz, syz, wxy, wxz, wyz,
   qVec, aVec, pi, sig, vort, tensor, kin, uCov, uCon, qFour,
   h1, h2, h3, meanH, r1, r2, r3, e1, e2, e3, radii,
   dirsOld, hs, ratioSquared, logEnergyDerivative, shearProjection,
   b, z, meanAxisH, shear, characteristicSquare, muSquared,
   eta, directions, beamEnergies, pressure, fluxOverC, targetPressure,
   nBefore, source, dt, l1, l2, l3, lambda, nAfter,
   oneBeamAfter, absorptions, energyBefore, energyAfter, nu,
   workDiscrete, workEndpoint, workCorrection, thetaStage,
   nGeneralAfter, r, energyRatio, pressureDifference},
  check[expr_] := And @@ (TrueQ[Together[#] === 0] & /@ Flatten[{expr}]);
  qVec = {qx, qy, qz}; aVec = {ax, ay, az};
  pi = {{pxx, pxy, pxz}, {pxy, pyy, pyz}, {pxz, pyz, -pxx-pyy}};
  sig = {{sxx, sxy, sxz}, {sxy, syy, syz}, {sxz, syz, -sxx-syy}};
  vort = {{0, wxy, wxz}, {-wxy, 0, wyz}, {-wxz, -wyz, 0}};
  tensor = ArrayFlatten[{{{{rho}}, {qVec/cLight}},
    {Transpose[{qVec/cLight}], rho IdentityMatrix[3]/3+pi}}];
  kin = ArrayFlatten[{{{{0}}, {aVec/cLight^2}},
    {ConstantArray[0, {3, 1}], (theta IdentityMatrix[3]/3+sig+vort)/cLight}}];
  uCov = {-1,0,0,0}; uCon = {1,0,0,0}; qFour = Prepend[qVec,0];
  AssociateTo[checks, "local_rest_u_T_contraction" ->
    check[uCov.tensor+rho uCon+qFour/cLight]];
  AssociateTo[checks, "local_rest_T_grad_u_contraction" ->
    check[cLight Flatten[tensor].Flatten[kin]
      -theta rho/3-aVec.qVec/cLight^2-Flatten[sig].Flatten[pi]]];
  AssociateTo[checks, "two_acceleration_flux_terms" ->
    check[dRho+theta rho+divSpatial+aVec.qVec/cLight^2
      +cLight Flatten[tensor].Flatten[kin]
      -(dRho+4 theta rho/3+divSpatial+2 aVec.qVec/cLight^2
        +Flatten[sig].Flatten[pi])]];

  meanH = (h1+h2+h3)/3;
  radii = {r1,r2,r3}; dirsOld = {e1,e2,e3}; hs = {h1,h2,h3};
  ratioSquared = Total[(radii dirsOld)^2];
  logEnergyDerivative =
    Sum[D[ratioSquared, radii[[i]]] (-hs[[i]] radii[[i]]), {i,3}]
      /(2 ratioSquared);
  shearProjection = Total[(hs-meanH) (radii dirsOld)^2]/ratioSquared;
  AssociateTo[checks, "direction_endpoint_unit_norm" ->
    check[Total[(radii dirsOld)^2]/ratioSquared-1]];
  AssociateTo[checks, "direction_endpoint_parity" ->
    check[(ratioSquared /. Thread[dirsOld -> -dirsOld])-ratioSquared]];
  AssociateTo[checks, "bianchi_direction_energy_derivative" ->
    check[logEnergyDerivative+meanH+shearProjection]];
  characteristicSquare = (1-z) Exp[2 b]+z Exp[-4 b];
  muSquared = z Exp[-4 b]/characteristicSquare;
  AssociateTo[checks, "native_axisym_characteristic_redshift" ->
    check[-meanAxisH+shear D[characteristicSquare,b]/(2 characteristicSquare)
      +meanAxisH+shear (3 muSquared-1)]];

  directions = {{1,0,0},{-1,0,0},{0,1,0},{0,-1,0},{0,0,1},{0,0,-1}};
  beamEnergies = rho {(1-eta)/4,(1-eta)/4,(1-eta)/4,(1-eta)/4,eta/2,eta/2};
  fluxOverC = Total[MapThread[Times, {beamEnergies,directions}]];
  pressure = Total[MapThread[#1 Outer[Times,#2,#2] &, {beamEnergies,directions}]];
  targetPressure = rho DiagonalMatrix[{(1-eta)/2,(1-eta)/2,eta}];
  AssociateTo[checks, "six_beam_flux_and_pressure" ->
    check[Join[fluxOverC,Flatten[pressure-targetPressure]]]];
  AssociateTo[checks, "six_beam_trace_and_shear" ->
    check[{Tr[pressure]-rho,
      Flatten[DiagonalMatrix[{-shear,-shear,2 shear}]].
        Flatten[pressure-rho IdentityMatrix[3]/3]-shear rho (3 eta-1)}]];

  lambda = l1+l2+l3;
  nAfter = (nBefore+dt source)/(1+dt lambda);
  oneBeamAfter = (nBefore/2+dt source/2)/(1+dt lambda);
  absorptions = dt {l1,l2,l3} nAfter;
  AssociateTo[checks, "paired_BE_and_number_allocation" ->
    check[{2 oneBeamAfter-nAfter,nAfter-nBefore-dt source+Total[absorptions]}]];
  AssociateTo[checks, "paired_absorbed_momentum" ->
    check[(energyAfter/cLight) dt lambda oneBeamAfter (dirsOld-dirsOld)]];

  workDiscrete = (energyBefore-energyAfter) nBefore;
  workEndpoint = dt nu energyAfter nAfter;
  workCorrection = workDiscrete-workEndpoint;
  AssociateTo[checks, "history_energy_discrete_work" ->
    check[energyAfter nAfter-energyBefore nBefore+workDiscrete
      -dt energyAfter source+energyAfter Total[absorptions]]];
  AssociateTo[checks, "endpoint_work_correction" ->
    check[energyAfter nAfter-energyBefore nBefore+workEndpoint+workCorrection
      -dt energyAfter source+energyAfter Total[absorptions]]];
  AssociateTo[checks, "general_discrete_product_rule" ->
    check[energyAfter nGeneralAfter-energyBefore nBefore
      -((1-thetaStage) energyBefore+thetaStage energyAfter) (nGeneralAfter-nBefore)
      -(thetaStage nBefore+(1-thetaStage) nGeneralAfter) (energyAfter-energyBefore)]];

  energyRatio = (1-eta) r+eta/r^2;
  pressureDifference = eta/r^2-(1-eta) r/2;
  AssociateTo[checks, "zero_mean_expansion_directional_shear" ->
    check[shear r D[energyRatio,r]+2 shear pressureDifference]];
  AssociateTo[checks, "rational_two_and_six_beam_examples" ->
    check[{(energyRatio /. {r->2,eta->1})-1/4,
      (energyRatio /. {r->2,eta->2/3})-5/6,
      (energyRatio /. {r->2,eta->1/3})-17/12,
      ((1-energyRatio) /. {r->2,eta->1})-3/4,
      ((1-energyRatio) /. {r->2,eta->2/3})-1/6,
      ((1-energyRatio) /. {r->2,eta->1/3})+5/12}]];
  <|"schema" -> "theory04_geometry_exact_checks_v1",
    "method" -> "Exact Wolfram Language rational/matrix algebra and differentiation",
    "check_count" -> Length[checks], "checks" -> checks,
    "all_pass" -> And @@ Values[checks]|>
 ],
 "RawJSON"
]
