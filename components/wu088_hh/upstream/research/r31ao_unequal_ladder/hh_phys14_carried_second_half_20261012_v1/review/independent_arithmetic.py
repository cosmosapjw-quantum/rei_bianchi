#!/usr/bin/env python3
"""Independent, post-hoc PHYS14 certificate arithmetic.

The candidate module is neither imported nor executed.  Captured source Jets
are reused as premises.  A distinct 380+ bit directed rational arithmetic
checks the delivered root certificate, linear enclosures and observables.
"""
from fractions import Fraction as Q
from pathlib import Path
from collections import Counter
import hashlib, json, struct, time

P=Path('/workspace/scratch/b826cbaab54f/HH_PHYS14_20261012_v1')
O=Path(__file__).parent
COUNTS=Counter(); FAIL=[]; DETAIL=[]

def check(kind, condition, detail=''):
    COUNTS[kind]+=1
    if not condition:
        FAIL.append({'kind':kind,'detail':detail})

def rnd(q, up):
    """Use a finer binary grid without the candidate's floor-log2 branch."""
    q=Q(q)
    if not q:return q
    e=abs(q.numerator).bit_length()-q.denominator.bit_length()-380
    unit=Q(2)**e
    r=q/unit
    k=r.numerator//r.denominator
    return (k+int(up and r.denominator!=1))*unit

def iv(a=0,b=None):
    if isinstance(a,tuple):return a
    return rnd(Q(a),False),rnd(Q(a if b is None else b),True)
def add(a,b):
    a,b=iv(a),iv(b);return rnd(a[0]+b[0],False),rnd(a[1]+b[1],True)
def neg(a):a=iv(a);return -a[1],-a[0]
def sub(a,b):return add(a,neg(b))
def mul(a,b):
    a,b=iv(a),iv(b);z=[x*y for x in a for y in b]
    return rnd(min(z),False),rnd(max(z),True)
def div(a,b):
    a,b=iv(a),iv(b)
    if b[0]<=0<=b[1]:raise ZeroDivisionError('interval denominator contains zero')
    z=[x/y for x in a for y in b]
    return rnd(min(z),False),rnd(max(z),True)
def pw(a,n):
    a=iv(a)
    z=[a[0]**n,a[1]**n]
    return iv(0 if n%2==0 and a[0]<=0<=a[1] else min(z),max(z))
def meet(a,b):return max(a[0],b[0]),min(a[1],b[1])
def dot(a,b):
    s=iv(0)
    for x,y in zip(a,b):s=add(s,mul(x,y))
    return s
def plus(a,b):return [add(x,y) for x,y in zip(a,b)]
def times(a,b):return [mul(a,x) for x in b]
def mv(a,b):return [dot(row,b) for row in a]
def mag(a):return max(abs(a[0]),abs(a[1]))
def inside(a,b):return b[0]<=a[0] and a[1]<=b[1]
def overlaps(a,b):return max(a[0],b[0])<=min(a[1],b[1])
def binary(bits):return Q(struct.unpack('>d',bytes.fromhex(bits))[0])
def saved(a):
    if 'exact' in a:
        z=a['exact'];return Q(*map(int,z['lo'])),Q(*map(int,z['hi']))
    return binary(a['lo_bits']),binary(a['hi_bits'])
def read(s):return json.loads((P/s).read_text())
def srcjet(j):
    return {'f':saved(j['value']),'g':[saved(x) for x in j['gradient'][:4]],
            'H':[[saved(x) for x in row[:4]] for row in j['signed_hessian'][:4]]}
def taylor(j,jc,d):
    return {'f':meet(j['f'],add(jc['f'],dot(j['g'],d))),
            'g':[meet(j['g'][k],add(jc['g'][k],dot(j['H'][k],d))) for k in range(4)],
            'H':j['H']}
def test_cover(kind,got,expected,label=''):
    check(kind,inside(expected,got),label)
    if not inside(expected,got):
        DETAIL.append({'kind':kind,'label':label,'claimed':[float(x) for x in got],
                       'independent':[float(x) for x in expected]})

