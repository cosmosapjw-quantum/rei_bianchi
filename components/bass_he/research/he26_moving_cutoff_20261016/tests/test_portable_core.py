import sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'inputs')]
from portable_cut_core import children_of_cell,angular_cuts
from moving_cuts import he25_basis,birth_frame_reference,G,X_END
from he21_photo import FIT_CUTS,BIND_EV,shape,sigma_cm2

def test_child_true_moments_and_zero_threshold_straddle():
    b=he25_basis(4,4,+.005);x=.37*X_END
    kids=[c for nu,aw,lo,hi,*_ in b.panels for c in children_of_cell(
        lo,hi,x,+.005,nu,aw,13.60,100.,FIT_CUTS,BIND_EV,shape,sigma_cm2)]
    assert len(kids)==72
    N=sum(c['n'] for c in kids)
    reference=birth_frame_reference()
    assert abs(N/reference['raw_n']-1)<1e-13
    assert abs(sum(c['u_ev'] for c in kids)/N-reference['mean_ev'])<1e-11
    for c in kids:
        assert c['n']>0
        assert all(v>=0 for v in c['photo_cm2'])
        assert not any(c['low_ev']<chi-4e-12 and c['high_ev']>chi+4e-12 for chi in FIT_CUTS)

def test_signed_cut_roots():
    for q in (-.005,.005):
        Eref=54.42/G(X_END,.47,q)
        cuts=angular_cuts(X_END,q,Eref,[54.42])
        assert len(cuts)==4
        assert abs(cuts[1]+.47)<1e-9 and abs(cuts[2]-.47)<1e-9
