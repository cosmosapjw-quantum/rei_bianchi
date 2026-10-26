ClearAll[c,r,y,a1,a2,q1,q2,e1,e2,chi,dr,dy,da1,da2];
w={c*r*y*a1*q1,c*r*y*a2*q2}; energies={e1-chi,e2-chi};
mom={Total[w],{e1,e2}.w,energies.w};
dw=D[w,r]*dr+D[w,y]*dy+D[w,a1]*da1+D[w,a2]*da2;
explicit=c*{q1*(r*a1*dy+r*y*da1+y*a1*dr),q2*(r*a2*dy+r*y*da2+y*a2*dr)};
physical=r*w;
checks=Join[{Together[mom[[2]]-chi*mom[[1]]-mom[[3]]]},Together[dw-explicit],Together[D[physical,r]-2*physical/r],{Together[D[mom[[3]],y]-c*r*(a1*q1*(e1-chi)+a2*q2*(e2-chi))]}];
x=(src-z*rr)/r; quotient=Together[D[x,src]*dsrc+D[x,z]*dz+D[x,rr]*drr+D[x,r]*dr-((dsrc-rr*dz-z*drr)/r-x*dr/r)];
checks=Append[checks,quotient];
<|"scalar_residuals"->checks,"all_zero"->And@@Thread[checks==0],"count"->Length[checks],"scope"->"two arbitrary finite atoms; linearity extends to finite sums; no physical stopping check"|>