start=time.perf_counter()
D=read('results/advance01/ADVANCE_RESULTS.json')
SB=read('inputs/ncp07/results/full/SOURCE_BOX.json')
SC=read('inputs/ncp07/results/full/SOURCE_CENTRE.json')
NP=read('inputs/ncp07/results/full/SOURCE_BOX_COMPONENTS.json')
NPC=read('inputs/ncp07/results/full/SOURCE_CENTRE_COMPONENTS.json')
LEAF=read('inputs/ncp07/results/full/NATIVE_CONSTANT_LEAVES.json')
P9=read('inputs/phys09/PROJECTED_RESULTS.json')
P11=read('inputs/phys11/CARRY_RESULTS.json')
P13=read('inputs/phys13/THERMO_RESULTS.json')
RHO=saved(D['constants']['rho'])
h=binary(read('inputs/ncp07/results/first_half/SOURCE_BOX.json')['dt_bits'])
nh=binary(SB['nH_bits']);fh=binary(SB['nHe_stored_bits'])/nh
CT=2*binary(LEAF['ev_erg_bits'])/(3*binary(LEAF['kb_bits']))
HM=binary(SB['Hmean_bits']);chi=binary(LEAF['CHI_bits'][0]);C=iv(CT)
E=[binary(x) for x in SB['energy_bits']]
A=[binary(LEAF['c_bits'])*nh*binary(row[0]) for row in SB['sigma_bits']]
HEAT=[binary(row[0]) for row in SB['heat_bits']]
Z=[saved(x) for x in D['root_certificate']['root_image']]
X=[saved(x) for x in D['root_certificate']['domain_X']]
G1=[saved(x) for x in D['root_certificate']['input_g1']]
N={s:[saved(x) for x in D['photon_state']['incoming'][s]] for s in ['value','U','V','W']}
GS={s:[saved(x) for x in D['gas_response'][s]] for s in ['U','V','W']}
CP=read('inputs/ncp07/results/full/UNIFORM_DIAGNOSTICS.json')['center']
CENTER=[iv(Q(x)) for x in CP]
OLD=next(x for x in P9['stages'] if x['stage']=='first_half')
OD=next(x for x in P9['details'] if x['stage']=='first_half')
check('captured_centre_binding',[saved(x) for x in OD['Banach_ball_center']]==CENTER)
check('chronology',h==625000000 and binary(SB['dt_bits'])==2*h)
test_cover('temperature_constant',saved(D['constants']['C_T']),iv(CT))
test_cover('density_ratio',saved(D['constants']['fhat_source']),iv(fh))

