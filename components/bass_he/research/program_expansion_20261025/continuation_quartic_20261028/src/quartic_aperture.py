"""QUARTIC12 signed quartic positivity sandwich. No calculations on import."""
from fractions import Fraction as F
from itertools import combinations
from pathlib import Path
import hashlib
import importlib.util
import sys
ROOT=Path(__file__).resolve().parents[1]
p=ROOT.parent/'continuation_exfor_20261028/src/exfor_aperture.py'
spec=importlib.util.spec_from_file_location('_quartic12_exfor',p);E=importlib.util.module_from_spec(spec);sys.modules[spec.name]=E;spec.loader.exec_module(E)
ContractError=E.ContractError
B=F(160);DMIN=F(49,4800000);D=(F(2),F(2,3),F(2,5));ANGLES=E.ANGLES
rational=E.rational
def dot(a,b):return sum((x*y for x,y in zip(a,b)),F(0))

def angle_row(theta):
    theta=rational(theta)
    if not 0<=theta<=180:raise ContractError('nominal angle outside [0,180]')
    mu=E.H.sincos_turn(theta/720)[1]
    # Nominal measured angles lie in first quadrant; general intervals may cross0.
    def square(iv):
        lo=F(0) if iv.lower<=0<=iv.upper else min(iv.lower**2,iv.upper**2)
        hi=max(iv.lower**2,iv.upper**2)
        return E.H.Interval(lo,hi)
    z=square(mu);z2=square(z)
    z=E.H.Interval(E.H.floor_grid(z.lower,60),E.H.ceil_grid(z.upper,60))
    z2=E.H.Interval(E.H.floor_grid(z2.lower,60),E.H.ceil_grid(z2.upper,60))
    return dict(angle=theta,mu=(mu.lower,mu.upper),z=(z.lower,z.upper),z2=(z2.lower,z2.upper),midpoint=(F(1),(z.lower+z.upper)/2,(z2.lower+z2.upper)/2),epsilon=B*(z.width+z2.width)/2)

def quadratic_minimum(b):
    b=tuple(rational(x) for x in b)
    if len(b)!=3:raise ContractError('three signed monomial coefficients required')
    candidates=[(b[0],F(0)),(sum(b),F(1))]
    if b[2]>0:
        z=-b[1]/(2*b[2])
        if 0<z<1:candidates.append((b[0]+b[1]*z+b[2]*z*z,z))
    minimum,z=min(candidates)
    return dict(value=minimum,z=z,nonnegative=minimum>=0)

def folded_bernstein(b):
    x,y,z=b;return (x+y+z,x-z,x+z-y/3)

def lift(v,endpoint):return (v[0],v[1],-v[0]-v[1]) if endpoint else tuple(v)
def transform(row,endpoint):return (row[0]-row[2],row[1]-row[2]) if endpoint else tuple(row)

def positivity_rows(N,kind,endpoint):
    # All rows represent q/control >=0, converted to <=0 by caller.
    if endpoint:return ((F(1),F(0)),(F(2),F(1)))
    if type(N)!=int or N not in (1,4,16) or kind not in ('inner','outer'):raise ContractError('fixed N and family kind required')
    rows=[]
    for k in range(N+1):
        x=F(k,N);rows.append((F(1),x,x*x))
    if kind=='inner':
        for k in range(N):
            l,r=F(k,N),F(k+1,N);rows.append((F(1),(l+r)/2,l*r))
    return tuple(rows)

def system(rows,bounds,N,kind,endpoint=False):
    if kind not in ('inner','outer') or type(endpoint)!=bool:raise ContractError('explicit inner/outer and endpoint flag required')
    matrix=[];rhs=[]
    for row,(L,U) in zip(rows,bounds):
        midpoint=transform(row['midpoint'],endpoint);eps=row['epsilon'];offset=eps if kind=='outer' else -eps
        matrix.extend((midpoint,tuple(-x for x in midpoint)));rhs.extend((U+offset,-L+offset))
    for j in range(3):
        row=transform(tuple(F(int(j==k)) for k in range(3)),endpoint)
        matrix.extend((row,tuple(-x for x in row)));rhs.extend((B,B))
    matrix.append(tuple(-x for x in transform(D,endpoint)));rhs.append(-DMIN)
    pos=positivity_rows(N,kind,endpoint)
    for row in pos:matrix.append(tuple(-x for x in row));rhs.append(F(0))
    before=len(matrix);unique={}
    for row,b in zip(matrix,rhs):
        # Same lhs: keep tighter RHS; both data sides preserve exact offsets.
        if row not in unique or b<unique[row]:unique[row]=b
    return tuple(unique),tuple(unique.values()),dict(constraints_before=before,constraints_after=len(unique),duplicate_constraints_removed=before-len(unique),positivity_rows_before=len(pos))

