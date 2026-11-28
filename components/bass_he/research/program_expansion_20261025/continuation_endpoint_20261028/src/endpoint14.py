"""Frozen ENDPOINT14 algebra. Fraction-only science; no computations on import."""
from fractions import Fraction as F
from itertools import combinations
from math import comb
import hashlib
import json

B=F(160)
D=(F(4,3),F(4,15),F(4,35))
DMIN=F(49,14400000)
CANDIDATE=(F(1411,10000),F(-1,4),F(33,25))
WINDOWS={'46':(F(11,100),F(17,100)), '61':(F(11,100),F(21,100)), '73':(F(1,50),F(3,25)), '87':(F(7,50),F(6,25))}
SAVED_SHA='a8fbe269d3941706a510796963f059d7404f3f4655a6a3163042e85011aa0d45'
OFFICIAL_SHA='b2c1c52931e813dd63fb0e98edfc90088bc2eca497fd9142277e748f0935a82f'

def dot(x,y):return sum((a*b for a,b in zip(x,y)),F(0))
def encode(x):
    if isinstance(x,F):return str(x)
    if isinstance(x,(list,tuple)):return [encode(v) for v in x]
    if isinstance(x,dict):return {k:encode(v) for k,v in x.items()}
    return x

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def load_inputs(saved,official):
    assert digest(saved)==SAVED_SHA,'immutable saved input identity'
    assert digest(official)==OFFICIAL_SHA,'official M0475 source identity'
    old=json.loads(saved.read_text());assert old['source_sha256']==OFFICIAL_SHA
    return old

def cubic(a):return (a[0],a[1]-a[0],a[2]-a[1],-a[2])
def rvalue(a,z):return a[0]+a[1]*z+a[2]*z*z
def fvalue(a,mu):return (1-mu*mu)*rvalue(a,mu*mu)
def minimum(a):
    points=[F(0),F(1)]
    if a[2]>0:
        z=-a[1]/(2*a[2])
        if 0<z<1:points.append(z)
    z=min(points,key=lambda t:rvalue(a,t))
    return {'z':z,'value':rvalue(a,z),'nonnegative':rvalue(a,z)>=0}

def rows_from_saved(old):
    rows=[]
    for row in old['rows']:
        zl,zh=map(F,row['z']);lo=[zl**j*(1-zh) for j in range(3)];hi=[zh**j*(1-zl) for j in range(3)]
        m=[(l+h)/2 for l,h in zip(lo,hi)];eps=B*sum((h-l for l,h in zip(lo,hi)),F(0))/2
        rows.append({'angle':row['angle'],'z':[zl,zh],'basis_lower':lo,'basis_upper':hi,'midpoint':m,'epsilon':eps,'window':WINDOWS[row['angle']],'mu':list(map(F,row['mu'])) if 'mu' in row else None})
    return rows

def weighted(j,t):return 2*((1-t**(2*j+1))/F(2*j+1)-(1-t**(2*j+3))/F(2*j+3))
def monomial(j,t):return 2*(1-t**(2*j+1))/F(2*j+1)
def moments_from_saved(old):
    moments={'FULL':{'lower':list(D),'upper':list(D),'threshold':[F(0),F(0)]}}
    controls={}
    for name in ('HEMISPHERES','CAPS'):
        prior=old['moments_by_energy']['330'][name];pl=list(map(F,prior['lower']));ph=list(map(F,prior['upper']))
        tl=1-ph[0]/2;th=1-pl[0]/2
        assert 0<=tl<=th<=1
        l=[weighted(j,th) for j in range(3)];h=[weighted(j,tl) for j in range(3)]
        assert all(0<=x<=y for x,y in zip(l,h))
        ml=[monomial(j,th) for j in range(3)];mh=[monomial(j,tl) for j in range(3)]
        overlap=[max(x,y)<=min(u,v) for x,y,u,v in zip(pl,ml,ph,mh)]
        assert all(overlap),'old monomial threshold overlap'
        moments[name]={'lower':l,'upper':h,'threshold':[tl,th]}
        controls[name]={'old_lower':pl,'old_upper':ph,'threshold_monomial_lower':ml,'threshold_monomial_upper':mh,'overlap':overlap,'exact_equality':[x==y and u==v for x,y,u,v in zip(pl,ml,ph,mh)]}
    return moments,controls

def kinematic_control():
    a=F('3727.3794118');m=F('1875.61294500');e=F(330);s=a*a+2*a*e
    k=e*e-(a+e)**2*(s-4*m*m)/s
    assert k<0
    return {'A':a,'M':m,'e':e,'s':s,'K':k,'strictly_negative':k<0,'topology_proof':'THEORY.md'}

