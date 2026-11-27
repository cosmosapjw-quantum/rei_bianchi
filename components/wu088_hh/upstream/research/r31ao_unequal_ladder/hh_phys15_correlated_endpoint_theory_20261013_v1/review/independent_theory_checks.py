#!/usr/bin/env python3
"""PHYS15 independent exact checks; no candidate import and no history solve."""
from fractions import Fraction as Q
from pathlib import Path
import datetime
import hashlib
import json
import resource
import struct
import time

HERE = Path(__file__).resolve().parent
BASE = HERE.parent / 'HH_PHYS14_20261012_v1'
checks = []
started = time.perf_counter()

def record(name, condition, scope):
    assert condition, name
    checks.append({'name': name, 'result': 'pass_scoped', 'scope': scope})

def bits(x):
    return Q(struct.unpack('>d', bytes.fromhex(x))[0])

def load(p):
    return json.loads(p.read_text())

def vecadd(*xs):
    return [sum(v, Q(0)) for v in zip(*xs)]

def scale(a, v):
    return [a*x for x in v]

def matmul(a, b):
    return [[sum((a[i][k]*b[k][j] for k in range(len(b))), Q(0))
             for j in range(len(b[0]))] for i in range(len(a))]

def matvec(a, v):
    return [sum((x*y for x,y in zip(row,v)), Q(0)) for row in a]

def matrixadd(*xs):
    return [vecadd(*rows) for rows in zip(*xs)]

def matrixscale(c, a):
    return [scale(c, row) for row in a]

def diag(d):
    return [[x if i==j else Q(0) for j in range(len(d))] for i,x in enumerate(d)]

def remap(E, rho):
    n=len(E); a=[[Q(0) for j in range(n+2)] for i in range(n+2)]
    a[n][n]=1; a[n+1][n+1]=rho
    for j,e in enumerate(E):
        v=rho*e
        if v<E[0]:
            a[n][j]=1; a[n+1][j]=v
        else:
            k=next(k for k in range(n-1) if E[k]<=v<=E[k+1])
            weight=(v-E[k])/(E[k+1]-E[k])
            a[k][j]=1-weight; a[k+1][j]=weight
    return a

def dot(a,b):
    return sum((x*y for x,y in zip(a,b)), Q(0))

# A noncommuting small physical remap, with an active-active edge and guard.
# Direct histories use matrix multiplication; candidate sectors are recombined
# independently below after the algebra was checked by hand.
E=list(map(Q,[10,12,14,16])); rho=Q(19,20); size=len(E)+2
R=remap(E,rho); RF=remap(E,rho*rho); R2=matmul(R,R)
Id=diag([Q(1)]*size)
DR=matrixadd(R2,matrixscale(-1,RF))
h=Q(2,13); c=Q(5,3); n1=Q(7,11); n2=Q(5,11)
x1=Q(2,5); x2=Q(3,5); xF=Q(4,7)
sigma=[Q(0),Q(0),Q(3,7),Q(2,7)]
tau=[h*c*n2*s*(1-x2) for s in sigma]+[Q(0),Q(0)]
A=diag([1/(1+t) for t in tau]); B=matrixadd(Id,matrixscale(-1,A))
AF=diag([1/(1+2*t) for t in tau]); BF=matrixadd(Id,matrixscale(-1,AF))
A1=diag([1/(1+h*c*n1*s*(1-x1)) for s in sigma]+[Q(1),Q(1)])
B1=matrixadd(Id,matrixscale(-1,A1)); DA=matrixadd(A1,matrixscale(-1,A))
C1=diag([t/((1+t)**2*(1+2*t)) for t in tau])
C2=diag([t*t/((1+t)**2*(1+2*t)) for t in tau])
RA=matrixadd(matmul(R,A),matrixscale(-1,matmul(A,R)))
z0=[Q(3,7),Q(2,9),Q(5,13),Q(7,15),Q(2,3),Q(4,5)]
J=[Q(0),Q(0),Q(0),Q(5,11),Q(0),Q(0)]; b=Q(3,7)
q1=vecadd(matvec(R,z0),scale(b,J)); z1=matvec(A1,q1)
q2=vecadd(matvec(R,z1),scale(b,J)); z2=matvec(A,q2)
qF=vecadd(matvec(RF,z0),scale(2*b,J)); zF2=matvec(AF,qF)
p1=matvec(B1,q1); p2=matvec(B,q2); pF2=matvec(BF,qF)
actual_z=vecadd(z2,scale(-1,zF2))
actual_p=vecadd(p1,p2,scale(-1,pF2))
dz_terms=[matvec(matmul(A,R),matvec(DA,q1)),matvec(A,matvec(RA,q1)),
          scale(-1,matvec(C2,matvec(R2,z0))),matvec(AF,matvec(DR,z0)),
          scale(b,matvec(matmul(A,A),matvec(matrixadd(R,matrixscale(-1,Id)),J))),
          scale(b,matvec(C1,J))]
