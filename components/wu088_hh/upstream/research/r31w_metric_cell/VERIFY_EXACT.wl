(* Exact small-matrix checks executed through WolframLanguageEvaluator.
   No HH arrays, integrals, propagations or production assumptions. *)
ClearAll[tt,hb,ss,aa,oo,dd,hh,tr,rr,op,dp,rp,ag,gp,q,oq,dq,rq,o0,o1,r0,r1];
ass=Element[{tt,hb,ss,aa,o0,o1,r0,r1},Reals]&&hb>0&&o0>0&&o1>0&&0<=ss<=1;
adj[x_]:=Simplify[ConjugateTranspose[x],ass];
oo={{2+tt^2,I tt},{-I tt,3+tt^2}};dd={{I tt,tt+I},{-2 tt+I,1-I tt}};hh={{2,tt+I},{tt-I,-1}};tr={{1,tt},{I tt,1+I tt^2}};
rr=Simplify[D[oo,tt]-dd-adj[dd],ass];op=adj[tr].oo.tr;dp=adj[tr].dd.tr+adj[tr].oo.D[tr,tt];rp=Simplify[D[op,tt]-dp-adj[dp],ass];
ag=-I/hb Inverse[oo].hh-Inverse[oo].dd;gp=-I/hb Inverse[op].(adj[tr].hh.tr)-Inverse[op].dp;
q={{1},{I tt}};oq=adj[q].oo.q;dq=adj[q].dd.q+adj[q].oo.D[q,tt];rq=Simplify[D[oq,tt]-dq-adj[dq],ass];
ray=((1-ss)r0+ss r1)/((1-ss)o0+ss o1);weighted=((1-ss)o0/((1-ss)o0+ss o1))r0/o0+(ss o1/((1-ss)o0+ss o1))r1/o1;
ExportString[<|"det_T"->Simplify[Det[tr]],"residual_covariance_zero"->(Simplify[rp-adj[tr].rr.tr,ass]===ConstantArray[0,{2,2}]),"generator_transform_zero"->(Simplify[gp-Inverse[tr].ag.tr+Inverse[tr].D[tr,tt],ass]===ConstantArray[0,{2,2}]),"norm_identity_zero"->(Simplify[adj[ag].oo+oo.ag+D[oo,tt]-rr,ass]===ConstantArray[0,{2,2}]),"rectangular_projection_zero"->(Simplify[rq-adj[q].rr.q,ass]==={{0}}),"affine_rayleigh_convex_identity_zero"->(Simplify[ray-weighted,ass]===0),"affine_rayleigh_derivative"->ToString[Factor[D[ray,ss]],InputForm],"missing_connection_nonzero_at_t0"->(Simplify[(D[op,tt]-adj[tr].dd.tr-adj[adj[tr].dd.tr]-adj[tr].rr.tr)/.tt->0,ass]=!=ConstantArray[0,{2,2}]),"projection_counterexample"->Simplify[{{1/Sqrt[2],1/Sqrt[2]}}.DiagonalMatrix[{1,-1}].{{1/Sqrt[2]},{1/Sqrt[2]}}],"nonaffine_endpoint_defects"->ToString[{(aa ss(1-ss)/.ss->0),(aa ss(1-ss)/.ss->1),(aa ss(1-ss)/.ss->1/2)},InputForm]|>,"RawJSON"]
