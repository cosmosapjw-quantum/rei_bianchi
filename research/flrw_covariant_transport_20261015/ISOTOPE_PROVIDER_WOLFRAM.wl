ClearAll["Global`*"];
assumptions = Element[{lam,mu,tt,kb,ee,vv}, Reals] && lam>0 && mu>0 && tt>0 && kb>0 && ee>0 && vv>0;
fvel[m_,t_,v_] := 4 Pi (m/(2 Pi kb t))^(3/2) v^2 Exp[-m v^2/(2 kb t)];
pdfScale = FullSimplify[fvel[lam mu,tt,vv]/fvel[mu,tt/lam,vv],Assumptions->assumptions];
milneRatio = FullSimplify[((lam ee)^2/((lam mu)^2 vv^2))*lam^-2/(ee^2/(mu^2 vv^2)),Assumptions->assumptions];
rrScale = FullSimplify[pdfScale*milneRatio,Assumptions->assumptions];
coolScale = FullSimplify[(lam mu vv^2/2)/(mu vv^2/2)*rrScale,Assumptions->assumptions];
photoIdentity = Simplify[-eph + chi + (eph-chi)];
rrIdentity = Simplify[-cool - chi*rr + (chi*rr+cool)];
ciIdentity = Simplify[-chi*ci+chi*ci];
cxIdentity = Simplify[-(chiD-chiH)*xi+(chiD-chiH)*xi];
alphaDim = {0,2,0,0}+{0,1,-1,0};
coolDim = alphaDim+{1,2,-2,0};
volumeRRDim = coolDim+2{0,-3,0,0};
heatPhotoDim = {0,0,-1,0}+{1,2,-2,0};
<|"maxwellVelocityScale"->pdfScale,"milneCrossSectionScale"->milneRatio,"RRRateScale"->rrScale,"RRCoolingScale"->coolScale,"eventEnergyResiduals"->{photoIdentity,rrIdentity,ciIdentity,cxIdentity},"dimensionAlpha"->alphaDim,"dimensionCoolingCoefficient"->coolDim,"dimensionVolumetricCooling"->volumeRRDim,"dimensionHeatPerAbsorber"->heatPhotoDim|>
