"""PHYS57B small exact-rational standalone certificate.
The full 80-dps code/test/evidence is archived in the two-provider source capsule.
This script is for simple reproducible rational checks, not screened exterior.
"""
from fractions import Fraction as F
from math import factorial
K=F(7,10); a=F(10,7); rho=F(189,10)
B=27; T=216; ell=50; A=F(87,32)
cD=F(9,1000); Ct=F(4849,16800)
e_up=sum((F(1,factorial(n)) for n in range(9)),F(0))+F(10,9*factorial(9))
assert e_up<A
assert 2*a+3*a*a/ell==F(146,49)<3
assert 2*rho*F(5,2)+a*F(22,7)==F(9701,98)<99
p=F(48,725)*(F(12,5)*ell-a)*F(169,25)**ell/A**99
n=A**3*a**3/ell**2
assert p>n>0
lam=(ell-1)*ell
q=K*K-F(lam,T*T)
v=F(2,T)+F(lam,T*T)
assert q==F(255143,583200)>F(1,4)
assert v==F(1441,23328)<F(1,8)
D=(lam*(F(1,B)-F(1,T))+6)/(2*K)
assert D==F(46115,756) and 2*D<122
j=K/(16*ell*3**122)
bound=(1+Ct/cD)**2/j
print("TAIL_CUTOFF_PROVED",ell,"POSITIVE_TO_NEGATIVE_RATIO",float(p/n))
print("FINITE_EXCEPTIONS_PROVED",21,ell-1,"LOGNORM",str(D))
print("WRONSKIAN_JSTAR_EXACT",str(j))
print("HYBRID_INVERSE_UPPER_EXACT",str(bound))
print("HYBRID_INVERSE_UPPER_FLOAT_NONCERT",float(bound))
print("FULL_SCREENED_EXTERIOR_ZS","NOT_CERTIFIED","HH_R10","OFF")
