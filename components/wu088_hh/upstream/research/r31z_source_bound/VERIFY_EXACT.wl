ClearAll[u,s,a0,a1,a2,a3,a4,a5,y0,y2,y4,d0,d2,d4,tt,p,sol,q,k0,k2,k4,ks];
p=a0+a1 s+a2 s^2+a3 s^3+a4 s^4+a5 s^5;
sol=First@Solve[{
 (p/.s->0)==y0,(D[p,s]/.s->0)==tt d0,
 (p/.s->1/2)==y2,(D[p,s]/.s->1/2)==tt d2,
 (p/.s->1)==y4,(D[p,s]/.s->1)==tt d4},{a0,a1,a2,a3,a4,a5}];
q=Expand[p/.sol];
ks=Expand[InterpolatingPolynomial[{{0,k0},{1/2,k2},{1,k4}},s]];
ExportString[<|
 "six_constraints"->{Simplify[(q/.s->0)-y0],Simplify[(D[q,s]/.s->0)-tt d0],Simplify[(q/.s->1/2)-y2],Simplify[(D[q,s]/.s->1/2)-tt d2],Simplify[(q/.s->1)-y4],Simplify[(D[q,s]/.s->1)-tt d4]},
 "quintic_basis"->ToString[Collect[q,{y0,tt d0,y2,tt d2,y4,tt d4},Simplify],InputForm],
 "quadratic_K"->ToString[ks,InputForm],
 "compatibility_identity"->Simplify[D[q,s]/tt-((D[q,s]/tt)/2+ks)-((D[q,s]/tt)/2-ks)],
 "endpoint_kernel_mass"->Integrate[1-u,{u,0,1}],
 "midpoint_kernel_mass"->Simplify[(1/2)Integrate[u,{u,0,1/2}]+(1/2)Integrate[1-u,{u,1/2,1}]]
|>,"RawJSON"]
