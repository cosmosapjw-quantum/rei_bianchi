"""Closed event solutions are differentiated independently with SymPy.

No ODE integrator or nonlinear event/root solver is used. All derivatives at
the reference point are exact rationals, including logarithmic/exponential
closed flows whose nominal exponent vanishes.
"""
from fractions import Fraction
import sys
import unittest
from pathlib import Path

import sympy as s

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.hybrid_mixed import FlowJet, ScalarJet, ResetJet, transport_event

t,a,b=s.symbols('t a b',real=True)
ZERO={a:0,b:0}


def rat(v):
    v=s.cancel(s.simplify(v))
    if not v.is_Rational:
        raise ValueError(f'non-rational reference coefficient: {v}')
    return Fraction(int(s.numer(v)),int(s.denom(v)))


def compare_case(xs,initial,fm,fp,guard,reset,tau,synchronized):
    n=len(xs);coords=[t,*xs,a,b]
    z0=[s.sympify(v).subs(ZERO) for v in initial]
    pre_at={t:0,a:0,b:0,**dict(zip(xs,z0))}
    y0=[s.sympify(v).subs(pre_at) for v in reset]
    post_at={t:0,a:0,b:0,**dict(zip(xs,y0))}
    def value(v,sub):return rat(s.sympify(v).subs(sub))
    def flow(expr,sub):
        return FlowJet([value(f,sub) for f in expr],
                       [value(s.diff(f,t),sub) for f in expr],
                       [[value(s.diff(f,x),sub) for x in xs] for f in expr],
                       [value(s.diff(f,a),sub) for f in expr],
                       [value(s.diff(f,b),sub) for f in expr])
    gj=ScalarJet(value(guard,pre_at),
                 [value(s.diff(guard,x),pre_at) for x in coords],
                 [[value(s.diff(guard,x,y),pre_at) for y in coords] for x in coords])
    rj=ResetJet(list(map(rat,y0)),
                [[value(s.diff(r,x),pre_at) for x in coords] for r in reset],
                [[[value(s.diff(r,x,y),pre_at) for y in coords] for x in coords] for r in reset])
    u=[value(s.diff(z,a),ZERO) for z in initial]
    v=[value(s.diff(z,b),ZERO) for z in initial]
    w=[value(s.diff(z,a,b),ZERO) for z in initial]
    result=transport_event(flow(fm,pre_at),flow(fp,post_at),gj,rj,u,v,w)
    for name,orders in [('u_plus',(a,)),('v_plus',(b,)),('w_plus',(a,b))]:
        expected=[value(s.diff(z,*orders),ZERO) for z in synchronized]
        assert result[name]==expected,(name,result[name],expected)
    for name,orders in [('event_time_a',(a,)),('event_time_b',(b,)),('event_time_ab',(a,b))]:
        expected=value(s.diff(tau,*orders),ZERO)
        assert result[name]==expected,(name,result[name],expected)
    return result,(flow(fm,pre_at),flow(fp,post_at),gj,rj,u,v,w)


