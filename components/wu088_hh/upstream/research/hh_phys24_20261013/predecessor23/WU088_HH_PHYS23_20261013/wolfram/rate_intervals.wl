(* PHYS23. All T numbers denote kelvin and rates are cm^3/s. *)
ClearAll["Global`*"];
tt=N[Interval[{4999963846/100000,5000036154/100000}],50];
rMass=N[Interval[{0,1/1800}],50]; theta=157800/tt;
k=<|"LCS91"->12/10^18 tt^(6/5) Exp[-theta],
"HM89"->17/10^15 Sqrt[tt] Exp[-149000/tt],
"HM79"->98/10^16 Sqrt[tt] Exp[-theta],
"D69"->157/10^16 Sqrt[tt](1+2/theta)/(1+(2 rMass/theta)^2)Exp[-theta],
"KS91_G15"->465/10^23 tt^(3/2) Exp[-theta]|>;
outward[v_]:=ToString[#,InputForm]&/@{Floor[SetPrecision[Min[v],Infinity]10^40]/10^40,Ceiling[SetPrecision[Max[v],Infinity]10^40]/10^40};
exact=outward/@k;
point=Block[{tt=50000,theta=157800/50000,rMass=1/1837},<|"LCS91"->12/10^18 tt^(6/5)Exp[-theta],"HM89"->17/10^15 Sqrt[tt]Exp[-149000/tt],"HM79"->98/10^16 Sqrt[tt]Exp[-theta],"D69"->157/10^16 Sqrt[tt](1+2/theta)/(1+(2 rMass/theta)^2)Exp[-theta],"KS91_G15"->465/10^23 tt^(3/2)Exp[-theta]|>];
Print[ExportString[<|"status"->"COMPLETED_RATE_INTERVAL_EVALUATION","kernel"->System`$Version,"precision"->50,"T_box_K"->{"49999.63846","50000.36154"},"mass_ratio_box"->{"0","1/1800"},"point_mass_ratio"->"1/1837","rate_bounds_rational_cm3_s"->exact,"point_values_cm3_s"->(ToString[N[#,40],InputForm]&/@point),"all_positive"->And@@(Min[#]>0&/@Values[k])|>,"RawJSON"]];