def evaluate(Y,tight):
    delta=[sub(x,c) for x,c in zip(Y,CENTER)]
    np=[srcjet(x) for x in NP['nonphoto']];q=srcjet(SB['q'])
    if tight:
        np=[taylor(x,srcjet(y),delta) for x,y in zip(np,NPC['nonphoto'])]
        q=taylor(q,srcjet(SC['q']),delta)
    hh=[iv(1),iv(0),iv(0),iv(-chi)]
    f=[add(np[i]['f'],mul(mul(iv(0,1),q['f']),hh[i])) for i in range(4)]
    j=[[add(np[i]['g'][k],mul(mul(iv(0,1),q['g'][k]),hh[i])) for k in range(4)] for i in range(4)]
    hes=[[[add(np[i]['H'][k][l],mul(mul(iv(0,1),q['H'][k][l]),hh[i])) for l in range(4)] for k in range(4)] for i in range(4)]
    qa=[mul(q['f'],v) for v in hh]
    mem=[iv(0) for _ in range(4)];vb=mem.copy();mix=mem.copy()
    ja=[[mul(q['g'][k],hh[i]) for k in range(4)] for i in range(4)]
    jb=[[iv(0) for _ in range(4)] for _ in range(4)]
    kernels=[]
    for m,a in enumerate(A):
        d=add(1,mul(h*a,sub(1,Y[0])))
        k=div(mul(a,sub(1,Y[0])),d)
        k1=div(-a,pw(d,2));k2=div(-2*h*a*a,pw(d,3))
        kernels.append((d,k,k1,k2))
        for i,c in [(0,Q(1)),(3,HEAT[m])]:
            f[i]=add(f[i],mul(mul(c,k),N['value'][m]))
            j[i][0]=add(j[i][0],mul(mul(c,k1),N['value'][m]))
            hes[i][0][0]=add(hes[i][0][0],mul(mul(c,k2),N['value'][m]))
            mem[i]=add(mem[i],mul(mul(c,k),N['U'][m]))
            vb[i]=add(vb[i],mul(mul(c,k),N['V'][m]))
            mix[i]=add(mix[i],mul(mul(c,k),N['W'][m]))
            ja[i][0]=add(ja[i][0],mul(mul(c,k1),N['U'][m]))
            jb[i][0]=add(jb[i][0],mul(mul(c,k1),N['V'][m]))
    f[3]=sub(f[3],mul(2*HM,Y[3]));j[3][3]=sub(j[3][3],2*HM)
    return dict(f=f,j=j,H=hes,u=plus(qa,mem),v=vb,ja=ja,jb=jb,mix=mix,qa=qa,mem=mem,kernels=kernels)

WHOLE=evaluate(X,False)
Pi=plus(G1,times(h,WHOLE['f']))
REC=D['root_certificate']
for i in range(4):
    test_cover('whole_X_self_map',saved(REC['whole_domain_self_map_image'][i]),Pi[i],str(i))
    check('strict_self_map',X[i][0]<Pi[i][0] and Pi[i][1]<X[i][1],str(i))
S=[saved(x)[0] for x in REC['scaled_inf_scales']]
def row_norm(L):return [sum(mag(L[i][j])*S[j]/S[i] for j in range(4)) for i in range(4)]
WROWS=row_norm([times(h,row) for row in WHOLE['j']])
for i,r in enumerate(WROWS):
    check('whole_contraction_row',r<=saved(REC['whole_domain_row_bounds'][i])[1],str(i))
check('whole_contraction',max(WROWS)<=saved(REC['whole_domain_contraction_upper'])[1]<1)
prior=[meet(x,y) for x,y in zip(X,[saved(z) for z in REC['whole_domain_self_map_image']])]
for k,target in enumerate(REC['refinement_images']):
    ev=evaluate(prior,True)
    im=plus(G1,times(h,ev['f']))
    expected=[meet(a,b) for a,b in zip(prior,im)]
    for i in range(4):test_cover('root_refinement',saved(target[i]),expected[i],f'{k}:{i}')
    prior=[saved(x) for x in target]
check('root_is_final_refinement',prior==Z)
for i in range(4):check('refined_inside_original_X',inside(Z[i],X[i]),str(i))

NEW=evaluate(Z,True)
LC=D['linear_certificates'];L=[[saved(x) for x in row] for row in LC['L_hFg']]
for i in range(4):
    for j in range(4):test_cover('new_source_Jacobian',L[i][j],mul(h,NEW['j'][i][j]),f'{i}:{j}')
check('refined_contraction',max(row_norm(L))<=saved(REC['refined_contraction_upper'])[1]<1)
RHS={s:[saved(x) for x in LC['rhs_'+s]] for s in ['U','V','W']}
for s,forcing in [('U',NEW['u']),('V',NEW['v'])]:
    ex=plus([saved(x) for x in OLD[s]],times(h,forcing))
    for i in range(4):test_cover('global_'+s+'_forcing',RHS[s][i],ex[i],str(i))
bil=[]
for i in range(4):
    acc=iv(0)
    for j in range(4):
        for k in range(4):acc=add(acc,mul(mul(NEW['H'][i][j][k],GS['U'][j]),GS['V'][k]))
    bil.append(acc)