def matrix(rows,n,inner):
    constraints=[]
    for row in rows:
        m=row['midpoint'];eps=row['epsilon'];lo,hi=row['window'];shift=eps if inner else -eps
        constraints.extend([(tuple(m),hi-shift),(tuple(-v for v in m),-lo-shift)])
    for j in range(3):
        v=tuple(F(int(j==k)) for k in range(3));constraints.extend([(v,B),(tuple(-x for x in v),B)])
    constraints.append((tuple(-v for v in D),-DMIN))
    for k in range(n+1):
        z=F(k,n);constraints.append(((F(-1),-z,-z*z),F(0)))
    if inner:
        for k in range(n):
            l,h=F(k,n),F(k+1,n);constraints.append(((F(-1),-(l+h)/2,-l*h),F(0)))
    dedup={}
    for lhs,rhs in constraints:dedup[lhs]=min(dedup.get(lhs,rhs),rhs)
    return list(dedup),list(dedup.values())

def determinant(m):
    a,b,c=m
    return a[0]*(b[1]*c[2]-b[2]*c[1])-a[1]*(b[0]*c[2]-b[2]*c[0])+a[2]*(b[0]*c[1]-b[1]*c[0])

def solve3(m,b):
    # Exact Cramer elimination; only the prescribed active triple is solved.
    det=F(determinant(m))
    if not det:return None
    return tuple(determinant([tuple(b[i] if k==j else m[i][k] for k in range(3)) for i in range(3)])/det for j in range(3))

def inside(v,m,b):return all(dot(row,v)<=rhs for row,rhs in zip(m,b))
def enumerate_polytope(m,b):
    vertices={};singular=0;feasible=0;attempts=0
    for active in combinations(range(len(m)),3):
        attempts+=1;v=solve3([m[i] for i in active],[b[i] for i in active])
        if v is None:singular+=1;continue
        if inside(v,m,b):feasible+=1;vertices.setdefault(v,active)
    assert attempts==comb(len(m),3)
    ordered=sorted(vertices)
    return {'matrix':m,'rhs':b,'vertices':ordered,'active_bases':[vertices[v] for v in ordered], 'bases_attempted':attempts,'singular_bases':singular,'invertible_bases':attempts-singular,'feasible_bases':feasible,'unique_vertices':len(ordered),'enumeration_complete':True,'quadratic_minima':[minimum(v) for v in ordered]}

def witness(a,rows):
    den=dot(D,a);data=[]
    for row in rows:
        center=dot(row['midpoint'],a);eps=row['epsilon'];lo,hi=row['window']
        data.append({'angle':row['angle'],'value_enclosure':[center-eps,center+eps],'window':[lo,hi],'inside':lo<=center-eps and center+eps<=hi})
    mini=minimum(a)
    return {'parameters':a,'ordinary_cubic':cubic(a),'denominator':den,'denominator_floor':den>=DMIN,'box':all(abs(x)<=B for x in a),'rminimum':mini,'endpoint_values':[fvalue(a,F(-1)),fvalue(a,F(1))],'data':data,'feasible':den>=DMIN and all(abs(x)<=B for x in a) and mini['nonnegative'] and all(x['inside'] for x in data)}

def ratio(a,moment):
    den=dot(D,a);assert den>0
    lo=dot(a,[l if x>=0 else h for x,l,h in zip(a,moment['lower'],moment['upper'])]);hi=dot(a,[h if x>=0 else l for x,l,h in zip(a,moment['lower'],moment['upper'])])
    return lo/den,hi/den

