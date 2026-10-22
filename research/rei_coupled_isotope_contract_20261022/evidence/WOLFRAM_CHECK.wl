(* Exact submitted expression. Symbols are deliberately symbolic. *)
Clear[nb,t,chi,k,H,T,Q,nbdot,Tdot,chidot];
u=(3/2) k nb T chi;
udot=D[u,nb] (-3 H nb)+D[u,T] Tdot+D[u,chi] chidot;
td=FullSimplify[Tdot/.First[Solve[udot+3 H (u+nb k T chi)==Q,Tdot]]];
eosResidual=FullSimplify[td-(-2 H T-T chidot/chi+2 Q/(3 k nb chi))];
fractionResidual=FullSimplify[((g f y+s) y-f y st)/y^2-(g f+(s-f st)/y)];
qResidual=Expand[(qb+b0)-(b0-bq)-(qb+bq)];
<|"temperature_derivative"->td,"EOS_residual"->eosResidual,
"fraction_source_residual"->fractionResidual,"energy_reference_residual"->qResidual|>
