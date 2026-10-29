"""Source-locked REI/BASS inventory compatibility and exact photo-only lumpability.

No IVP, native rate calibration, actual nHref/n_b, K or physical tau is calculated.
REI stored seven frozen snapshots and the BASS PR234 reconstructed owner sources
are DIFFERENT pilot model families. An obstruction is not a numerical solver bug.
"""
from __future__ import annotations
import hashlib, json, math
from fractions import Fraction as Q
from decimal import Decimal, localcontext
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REI=ROOT/'source/REI_SAVED7.json'
BASS=ROOT/'source/BASS_ATOMIC_MODEL.json'
COMPACT=ROOT/'source/BASS_COMPACT_SYSTEM.py'
COUPLED=ROOT/'source/BASS_COUPLED.py'
NETWORK=ROOT/'source/BASS_ATOMIC_NETWORK.py'
SOURCE_HASH={
 'REI_SAVED7.json':'7653f7f75fcbe92465de1b22faabf565efee36e90d1d967499f68ff123a6bc77',
 'BASS_ATOMIC_MODEL.json':'9cc399e9e33ece544109f442f50b00c463cde96e406965e796240eaabd49c614',
 'BASS_COMPACT_SYSTEM.py':'3ebf56b5a8f1f392681365ec0769364329f293f944a0de4a5add441c8cbc1c49',
 'BASS_COUPLED.py':'09a3325c584b895f8c1de44d3b64a458ec7e27f8eec843c7e15aa246a6088d47',
 'BASS_ATOMIC_NETWORK.py':'baecce07aded483fa60006cc576feff67d068c0d70394f7095abacc6d47eaa80',
}
LABELS=('n','H1_0','H1_1','D_0','D_1','T_0','T_1','He3_0','He3_1','He3_2','He4_0','He4_1','He4_2','Li7_0','Li7_1','Li7_2','Li7_3')
CHARGE=(0,0,1,0,1,0,1,0,1,2,0,1,2,0,1,2,3)
BARYON=(1,1,1,2,2,3,3,3,3,3,4,4,4,7,7,7,7)
RATE_EVENTS=((1,2,0),(3,4,0),(5,6,0),(7,8,1),(8,9,2),(10,11,1),(11,12,2))
BASS_MASSES={'n':1,'H1':1,'D':2,'T':3,'He3':3,'He4':4,'Li6':6,'Li7':7}

def verified_bytes(path, expected):
    raw=path.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=expected:raise ValueError('SOURCE_SHA_MISMATCH:'+path.name)
    return raw

def exact(x):
    if isinstance(x,bool) or isinstance(x,float):raise TypeError('EXACT_RATIONAL_REQUIRED')
    if isinstance(x,Decimal):return Q(x)
    return Q(x)

def load_rei():
    obj=json.loads(verified_bytes(REI,SOURCE_HASH[REI.name]),parse_float=Decimal)
    if obj['original_git_blob']!='189c2d903e25c18bee49e0ab6add3ba1d1805e93':
        raise ValueError('REI_ORIGINAL_CSV_GIT_BLOB_CHANGED')
    if tuple(obj['labels'])!=LABELS or len(obj['rows'])!=7:raise ValueError('REI_SCHEMA_CHANGED')
    return obj['rows']

def load_bass():
    obj=json.loads(verified_bytes(BASS,SOURCE_HASH['BASS_ATOMIC_MODEL.json']))
    compact=verified_bytes(COMPACT,SOURCE_HASH[COMPACT.name]).decode()
    coupled=verified_bytes(COUPLED,SOURCE_HASH[COUPLED.name]).decode()
    atomic=verified_bytes(NETWORK,SOURCE_HASH[NETWORK.name]).decode()
    # Only assert the extracted authority snippets that define this analysis.
    for source,phrase in ((compact,'nonzero initial neutron/tritium inventory'),
                          (compact,'ATOMIC = np.array([1,2,10,11,12,17,18,19,20])'),
                          (coupled,'THOMSON = GAMMA_PER_NE/1e6'),
                          (coupled,"out[61]=THOMSON*ne/field['H']"),
                          (atomic,"'T': (5, 6)")):
        if phrase not in source:raise ValueError('PINNED_BASS_AUTHORITY_MISSING:'+phrase)
    ratios=obj['inventory_number_ratios_to_H1']
    # Replicate BASS owner's binary64 normalization, *then* exactify each weight.
    norm=math.fsum(BASS_MASSES[name]*ratios[name] for name in BASS_MASSES)
    weights={name:Q.from_float(ratios[name]/norm) for name in BASS_MASSES}
    if obj['species_order'][5:7]!=['TI','TII']:raise ValueError('BASS_T_ORDER_CHANGED')
    return obj,weights,norm

