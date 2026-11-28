h = awr a; ds = a + h - qs; qb = a + b - dd;
dh = h - b; ddel = ds - dd;
rh = h - (b + ee - bh); rd = ds - (dd + ee - bd);
uH = Array[uh, 4]; uD = Array[ud, 4]; qn = Array[nn, 4];
kg = qn + h uH - ds uD;
carrier = dh uH - ddel uD;
mb = a + b; ms = a + h;
wbl = Sqrt[mb^2 + 2 b es]; wsc = Sqrt[ms^2 + 2 h es];
kbl = wbl - mb; ksc = wsc - ms;
kbofeb = Sqrt[mb^2 + 2 b eb] - mb;
chi = kbofeb (2 ms + kbofeb)/(2 h);
wbofeb = mb + kbofeb; wsofmatched = ms + kbofeb;
estar = (ww^2 - dd^2)/(2 ww); kdstar = (ww - dd)^2/(2 ww);
gg = 1/Sqrt[1 - beta^2];
photonStar = {estar, estar Sqrt[1-mu^2], 0, estar mu};
daughterStar = {dd + kdstar, -estar Sqrt[1-mu^2], 0, -estar mu};
boost[v_] := {gg (v[[1]] + beta v[[4]]), v[[2]], v[[3]], gg (v[[4]] + beta v[[1]])};
norm[v_] := -v[[1]]^2 + v[[2]]^2 + v[[3]]^2 + v[[4]]^2;
assume = a>0 && b>0 && awr>0 && es>0 && eb>0 && ww>dd>0 && -1<beta<1 && -1<=mu<=1 &&
 Element[{a,b,awr,es,eb,ww,dd,beta,mu},Reals];
res = <|
 "mass_Q_decomposition" -> Expand[qs-qb-(bd-bh+rh-rd)],
 "mass_total_shifts" -> Expand[qs-qb-(dh-ddel)],
 "carrier_four_components" -> (Expand /@ (dd uD+kg-qn-b uH-carrier)),
 "LAB_log_source_Jacobian" -> FullSimplify[es D[kbl,es]-b es/wbl,assume],
 "COM_log_source_Jacobian" -> FullSimplify[es D[ksc,es]-h es/wsc,assume],
 "COM_inverse_map" -> FullSimplify[(chi/.eb->ksc (2mb+ksc)/(2b))-es,assume],
 "COM_derivative" -> FullSimplify[D[chi,eb]-b wsofmatched/(h wbofeb),assume],
 "rest_energy_closure" -> Together[dd+kdstar+estar-ww],
 "rest_daughter_shell" -> Together[norm[daughterStar]+dd^2],
 "rest_photon_shell" -> FullSimplify[norm[photonStar],assume],
 "boost_four_components" -> (FullSimplify[#,assume]& /@ (boost[photonStar]+boost[daughterStar]-{gg ww,0,0,gg beta ww})),
 "boost_daughter_shell" -> FullSimplify[norm[boost[daughterStar]]+dd^2,assume],
 "boost_photon_shell" -> FullSimplify[norm[boost[photonStar]],assume]
|>;
nominal = {a->93956542194/100,b->93827208943/100,dd->1875612945,
ee->51099895069/100000,awr->9991673/10000000,qs->2224648,
bh->13598434599702/1000000000000,bd->13602134636569/1000000000000};
numbers = <|"Q_source_minus_bare_eV"->(qs-qb/.nominal),
"binding_shift_eV"->(bd-bh/.nominal),
"rhoH_minus_rhoD_eV"->(rh-rd/.nominal),
"DeltaH_eV"->(dh/.nominal),"DeltaD_eV"->(ddel/.nominal),
"rhoH_eV"->(rh/.nominal),"rhoD_eV"->(rd/.nominal)|>;
ExportString[<|"schema"->"PHYS88_SYMBOLIC_REMAP_REFERENCE_V1","metric"->"-+++",
"residuals"->res,"all_zero"->And@@(TrueQ[#==0]& /@ Flatten[Values[res]]),
"COM_map_monotone"->FullSimplify[D[chi,eb]>0,assume],
"exact_nominal_strings"->Map[ToString[#,InputForm]&,numbers],
"nominal_decimal_20digit_strings"->Map[ToString[N[#,20],InputForm]&,numbers],
"scope"->"Exact algebra on symbols and displayed rational tokens; no physical CI or source-transfer proof"|>,"RawJSON"]
