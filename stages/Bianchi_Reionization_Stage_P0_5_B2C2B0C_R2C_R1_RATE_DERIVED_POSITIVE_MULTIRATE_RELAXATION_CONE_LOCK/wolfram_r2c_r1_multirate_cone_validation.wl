(* R2C-R1 symbolic validation for the positive multirate cone lock.
   Conventions: metric (-,+,+,+), epsilon_123=+1.  Rates are in Myr^-1,
   time is in Myr, and every product k dt is dimensionless. *)
ClearAll["Global`*"];

positiveAssumptions = dt > 0 && k > 0 && 0 < kl < ke < ku &&
  Element[{y0, y1, c, lambda, slack}, Reals];

(* One-mode endpoint reconstruction. *)
decay = Exp[-k dt];
aInverse = 1/(1 - decay);
yEq = y0 + aInverse (y1 - y0);
endpointIdentity = FullSimplify[
  yEq + (y0 - yEq) decay == y1,
  Assumptions -> dt > 0 && k > 0 && Element[{y0, y1}, Reals]
];

(* The two-mode convex weight reproduces the locked effective attenuation. *)
slowDecay = Exp[-kl dt];
fastDecay = Exp[-ku dt];
effectiveDecay = Exp[-ke dt];
slowWeight = (effectiveDecay - fastDecay)/(slowDecay - fastDecay);
twoModeIdentity = FullSimplify[
  slowWeight slowDecay + (1 - slowWeight) fastDecay == effectiveDecay,
  Assumptions -> dt > 0 && 0 < kl < ke < ku
];
twoModeWeightBounds = FullSimplify[
  0 < slowWeight < 1,
  Assumptions -> dt > 0 && 0 < kl < ke < ku
];

(* Derivatives used by the centered Taylor--Lagrange interval bound. *)
taylorDerivativeIdentity = And @@ Table[
  FullSimplify[
    D[Exp[-k t], {t, n}] == (-k)^n Exp[-k t],
    Assumptions -> k > 0 && Element[t, Reals]
  ],
  {n, 0, 8}
];

(* Single-row box Farkas construction.  For z_j in [0,1], the lower
   support value is Sum Min[g_j,0].  Bound columns cancel the row exactly. *)
gvec = Array[g, 6];
realG = And @@ Thread[Element[gvec, Reals]];
boundColumnIdentity = And @@ Map[
  FullSimplify[# - Max[#, 0] + Max[-#, 0] == 0,
    Assumptions -> Element[#, Reals]] &,
  gvec
];
rowMinimum = Total[Min[#, 0] & /@ gvec];
farkasRhsIdentity = FullSimplify[
  b + Total[Max[-#, 0] & /@ gvec] == b - rowMinimum,
  Assumptions -> realG && Element[b, Reals]
];
farkasNegativity = FullSimplify[
  Implies[rowMinimum > b, b - rowMinimum < 0],
  Assumptions -> realG && Element[b, Reals]
];

(* Generic KKT complementarity identities. *)
kktComplementarityActive = FullSimplify[lambda slack == 0 /. slack -> 0];
kktComplementarityInactive = FullSimplify[lambda slack == 0 /. lambda -> 0];

(* Structural zeros and the half-integer thermal-moment normalization used
   by the independent special-function auditor. *)
exactZeroIdentity = And @@ Thread[{kG2b, kG3, jG2b, jG3, heIIG3} == 0];
gammaHalfIdentity = FullSimplify[Gamma[3/2] == Sqrt[Pi]/2];

result = <|
  "endpointIdentity" -> endpointIdentity,
  "twoModeIdentity" -> twoModeIdentity,
  "twoModeWeightBounds" -> twoModeWeightBounds,
  "taylorDerivativeIdentity" -> taylorDerivativeIdentity,
  "boundColumnIdentity" -> boundColumnIdentity,
  "farkasRhsIdentity" -> farkasRhsIdentity,
  "farkasNegativity" -> farkasNegativity,
  "KKTComplementarityActive" -> kktComplementarityActive,
  "KKTComplementarityInactive" -> kktComplementarityInactive,
  "exactZeroIdentity" -> exactZeroIdentity,
  "gammaHalfIdentity" -> gammaHalfIdentity
|>;
Export["wolfram_r2c_r1_multirate_cone_validation_result.json", result, "RawJSON"];
If[And @@ Values[result], Exit[0], Exit[1]];
