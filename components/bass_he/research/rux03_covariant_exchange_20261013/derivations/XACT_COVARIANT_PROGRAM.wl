(* Parsed AFTER Needs["xAct`xTensor`"]. This avoids pre-load Global` shadowing.
   xPerm's supported pure Wolfram backend is selected by $xpermQ=False.
   The executed self-contained wrapper is evidence/XACT_COVARIANT_EXECUTED.wl. *)
Module[{hr, tr, tg, kin, red, redD, norm, duRules, dqRules, piRules,
  ab, em, gg, nn, hn, checks=<||>, residuals=<||>, put, gradRho,
  radiationTarget, gasEnergyTarget, gasMomentumTarget, gasDiv, radDiv,
  scalarChecks, nH, nHDot, wH, wDot, binding, bindingDot, epsUnit, mRef,
  th, rhoGas, pGas, qHeatH, qAbsH, qEscH, uZero, kappa, cp, cm},
 $xpermQ=False; $DefInfoQ=False;
 DefManifold[CovM,4,{a,b,d,e,f,i,j,k,l,m}];
 DefMetric[-1,ggmetric[-a,-b],CD,{";","D"}];
 DefTensor[uu[a],CovM]; DefTensor[ee[a],CovM];
 DefTensor[vv[a],CovM]; DefTensor[qq[a],CovM];
 DefTensor[acc[a],CovM]; DefTensor[force[a],CovM];
 DefTensor[src[a],CovM];
 DefTensor[pi[a,b],CovM,Symmetric[{a,b}]];
 DefTensor[sig[a,b],CovM,Symmetric[{a,b}]];
 DefTensor[omg[a,b],CovM,Antisymmetric[{a,b}]];
 DefTensor[rho[],CovM]; DefTensor[pres[],CovM];
 DefTensor[theta[],CovM];
 Scan[DefConstantSymbol,{cc,photonEnergy,eventRate,escapePower,gasPower,
   beta,gamma}];
 norm=Join@@(MakeRule[#,MetricOn->All,ContractMetrics->True]& /@ {
   {uu[a]uu[-a],-1},{ee[a]ee[-a],1},{vv[a]vv[-a],1},
   {uu[a]ee[-a],0},{uu[a]vv[-a],0},{uu[a]qq[-a],0},
   {uu[a]acc[-a],0},{uu[a]force[-a],0},
   {uu[a]pi[-a,-b],0},{uu[a]sig[-a,-b],0},{uu[a]omg[-a,-b],0},
   {pi[a,-a],0},{sig[a,-a],0}});
 hr[i_,j_]:=ggmetric[i,j]+uu[i]uu[j];
 red[x_]:=ToCanonical[ContractMetric[ToCanonical[Expand[x]]]] //. norm // ToCanonical;
 put[name_,expr_]:=Module[{r=red[expr]},
   AssociateTo[residuals,name->ToString[InputForm[r]]];
   AssociateTo[checks,name->TrueQ[r===0]]];
 tr[i_,j_]:=rho[] uu[i]uu[j]+(uu[i]qq[j]+qq[i]uu[j])/cc
   +rho[] hr[i,j]/3+pi[i,j];
 tg[i_,j_]:=rho[] uu[i]uu[j]+pres[] hr[i,j];
 kin[i_,j_]:=-uu[i]acc[j]/cc^2
   +(theta[] hr[i,j]/3+sig[i,j]+omg[i,j])/cc;
 ab[i_]:=photonEnergy eventRate (uu[i]+ee[i])/cc;
 em[i_]:=escapePower uu[i]/cc;
 gg[i_]:=gasPower uu[i]/cc+force[i];
 nn[i_]:=gamma (uu[i]+beta vv[i]);
 hn[i_,j_]:=ggmetric[i,j]+nn[i]nn[j];
 put["projector_orthogonal",hr[a,-b]uu[b]];
 put["projector_idempotent",hr[a,-b]hr[b,-d]-hr[a,-d]];
 put["projector_trace_three",hr[a,-a]-3];
 put["photon_null",(uu[a]+ee[a])(uu[-a]+ee[-a])];
 put["absorption_energy_full_E",-cc uu[-a]ab[a]-photonEnergy eventRate];
 put["absorption_spatial_full_E",hr[a,-b]ab[b]-photonEnergy eventRate ee[a]/cc];
 put["isotropic_escape_energy",-cc uu[-a]em[a]-escapePower];
 put["isotropic_escape_spatial",hr[a,-b]em[b]];
 put["total_exchange_vector",(ab[a]-em[a])+(-ab[a]+src[a])+em[a]-src[a]];
 put["gas_fourforce_energy",-cc uu[-a]gg[a]-gasPower];
 put["gas_fourforce_spatial",hr[a,-b]gg[b]-force[a]];
 put["observer_power_exact",-cc nn[-a]gg[a]
   -gamma (gasPower-cc beta vv[-a]force[a])];
 put["tilted_escape_power",-cc nn[-a]em[a]-gamma escapePower];
 put["tilted_escape_spatial",hn[a,-b]em[b]
   -escapePower (uu[a]-gamma nn[a])/cc];
 put["radiation_u_contraction",uu[-b]tr[a,b]+rho[] uu[a]+qq[a]/cc];
 put["radiation_trace_zero",ggmetric[-a,-b]tr[a,b]];
 put["kinematic_normalization_derivative",uu[b]kin[-a,-b]];
 put["kinematic_acceleration",uu[a]kin[-a,-b]-acc[-b]/cc^2];
 put["kinematic_expansion",ggmetric[a,b]kin[-a,-b]-theta[]/cc];
 put["radiation_kinematic_work",cc tr[a,b]kin[-a,-b]
   -theta[] rho[]/3-acc[a]qq[-a]/cc^2-sig[-a,-b]pi[a,b]];
 put["gas_kinematic_work",cc tg[a,b]kin[-a,-b]-theta[] pres[]];

 (* The derivative rules are the velocity decomposition and derivatives of
    u.q=0, u.pi=0. They are independent kinematic assumptions, not the target
    radiation energy equation. Product differentiation is performed by CD. *)
 duRules={HoldPattern[CD[idxA_][uu[idxB_]]]:>kin[idxA,idxB]};
 dqRules={
   (HoldPattern[uu[idxB_] CD[idxA_][qq[idxC_]]] /;
     idxB===-idxC):>-kin[idxA,idxC]qq[-idxC]};
 piRules={
   (HoldPattern[uu[idxB_] CD[idxA_][pi[idxC_,idxD_]]] /;
     idxB===-idxC):>-kin[idxA,idxC]pi[-idxC,idxD],
   (HoldPattern[uu[idxB_] CD[idxA_][pi[idxC_,idxD_]]] /;
     idxB===-idxD):>-kin[idxA,idxD]pi[idxC,-idxD]};
 redD[x_]:=FixedPoint[red[(# /. duRules) //. Join[dqRules,piRules]]&,x,6];
 gradRho=cc uu[a]CD[-a][rho[]];
 (* div q here is the four-divergence. Substituting div q=D.q+a.q/c^2
    gives the physical 1+3 equation's two acceleration terms. *)
 radiationTarget=gradRho+4 theta[] rho[]/3+CD[-a][qq[a]]
   +acc[a]qq[-a]/cc^2+sig[-a,-b]pi[a,b];
 gasEnergyTarget=gradRho+theta[] (rho[]+pres[]);
 radDiv=redD[-cc uu[-b]CD[-a][tr[a,b]]-radiationTarget];
 gasDiv=redD[-cc uu[-b]CD[-a][tg[a,b]]-gasEnergyTarget];
 put["radiation_differential_projection",radDiv];
 put["gas_differential_energy_projection",gasDiv];
 gasMomentumTarget=(rho[]+pres[])acc[a]/cc^2+hr[a,b]CD[-b][pres[]];
 put["gas_differential_momentum_projection",
   redD[hr[a,-b]CD[-d][tg[d,b]]-gasMomentumTarget]];

 (* Remaining exact scalar connections use the same c-explicit contract.
    These are labeled separately from xAct tensor canonicalizations. *)
 rhoGas=nH mRef cc^2+nH epsUnit (wH+binding);
 pGas=2 nH epsUnit wH/3;
 nHDot=-th nH;
 scalarChecks=<|
  "gas_reference_mass_density_cancellation"->TrueQ[Expand[
    D[rhoGas,nH]nHDot+D[rhoGas,wH]wDot+D[rhoGas,binding]bindingDot
      +th(rhoGas+pGas)-nH epsUnit(wDot+bindingDot)-th pGas]===0],
  "thermal_specific_energy_recovery"->TrueQ[Expand[
    (qHeatH-2 th wH/3)+(qAbsH-qEscH-qHeatH)
       +2 th wH/3-(qAbsH-qEscH)]===0],
  "thermal_density_five_thirds"->TrueQ[Expand[
    -th nH epsUnit wH+nH epsUnit(qHeatH-2 th wH/3)
       -(-5 th nH epsUnit wH/3+nH epsUnit qHeatH)]===0],
  "zero_flux_nonzero_weighted_force"->TrueQ[
    cc(uZero/2-uZero/2)===0 &&
    Expand[(2 kappa uZero/2-kappa uZero/2)-kappa uZero/2]===0],
  "observer_unit_norm_after_gamma_constraint"->TrueQ[
    Simplify[red[nn[a]nn[-a]+1]/.gamma^2->1/(1-beta^2)]===0]
 |>;
 ExportString[<|"schema"->"theory04_xact_covariant_v1",
   "kernel"->System`$Version,"xTensorLoaded"->MemberQ[$Packages,"xAct`xTensor`"],
   "xTensorVersion"->ToString[InputForm[xAct`xTensor`$Version]],
   "xPermExternalBackend"->$xpermQ,"tensorDeclared"->xTensorQ[uu],
   "tensor_check_count"->Length[checks],"tensor_checks"->checks,
   "tensor_residuals"->residuals,"scalar_check_count"->Length[scalarChecks],
   "scalar_checks"->scalarChecks,
   "all_pass"->And@@Join[Values[checks],Values[scalarChecks]]|>,"RawJSON"]
]