dp_terms=[scale(-1,matvec(matrixadd(Id,matrixscale(-1,matmul(B,R))),matvec(DA,q1))),
          matvec(B,matvec(RA,q1)),
          matvec(B,matvec(matrixadd(Id,matrixscale(-1,R)),matvec(R,z0))),
          matvec(C2,matvec(R2,z0)),matvec(BF,matvec(DR,z0)),
          scale(b,matvec(matmul(B,A),matvec(matrixadd(R,matrixscale(-1,Id)),J))),
          scale(-b,matvec(C1,J))]
record('outgoing_six_sectors',vecadd(*dz_terms)==actual_z,'One exact rational remap/absorption example; noncommuting operators and guard.')
record('absorption_seven_sectors',vecadd(*dp_terms)==actual_p,'Same chronology; direct stage absorption versus sector sum.')
record('absorption_chronology_discriminated',any(dp_terms[2]) and vecadd(*(dp_terms[:2]+dp_terms[3:]))!=actual_p,'Omitting B(I-R)Rz0 changes the vector.')
record('noncommuting_order_discriminated',any(dp_terms[1]) and vecadd(*(dp_terms[:1]+dp_terms[2:]))!=actual_p,'Active-active commutator contributes in this example.')
nr=[Q(1)]*len(E)+[Q(1),Q(0)]; ur=E+[Q(0),Q(1)]
record('guard_number_ledger',dot(nr,actual_p)==-dot(nr,actual_z),'Integrated absorbed photons plus outgoing/guard number.')
record('guard_energy_ledger',dot(ur,actual_p)==(1-rho)*(dot(ur,p1)-b*dot(ur,J))-dot(ur,actual_z),'First absorption precedes second redshift; first birth also redshifts.')
record('remap_number_moment',matvec(list(map(list,zip(*DR))),nr)==[0]*size,'Difference of full and two-half remaps including guard.')
record('remap_energy_moment',matvec(list(map(list,zip(*DR))),ur)==[0]*size,'Same physical terminal redshift.')
tauF=[h*c*n2*s*(1-xF) for s in sigma]+[Q(0),Q(0)]
AFF=diag([1/(1+2*t) for t in tauF])
actual_endpoint=vecadd(z2,scale(-1,matvec(AFF,qF)))
anchor_correction=[2*h*c*n2*s*q/(1+2*t)/(1+2*tf)*(x2-xF)
                   for s,q,t,tf in zip(sigma,qF,tau,tauF)]+[Q(0),Q(0)]
record('Full_anchor_opacity_secant',actual_endpoint==vecadd(actual_z,anchor_correction),'Residual anchor g2 converted to actual Full root gF by Full denominator secant.')

# Original captured-leaf conditions. These are algebraic input checks, not
# atomic source calls or a replay of a certified physical history.
half=load(BASE/'inputs/ncp07/results/first_half/SOURCE_BOX.json')
full=load(BASE/'inputs/ncp07/results/full/SOURCE_BOX.json')
native=load(BASE/'inputs/ncp07/results/full/NATIVE_CONSTANT_LEAVES.json')
M1=bits(load(BASE/'inputs/ncp07/results/first_half/PREBE.json')['fl_dt_SOURCE_bits'])
MF=bits(load(BASE/'inputs/ncp07/results/full/PREBE.json')['fl_dt_SOURCE_bits'])
n1=bits(half['nH_bits']); n2=bits(full['nH_bits']); h=bits(half['dt_bits'])
f1=bits(half['nHe_stored_bits'])/n1; f2=bits(full['nHe_stored_bits'])/n2
c=bits(native['c_bits']); chi=bits(native['CHI_bits'][0])
E=list(map(bits,full['energy_bits'])); sig=[bits(s[0]) for s in full['sigma_bits']]
eps=[bits(s[0]) for s in full['heat_bits']]
record('captured_birth_scaling',MF==2*M1,'Original Full and half captured leaves, exactly.')
record('captured_HI_heat_identity',all(eps[j]==E[j]-chi for j in range(16,33)),'All active HI nodes; exact binary values.')
record('captured_Sterbenz_domain',all(chi<=E[j]<=2*chi for j in range(16,33)),'Active photon energies within factor two of HI threshold.')
record('captured_sigma_order',all(sig[j]>sig[j+1]>0 for j in range(16,32)) and all(s==0 for s in sig[:16]),'Monotone active HI edges; inactive outputs have B=0.')
record('birth_redshift_number_sign_condition',(h*c*n2)**2*sig[23]*sig[24]<1,'Whole 0<=x2<=1 opacity range.')
record('birth_redshift_heat_sign_condition',eps[23]*sig[23]<eps[24]*sig[24] and sig[23]>sig[24],'Positive neutral fraction and birth amplitude give negative direct thermal sector.')

