ClearAll[a,b,c,d,v0,v1,f0,f1,alpha,beta,v,f,poly,corner,
  eps,chi,eta,dEg,dEc,dU,dEots,sH,sHeI,sHeII,cH,cHe,
  ah,ahei,ell,m,y,z,vp,fp,photonIdentity,weights];

v=(1-alpha)v0+alpha v1;
f=(1-beta)f0+beta f1;
poly[x_,q_]=a+b x+c q+d x q;
weights={(1-alpha)(1-beta),alpha(1-beta),(1-alpha)beta,alpha beta};
corner=weights.{poly[v0,f0],poly[v1,f0],poly[v0,f1],poly[v1,f1]};

dEg=-eps;
dEc=chi;
dU=eta(eps-chi);
dEots=(1-eta)(eps-chi);

sH={-1,1,0,0,0};
sHeI={0,0,-1,1,0};
sHeII={0,0,0,-1,1};
cH={1,1,0,0,0};
cHe={0,0,1,1,1};

ell=57/40;
m=737/1000;
ah=vp((ell-m)+m y)+(1-vp)fp z;
ahei=vp m(1-y)+(1-vp)fp(1-z);
photonIdentity=ah+ahei+vp(2-ell)+(1-vp)(1-fp)-(1+vp);

<|
 "MultiAffineCornerInterpolationResidual"->FullSimplify[poly[v,f]-corner],
 "CornerWeights"->weights,
 "CornerWeightsSumResidual"->FullSimplify[Total[weights]-1],
 "AugmentedAbsorptionEnergyResidual"->FullSimplify[dEg+dEc+dU+dEots],
 "HydrogenInvariantResiduals"->{cH.sH,cH.sHeI,cH.sHeII},
 "HeliumInvariantResiduals"->{cHe.sH,cHe.sHeI,cHe.sHeII},
 "CascadePhotonIdentityResidual"->FullSimplify[photonIdentity],
 "BranchMixedDerivatives"->{D[ah,vp,fp],D[ahei,vp,fp]},
 "NonnegativeCornerWeightDomain"->
   Reduce[0<=alpha<=1 && 0<=beta<=1 && And@@Thread[weights>=0],
     {alpha,beta},Reals],
 "InstantaneousCornerTheoremDoesNotImplyNonlinearFlowEnclosure"->True
|>
