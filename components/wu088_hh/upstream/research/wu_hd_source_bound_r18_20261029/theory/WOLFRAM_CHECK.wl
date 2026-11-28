mant={399/100,292/100,115/100,274/100,333/100,318/100,285/100,255/100,230/100,208/100};
expo={14,11,10,10,10,10,10,10,10,10};
ref={399/10^22,73/2500000000000000000,23/200000000000000000,137/500000000000000000,333/1000000000000000000,159/500000000000000000,57/200000000000000000,51/200000000000000000,23/100000000000000000,13/62500000000000000};
unit=MapThread[#1/10^(#2+6)-#3&,{mant,expo,ref}];
nu={-1,-1,1,1}; cons=({1,1,0,2}.nu); deut=({0,1,1,0}.nu); charge=({1,0,1,0}.nu);
res=Join[unit,{cons,deut,charge,1/4+3/4-1,5/4+15/4-5}];
ExportString[<|"exact_zero_residuals"->res,"all_zero"->And@@Thread[res==0],"positive_native_printed_cells"->And@@Thread[ref>0],"residual_count"->Length[res],"state_to_thermal_spin"->3/4,"scope"->"exact printed nominal units and conservation; no physical error enclosure"|>,"RawJSON"]
