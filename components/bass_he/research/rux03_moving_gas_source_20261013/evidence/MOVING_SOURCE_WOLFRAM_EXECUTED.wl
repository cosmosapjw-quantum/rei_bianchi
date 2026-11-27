ClearAll["Global`*"];
started=AbsoluteTime[];
checks=<||>; residuals=<||>;
save[name_,value_]:=(checks[name]=TrueQ[value];residuals[name]=ToString[value,InputForm]);
save["doppler_target_density_normalization",Together[cc (dn yy/gp) ss gp (1-vv mu)-cc dn yy ss (1-vv mu)]===0];
save["species_lab_to_gas_clock",Together[h rate/dn-(h/gp) rate/(dn/gp)]===0];
np=(nm+h src)/(1+h (l1+l2+l3));
absEvents=h {l1,l2,l3} np;
save["photon_backward_euler_identity",Together[np-nm-h src+Total[absEvents]]===0];
save["photon_nonnegative_and_bounded_absorption",FullSimplify[np>=0&&Total[absEvents]>=0&&Total[absEvents]<=nm+h src,
Assumptions->Element[{nm,h,src,l1,l2,l3},Reals]&&nm>=0&&h>=0&&src>=0&&l1>=0&&l2>=0&&l3>=0]];
p1=(n1+h s1)/(1+h la1);p2=(n2+h s2)/(1+h la2);
a1=h la1 p1;a2=h la2 p2;
force1={1,ex1,ey1,ez1};force2={1,ex2,ey2,ez2};
gasIncrement=ep(e1 a1 force1+e2 a2 force2)-gp esc {1,bx,by,bz};
photonIncrement=ep(e1(p1-n1)force1+e2(p2-n2)force2);
escapeIncrement=gp esc {1,bx,by,bz};
injected=ep h(e1 s1 force1+e2 s2 force2);
save["finite_total_energy_three_momentum_balance",
Map[Together,gasIncrement+photonIncrement+escapeIncrement-injected]===ConstantArray[0,4]];
rhoP=dn/gp (rm+ep db+ep(wm+dw));
rhoM=dn/gm (rm+ep wm);presM=kk dn/gm ep wm;
projected=gp rhoP-gm(rhoM+presM)gr+gp presM;
kin=dn((rm+(1+kk)ep wm)(gr-1)-kk ep wm(gp/gm-1));
save["finite_thermal_constitutive_identity",Together[projected-dn ep(dw+db)+kin]===0];
save["finite_thermal_binding_elimination",Together[
(projected/.dw->h qh/gp+kin/(dn ep))-(dn ep db+h dn ep qh/gp)]===0];
g0=1/Sqrt[1-v^2];gt=1/Sqrt[1-(v+t ax)^2-(t ay)^2-(t az)^2];
grel=gt g0 (1-v(v+t ax));
limAss=Element[{v,ax,ay,az,dn,ep,wm,rm,kk},Reals]&&-1<v<1;
rel1=FullSimplify[D[grel,t]/.t->0,Assumptions->limAss];
rel2=FullSimplify[(D[grel,{t,2}]/.t->0)-(g0^4 ax^2+g0^2(ay^2+az^2)),Assumptions->limAss];
kt=dn((rm+(1+kk)ep wm)(grel-1)-kk ep wm(gt/g0-1));
limK=FullSimplify[(D[kt,t]/.t->0)+dn kk ep wm (D[Log[gt],t]/.t->0),Assumptions->limAss];
save["relative_gamma_and_pressure_work_limit",{rel1,rel2,limK}==={0,0,0}];
vlist={b1,b2,b3};gv=1/Sqrt[1-vlist.vlist];
ww=ar gv+alpha pp gv^2;
forward=Join[{ww-pp},ww vlist];
jac=Table[D[forward[[i]],Join[{pp},vlist][[j]]],{i,4},{j,4}];
jacAxis=jac/.{b1->v,b2->0,b3->0};
wAxis=ar g0+alpha pp g0^2;
target=wAxis^2(ar(alpha-1)g0^3+alpha pp((alpha-2)g0^4+g0^2));
jres=FullSimplify[Det[jacAxis]-target,Assumptions->Element[{ar,alpha,pp,v},Reals]&&ar>0&&pp>0&&alpha>=2&&-1<v<1];
save["full_four_by_four_primitive_jacobian",jres===0];
save["primitive_jacobian_positive",FullSimplify[target>0,Assumptions->Element[{ar,alpha,pp,v},Reals]&&ar>0&&pp>=0&&alpha>=2&&-1<v<1]];
save["rest_paired_scalar_thermal_limit",Together[kin/.{gp->1,gm->1,gr->1}]===0];
save["covariant_to_eulerian_thermal_clock",Together[(qh-kk gd wm)/gg-(qh/gg-kk wm gd/gg)]===0];
ExportString[<|"unit"->"HERE_RUX03_MOVING_GAS_SOURCE_05","version"->$Version,
"systemID"->$SystemID,"elapsedSeconds"->AbsoluteTime[]-started,
"checks"->checks,"checkCount"->Length[checks],"passCount"->Count[Values[checks],True],
"allPass"->And@@Values[checks],"evaluatedAssertions"->residuals,
"jacobianMethod"->"Differentiate full 4x4 (p,beta_x,beta_y,beta_z), then rotate beta to one axis; isotropy extends the determinant to all beta.",
"novelScope"->"Finite event and thermal identities, exact 4x4 determinant and continuous limit. The primitive positive-factor identity is also checked in the separate primitive batch."|>,"RawJSON"]