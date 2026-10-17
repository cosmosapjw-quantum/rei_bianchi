(* Executed in Wolfram tool, exact rational arithmetic; not Rust execution. *)
Clear[cl,fl,ct,ft,shift];
identity=Expand[(cl-fl)-(ct-ft)-((cl-ct)-(fl-ft))];
grid=Range[-1,1,1/4];
rows=Table[With[{a=q[[1]],b=q[[2]],c=q[[3]],d=q[[4]]},
  With[{o=Abs[c-d],inn=Abs[a-c]+Abs[b-d],old=Abs[a-b]},
    {old,o,inn,Abs[(a-b)-(c-d)],o<=3/4&&inn<=1/4}]],{q,Tuples[grid,4]}];
checks={And@@((#[[1]]<=#[[2]]+#[[3]])& /@ rows),
        And@@((#[[4]]<=#[[3]])& /@ rows),
        And@@((!TrueQ[#[[5]]]||#[[1]]<=1)& /@ rows)};
<|"identity_residual"->identity,"exact_rational_quadruples"->Length[rows],
  "checks"->checks,"accepted"->Count[rows,x_/;TrueQ[x[[5]]]],
  "loose_pass_but_new_reject"->Count[rows,x_/;x[[1]]<=1&&!TrueQ[x[[5]]]],
  "common_bias_transform_residuals"->{
    Expand[(cl+shift)-(ct+shift)-(cl-ct)],
    Expand[(fl+shift)-(ft+shift)-(fl-ft)],
    Expand[(ct+shift)-(ft+shift)-(ct-ft)]}|>
