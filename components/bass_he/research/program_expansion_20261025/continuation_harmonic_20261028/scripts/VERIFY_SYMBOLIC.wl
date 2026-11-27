(* HARMONIC10: one independent symbolic corroboration, frozen before runtime.
   Exact rational algebra plus explicitly labeled 130-digit Pi oracle checks.
   No external data acquisition, no production Python execution. *)
TimeConstrained[
 Module[{b, at, x, mu, t, a, w, lam, kap, k, n, i, res, flat, checks,
   p5, p239, pL, pU, piDec, orient, eighth, rho2, rho8, outside0, outsideC,
   y, ha, naive, trigErrS, trigErrC, output},
  b[n_, i_, x_] := Binomial[n, i] x^i (1-x)^(n-i);
  at[d_, m_] := Sum[(-1)^j/( (2 j+1) d^(2 j+1)), {j,0,m-1}];
  p5 = {at[5,24],at[5,24]+1/(49*5^49)};
  p239 = {at[239,8],at[239,8]+1/(17*239^17)};
  pL = Floor[2^96 (16 p5[[1]]-4 p239[[2]])]/2^96;
  pU = Ceiling[2^96 (16 p5[[2]]-4 p239[[1]])]/2^96;
  piDec = 31415926535897932384626433832795028841971693993751058209749445923078164062862089986280348253421170679/10^100;
  orient = 2 Integrate[1+lam Cos[4 Pi t]+kap Sin[4 Pi t],{t,a,a+w}];
  eighth = 1/4+((lam+kap) Cos[4 Pi a]+(kap-lam) Sin[4 Pi a])/(2 Pi);
  rho2 = Sum[{1/2,-1/2,1/2}[[i+1]] b[2,i,(mu+1)/2],{i,0,2}];
  rho8 = Sum[(-1)^i/2 b[8,i,(mu+1)/2],{i,0,8}];
  outside0 = Sum[{1,0,1}[[i+1]] b[2,i,(mu+1)/2],{i,0,2}];
  outsideC = Sum[{0,1/2,0}[[i+1]] b[2,i,(mu+1)/2],{i,0,2}];
  y = (1-k)/8+(1-k^3)/(12 Pi);
  ha = (1+k)/8+(1+k^3)/(12 Pi);
  naive = (1-k)/8+(1-k)/(12 Pi);
  trigErrS = 2 (2^41/41!+2^-94)+2*2^-88;
  trigErrC = 2 (2^40/40!+2^-94)+2*2^-88;
  res = <|
   "bernstein_normalization" -> Flatten[Table[
     Simplify[2 Integrate[b[n,i,x],{x,0,1}]-2/(n+1)],{n,0,8},{i,0,n}]],
   "bernstein_reflection" -> Flatten[Table[
     Expand[b[n,i,(1-mu)/2]-b[n,n-i,(1+mu)/2]],{n,0,8},{i,0,n}]],
   "harmonic_primitives" -> {
     Simplify[D[Sin[4 Pi t]/(4 Pi),t]-Cos[4 Pi t]],
     Simplify[D[-Cos[4 Pi t]/(4 Pi),t]-Sin[4 Pi t]],
     FullSimplify[Integrate[Cos[4 Pi t],{t,a,a+1/2}],Element[a,Reals]],
     FullSimplify[Integrate[Sin[4 Pi t],{t,a,a+1/2}],Element[a,Reals]]},
   "machin" -> {
     FullSimplify[16 ArcTan[1/5]-4 ArcTan[1/239]-Pi],
     FullSimplify[Tan[4 ArcTan[1/5]-ArcTan[1/239]]-1]},
   "polynomial_examples" -> {
     Expand[rho2-mu^2/2],Expand[rho8-mu^8/2],
     Expand[outside0-outsideC-(1+3 mu^2)/4],
     Simplify[Integrate[rho2,{mu,-1,1}]-1/3]},
   "orientation" -> {
     FullSimplify[TrigExpand[(orient/.w->1/8)-eighth],Element[{a,lam,kap},Reals]],
     Simplify[(eighth/.{a->0,lam->3/5,kap->4/5})-(1/4+7/(10 Pi))],
     Simplify[(eighth/.{a->1/8,lam->3/5,kap->4/5})-(1/4+1/(10 Pi))],
     Simplify[(eighth/.{a->1/4,lam->3/5,kap->4/5})-(1/4-7/(10 Pi))],
     Simplify[(eighth/.{a->3/8,lam->3/5,kap->4/5})-(1/4-1/(10 Pi))]},
   "nonseparable" -> {
     Simplify[2 Integrate[1/16+mu^2/(8 Pi),{mu,-1,1}]-(1/4+1/(6 Pi))],
     Simplify[2 Integrate[1/16+mu^2/(8 Pi),{mu,k,1}]-y],
     Simplify[2 Integrate[1/16+mu^2/(8 Pi),{mu,-k,1}]-ha],
     Simplify[y-naive-(k-k^3)/(12 Pi)]},
   "rotation" -> {
     FullSimplify[TrigExpand[
      lam Cos[4 Pi (t+a)]+kap Sin[4 Pi (t+a)]-
      ((lam Cos[4 Pi a]+kap Sin[4 Pi a]) Cos[4 Pi t]+
       (-lam Sin[4 Pi a]+kap Cos[4 Pi a]) Sin[4 Pi t])],
       Element[{t,a,lam,kap},Reals]],
     Simplify[(lam Cos[4 Pi a]+kap Sin[4 Pi a])/.a->1/8]-kap,
     Simplify[(-lam Sin[4 Pi a]+kap Cos[4 Pi a])/.a->1/8]+lam},
   "same_event_symmetry" -> {
     FullSimplify[Cos[4 Pi(t+1/2)]-Cos[4 Pi t],Element[t,Reals]],
     FullSimplify[Sin[4 Pi(t+1/2)]-Sin[4 Pi t],Element[t,Reals]],
     Integrate[mu rho2,{mu,-1,1}]},
   "cone_examples" -> {(3/5)^2+(4/5)^2-1,(3/2)^2-(9/10)^2-(6/5)^2}
  |>;
  flat = Join@@Values[res];
  checks = <|
   "pi_width_lt_2pow_minus94" -> (pU-pL<2^-94),
   "pi_lower_gt3" -> (pL>3),
   "pi_enclosure_lower_numeric130" -> (N[Pi-pL,130]>0),
   "pi_enclosure_upper_numeric130" -> (N[pU-Pi,130]>0),
   "independent_decimal_pi_lower_numeric130" -> (N[Pi-piDec,130]>0),
   "independent_decimal_pi_upper_numeric130" -> (N[piDec+10^-100-Pi,130]>0),
   "sin_width_lt_2pow_minus86" -> (trigErrS<2^-86),
   "cos_width_lt_2pow_minus86" -> (trigErrC<2^-86),
   "primitive_width_lt_2pow_minus84" -> (2^-85/12+2*2^-92/144<2^-84),
   "default_width_lt_epsilon" -> (2^-41+260*2^-84<2^-40),
   "max52_bisections_sufficient" -> (2/2^52<=1/(1440*2^40)),
   "nonseparable_gap_positive_at_40over51" -> ((40/51-(40/51)^3)/(12 Pi)>0),
   "positive_outside_cone_min" -> (1/4>0),
   "outside_cone_middle_rejected" -> (0^2<(1/2)^2)
  |>;
  output = <|
   "schema"->"HARMONIC10_WOLFRAM_CORROBORATION_V1",
   "residuals"->Association[KeyValueMap[
       Function[{key,values},key->(ToString[#,InputForm]& /@ values)],res]],
   "residual_count"->Length[flat],
   "literal_zero_count"->Count[flat,v_/;SameQ[v,0]],
   "all_residuals_literal_zero"->And@@(SameQ[#,0]& /@ flat),
   "checks"->Association[KeyValueMap[
       Function[{key,value},key->ToString[value,InputForm]],checks]],
   "boolean_check_count"->Length[checks],
   "all_checks_true"->And@@(TrueQ /@ Values[checks]),
   "pi_interval"->{ToString[pL,InputForm],ToString[pU,InputForm]},
   "mixed_k"->"40/51",
   "mixed_oracle_decimal30"->(ToString[N[#,30],InputForm]& /@
     ({y,ha,y/ha,y-naive}/.k->40/51)),
   "remote_cpu_s"->Null,
   "timing_scope"->"Remote tool provides no measured kernel CPU in this result; numeric130 labels identify high-precision oracle comparisons",
   "physical_inputs_closed"->0
  |>;
  ExportString[output,"RawJSON"]
 ],15,"TIME_LIMIT_EXCEEDED"]