def isotope_totals(y):
    v=[exact(a) for a in y]
    if len(v)!=17:raise ValueError('REI_STATE_DIMENSION')
    return {'H1':v[1]+v[2],'D':v[3]+v[4],'T':v[5]+v[6],
            'He3':v[7]+v[8]+v[9],'He4':v[10]+v[11]+v[12],
            'Li7':sum(v[13:17]),'n':v[0]}

def sharp_two_isotope_minimax(A,B):
    """min_{rho>0} max(|rho A-1|,|rho B-1|), A,B>0. Exact Fractions."""
    A,B=exact(A),exact(B)
    if min(A,B)<=0:raise ValueError('NONPOSITIVE_RATIO')
    return 2/(A+B),abs(A-B)/(A+B)

def field_minimax(y,weights):
    iso=isotope_totals(y)
    A=iso['H1']/weights['H1']; B=iso['He4']/weights['He4']
    rho,delta=sharp_two_isotope_minimax(A,B)
    residual_H=rho*A-1; residual_He=rho*B-1
    if residual_H!=-residual_He or abs(residual_H)!=delta:
        raise ArithmeticError('MINIMAX_EQUILIBRATION_FAILURE')
    return {'rho_opt':rho,'irreducible_relative':delta,'r_H':residual_H,
            'r_He4':residual_He,'He4_over_H1':iso['He4']/iso['H1'],
            'T_over_H1':iso['T']/iso['H1'],'T_inventory':iso['T']}

def photo_full_rhs(y,gammas):
    """Exact seven-source instantaneous 17-vector F(y, gamma) per Href/s."""
    y=[exact(t) for t in y]; gammas=[exact(t) for t in gammas]
    if len(y)!=17 or len(gammas)!=3 or min(y+gammas)<0:raise ValueError('UNPHYSICAL_SOURCE')
    f=[Q(0)]*17
    for start,stop,r in RATE_EVENTS:
        lam=y[start]*gammas[r]
        f[start]-=lam;f[stop]+=lam
    return f

def reduced_raw(y):
    v=[exact(a) for a in y]
    iso=isotope_totals(v)
    return {'Hplus':v[2]+v[4],'Heplus':v[8]+v[11],
            'He2plus':v[9]+v[12],'Tplus':v[6],
            'NH':iso['H1']+iso['D'],'NHe':iso['He3']+iso['He4'],'NT':iso['T']}

def photo_lumped_rhs(y,gammas):
    """Closed FOUR charges given the TWO aggregated totals and T total.

    Only under common HI rate among H1/D/T and common He rates. No full BASS RHS.
    """
    r=reduced_raw(y);a,b,c=map(exact,gammas)
    return {'Hplus':a*(r['NH']-r['Hplus']),
            'Heplus':b*(r['NHe']-r['Heplus']-r['He2plus'])-c*r['Heplus'],
            'He2plus':c*r['Heplus'],
            'Tplus':a*(r['NT']-r['Tplus'])}

def photo_direct_reduced_rhs(y,gammas):
    f=photo_full_rhs(y,gammas)
    return {'Hplus':f[2]+f[4],'Heplus':f[8]+f[11],
            'He2plus':f[9]+f[12],'Tplus':f[6]}

def photo_lumped_jacobian(gammas):
    """4x4 source-only Jacobian on (H+,He+,He2+,T+) at fixed isotope totals.

    This is not the BASS native 21x21 Jacobian, and not REI full chemistry.
    """
    a,b,c=map(exact,gammas)
    if min(a,b,c)<0:raise ValueError('NEGATIVE_PHOTO_RATE')
    return ((-a,Q(0),Q(0),Q(0)),
            (Q(0),-(b+c),-b,Q(0)),
            (Q(0),c,Q(0),Q(0)),
            (Q(0),Q(0),Q(0),-a))

