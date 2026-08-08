Module[
 {yy, zz, yaa, ybb, vv, ff, pp = 24/25, ll = 57/40,
  mm = 737/1000, ww, bh, ah, ahe, sh, shei, sheii, ch, che,
  ev, ex, res, inv, ep, xx, kk, ee},
 ww = (ll - mm) + mm yy;
 bh = 1 - yaa - ybb;
 ah = vv ww + (1 - vv) ff zz;
 ahe = vv mm (1 - yy) + (1 - vv) ff (1 - zz);
 sh = {-1, 1, 0, 0, 0};
 shei = {0, 0, -1, 1, 0};
 sheii = {0, 0, 0, -1, 1};
 ch = {1, 1, 0, 0, 0};
 che = {0, 0, 1, 1, 1};
 ev = <|
   "HII_CASE_B" -> -sh,
   "HEII_GROUND" -> -shei + yy sh + (1 - yy) shei,
   "HEII_CASE_B" -> -shei + pp sh,
   "HEIII_GROUND" -> -sheii + bh sh + ybb shei + yaa sheii,
   "HEIII_N2_BALMER" -> -sheii + sh,
   "HEIII_CASCADE" -> -sheii + ah sh + ahe shei|>;
 ex = <|
   "HII_CASE_B" -> {1, -1, 0, 0, 0},
   "HEII_GROUND" -> {-yy, yy, yy, -yy, 0},
   "HEII_CASE_B" -> {-pp, pp, 1, -1, 0},
   "HEIII_GROUND" -> {-bh, bh, -ybb, 1 + ybb - yaa, -1 + yaa},
   "HEIII_N2_BALMER" -> {-1, 1, 0, 1, -1},
   "HEIII_CASCADE" -> {-ah, ah, -ahe, 1 + ahe, -1}|>;
 res = AssociationMap[FullSimplify[ev[#] - ex[#]] &, Keys[ev]];
 inv = AssociationMap[
   <|"H" -> FullSimplify[ch.ev[#]], "He" -> FullSimplify[che.ev[#]]|> &,
   Keys[ev]];
 ee = <|
   "absorption" -> FullSimplify[-ep + xx + kk (ep - xx) + (1 - kk) (ep - xx)],
   "recombination" -> FullSimplify[-xx - kk + (xx + kk)]|>;
 <|
  "VectorResiduals" -> res,
  "NucleiInvariants" -> inv,
  "BranchChecks" -> <|
    "HEII_ground" -> FullSimplify[yy + (1 - yy) - 1],
    "HEIII_ground" -> FullSimplify[bh + yaa + ybb - 1],
    "two_photon_ionizing_count" -> FullSimplify[ww + mm (1 - yy) - ll],
    "cascade_absorbed_count" -> FullSimplify[ah + ahe - (vv ll + (1 - vv) ff)],
    "cascade_total_emitted_photon_count" ->
      FullSimplify[ah + ahe + vv (2 - ll) + (1 - vv) (1 - ff) - (1 + vv)]|>,
  "EnergyChecks" -> ee,
  "NoDirectHeIToHeIIIStoichiometry" ->
    FreeQ[Values[ev], {-1, 0, 0, 0, 1}],
  "BranchDomainImpliesNonnegative" -> FullSimplify[
    And @@ Thread[
      Flatten[{yy, 1 - yy, bh, yaa, ybb, pp, 1 - pp,
        vv ww, vv mm (1 - yy), vv (2 - ll),
        (1 - vv) ff zz, (1 - vv) ff (1 - zz),
        (1 - vv) (1 - ff)}] >= 0],
    Assumptions -> 0 <= yy <= 1 && 0 <= zz <= 1 && 0 <= yaa &&
      0 <= ybb && yaa + ybb <= 1 && 0 <= vv <= 1 && 0 <= ff <= 1],
  "Parameters" -> <|"p" -> pp, "ell" -> ll, "m" -> mm|>
 |>
]
