(* Readable reproduction of the algebra evaluated in HE31 (not a new run).
   See WOLFRAM_ALGEBRA.json for the returned result. No external tables. *)
Clear[mu, v, x, nH0, nHe0, h, he2, he3, ne, csi, sigmasi, necm];
kernel = 3/8 (1 + mu^2 v^2 + (1 - mu^2) (1 - v^2)/2);
gain = Table[FullSimplify[Integrate[kernel LegendreP[l, v], {v, -1, 1}]], {l, 0, 4}];
eig = Table[FullSimplify[Integrate[gain[[l + 1]] LegendreP[l, mu], {mu, -1, 1}]/
  Integrate[LegendreP[l, mu]^2, {mu, -1, 1}]], {l, 0, 4}];
loss = 1 - eig;
ne[x_] := Exp[-3 x] (nH0 h[x] + nHe0 (he2[x] + 2 he3[x]));
densityResidual = Simplify[D[ne[x], x] + 3 ne[x] - Exp[-3 x]
  (nH0 h'[x] + nHe0 (he2'[x] + 2 he3'[x]))];
unitResidual = Simplify[(100 csi) (10^4 sigmasi) necm - csi sigmasi (10^6 necm)];
{eig, loss, densityResidual, unitResidual}
