ClearAll[b3,sp];
b3[v_List,y_]:=Sum[Binomial[3,k] v[[k+1]] y^k (1-y)^(3-k),{k,0,3}];
sp[v_List,r_]:=Module[{a0,a1,a2,c0,c1,d0},
 a0=(1-r)v[[1]]+r v[[2]];
 a1=(1-r)v[[2]]+r v[[3]];
 a2=(1-r)v[[3]]+r v[[4]];
 c0=(1-r)a0+r a1;
 c1=(1-r)a1+r a2;
 d0=(1-r)c0+r c1;
 {{v[[1]],a0,c0,d0},{d0,c1,a2,v[[4]]}}
];
Module[{z,sets,checks,l,r,p,sim,integ},
 z=Unique["u"];
 sets={{1,-2,3,1},{1/4,-1/12,-1/12,1/4},{1,2,3,4},{0,0,0,0},{0,1,-1,0},{1/9,-1/9,0,4/9}};
 checks=Flatten[Table[
  {l,r}=sp[v,1/3]; p=b3[v,z];
  integ=Integrate[p,{z,1/7,4/5}];
  sim=(4/5-1/7)(b3[v,1/7]+4 b3[v,(1/7+4/5)/2]+b3[v,4/5])/6;
  {Expand[b3[v,z/3]-b3[l,z]],Expand[b3[v,1/3+2z/3]-b3[r,z]],Together[integ-sim]}
 ,{v,sets}]];
 <|"count"->Length[checks],"exactZero"->Count[checks,0],"nonzero"->Select[checks,#=!=0&]|>
]
