(* Finite Markov mathematics only. No physical continuum identification. *)
ClearAll[p,q,r,n1,n2,m];
a = {{1-p,p,0,0},{p,1-p,0,0},{0,0,1,0},{0,0,0,1}};
b = {{1,0,0,0},{0,1-q,q,0},{0,q,1-q,0},{0,0,0,1}};
c = {{1,0,0,0},{0,1,0,0},{0,0,1-r,0},{0,0,r,1}};
y = Factor /@ (a.b.c.c.b.a.{1,0,0,0});
return3 = p^2 ((1-q)^2+q^2(1-r)^2);
return4 = p q^2 (1-r)^2;
checks = <|
 "N3Migration" -> Factor[p(2-p)-return3-Total[Rest[y]]],
 "N4Migration" -> Factor[p q(2-q)-return4-y[[3]]-y[[4]]],
 "HydrogenN" -> Expand[n1+(3n2+n1+m+1)+m+1-2(n1+n2+m+1)-n2]
|>;
Print[checks];
If[!And@@(TrueQ[# == 0]& /@ Values[checks]), Exit[1]];
