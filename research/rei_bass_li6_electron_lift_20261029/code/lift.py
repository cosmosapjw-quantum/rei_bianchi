"""BASS full21 Li6/Li7 invariant-lift proof and counterfactual electron response.

Read-only original-source structure; artificial rates used only as exact algebraic witnesses.
No native BASS rate coefficients, source-consistent REI trajectory, IVP or physical tau.
"""
from __future__ import annotations
from pathlib import Path
from fractions import Fraction as Q
from decimal import Decimal, localcontext
import hashlib, json, math

ROOT=Path(__file__).resolve().parents[1]
SOURCE_LOCK={
 'BASS_ATOMIC_MODEL.json':'9cc399e9e33ece544109f442f50b00c463cde96e406965e796240eaabd49c614',
 'BASS_ATOMIC_NETWORK.py':'baecce07aded483fa60006cc576feff67d068c0d70394f7095abacc6d47eaa80',
 'REI_SAVED7.json':'7653f7f75fcbe92465de1b22faabf565efee36e90d1d967499f68ff123a6bc77'
}
GROUPS={'n':(0,), 'H1':(1,2), 'D':(3,4), 'T':(5,6), 'He3':(7,8,9),
        'He4':(10,11,12),'Li6':(13,14,15,16),'Li7':(17,18,19,20)}
RETAIN=tuple(range(13))+tuple(range(17,21))
Q21=(0,0,1,0,1,0,1,0,1,2,0,1,2,0,1,2,3,0,1,2,3)
Q17=tuple(Q21[i] for i in RETAIN)
MASS={'n':1,'H1':1,'D':2,'T':3,'He3':3,'He4':4,'Li6':6,'Li7':7}
NUCLEI={name:(0 if name=='n' else {'H1':1,'D':1,'T':1,'He3':2,'He4':2,'Li6':3,'Li7':3}[name]) for name in GROUPS}


def source_bytes(name):
    if name not in SOURCE_LOCK:raise ValueError('UNKNOWN_SOURCE_ID')
    raw=(ROOT/'source'/name).read_bytes()
    got=hashlib.sha256(raw).hexdigest()
    if got!=SOURCE_LOCK[name]:raise ValueError('SOURCE_SHA256_MISMATCH:'+name)
    return raw

def load_inputs():
    data=json.loads(source_bytes('BASS_ATOMIC_MODEL.json'))
    code=source_bytes('BASS_ATOMIC_NETWORK.py').decode()
    for phrase in ('self.Z[index], self.q[index]',
                   "'Li6': (13, 14, 15, 16), 'Li7': (17, 18, 19, 20)",
                   "(0, 2, self.neutron_lambda_s)",
                   "(5, 8, self.tritium_lambda_s)",
                   "(6, 9, self.tritium_lambda_s)",
                   "density * np.outer(",
                   "recombination_action, self.q)"):
        if phrase not in code:raise ValueError('SOURCE_CODE_SEMANTICS_CHANGED:'+phrase)
    saved=json.loads(source_bytes('REI_SAVED7.json'),parse_float=Decimal)
    if len(saved['rows'])!=7 or len(saved['labels'])!=17:raise ValueError('REI_SAVED7_INVALID')
    return data,saved

def exact(x):
    if isinstance(x,bool):raise TypeError('NO_BOOL')
    if isinstance(x,Q):return x
    if isinstance(x,int):return Q(x)
    if isinstance(x,Decimal):return Q(x)
    if isinstance(x,str):return Q(x)
    raise TypeError('EXACT_RATIONAL_INPUT_REQUIRED')

def owner_scales(config):
    """Source owner uses *binary64* math.fsum and per-isotope division."""
    ratios={k:float(v) for k,v in config['inventory_number_ratios_to_H1'].items()}
    norm=math.fsum(MASS[k]*ratios[k] for k in MASS)
    numbers={k:Q.from_float(ratios[k]/norm) for k in MASS}
    if numbers['Li6']<=0 or numbers['Li7']<=0:raise ValueError('REQUIRES_POSITIVE_LI_INVENTORY')
    return norm,numbers,numbers['Li6']/numbers['Li7']

