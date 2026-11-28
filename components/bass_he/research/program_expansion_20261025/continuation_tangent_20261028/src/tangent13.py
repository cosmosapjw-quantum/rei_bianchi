"""Frozen TANGENT13 construction. Standard-library exact arithmetic; inert import."""
from fractions import Fraction as Q
import hashlib
import json
import math

INPUT_SHA = 'a8fbe269d3941706a510796963f059d7404f3f4655a6a3163042e85011aa0d45'
SOURCE_SHA = 'b2c1c52931e813dd63fb0e98edfc90088bc2eca497fd9142277e748f0935a82f'

def require(ok, reason):
    if not ok:
        raise ValueError(reason)

def vec(x):
    return [Q(v) for v in x]

def dot(x,y):
    return sum((a*b for a,b in zip(x,y)),Q(0))

def load_inputs(saved, source):
    raw=saved.read_bytes(); official=source.read_bytes()
    require(hashlib.sha256(raw).hexdigest()==INPUT_SHA, 'saved input SHA256 mismatch')
    require(hashlib.sha256(official).hexdigest()==SOURCE_SHA, 'official source SHA256 mismatch')
    a=json.loads(raw)
    c=[c for c in a['cases'] if c['energy']==258 and c['case']=='free_N16']
    require(len(c)==1 and c[0]['N']==16 and not c[0]['endpoint_zero'], 'fixed case missing')
    require(a['B']=='160' and a['D']==['2','2/3','2/5'] and a['Dmin']=='49/4800000','normalization mismatch')
    rows={r['angle']:r for r in a['rows']}
    require(set(rows)=={'46','61','73','87'},'four nominal rows required')
    windows={r[1]:[Q(r[2])-Q(r[3]),Q(r[2])+Q(r[3])] for r in a['dcs'] if r[0]=='258'}
    expected={'46':vec(['.05','.11']),'61':vec(['.15','.31']),'73':vec(['.09','.23']),'87':vec(['.18','.32'])}
    require(windows==expected,'fixed sensitivity windows mismatch')
    return a,c[0],rows,windows

def polynomial(m61,m73,L,U):
    # Ascending coefficients of U*w61-L*w73.
    return [U*m61[2]-L*m73[2], -2*U*m61[1]+2*L*m73[1], U-L]

def evaluate(p,r):
    return p[0]+r*(p[1]+r*p[2])

def isolate(p,steps=80):
    lo,hi=Q(4,5),Q(9,10)
    require(evaluate(p,lo)<0<evaluate(p,hi),'invalid root bracket signs')
    deriv=[p[1]+2*p[2]*t for t in (lo,hi)]
    require(min(deriv)>0,'root derivative not positive on declared interval')
    for i in range(steps):
        mid=(lo+hi)/2; f=evaluate(p,mid)
        if f==0:
            return {'bracket':[mid,mid],'bisections':i+1,'exact_root':True,'initial_derivative_endpoints':deriv}
        if f<0: lo=mid
        else: hi=mid
    return {'bracket':[lo,hi],'bisections':steps,'exact_root':False,'initial_derivative_endpoints':deriv}

def solve3(matrix,rhs):
    a=[list(row)+[b] for row,b in zip(matrix,rhs)]
    for j in range(3):
        pivot=next((i for i in range(j,3) if a[i][j]),None)
        require(pivot is not None,'singular dual system')
        a[j],a[pivot]=a[pivot],a[j]
        d=a[j][j]; a[j]=[v/d for v in a[j]]
        for i in range(3):
            if i!=j:
                d=a[i][j];a[i]=[x-d*y for x,y in zip(a[i],a[j])]
    x=[a[i][3] for i in range(3)]
    require([dot(row,x) for row in matrix]==rhs,'linear elimination residual')
    return x

def dual(k,d,h,r):
    v=[Q(1),r,r*r]
    alpha,lam,mu=solve3([[d[i],h[i],v[i]] for i in range(3)],k)
    require(lam>=0 and mu>=0,'negative dual multiplier')
    residual=[k[i]-alpha*d[i]-lam*h[i]-mu*v[i] for i in range(3)]
    require(residual==[0,0,0],'dual identity residual')
    return {'alpha':alpha,'lambda':lam,'mu':mu,'residual':residual}

def signed_ratio(b,lower,upper,d):
    D=dot(d,b);require(D>0,'nonpositive denominator')
    return [sum((b[i]*(lower[i] if b[i]>=0 else upper[i]) for i in range(3)),Q(0))/D,
            sum((b[i]*(upper[i] if b[i]>=0 else lower[i]) for i in range(3)),Q(0))/D]

def outward(x,up):
    f=float(x)
    while (Q.from_float(f)<x if up else Q.from_float(f)>x):
        f=math.nextafter(f,math.inf if up else -math.inf)
    return f

