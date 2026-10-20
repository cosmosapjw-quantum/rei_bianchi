ClearAll[step,a,b,c,d,e,cp,cpp,s0,M,G,P,m,mp,mm];
cells={{a,b},{},{c},{d,e}};
candidate=ReplacePart[cells,3->{cp,cpp}];
owned=Flatten[candidate,1];
borrowed=Join@@candidate;
ownedState=Fold[step,s0,owned];
borrowedState=Fold[Function[{s,cell},Fold[step,s,cell]],s0,candidate];
wrongState=Fold[step,s0,Join[Flatten[Delete[cells,3],1],{cp,cpp}]];
baseCopies=1+2 (P+G);
nodeCopies=(1+2 G) M+Sum[2 M-2 m[i]+mp[i]+mm[i],{i,1,P}];
equalLengthCopies=Simplify[nodeCopies/.{m[_]->mc,mp[_]->mc,mm[_]->mc},Assumptions->Element[{P,G},Integers]&&P>=0&&G>=0];
ExportString[<|"ordered_symbolic_trace_equal"->SameQ[ownedState,borrowedState],"append_replacement_counterexample_equal"->SameQ[ownedState,wrongState],"ordered_nodes"->ToString[owned,InputForm],"new_prepared_state_copies_per_successful_full_central_Jacobian"->0,"old_prepared_state_copies"->ToString[baseCopies,InputForm],"old_node_copies_general"->ToString[nodeCopies,InputForm],"old_node_copies_same_node_counts"->ToString[equalLengthCopies,InputForm],"C40_P80_G4_M640_example"-><|"old_prepared_state_copies"->(baseCopies/.{P->80,G->4}),"old_prepared_node_copies"->(equalLengthCopies/.{P->80,G->4,M->640})|>,"scope"->"symbolic storage-order and copy-count check only; general proof is induction on the identical node sequence; no native cosmology or time-accuracy result"|>,"RawJSON"]
