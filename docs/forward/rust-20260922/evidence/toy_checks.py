from fractions import Fraction as F
import json
p=[F(1),F(3)];s=sum(p);mass=[x*8/s for x in p]
assert mass==[2,6]
w=[x/s for x in p];rate=F(-4);pos=[x*max(rate,0) for x in w];neg=[x*max(-rate,0) for x in w]
assert pos==[0,0] and neg==[1,3] and [a-b for a,b in zip(pos,neg)]==[-1,-3]
n=list(map(F,[1,2,3,4]));r=[F(i,10) for i in [1,2,3,4]]
rhs=[-r[i]*n[i]+(r[i+1]*n[i+1] if i<3 else 0) for i in range(4)]
assert sum(rhs)==F(-1,10)
c=F('2.99792458e10');mpc=F('3.085677581491367e24');sig=F('6e-18');nh=F('1.2e-5')
assert c*sig/mpc**3==(c/100)*(sig/10000)/(mpc/100)**3
assert nh*sig*mpc==(nh*1000000)*(sig/10000)*(mpc/100)
assert (1+F(3))**3==64
print(json.dumps({'grade':'EXACT_RATIONAL_TOY_NOT_RUST_TEST','checks':6,'passed':True,'mass':list(map(str,mass)),'signed':list(map(str,[a-b for a,b in zip(pos,neg)])),'redshift_rhs':list(map(str,rhs)),'redshift_sum':str(sum(rhs))}))