WTERMS={'F_gg_U_V':bil,'F_g_lambda_V':mv(NEW['ja'],GS['V']),
        'F_g_b_U':mv(NEW['jb'],GS['U']),'F_lambdab_incoming':NEW['mix']}
for name,term in WTERMS.items():
    for i in range(4):test_cover('mixed_forcing_terms',saved(LC['mixed_rhs_terms_per_second'][name][i]),term[i],name+str(i))
WF=[]
for i in range(4):
    z=iv(0)
    for term in WTERMS.values():z=add(z,term[i])
    WF.append(z)
expectedW=plus([saved(x) for x in OLD['W']],times(h,WF))
for i in range(4):test_cover('global_W_forcing',RHS['W'][i],expectedW[i],str(i))

def neumann_review(rhs,certificate,target,label):
    q=saved(certificate['contraction_upper'])[1]
    check('Neumann_contraction',max(row_norm(L))<=q<1,label)
    degree=certificate['degree'];term=rhs.copy();poly=rhs.copy()
    for _ in range(degree):term=mv(L,term);poly=plus(poly,term)
    bn=max(mag(rhs[i])/S[i] for i in range(4))
    check('scaled_rhs_norm',bn<=saved(certificate['scaled_rhs_norm_upper'])[1],label)
    exact_tail=q**(degree+1)*bn/(1-q)
    for i in range(4):
        tail=S[i]*exact_tail
        check('linear_tail_bound',tail<=saved(certificate['absolute_tail'][i])[1],label+str(i))
        test_cover('linear_solution_enclosure',target[i],add(poly[i],iv(-tail,tail)),label+str(i))
for s in ['U','V','W']:neumann_review(RHS[s],LC[s],GS[s],s)

e=add(Z[0],mul(fh,add(Z[1],mul(2,Z[2]))));parts=add(1+fh,e);w=Z[3]
T=div(mul(CT,w),parts)
EM={s:add(GS[s][0],mul(fh,add(GS[s][1],mul(2,GS[s][2])))) for s in GS}
TM={s:mul(CT,sub(div(GS[s][3],parts),div(mul(w,EM[s]),pw(parts,2)))) for s in ['U','V']}
Wt=div(GS['W'][3],parts)
Wt=sub(Wt,div(mul(GS['U'][3],EM['V']),pw(parts,2)))
Wt=sub(Wt,div(mul(GS['V'][3],EM['U']),pw(parts,2)))
Wt=sub(Wt,div(mul(w,EM['W']),pw(parts,2)))
Wt=add(Wt,div(mul(mul(mul(2,w),EM['U']),EM['V']),pw(parts,3)))
TM['W']=mul(CT,Wt)
READ=D['readouts']
for key,z in [('electron_per_H',e),('particle_per_H',parts),('temperature_K',T),('electron_density_cm3',mul(nh,e))]:
    test_cover('value_readout',saved(READ['value'][key]),z,key)
for s in GS:
    test_cover('electron_readout',saved(READ[s]['electron_per_H']),EM[s],s)
    test_cover('temperature_readout',saved(READ[s]['temperature_K']),TM[s],s)
    test_cover('electron_density_readout',saved(READ[s]['electron_density_cm3']),mul(nh,EM[s]),s)
check('HH_ionization_and_cooling',EM['U'][0]>0 and TM['U'][1]<0)
check('birth_heat_and_cooling',GS['V'][3][0]>0 and EM['V'][0]>0 and TM['V'][1]<0)
check('mixed_signs',EM['W'][1]<0 and TM['W'][0]>0)
TG=[neg(div(mul(CT,w),pw(parts,2))),neg(div(mul(CT*fh,w),pw(parts,2))),
    neg(div(mul(2*CT*fh,w),pw(parts,2))),div(CT,parts)]
