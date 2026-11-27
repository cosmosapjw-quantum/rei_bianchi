timed = AbsoluteTiming[Timing[TimeConstrained[
Module[{m, vP, vA, vB, vQ, mu, nu, vq, vk, al, beta, gam, disc, rr, hh, cc, y, rad, pp, pm, ax, cube, nodes, weights, avg, checks, eps, recoilMean, recoilVar, aa2, cstar, fourth, second},
 vP={px,py,pz}; vA={ax1,ay1,az1}; vB={bx1,by1,bz1}; vQ=vP-vA-vB;
 mu=m/(m+1); nu=(m+1)/(m+2); vq=vA-vP/(m+2); vk=vB+vA/(m+1)-vP/(m+1);
 al=(m+1)/m; rr=vP-vA; hh=e0-bind-vA.vA/2-rr.rr/(2(m+1)); cc=rr/(m+1);
 disc=beta^2-2 al gam; pp=(beta+Sqrt[disc])/al; pm=(beta-Sqrt[disc])/al;
 ax=Join[IdentityMatrix[6],-IdentityMatrix[6]];
 cube=Tuples[{-1,1},6]/Sqrt[6]; nodes=Join[ax,cube]; weights=Join[ConstantArray[1/48,12],ConstantArray[3/256,64]];
 avg[f_]:=Total[MapThread[#1 f[#2]&,{weights,nodes}]];
 aa2=m^2 pSquared/(m+2)^2; cstar=4m eps/(m+2);
 second=aa2+cstar/2; fourth=aa2^2+5aa2 cstar/3+5cstar^2/16;
 recoilMean=m pSquared/(2(m+2)^2)+eps/(m+2);
 recoilVar=2m pSquared eps/(3(m+2)^3)+eps^2/(4(m+2)^2);
 checks=<|
 "jacobi_energy"->(Together[vA.vA/2+vB.vB/2+vQ.vQ/(2m)-vP.vP/(2(m+2))-vk.vk/(2mu)-vq.vq/(2nu)]===0),
 "unit_coordinate_determinant"->(Det[{{1,0},{1/(m+1),1}}]^3===1),
 "lab_COM_available_energy"->(Together[e0-bind-2e0/(2(m+2))-(nu e0-bind)]===0),
 "conditional_sphere"->(Together[e0-bind-vA.vA/2-vB.vB/2-vQ.vQ/(2m)-(hh-al (vB-cc).(vB-cc)/2)]===0),
 "quadratic_plus"->(FullSimplify[al pp^2/2-beta pp+gam,Assumptions->m>0]===0),
 "quadratic_minus"->(FullSimplify[al pm^2/2-beta pm+gam,Assumptions->m>0]===0),
 "derivative_plus"->(Simplify[al pp-beta-Sqrt[disc]]===0),
 "derivative_minus"->(Simplify[al pm-beta+Sqrt[disc]]===0),
 "radial_beta_integral"->(Integrate[y^2 Sqrt[1-y^2],{y,0,1}]===Pi/16),
 "phase_volume"->(FullSimplify[16Pi^2 mu Sqrt[2mu](2nu eps)^(3/2)Sqrt[eps]Pi/16-4Pi^3(mu nu)^(3/2)eps^2,Assumptions->m>0&&eps>0]===0),
 "fold_antiderivative"->(FullSimplify[D[2y Sqrt[y^2+cc0^2-rad^2]/(al cc0),y]-2(cc0^2-rad^2+2y^2)/(al cc0 Sqrt[y^2+cc0^2-rad^2]),Assumptions->m>0&&cc0>rad>0&&y>=0]===0),
 "fold_total"->(FullSimplify[2Pi(2rad Sqrt[rad^2+cc0^2-rad^2]/(al cc0))-4Pi rad/al,Assumptions->m>0&&cc0>rad>0]===0),
 "positive_rule_normalization"->(Total[weights]===1),
 "positive_rule_second"->(avg[Function[u,u[[1]]^2]]===1/6),
 "positive_rule_fourth"->(avg[Function[u,u[[1]]^4]]===1/16),
 "positive_rule_crossfourth"->(avg[Function[u,u[[1]]^2u[[2]]^2]]===1/48),
 "positive_rule_odd"->(avg[Function[u,u[[1]]^3u[[2]]]]===0),
 "recoil_mean"->(Together[second/(2m)-recoilMean]===0),
 "recoil_variance"->(Together[(fourth-second^2)/(4m^2)-recoilVar]===0),
 "hydrogen_threshold"->(Together[(mu/2)/nu-m(m+2)/(2(m+1)^2)]===0),
 "toy_roots"->(Simplify[((3Sqrt[2]+Sqrt[10])/8)((3Sqrt[2]-Sqrt[10])/8)]===1/8)
 |>;
 <|"checks"->checks,"all_true"->And@@Values[checks],"checks_count"->Length[checks],"toy_theta_c_deg"->N[ArcCos[2/3]180/Pi,30],"toy_roots"->N[{(3Sqrt[2]-Sqrt[10])/8,(3Sqrt[2]+Sqrt[10])/8},30],"scope"->"symbolic kinematics and exact rational cubature only; no physical amplitude"|>
],10,$Aborted]]];
<|"body_wall_s"->timed[[1]],"body_cpu_s"->timed[[2,1]],"result"->timed[[2,2]],"remote_total_CPU"->"UNKNOWN_NOT_ZERO"|>