def normalized_lumped_rhs(y,gammas,rho,rho_prime,H,weights):
    """x=ln a, proper-time photo rates, rho time derivative; no BASS fit claim."""
    rho=exact(rho);rp=exact(rho_prime);H=exact(H)
    if min(rho,H)<=0:raise ValueError('POSITIVE_CLOCK_DENSITY_REQUIRED')
    r=reduced_raw(y);f=photo_lumped_rhs(y,gammas)
    w={name:exact(weights[name]) for name in ('H1','D','He3','He4','Li6','Li7')}
    wh=w['H1']+w['D']; whe=w['He3']+w['He4']; wli=w['Li6']+w['Li7']
    charge=(r['Hplus'],r['Heplus'],r['He2plus'],
            exact(y[14]),exact(y[15]),exact(y[16]))
    src=(f['Hplus'],f['Heplus'],f['He2plus'],Q(0),Q(0),Q(0))
    wt=(wh,whe,whe,wli,wli,wli)
    z=[rho*charge[i]/wt[i] for i in range(6)]
    dz=[(rp/rho)*z[i]+rho/H*src[i]/wt[i] for i in range(6)]
    t=rho*r['Tplus']
    dt=(rp/rho)*t+rho/H*f['Tplus']
    return {'z':z,'zprime':dz,'T_complement':t,'Tprime':dt,
            'charge_equality':wh*z[0]+whe*(z[1]+2*z[2])+wli*(z[3]+2*z[4]+3*z[5])+t,
            'raw_charge_rho':rho*sum(exact(y[i])*CHARGE[i] for i in range(17))}

def source_compatibility():
    rows=load_rei();model,weights,norm=load_bass()
    result=[]
    with localcontext() as ctx:
        ctx.prec=65
        def dec(fr):return str(Decimal(fr.numerator)/Decimal(fr.denominator))
        for row in rows:
            calc=field_minimax(row['y'],weights)
            iso=isotope_totals(row['y'])
            # A zero BASS-T pilot cannot represent nonzero REI-T inventory by rho>0.
            if weights['T']!=0 or iso['T']<=0:raise AssertionError('EXPECTED_T_BRANCH_MISMATCH')
            result.append({'z_mean':str(row['z']),
              'rho_opt_minimax_H1_He4_not_physical':dec(calc['rho_opt']),
              'sharp_best_relative_error_H1_He4':dec(calc['irreducible_relative']),
              'He4_H1_REI':dec(calc['He4_over_H1']),
              'He4_H1_BASS':str(model['inventory_number_ratios_to_H1']['He4']),
              'T_H1_REI':dec(calc['T_over_H1']),
              'T_H1_BASS':str(model['inventory_number_ratios_to_H1']['T']),
              'photo_lump_direct_matches':photo_lumped_rhs(row['y'],['1/1000','2/1000','3/1000'])==photo_direct_reduced_rhs(row['y'],['1/1000','2/1000','3/1000']),
              'full_dynamics_lump_admitted':False})
    return {'schema':'REI_BASS_INVENTORY_PREFLIGHT_V1','input_rows':len(result),
            'fixed_BASS_normalization_float64':repr(norm),
            'BASS_T_inventory':model['inventory_number_ratios_to_H1']['T'],
            'BASS_weights_represented_real':{k:str(weights[k]) for k in weights},
            'seven_rows':result,'working_dag':'33/88','central_dag':'28/88',
            'physical_delta':0,'NO_MORE_IVPs':True,'full_chemistry_Jy':None,
            'actual_K_H_nb_nHref':None,'directional_z':None,
            'science_claim':'positive-rho isotope-source incompatibility for specified frozen pilot states only',
            'conditional_photo_only_closure':'exact for common H and He rates and fixed isotope-total ports; different from BASS native rates'}

if __name__=='__main__':
    print(json.dumps(source_compatibility(),indent=2))