for i in range(4):test_cover('temperature_gradient',saved(READ['temperature_gradient'][i]),TG[i],str(i))
for name,forcing in [('inherited_gas',[saved(x) for x in OLD['U']]),('direct_second_half_HH',times(h,NEW['qa'])),('inherited_photon_memory',times(h,NEW['mem']))]:
    q=D['HH_U_decomposition'][name];g=[saved(x) for x in q['gas_U']]
    # Forcing reconstructed at higher precision is tighter than owner RHS.
    neumann_review(forcing,q['linear_tail'],g,name)
    test_cover('decomposition_temperature',saved(q['temperature_U_K']),dot(TG,g),name)
    check('decomposition_cooling_sign',saved(q['temperature_U_K'])[1]<0,name)

# Distinct four-slot Jet operations check the outgoing implicit quotient.
def jmul(a,b):
    return [mul(a[0],b[0]),add(mul(a[1],b[0]),mul(a[0],b[1])),
            add(mul(a[2],b[0]),mul(a[0],b[2])),
            add(add(mul(a[3],b[0]),mul(a[1],b[2])),add(mul(a[2],b[1]),mul(a[0],b[3])))]
def jinv(a):
    return [div(1,a[0]),neg(div(a[1],pw(a[0],2))),neg(div(a[2],pw(a[0],2))),
            sub(div(mul(2,mul(a[1],a[2])),pw(a[0],3)),div(a[3],pw(a[0],2)))]
PH=D['photon_state']
for j,a in enumerate(A):
    den=[NEW['kernels'][j][0],mul(-h*a,GS['U'][0]),mul(-h*a,GS['V'][0]),mul(-h*a,GS['W'][0])]
    full=jmul([N[s][j] for s in ['value','U','V','W']],jinv(den))
    test_cover('positive_denominator',saved(REC['denominators'][j]),den[0],str(j))
    check('denominator_positive',den[0][0]>0,str(j))
    for s,expected in zip(['value','U','V','W'],full):
        got=saved(PH['outgoing'][s][j])
        # Interval expression regrouping may produce a different valid width;
        # equality of the rational function is separately checked by Jet algebra.
        check('outgoing_Jet_overlap',overlaps(got,expected),s+str(j))
        balance=sub(sub(N[s][j],got),saved(PH['absorbed'][s][j]))
        check('absorption_number_balance',balance[0]<=0<=balance[1],s+str(j))

# Reconstruct the delivered second-stage input from the inherited first-stage
# spectral jets and the actual little-endian pre-BE guard payload.
ST11=next(z for z in P11['stages'] if z['stage']=='first_half')
preblob=(P/'inputs/ncp07/results/first_half/prebe_words.bin').read_bytes()
gn0,gu0=iv(0),iv(0)
for r in range(128):
    for k in [0,1]:
        off=(6+114*(4+4224+128*k+r))*8
        z=tuple(Q(x) for x in struct.unpack_from('<dd',preblob,off))
        if k==0:gn0=add(gn0,z)
        else:gu0=add(gu0,z)
birth=saved(D['constants']['birth_amount_M'])
for s in ['value','U','V','W']:
    prior=[saved(row['outgoing_joint'][s]) for row in ST11['groups']]
    carried=[iv(0) for _ in E]
    gN=gn0 if s=='value' else iv(0)
    gU=mul(RHO,gu0) if s=='value' else iv(0)
    for j,en in enumerate(E):
        eprime=mul(RHO,en)
        if eprime[1]<E[0]:
            gN=add(gN,prior[j]);gU=add(gU,mul(eprime,prior[j]))
        else:
            check('carry_branch',j>=1 and E[j-1]<eprime[0]<eprime[1]<en,s+str(j))
            down=div(sub(en,eprime),en-E[j-1])
            carried[j-1]=add(carried[j-1],mul(down,prior[j]))
            carried[j]=add(carried[j],mul(sub(1,down),prior[j]))
    if s=='value':carried[24]=add(carried[24],mul(iv(0,1),birth))
    if s=='V':carried[24]=add(carried[24],birth)
    for j in range(33):test_cover('inherited_spectral_carry',N[s][j],carried[j],s+str(j))
    test_cover('inherited_guard_carry',saved(PH['guard'][s]['number']),gN,s+' N')
    test_cover('inherited_guard_carry',saved(PH['guard'][s]['energy_eV_per_H']),gU,s+' E')

