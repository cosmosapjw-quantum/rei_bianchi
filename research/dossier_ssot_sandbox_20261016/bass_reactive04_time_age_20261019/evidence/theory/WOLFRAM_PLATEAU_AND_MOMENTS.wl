Clear[t,u,v,b,x,z];
ph[z_]:=(1-Exp[-z])/z;
ps[z_]:=(1-(1+z)Exp[-z])/z^2;
ch[z_]:=(z-1+Exp[-z])/z^2;
g[x_]:=(1-Exp[-t x])/(1-Exp[-t]);
ell=v-u;
lhs=Exp[-t u] ell (ell ps[t ell]+Exp[-t ell](b-v)ph[t(b-v)])/ph[t];
rhs=Exp[-t b] ell ((u-b)ph[t(u-b)]+Exp[-t(u-b)]ell ch[t ell])/ph[t];
{
 FullSimplify[lhs-Integrate[g[b]-g[x],{x,u,v}],Assumptions->t>0&&0<u<v<b<1],
 FullSimplify[rhs-Integrate[g[x]-g[b],{x,u,v}],Assumptions->t>0&&0<b<u<v<1],
 Series[ps[z],{z,0,6}],Series[ch[z],{z,0,6}],
 Series[1/z-1/(Exp[z]-1),{z,0,8}],
 Series[2/z^2-(1+2/z)/(Exp[z]-1),{z,0,8}]
}
