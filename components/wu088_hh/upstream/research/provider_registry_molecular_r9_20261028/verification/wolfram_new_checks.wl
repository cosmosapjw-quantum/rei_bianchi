Module[{aa,bb,a,b,c,del,ph,det,mat,inv,rs,es,ass,zeros,truths,controls},
 det=1-del a-del b ph c;
 mat={{1-del a,-del b},{-ph c,1}};
 inv={{1,del b},{ph c,1-del a}}/det;
 rs=(aa+del b bb)/det; es=bb+ph c rs;
 ass=Element[{aa,bb,a,b,c,del,ph},Reals]&&aa>=0&&bb>=0&&a>=0&&b>=0&&c>=0&&del>0&&ph>0&&det>0;
 zeros=Join[Flatten[Simplify[mat.inv-IdentityMatrix[2]]],
    Simplify[mat.{rs,es}-{aa,bb}],
    {Simplify[es-(ph c aa+(1-del a)bb)/det]}];
 truths=FullSimplify[#,Assumptions->ass]& /@
    {1-del a>0,rs>=0,es>=0,det>0};
 controls={
    (rs/.{aa->1,bb->0,a->0,b->1/2,c->1/4,del->1,ph->1})-8/7,
    (es/.{aa->1,bb->0,a->0,b->1/2,c->1/4,del->1,ph->1})-2/7,
    (rs/.{aa->1,bb->0,a->999/1000,b->0,c->0,del->1,ph->1})-1000,
    Together[(bb+ph c (aa+del b bb)/det)-(ph c aa+(1-del a)bb)/det]
 };
 <|"schema"->"WU_R9_NEW_CAS_V1","zero_residuals"->zeros,"positive_claims"->truths,
   "exact_control_residuals"->controls,"old_kernel_or_exp_replays"->0,
   "scope"->"Exact algebra corroboration; general cell proof and actual source binding separate"|>
]

