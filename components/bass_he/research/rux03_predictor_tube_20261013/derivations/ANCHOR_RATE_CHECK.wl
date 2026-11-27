(* THEORY07 new point intervals. Reuses THEORY06 proven helper structure; power grid is 10^24. *)
anchorSeconds=AbsoluteTiming[
 anchorResult=Catch[
  anchorChecks = <||>; powerWitnesses = {}; expWitnesses = {};
  addAnchorCheck[name_, value_] := AssociateTo[anchorChecks, name -> TrueQ[value]];
  powPoint[x_, a_] := Module[{pn, qn, grid, k, lo, hi, ok},
    If[!TrueQ[x > 0] || !MatchQ[x, _Integer | _Rational] ||
       !MatchQ[a, _Integer | _Rational],
       Throw[<|"status" -> "FAILED_INTERVAL_INPUT"|>, "anchorRate"]];
    pn = Numerator[a]; qn = Denominator[a];
    If[qn == 1, Return[{x^pn, x^pn}]];
    grid = 10^24;
    k = Floor[N[grid x^a, 80]];
    lo = (k - 1)/grid; hi = (k + 2)/grid;
    ok = TrueQ[0 < lo <= hi && lo^qn <= x^pn <= hi^qn];
    AppendTo[powerWitnesses, ok];
    If[!ok, Throw[<|"status" -> "FAILED_EXACT_POWER_BRACKET",
       "base" -> ToString[x, InputForm],
       "exponent" -> ToString[a, InputForm]|>, "anchorRate"]];
    {lo, hi}
  ];
  pb[u_, a_] := Module[{l, r},
    If[u[[1]] == u[[2]], Return[powPoint[u[[1]], a]]];
    If[a >= 0,
      l = powPoint[u[[1]], a][[1]]; r = powPoint[u[[2]], a][[2]],
      l = powPoint[u[[2]], a][[1]]; r = powPoint[u[[1]], a][[2]]];
    {l, r}
  ];
  ab[u_, v_] := {u[[1]] + v[[1]], u[[2]] + v[[2]]};
  mb[u_, v_] := {u[[1]] v[[1]], u[[2]] v[[2]]};
  db[u_, v_] := {u[[1]]/v[[2]], u[[2]]/v[[1]]};
  sb[k_, u_] := {k u[[1]], k u[[2]]};
  oneb = {1, 1};
  expNegativeBox[x_] := Module[{nn = 64, ss, next, upperTail, ok},
    ok = TrueQ[0 <= x < nn + 2];
    AppendTo[expWitnesses, ok];
    If[!ok, Throw[<|"status" -> "FAILED_EXP_TAIL_DOMAIN"|>, "anchorRate"]];
    ss = Sum[x^j/j!, {j, 0, nn}];
    next = x^(nn + 1)/(nn + 1)!;
    upperTail = next/(1 - x/(nn + 2));
    {1/(ss + upperTail), 1/ss}
  ];
  disp[x_] := ToString[N[x, 20], InputForm];
  strs[x_] := Map[ToString[#, InputForm] &, x, {-1}];
  kb = 1380649/10^22; eps = 1602176634/10^21;
  lightc = 29979245800; nucD = 1/1000; fhe = 2/25;
  lamVec = {315614, 570670, 1263030};
  ciAmp = {2111/100, 1619/50, 399/20};
  ciP = {-1089/1000, -573/500, -1089/1000};
  ciC = {177/500, 52/125, 553/1000};
  ciR = {437/500, 987/1000, 147/200};
  ciD = {1101/1000, 132/125, 51/40};
  rrA = 1503/1000; rrB = 1923/1000; rrQ = 47/100;
  rrC = 261/500;
  drB1 = (4049664394833662/10^14) 11605;
  drB2 = (8099328789667/10^12) 11605;
  drExponent = {drB1, drB1 + drB2};
  drFactor = {1, 3/10};
  drEnergies = kb drExponent;
  bindingEV = {13598434599702/10^12, 24587389011/10^9, 5441776/10^5};
  rrBox[i_, temp_] := Module[{l = lamVec[[i]]/temp, u, num, den, pref},
    If[i == 2, Return[sb[3/10^14, pb[{l, l}, 327/500]]]];
    pref = If[i == 3, 2, 1];
    u = pb[{l/rrC, l/rrC}, rrQ];
    num = sb[pref 1269/10^16, pb[{l, l}, rrA]];
    den = pb[ab[oneb, u], rrB];
    db[num, den]
  ];
  ciBox[i_, temp_] := Module[{l = lamVec[[i]]/temp, v, val, den},
    val = sb[ciAmp[[i]], pb[{temp, temp}, -3/2]];
    val = mb[val, expNegativeBox[l/2]];
    val = mb[val, pb[{l, l}, ciP[[i]]]];
    v = pb[{l/ciC[[i]], l/ciC[[i]]}, ciR[[i]]];
    den = pb[ab[oneb, v], ciD[[i]]];
    db[val, den]
  ];
  drBox[i_, temp_] := Module[{val},
    val = sb[drFactor[[i]] 154/10^11,
      pb[{11605/temp, 11605/temp}, 3/2]];
    mb[val, expNegativeBox[drExponent[[i]]/temp]]
  ];
  vernerPars = {
    {2149/5000, 54750, 822/25, 2963/1000, 0, 0, 0},
    {1361/100, 4746/5, 1469/1000, 797/250,
      2039/1000, 2217/5000, 267/125},
    {43/25, 13690, 822/25, 2963/1000, 0, 0, 0}};

  tempStar = 50000; oldH = 500000000; newH = 1000000000;
  betaStar = {0, 0, 41/841}; gammaStar = 841/840;
  zetaStar = {1/2, 1/50, 1/50};
  lower = {1/2, 1/25, 1/50}; upper = zetaStar;
  electron = 14/25; pOld = 1/100;
  dirs = {{1,0,0},{-1,0,0},{0,1,0},{0,-1,0},{0,0,1},{0,0,-1}};
  labE = {23,23,35,35,70,70};
  rayb = (1 - betaStar.#)& /@ dirs;
  deltaStar = gammaStar rayb; restE = deltaStar labE;
  thresholds = {68/5,2459/100,2721/50};
  active = Table[restE[[j]] > thresholds[[i]], {i,3},{j,6}];
  expectedActive = {{True,True,True,True,True,True},
    {False,False,True,True,True,True},{False,False,False,False,True,True}};
  addAnchorCheck["A01_anchor_Doppler", gammaStar^2 (1-betaStar.betaStar)==1 &&
    restE == {19343/840,19343/840,841/24,841/24,200/3,147/2} &&
    electron == zetaStar.{1,1,2}];
  addAnchorCheck["A02_cutoff_cell", active==expectedActive &&
    Count[Flatten[active],True]==12];
  rrRaw = Table[rrBox[i,tempStar],{i,3}];
  ciRaw = Table[ciBox[i,tempStar],{i,3}];
  drRaw = Table[drBox[i,tempStar],{i,2}];
  rrHeatFactor[i_] := Module[{l,u,ratio},
    If[i==2,Return[{423/500,423/500}]];
    l=lamVec[[i]]/tempStar;u=pb[{l/rrC,l/rrC},rrQ];
    ratio=db[u,ab[oneb,u]];
    ab[{3/2-rrA,3/2-rrA},sb[rrB rrQ,ratio]]
  ];
  rrKinRaw = Table[sb[kb tempStar,mb[rrRaw[[i]],rrHeatFactor[i]]],{i,3}];
  drKinRaw = Table[sb[drEnergies[[i]],drRaw[[i]]],{i,2}];
  vernerPoint[i_,j_] := Module[
    {e0,sig0,ya,pv,yw,y0,y1,xx,yy,ff,v,den},
    If[!active[[i,j]],Return[{0,0}]];
    {e0,sig0,ya,pv,yw,y0,y1}=vernerPars[[i]];
    xx=restE[[j]]/e0-y0;
    If[!TrueQ[xx>1],Throw[<|"status"->"BAD_VERNER_DOMAIN"|>,"anchorRate"]];
    yy=pb[{xx^2+y1^2,xx^2+y1^2},1/2];
    ff=(xx-1)^2+yw^2;
    v=sb[ff,pb[yy,pv/2-11/2]];
    den=pb[ab[oneb,pb[sb[1/ya,yy],1/2]],pv];
    sb[sig0/10^18,db[v,den]]
  ];
  sigRaw=Table[vernerPoint[i,j],{i,3},{j,6}];
  compact[u_,digits_] := {Floor[u[[1]]10^digits],Ceiling[u[[2]]10^digits]}/10^digits;
  rr=compact[#,30]& /@ rrRaw;ci=compact[#,30]& /@ ciRaw;
  dr=compact[#,30]& /@ drRaw;rrKin=compact[#,40]& /@ rrKinRaw;
  drKin=compact[#,40]& /@ drKinRaw;
  sig=Map[compact[#,34]&,sigRaw,{2}];
  enclosing[raw_,outer_]:=TrueQ[outer[[1]]<=raw[[1]]<=raw[[2]]<=outer[[2]]];
  narrow[u_]:=TrueQ[0<u[[1]]<=u[[2]] && u[[2]]-u[[1]]<u[[1]]/10^11];
  atomBoxes=Join[rr,ci,dr,rrKin,drKin];
  addAnchorCheck["A03_atomic_intervals",And@@(narrow/@atomBoxes)];
  addAnchorCheck["A04_sigma_intervals",And@@Flatten[
    Table[If[active[[i,j]],narrow[sig[[i,j]]],sig[[i,j]]=={0,0}],{i,3},{j,6}]]];
  addAnchorCheck["A05_outward_compaction",
    And@@MapThread[enclosing,{Join[rrRaw,ciRaw,drRaw,rrKinRaw,drKinRaw],
      atomBoxes}] && And@@Flatten[Table[enclosing[sigRaw[[i,j]],sig[[i,j]]],{i,3},{j,6}]]];
  addAnchorCheck["A06_exact_power_exp_witnesses",
    And@@powerWitnesses && And@@expWitnesses];
  mid[u_]:=Total[u]/2;rad[u_]:=(u[[2]]-u[[1]])/2;
  rrMid=mid/@rr;ciMid=mid/@ci;drMid=mid/@dr;
  rrKinMid=mid/@rrKin;drKinMid=mid/@drKin;
  sigMid=Map[mid,sig,{2}];
  lambdaMid=Table[lightc nucD lower[[i]]rayb[[j]]sigMid[[i,j]],{i,3},{j,6}];
  lambdaTotal=Total[lambdaMid];
  fac=nucD gammaStar^(-2)electron;
  rateCI=fac lower ciMid;rateRR=fac upper rrMid;
  rateDR=fac upper[[2]]drMid;
  kin=fac (upper.rrKinMid+upper[[2]]Total[drKinMid])/eps;
  bind=bindingEV.rateRR+bindingEV[[2]]Total[rateDR];
  bindingStar=bindingEV.{zetaStar[[1]],zetaStar[[2]]+zetaStar[[3]],zetaStar[[3]]};
  amin=10^9+bindingStar;
  predRows={1,2,3,4,7};
  predA={
    1000(rateCI[[1]]-rateRR[[1]]),
    1000(rateCI[[2]]-rateRR[[2]]-rateCI[[3]]+rateRR[[3]]-Total[rateDR]),
    1000(rateCI[[3]]-rateRR[[3]]),
    -4(bindingEV.rateCI+kin),
    -10^6 (41/840)(kin+bind)};
  predB=Table[{
    1000pOld lambdaMid[[1,j]],
    1000pOld(lambdaMid[[2,j]]-lambdaMid[[3,j]]),
    1000pOld lambdaMid[[3,j]],
    4pOld Total[Table[(restE[[j]]-bindingEV[[i]])lambdaMid[[i,j]],{i,3}]],
    10^6 pOld labE[[j]]dirs[[j,3]]lambdaTotal[[j]]
   },{j,6}]//Transpose;
  photo[h_]:=Table[pOld lambdaMid[[i,j]]/(1+h lambdaTotal[[j]]),{i,3},{j,6}];
  ph=photo[hh];ps=Total/@ph;
  direct={
    1000(ps[[1]]+rateCI[[1]]-rateRR[[1]]),
    1000(ps[[2]]+rateCI[[2]]-rateRR[[2]]-ps[[3]]-rateCI[[3]]+
      rateRR[[3]]-Total[rateDR]),
    1000(ps[[3]]+rateCI[[3]]-rateRR[[3]]),
    4(Total[Flatten[Table[(restE[[j]]-bindingEV[[i]])ph[[i,j]],
      {i,3},{j,6}]]]-bindingEV.rateCI-kin),
    10^6(Total[Table[labE[[j]]dirs[[j,3]]Total[ph[[All,j]]],{j,6}]]-
      (41/840)(kin+bind))};
  compactG=predA+predB.(1/(1+hh lambdaTotal));
  addAnchorCheck["A07_full_predictor_representation",
    And@@(Together[#]==0& /@ (direct-compactG)) &&
    bindingStar==8871068060291/10^12];
  transverse=Table[Total[Table[labE[[j]]dirs[[j,k]]Total[ph[[All,j]]],{j,6}]],{k,2}];
  addAnchorCheck["A08_pair_parity_and_denominators",
    lambdaMid[[All,1]]==lambdaMid[[All,2]] &&
    lambdaMid[[All,3]]==lambdaMid[[All,4]] &&
    And@@(Together[#]==0& /@ transverse) &&
    And@@Thread[lambdaTotal>0] && Min[Flatten[lambdaMid]]>=0];
  rough5=newH Abs[predA]+(Abs[predB]).(newH/(1+newH lambdaTotal));
  rough7={rough5[[1]],rough5[[2]],rough5[[3]],rough5[[4]],0,0,rough5[[5]]/amin};
  roughCap=Ceiling[10^12 rough7]/10^12;
  phRad=pOld Table[
    lightc nucD lower[[i]]rayb[[j]]rad[sig[[i,j]]]+
    newH lambdaMid[[i,j]]Total[Table[
      lightc nucD lower[[k]]rayb[[j]]rad[sig[[k,j]]],{k,3}]],{i,3},{j,6}];
  ciRad=fac lower(rad/@ci);rrRad=fac upper(rad/@rr);drRad=fac upper[[2]](rad/@dr);
  kinRad=fac(upper.(rad/@rrKin)+upper[[2]]Total[rad/@drKin])/eps;
  bindRad=bindingEV.rrRad+bindingEV[[2]]Total[drRad];
  phRadEdge=Total/@phRad;
  err7=newH{
    1000(phRadEdge[[1]]+ciRad[[1]]+rrRad[[1]]),
    1000(Total[phRadEdge[[{2,3}]]]+Total[ciRad[[{2,3}]]]+
      Total[rrRad[[{2,3}]]]+Total[drRad]),
    1000(phRadEdge[[3]]+ciRad[[3]]+rrRad[[3]]),
    4(Total[Flatten[Table[Abs[restE[[j]]-bindingEV[[i]]]phRad[[i,j]],
      {i,3},{j,6}]]]+bindingEV.ciRad+kinRad),
    0,0,
    10^6/amin(Total[Table[labE[[j]]Abs[dirs[[j,3]]]Total[phRad[[All,j]]],{j,6}]]+
      (41/840)(kinRad+bindRad))};
  errCap=Ceiling[10^25 err7]/10^25;
  addAnchorCheck["A09_uniform_h_rounding_bounds",
    And@@Thread[roughCap>=rough7] && And@@Thread[errCap>=err7] &&
    And@@Thread[err7>=0] &&
    Together[D[hh/(1+hh ll),hh]-1/(1+hh ll)^2]==0];
  addAnchorCheck["A10_midpoint_accuracy",
    Max[errCap]<1/10^11];
  getGrid[x_,digits_]:=strs[10^digits x];
  midDisplay=<|"CI"->(disp/@ciMid),"RR"->(disp/@rrMid),"DR"->(disp/@drMid),
    "K_eV_H_s"->disp[kin],"Besc_eV_H_s"->disp[bind],
    "lambda_s"->(disp/@lambdaTotal)|>;
  <|"schema"->"he07-anchor-v1","unit"->"HERE_RUX03_PREDICTOR_TUBE_AND_REANCHORED_FAMILY_07",
    "status"->If[And@@Values[anchorChecks],"PASS","FAIL"],
    "checks"->anchorChecks,"groups"->Length[anchorChecks],
    "witnesses"->{Length[powerWitnesses],Length[expWitnesses]},
    "source"->"a5c958c414dea41216b445c05f58df837f05cacb",
    "grid_exponents"-><|"rates"->-30,"kinetic_erg"->-40,"sigma_cm2"->-34|>,
    "CI"->getGrid[ci,30],"RR"->getGrid[rr,30],"DR"->getGrid[dr,30],
    "KRR"->getGrid[rrKin,40],"KDR"->getGrid[drKin,40],
    "sigma"->getGrid[sig,34],"rest_E_eV"->strs[restE],
    "predictor"-><|"rows"->predRows,
      "formula"->"p_rows=h*(A+B.(1/(1+h*Lambda))); row7 also divided by aStar=mu+Bstar; rows5,6=0",
      "A"->strs[predA],"B"->strs[predB],"Lambda"->strs[lambdaTotal],
      "Bstar"->ToString[bindingStar,InputForm],"H"->newH,
      "uniform_abs_X_cap"->strs[roughCap],
      "uniform_point_midpoint_error_cap"->strs[errCap],
      "Pnorm_cap"->ToString[Max[roughCap],InputForm],
      "Pnorm_lt_one"->TrueQ[Max[roughCap]<1],
      "p_at_H_display"->(disp/@Join[
        (newH(compactG/.hh->newH))[[1;;4]],{0,0},
        {newH(compactG/.hh->newH)[[5]]/amin}])|>,
    "display"->midDisplay,
    "scope"->"New anchor coefficients and rational predictor only; retained full-box checks rerun 0; native/RHS/ODE/Python science 0."
  |>
,"anchorRate"];
][[1]];
anchorResult=Join[anchorResult,<|"seconds"->anchorSeconds,"kernel"->$Version,"system"->$SystemID|>];
ExportString[anchorResult,"RawJSON","Compact"->True]
