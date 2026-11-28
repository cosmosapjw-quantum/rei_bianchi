vars={q,v,h,l}; he=b3+b4; li=c6+c7;
xe=q+he h+li l; nt=aH+aD+he+li+xe;
bp=ih q+del v+ihe he h+ili li l;
ua=u0-ih(q-q0)-del(v-v0)-ihe he(h-h0)-ili li(l-l0);
tt=ua/(cv nt);
gg={1,0,he,li}; ee={ih,del,ihe he,ili li};
tg=-(ee+cv tt gg)/(cv nt);
p=aH+aD-q; aa=aD-v; bb=q-v; cc=aH-q+v;
z=kf[t] aa bb-kr[t] v cc;
ff=den {kh[t] xe p,kh[t] xe aa+z, khe[t] xe(1-h),kli[t] xe(1-l)};
mm={{kh[t](p-xe),0,kh[t] p he,kh[t] p li},
 {kh[t] aa+kf[t] aa+kr[t] v,-kh[t] xe-kf[t](aa+bb)-kr[t](cc+v),kh[t] aa he,kh[t] aa li},
 {khe[t](1-h),0,khe[t](he(1-h)-xe),khe[t] li(1-h)},
 {kli[t](1-l),0,kli[t] he(1-l),kli[t](li(1-l)-xe)}};
ww={kh'[t] xe p,kh'[t] xe aa+kf'[t] aa bb-kr'[t] v cc,khe'[t] xe(1-h),kli'[t] xe(1-l)};
jac=den(mm+Outer[Times,ww,tg])/.t->tt;
fclosed=ff/.t->tt;
direct=Table[D[fclosed[[i]],vars[[j]]],{i,4},{j,4}];
resJac=Map[Simplify,direct-jac,{2}];
y={aH-q+v,q-v,aD-v,v,0,0,b3(1-h),b3 h,0,b4(1-h),b4 h,0,c6(1-l),c6 l,0,0,c7(1-l),c7 l,0,0,0};
charges={0,1,0,1,0,1,0,1,2,0,1,2,0,1,2,3,0,1,2,3,0};
eps={0,ih,0,ih+del,0,ih,0,ihe,ehe3,0,ihe,ehe3,0,ili,eli3,eli4,0,ili,eli3,eli4,0};
rh=den kh[t] xe y[[1]];rd=den kh[t] xe y[[3]];
rh3=den khe[t] xe y[[7]];rh4=den khe[t] xe y[[10]];
rl6=den kli[t] xe y[[13]];rl7=den kli[t] xe y[[17]];
zz=den z;
full={-rh+zz,rh-zz,-rd-zz,rd+zz,0,0,-rh3,rh3,0,-rh4,rh4,0,-rl6,rl6,0,0,-rl7,rl7,0,0,0};
recJac=Table[D[y[[i]],vars[[j]]],{i,21},{j,4}];
recRes=Simplify[recJac.ff-full];
qheat=-(ih rh+(ih+del)rd+ihe(rh3+rh4)+ili(rl6+rl7)+del zz);
heatRes=Simplify[-ee.ff-qheat];
thermRes=Simplify[Table[D[tt,s],{s,vars}].fclosed-(-ee.fclosed/(cv nt)-tt gg.fclosed/nt)];
ExportString[<|
"Jacobian_residual"->resJac,
"temperature_gradient_residual"->Simplify[Table[D[tt,s],{s,vars}]-tg],
"21_state_reconstruction_rhs_residual"->recRes,
"electron_reconstruction_residual"->Simplify[charges.y-xe],
"particle_reconstruction_residual"->Simplify[Total[y]+charges.y-nt],
"binding_reconstruction_residual"->Simplify[eps.y-bp],
"energy_rhs_residual"->heatRes,
"temperature_chain_rule_residual"->thermRes,
"He_fraction_difference_rhs_residual"->Expand[den khe[t] xe ((1-h3)-(1-h4))+den khe[t] xe(h3-h4)],
"Li_fraction_difference_rhs_residual"->Expand[den kli[t] xe ((1-l6)-(1-l7))+den kli[t] xe(l6-l7)],
"dimensions"->{Length[y],Length[vars]},
"ODE_calls"->0|>,"RawJSON"]
