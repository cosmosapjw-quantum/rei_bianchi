"""Static collinear attractive Coulomb sector bounds, not target certificates."""
from fractions import Fraction
import math
import numbers

def coulomb_sector_lower_bound(charges, m_abs):
    """Return exact Fraction -sum(Z)^2/[2(|m|+1)^2].

    Assumes T=-Delta/2, nonnegative charges on the common z axis, spinless
    static scalar Coulomb H; no vector potential/ETF/rotating-frame terms.
    Charge floats are interpreted as their exact binary values.
    """
    if isinstance(m_abs,bool) or not isinstance(m_abs,numbers.Integral) or m_abs<0:
        raise ValueError('nonnegative integer m_abs required')
    qq=[]
    for z in charges:
        if isinstance(z,bool):raise ValueError('boolean charge invalid')
        try:q=Fraction(z)
        except (ValueError,TypeError,OverflowError) as e:raise ValueError('finite rational charge required') from e
        if q<0:raise ValueError('attractive nonnegative charges required')
        qq.append(q)
    total=sum(qq,Fraction(0))
    if not qq or total<=0:raise ValueError('positive total charge required')
    return -total*total/(2*(int(m_abs)+1)**2)

def exterior_screen(charges, min_m_abs, selected_energy_values):
    """Nominal screen only: input energies are NOT presumed rigorous upper bounds."""
    if min_m_abs<1:raise ValueError('exterior screen requires min_m_abs>=1')
    bound=coulomb_sector_lower_bound(charges,min_m_abs)
    vals=[float(x) for x in selected_energy_values]
    if not vals or not all(math.isfinite(x) for x in vals):raise ValueError('finite selected energies required')
    upper=max(vals)
    return {'operator_bound_exact':str(bound),'operator_bound_float':float(bound),
            'covered_sectors':f'all |m| >= {min_m_abs}',
            'selected_reference_max_energy':upper,'nominal_margin':float(bound)-upper,
            'selected_values_are_rigorous_upper_enclosures':False,
            'gap_certificate':False,'continuum_certificate':False,
            'meaning':'Exact static sector theorem; margin is arithmetic on archived approximate eigenvalues, not a target-spectrum enclosure.'}