def enumerate_shared(matrix,right_sides):
    n=len(matrix[0]);vertices=[set() for _ in right_sides];feasible=[0]*len(right_sides);attempted=singular=0
    for active in combinations(range(len(matrix)),n):
        attempted+=1;inv=E.inverse(tuple(matrix[i] for i in active))
        if inv is None:singular+=1;continue
        for j,rhs in enumerate(right_sides):
            v=tuple(dot(row,tuple(rhs[i] for i in active)) for row in inv)
            if all(dot(row,v)<=r for row,r in zip(matrix,rhs)):vertices[j].add(v);feasible[j]+=1
    shared=dict(active_bases_attempted=attempted,singular_bases=singular,exact_inverse_calls=attempted,invertible_bases=attempted-singular,rhs_candidate_count=(attempted-singular)*len(right_sides),rhs_system_count=len(right_sides))
    return [dict(vertices=sorted(v),bases_attempted=attempted,singular_bases=singular,feasible_bases=f,unique_vertices=len(v)) for v,f in zip(vertices,feasible)],shared

def integrate_monomials(intervals):
    intervals=tuple((rational(l),rational(h)) for l,h in intervals)
    if any(not -1<=l<=h<=1 for l,h in intervals) or any(intervals[i][1]>intervals[i+1][0] for i in range(len(intervals)-1)):raise ContractError('ordered disjoint physical intervals required')
    return tuple(sum(((h**(2*j+1)-l**(2*j+1))/(2*j+1) for l,h in intervals),F(0)) for j in range(3))

def moments(strips):
    lo=[F(0)]*3;hi=lo.copy()
    for strip in strips:
        l,h=strip['interval'];sets=strip['sets']['coincidence']
        for out,region in ((lo,sets.inner),(hi,sets.outer)):
            for j,v in enumerate(integrate_monomials(region)):out[j]+=(h-l)*v
    assert all(0<=a<=b<=d for a,b,d in zip(lo,hi,D))
    return dict(lower=tuple(lo),upper=tuple(hi),width=tuple(b-a for a,b in zip(lo,hi)))

def signed_numerator(b,klo,khi):
    return (sum((x*(l if x>=0 else h) for x,l,h in zip(b,klo,khi)),F(0)),sum((x*(h if x>=0 else l) for x,l,h in zip(b,klo,khi)),F(0)))

def vertex_intervals(vertices,endpoint,moment):
    result=[]
    for v in vertices:
        b=lift(v,endpoint);den=dot(D,b)
        if den<DMIN:raise ContractError('Dfloor violated')
        lo,hi=signed_numerator(b,moment['lower'],moment['upper'])
        result.append(dict(parameters=v,coefficients=b,denominator=den,lower=lo/den,upper=hi/den))
    return result

def objective(inner,outer,endpoint,moment):
    vin=vertex_intervals(inner,endpoint,moment);vout=vertex_intervals(outer,endpoint,moment)
    if not vout:return dict(status='EMPTY_OUTER',raw_outer_ratio_range=None,physical_range=None,minimum_bracket=None,maximum_bracket=None,outer_lower_witness=None,outer_upper_witness=None,inner_minimum_witness=None,inner_maximum_witness=None)
    low=min(vout,key=lambda v:v['lower']);high=max(vout,key=lambda v:v['upper']);raw=(low['lower'],high['upper']);physical=(max(F(0),raw[0]),min(F(1),raw[1]))
    if physical[0]>physical[1]:
        if vin:raise ContractError('inner witness contradicts empty physical intersection')
        return dict(status='EMPTY_PHYSICAL_INTERSECTION',reason='The specified outer ratio enclosure has empty intersection with physical [0,1]; scoped to this finite family and geometry.',raw_outer_ratio_range=raw,physical_range=None,minimum_bracket=None,maximum_bracket=None,outer_lower_witness=low,outer_upper_witness=high,inner_minimum_witness=None,inner_maximum_witness=None)
    imin=min(vin,key=lambda v:v['upper']) if vin else None;imax=max(vin,key=lambda v:v['lower']) if vin else None
    return dict(status='CERTIFIED_SANDWICH',raw_outer_ratio_range=raw,physical_range=physical,minimum_bracket=(physical[0],imin['upper'] if imin else None),maximum_bracket=(imax['lower'] if imax else None,physical[1]),outer_lower_witness=low,outer_upper_witness=high,inner_minimum_witness=imin,inner_maximum_witness=imax)

