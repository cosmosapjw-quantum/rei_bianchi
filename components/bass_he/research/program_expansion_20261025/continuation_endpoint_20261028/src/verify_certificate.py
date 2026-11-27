"""Independent exact saved-certificate reader. No producer import or enumeration."""
from fractions import Fraction as Q
from math import comb
import hashlib
import json

EXPECTED_SAVED='a8fbe269d3941706a510796963f059d7404f3f4655a6a3163042e85011aa0d45'
EXPECTED_SOURCE='b2c1c52931e813dd63fb0e98edfc90088bc2eca497fd9142277e748f0935a82f'

def check(condition,label):
    if not condition:raise ValueError(label)
def scalar(a,b):return sum((x*y for x,y in zip(a,b)),Q(0))
def det(a):return a[0][0]*(a[1][1]*a[2][2]-a[1][2]*a[2][1])-a[0][1]*(a[1][0]*a[2][2]-a[1][2]*a[2][0])+a[0][2]*(a[1][0]*a[2][1]-a[1][1]*a[2][0])
def qmin(a):
    candidates=[(a[0],Q(0)),(sum(a),Q(1))]
    if a[2]>0:
        z=-a[1]/(2*a[2])
        if 0<z<1:candidates.append((a[0]+a[1]*z+a[2]*z*z,z))
    value,z=min(candidates,key=lambda p:p[0]);return value,z

def check_witness(v,rows):
    check(all(abs(x)<=160 for x in v),'witness containing box')
    check(scalar((Q(4,3),Q(4,15),Q(4,35)),v)>=Q(49,14400000),'witness D floor')
    check(qmin(v)[0]>=0,'witness full positivity')
    for row in rows:
        m=list(map(Q,row['midpoint']));eps=Q(row['epsilon']);l,h=map(Q,row['window']);value=scalar(m,v)
        check(l<=value-eps and value+eps<=h,'witness true-data enclosure')

def ratio(v,moment):
    denominator=scalar(v,(Q(4,3),Q(4,15),Q(4,35)));check(denominator>0,'positive ratio denominator')
    bounds=list(zip(map(Q,moment['lower']),map(Q,moment['upper'])))
    low=sum((x*(lo if x>=0 else hi) for x,(lo,hi) in zip(v,bounds)),Q(0))
    high=sum((x*(hi if x>=0 else lo) for x,(lo,hi) in zip(v,bounds)),Q(0))
    return low/denominator,high/denominator

