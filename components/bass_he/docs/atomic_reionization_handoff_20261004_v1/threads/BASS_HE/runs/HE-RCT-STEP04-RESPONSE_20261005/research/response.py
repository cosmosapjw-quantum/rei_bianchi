"""Cancellation-free first/quadratic response for U'=B(U)+theta H(U).

State blocks: U0[8], S1[8], S2[8], count coefficients[2], four process
coefficients at order one[4] and two[4]. S2 is the quadratic coefficient,
not d2U/dtheta2. This is a formal expansion at theta=0, not a tube bound.
"""
from jets import Jet2
class Response:
    SIZE=34
    def __init__(self,model):
        self.m=model;self.calls=0;self.min_temperature=None;self.max_temperature=None
    def initial(self):return list(self.m.initial)+[self.m.M(0)]*(self.SIZE-8)
    def __call__(self,t,state):
        if len(state)!=self.SIZE:raise ValueError('34 coefficients required')
        self.calls+=1;m=self.m
        u=[Jet2(state[i],state[8+i],state[16+i]) for i in range(8)]
        rr,esc,_,ch=m.evaluate(u)
        temp=m.temperature(u).c[0]
        self.min_temperature=temp if self.min_temperature is None else min(temp,self.min_temperature)
        self.max_temperature=temp if self.max_temperature is None else max(temp,self.max_temperature)
        B=[r*m.tend for r in rr]+[esc*m.tend/(m.nh*m.ev)]
        H,h=m.source(u)
        out=[b.c[0] for b in B]+[b.c[1]+h.c[0] for b,h in zip(B,H)]+[b.c[2]+h.c[1] for b,h in zip(B,H)]
        out += [h.c[0],h.c[1]]
        out += [x.c[1]*m.tend for x in ch]+[x.c[2]*m.tend for x in ch]
        return out
    def reconstruct(self,coeff,epsilon=None):
        e=self.m.epsilon if epsilon is None else epsilon
        return [e*coeff[8+i]+e*e*coeff[16+i] for i in range(8)]
    def electron(self,delta):return delta[0]+self.m.f*(delta[1]+2*delta[2])
