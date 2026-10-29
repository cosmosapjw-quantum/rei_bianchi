"""Source-qualified *photo-event electron observable* bridge, not a BASS dynamical lift.

No physical K, n_b, n_Href, H, full chemistry or IVP is supplied.  The
six-coordinate BASS row is an isotope-weighted observable projection; the
additional T+ coordinate makes the REI 17-state charge observable exact.
Only the source-specific seven REI PR262 photo events are represented.
"""
from __future__ import annotations
from fractions import Fraction as Q
from decimal import Decimal, localcontext
from pathlib import Path
import hashlib, json

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / 'source/SEVEN_ROWS_TRANSCRIPT.json'
DATA_SHA256 = '785708eaba030d4291cf1b9a06976b1a7f16bcb4e3fd102af95f6169c80af262'
LABELS = ('n','H1_0','H1_1','D_0','D_1','T_0','T_1','He3_0','He3_1','He3_2',
          'He4_0','He4_1','He4_2','Li7_0','Li7_1','Li7_2','Li7_3')
CHARGE = (0,0,1,0,1,0,1,0,1,2,0,1,2,0,1,2,3)
PHOTO_EVENTS = ((1,2,0),(3,4,0),(5,6,0),(7,8,1),(8,9,2),(10,11,1),(11,12,2))

class SourceBindingError(ValueError): pass

def exact(x):
    """An explicitly supplied exact decimal, integer, or Fraction, never float/bool."""
    if isinstance(x,(float,bool)) or x is None:
        raise SourceBindingError('EXACT_INPUT_REQUIRED_NO_FLOAT')
    try: return Q(x)
    except (TypeError,ValueError,ZeroDivisionError): raise SourceBindingError('INVALID_EXACT_RATIONAL')

def parse_rows(path:Path=DATA, expected_sha:str=DATA_SHA256):
    raw=path.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=expected_sha:
        raise SourceBindingError('SOURCE_TRANSCRIPT_SHA_MISMATCH')
    data=json.loads(raw)
    if data.get('schema')!='REI_ELECTRON_BRIDGE_LOCAL_SOURCE_TRANSCRIPT_V1' or len(data.get('rows',[]))!=7:
        raise SourceBindingError('UNEXPECTED_SOURCE_SCHEMA')
    if data['provenance']['pr263_head']!='f52ecdb11b3f7e43fdf1fbc19d9feff38fe56927':
        raise SourceBindingError('PARENT_IDENTITY_MISMATCH')
    return data['rows']

def charge(y):
    if len(y)!=17: raise SourceBindingError('EXPECTED_17_SPECIES')
    return sum((exact(x)*v for x,v in zip(y,CHARGE)),Q(0))

def photo_stoichiometry():
    s=[[0]*7 for _ in LABELS]
    for j,(i,k,_rate) in enumerate(PHOTO_EVENTS):s[i][j]=-1;s[k][j]=1
    return s

def photo_rates(y, gamma):
    """Rate units 1/s; state per Href; resulting events per Href/s."""
    if len(y)!=17 or len(gamma)!=3: raise SourceBindingError('SOURCE_SHAPE')
    y=[exact(t) for t in y]; gamma=[exact(t) for t in gamma]
    if any(t<0 for t in y) or any(t<0 for t in gamma):raise SourceBindingError('NEGATIVE_RATE_OR_POPULATION')
    return [y[i]*gamma[r] for i,k,r in PHOTO_EVENTS]

def isocharged_map(rho,wH,wHe,wLi):
    """6x17 dimensionless map M, conditional rho=nHref/nb>0.

    Weights are source individual binary64 isotope scales exactified BEFORE
    combining, but are NOT supplied as physical BASS values by this module.
    """
    rho,wH,wHe,wLi=map(exact,(rho,wH,wHe,wLi))
    if min(rho,wH,wHe,wLi)<=0:raise SourceBindingError('POSITIVE_NORMALIZATION_REQUIRED')
    M=[[Q(0) for _ in LABELS] for _ in range(6)]
    for j in (2,4):M[0][j]=rho/wH
    for j in (8,11):M[1][j]=rho/wHe
    for j in (9,12):M[2][j]=rho/wHe
    for row,j in ((3,14),(4,15),(5,16)):M[row][j]=rho/wLi
    return M

def map_state(y,rho,w):
    if len(y)!=17 or len(w)!=3:raise SourceBindingError('STATE_OR_WEIGHT_SHAPE')
    M=isocharged_map(rho,*w)
    y=[exact(a) for a in y]
    return [sum((v*yy for v,yy in zip(row,y)),Q(0)) for row in M]

