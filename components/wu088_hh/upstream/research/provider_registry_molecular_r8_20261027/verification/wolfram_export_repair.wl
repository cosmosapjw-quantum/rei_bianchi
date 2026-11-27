Module[{damp, delta, t, s, j, n, u, phi, base, residuals, signs, h, brute, row, out},
 phi=(Exp[damp delta]-1)/damp;
 base=Element[{damp,delta,t,s,u},Reals]&&delta>0&&damp!=0;
 residuals={
  FullSimplify[D[(Exp[damp u]-1)/damp,u]-Exp[damp u],base],
  FullSimplify[Limit[(Exp[damp delta]-1)/damp,damp->0]-delta,delta>0],
  FullSimplify[Integrate[Exp[damp(t-s)],{s,j delta,(j+1)delta},
    Assumptions->base&&Element[j,Integers]]-phi Exp[damp(t-(j+1)delta)],base&&Element[j,Integers]],
  FullSimplify[(phi Exp[damp(t-(j+1)delta)]/.t->(n+1)delta)-
    phi Exp[damp(n-j)delta],base&&Element[{n,j},Integers]],
  FullSimplify[(phi Exp[damp(t-(j+1)delta)]/.t->n delta)-
    phi Exp[damp(n-j-1)delta],base&&Element[{n,j},Integers]],
  FullSimplify[(1-Exp[damp delta])/(-damp)-phi,base],
  FullSimplify[(1/Exp[-damp delta]-1)/damp-phi,base]
 };
 signs={
  FullSimplify[D[Exp[damp t],t]<=0,Element[{damp,t},Reals]&&damp<=0],
  FullSimplify[D[Exp[damp t],t]>=0,Element[{damp,t},Reals]&&damp>=0],
  FullSimplify[D[(Exp[damp u]-1)/damp,u]>0,base],
  FullSimplify[phi>0,base],
  FullSimplify[t-s>=(n-j-1)delta,Element[{t,s,delta},Reals]&&delta>0&&Element[{n,j},Integers]&&t>=n delta&&s<=(j+1)delta],
  FullSimplify[(n+1)delta-s>=(n-j)delta,Element[{s,delta},Reals]&&delta>0&&Element[{n,j},Integers]&&s<=(j+1)delta]
 };
 h={1};
 Do[row={Last[h]};If[n>=2,AppendTo[row,h[[n-1]]/2]];
    If[n>=4,AppendTo[row,h[[n-3]]/5]];AppendTo[h,Min[row]],{n,1,8}];
 brute=Table[Min[Flatten[Table[If[2 j+4 u<=n,(1/2)^j(1/5)^u,1],
                  {j,0,Floor[n/2]},{u,0,Floor[n/4]}]]],{n,0,8}];
 out=<|"schema"->"WU_R8_NEW_SYMBOLIC_CHECKS_EXPORT_REPAIR_V1","scalar_residuals"->(ToString[#,InputForm]&/@residuals),
 "scalar_residual_count"->Length[residuals],"signed_inequalities"->(ToString[#,InputForm]&/@signs),
 "signed_inequality_count"->Length[signs],"kernel_DP_minus_integer_enumeration"->(ToString[#,InputForm]&/@(h-brute)),
 "kernel_controls"->Length[h],"new_scientific_calls"->1,
 "old_R6_R7_runner_replays"->0,"general_proof_replaced_by_CAS"->False|>;
 ExportString[out,"RawJSON"]
]
