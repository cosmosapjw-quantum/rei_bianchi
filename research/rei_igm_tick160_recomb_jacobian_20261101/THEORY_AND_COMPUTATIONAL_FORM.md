# Derivation and strict scientific boundary

Metric signature (-,+,+,+) by project convention. Rate coefficient dimensions are cm³/s; time evolution is *not* performed.

## H II Case A/B external literature formula
Let `lambda = 315614 Kelvin/T`, `u=(lambda/b)^q`, `alpha(T)=a lambda^p/(1+u)^r`, with (a,p,b,q,r)=(1.269e-13,1.503,.522,.470,1.923) Case A and (2.753e-14,1.500,2.740,.407,2.242) Case B.
```
s(T) = d ln alpha/d ln T = -p+r*q*u/(1+u)
alpha_T = alpha*s/T
alpha_TT = alpha/T^2*[s*(s-1)-r*q^2*u/(1+u)^2]
r(T,xe,xHII)=alpha(T)*xe*xHII
r_T=alpha_T*xe*xHII
r_xe=alpha*xHII
r_xHII=alpha*xe
r_TT=alpha_TT*xe*xHII
r_T,xe=alpha_T*xHII ; r_T,xHII=alpha_T*xe
```
Since p−r*q=0.59919(A),0.587506(B)>0, s(T)<0 for all T>0. Positive original interval Tlo..Thi and ionization intervals imply conservative joint source bounds rlo=alpha(Thi)*xe_lo*xHII_lo, rhi=alpha(Tlo)*xe_hi*xHII_hi.

## Equal-node mean factorization versus source-level nonlinearity
Define `C=<alpha(T)xe xHII>_nodes/[alpha(<T>)<xe><xHII>]`. It exactly splits into `<alpha>/alpha(<T>) * <xe xHII>/(<xe><xHII>) * <alpha xe xHII>/(<alpha><xe xHII>)`. These factors isolate temperature nonlinearity, ionic pair covariance and conditional coefficient/ionic correlation, with **equal-node** weights only. Model Case A/B selection and weighting remain scientifically unresolved for the original IGM owner.

## Correct use for first canonical interval local error
The next target is **not** C. For the actual original 26-event RHS step `F_h`, form `D_h(X,Theta)=F_h(X,Theta)-F_{h/2}(F_{h/2}(X,Theta),Theta)` with a **common parent and common source**; certify a joint Jacobian+remainder of the *difference map*. Independent full/half interval subtraction retains parent spread and cannot prove local error. The old original numeric logT 1-tick cross-box error 2.1245050576368385e-4 >2e-4 is binding, with no legal tolerance relaxation. This unit's nodewise recombination derivative is an enabling input, not the original full-map proof.