def lift17(y,gamma):
    """17 retained abundances -> 21 BASS abundances via Li6=gamma*Li7."""
    v=[exact(x) for x in y]
    if len(v)!=17:raise ValueError('EXPECTED17')
    g=exact(gamma)
    if g<=0:raise ValueError('POSITIVE_GAMMA_REQUIRED')
    out=[Q(0)]*21
    for j,i in enumerate(RETAIN):out[i]=v[j]
    for k in range(4):out[13+k]=g*v[13+k]
    return out

def select21(v):return [v[i] for i in RETAIN]

def effective_charge17(gamma):
    g=exact(gamma)
    return [Q(v)+(g*Q(v) if i>=13 else Q(0)) for i,v in enumerate(Q17)]

def dot(a,b):return sum((x*y for x,y in zip(a,b)),Q(0))

def operator_blocks(photo,recomb,neutron=Q(0),tritium=Q(0),li6_photo_override=None):
    """Exact source-pattern G0+D, Gne using *supplied synthetic rational* rate arrays.

    Photo rates in s^-1; recombination entries in m^3/s. Never call them native coefficients.
    """
    n=21;G=[[Q(0) for _ in range(n)] for _ in range(n)];R=[[Q(0) for _ in range(n)] for _ in range(n)]
    for name,ii in GROUPS.items():
        z=NUCLEI[name]
        for q in range(z):
            i,j=ii[q],ii[q+1]
            val=exact(photo[(z,q)])
            if name=='Li6' and li6_photo_override is not None and q==0:val=exact(li6_photo_override)
            G[i][i]-=val;G[j][i]+=val
        for q in range(1,z+1):
            i,j=ii[q],ii[q-1]
            val=exact(recomb[(z,q)])
            R[i][i]-=val;R[j][i]+=val
    for i,j,rate in [(0,2,neutron),(5,8,tritium),(6,9,tritium)]:
        rate=exact(rate);G[i][i]-=rate;G[j][i]+=rate
    return G,R

def matvec(a,v):return [dot(row,v) for row in a]

def full_rhs(a,r,y,nb):
    yy=[exact(v) for v in y];nb=exact(nb);electron=nb*dot(Q21,yy)
    ay=matvec(a,yy);ry=matvec(r,yy)
    return [u+electron*v for u,v in zip(ay,ry)]

def full_jacobian(a,r,y,nb):
    yy=[exact(v) for v in y];nb=exact(nb);qdot=dot(Q21,yy);ry=matvec(r,yy)
    return [[a[i][j]+nb*qdot*r[i][j]+nb*ry[i]*Q21[j] for j in range(21)] for i in range(21)]

def reduced_rhs(a,r,y,nb,gamma):return select21(full_rhs(a,r,lift17(y,gamma),nb))

def reduced_jacobian(a,r,y,nb,gamma):
    j=full_jacobian(a,r,lift17(y,gamma),nb)
    return [[j[i][RETAIN[k]]+(exact(gamma)*j[i][13+(k-13)] if k>=13 else Q(0))
             for k in range(17)] for i in RETAIN]

def source_intertwining(a,r,y,nb,gamma):
    """Compute two exact residuals (F21(E y)-E f17, J21(Ey)E-E J17)."""
    yy=lift17(y,gamma);f=full_rhs(a,r,yy,nb);fr=select21(f)
    residual=[v-w for v,w in zip(f,lift17(fr,gamma))]
    j=full_jacobian(a,r,yy,nb);jr=reduced_jacobian(a,r,y,nb,gamma)
    max_res=Q(0)
    for i in range(21):
        for k in range(17):
            lhs=j[i][RETAIN[k]]+(exact(gamma)*j[i][13+k-13] if k>=13 else Q(0))
            rhs=jr[RETAIN.index(i)][k] if i in RETAIN else exact(gamma)*jr[13+i-13][k]
            max_res=max(max_res,abs(lhs-rhs))
    return max(abs(v) for v in residual),max_res

