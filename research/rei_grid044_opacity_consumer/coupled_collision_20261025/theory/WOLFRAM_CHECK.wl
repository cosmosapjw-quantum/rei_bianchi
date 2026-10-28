(* A: representative collision/source Jacobian, quotient rule; actual 60-zero result. *)
ClearAll["Global`*"];
z={y0,y1,n1,n2,b,k}; vg={v1,v2,v3,v4,v5,v6}; lam=l0+vg.z;
r1=cc nr s1 y0 n1;r2=cc nr s2 y0 n2;rt=r1+r2;
inj={aa q11+bb q21,aa q12+bb q22};
f0={-rt,rt,inj[[1]]-r1,inj[[2]]-r2,ch rt,(e1-ch)r1+(e2-ch)r2};
f=f0-lam z;
j0={{-cc nr(s1 n1+s2 n2),0,-cc nr s1 y0,-cc nr s2 y0,0,0},
{cc nr(s1 n1+s2 n2),0,cc nr s1 y0,cc nr s2 y0,0,0},
{-cc nr s1 n1,0,-cc nr s1 y0,0,0,0},
{-cc nr s2 n2,0,0,-cc nr s2 y0,0,0},
{ch cc nr(s1 n1+s2 n2),0,ch cc nr s1 y0,ch cc nr s2 y0,0,0},
{cc nr((e1-ch)s1 n1+(e2-ch)s2 n2),0,(e1-ch)cc nr s1 y0,(e2-ch)cc nr s2 y0,0,0}};
jc=j0-lam IdentityMatrix[6]-Outer[Times,z,vg];
js={{0,0},{0,0},{q11,q21},{q12,q22},{0,0},{0,0}};
w={0,0,e1,e2,1,1};
res=Join[Flatten[D[f,{z}]-jc],Flatten[D[f,{{aa,bb}}]-js],
{f[[1]]+f[[2]]+lam(y0+y1),f[[2]]+lam y1-rt,f[[3]]+f[[4]]+lam(n1+n2)-Total[inj]+rt,
 f[[5]]-ch f[[2]]+lam(b-ch y1),w.f+lam w.z-{e1,e2}.inj},
Flatten[w.jc+lam w+(w.z)vg],
{D[(rho[t]/ref[t]),t]-(src[t]/ref[t]-(sr[t]/ref[t])rho[t]/ref[t])}/.{Derivative[1][rho][t]->src[t]-3hh rho[t],Derivative[1][ref][t]->sr[t]-3hh ref[t]}];
FullSimplify[res]

(* B: Xext and reference equivalence; actual warning preserved. *)
ClearAll["Global`*"];
z={n1,n2,y0,y1,b,k,x};v={v1,v2,v3,v4,v5,v6,v7};lam=l0+v.z;
r1=cc nr s1 y0 n1;r2=cc nr s2 y0 n2;rt=r1+r2;
q={aa q11+bb q21,aa q12+bb q22};
fc={-r1,-r2,-rt,rt,ch rt,(e1-ch)r1+(e2-ch)r2,0};
Q=Join[q,{0,0,0,0,{e1,e2}.q}];f=fc+Q-lam z;
w={e1,e2,0,0,1,1,-1};j=D[f,{z}];
zp=z/rr;nrp=rr nr;lamp=lam+uu;
rp1=cc nrp s1 zp[[3]] zp[[1]];rp2=cc nrp s2 zp[[3]] zp[[2]];rpt=rp1+rp2;
fcp={-rp1,-rp2,-rpt,rpt,ch rpt,(e1-ch)rp1+(e2-ch)rp2,0};
fp=fcp+Q/rr-lamp zp;
FullSimplify[Join[{w.f+lam w.z},Flatten[w.j+lam w+(w.z)v],Flatten[fp-f/rr+uu zp]],Assumptions->rr>0]

(* C: identifier repair; actual clean 15-zero result. *)
ClearAll["Global`*"];
z={n1,n2,y0,y1,b,k,x};v={v1,v2,v3,v4,v5,v6,v7};lam=l0+v.z;
r1=cc nr s1 y0 n1;r2=cc nr s2 y0 n2;rt=r1+r2;
q={aa q11+bb q21,aa q12+bb q22};
fc={-r1,-r2,-rt,rt,ch rt,(e1-ch)r1+(e2-ch)r2,0};
qvec=Join[q,{0,0,0,0,{e1,e2}.q}];f=fc+qvec-lam z;
w={e1,e2,0,0,1,1,-1};j=D[f,{z}];
zp=z/rr;nrp=rr nr;lamp=lam+uu;
rp1=cc nrp s1 zp[[3]] zp[[1]];rp2=cc nrp s2 zp[[3]] zp[[2]];rpt=rp1+rp2;
fcp={-rp1,-rp2,-rpt,rpt,ch rpt,(e1-ch)rp1+(e2-ch)rp2,0};
fp=fcp+qvec/rr-lamp zp;
FullSimplify[Join[{w.f+lam w.z},Flatten[w.j+lam w+(w.z)v],Flatten[fp-f/rr+uu zp]],Assumptions->rr>0]

