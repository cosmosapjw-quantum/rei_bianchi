(* PHYS51 independent Wolfram15 exact-parity run *)
ClearAll[k,r,rr,t,c,l,m,mu,qmin,variation,p1,p2,q,z,h,hprime];
{k,r,rr,t,c,l,m}={7/10,27,7/10,43,4/5,28,43};
mu=(l(l+1)/r^2-2/r)/(2k);
qmin=k^2+2/t-l(l+1)/t^2;
variation=2/t+l(l+1)/t^2;
p1=2(r-rr)-2c(t-r);p2=2(t-rr);
q=(m^2/k)(1+1/(r-rr))(Exp[-p1]/(1+c)+Exp[-p2]);
Print["mu=",mu," margin=",c-mu," qmin=",qmin," variation=",variation,
 " p1=",p1," p2=",p2," q_double=",N[q,45]];
If[mu!=3790/5103 || p1!=27 || qmin!=18001/184900 || N[q,35]>=10^-7,Exit[2]];
{l,t}={21,27};
h[n_]:=N[CoulombH1[n,-1/k,k t],65];
hprime=N[((l+1)/(k t)-1/(k(l+1)))*h[l]-
 Sqrt[1+1/(k^2(l+1)^2)] h[l+1],65];
z=N[k hprime/h[l],55];
Print["Coulomb ell21 Z=",z," outgoing current positive=",Im[z]>0];
If[Im[z]<=0,Exit[3]];
Exit[0];
