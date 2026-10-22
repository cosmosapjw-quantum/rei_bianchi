# Symbolic check record

Wolfram Language evaluator, timeConstraint 30 s, 2026-10-22. This calculation
was actually executed before the numerical implementation. The output was
the three zero residuals shown below. No numeric fit values were substituted
in these algebraic identities.

```wolfram
Clear[a,b,s0,s1,r,nb,k,chi,x,temp,alpha,dd,lambdaRR,
      xd,td,ud,eg,lam,kap,h,nn,pp];
aa=a/((r/s0) (1+r/s0)^(1-b) (1+r/s1)^(1+b));
dcalc=FullSimplify[r D[Log[aa],r]/2,
  Assumptions->{r>0,s0>0,s1>0,a>0}];
dexpect=-(3 r^2+((2+b)s0+(2-b)s1)r+s0 s1)
  /(2(r+s0)(r+s1));
vf=FullSimplify[dcalc-dexpect,
  Assumptions->{r>0,s0>0,s1>0,a>0}];
xd=-nb alpha x^2;
td=-(2/3)nb alpha x^2 temp dd/(1+x);
lambdaRR=k temp alpha(3/2+dd);
ud=3k((1+x)td+temp xd)/2;
eg=nb x^2(chi alpha+lambdaRR);
energy=FullSimplify[ud+chi xd+eg];
f={-lam nn,lam nn-kap pp^2};
jac=Table[D[f[[i]],{nn,pp}[[j]]],{i,2},{j,2}];
n1=nn Exp[-lam h/2];
p1=pp+nn(1-Exp[-lam h/2]);
p2=p1/(1+kap h p1);
out={n1 Exp[-lam h/2],p2+n1(1-Exp[-lam h/2])};
order=FullSimplify[Normal[
  Series[out-{nn,pp}-h f-h^2 jac.f/2,{h,0,2}]]];
<|"VF_D_residual"->vf,"thermal_energy_residual"->energy,
  "Strang_order2_residual"->order|>
```

Actual returned output:

```text
Out[1]= <|"VF_D_residual" -> 0,
          "thermal_energy_residual" -> 0,
          "Strang_order2_residual" -> {0, 0}|>
```

The rational functions require positive physical temperature and 1+x>0.
Positivity of the exact subflows, the global finite-time order implication,
the primitive's domain and the Bessel boundary data are established in
THEORY.md and the independent review, rather than inferred from a symbolic
zero alone. The failed context-discovery request is an environment/tool
failure; the algebra evaluator itself succeeded.
