ClearAll["Global`*"];
s = {{-1,-1,-1,0,0,0},{0,0,0,1,1,-1},{0,0,0,-1,-1,1},{-1,1,1,0,0,0},{0,1,1,-1,-1,1},{0,0,0,1,1,-1},{1,-1,-1,0,0,0}};
c = {{1,1,2,7,2,3,8},{0,1,1,0,0,0,0},{1,0,0,3,2,2,4},{1,1,0,0,2,1,1},{0,0,1,0,0,1,0},{0,0,0,1,0,0,1}};
xx = {x1,x2,x3}; pp = {p1,p2,1-p1-p2}; dd = {d1,d2,d3}; rr = xx - pp Total[xx];
sharp[x_] := Module[{d={1,3},p={1/2,1/2},h=1,r,j,jp,b},r=x-p Total[x];j=h d.x;jp=h (d.p) Total[x];b=h (Max[d]-Min[d])Total[Abs[r]]/2;<|"exact_flux"->j,"lifted_flux"->jp,"defect"->j-jp,"bound"->b|>];
ExportString[<|
"scope"->"Declared finite matrix and symbolic examples only; general proof is independently reviewed separately",
"material_order"->{"H","H+","D+","Li","H2","HD","LiH"},
"event_order"->{"RA","Do","Dp","FT","FS","R"},
"invariant_rows"->{"baryon","charge","bound_electron","H1","D2","Li7"},
"invariant_matrix_product"->c.s,
"thermal_material_particle_delta"->Total[s],
"zero_sum_residual"->Expand[Total[rr]],
"defect_identity"->Expand[h (dd.xx-(dd.pp)Total[xx])-h dd.rr],
"centering_identity"->Expand[(dd-center {1,1,1}).rr-dd.rr],
"constant_rate_defect"->Expand[h dd.rr/.{d1->dc,d2->dc,d3->dc}],
"distinct_pair_reference_flux_identity"->Cancel[k (nref yA)(nref yB)/nref-k nref yA yB],
"sharp_low"->sharp[{1,0}],
"sharp_high"->sharp[{0,1}],
"physical_rate_admission"->False,
"nuclear_Q_admission"->False|>,"RawJSON"]
