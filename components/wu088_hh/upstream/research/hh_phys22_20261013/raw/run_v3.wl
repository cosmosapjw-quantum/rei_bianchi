(* Surgical correction of input representation and final verdict coverage. *)
Module[{root="/tmp/WU088_HH_PHYS22_20261013.8xnKcM",s,p,tail},
s=Import[FileNameJoin[{root,"finite_response_interval_v2.wl"}],"Text"];
s=StringReplace[s,{
 "Rationalize[hi[x],0]"->"SetPrecision[hi[x],Infinity]",
 "Rationalize[lo[x],0]"->"SetPrecision[lo[x],Infinity]",
 "Rationalize[arr[\"initial_state\"][[1;;4]],0]"->"SetPrecision[arr[\"initial_state\"][[1;;4]],Infinity]",
 "Rationalize[arr[\"q_eV\"],0]"->"SetPrecision[arr[\"q_eV\"],Infinity]",
 "Rationalize[arr[\"weights\"],0]"->"SetPrecision[arr[\"weights\"],Infinity]",
 "Rationalize[5.935621973155476*^-5,0]"->"SetPrecision[5.935621973155476*^-5,Infinity]",
 "Rationalize[arr[\"initial_state\"][[5;;4+nn]],0]"->"SetPrecision[arr[\"initial_state\"][[5;;4+nn]],Infinity]",
 "rows=Map[Rationalize[ToExpression[StringReplace[#,{\"E\"->\"*^\",\"e\"->\"*^\"}]],0]&,tokens,{2}];"->"decToken[st_String]:=Module[{q=ToLowerCase[st],sg=1,parts,m,ex,ds},If[StringStartsQ[q,\"-\"],sg=-1;q=StringDrop[q,1],If[StringStartsQ[q,\"+\"],q=StringDrop[q,1]]];parts=StringSplit[q,\"e\"];m=parts[[1]];ex=If[Length[parts]==2,ToExpression[parts[[2]]],0];ds=StringSplit[m,\".\",All];sg FromDigits[StringJoin[ds]]10^(ex-If[Length[ds]==2,StringLength[ds[[2]]],0])]; rows=Map[decToken,tokens,{2}];",
 "serial[Total[m0]]"->"bounds[Total[iv/@m0]]"
}];
s=StringReplace[s,"ExportString[result,\"RawJSON\"]"->""];
tail="\ngasOK=TrueQ[lo[x]>0&&hi[x]<1&&lo[y]>0&&lo[z]>0&&hi[y+z]<1&&lo[temp]>30000&&hi[temp]<110000];\nsourceOK=TrueQ[Min[en0]lo[ratI]>=Min[nativeE]&&Max[en0]<=Max[nativeE]&&Min[sourceU]>=0&&Min[m0]>=0&&Min[wei]>=0];\nrepOK=And@@(TrueQ[IntegerQ[Log[2,Denominator[#]]]]&/@Join[g0,en0,wei]);\ninvOK=And@@(TrueQ[#>=0]&/@Flatten[Inverse[IdentityMatrix[4]-gain]]);\nresult[\"status\"]=If[TrueQ[tubePass&&etaGain<1&&Min[uu]>0&&gasOK&&sourceOK&&repOK&&invOK&&Min[electron]>0&&Max[tempResp]<0],\"PASS_INTERVAL_TUBE_AND_FINITE_COMPARISON\",\"FAIL\"];\nresult[\"binary64_dyadic_input_check\"]=repOK;result[\"inverse_nonnegative\"]=invOK;\nresult[\"number_representation\"]=\"NPZ inputs decoded to exact binary64 rationals by SetPrecision[...,Infinity]; source decimal tokens parsed exactly; analytic coefficient decimal leaves exact\";\nresult[\"gas_domain\"]=gasOK;result[\"source_domain_check\"]=sourceOK;\nresult[\"electron_interval_rational\"]=serial/@{Floor[electron[[1]]10^30]/10^30,Ceiling[electron[[2]]10^30]/10^30};\nresult[\"temperature_interval_rational_K\"]=serial/@{Floor[tempResp[[1]]10^24]/10^24,Ceiling[tempResp[[2]]10^24]/10^24};\nresult[\"finite_gas_bound_rational\"]=serial/@(Ceiling[10^30 #]/10^30&/@uu);\nresult[\"feedback_bound_rational\"]=serial/@(Ceiling[10^32 #]/10^32&/@err);\nresult[\"kernel\"]=System`$Version;\nExport[FileNameJoin[{DirectoryName[$InputFileName],\"interval_result_v3.json\"}],result,\"RawJSON\"];\nPrint[ExportString[KeyTake[result,{\"status\",\"kernel\",\"node_count\",\"gas_initial_exact\",\"tube_ratios\",\"weighted_gain\",\"finite_gas_bound\",\"feedback_error_bound\",\"electron_lambda1_interval\",\"temperature_lambda1_interval_K\",\"gas_domain\",\"source_domain_check\",\"binary64_dyadic_input_check\",\"inverse_nonnegative\",\"source_z_columns\",\"source_native_shape\",\"threshold_overlap_counts\"}],\"RawJSON\"]];\nIf[result[\"status\"]=!=\"PASS_INTERVAL_TUBE_AND_FINITE_COMPARISON\",Exit[2]];\n";
p=FileNameJoin[{root,"finite_response_interval_v3.wl"}];Export[p,s<>tail,"Text"];
Print["SCRIPT_SHA256="<>FileHash[p,"SHA256","HexString"]];Get[p];
]
