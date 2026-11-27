"""EXFOR11 exact finite-family sensitivity certificates; no calculations on import."""
from fractions import Fraction as F
from functools import lru_cache
from itertools import combinations
from math import comb
from pathlib import Path
import hashlib
import importlib.util
import sys

ROOT=Path(__file__).resolve().parents[1]
PARENT=ROOT.parent/'continuation_harmonic_20261028/src/harmonic.py'
spec=importlib.util.spec_from_file_location('_exfor11_harmonic',PARENT)
H=importlib.util.module_from_spec(spec);sys.modules[spec.name]=H;spec.loader.exec_module(H)
ContractError=H.ContractError
SOURCE_SHA='b2c1c52931e813dd63fb0e98edfc90088bc2eca497fd9142277e748f0935a82f'
ANGLES=(46,61,73,87)
LITERALS=((213,'0.22','0.04','0.35','0.09','0.41','0.09','0.54','0.1'),(258,'0.08','0.03','0.23','0.08','0.16','0.07','0.25','0.07'),(330,'0.14','0.03','0.16','0.05','0.07','0.05','0.19','0.05'))
TOTALS=((201,'2.41','0.32'),(225,'1.29','0.23'),(253,'0.92','0.20'),(285,'1.04','0.20'),(320,'0.61','0.16'),(359,'0.55','0.15'))

def rational(x):
    if isinstance(x,bool) or not isinstance(x,(int,str,F)):raise ContractError('exact int/string/Fraction required; floats forbidden')
    try:return F(x)
    except (ValueError,ZeroDivisionError) as exc:raise ContractError('invalid rational') from exc

def dot(a,b):return sum((x*y for x,y in zip(a,b)),F(0))

def sensitivity(y,error):
    y,error=rational(y),rational(error)
    if y<0 or error<0:raise ContractError('nonnegative data and error required')
    return max(F(0),y-error),y+error

def parse_source(path):
    raw=Path(path).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=SOURCE_SHA:raise ContractError('immutable source identity differs')
    tables={};section=None;active=False
    for line in raw.decode('ascii').splitlines():
        if line.startswith('SUBENT'):section=line.split()[1]
        if line.startswith('DATA '):active=True;tables[section]=[];continue
        if line.startswith('ENDDATA'):active=False
        if active and line.strip() and line.lstrip()[0].isdigit():tables[section].append(tuple(F(t) for t in line.split()))
    expected=[(F(e),F(t),F(vals[2*i]),F(vals[2*i+1])) for e,*vals in LITERALS for i,t in enumerate(ANGLES)]
    if tables.get('M0475002')!=expected or tables.get('M0475003')!=[tuple(F(v) for v in r) for r in TOTALS]:raise ContractError('literal tables differ')
    if {r[0] for r in expected}&{r[0] for r in tables['M0475003']}:raise ContractError('energy join forbidden')
    return tables

