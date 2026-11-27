Module[{x,r,rr,t,hb,m,v,ga,f,boost,kin,chain,u,ud,h0,k,ass},
ass=Element[{x,r,rr,t,hb,m,v,ga},Reals]&&hb>0&&m>0;
kin=-hb^2/(2m)D[f[x],{x,2}];
boost=FullSimplify[Exp[-I*m*v*x/hb]*(-hb^2/(2m))*D[Exp[I*m*v*x/hb]*f[x],{x,2}]-(kin-I*hb*v*D[f[x],x]+m*v^2*f[x]/2),Assumptions->ass];
chain=FullSimplify[(D[f[r-ga*rr,rr],{rr,2}]/.r->x+ga*rr)-(D[f[x,rr],{rr,2}]-2ga*D[f[x,rr],x,rr]+ga^2*D[f[x,rr],{x,2}]),Assumptions->ass];
u={{Cos[t],-Sin[t]},{Sin[t],Cos[t]}}.DiagonalMatrix[{Exp[I*2t],Exp[-I*3t]}];
ud=D[u,t];h0={{2,1-I},{1+I,3}};
k=ConjugateTranspose[u].h0.u-I*hb*ConjugateTranspose[u].ud;
<|"common_boost_kinetic_residual"->boost,"quantum_origin_chain_rule_residual"->chain,
"nonabelian_unitary_residual"->FullSimplify[ConjugateTranspose[u].u-IdentityMatrix[2],Assumptions->ass],
"nonabelian_K_hermiticity_residual"->FullSimplify[k-ConjugateTranspose[k],Assumptions->ass],
"diatomic_ERF_tensor_rank_example"->MatrixRank[{{0,0,0},{0,0,0},{0,0,7}}],
"scope"->"Operator algebra and constructed matrix examples only; no collision solver or physical completeness"|>]
