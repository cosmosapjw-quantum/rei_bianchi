Module[{aa,bb,rr,i1,i2,i3,i4,j2,j4,vv,alpha,beta,ha,hb,tt,mm,
dR,dI,xR,xI,dd,xx,swap,mat,spinExpr,spinTarget,checks,timed,
ka,kb,kzero,mua,mub,ra2,rb2,zv,avec,bvec,redD,redX},
timed=AbsoluteTiming[Timing[
 rr=Sqrt[aa^2-bb^2];i1=1/rr;i2=aa/rr^3;
 i3=(2aa^2+bb^2)/(2rr^5);i4=aa(2aa^2+3bb^2)/(2rr^7);
 j2=-bb/rr^3;j4=-bb(4aa^2+bb^2)/(2rr^7);
 vv=aa bb^2(5aa+3rr)/(2rr^7(aa+rr));
 dd=dR+I dI;xx=xR+I xI;
 swap={{1,0,0,0},{0,0,1,0},{0,1,0,0},{0,0,0,1}};
 mat=dd IdentityMatrix[4]-xx swap;
 spinExpr=ComplexExpand[Tr[mat.ConjugateTranspose[mat]]/4];
 spinTarget=dR^2+dI^2+xR^2+xI^2-dR xR-dI xI;
 kzero=Sqrt[200];ka=Sqrt[119];kb=Sqrt[80];
 mua=239/(2Sqrt[23800]);mub=161/(2Sqrt[16000]);
 ra2=FullSimplify[ka^2(1-mua^2)];
 rb2=FullSimplify[kb^2(1-mub^2)];
 zv=FullSimplify[kzero-ka mua-kb mub];
 redD=5/324;redX=253/135252;
 checks=<|
 "I2_derivative"->FullSimplify[-D[i1,aa]==i2,aa>bb>0],
 "I4_derivative"->FullSimplify[-D[i1,{aa,3}]/6==i4,aa>bb>0],
 "J2_identity"->FullSimplify[i1-aa i2==bb j2,aa>bb>0],
 "J4_identity"->FullSimplify[i3-aa i4==bb j4,aa>bb>0],
 "variance_identity"->FullSimplify[i4-i2^2==vv,aa>bb>0],
 "positive_mean_identity"->FullSimplify[
 (alpha^2+beta^2-alpha beta)(vv+i2^2)+
 (-2alpha^2 hb-2beta^2 ha+alpha beta(ha+hb))i2+
 (alpha^2 hb^2+beta^2 ha^2-alpha beta ha hb)==
 (alpha^2+beta^2-alpha beta)vv+
 (alpha(i2-hb)-beta(i2-ha)/2)^2+3(beta(i2-ha))^2/4],
 "spin_swap_trace"->Simplify[spinExpr==spinTarget],
 "spin_weight_identity"->Simplify[ComplexExpand[
 Abs[dd+xx]^2/4+3Abs[dd-xx]^2/4]==spinTarget],
 "transition_prefactor"->FullSimplify[(2Pi)^4(Sqrt[2]/Pi^3)^2==32/Pi^2],
 "a5_b3_oracles"->FullSimplify[{i2,i4,j2,j4,vv}/.{aa->5,bb->3}],
 "complex_spin_oracle"->{Abs[(1+2I)+(3-I)]^2,Abs[(1+2I)-(3-I)]^2,
 (Abs[(1+2I)+(3-I)]^2+3Abs[(1+2I)-(3-I)]^2)/4},
 "G4_exact"->{ra2,rb2,zv,FullSimplify[2Sqrt[ra2 rb2]]},
 "vector_d_x_w"->{redD,redX,Together[redD^2+redX^2-redD redX]},
 "exact_conditional_node"->FullSimplify[
 ((3/Sqrt[7]-2/Sqrt[7])^2-1/7)==0],
 "b_zero_limits"->FullSimplify[{i2,i4,j2,j4,vv}/.bb->0,aa>0]
 |>;
 checks]];
 <|"body_wall_s"->timed[[1]],"body_cpu_s"->timed[[2,1]],"checks"->timed[[2,2]]|>
]
