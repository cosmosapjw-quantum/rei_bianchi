(* PHYS48 source-locked central Coulomb barrier. EXACT symbolic checks. *)
ClearAll["Global`*"];
kap48=7/10; B48=20;
pot48[r_,L_]:=L/r^2-2/r-kap48^2;
turn48[L_]:=(Sqrt[1+kap48^2 L]-1)/kap48^2;
check48={
 FullSimplify[pot48[turn48[L],L],Assumptions->L>0],
 FullSimplify[D[pot48[r,L],r]-2(r-L)/r^3],
 FullSimplify[turn48[L]<L,Assumptions->L>0],
 FullSimplify[pot48[B48,210]+13/200],
 FullSimplify[pot48[B48,240]-1/100]
};
Print["PHYS48_BARRIER_SYMBOLIC_CHECK=",check48];
If[!TrueQ[check48==={0,0,True,0,0}],Quit[2]];
angles48={14,15,20,21,24,28,33,41,61,80,120};
radii48=Table[{l,N[turn48[l(l+1)],35]}, {l,angles48}];
Print["PHYS48_TURNING_RADIUS_REFERENCE=",radii48];
Print["PHYS48_WOLFRAM_PASS=True"];
Quit[];