def witness(vertices,endpoint,rows,bounds):
    if not vertices:return None
    candidates=[]
    for v in vertices:
        b=lift(v,endpoint);minimum=quadratic_minimum(b)
        if not minimum['nonnegative']:raise ContractError('inner exact positivity failed')
        a=folded_bernstein(b)
        # Prefer an outside-old-cone vertex, then lexicographic exact order.
        candidates.append((not any(x<0 for x in a),v,b,minimum,a))
    _,v,b,minimum,a=min(candidates)
    data=[dict(angle=row['angle'],midpoint_value=dot(row['midpoint'],b),value_enclosure=(dot(row['midpoint'],b)-row['epsilon'],dot(row['midpoint'],b)+row['epsilon']),sensitivity=(L,U)) for row,(L,U) in zip(rows,bounds)]
    return dict(parameters=v,coefficients=b,qminimum=minimum,denominator=dot(D,b),old_folded_bernstein=a,outside_old_sufficient_cone=any(x<0 for x in a),data=data)

def campaign(source,prior_saved,progress=None):
    tables=E.parse_source(source);energies=(213,258,330);rows=tuple(angle_row(t) for t in ANGLES)
    selected=[rows[i]['z'] for i in (0,1,3)];assert all(0<=l<=h<=1 for l,h in selected)
    for i in range(3):
        for j in range(i):assert max(selected[i][0]-selected[j][1],selected[j][0]-selected[i][1])>=F(1,5)
    delta=F(7,50)/(12*B);assert -1<rows[-1]['mu'][0]-delta and rows[-1]['mu'][1]+delta<1
    bounds={e:tuple(E.sensitivity(r[2],r[3]) for r in tables['M0475002'] if r[0]==e) for e in energies}
    assert all(0<=L<=U<=1 for b in bounds.values() for L,U in b) and all(b[-1][0]>=F(7,50) for b in bounds.values())
    data=dict(unit='HE-EXP-QUARTIC-12',source_sha256=E.SOURCE_SHA,B=B,D=D,Dmin=DMIN,rows=rows,dcs=tables['M0475002'],totals=tables['M0475003'],cases=[],enumeration_groups=[],scope='FULL nonnegative even quartic; sensitivity windows; declared uniform azimuth')
    raw=Path(prior_saved).read_bytes();import json
    prior=json.loads(raw);assert prior['unit']=='HE-EXP-EXFOR-11' and prior['source_sha256']==E.SOURCE_SHA
    data['prior_saved_result_sha256']=hashlib.sha256(raw).hexdigest();data['prior_degree4_comparison']=[{k:c[k] for k in ('energy','degree','endpoint_zero','polytopes')} for c in prior['cases'] if c['degree']==4]
    geo={e:{name:moments(s) for name,s in E.geometries(e).items()} for e in energies};data['moments_by_energy']={str(e):v for e,v in geo.items()}
    if progress:progress(data)
    for N,endpoint,label in ((1,False,'free_N1'),(4,False,'free_N4'),(16,False,'free_N16'),(None,True,'endpointzero_exact')):
        cases={e:dict(energy=e,case=label,N=N,endpoint_zero=endpoint,polytopes={}) for e in energies}
        # Group identical matrix identities; endpoint inner/outer share inversions.
        groups={}
        data['in_progress_cases']=cases
        for kind in ('inner','outer'):
            for e in energies:
                matrix,rhs,counts=system(rows,bounds[e],N,kind,endpoint);groups.setdefault(matrix,[]).append((kind,e,rhs,counts))
        for matrix,members in groups.items():
            solutions,counts=enumerate_shared(matrix,[entry[2] for entry in members]);data['enumeration_groups'].append(dict(case=label,**counts))
            for (kind,e,rhs,dedup),p in zip(members,solutions):
                p.update(matrix=matrix,rhs=rhs,**dedup)
                if kind=='inner':
                    p['quadratic_positivity']=[quadratic_minimum(lift(v,endpoint)) for v in p['vertices']]
                    assert all(v['nonnegative'] for v in p['quadratic_positivity'])
                cases[e]['polytopes'][kind]=p
            if progress:progress(data)
        for e in energies:
            case=cases[e];inner=case['polytopes']['inner']['vertices'];outer=case['polytopes']['outer']['vertices']
            case['objectives']={name:objective(inner,outer,endpoint,m) for name,m in geo[e].items()};case['inner_witness']=witness(inner,endpoint,rows,bounds[e])
            case['human_readable_floats']={name:{key:None if o[key] is None else tuple(None if x is None else float(x) for x in o[key]) for key in ('raw_outer_ratio_range','physical_range','minimum_bracket','maximum_bracket')} for name,o in case['objectives'].items()}
            data['cases'].append(case)
        data.pop('in_progress_cases',None)
        if progress:progress(data)
    assert len(data['cases'])==12
    return data

def encode(value):return E.encode(value)