def delta_chemistry(a,r,y,nb,gamma):
    """Exactly isolate omitted-Li6 electron feedback on 17 retained states."""
    yy=[exact(x) for x in y];nb=exact(nb);g=exact(gamma)
    R17=[[r[i][j] for j in RETAIN] for i in RETAIN]
    ry=matvec(R17,yy)
    d=[Q(0)]*17
    for k in range(4):d[13+k]=g*k
    eta=dot(d,yy)
    dF=[nb*eta*v for v in ry]
    dJ=[[nb*(eta*R17[i][j]+ry[i]*d[j]) for j in range(17)] for i in range(17)]
    return eta,dF,dJ

def pure_li6_photo_counterexample(a,r,y,nb,gamma,extra):
    """Source mismatch in only one Li6 photo rate -> exact loss of lift invariance."""
    yy=lift17(y,gamma);f=full_rhs(a,r,yy,nb)
    photo_diff=exact(extra)*yy[13]
    return photo_diff # component 13 decreases and component 14 increases

def rho_pullback(y,yp,rho,rhop):
    """From Y=rho*y: y' = Y'/rho-rho'/rho*y, no IVP."""
    rho=exact(rho);rhop=exact(rhop)
    if rho<=0:raise ValueError('RHO_POSITIVE_REQUIRED')
    return [exact(v)/rho-rhop*exact(w)/(rho*rho) for w,v in zip(y,yp)]

def diagnostics():
    data,saved=load_inputs();norm,n,ratio=owner_scales(data)
    qinitial=Q(0)
    for group,indices in GROUPS.items():
        if group in ('H1','D'):
            f=Q.from_float(float(data['initial_H1_D_ionized_fraction']))
            qinitial+=n[group]*f
        elif group.startswith('Li'):qinitial+=n[group] # initially Li singly
    eta0=n['Li6']
    out=[]
    for row in saved['rows']:
        y=[Q(v) for v in row['y']]
        li7=sum(y[13:17],Q(0));charge_li7=dot([0,1,2,3],y[13:17]);missing=ratio*charge_li7
        out.append(dict(z_mean=str(row['z']),REI_li7_total_per_Href=str(Decimal(li7.numerator)/Decimal(li7.denominator)),
                        counterfactual_missing_Li6_charge_per_Href=str(Decimal(missing.numerator)/Decimal(missing.denominator)),
                        note='NOT physical conversion: assumes BASS ratio on REI frozen state without source matching'))
    with localcontext() as context:
        context.prec=55
        dec=lambda f:str(Decimal(f.numerator)/Decimal(f.denominator))
        return dict(schema='REI_BASS_LI6_LIFT_RESULT_V1',source='PINNED_BASS_PR234_SOURCE_PLUS_REI_PR262_SEVEN_ROWS',
                    source_hashes=SOURCE_LOCK,owner_mass_normalization_binary64=repr(norm),
                    owner_gamma_ideal_decimal='0.00002',owner_gamma_represented_real=str(ratio),
                    owner_gamma_represented_decimal=dec(ratio),owner_nu6_per_baryon=dec(n['Li6']),
                    owner_nu7_per_baryon=dec(n['Li7']),
                    owner_initial_electrons_per_baryon=dec(qinitial),
                    initial_Li6_fraction_of_total_electrons=dec(eta0/qinitial),
                    strict_Li6_electron_upper_per_baryon=dec(3*n['Li6']),
                    initial_missing_Li6_electrons_per_baryon=dec(eta0),
                    source_only_REI_seven_counterfactual=out,actual_rei_source_rates_equal=False,
                    full_BASS_native_network_evaluated=False,full_REI_chemistry_evaluated=False,
                    new_IVPs=0,original_DAG={'working':'33/88','central':'28/88','delta':0},F4='PARTIAL',L4_ready=False)

if __name__=='__main__':
    print(json.dumps(diagnostics(),indent=2))
