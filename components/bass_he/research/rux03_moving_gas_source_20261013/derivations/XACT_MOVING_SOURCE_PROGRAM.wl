(* Parse after loading xAct`xTensor`. Pure Wolfram xPerm backend.
   All gamma symbols below are scalar fields; the homogeneous time-derivative
   checks therefore preserve the time dependence of u and -n.u. *)
Module[{norm,red,put,hh,kk,dop,erest,jph,abs,Tp,Tm,Cp,Cm,vel,Ec,Mc,
  gradRules,checks=<||>,residuals=<||>,baryonDiv,speciesDiv},
 $xpermQ=False; $DefInfoQ=False;
 DefManifold[MovingM,4,{a,b,d,e,f,i,j,k,l,m}];
 DefMetric[-1,metric[-a,-b],CD,{";","D"}];
 Scan[(DefTensor[#[a],MovingM])&,{normal,up,um,edir,udot}];
 Scan[(DefTensor[#[],MovingM])&,{gp,gm,grel,rhop,pp,rhom,pm,nh,zfrac}];
 Scan[DefConstantSymbol,{cc,energyLab,numberLab,eventDensity,mu,
   eventIncrement,escapeIncrement,nDot,zDot,gDot,pDot}];
 norm=Join@@(MakeRule[#,MetricOn->All,ContractMetrics->True]& /@ {
  {normal[a]normal[-a],-1},{up[a]up[-a],-1},{um[a]um[-a],-1},
  {edir[a]edir[-a],1},{normal[a]edir[-a],0},
  {normal[a]up[-a],-gp[]},{normal[a]um[-a],-gm[]},
  {up[a]um[-a],-grel[]},{up[a]edir[-a],gp[] mu},
  {normal[a]udot[-a],-gDot},{up[a]udot[-a],0}});
 red[x_]:=Module[{y},
   y=ToCanonical[ContractMetric[ToCanonical[Expand[x]]]];
   y=ToCanonical[y //. norm]; Simplify[Together[y]]];
 put[name_,expr_]:=Module[{r=red[expr]},
   AssociateTo[checks,name->TrueQ[r===0]];
   AssociateTo[residuals,name->ToString[InputForm[r]]]];
 hh[u_,i_,j_]:=metric[i,j]+u[i]u[j];
 kk[i_]:=normal[i]+edir[i]; dop=gp[](1-mu);
 erest[i_]:=kk[i]/dop-up[i];
 jph[i_]:=cc numberLab kk[i];
 abs[i_]:=eventDensity energyLab kk[i]/cc;
 Tp[i_,j_]:=(rhop[]+pp[])up[i]up[j]+pp[] metric[i,j];
 Tm[i_,j_]:=(rhom[]+pm[])um[i]um[j]+pm[] metric[i,j];
 (* Expand the n-contraction once so a caller's free index never collides
    with an internal dummy index. The stress contraction is checked below. *)
 Cp[i_]:=(rhop[]+pp[])gp[]up[i]-pp[]normal[i];
 Cm[i_]:=(rhom[]+pm[])gm[]um[i]-pm[]normal[i];
 vel[i_]:=up[i]/gp[]-normal[i];
 Ec=(rhop[]+pp[])gp[]^2-pp[];
 Mc[i_]:=(rhop[]+pp[])gp[]^2 vel[i];

 put["M01_doppler_contraction",-up[-a]kk[a]-dop];
 put["M01_beam_number_density",-up[-a]jph[a]/cc-dop numberLab];
 put["M01_rest_direction_spatial",up[-a]erest[a]];
 put["M01_rest_direction_unit",erest[a]erest[-a]-1];
 put["M01_photon_momentum_reconstruction",
   energyLab kk[a]/cc-dop energyLab(up[a]+erest[a])/cc];
 put["M01_lab_absorption_energy",-cc normal[-a]abs[a]-energyLab eventDensity];
 put["M01_lab_absorption_momentum",
   cc hh[normal,a,-b]abs[b]-energyLab eventDensity edir[a]];
 put["M01_rest_absorption_energy",-cc up[-a]abs[a]-dop energyLab eventDensity];
 put["M02_hydrogen_lab_density",-normal[-a]nh[]up[a]-gp[]nh[]];
 put["M02_species_lab_density",
   -normal[-a]nh[]zfrac[]up[a]-gp[]nh[]zfrac[]];
 put["M03_conservative_current_from_stress",-Tp[a,b]normal[-b]-Cp[a]];
 put["M03_conservative_energy",-normal[-a]Cp[a]-Ec];
 put["M03_conservative_momentum",hh[normal,a,-b]Cp[b]-Mc[a]];
 put["M03_velocity_spatial",normal[-a]vel[a]];
 put["M03_velocity_norm",vel[a]vel[-a]-(1-1/gp[]^2)];
 put["M04_endpoint_energy_minus_beta_momentum",Ec-vel[-a]Mc[a]-rhop[]];
 put["M04_current_endpoint_projection",-up[-a]Cp[a]-gp[]rhop[]];
 put["M04_old_current_endpoint_projection",
   -up[-a]Cm[a]-gm[](rhom[]+pm[])grel[]+gp[]pm[]];
 put["M04_finite_gas_projection",
   -up[-a](Cp[a]-Cm[a])-
   (gp[]rhop[]-gm[](rhom[]+pm[])grel[]+gp[]pm[])];
 put["M04_finite_event_escape_projection",
   -up[-a](energyLab eventIncrement kk[a]-escapeIncrement up[a])-
   (dop energyLab eventIncrement-escapeIncrement)];

 (* Homogeneous Eulerian source substep: grad X=-n d_t X/c,
    grad_a u^b=-n_a d_t u^b/c, n.d_t u=-d_t gamma.
    These are kinematic input rules, before any source equation. *)
 gradRules={
  HoldPattern[CD[idxA_][nh[]]]:>-normal[idxA]nDot/cc,
  HoldPattern[CD[idxA_][zfrac[]]]:>-normal[idxA]zDot/cc,
  HoldPattern[CD[idxA_][gp[]]]:>-normal[idxA]gDot/cc,
  HoldPattern[CD[idxA_][pp[]]]:>-normal[idxA]pDot/cc,
  HoldPattern[CD[idxA_][up[idxB_]]]:>-normal[idxA]udot[idxB]/cc};
 baryonDiv=Expand[CD[-a][cc nh[]up[a]]] /. gradRules;
 speciesDiv=Expand[CD[-a][cc nh[]zfrac[]up[a]]] /. gradRules;
 put["M04_eulerian_nucleus_continuity",baryonDiv-(gp[]nDot+nh[]gDot)];
 put["M04_eulerian_species_continuity",
   speciesDiv-zfrac[](gp[]nDot+nh[]gDot)-gp[]nh[]zDot];
 put["M04_gas_clock",(cc up[a]CD[-a][zfrac[]] /. gradRules)-gp[]zDot];
 put["M04_source_step_expansion",(cc CD[-a][up[a]] /. gradRules)-gDot];
 put["M04_rest_pressure_gradient",
   (hh[up,a,b]CD[-b][pp[]] /. gradRules)-pDot(gp[]up[a]-normal[a])/cc];

 ExportString[<|"schema"->"theory05_xact_moving_source_v1",
  "kernel"->System`$Version,"xTensorLoaded"->MemberQ[$Packages,"xAct`xTensor`"],
  "xTensorVersion"->ToString[InputForm[xAct`xTensor`$Version]],
  "xPermExternalBackend"->$xpermQ,"tensorDeclared"->xTensorQ[up],
  "tensor_check_count"->Length[checks],"tensor_checks"->checks,
  "tensor_residuals"->residuals,"all_pass"->And@@Values[checks]|>,"RawJSON"]
]
