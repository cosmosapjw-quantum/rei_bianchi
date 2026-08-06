(* R2C-R1B exact symbolic validation.  Stateless and front-end independent. *)
Module[{uu, rr, nhi, nhii, mat, col, b1, b2, ss, gg, ff, aa, kk, nn,
  kpts, wt, mt, nnode, nknot, endpointRows, totalRows, ms,
  dN, jInt, qInt, rInt, spInt, smInt, ledgerSolution},
 mat = {{-uu, rr}, {uu, -rr}};
 col = Total[mat];
 b1 = First[mat . {0, nhii}];
 b2 = Last[mat . {nhi, 0}];
 gg[ss_] := ss (1 - ss) (ss - 1/2);
 ff[ss_] := ss (1 - ss);
 kpts = 8;
 wt = Join[{1/2}, ConstantArray[1, kpts - 2], {1/2}];
 mt = Join[{UnitVector[kpts, 1]}, {UnitVector[kpts, kpts]}, {wt}];
 nnode = 3; nknot = 4;
 endpointRows = Join[
   Table[UnitVector[nnode nknot, (i - 1) nknot + 1], {i, nnode}],
   Table[UnitVector[nnode nknot, i nknot], {i, nnode}]
 ];
 totalRows = Table[Flatten@Table[UnitVector[nknot, q], {i, nnode}], {q, nknot}];
 ms = Join[endpointRows, totalRows];
 ledgerSolution = First@Solve[dN == -jInt - qInt + rInt + spInt - smInt, jInt];
 InputForm@<|
  "MetzlerOffDiagonalNonnegativeUnderRates" ->
    FullSimplify[{mat[[1, 2]] >= 0, mat[[2, 1]] >= 0}, Assumptions -> {uu >= 0, rr >= 0}],
  "ColumnSums" -> col,
  "BoundaryDerivatives" -> {b1, b2},
  "IntegratedLedgerSolution" -> ledgerSolution,
  "LedgerResidualAfterSubstitution" ->
    FullSimplify[(jInt + dN + qInt - rInt - spInt + smInt) /. ledgerSolution],
  "TemporalNull" -> {gg[0], gg[1], Integrate[gg[ss], {ss, 0, 1}]},
  "SpatialPointwiseNull" ->
    FullSimplify[(aa + kk ff[ss]) + (nn - kk ff[ss]) - (aa + nn)],
  "SpatialEndpointAndIntegral" -> {ff[0], ff[1], Integrate[ff[ss], {ss, 0, 1}]},
  "TemporalK8RankNullity" -> {MatrixRank[mt], kpts - MatrixRank[mt]},
  "SpatialN3K4RankNullity" -> {MatrixRank[ms], nnode nknot - MatrixRank[ms]}
 |>
]
