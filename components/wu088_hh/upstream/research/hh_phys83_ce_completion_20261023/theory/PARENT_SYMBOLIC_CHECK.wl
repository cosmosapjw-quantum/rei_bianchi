ClearAll["Global\`*"];
ass = z>0 && theta>0 && del>0 && m>0 && rr>0 && cc>0 && aa>0 && ap>0 && ds>0 && dp>0 && ss>0;
bb={{ds+aa,aa},{ap,dp+ap}}; av={aa,ap};
stat={aa/ds,ap/dp}/(1+aa/ds+ap/dp);
den=(ss+ds)*(ss+dp)+aa*(ss+dp)+ap*(ss+ds);
checks=<|
"endpoint_left"->FullSimplify[Integrate[(1-u)*Exp[-z*u],{u,0,1},Assumptions->z>0]-(z-1+Exp[-z])/z^2,Assumptions->ass],
"endpoint_right"->FullSimplify[Integrate[u*Exp[-z*u],{u,0,1},Assumptions->z>0]-(1-(1+z)*Exp[-z])/z^2,Assumptions->ass],
"paired_balance"->FullSimplify[(cc*theta^(-3/2)*Exp[-del/theta]*m)/(cc*theta^(-3/2)*m/rr)-rr*Exp[-del/theta],Assumptions->ass],
"stationary_population"->FullSimplify[bb.stat-av,Assumptions->ass],
"cayley_hamilton"->FullSimplify[bb.bb-Tr[bb]*bb+Det[bb]*IdentityMatrix[2],Assumptions->ass],
"ground_start_resolvent"->FullSimplify[Inverse[ss*IdentityMatrix[2]+bb].av-{aa*(ss+dp),ap*(ss+ds)}/den,Assumptions->ass],
"thermal_atomic_radiative_ledger"->Expand[-del*((aa+ap)*xg-bs*xs-bp*xp)+del*((aa+ap)*xg-(bs+a2g+am1)*xs-(bp+ar)*xp)+del*((a2g+am1)*xs+ar*xp)]
|>;
checks
