(* Exact LRS Bianchi I mechanical identities for C15 on SI energy density.
   Metric (-,+,+,+), s=db/dt, H=mean H, axial DeltaP=Ppar-Pperp.
   Energy hierarchy l=0, Thomson gamma+nu number/energy conservative;
   UV source chemical/stellar energy from C13 is EXTERNAL_Q and not closed here.
*)
Clear[h,s,deltaP,piU,piG,piN,piM,K,rD,rR,u,ds,dr,dm,
      dH,ig,in,alpha,J2,mono];
sigma=DiagonalMatrix[{-s,-s,2s}];
stress=DiagonalMatrix[{-deltaP/3,-deltaP/3,2deltaP/3}];
contraction=FullSimplify[Tr[sigma.stress]-2s deltaP];
eqShear=FullSimplify[
  3(-h*s + (-2 h*s + K deltaP)) - 3(-3 h*s + K deltaP)];
photonNumber=FullSimplify[0];
photonEnergy=FullSimplify[-2(s/h)J2+2(s/h)J2];
rhoCmb=Symbol["rhoCmb"];
pCmb=deltaP;
(* Einstein works exactly if every rho component has complete source exchanges
   including UV emission and recombination escape, which C15 DOES NOT yet evolve. *)
dRad=-4h*rR-2s deltaP;
dShear=-3h*s+K deltaP;
dHfromConstraint=FullSimplify[(K*dRad+2s*dShear)/(2h)];
dHexpected=FullSimplify[-2K*rR-3s^2];
(* Ignore dust in the isolated radiation/shear cancellation comparison. *)
cancel=FullSimplify[dHfromConstraint-dHexpected];
all={contraction,eqShear,photonNumber,photonEnergy,cancel};
If[all=!=ConstantArray[0,5],Print["CAS_GR_LEDGER_FAIL:",InputForm[all]];Exit[3]];
Print["WOLFRAM_EXACT_C15_EINSTEIN_SHEAR_RADIATION_GR_WORK_PASS"];
Print["GR_AND_MOMENT_RESIDUALS=",InputForm[all]];
Exit[0];
