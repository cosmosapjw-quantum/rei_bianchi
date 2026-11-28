(* Only this output projection replaces the PHYS85 repair01 wrapper. Core unchanged. *)
PHYS85Input=ImportString[PHYS85FrozenJSON,"RawJSON"];
PHYS85RawReport=TimeConstrained[
 CheckAbort[PHYS85RunVerification[PHYS85Input],PHYS85VerificationSnapshot["ABORTED_FIRST_ATTEMPT_PRESERVED"]],
 55,PHYS85VerificationSnapshot["TIME_LIMIT_EXCEEDED_FIRST_ATTEMPT_PRESERVED"]];
ClearAll[PHYS86EventResidual,PHYS86EnsembleResidual];
PHYS86EventResidual[c_]:=Module[{s=c["source"],o=Lookup[c,"independent_oracle",<||>]},
 If[!AssociationQ[s]||!KeyExistsQ[o,"energy_columns"],Return["INCOMPLETE_ROW"]];
 Total[Abs[Together[#]]&/@Join[
 Values[s["energy_columns_MeV"]]-o["energy_columns"],Values[s["count_columns"]]-o["count_columns"],
 {s["energy_residual_MeV"],s["particle_residual"],s["K_in_normal_MeV"]-o["Kin"],s["K_c_normal_MeV"]-o["Kc"],s["E_gamma_normal_MeV"]-o["Egamma"]},
 Values[s["incidence_residuals"]],o["A_Z_incidence"],Lookup[o,{"gamma_identity_residual","photon_null_residual","daughter_mass_shell_residual","total_energy_residual","total_boost_momentum_residual"}]]]
];
PHYS86EnsembleResidual[c_]:=Module[{s=c["source"],o=Lookup[c,"independent_oracle",<||>]},
 If[!AssociationQ[s]||!KeyExistsQ[o,"energy_columns"],Return["INCOMPLETE_ROW"]];
 Total[Abs[Together[#]]&/@Join[Values[s["mean_energy_columns_MeV"]]-o["energy_columns"],Values[s["mean_count_columns"]]-o["count_columns"],{s["energy_residual_MeV"],s["particle_residual"],s["mean_joint_hKc_MeV"]-o["joint_hKc"],s["owner_energy_covariance_MeV"]-o["covariance"]}]]
];
PHYS86RecoveryLabels=Lookup[$checks,"label"];
PHYS86RecoveryLabelSHA=Hash[StringRiffle[PHYS86RecoveryLabels,"\n"],"SHA256","HexString"];
(* Expected SHA is injected mechanically from PHYS85_EXPECTED_ORDER.json by assembly. *)
PHYS86ExpectedLabelSHA="2c238591e544c5c805d5af5a73d4c14ab3d4af2aa2bef9d0c15e464f4ee47add";
PHYS86ProjectionFailures=If[PHYS86RecoveryLabelSHA===PHYS86ExpectedLabelSHA,{}, {"ASSERTION_LABEL_ORDER_MISMATCH"}];
PHYS86Triples=Table[If[i<=Length[$cases]&&AssociationQ[$cases[[i]]["source"]],Lookup[$cases[[i]]["source"],{"K_in_normal_MeV","K_c_normal_MeV","E_gamma_normal_MeV"}],"NOT_REACHED"],{i,{1,5,9,13,17,21,25,29,33}}];
PHYS86Covariances=Table[If[i<=Length[$ensembles]&&AssociationQ[$ensembles[[i]]["source"]],$ensembles[[i]]["source"]["owner_energy_covariance_MeV"],"NOT_REACHED"],{i,{1,3,5}}];
PHYS86Certificate=<|"schema"->"PHYS86_PHYS85_COMPACT_CERT_V1","status"->PHYS85RawReport["status"],
 "counts"->{Length[$cases],Length[$ensembles],Length[$guards],Length[$checks],Count[Lookup[$checks,"pass"],True]},
 "complete"->TrueQ[PHYS85RawReport["status"]==="PASS"&&{Length[$cases],Length[$ensembles],Length[$guards],Length[$checks]}==={36,6,23,1017}&&PHYS86ProjectionFailures==={}],
 "bits"->StringJoin[If[TrueQ[#],"1","0"]&/@Lookup[$checks,"pass"]],"label_sha256"->PHYS86RecoveryLabelSHA,
 "triples"->PHYS86Triples,"covariances"->PHYS86Covariances,
 "event_residual_sumabs"->(PHYS86EventResidual/@$cases),"ensemble_residual_sumabs"->(PHYS86EnsembleResidual/@$ensembles),
 "guard_tags"->Table[If[FailureQ[g["result"]],ToString[First[g["result"]]],"NOT_A_FAILURE"],{g,$guards}],
 "failures"->Join[$failures,PHYS86ProjectionFailures],"runtime"->{$Version,$SystemID},"kernel_count"->1,"hardware"->"UNOBSERVED","HH_R10"->"OFF"|>;
PHYS86Transport[PHYS86Certificate]
