"""Proved synthetic callbacks. These are not Frozen107/HH primitives."""
from fractions import Fraction as F
from .engine import (Interval as I,Rectangle as R,RangeClaim,DomainFailure,
                     ResourceLimit,integrate_range)


def point(x): return R(I(F(x),F(x)),I(0,0))


def polynomial_range(t,z):
    return RangeClaim(z*R(t*t,I(0,0)),t,z,True,'TOY_T1_exact_rectangle_product_z_t_squared')


def constant_range(t,z):
    return RangeClaim(z,t,z,True,'TOY_T2_parameter_constant_in_real_integration_variable')


def nested_range(t,z,budget):
    """For the outer real panel t, integrate z*t_inner**2 with z ranging over t.

    The exact inner target is z/3 on the entire outer parameter panel. Adding
    its unavoidable parameter-image width to a discretization width target is
    solely a toy split heuristic. It is not an HH endpoint/interior budget.
    """
    inner_box=R(t,I(0,0))
    inner=integrate_range(polynomial_range,I(0,1),inner_box,budget=budget,
                          target_width=t.width/F(3)+F(1,128))
    if inner.status=='CERTIFICATE_INCONCLUSIVE_RESOURCE_LIMIT':
        raise ResourceLimit(inner.reason)
    if inner.enclosure is None:
        raise DomainFailure('inner enclosure absent')
    return RangeClaim(inner.enclosure,t,z,True,'TOY_T3_uniform_inner_image_over_entire_outer_panel')