# Temperature alignment and raw-reaction normalization, evaluated with
# independent manufactured rational rates at the aligned temperature.
x=Q(183,200); y=Q(3,10); z=Q(3,5); w=Q(27,2)
kb=bits(native['kb_bits']); ev=bits(native['ev_erg_bits']); CT=2*ev/(3*kb)
e1=x+f1*(y+2*z); e2=x+f2*(y+2*z)
Pi1=1+f1+e1; Pi2=1+f2+e2; ws=w*Pi2/Pi1
T1=CT*w/Pi1; T2=CT*ws/Pi2
record('source_temperature_pullback',T1==T2 and ws>w,'Actual density and fhat leaves, rational point in original root hull.')
t=T1/Q(50000)
alpha=[(i+1)*Q(1,10**13)*(1+t)**2 for i in range(3)]
beta=[(i+2)*Q(1,10**12)/(1+t) for i in range(3)]
kappa=[kb*T1*a*Q(7,2)/ev for a in alpha]
dr=[Q(1,10**14)/(1+t),Q(3,10**15)/(1+t)]
drheat=[Q(23),Q(31)]
threshold=[chi,Q(24),Q(54)]
def raw_np(n,f):
    ne=n*(x+f*(y+2*z)); lower=[n*(1-x),n*f*(1-y-z),n*f*y]
    upper=[n*x,n*f*y,n*f*z]
    ci=[lo*ne*bb/n for lo,bb in zip(lower,beta)]
    rr=[up*ne*aa/n for up,aa in zip(upper,alpha)]
    drr=[upper[1]*ne*dd/n for dd in dr]
    j=[ci[i]-rr[i] for i in range(3)]; j[1]-=sum(drr)
    fw=-dot(threshold,ci)-sum(up*ne*kk/n for up,kk in zip(upper,kappa))-dot(drheat,drr)
    return [j[0],(j[1]-j[2])/f,j[2]/f,fw]
F1=raw_np(n1,f1); F2=raw_np(n2,f2); ratio=n1*e1/(n2*e2)
kwhe=-threshold[1]*(1-y-z)*beta[1]-threshold[2]*y*beta[2]-y*kappa[1]-z*kappa[2]-y*dot(dr,drheat)
record('FT03_fraction_density_bridge',F1[:3]==scale(ratio,F2[:3]),'Raw reaction densities divided by nH and fhat; manufactured rational rates.')
record('FT03_thermal_He_bridge',F1[3]==ratio*F2[3]+n1*e1*(f1-f2)*kwhe,'Separate H and He thermal contributions, same aligned temperature.')
q1=n1*(1-x)**2*(1+t)**3; q2=n2*(1-x)**2*(1+t)**3
record('HH_density_bridge',q1==n1/n2*q2,'Same HH rate function at aligned T; manufactured rational rate.')

# A nonlinear two-dimensional gas source permits a closed-form segment
# Jacobian; it tests the residual sign, rational photo secant and finite T.
h=Q(1,7); a=Q(2,9); Nin=Q(3,11); nu=[Q(1),Q(1,5)]
gF=[Q(4,5),Q(13)]; delta=[Q(1,70),Q(-1,90)]; g2=vecadd(gF,delta)
aa,bb,cc,dd=Q(1,101),Q(1,211),Q(-1,307),Q(1,401)
def F(g):
    xx,ww=g; ph=a*(1-xx)*Nin/(1+2*h*a*(1-xx))
    return [aa*xx*xx+bb*ww+ph,cc*xx+dd*ww*ww+nu[1]*ph]
g0=vecadd(gF,scale(-2*h,F(gF)))
r=vecadd(g2,scale(-1,g0),scale(-2*h,F(g2)))
D0=1+2*h*a*(1-gF[0]); D1=1+2*h*a*(1-g2[0])
psec=-a*Nin/(D0*D1)
Jbar=[[aa*(gF[0]+g2[0])+psec,bb],[cc+nu[1]*psec,dd*(gF[1]+g2[1])]]
Mbar=matrixadd(diag([Q(1),Q(1)]),matrixscale(-2*h,Jbar))
record('nonlinear_residual_sign_and_average',matvec(Mbar,delta)==r,'Full residual evaluated at two-half point gives +r for delta=g2-gF.')
f=Q(83,1000); helium=Q(3,2); PF=1+f+gF[0]+f*helium; P2=PF+delta[0]
Tdiff=CT*g2[1]/P2-CT*gF[1]/PF
record('finite_temperature_difference',Tdiff==CT*(PF*delta[1]-gF[1]*delta[0])/(PF*P2),'Exact finite quotient identity with shared endpoint normalization.')

