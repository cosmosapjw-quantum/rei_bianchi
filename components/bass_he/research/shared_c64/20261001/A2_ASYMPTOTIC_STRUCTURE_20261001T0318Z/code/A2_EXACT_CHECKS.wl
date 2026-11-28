ClearAll["Global`*"];
ass = a > 0 && lam > 0 && s > 0 && kap > 0 && alpha > 0;
fshift = FullSimplify[(4 Pi/3) (Integrate[r^4 Exp[-lam r], {r,0,s}, Assumptions -> ass]/s^2 + s Integrate[r Exp[-lam r], {r,s,Infinity}, Assumptions -> ass]),ass];
seriesShift = FullSimplify[Normal[Series[fshift,{s,0,4}]],ass];
smallCoeff = FullSimplify[(1/(4 Sqrt[2] Pi (a/3)^4))*(-4 Pi/45)/(-27/(8 a))*a^3];
hl[f_,ell_] := -kap a/2 (D[f,{r,2}]+2 D[f,r]/r-ell(ell+1) f/r^2)-kap f/r;
cg = -alpha/2 r (r+2 a) Exp[-r/a];
cb = -alpha r^2 (r+6 a) Exp[-r/(2 a)];
resg = FullSimplify[hl[cg,1]+kap/(2 a) cg+alpha kap r Exp[-r/a],ass&&r>0];
resb = FullSimplify[hl[cb,2]+kap/(8 a) cb+alpha kap r^2 Exp[-r/(2 a)],ass&&r>0];
d2s2p = FullSimplify[1/(32 Pi a^4)*(4 Pi/3)*Integrate[r^4 (2-r/a) Exp[-r/a],{r,0,Infinity},Assumptions->a>0],a>0];
q2pz = FullSimplify[1/(32 Pi a^5)*(16 Pi/15)*Integrate[r^6 Exp[-r/a],{r,0,Infinity},Assumptions->a>0],a>0];
q2px = FullSimplify[1/(32 Pi a^5)*(-8 Pi/15)*Integrate[r^6 Exp[-r/a],{r,0,Infinity},Assumptions->a>0],a>0];
intrinsicCoeff = FullSimplify[alpha/(6 Sqrt[2] a^4)*Integrate[r^4 (r+2 a) Exp[-3 r/(2 a)],{r,0,Infinity},Assumptions->a>0]/a^2,a>0];
<|"ShiftedCoulombDipoleSeries"->seriesShift,"SmallRDimensionlessCoefficient"->smallCoeff,"PolarizedGroundResidual"->resg,"PolarizedBrightResidual"->resb,"n2Dipole2s2pz"->d2s2p,"n2Quadrupole2pz"->q2pz,"n2Quadrupole2px"->q2px,"IntrinsicLyCoefficientOverIhbarAlpha_aB2_R2"->FullSimplify[intrinsicCoeff/alpha]|>