def outward_decimal(x,up,places=16):
    """Fixed decimal grid floor/ceiling; independent of binary64 formatting."""
    scale=10**places
    numerator=x.numerator*scale
    integer=-((-numerator)//x.denominator) if up else numerator//x.denominator
    sign='-' if integer<0 else ''
    whole,tail=divmod(abs(integer),scale)
    return sign+str(whole)+'.'+str(tail).zfill(places)

def serialize(o):
    if isinstance(o,Q): return str(o)
    if isinstance(o,dict):return {k:serialize(v) for k,v in o.items()}
    if isinstance(o,(list,tuple)): return [serialize(v) for v in o]
    return o

def construct(saved,source):
    a,c,rows,windows=load_inputs(saved,source);d=vec(a['D'])
    m={ang:vec(row['midpoint']) for ang,row in rows.items()}
    eps={ang:Q(row['epsilon']) for ang,row in rows.items()}
    windows_outer={t:[l-eps[t],u+eps[t]] for t,(l,u) in windows.items()}
    windows_inner={t:[l+eps[t],u-eps[t]] for t,(l,u) in windows.items()}
    roots={}
    for name,w in [('outer',windows_outer),('inner',windows_inner)]:
        p=polynomial(m['61'],m['73'],w['61'][0],w['73'][1]); roots[name]={'polynomial':p,**isolate(p)}
    rout=sum(roots['outer']['bracket'],Q(0))/2;rin=roots['inner']['bracket'][1]
    w=lambda row,r:r*r-2*row[1]*r+row[2]
    w61,w73=w(m['61'],rin),w(m['73'],rin)
    require(w61>0 and w73>0,'nonpositive witness scale denominator')
    scale=[windows_inner['61'][0]/w61,windows_inner['73'][1]/w73]
    require(scale[0]<=scale[1],'empty witness scale interval')
    av=sum(scale,Q(0))/2;b=[av*rin*rin,-2*av*rin,av];D=dot(d,b)
    require(av>0 and 0<=rin<=1 and all(abs(x)<=160 for x in b) and D>=Q(a['Dmin']),'square witness parameter bounds')
    data=[]
    for t in ['46','61','73','87']:
        z=dot(m[t],b);lo,hi=windows_inner[t]
        require(lo<=z<=hi,'square witness contracted data violation '+t)
        data.append({'angle':t,'midpoint_value':z,'contracted_window':[lo,hi],'true_value_enclosure':[z-eps[t],z+eps[t]]})
    poly=c['polytopes']['outer'];vertices=[vec(v) for v in poly['vertices']]
    matrix=[vec(v) for v in poly['matrix']];rhs=vec(poly['rhs'])
    require(len(vertices)==poly['unique_vertices'] and len(matrix)==len(rhs),'saved outer shape mismatch')
    for v in vertices:
        require(dot(d,v)>0,'saved outer denominator nonpositive')
        require(all(dot(row,v)<=r for row,r in zip(matrix,rhs)),'saved outer vertex constraint violation')
    M=[max(abs(v[j])/dot(d,v) for v in vertices) for j in range(3)]
    maximizers=[[i for i,v in enumerate(vertices) if abs(v[j])/dot(d,v)==M[j]] for j in range(3)]
    h=[m['61'][j]-windows_outer['61'][0]/windows_outer['73'][1]*m['73'][j] for j in range(3)]
    objects={}
    for geom in ['HEMISPHERES','CAPS']:
        moment=a['moments_by_energy']['258'][geom];kl,ku=vec(moment['lower']),vec(moment['upper']);km=[(l+u)/2 for l,u in zip(kl,ku)]
        cert=dual(km,d,h,rout);delta=sum((M[j]*(ku[j]-kl[j])/2 for j in range(3)),Q(0))
        interval=signed_ratio(b,kl,ku,d);bounds=[max(Q(0),cert['alpha']-delta),min(Q(1),interval[1])]
        prior=vec(c['objectives'][geom]['minimum_bracket']);width=bounds[1]-bounds[0]
        require(0<=width<=Q(1,10**10),'minimum bracket target violation '+geom)
        require(prior[0]<=bounds[0]<=bounds[1]<=prior[1],'predecessor inclusion violation '+geom)
        objects[geom]={'moment_lower':kl,'moment_upper':ku,'moment_midpoint':km,'dual':cert,'Delta_k':delta,'witness_ratio':interval,'minimum_bracket':bounds,'width':width,'display_width_float':float(width),'predecessor_minimum_bracket':prior,'outward_decimal_endpoints':[outward_decimal(bounds[0],False),outward_decimal(bounds[1],True)],'outward_float_bracket':[outward(bounds[0],False),outward(bounds[1],True)]}
    return serialize({'unit':'HE-EXP-TANGENT-13','energy_MeV':258,'case':'free_N16','source_identities':{'saved_sha256':INPUT_SHA,'official_sha256':SOURCE_SHA},'D':d,'Dmin':Q(a['Dmin']),'B':Q(a['B']),'rows':rows,'windows':windows,'outer_windows':windows_outer,'inner_windows':windows_inner,'root_isolation':roots,'r_out':rout,'r_in':rin,'h':h,'square_witness':{'a':av,'r':rin,'scale_interval':scale,'coefficients':b,'denominator':D,'data':data},'normalized_envelope':{'M':M,'maximizer_indices':maximizers,'vertices':vertices,'matrix':matrix,'rhs':rhs,'enumeration_reused':True},'objectives':objects,'scope':'Global minima within full nonnegative even quartic and fixed deterministic coordinate ERR-S windows; no physical production admission.'})
