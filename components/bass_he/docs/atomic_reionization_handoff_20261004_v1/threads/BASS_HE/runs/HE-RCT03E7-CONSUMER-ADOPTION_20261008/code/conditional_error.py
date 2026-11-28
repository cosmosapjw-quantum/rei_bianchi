"""Exact rational conditional bounds. No premises are inferred from refinement.

A source-bound discrete measure and a physical continuous spectrum are different
objects. Uncertainty radii and uniform cell bounds must be supplied explicitly;
this module checks arithmetic, not the scientific origin of those premises.
"""
from fractions import Fraction as F

class MissingPremise(ValueError):
    """A physical or mathematical error premise has not been supplied."""


def _q(x, *, positive=False):
    if not isinstance(x,F) or x<0 or (positive and x<=0):
        raise ValueError('exact nonnegative Fraction required (positive where specified)')
    return x


def fixed_measure_envelope(weights,density,sigma,n,c,*,density_radius=None,
                           sigma_radius=None,n_radius=None,premise_id=None):
    """Positive-product box on ONE fixed list of spectral nodes and weights.

    sigma_radius must enclose all intended changes of the cross section,
    including energy or branch uncertainty. Point sigma with uncertain energy
    is not automatically a valid premise. No quadrature remainder is included.
    """
    if density_radius is None or sigma_radius is None or n_radius is None or not premise_id:
        raise MissingPremise('density, kernel and background radii plus provenance are required')
    if not weights or len({len(weights),len(density),len(sigma),len(density_radius),len(sigma_radius)})!=1:
        raise ValueError('nonempty equal-sized fixed measure required')
    w=list(map(_q,weights));f=list(map(_q,density));s=list(map(_q,sigma))
    df=list(map(_q,density_radius));ds=list(map(_q,sigma_radius));_q(n,positive=True);_q(c,positive=True);_q(n_radius)
    nominal=c*n*sum((a*b*d for a,b,d in zip(w,f,s)),F())
    low=c*max(F(),n-n_radius)*sum((a*max(F(),b-db)*max(F(),d-dd) for a,b,d,db,dd in zip(w,f,s,df,ds)),F())
    high=c*(n+n_radius)*sum((a*(b+db)*(d+dd) for a,b,d,db,dd in zip(w,f,s,df,ds)),F())
    return {'nominal':nominal,'lower':low,'upper':high,'absolute_error':max(nominal-low,high-nominal),
            'premise_id':str(premise_id),'scope':'fixed positive atomic measure, conditional on supplied boxes',
            'quadrature_remainder_included':False,'physical_premises_verified':False}


def uniform_exposure_bound(cells,*,premise_kind=None,premise_id=None):
    """Conditional bound on int Gamma/H ds, not on absorber events per H.

    Each entry is a UNIFORM cell bound: H >= H_lower > 0,
    Hhat >= Hhat_lower > 0, |Gamma-Gammahat| <= rate_error,
    |H-Hhat| <= H_error, |Gammahat| <= rate_hat_upper.
    Recorded nodes/refinement ratios alone cannot supply these quantities.
    """
    if premise_kind!='uniform_cell' or not premise_id:
        raise MissingPremise('uniform bounds over whole cells, not sampled/refinement evidence, are required')
    if not cells:
        raise MissingPremise('uniform cell records are absent')
    total=F()
    for cell in cells:
        try:
            h=_q(cell['width'],positive=True);bg=_q(cell['rate_error'])
            lo=_q(cell['H_lower'],positive=True);lh=_q(cell['Hhat_lower'],positive=True)
            bh=_q(cell['H_error']);g=_q(cell['rate_hat_upper'])
        except KeyError as exc:
            raise MissingPremise('incomplete uniform cell bounds') from exc
        total+=h*(bg/lo+g*bh/(lo*lh))
    return total
