ClearAll["Global`*"];
ell = 57/40; m = 737/1000;
w = (ell - m) + m y;
AH = v w + (1 - v) f z;
AHe = v m (1 - y) + (1 - v) f (1 - z);
branch = FullSimplify[AH + AHe + v (2 - ell) + (1 - v) (1 - f) - (1 + v)];
h = {h1, h2, h3};
owner = FullSimplify[Total[h/Total[h]] - 1];
energy = FullSimplify[chemical + resolved + escaped + (-chemical - resolved - escaped)];
transitions = {{-1,1,0,0,0},{1,-1,0,0,0},{0,0,-1,1,0},{0,0,1,-1,0},{0,0,0,-1,1},{0,0,0,1,-1}};
hinv = FullSimplify /@ ({1,1,0,0,0}.# & /@ transitions);
heinv = FullSimplify /@ ({0,0,1,1,1}.# & /@ transitions);
<|"CascadePhotonIdentity"->branch,"OwnerSimplexResidual"->owner,
  "AugmentedEnergyResidual"->energy,"HydrogenInvariants"->hinv,
  "HeliumInvariants"->heinv|>
