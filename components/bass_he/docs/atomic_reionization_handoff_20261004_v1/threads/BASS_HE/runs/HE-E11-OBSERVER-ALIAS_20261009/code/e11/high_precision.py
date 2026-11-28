"""Independent Decimal-from-binary64 photo source assembly, no fitting."""
from __future__ import annotations
from decimal import Decimal,localcontext
from fractions import Fraction as F


def fraction_to_decimal(q:F, precision:int=110) -> Decimal:
    with localcontext() as c:
        c.prec=precision
        return Decimal(q.numerator)/Decimal(q.denominator)


def decimal_photo(endpoint_state:dict,gamma_values:list[str]|tuple[str,...], precision:int=110) -> Decimal:
    with localcontext() as c:
        c.prec=precision
        D=lambda x:Decimal.from_float(float(x))
        n=D(endpoint_state['nH']);h=D(endpoint_state['nHe'])
        x,y,z=(D(endpoint_state[k]) for k in ('x','y','z'))
        g0,g1,g2=(D(g) for g in gamma_values)
        return (D(1)-x)*g0+(h/n)*((D(1)-y-z)*g1+y*g2)