class EvenBasis:
    def __init__(self,n,endpoint_zero=False):
        if type(n)!=int or n not in (4,8) or type(endpoint_zero)!=bool:raise ContractError('degree 4/8 and boolean endpoint assumption required')
        self.n=n;self.endpoint_zero=endpoint_zero;self.indices=tuple(range(int(endpoint_zero),n//2+1))
        self.d=tuple(F(2 if j==n//2 else 4,n+1) for j in self.indices)
        self.power=tuple(H._power(tuple(F(int(k==j or (j<n//2 and k==n-j))) for k in range(n+1))) for j in self.indices)
    def value(self,mu):
        mu=rational(mu)
        if not -1<=mu<=1:raise ContractError('mu outside physical interval')
        x=(mu+1)/2
        return tuple(sum((comb(self.n,k)*x**k*(1-x)**(self.n-k) for k in ({j,self.n-j})),F(0)) for j in self.indices)
    def integrate(self,intervals):
        intervals=tuple((rational(l),rational(h)) for l,h in intervals)
        if any(not -1<=l<=h<=1 for l,h in intervals) or any(intervals[i][1]>intervals[i+1][0] for i in range(len(intervals)-1)):raise ContractError('ordered disjoint physical intervals required')
        return tuple(sum((sum((p[k]*(h**(k+1)-l**(k+1))/(k+1) for k in range(len(p))),F(0)) for l,h in intervals),F(0)) for p in self.power)
    def row(self,theta):
        theta=rational(theta)
        if not 0<=theta<=180:raise ContractError('angle outside [0,180]')
        mu=H.sincos_turn(theta/720)[1];x=(mu+1)/2;one=H.Interval.point(1)-x
        def power(v,k):
            out=H.Interval.point(1)
            for _ in range(k):out=out*v
            return out
        out=[]
        for j in self.indices:
            val=H.Interval.point(0)
            for k in {j,self.n-j}:val=val+comb(self.n,k)*power(x,k)*power(one,self.n-k)
            out.append((max(F(0),H.floor_grid(val.lower,60)),H.ceil_grid(val.upper,60)))
        return tuple(out)

def constraints(rows,bounds,kind):
    if kind not in ('inner','outer'):raise ContractError('polytope kind required')
    dimension=len(rows[0]);matrix=[];rhs=[]
    for row,(L,U) in zip(rows,bounds):
        l=tuple(v[0] for v in row);u=tuple(v[1] for v in row)
        matrix.extend((u if kind=='inner' else l,tuple(-v for v in (l if kind=='inner' else u))));rhs.extend((U,-L))
    for j in range(dimension):matrix.append(tuple(F(-int(j==k)) for k in range(dimension)));rhs.append(F(0))
    return tuple(matrix),tuple(rhs)

def inverse(matrix):
    n=len(matrix);a=[list(row)+[F(int(i==j)) for j in range(n)] for i,row in enumerate(matrix)]
    for k in range(n):
        pivot=next((i for i in range(k,n) if a[i][k]),None)
        if pivot is None:return None
        a[k],a[pivot]=a[pivot],a[k];p=a[k][k];a[k]=[v/p for v in a[k]]
        for i in range(n):
            if i!=k and a[i][k]:
                p=a[i][k];a[i]=[x-p*y for x,y in zip(a[i],a[k])]
    return tuple(tuple(row[n:]) for row in a)

def enumerate_energies(matrix,right_sides):
    """Enumerate every basis, sharing each inverse across energy RHS vectors."""
    n=len(matrix[0]);vertices=[set() for _ in right_sides];feasible=[0]*len(right_sides);attempted=singular=0
    for active in combinations(range(len(matrix)),n):
        attempted+=1;inv=inverse(tuple(matrix[i] for i in active))
        if inv is None:singular+=1;continue
        for j,rhs in enumerate(right_sides):
            b=tuple(rhs[i] for i in active);v=tuple(dot(row,b) for row in inv)
            if all(dot(row,v)<=bound for row,bound in zip(matrix,rhs)):vertices[j].add(v);feasible[j]+=1
    return [dict(vertices=sorted(v),bases_attempted=attempted,singular_bases=singular,feasible_bases=f,unique_vertices=len(v)) for v,f in zip(vertices,feasible)]

def ratio_extrema(vertices,lower,upper,d):
    if not vertices:return dict(status='EMPTY',lower=None,upper=None,lower_witness=None,upper_witness=None)
    if any(dot(d,v)<=0 for v in vertices):raise ContractError('positive denominator required')
    lo=min(vertices,key=lambda v:dot(lower,v)/dot(d,v));hi=max(vertices,key=lambda v:dot(upper,v)/dot(d,v))
    return dict(status='CERTIFIED_ENCLOSURE',lower=dot(lower,lo)/dot(d,lo),upper=dot(upper,hi)/dot(d,hi),lower_witness=lo,upper_witness=hi)

def geometry_coefficients(basis,strips):
    lower=[F(0)]*len(basis.d);upper=lower.copy()
    for strip in strips:
        l,h=strip['interval'];sets=strip['sets']['coincidence']
        for target,region in ((lower,sets.inner),(upper,sets.outer)):
            for j,v in enumerate(basis.integrate(region)):target[j]+=(h-l)*v
    if any(not 0<=l<=u<=d for l,u,d in zip(lower,upper,basis.d)):raise ContractError('geometry coefficient enclosure violated')
    return tuple(lower),tuple(upper)

def geometries(energy):
    energy=rational(energy)
    model=H.PhysicalAngularMap(F('3727.3794118'),F('1875.61294500'),energy)
    result={}
    for name,a,b in [('FULL',(-1,1),(-1,1)),('HEMISPHERES',(0,1),(-1,0)),('CAPS',(F(1,2),1),(-1,F(-1,2)))]:
        da=H.FiniteDetector((H.DetectorPatch(a,(0,1)),));db=H.FiniteDetector((H.DetectorPatch(b,(0,1)),))
        geo=H._Z.azimuth_pair_response(model,H.BernsteinDensity((1,)),da,db,azimuth_law='UNIFORM_DECLARED',delta=F(1,2**48))
        result[name]=geo['strips']
    return result

def campaign(source):
    tables=parse_source(source);energies=(213,258,330);geo={e:geometries(e) for e in energies};cases=[]
    for n in (4,8):
        for endpoint in (False,True):
            basis=EvenBasis(n,endpoint);rows=tuple(basis.row(t) for t in ANGLES)
            bounds=[tuple(sensitivity(r[2],r[3]) for r in tables['M0475002'] if r[0]==e) for e in energies]
            if any(l<=0 for row in rows for l,u in row) or any(not any(L>0 for L,U in b) for b in bounds):raise ContractError('boundedness and nonzero-normalization obligations violated')
            polytopes={}
            for kind in ('inner','outer'):
                pairs=[constraints(rows,b,kind) for b in bounds];matrix=pairs[0][0]
                polytopes[kind]=[(matrix,p[1],v) for p,v in zip(pairs,enumerate_energies(matrix,[p[1] for p in pairs]))]
            for i,e in enumerate(energies):
                objectives={name:geometry_coefficients(basis,s) for name,s in geo[e].items()};case=dict(energy=e,degree=n,endpoint_zero=endpoint,rows=rows,d=basis.d,bounds=bounds[i],coordinate_bounds=tuple(min(U/row[j][0] for row,(L,U) in zip(rows,bounds[i])) for j in range(len(basis.d))),polytopes={},objectives={})
                for kind in ('inner','outer'):
                    matrix,rhs,v=polytopes[kind][i];case['polytopes'][kind]=dict(matrix=matrix,rhs=rhs,**v)
                for name,(lo,hi) in objectives.items():case['objectives'][name]=dict(c_lower=lo,c_upper=hi,coefficient_width=tuple(u-l for l,u in zip(lo,hi)),**{kind:ratio_extrema(case['polytopes'][kind]['vertices'],lo,hi,basis.d) for kind in ('inner','outer')})
                case['human_readable_floats']={name:{kind:{key:float(obj[kind][key]) if obj[kind][key] is not None else None for key in ('lower','upper')} for kind in ('inner','outer')} for name,obj in case['objectives'].items()}
                cases.append(case)
    return dict(unit='HE-EXP-EXFOR-11',azimuth_law='DECLARED_AZIMUTH_UNIFORM',error_scope='literal ERR-S sensitivity window; not confidence',source_sha256=SOURCE_SHA,dcs=tables['M0475002'],totals=tables['M0475003'],cases=cases)

def encode(value):
    if isinstance(value,F):return str(value)
    if isinstance(value,dict):return {k:encode(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):return [encode(v) for v in value]
    return value
