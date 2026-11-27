(* Concatenate after frozen JSON assignment, event_owner.wl and verifier.
   PHYS85FrozenJSON is a JSON text STRING injected with proper WL string escaping.
   No Get, ToExpression, external program, arbitrary string evaluation or disk write. *)
ClearAll[PHYS85EncodeExact];
PHYS85EncodeExact[x_Association]:=Map[PHYS85EncodeExact,x];
PHYS85EncodeExact[x_List]:=PHYS85EncodeExact/@x;
PHYS85EncodeExact[x_Integer]:=ToString[x,InputForm];
PHYS85EncodeExact[x_Rational]:=ToString[Numerator[x],InputForm]<>"/"<>ToString[Denominator[x],InputForm];
PHYS85EncodeExact[x_Failure]:=<|"failure_tag"->ToString[First[x]],"details"->PHYS85EncodeExact[x[[2]]]|>;
PHYS85EncodeExact[x_String]:=x;
PHYS85EncodeExact[Null]:=Null;
PHYS85EncodeExact[x_?BooleanQ]:=x;
PHYS85EncodeExact[x_]:=ToString[x,InputForm];
PHYS85Input=ImportString[PHYS85FrozenJSON,"RawJSON"];
PHYS85RawReport=TimeConstrained[
 CheckAbort[PHYS85Verify`PHYS85RunVerification[PHYS85Input],PHYS85Verify`PHYS85VerificationSnapshot["ABORTED_FIRST_ATTEMPT_PRESERVED"]],
 55,PHYS85Verify`PHYS85VerificationSnapshot["TIME_LIMIT_EXCEEDED_FIRST_ATTEMPT_PRESERVED"]];
PHYS85Output=<|"schema"->"PHYS85_CLOUD_REFERENCE_OUTPUT_V1","reference_report"->PHYS85RawReport,"runtime_diagnostic"-><|"Wolfram_version"->$Version,"system_id"->$SystemID,"remote_hardware_identity"->"UNOBSERVED","remote_thread_scheduler"->"UNOBSERVED","kernel_count_requested"->1,"parallel_functions_used"->False,"local_guard_admission_claimed"->False|>,"budget"-><|"inherited_spend"->Null,"remaining"->Null,"currency"->Null,"reset"->False|>,"claim_limit"->"Exact arithmetic on rounded pinned inputs and conditional NR theorem; no physical rate, stopping, trajectory or consumer admission."|>;
ExportString[PHYS85EncodeExact[PHYS85Output],"RawJSON","Compact"->False]
