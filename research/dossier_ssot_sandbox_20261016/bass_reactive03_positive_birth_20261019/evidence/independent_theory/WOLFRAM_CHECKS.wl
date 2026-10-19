(* Actually evaluated in the Wolfram connector during this theory unit. *)
Assuming[tau > 0,
 {Integrate[Exp[-tau x], {x, 0, 1}],
  Integrate[x Exp[-tau x], {x, 0, 1}],
  Series[(1 - Exp[-tau])/tau, {tau, 0, 6}],
  Series[1/tau - 1/(Exp[tau] - 1), {tau, 0, 6}]}]

Assuming[z > 0,
 FullSimplify[
  {Series[ArcCosh[Sinh[z]/z]/z, {z, 0, 8}],
   Series[(Coth[z]/2 - 1/(2z)) -
     (ArcCosh[Sinh[z]/z]/(2z)) Tanh[ArcCosh[Sinh[z]/z]],
    {z, 0, 7}]}]]