def bass_e_weights(w):
    wH,wHe,wLi=map(exact,w)
    if min(wH,wHe,wLi)<=0:raise SourceBindingError('POSITIVE_NORMALIZATION_REQUIRED')
    return (wH,wHe,2*wHe,wLi,2*wLi,3*wLi)

def projected_charge(y,rho,w):
    return sum((e*z for e,z in zip(bass_e_weights(w),map_state(y,rho,w))),Q(0))

def augmented_charge(y,rho,w):
    """One rank-one T+ complement, electron observable only, not BASS dynamics."""
    return projected_charge(y,rho,w)+exact(rho)*exact(y[6])

def event_charge_residual(rho,w):
    """e_B M S-rho q S: seven source events in original REI owner order."""
    M=isocharged_map(rho,*w); e=bass_e_weights(w); S=photo_stoichiometry()
    return [sum((e[i]*sum((M[i][j]*S[j][k] for j in range(17)),Q(0)) for i in range(6)),Q(0))-
            exact(rho)*sum((CHARGE[j]*S[j][k] for j in range(17)),Q(0)) for k in range(7)]

def admissible_charged_simplex(z,totals):
    """Necessary *coordinate* gate; does not certify chemical or isotope ownership."""
    if len(z)!=6 or len(totals)!=3: raise SourceBindingError('SIMPLEX_SHAPE')
    zz=[exact(a) for a in z];t=[exact(a) for a in totals]
    if any(a<0 for a in zz+t): raise SourceBindingError('NEGATIVE_SIMPLEX_INPUT')
    return zz[0]<=t[0] and zz[1]+zz[2]<=t[1] and sum(zz[3:])<=t[2]

def source_defect(y,gamma,rho):
    """Exact REI-minus-BASS photo electron source per nb, no time integration."""
    rt=photo_rates(y,gamma)
    rtot=sum(rt,Q(0))
    return {'total_per_Href_s':rtot,'missing_T_event_per_Href_s':rt[2],
            'electron_rate_per_nb_s':exact(rho)*rtot,
            'projected_rate_per_nb_s':exact(rho)*(rtot-rt[2]),
            'remainder_rate_per_nb_s':exact(rho)*rt[2],
            'epsilon':rt[2]/rtot if rtot else None}

def upper_fraction_from_row(row):
    """Gamma_HI common to H1,D,T; helium photo rates nonnegative."""
    h,d,t=(exact(str(row[k])) for k in ('H1_0','D_0','T_0'))
    if min(h,d,t)<0 or h+d+t<=0:raise SourceBindingError('INVALID_POSITIVE_ROW')
    return t/(h+d+t)

def twojet_rel_defect_bound(epsilon):
    e=exact(epsilon)
    if not 0<=e<=1:raise SourceBindingError('EPSILON_OUT_OF_RANGE')
    return 2*e-e*e

def endpoint_jet_report():
    rows=parse_rows();out=[]
    with localcontext() as ctx:
        ctx.prec=85
        for r in rows:
            z=Decimal(str(r['z_mean']));g=Decimal(str(r['g_beta']))
            D=-(1+z)*g*g
            supplied=Decimal(str(r['det_norm']))
            u=upper_fraction_from_row(r)
            relative=twojet_rel_defect_bound(u)
            assert abs(D-supplied)<Decimal('2e-44')
            assert 0<Decimal(str(r['lo_absdet_joint2_95']))<=abs(supplied)<=Decimal(str(r['hi_absdet_joint2_95']))
            out.append({'z':str(z),'epsilon_upper_exact_fraction':str(u),
                        'epsilon_upper_decimal_85':str(Decimal(u.numerator)/Decimal(u.denominator)),
                        'relative_twojet_defect_upper':str(Decimal(relative.numerator)/Decimal(relative.denominator)),
                        'normalized_det_from_source':str(D),
                        'joint2_95_is_pointwise':True,'physical_tau':False})
    return {'schema':'REI_PHOTO_ELECTRON_BRIDGE_SOURCE_ONLY_V1','rows':out,'ivp_count':0,
            'original_dag':{'working':'33/88','central_last':'28/88','physical_delta':0},
            'notes':'each upper holds at its own frozen source epoch under common H/D/T Gamma_HI and nonnegative helium rates; not time-global error'}

def physical_tau(*args,**kw):
    raise SourceBindingError('PHYSICAL_TAU_BLOCKED_FULL_CHEM_K_NHREF_NB_H_AND_DIRECTIONAL_Z_NOT_BOUND')

if __name__=='__main__':
    print(json.dumps(endpoint_jet_report(),ensure_ascii=False,indent=2))
