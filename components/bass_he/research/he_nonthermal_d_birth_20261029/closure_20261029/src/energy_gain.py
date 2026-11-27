"""Conditional inclusive energy gain per exclusive He4(gamma,DD) event.

Fractions retain exact bin moments and trace remainders; see THEORY.md.
No event rate, physical pool, angular tensor or stopping operator is supplied.
"""
from fractions import Fraction as F
from nonthermal_d_birth import exact
from conditional_pressure_trace import E0_MEV, B2_MEV2, D_REST_MEV, moment_trace_bounds

FULL_WITNESS = ('1411/10000', '-1/4', '33/25')


class SexticLaw:
    """q(mu)=(1-mu²)(a0+a1*mu²+a2*mu⁴)/Z per dmu on [-1,1]."""
    def __init__(self, coefficients):
        a = tuple(exact(v) for v in coefficients)
        if len(a) != 3: raise ValueError('three exact coefficients required')
        a0, a1, a2 = a
        values = [a0, a0+a1+a2]
        if a2 > 0:
            vertex = -a1/(2*a2)
            if 0 < vertex < 1: values.append(a0+a1*vertex+a2*vertex**2)
        z = 4*a0/F(3)+4*a1/F(15)+4*a2/F(35)
        if min(values) < 0 or z <= 0:
            raise ValueError('nonnegative nonzero sextic density required')
        self.coefficients = a
        self.power_coefficients = (a0, a1-a0, a2-a1, -a2)
        self.normalization = z

    def density(self, mu):
        """Selected CM marginal q, not a measured angular provider."""
        u = exact(mu)
        if not -1 <= u <= 1: raise ValueError('mu outside [-1,1]')
        a0, a1, a2 = self.coefficients
        return (1-u*u)*(a0+a1*u*u+a2*u**4)/self.normalization

    def even_moment(self, k):
        """Return E[mu^(2k)], exact, for integer0<=k<=33."""
        if not isinstance(k, int) or isinstance(k, bool) or not 0 <= k <= 33:
            raise ValueError('moment order must be an integer in [0,33]')
        return 2*sum(c/F(2*j+2*k+1) for j,c in enumerate(self.power_coefficients))/self.normalization

    def bins(self, reduced_edges):
        """Exact per-event number, x, x² on a full reduced partition.

        x=(K-K0)/B. Bin kinetic=K0*number+B*first_x [MeV/event].
        Retain integrated first_x; midpoint assignment need not conserve energy.
        """
        edges = tuple(exact(v) for v in reduced_edges)
        if (len(edges)<2 or edges[0]!=-1 or edges[-1]!=1
                or any(l>=h for l,h in zip(edges,edges[1:]))):
            raise ValueError('strict partition covering [-1,1] required')
        out=[]
        for lo,hi in zip(edges,edges[1:]):
            moments=[2*sum(c*(hi**(2*j+k+1)-lo**(2*j+k+1))/F(2*j+k+1)
                for j,c in enumerate(self.power_coefficients))/self.normalization for k in range(3)]
            out.append(dict(lo_x=lo,hi_x=hi,number=moments[0],first_x=moments[1],second_x=moments[2]))
        return out

    def trace_enclosure(self, order):
        """Exact MeV/event trace enclosure for frozen above-threshold330MeV.

        Raw rational remainder bounds are preserved; final endpoints intersect
        the universal m2 Jensen/secant interval. No physical rate is supplied.
        """
        if not isinstance(order,int) or isinstance(order,bool) or not 0<=order<=32:
            raise ValueError('series order must be an integer in [0,32]')
        r=B2_MEV2/E0_MEV**2
        d=2*D_REST_MEV**2/E0_MEV
        series=sum(r**k*self.even_moment(k) for k in range(order+1))
        rem_lo=r**(order+1)*self.even_moment(order+1)
        raw_lo=2*E0_MEV-d*(series+rem_lo/(1-r))
        raw_hi=2*E0_MEV-d*(series+rem_lo)
        universal=moment_trace_bounds(self.even_moment(1))
        lo=max(raw_lo,universal['lower_MeV_per_event'])
        hi=min(raw_hi,universal['upper_MeV_per_event'])
        if lo>hi: raise ArithmeticError('incompatible exact trace enclosures')
        return dict(order=order,r=r,raw_lower_MeV_per_event=raw_lo,
            raw_upper_MeV_per_event=raw_hi,
            raw_width_MeV_per_event=d*r**(order+2)*self.even_moment(order+1)/(1-r),
            lower_MeV_per_event=lo,upper_MeV_per_event=hi,width_MeV_per_event=hi-lo,
            universal=universal,physical_event_rate=None,physical_activation=False,
            production='HOLD',units='MeV per exclusive event')