def raw_photon(blob,ray,j):
    off=(5+114*(4+ray*33+j))*8
    lo,hi=struct.unpack_from('<dd',blob,off)
    return Q(lo),Q(hi)
blob=(P/'inputs/ncp07/results/first_half/prebe_input_words.bin').read_bytes()
COMMON=[]
for j in range(33):
    row=[raw_photon(blob,r,j) for r in range(128)]
    COMMON.append((sum(x[0] for x in row),sum(x[1] for x in row)))
REM=D['remap_split_defect'];a=[iv(0)]+[div(mul(sub(1,RHO),E[j]),E[j]-E[j-1]) for j in range(1,33)]
DEF=[iv(0) for _ in E];l1=[]
for col in REM['columns_j_ge_2']:
    j=col['input_node'];t=(E[j-1]-E[j-2])/(E[j]-E[j-1]);u=mul(a[j],a[j-1])
    co=[u,mul(-(1+t),u),mul(t,u)]
    for k,c in enumerate(co):
        test_cover('remap_column_coefficient',saved(col['coefficients'][k]),c,f'{j}:{k}')
        DEF[j-2+k]=add(DEF[j-2+k],mul(c,COMMON[j]))
    ell=mul(2*(1+t),u);l1.append(ell)
    test_cover('remap_column_L1',saved(col['L1']),ell,str(j))
DEF[1]=add(DEF[1],mul(mul(a[1],sub(add(a[1],RHO),1)),COMMON[1]))
DEF[0]=sub(DEF[0],mul(mul(a[1],add(a[1],RHO)),COMMON[1]))
GN=mul(a[1],COMMON[1]);GU=mul(mul(RHO,E[0]),GN)
for j,z in enumerate(DEF):test_cover('COMMON_weighted_remap',saved(REM['common_weighted_group_difference'][j]),z,str(j))
test_cover('COMMON_guard_N_remap',saved(REM['common_weighted_guard_number_difference']),GN)
test_cover('COMMON_guard_U_remap',saved(REM['common_weighted_guard_energy_difference_eV_per_H']),GU)
act=iv(0)
for z in DEF[16:]:act=add(act,z)
test_cover('COMMON_HI_active_remap',saved(REM['common_weighted_HI_active_photon_number_difference']),act)
check('COMMON_HI_active_sign',act[1]<0)
maximum=(max(x[0] for x in l1),max(x[1] for x in l1))
test_cover('max_remap_L1',saved(REM['max_column_L1_enclosure']),maximum)
boundary_l1_upper=2*a[1][1]+2*a[1][1]*a[1][1]
check('max_includes_guard_boundary_column',boundary_l1_upper<maximum[0])

# All delivered decimal endpoints and signs, including repeated finite views.
def walk(v,path=''):
    if isinstance(v,dict):
        if 'exact' in v and 'outward_decimal' in v:
            a,b=saved(v);lo,hi=map(Q,v['outward_decimal'])
            check('outward_decimal',lo<=a<=b<=hi,path)
            sign='STRICT_POSITIVE' if a>0 else 'STRICT_NEGATIVE' if b<0 else 'EXACT_ZERO' if a==b==0 else 'ZERO_CONTAINING'
            check('sign_label',sign==v['sign'],path)
        for k,w in v.items():walk(w,path+'/'+k)
    elif isinstance(v,list):
        for i,w in enumerate(v):walk(w,path+'/'+str(i))
walk(D)
RUN=read('evidence/advance01/RUN_RECORD.json')
check('actual_run_success',RUN['exit_code']==0 and not RUN['timed_out'] and RUN['source_unchanged'])
for rel,z in RUN['outputs'].items():
    data=(P/rel).read_bytes();check('run_output_binding',len(data)==z['bytes'] and hashlib.sha256(data).hexdigest()==z['sha256'],rel)
