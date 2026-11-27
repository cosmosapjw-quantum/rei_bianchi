ClearAll["Global`*"];
ciA={-1,1,0,0,1}; ciB={0,0,-1,1,1}; cx={1,-1,-1,1,0};
stoich=Transpose[{ciA,ciB,cx}];
nuclei={{1,1,0,0,0},{0,0,1,1,0}};
charge={0,1,0,1,-1}; particles={1,1,1,1,1};
boundEnergy={0,chiA,0,chiB,0};
deltaBound=Simplify[boundEnergy.stoich];
qheat={-chiA,-chiB,chiA-chiB};
particleChanges=particles.stoich;
tempdot=-2 hub temp+2 heat/(3 kb part)-temp edot/part;
uth=3 kb temp part/2;
uthdot=Simplify[D[uth,temp] tempdot+D[uth,part] edot];
uvol=nref uth;
uvolDot=Simplify[-3 hub nref uth+nref uthdot];
bvol=nref binding;
bvolDot=-3 hub nref binding+nref bdot;
pressure=2 uvol/3;
result=<|
"nucleusStoichiometry"->nuclei.stoich,
"chargeStoichiometry"->charge.stoich,
"particleChanges"->particleChanges,
"deltaIonizationEnergy"->deltaBound,
"collisionEnergyPerEventResidual"->Simplify[deltaBound+qheat],
"thermalPerHResidual"->Simplify[uthdot+2 hub uth-heat],
"thermalVolumeResidual"->Simplify[uvolDot+5 hub uvol-nref heat],
"chemicalVolumeResidual"->Simplify[bvolDot+3 hub bvol-nref bdot],
"collisionTotalVolumeResidual"->Simplify[(uvolDot+bvolDot+3 hub (uvol+bvol+pressure))/.heat->-bdot],
"photoRRExchangeResidual"->Simplify[(heat+bdot+escape-absorbed)/.heat->absorbed-bdot-escape]
|>;
InputForm[result]