# The original fixed preconditioner is a stored dyadic approximate inverse.
# Bind its magnitude certificate to the mean-Jacobian theorem without any
# source evaluation or root solver; all products below are exact rationals.
arithmetic=load(HERE.parent/'phys15_premises/extra_inputs/results/full/UNIFORM_ARITHMETIC.json')
C=[[Q(x) for x in row] for row in arithmetic['fixed_C']]
S=[Q(x) for x in arithmetic['radius']]
B=[[bits(v['hi_bits']) for v in row] for row in arithmetic['B']]
q=bits(arithmetic['q']['hi_bits'])
bound_ok=True; exact_magnitudes=[]
for i in range(4):
    magnitudes=[]
    for j in range(4):
        plo=phi=Q(0)
        for k in range(4):
            cell=full['A_Gg'][k][j]
            products=[C[i][k]*bits(cell['lo_bits']),C[i][k]*bits(cell['hi_bits'])]
            plo+=min(products); phi+=max(products)
        ident=Q(i==j)
        magnitude=max(abs(ident-plo),abs(ident-phi))
        bound_ok=bound_ok and magnitude<=B[i][j]
        magnitudes.append(magnitude)
    exact_magnitudes.append(magnitudes)
record('stored_C_B_source_binding',bound_ok,'16 exact I-C*A interval magnitudes fit the original ARITHMETIC B; C is not replaced by an exact inverse.')
rows=[sum(B[i][j]*S[j]/S[i] for j in range(4)) for i in range(4)]
record('stored_radius_q_binding',max(rows)<=q<1,'The original radius scale and same-file q apply to all mean Jacobians on X.')
record('preconditioned_residual_amplification',1/(1-q)<Q(1000118,1000000),'The 1.000118 bound concerns the S-scaled preconditioned residual C*r.')

# Closed exact inverse in a small example verifies the componentwise
# Neumann majorant and the common-adjoint finite attribution independently.
def inverse2(m):
    det=m[0][0]*m[1][1]-m[0][1]*m[1][0]
    return [[m[1][1]/det,-m[0][1]/det],[-m[1][0]/det,m[0][0]/det]]
invA=inverse2(Mbar)
ell=[-CT*g2[1]/P2/PF,CT/PF]
adjoint=matvec(list(map(list,zip(*invA))),ell)
record('same_adjoint_finite_attribution',dot(adjoint,r)==Tdiff,'Endpoint-dependent finite T covector and the same averaged gas inverse.')
S2=[Q(1,10),Q(2)]; Ebar=matrixadd(diag([Q(1),Q(1)]),matrixscale(-1,Mbar))
Btilde=[[abs(Ebar[i][j])*S2[j]/S2[i] for j in range(2)] for i in range(2)]
q2=max(map(sum,Btilde)); rhs_abs=[abs(r[i])/S2[i] for i in range(2)]
majorant=matvec(inverse2(matrixadd(diag([Q(1),Q(1)]),matrixscale(-1,Btilde))),rhs_abs)
record('componentwise_Neumann_majorant',q2<1 and all(abs(delta[i])/S2[i]<=majorant[i] for i in range(2)),'Nonlinear-source secant example with an exact two-dimensional inverse.')

result={'schema':'WU088_HH_PHYS15_INDEPENDENT_THEORY_CHECKS_V1',
        'reviewer':'/root/hh_phys15_review','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'status':'completed','result':'pass_scoped','arithmetic':'Python Fraction exact rational; standard library only',
        'candidate_modules_imported':False,'candidate_main_reexecuted':False,
        'scientific_history_runs':0,'native_source_runs':0,
        'check_count':len(checks),'checks':checks,
        'case_scope':'Three independent manufactured algebra families plus original captured-leaf inequalities and reused preconditioner binding; general proof assessed separately.',
        'wall_seconds':time.perf_counter()-started,
        'peak_RSS_KiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
target=HERE/'INDEPENDENT_THEORY_CHECKS.json'
with target.open('x') as f: json.dump(result,f,ensure_ascii=False,indent=2); f.write('\n')
print(json.dumps({k:result[k] for k in ('status','result','check_count','scientific_history_runs','wall_seconds','peak_RSS_KiB')},ensure_ascii=False))
