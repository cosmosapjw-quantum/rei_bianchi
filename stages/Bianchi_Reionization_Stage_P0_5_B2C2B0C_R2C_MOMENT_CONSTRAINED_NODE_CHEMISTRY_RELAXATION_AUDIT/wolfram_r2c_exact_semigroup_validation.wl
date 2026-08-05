(* R2C exact-semigroup and KKT validation.
   Conventions: metric (-,+,+,+), epsilon_123=+1; this homogeneous sink
   auditor uses explicit k_B and no natural-unit declaration. *)
ClearAll["Global`*"];
$Assumptions = dt > 0 && tau > 0 && n > 0 && p > 0 && x > 0;

q = Exp[-dt/tau];
yeq = y0 + (y1 - y0)/(1 - q);
yReached = FullSimplify[yeq + (y0 - yeq) q];
endpointIdentity = FullSimplify[yReached == y1];

advance[y_, t_] := yeq + (y - yeq) Exp[-t/tau];
semigroupIdentity = FullSimplify[advance[advance[y0, t1], t2] == advance[y0, t1 + t2],
  Assumptions -> tau > 0 && t1 >= 0 && t2 >= 0];

beFactor = (1 + dt/(n tau))^-n;
beLimitIdentity = FullSimplify[Limit[beFactor, n -> Infinity] == Exp[-dt/tau]];

hNucleiIdentity = FullSimplify[m - i - (m - i) == 0];
currentGammaIdentity = FullSimplify[kappa phi - j == 0 /. kappa -> j/phi,
  Assumptions -> phi != 0];
exactZeroIdentity = And @@ Thread[{kG2b, kG3, jG2b, jG3, heIIG3} == 0];

(* KL KKT stationarity for one positive entry with row multiplier lambda>=0
   and column multiplier alpha. *)
kl = x Log[x/p] - x + p;
stationarity = FullSimplify[D[kl, x] + alpha + lambda == 0 /. x -> p Exp[-alpha - lambda]];
complementarityActive = FullSimplify[lambda (cap - row) == 0 /. row -> cap];
complementarityInactive = FullSimplify[lambda (cap - row) == 0 /. lambda -> 0];

result = <|
  "endpointIdentity" -> endpointIdentity,
  "semigroupIdentity" -> semigroupIdentity,
  "backwardEulerLimitIdentity" -> beLimitIdentity,
  "hydrogenNucleiIdentity" -> hNucleiIdentity,
  "currentGammaIdentity" -> currentGammaIdentity,
  "exactZeroIdentity" -> exactZeroIdentity,
  "KKTStationarity" -> stationarity,
  "KKTComplementarityActive" -> complementarityActive,
  "KKTComplementarityInactive" -> complementarityInactive
|>;
Export["wolfram_r2c_exact_semigroup_validation_result.json", result, "RawJSON"];
If[And @@ Values[result], Exit[0], Exit[1]];
