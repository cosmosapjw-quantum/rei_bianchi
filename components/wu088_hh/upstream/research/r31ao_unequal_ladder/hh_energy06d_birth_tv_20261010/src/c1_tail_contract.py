"""Conditional uniform Kummer 1F1 absolute-tail inequality for the FD2 candidate.

This proof is purely algebraic, fixed a=r-k/2, b=r+3/2, selected odd k.
It never claims holomorphy of composed HH field or integrator convergence.
"""
from fractions import Fraction as F
class NotAdmitted(ValueError):
    pass

def uniform_selected_kummer_tail(k:int,r:int,terms:int=256,abs_z_bound:int=64)->dict:
    if type(k) is not int or k not in (1,3,5,7) or type(r) is not int or r not in (0,1,2):
        raise NotAdmitted('FD2_SELECTED_K_R_ONLY')
    if type(terms) is not int or terms < 256:
        raise NotAdmitted('FD2_N_GE_256_REQUIRED')
    if type(abs_z_bound) is not int or not 0 <= abs_z_bound <= 64:
        raise NotAdmitted('FD2_WHOLE_BOX_ABS_Z_LE_64_REQUIRED')
    a=F(2*r-k,2)
    b=F(2*r+3,2)
    # For every n>=terms>=256, 0<n+a<n+b, b>0, so
    # |T_{n+1}|/|T_n| = [(n+a)/(n+b)] |z|/(n+1) < L/(n+1) <= L/(N+1).
    if not (terms+a>0 and b>a and b>0):
        raise NotAdmitted('FD2_RATIO_MONOTONICITY_UNPROVEN')
    q=F(abs_z_bound,terms+1)
    if q>=1:
        raise NotAdmitted('FD2_NO_GEOMETRIC_TAIL')
    oldq=F(6656,26471)
    oldfactor=F(26471,19815)
    assert oldfactor == 1/(1-oldq) and q <= oldq
    return {'conditional_series_tail_verified':True,'n_start':terms,'k':k,'r':r,
            'a':a,'b':b,'ratio_q':q,'factor':1/(1-q),
            'old_candidate_ratio':oldq,'old_candidate_factor':oldfactor,
            'full_box_admitted':False,'whole_physical_field_admitted':False,
            'proof_scope':'fixed half-integer hypergeometric (a,b), n>=N, |z|<=64; composition holomorphy and complete HH integrand not certified'}
