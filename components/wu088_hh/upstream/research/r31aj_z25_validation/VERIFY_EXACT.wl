ClearAll[u,h,o0,o1,d0,d1,c,b,m,a,g,ee];
p=(2u^3-3u^2+1)o0+(u^3-2u^2+u)h d0+(-2u^3+3u^2)o1+(u^3-u^2)h d1;
checks=<|"midpoint_O_identity"->Simplify[(p/.u->1/2)-((o0+o1)/2+h(d0-d1)/8)],
"midpoint_dotO_identity"->Simplify[(D[p,u]/h/.u->1/2)-(3(o1-o0)/(2h)-(d0+d1)/4)],
"metric_preserving_source_perturbation"->Expand[(c+m)+(b-m)-(c+b)],
"K_shift_identity"->Expand[((c+m)-(b-m))/2-(c-b)/2-m],
"equal_distance_counterexample"->FullSimplify[Abs[a-(a+g)/2]-Abs[g-(a+g)/2],Element[{a,g},Reals]],
"sharp_margin_perturbation"->ToString[FullSimplify[(Abs[2-ee]-Abs[-2-ee])-(Abs[2]-Abs[-2]),0<=ee<2],InputForm]|>;
ExportString[checks,"RawJSON"]