class HybridExactTests(unittest.TestCase):
    def test_fixed_birth_preserves_prior_sensitivities(self):
        x,w,p=s.symbols('x w p',real=True)
        initial=[1+a+2*b+3*a*b,4-2*a+b+5*a*b,7+11*a+13*b+17*a*b]
        reset=[x,w,s.Rational(2,3)*p+19*b]
        expected=[initial[0],initial[1],s.Rational(2,3)*initial[2]+19*b]
        out,_=compare_case([x,w,p],initial,[1,2,3],[4,5,6],t,reset,s.Integer(0),expected)
        self.assertEqual(out['u_plus'][2],Fraction(22,3))
        self.assertEqual(out['w_plus'][2],Fraction(34,3))

    def test_prescribed_parameter_time_and_explicit_time_flows(self):
        x=s.symbols('x',real=True)
        x0=2+3*a-2*b+5*a*b
        speed=1+a+2*b+a*b;acc=s.Rational(3,2)+a-b
        tau=a+2*b+3*a*b
        pre_event=x0+speed*tau+acc*tau**2/2
        reset=x+x**2+t**2+a*t+2*b*t+a*b
        rr=reset.subs({x:pre_event,t:tau})
        post_speed=2+3*a-b+a*b;post_acc=s.Rational(5,3)+2*a
        sync=rr-post_speed*tau-post_acc*tau**2/2
        compare_case([x],[x0],[speed+acc*t],[post_speed+post_acc*t],
                     t-tau,[reset],tau,[sync])

    def test_curved_state_guard_and_parameter_post_dynamics(self):
        x=s.symbols('x',real=True)
        x0=2+a+2*b+3*a*b;level=2+3*a-b+2*a*b
        speed=1+2*a+3*b;rate=s.Rational(2,3)+a-2*b
        tau=(level-x0)/speed
        reset=x**2+t*x+a*b
        rr=reset.subs({x:level,t:tau})
        compare_case([x],[x0],[speed],[rate*x],x**2-level**2,[reset],tau,
                     [rr*s.exp(-rate*tau)])

    def test_state_and_time_dependent_fields(self):
        x=s.symbols('x',real=True)
        x0=2+a-3*b+2*a*b;level=2+2*a+b+4*a*b
        k=s.Rational(2,3);d=1+a+2*b
        tau=s.log((level+d/k)/(x0+d/k))/k
        reset=x+x**2+t*x+a*t+b*x+a*b
        rr=reset.subs({x:level,t:tau})
        alpha=s.Rational(2,5);beta=s.Rational(3,7);gamma=1+2*a-b+a*b
        e=s.exp(-alpha*tau)
        sync=e*rr+beta*((tau/alpha+1/alpha**2)*e-1/alpha**2)+gamma*(e-1)/alpha
        compare_case([x],[x0],[k*x+d],[alpha*x+beta*t+gamma],x-level,[reset],tau,[sync])

    def test_vector_cross_derivatives(self):
        x,y=s.symbols('x y',real=True)
        x0=1+2*a-b+3*a*b;y0=2-a+3*b+2*a*b
        vx=1+a;vy=2-b+a*b;level=2+2*a-b+3*a*b
        tau=(level-y0)/vy;xe=x0+vx*tau
        reset=[x*x+t*y+a*b,y+x*a+b*b]
        rx=reset[0].subs({x:xe,y:level,t:tau});ry=reset[1].subs({x:xe,y:level,t:tau})
        alpha=s.Rational(1,3);beta=s.Rational(2,5)+a-b
        e=s.exp(-alpha*tau)
        sync=[e*rx+beta*ry*(e-1)/alpha,ry]
        compare_case([x,y],[x0,y0],[vx,vy],[alpha*x+beta*y,0],y*y-level*level,reset,tau,sync)

    def test_identity_event_with_identical_fields(self):
        x=s.symbols('x',real=True)
        x0=2+a+3*b+5*a*b;level=2+2*a-b+a*b;speed=1+a-b
        tau=(level-x0)/speed
        out,_=compare_case([x],[x0],[speed],[speed],x-level,[x],tau,[x0])
        self.assertEqual(out['w_plus'],[Fraction(5)])

    def test_nontransverse_refusal(self):
        z=Fraction(0);one=Fraction(1)
        f=FlowJet([z],[z],[[z]],[z],[z])
        g=ScalarJet(z,[z,one,z,z],[[z]*4 for _ in range(4)])
        r=ResetJet([z],[[z,one,z,z]],[[[z]*4 for _ in range(4)]])
        with self.assertRaisesRegex(ValueError,'NONTRANSVERSE'):
            transport_event(f,f,g,r,[z],[z],[z])

    def test_off_guard_refusal(self):
        z=Fraction(0);one=Fraction(1)
        f=FlowJet([z],[z],[[z]],[z],[z])
        g=ScalarJet(one,[one,z,z,z],[[z]*4 for _ in range(4)])
        r=ResetJet([z],[[z,one,z,z]],[[[z]*4 for _ in range(4)]])
        with self.assertRaisesRegex(ValueError,'not on'):
            transport_event(f,f,g,r,[z],[z],[z])


if __name__=='__main__':
    unittest.main(verbosity=2)
