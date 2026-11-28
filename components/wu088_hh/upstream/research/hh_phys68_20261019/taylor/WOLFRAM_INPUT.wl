ClearAll[c,z,ell,k,eta,Q,h];
q[z_] := k^2+2/(c+z)-ell (ell+1)/(c+z)^2;
Q[n_] := k^2 KroneckerDelta[n,0]+2 (-1)^n/c^(n+1)-ell (ell+1)(n+1)(-1)^n/c^(n+2);
qchecks=Table[Together[SeriesCoefficient[q[z],{z,0,n}]-Q[n]],{n,0,6}];
chaincheck=Together[k^2 (1-2 eta/(k r)-ell (ell+1)/(k r)^2)-(k^2+2/r-ell (ell+1)/r^2)]/.eta->-1/k;
h[0]=a;h[1]=b;
Do[h[n+2]=-Sum[Q[s]h[n-s],{s,0,n}]/((n+1)(n+2)),{n,0,6}];
poly=Sum[h[n]z^n,{n,0,8}];
residualchecks=Table[Together[SeriesCoefficient[D[poly,{z,2}]+q[z]poly,{z,0,n}]],{n,0,6}];
<|"QChecks"->qchecks,"ChainFactor"->FullSimplify[chaincheck],"ResidualChecks"->residualchecks,"PhysicalParameters"->{k->7/10,eta->-10/7}|>
