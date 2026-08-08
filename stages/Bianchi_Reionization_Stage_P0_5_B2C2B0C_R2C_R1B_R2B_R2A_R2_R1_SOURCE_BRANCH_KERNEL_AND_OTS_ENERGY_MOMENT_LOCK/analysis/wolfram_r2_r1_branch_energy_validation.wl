ClearAll[v, f, y, z, ell, m, w, AH, AHe, non, esc, chiH, chiHeI, chiHeII, E0, a, b, c];
ell = 57/40; m = 737/1000;
w = (ell - m) + m y;
AH = v w + (1 - v) f z;
AHe = v m (1 - y) + (1 - v) f (1 - z);
non = v (2 - ell); esc = (1 - v) (1 - f);
chiH = 13598434599702/1000000000000;
chiHeI = 24587389011/1000000000;
chiHeII = 54417760/1000000;
E0 = 3 chiHeII/4;
a = 2 - ell; b = m - a; c = 1 - a - b;
<|
 "PhotonCountResidual" -> FullSimplify[AH + AHe + non + esc - (1 + v)],
 "TwoPhotonIonizingCountResidual" -> FullSimplify[w + m (1 - y) - ell],
 "HummerSeatonVTable" -> (1 - #/2 & /@ {143/100, 139/100, 135/100, 130/100, 125/100}),
 "SupportWeights" -> {a, b, c},
 "HCountResidual" -> FullSimplify[a + 2 b + 2 c - ell],
 "HeICountResidual" -> FullSimplify[a + b - m],
 "PairCountResidual" -> FullSimplify[a + b + c - 1],
 "LyAlphaEnergy" -> E0,
 "LyAlphaHIExcess" -> FullSimplify[E0 - chiH],
 "LyAlphaHeIExcess" -> FullSimplify[E0 - chiHeI],
 "EnergyConservationAbsorption" -> FullSimplify[-Symbol["eps"] + Symbol["chi"] + Symbol["eta"] (Symbol["eps"]-Symbol["chi"]) + (1-Symbol["eta"])(Symbol["eps"]-Symbol["chi"])],
 "NoDirectHeIToHeIII" -> True
|>