def outward(x,places=12):
    scale=10**places;lower=x.numerator*scale//x.denominator;upper=-((-x.numerator*scale)//x.denominator)
    def fmt(n):return ('-' if n<0 else '')+str(abs(n)//scale)+'.'+str(abs(n)%scale).zfill(places)
    return [fmt(lower),fmt(upper)]

def objectives(inner,outer,candidate,moments):
    witnesses=list(inner['vertices'])
    if candidate['feasible']:witnesses.append(candidate['parameters'])
    assert witnesses and outer['vertices'],'nonempty required for primary success'
    result={}
    for name,moment in moments.items():
        i=[ratio(v,moment) for v in witnesses];o=[ratio(v,moment) for v in outer['vertices']]
        il=min(range(len(i)),key=lambda j:i[j][1]);ih=max(range(len(i)),key=lambda j:i[j][0]);ol=min(range(len(o)),key=lambda j:o[j][0]);oh=max(range(len(o)),key=lambda j:o[j][1])
        low,high=o[ol][0],o[oh][1]
        physical=[max(F(0),low),min(F(1),high)]
        minbr=[max(F(0),low),min(F(1),i[il][1])];maxbr=[max(F(0),i[ih][0]),min(F(1),high)]
        assert minbr[0]<=minbr[1] and maxbr[0]<=maxbr[1]
        result[name]={'raw_outer_ratio_range':[low,high],'physical_range':physical,'minimum_bracket':minbr,'maximum_bracket':maxbr,'minimum_width':minbr[1]-minbr[0],'maximum_width':maxbr[1]-maxbr[0],'inner_minimum_witness':witnesses[il],'inner_maximum_witness':witnesses[ih],'outer_lower_witness':outer['vertices'][ol],'outer_upper_witness':outer['vertices'][oh],'outward_decimal':{k:[outward(v)[0 if j==0 else 1] for j,v in enumerate(vals)] for k,vals in [('raw_outer_ratio_range',[low,high]),('physical_range',physical),('minimum_bracket',minbr),('maximum_bracket',maxbr)]}}
    return result

def containing_control(rows):
    chosen=[next(r for r in rows if r['angle']==a) for a in ('46','61','87')]
    separated=all(max(x['z'][0]-y['z'][1],y['z'][0]-x['z'][1])>=F(1,5) for x,y in combinations(chosen,2))
    assert separated and all(r['z'][1]<F(1,2) and r['window'][1]<=F(1,2) for r in chosen)
    row87=next(r for r in rows if r['angle']=='87');mu_lo,mu_hi=row87['mu'];lower=F(7,50);derivative=18*B;delta=lower/(36*B);expanded=[mu_lo-delta,mu_hi+delta];floor=lower*lower/(36*B)
    assert F(-1)<=expanded[0]<=expanded[1]<=F(1) and floor==DMIN
    return {'selected_angles':['46','61','87'],'separation_at_least':'1/5','verified':True,'lagrange_coefficient_bounds':[75,150,75],'containing_B':160,'denominator_floor_control':{'angle':'87','saved_mu':[mu_lo,mu_hi],'Lstar':lower,'derivative_bound':derivative,'delta':delta,'expanded_mu_interval':expanded,'contained_in_minus1_plus1':True,'Dmin':floor}}

def construct(old):
    rows=rows_from_saved(old);moments,compat=moments_from_saved(old);candidate=witness(CANDIDATE,rows);cases=[]
    for n in (1,4,16):
        polytopes={kind:enumerate_polytope(*matrix(rows,n,kind=='inner')) for kind in ('inner','outer')}
        for v in polytopes['inner']['vertices']:assert witness(v,rows)['feasible']
        cases.append({'N':n,'polytopes':polytopes,'objectives':objectives(polytopes['inner'],polytopes['outer'],candidate,moments)})
    nesting=[]
    for i,j in ((0,1),(1,2)):
        for kind,src,dst in (('inner',i,j),('outer',j,i)):
            p,q=cases[src]['polytopes'][kind],cases[dst]['polytopes'][kind]
            passed=all(inside(v,q['matrix'],q['rhs']) for v in p['vertices']);assert passed
            nesting.append({'kind':kind,'from_N':cases[src]['N'],'to_N':cases[dst]['N'],'checked_vertices':len(p['vertices']),'pass':passed})
    assert candidate['feasible'],'frozen candidate failed; preserve output and stop'
    curves=[{'mu':F(k,200),'dcs':fvalue(CANDIDATE,F(k,200))} for k in range(-200,201)]
    comparison=[{'N':c['N'],'endpoint_zero':c['endpoint_zero'],'objectives':c['objectives']} for c in old['cases'] if c['energy']==330]
    return {'unit':'HE-EXP-ENDPOINT-14','B':B,'D':D,'Dmin':DMIN,'source_sha256':OFFICIAL_SHA,'saved_input_sha256':SAVED_SHA,'rows':rows,'moments':moments,'threshold_compatibility':compat,'kinematic_compatibility':kinematic_control(),'containing_box_control':containing_control(rows),'candidate':candidate,'cases':cases,'nesting':nesting,'prior_quartic330':comparison,'plot':{'curve_samples':curves,'data_windows':[{'mu_interval':r['mu'],'window':WINDOWS[r['angle']],'angle':r['angle']} for r in old['rows']]},'scope':'Conditional330MeV endpoint-zero full nonnegative even-sextic; ERR-S deterministic windows; uniform azimuth; same-event union','scientific_admission':'PENDING_ROOT_INDEPENDENT_REVIEW'}