def verify(data,old,saved_path=None,official_path=None,unit=None):
    check(data['unit']=='HE-EXP-ENDPOINT-14','unit identity')
    check(data['source_sha256']==EXPECTED_SOURCE and data['saved_input_sha256']==EXPECTED_SAVED,'declared input identity')
    if saved_path is not None:check(hashlib.sha256(saved_path.read_bytes()).hexdigest()==EXPECTED_SAVED,'actual immutable saved input')
    if official_path is not None:check(hashlib.sha256(official_path.read_bytes()).hexdigest()==EXPECTED_SOURCE,'actual official input')
    if unit is not None:
        for path,digest in data['implementation_sha256'].items():check(hashlib.sha256((unit/path).read_bytes()).hexdigest()==digest,'actual implementation binding '+path)
    check(list(map(Q,data['D']))==[Q(4,3),Q(4,15),Q(4,35)] and Q(data['Dmin'])==Q(49,14400000) and Q(data['B'])==160,'fixed normalization/box/floor')
    expected_windows={'46':(Q(11,100),Q(17,100)),'61':(Q(11,100),Q(21,100)),'73':(Q(1,50),Q(3,25)),'87':(Q(7,50),Q(6,25))}
    check(len(data['rows'])==4,'four nominal angles')
    for row,prior in zip(data['rows'],old['rows']):
        l,h=map(Q,prior['z']);low=[(1-h)*l**j for j in range(3)];high=[(1-l)*h**j for j in range(3)]
        check(row['angle']==prior['angle'] and list(map(Q,row['z']))==[l,h],'saved z interval')
        check(list(map(Q,row['basis_lower']))==low and list(map(Q,row['basis_upper']))==high,'all three row basis intervals')
        check(list(map(Q,row['midpoint']))==[(x+y)/2 for x,y in zip(low,high)],'row midpoint')
        check(Q(row['epsilon'])==80*sum((y-x for x,y in zip(low,high)),Q(0)),'all-three-coefficient row epsilon')
        check(tuple(map(Q,row['window']))==expected_windows[row['angle']],'fixed sensitivity windows')
    # Reconstruct the root's D-floor containment from immutable saved mu, not producer rows.
    prior87=next(row for row in old['rows'] if row['angle']=='87');mu_lo,mu_hi=map(Q,prior87['mu']);delta=Q(7,50)/(36*160);expanded=[mu_lo-delta,mu_hi+delta]
    floor_control={'angle':'87','saved_mu':[mu_lo,mu_hi],'Lstar':Q(7,50),'derivative_bound':Q(2880),'delta':delta,'expanded_mu_interval':expanded,'contained_in_minus1_plus1':True,'Dmin':Q(7,50)**2/(36*160)}
    check(-1<=expanded[0]<=expanded[1]<=1,'actual saved87mu floor interval containment')
    recorded=data['containing_box_control']['denominator_floor_control']
    check(set(recorded)==set(floor_control),'Dfloor control complete field set')
    for key,value in floor_control.items():
        actual=recorded[key]
        if isinstance(value,Q):actual=Q(actual)
        elif isinstance(value,list):actual=list(map(Q,actual))
        check(actual==value,'Dfloor control '+key)
    selected=[next(row for row in old['rows'] if row['angle']==angle) for angle in ('46','61','87')]
    zlist=[tuple(map(Q,row['z'])) for row in selected]
    check(all(h<Q(1,2) for l,h in zlist),'containing box selected z upper')
    for i in range(3):
        for j in range(i+1,3):check(max(zlist[i][0]-zlist[j][1],zlist[j][0]-zlist[i][1])>=Q(1,5),'containing box selected z separation')
    bc=data['containing_box_control']
    check(bc['selected_angles']==['46','61','87'] and bc['separation_at_least']=='1/5' and bc['verified'] and bc['lagrange_coefficient_bounds']==[75,150,75] and bc['containing_B']==160,'containing box control fields')
    for name,moment in data['moments'].items():
        lo,hi=list(map(Q,moment['lower'])),list(map(Q,moment['upper']))
        if name=='FULL':check(lo==hi==[Q(4,3),Q(4,15),Q(4,35)],'full exact moments');continue
        previous=old['moments_by_energy']['330'][name];pl=list(map(Q,previous['lower']));ph=list(map(Q,previous['upper']))
        tl,th=1-ph[0]/2,1-pl[0]/2;check(list(map(Q,moment['threshold']))==[tl,th] and 0<=tl<=th<=1,'saved zeroth threshold')
        expectedlo=[2*((1-th**(2*j+1))/Q(2*j+1)-(1-th**(2*j+3))/Q(2*j+3)) for j in range(3)]
        expectedhi=[2*((1-tl**(2*j+1))/Q(2*j+1)-(1-tl**(2*j+3))/Q(2*j+3)) for j in range(3)]
        check(lo==expectedlo and hi==expectedhi and all(0<=x<=y for x,y in zip(lo,hi)),'weighted nonnegative-basis moments')
        control=data['threshold_compatibility'][name]
        for j in range(3):
            lnew=2*(1-th**(2*j+1))/Q(2*j+1);hnew=2*(1-tl**(2*j+1))/Q(2*j+1)
            check(max(lnew,pl[j])<=min(hnew,ph[j]),'old monomial overlap')
            check(control['exact_equality'][j]==(lnew==pl[j] and hnew==ph[j]),'equality separately recorded')
    a=Q('3727.3794118');mass=Q('1875.612945');s=a*a+660*a;k=330**2-(a+330)**2*(s-4*mass*mass)/s
    check(Q(data['kinematic_compatibility']['K'])==k and k<0,'rational monotonic lab map compatibility')
    candidate=tuple(map(Q,data['candidate']['parameters']));check(candidate==(Q(1411,10000),Q(-1,4),Q(33,25)),'frozen candidate')
    check_witness(candidate,data['rows']);check(data['candidate']['feasible'],'candidate outcome')
    check(tuple(map(Q,data['candidate']['ordinary_cubic']))==(candidate[0],candidate[1]-candidate[0],candidate[2]-candidate[1],-candidate[2]),'endpoint factorization')
    check(list(map(Q,data['candidate']['endpoint_values']))==[0,0],'endpoint zero')
    check([case['N'] for case in data['cases']]==[1,4,16],'fixed N set')
    poly={};total_vertices=0;total_bases=0
    for case in data['cases']:
        n=case['N']
        for kind,p in case['polytopes'].items():
            m=[tuple(map(Q,r)) for r in p['matrix']];b=list(map(Q,p['rhs']));vertices=[tuple(map(Q,v)) for v in p['vertices']]
            constraints=[]
            for row in data['rows']:
                mid=tuple(map(Q,row['midpoint']));eps=Q(row['epsilon']);l,h=map(Q,row['window']);shift=eps if kind=='inner' else -eps
                constraints.extend([(mid,h-shift),(tuple(-x for x in mid),-l-shift)])
            for j in range(3):
                v=tuple(Q(int(i==j)) for i in range(3));constraints.extend([(v,Q(160)),(tuple(-x for x in v),Q(160))])
            constraints.append(((Q(-4,3),Q(-4,15),Q(-4,35)),-Q(49,14400000)))
            for j in range(n+1):
                z=Q(j,n);constraints.append(((Q(-1),-z,-z*z),Q(0)))
            if kind=='inner':
                for j in range(n):
                    l,h=Q(j,n),Q(j+1,n);constraints.append(((Q(-1),-(l+h)/2,-l*h),Q(0)))
            expected={}
            for row,rhs in constraints:expected[row]=min(expected.get(row,rhs),rhs)
            check(m==list(expected) and b==list(expected.values()),'complete prescribed matrix '+kind)
            check(len(vertices)==len(set(vertices))==p['unique_vertices']>0,'unique nonempty vertices')
            check(p['bases_attempted']==comb(len(m),3) and p['singular_bases']+p['invertible_bases']==p['bases_attempted'] and p['enumeration_complete'],'exhaustive bounded enumeration count')
            check(p['feasible_bases']>=len(vertices) and p['feasible_bases']<=p['invertible_bases'],'feasible basis count')
            check(len(p['active_bases'])==len(vertices)==len(p['quadratic_minima']),'certificate dimensions')
            for v,active,mini in zip(vertices,p['active_bases'],p['quadratic_minima']):
                check(all(scalar(row,v)<=rhs for row,rhs in zip(m,b)),'vertex inequalities')
                check(len(set(active))==3 and all(0<=i<len(m) for i in active),'active triple indices')
                check(det([m[i] for i in active])!=0 and all(scalar(m[i],v)==b[i] for i in active),'independent active triple')
                val,z=qmin(v);check(Q(mini['value'])==val and Q(mini['z'])==z and mini['nonnegative']==(val>=0),'exact quadratic minimum')
                if kind=='inner':check_witness(v,data['rows'])
            poly[(n,kind)]=(m,b,vertices);total_vertices+=len(vertices);total_bases+=p['bases_attempted']
        feasible=poly[(n,'inner')][2]+[candidate]
        for name,obj in case['objectives'].items():
            iv=[ratio(v,data['moments'][name]) for v in feasible];ov=[ratio(v,data['moments'][name]) for v in poly[(n,'outer')][2]]
            outer=[min(v[0] for v in ov),max(v[1] for v in ov)];minbr=[max(Q(0),outer[0]),min(Q(1),min(v[1] for v in iv))];maxbr=[max(Q(0),max(v[0] for v in iv)),min(Q(1),outer[1])]
            expected={'raw_outer_ratio_range':outer,'physical_range':[max(Q(0),outer[0]),min(Q(1),outer[1])],'minimum_bracket':minbr,'maximum_bracket':maxbr}
            for key,vals in expected.items():
                check(list(map(Q,obj[key]))==vals,'saved extrema '+key)
                displayed=list(map(Q,obj['outward_decimal'][key]));check(displayed[0]<=vals[0] and displayed[1]>=vals[1],'outward display '+key)
            check(Q(obj['minimum_width'])==minbr[1]-minbr[0] and Q(obj['maximum_width'])==maxbr[1]-maxbr[0],'actual bracket widths')
            for label,bound,index in [('inner_minimum_witness',minbr,1),('inner_maximum_witness',maxbr,0)]:
                v=tuple(map(Q,obj[label]));check(v in feasible,'selected feasible witness membership');check_witness(v,data['rows'])
                value=ratio(v,data['moments'][name])[index];check((min(Q(1),value) if index else max(Q(0),value))==bound[index],'selected witness bound')
            for label,index in [('outer_lower_witness',0),('outer_upper_witness',1)]:
                v=tuple(map(Q,obj[label]));check(v in poly[(n,'outer')][2] and ratio(v,data['moments'][name])[index]==outer[index],'selected outer extremum')
            if name=='FULL':check(outer==minbr==maxbr==[1,1],'FULL exact one')
    check(len(data['nesting'])==4,'four nesting controls')
    for c in data['nesting']:
        _,_,vs=poly[(c['from_N'],c['kind'])];m,b,_=poly[(c['to_N'],c['kind'])]
        check(c['pass'] and c['checked_vertices']==len(vs) and all(all(scalar(row,v)<=rhs for row,rhs in zip(m,b)) for v in vs),'exact vertex nesting')
    prior=[{'N':c['N'],'endpoint_zero':c['endpoint_zero'],'objectives':c['objectives']} for c in old['cases'] if c['energy']==330]
    check(data['prior_quartic330']==prior,'saved comparison read-only')
    for sample in data['plot']['curve_samples']:
        mu=Q(sample['mu']);z=mu*mu;check(Q(sample['dcs'])==(1-z)*(candidate[0]+candidate[1]*z+candidate[2]*z*z),'primary saved curve')
    return {'status':'PASS','independent_reader':True,'producer_imports':0,'candidate_search_calls':0,'enumeration_calls':0,'checked_polytopes':6,'checked_vertices':total_vertices,'reported_exhausted_bases':total_bases,'scope':'Saved matrices, feasible independent active triples, reported exhaustion counts, exact moments/rows/witnesses/extrema/nesting/inputs; completeness additionally rests on producer exhaustive-loop implementation'}
