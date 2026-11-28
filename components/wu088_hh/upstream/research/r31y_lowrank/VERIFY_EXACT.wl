ClearAll[lam,f1,f2,aa,bb,tb,ff,kk,ss1,ss2,zz,ll,oo,rr0,gg]; adj[x_]:=ConjugateTranspose[x];
tb={{2,1+I},{0,3}}; ff={{f1,aa+I bb},{aa-I bb,f2}}; zero=ConstantArray[0,{2,2}]; eye=IdentityMatrix[2]; kk=ArrayFlatten[{{zero,tb},{adj[tb],ff}}];
ss1=ArrayFlatten[{{Inverse[adj[tb]],zero},{zero,eye}}]; ss2=ArrayFlatten[{{eye,-ff/2},{zero,eye}}];
cong=FullSimplify[adj[ss1.ss2].kk.(ss1.ss2),Element[{f1,f2,aa,bb},Reals]];
zz={{1,0,0,0},{0,1,0,0},{0,0,0,0},{0,0,0,0},{0,0,1,0},{0,0,0,1}};
ll=IdentityMatrix[6];ll[[2,1]]=I/3;ll[[4,2]]=1/4;ll[[5,1]]=1/5;ll[[6,3]]=I/7;oo=ll.adj[ll];kn=kk/.{f1->1,f2->-2,aa->1/3,bb->1/4};rr0=zz.kn.adj[zz];gg=adj[zz].Inverse[oo].zz;
polycheck=Simplify[Det[lam oo-rr0]-Det[oo]lam^2 Det[lam IdentityMatrix[4]-kn.gg]];
ExportString[<|"inertia_congruence_to_exchange"->(cong===ArrayFlatten[{{zero,eye},{eye,zero}}]),"exchange_eigenvalues"->Eigenvalues[ArrayFlatten[{{zero,eye},{eye,zero}}]],"metric_positive"->PositiveDefiniteMatrixQ[oo],"rank_R0"->MatrixRank[rr0],"nonzero_characteristic_identity"->(polycheck===0),"small_general_eigenvalues"->N[Sort[Eigenvalues[kn.gg]],16],"full_generalized_eigenvalues"->N[Sort[Eigenvalues[{rr0,oo}]],16],"zero_block_not_assumed_for_raw_HH"->True|>,"RawJSON"]