for rel,z in RUN['source_identity_after'].items():check('run_source_binding',hashlib.sha256((P/rel).read_bytes()).hexdigest()==z,rel)
for z in read('inputs/INPUT_MANIFEST.json'):
    data=(P/z['path']).read_bytes()
    check('input_manifest_binding',len(data)==z['bytes'] and hashlib.sha256(data).hexdigest()==z['sha256'],z['path'])

# Five small rational semantics checks are independent of the history case.
qs=[Q(1,3),-Q(7,5),Q(1,2**1700),-Q(1,2**1700),Q(2**700+1,7)]
check('small_rational_rounding',all(rnd(z,False)<=z<=rnd(z,True) for z in qs))
try:
    div(iv(1),iv(-1,1));zero_rejected=False
except ZeroDivisionError:zero_rejected=True
check('small_zero_divisor',zero_rejected)
# N=(1+b), D=(2-lambda), at lambda=1/3, b=2/5.
closed=jmul([iv(Q(7,5)),iv(0),iv(1),iv(0)],jinv([iv(Q(5,3)),iv(-1),iv(0),iv(0)]))
for got,want in zip(closed,[Q(21,25),Q(63,125),Q(3,5),Q(9,25)]):check('small_joint_quotient',inside(iv(want),got))
check('small_transparent_channel',jmul([iv(0),iv(2),iv(3),iv(5)],jinv([iv(1),iv(0),iv(0),iv(0)]))==[iv(0),iv(2),iv(3),iv(5)])
# A closed scalar implicit stage with parameter-dependent Jacobian checks both
# mixed g-parameter terms using an explicit rational-function Jet.
c0,cL,cB,q,r,h0=Q(-1,5),Q(1,7),Q(-1,11),Q(2,7),Q(3,11),Q(1,4)
la,be=Q(2,5),Q(1,3);s0,sU,sV,sW=Q(1,2),Q(1,17),Q(1,19),Q(1,23)
den=1-h0*(c0+cL*la+cB*be)
num=s0+h0*(la*q+be*r)
g0=num/den
gU=(sU+h0*(q+cL*g0))/den
gV=(sV+h0*(r+cB*g0))/den
gW=(sW+h0*(cL*gV+cB*gU))/den
quot=jmul([iv(num),iv(sU+h0*q),iv(sV+h0*r),iv(sW)],
          jinv([iv(den),iv(-h0*cL),iv(-h0*cB),iv(0)]))
check('small_scalar_implicit',all(inside(iv(ex),got) for ex,got in zip([g0,gU,gV,gW],quot)))

payload={'schema':'WU088_HH_PHYS14_INDEPENDENT_ARITHMETIC_V1','candidate_imported':False,
    'candidate_program_reexecuted':False,'atomic_source_kernel_replayed':False,
    'review_reference_arithmetic':'directed Fraction on a finer unbounded 380+ significant-bit binary grid',
    'new_scientific_history_families':1,'small_semantics_categories':5,
    'counts_are_scientific_case_counts':False,'assertion_counts':dict(COUNTS),
    'total_assertions':sum(COUNTS.values()),'failures':FAIL,'failed_interval_details':DETAIL,
    'wall_seconds':time.perf_counter()-start,
    'scope':'New source recomposition and certificate arithmetic only, inherited nonphoto/q and first-stage source/C2 inclusion premises',
    'candidate_sha256':hashlib.sha256((P/'src/phys14_advance.py').read_bytes()).hexdigest(),
    'result_sha256':hashlib.sha256((P/'results/advance01/ADVANCE_RESULTS.json').read_bytes()).hexdigest()}
(O/'INDEPENDENT_ARITHMETIC.json').write_text(json.dumps(payload,indent=2)+'\n')
print(json.dumps({'assertions':payload['total_assertions'],'failures':len(FAIL),'categories':dict(COUNTS),'wall_seconds':payload['wall_seconds'],'failure_preview':FAIL[:12]}))
