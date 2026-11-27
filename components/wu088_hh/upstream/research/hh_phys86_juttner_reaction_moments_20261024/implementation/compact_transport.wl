(* Hash string uses UTF-8 bytes, per official Hash documentation. Payload excludes
   all envelope fields; bytes binds exactly p, not a reserialized association. *)
ClearAll[PHYS86ExactJSON,PHYS86Transport];
PHYS86ExactJSON[x_Association]:=Map[PHYS86ExactJSON,x];
PHYS86ExactJSON[x_List]:=PHYS86ExactJSON/@x;
PHYS86ExactJSON[x_Rational]:=ToString[Numerator[x],InputForm]<>"/"<>ToString[Denominator[x],InputForm];
PHYS86ExactJSON[x_Failure]:=<|"tag"->ToString[First[x]],"details"->PHYS86ExactJSON[x[[2]]]|>;
PHYS86ExactJSON[x_Integer]:=x;
PHYS86ExactJSON[x_String]:=x;
PHYS86ExactJSON[True]:=True;
PHYS86ExactJSON[False]:=False;
PHYS86ExactJSON[Null]:=Null;
PHYS86ExactJSON[x_]:=ToString[x,InputForm];
PHYS86Transport[payload_]:=Module[{p,digest,envelope,out,n,ascii,escapedBytes},
 p=ExportString[PHYS86ExactJSON[payload],"RawJSON","Compact"->True];
 digest=Hash[p,"SHA256","HexString"];n=Length[ToCharacterCode[p,"UTF-8"]];
 envelope=<|"p"->p,"sha256"->digest,"bytes"->n|>;
 out=ExportString[envelope,"RawJSON","Compact"->True];
 ascii=AllTrue[ToCharacterCode[out],0<=#<=127&];
 If[!ascii,Return[ExportString[<|"status"->"NON_ASCII_OUTPUT","sha256"->digest,"payload_bytes"->n|>,"RawJSON","Compact"->True]]];
 escapedBytes=Length[ToCharacterCode[ExportString[out,"RawJSON","Compact"->True],"UTF-8"]];
 If[escapedBytes>8000,
 Return[ExportString[<|"status"->"OUTPUT_TOO_LARGE","sha256"->digest,"payload_bytes"->n,"escaped_bytes"->escapedBytes|>,"RawJSON","Compact"->True]]];
 out
];
