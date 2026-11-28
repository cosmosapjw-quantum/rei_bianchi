ClearAll[q,tau,n,x,u,d,z,b,a,L,V,dt,jn,w0,w1,prim,over];
ass = 0 < q < 1 && tau > 0 && Element[n, Integers] && n >= 1;
jn[x_, m_] := tau (1 - q^m)/(1 - q) + q^m (x - m tau);
w0[x_, dt_] := dt ((x - 1) Exp[x] + 1)/x^2;
w1[x_, dt_] := dt (Exp[x] - 1 - x)/x^2;
alg = {
 FullSimplify[D[jn[x,n],x] - q^n, ass],
 FullSimplify[jn[n tau,n] - jn[n tau,n-1], ass],
 FullSimplify[jn[x,0] - x, 0<q<1 && tau>0],
 FullSimplify[Integrate[Exp[x (1-u)] (1-u),{u,0,1},Assumptions->x>0] - w0[x,1], x>0],
 FullSimplify[Integrate[Exp[x (1-u)] u,{u,0,1},Assumptions->x>0] - w1[x,1], x>0],
 FullSimplify[w0[x,dt]+w1[x,dt]-dt (Exp[x]-1)/x, x>0 && dt>0],
 FullSimplify[w0[-x,dt]-Exp[-x] w1[x,dt], x>0 && dt>0],
 FullSimplify[w1[-x,dt]-Exp[-x] w0[x,dt], x>0 && dt>0],
 Integrate[1-u,{u,0,1}]-1/2,
 Integrate[u,{u,0,1}]-1/2,
 FullSimplify[D[Exp[d u] z + b (Exp[d u]-1)/d,u] - Exp[d u] (d z+b), d!=0],
 D[z+b u,u]-b
};
m = (1-a) L+a V;
split = FullSimplify[
 Exp[x (1-a)] (w0[x a,a] L+w1[x a,a] m)
 + w0[x (1-a),1-a] m+w1[x (1-a),1-a] V
 -w0[x,1] L-w1[x,1] V, x>0 && 0<a<1];
splitZero = FullSimplify[a (L+m)/2+(1-a) (m+V)/2-(L+V)/2];
prim[v_,qq_,tt_] := Module[{zz=Max[0,v],nn},nn=Floor[zz/tt];
 tt Sum[qq^kk,{kk,0,nn-1}]+qq^nn (zz-nn tt)];
over[t_,aa_,bb_,qq_,tt_] := Sum[qq^kk Max[0,Min[bb,t-kk tt]-Max[aa,t-(kk+1)tt]],{kk,0,3}];
ages={0,1/10,1/4,1/3,1/2,7/12,2/3,3/4,1};
ov=Table[over[t,1/7,3/5,2/5,1/3]-(prim[t-1/7,2/5,1/3]-prim[t-3/5,2/5,1/3]),{t,ages}];
fresh=over[1/2,0,1/4,1/2,1/3]-1/6;
res=Join[alg,{split,splitZero,fresh},ov];
<|"algebra_and_controls"->res,"residual_count"->Length[res],
"all_zero"->And@@Map[#===0&,res],
"scope"->"New R12 primitive/overlap/positive moments/refinement identities only; no previous CAS rerun"|>
