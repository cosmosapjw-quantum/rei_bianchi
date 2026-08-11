Module[{A, dA, z, db, dz, x, c, u0, w, r, h, dh, q, result},
  A = {{a11, a12}, {a21, a22}};
  dA = {{da11, da12}, {da21, da22}};
  z = {z1, z2}; db = {db1, db2};
  dz = Inverse[A].(db - dA.z);
  h = {h1, h2, h3}; dh = {dh1, dh2, dh3};
  q = Table[dh[[i]]/Total[h] - h[[i]] Total[dh]/Total[h]^2, {i, 3}];
  result = <|
    "ImplicitTangentResidual" -> FullSimplify[A.dz + dA.z - db],
    "ThermalRootDerivativeResidual" -> FullSimplify[
      D[c Exp[x] - u0 - w r[x], x] - (c Exp[x] - w r'[x])],
    "OwnerDerivativeSumResidual" -> FullSimplify[Total[q]],
    "HydrogenInvariantResidual" -> FullSimplify[{1, 1}.{-a, a}],
    "HeliumInvariantResidual" -> FullSimplify[{1, 1, 1}.{-b + cc, b - cc - d + e, d - e}]
  |>;
  result
]
