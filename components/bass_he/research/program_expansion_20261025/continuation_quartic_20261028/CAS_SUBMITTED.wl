q[z_] := b0+b1 z+b2 z^2;
bet={q[l],b0+b1(l+r)/2+b2 l r,q[r]};
x=(mu+1)/2;
a={b0+b1+b2,b0-b2,b0+b2-b1/3};
bern[j_]:=Binomial[4,j]x^j(1-x)^(4-j);
chord=(q[l](r-z)+q[r](z-l))/(r-l);
zz={0,1/3,1};
zeroLabels={"cell_bernstein","chord_residual","normalization","endpoint_factorization","endpoint_row_transform","old_folded_map","primitive0","primitive2","primitive4","lagrange_reconstruction","stationary_minimum","denominator_weighted_linear_ratio","Dfloor","delta_lipschitz","left_child_control","nodal_violation_at_midpoint"};
zeros={
Expand[q[l+(r-l)t]-(bet[[1]](1-t)^2+2bet[[2]]t(1-t)+bet[[3]]t^2)],
Together[q[z]-chord-b2(z-l)(z-r)],
Expand[Integrate[b0+b1 mu^2+b2 mu^4,{mu,-1,1}]-(2b0+2b1/3+2b2/5)],
Expand[(q[z]/.b2->-b0-b1)-(1-z)(b0+(b0+b1)z)],
Expand[((u0 b0+u1 b1+u2 b2)/.b2->-b0-b1)-((u0-u2)b0+(u1-u2)b1)],
Expand[q[mu^2]-a[[1]](bern[0]+bern[4])-a[[2]](bern[1]+bern[3])-a[[3]]bern[2]],
D[h,h]-1,
D[h^3/3,h]-h^2,
D[h^5/5,h]-h^4,
Expand[q[z]-Sum[q[zz[[i]]] Product[If[j==i,1,(z-zz[[j]])/(zz[[i]]-zz[[j]])],{j,3}],{i,3}]],
Together[q[-b1/(2b2)]-(4b0 b2-b1^2)/(4b2)],
Together[(lam n1+(1-lam)n2)/(lam d1+(1-lam)d2)-(lam d1/(lam d1+(1-lam)d2)n1/d1+(1-lam)d2/(lam d1+(1-lam)d2)n2/d2)],
(7/50)^2/(12*160)-49/4800000,
6*160*(7/50)/(12*160)-(7/50)/2,
Expand[(b0+b1/4)-(b0+(b0+b1/2))/2],
Expand[(b2(z-l)(z-r)/.z->(l+r)/2)+b2(r-l)^2/4]
};
controlLabels={"positive_outside_old_cone","endpoint_exact_signed_factor","outer_nodes_miss_negative","endpoint_boundary_square","signed_negative_lower","signed_negative_upper","positive_weight_sum","positive_weight_range","Dfloor_positive","manufactured_moment_range","subdivision_benefit","signed_row_radius"};
positiveQ=(z-1/2)^2+1/100;
controls={
((positiveQ/.z->1/2)==1/100 && (26/100-1)<0),
Expand[(1-3z/2+z^2/2)-(1-z)(1-z/2)]==0 && 2-3/2>=0,
And@@Thread[({(z-1/2)^2-1/100/.z->0,(z-1/2)^2-1/100/.z->1})>0] && ((z-1/2)^2-1/100/.z->1/2)<0,
Expand[(1-z)^2-(1-2z+z^2)]==0 && 2-2==0,
Min[-2*(1/4),-2*(1/3)]==-2/3,
Max[-2*(1/4),-2*(1/3)]==-1/2,
(2/5*3)/(2/5*3+3/5*7)+(3/5*7)/(2/5*3+3/5*7)==1,
0<(2/5*3)/(2/5*3+3/5*7)<1,
49/4800000>0,
And@@Table[0<=Integrate[mu^(2j),{mu,-1/2,3/4}]<=2/(2j+1),{j,0,2}],
(26/100-1/2)<0 && (26/100-1/4)>=0,
Abs[-160/(2*1024)+160/(2*2048)]<=160*(1/1024+1/2048)/2
};
<|"unit"->"HE-EXP-QUARTIC-12","zero_labels"->zeroLabels,"zeros"->zeros,"control_labels"->controlLabels,"booleans"->controls,"all_zero"->And@@(#===0&/@zeros),"all_true"->And@@controls,"scope"->"New exact symbolic/control checks; no remote CPU inferred; not a second numerical optimizer"|>

