ClearAll[z, kk, rr, hh, mu, aa, tt];
cpuStart=TimeUsed[];
timed=AbsoluteTiming[TimeConstrained[Module[{d,n,geometry,derivative,proofBounds,polyUpper,toy,fp,yp,sp,pairToy,spin},
d=((1+z^2)^(-2)-hh)/(kk+rr z);
n=rr hh(1+z^2)^3-rr(1+5z^2)-4kk z;
geometry=Together[(rr^2+kk-2rr Sqrt[kk]mu)-(kk+rr(rr-2Sqrt[kk]mu))]===0;
derivative=Together[D[d,z]-n/((kk+rr z)^2(1+z^2)^3)]===0;
polyUpper=1-(628/1125)^2/2+(628/1125)^4/24;
proofBounds={250/17>14,517/17<36,(2757/500)^2<517/17,(767/200)^2>250/17,
(1103/200)^2>517/17,(1917/500)^2<250/17,
polyUpper<849/1000,1-(176/315)^2/2>21/25,
2757/500-2(767/200)(849/1000)>-1,
1103/200-2(1917/500)(21/25)<-1/2,517<4*250};
toy=Minimize[{tt,aa>=0&&tt>=0&&-tt<=aa-1<=tt&&-tt<=2aa-4<=tt&&-tt<=4aa<=tt},{aa,tt}];
fp={1,2,4};yp={1,4,0};sp={1,1,1};
pairToy=Max[0,Flatten[Table[(yp[[i]]fp[[j]]-yp[[j]]fp[[i]])/(sp[[i]]fp[[j]]+sp[[j]]fp[[i]]),{i,3},{j,3}]]];
spin=Expand[(v+v)^2/4+3(v-v)^2/4-v^2]===0;
<|"geometryIdentity"->geometry,"derivativeIdentity"->derivative,"equalShareSpinIdentity"->spin,
"proofRationalBounds"->proofBounds,"toyMinimize"->ToString[toy,InputForm],"toyPair"->ToString[pairToy,InputForm],
"toyPairAgrees"->(pairToy==8/3),"toyOptimizerAgrees"->(toy[[1]]==8/3&&(aa/.toy[[2]])==2/3),
"scope"->"Exact symbolic identities and rational bounds plus one rational toy; no experimental TDCS/model evaluation or prior-suite replay"|>
],10,$Aborted]];
<|"bodyCPU_s"->(TimeUsed[]-cpuStart),"bodyWall_s"->timed[[1]],"result"->timed[[2]],"remoteTotalCPU"->"UNKNOWN_NOT_ZERO"|>
