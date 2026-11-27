ClearAll[h,s,nu,rr,pp,qq];
ratio=Expand[(-5h qq-nu qq-2pp s-2qq s)/pp-qq(-5h pp-4s qq)/pp^2]/.qq->rr pp//Simplify;
bounds={ratio/.rr->-1/2,ratio/.rr->1}//Simplify;
aa={{-5h+2s-nu/3,nu/3},{2nu/3,-5h-4s-2nu/3}};
vals={h->1/5,s->7/50,nu->10^8};dt=1/10;
exact=N[MatrixExp[N[(aa/.vals)dt,60]].{1,1},40];
bmat={{-nu/3,nu/3},{2nu/3,-2nu/3}}/.vals;
dr=DiagonalMatrix[Exp[N[{-5h+2s,-5h-4s}/.vals,60]dt/2]];
split=N[dr.MatrixExp[N[bmat dt,60]].dr.{1,1},40];
rOf[x_]:=(x[[2]]-x[[1]])/(2x[[1]]+x[[2]]);
ExportString[<|"ratioRHS"->ToString[ratio,InputForm],"ratioBoundaryRHS"->ToString[bounds,InputForm],"stiffExact"->exact,"stiffExactRatio"->rOf[exact],"stiffStrang"->split,"stiffStrangRatio"->rOf[split]|>,"RawJSON"]
