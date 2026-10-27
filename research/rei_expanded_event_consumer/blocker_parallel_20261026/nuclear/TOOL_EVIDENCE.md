# Actual external symbolic evidence — 2026-10-26

Wolfram context used first. Generic median lifetime suggestions were rejected as irrelevant. No local numerical runtime was used.

Call1 (timeConstraint10):
```
a=(1-Exp[-k h])/k; c=(h-a)/k; p1=Exp[-k h] p0+a s; int=a p0+c s;
{FullSimplify[p1+k int-p0-s h],FullSimplify[D[p1,h]-(s-k p1)],
 FullSimplify[D[int,h]-p1],Limit[a,k->0],Limit[c,k->0],
 FullSimplify[D[{p1,lam int,kap int},p0]],
 N[{1/(3511/4),Log[2]/(4500*86400),(4500*86400)/Log[2]},15]}
```
Returned:
```
{0,0,0,h,h^2/2,
 {Exp[-h*k],(lam-lam/Exp[h*k])/k,(kap-kap/Exp[h*k])/k},
 {0.0011392765593847906579,1.7827859582303120098e-9,5.6091983189762897278e8}}
```
Warnings included Power::infy, Infinity::indet and General::messages during removable-limit handling. The conversion numbers are s^-1,s^-1,s; they preserve laboratory input scope and are not defaults or admission.

Targeted Call2 (timeConstraint10) used regular series and exact integer incidence products:
```
{Normal[Series[(1-Exp[-x])/x,{x,0,3}]],
 Normal[Series[(x-1+Exp[-x])/x^2,{x,0,3}]],
 {1,1,3,3,0,0}.{{-1,0},{1,0},{0,-1},{0,1},{1,1},{1,1}},
 {0,1,1,2,-1,0}.{{-1,0},{1,0},{0,-1},{0,1},{1,1},{1,1}},
 {0,0,0,0,1,-1}.{{-1,0},{1,0},{0,-1},{0,1},{1,1},{1,1}}}
```
Returned without warnings:
```
{1-x/2+x^2/6-x^3/24,
 1/2-x/6+x^2/24-x^3/120,{0,0},{0,0},{0,0}}
```
Provider wall observed by wrapper for batches containing these calls was8.4s and8.3s; this is not isolated Wolfram CPU. Provider computational cost is unreported and UNKNOWN_NOT_ZERO. These calls grant no additional local campaign budget.

Source retrieval evidence: SciSpace query sought direct UCNtau2021 and Lucas/Unterweger lifetime data; results included primary UCNtau abstract. Exa primary-source searches returned NIST full public-domain PDF evaluation, UCNtau arXivv2, Vogel/Beacom original PDF AppendixA2, Akulov/Mamyrin2005 abstract, and NACREII collaboration reaction table. Exact bibliographic locators and usable scope appear in R1_R10_RESEARCH.md. No searched alternative lifetime or unsourced Wolfram entity value was substituted.
