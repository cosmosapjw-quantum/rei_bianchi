"""Independent MPFI checker for the pinned real analytic FT03 BE map.

Production Rust supplies approximate roots, boxes and arbitrary preconditioners.
This file does not call the production RHS/AD to establish any mathematical bound.
The real map fixes published binary64 parameters; physical fit error is unmeasured.
"""
import argparse
import hashlib
import json
import math
import struct
from pathlib import Path
from sage.all import RealIntervalField, matrix, vector, identity_matrix

R = RealIntervalField(200)
N = 7
I = identity_matrix(R, N)


def bits(s):
    return struct.unpack('>d', bytes.fromhex(s))[0]


def absmax(x):
    return max(abs(x.lower()), abs(x.upper()))


def upper(x):
    # JSON bounds themselves round outwards, including decimal serialization.
    a = x.upper() if hasattr(x, 'upper') else x
    f = float(a)
    return math.nextafter(f, math.inf) if R(f).lower() < a else f


def enc(x):
    lo, hi = float(x.lower()), float(x.upper())
    if R(lo).upper() > x.lower():
        lo = math.nextafter(lo, -math.inf)
    if R(hi).lower() < x.upper():
        hi = math.nextafter(hi, math.inf)
    return [lo, hi]


def outer(a, b):
    return matrix(R, N, 1, list(a)) * matrix(R, 1, N, list(b))


class J:
    """Independent second-order interval differentiation, not Rust's Jet."""
    def __init__(self, value, index=None, g=None, h=None):
        self.v = R(value)
        self.g = vector(R, N) if g is None else g
        self.h = matrix(R, N) if h is None else h
        if index is not None:
            self.g[index] = R(1)

    def __add__(self, other):
        b = other if isinstance(other, J) else J(other)
        return J(self.v+b.v, g=self.g+b.g, h=self.h+b.h)

    __radd__ = __add__

    def __neg__(self):
        return J(-self.v, g=-self.g, h=-self.h)

    def __sub__(self, other):
        return self + -(other if isinstance(other, J) else J(other))

    def __rsub__(self, other):
        return J(other)-self

    def __mul__(self, other):
        b = other if isinstance(other, J) else J(other)
        return J(self.v*b.v, g=self.g*b.v+b.g*self.v,
                 h=self.h*b.v+b.h*self.v+outer(self.g,b.g)+outer(b.g,self.g))

    __rmul__ = __mul__

    def chain(self, v, d, dd):
        return J(v, g=d*self.g, h=d*self.h+dd*outer(self.g,self.g))

    def power(self, p):
        p = R(float(p))
        assert self.v.lower() > 0, 'DOMAIN_EVENT: power'
        v = (p*self.v.log()).exp()
        return self.chain(v, p*v/self.v, p*(p-1)*v/(self.v*self.v))

    def __truediv__(self, other):
        b = other if isinstance(other, J) else J(other)
        assert not (b.v.lower() <= 0 <= b.v.upper()), 'DOMAIN_EVENT: division'
        return self * b.chain(1/b.v, -1/(b.v*b.v), 2/(b.v*b.v*b.v))

    def __rtruediv__(self, other):
        return J(other)/self

    def exp(self):
        v = self.v.exp()
        return self.chain(v, v, v)

    def log(self):
        assert self.v.lower() > 0, 'DOMAIN_EVENT: log'
        return self.chain(self.v.log(), 1/self.v, -1/(self.v*self.v))


class Model:
    def __init__(self, manifest, constants):
        self.manifest = manifest
        b = manifest['actual_center_and_model_bits']
        self.z0 = [R(bits(s)) for s in b['center_bits']]
        self.d = [R(float(d)) for d in manifest['radii']]
        self.p = [self.z0[i] + R(-self.d[i].upper(),self.d[i].upper()) for i in range(N)]
        self.nh,self.nhe,self.c,self.kb,self.ev,*rest = [R(bits(s)) for s in b['constants_bits']]
        self.chi = rest[:3]
        self.energy = rest[3:]
        self.fhe = self.nhe/self.nh
        self.sigma = [[R(bits(b['sigma_bits'][3*a+k])) for k in range(3)] for a in range(3)]
        self.da,self.b1,self.b2,self.b12 = [R(bits(constants[s])) for s in ['dr_a_bits','b1_bits','b2_bits','b12_bits']]

    def temperature(self, y):
        return (2*self.ev*y[3])/(3*self.kb*(1+self.fhe+y[0]+self.fhe*(y[1]+2*y[2])))

    def rhs(self, box):
        y = [J(v,index=i) for i,v in enumerate(box)]
        assert all(R(v).lower()>0 for v in box), 'DOMAIN_EVENT: positive state'
        assert R(box[0]).upper()<1 and (R(box[1])+R(box[2])).upper()<1, 'DOMAIN_EVENT: populations'
        t = self.temperature(y)
        assert t.v.lower()>=30000 and t.v.upper()<=110000, 'DOMAIN_EVENT: temperature'
        ne = self.nh*y[0]+self.nhe*(y[1]+2*y[2])
        lower = [self.nh*(1-y[0]),self.nhe*(1-y[1]-y[2]),self.nhe*y[1]]
        up = [self.nh*y[0],self.nhe*y[1],self.nhe*y[2]]
        al,be,kin = [],[],[]
        for a in range(3):
            l = float([315614,570670,1263030][a])/t
            if a==1:
                alpha = float(3e-14)*l.power(.654)
                g = J(float(-.654))
            else:
                u = (l/float(.522)).power(.470)
                alpha = float(2 if a==2 else 1)*float(1.269e-13)*l.power(1.503)/(1+u).power(1.923)
                g = float(-1.503)+R(float(1.923))*R(float(.470))*u/(1+u)
            beta = float([21.11,32.38,19.95][a])*t.power(-1.5)*(-l/2).exp()*l.power([-1.089,-1.146,-1.089][a])/(1+(l/float([.354,.416,.553][a])).power([.874,.987,.735][a])).power([1.101,1.056,1.275][a])
            al.append(alpha);be.append(beta);kin.append(self.kb*t*alpha*(float(1.5)+g))
        j,pd,w = [J(0) for _ in range(3)],[J(0) for _ in range(3)],J(0)
        for a in range(3):
            ci,rr = lower[a]*ne*be[a]/self.nh,up[a]*ne*al[a]/self.nh
            j[a] = ci-rr
            w = w-self.chi[a]*ci-up[a]*ne*kin[a]/(self.nh*self.ev)
            for k in range(3):
                ph = self.c*lower[a]*self.sigma[a][k]*y[4+k]
                j[a] = j[a]+ph;pd[k] = pd[k]-ph
                w = w+(self.energy[k]-self.chi[a])*ph
        for pref,b in [(self.da,self.b1),(R(float(.3))*self.da,self.b12)]:
            dr = up[1]*ne*pref*t.power(-1.5)*(-b/t).exp()/self.nh
            j[1] = j[1]-dr;w = w-dr*self.kb*b/self.ev
        return [j[0],(j[1]-j[2])/self.fhe,j[2]/self.fhe,w,*pd]

    def obs(self, box):
        y = [J(v,index=i) for i,v in enumerate(box)]
        return [y[0],y[1],y[2],self.temperature(y).log()]


def norm(m):
    return max(sum(R(absmax(m[i,j])) for j in range(N)).upper() for i in range(N))


def inverse_bound(a,c):
    b = I-c*a
    q = norm(b)
    assert q<1, 'DERIVATIVE_UNBOUNDED: Neumann contraction'
    s,t = I,I
    for _ in range(8):
        t = t*b;s = s+t
    tail = R(q)**9/(1-R(q))*R(norm(c))
    e = R(-tail.upper(),tail.upper())
    return s*c+matrix(R,N,N,[e]*(N*N)),q


def derivatives(model,box,dt,c):
    f = model.rhs(box)
    a = I-R(dt)*matrix(R,[list(j.g) for j in f])
    inv,q = inverse_bound(a,c)
    contractions = [inv.transpose()*j.h*inv for j in f]
    h = [sum((R(dt)*inv[i,k]*contractions[k] for k in range(N)),matrix(R,N)) for i in range(N)]
    return inv,h,q,f


def certify_site(model,site,parent,parent_center,parent_eta,dt):
    assert site['step_s']==dt
    y = vector(R,[R(float(v)) for v in site['center']])
    box = [R(float(a),float(b)) for a,b in site['box']]
    c = matrix(R,[[R(float(v)) for v in row] for row in site['preconditioner']])
    assert len(y)==N and len(box)==N and c.nrows()==N and c.ncols()==N
    assert all(box[i].lower()<y[i].lower()<=y[i].upper()<box[i].upper() for i in range(N)), 'ROOT_INCLUSION: centre outside box'
    f0 = model.rhs(y);f = model.rhs(box)
    a = I-R(dt)*matrix(R,[list(v.g) for v in f]);b = I-c*a
    residual = y-vector(R,parent)-R(dt)*vector(R,[v.v for v in f0])
    k = y-c*residual+b*(vector(R,box)-y)
    assert all(box[i].lower()<k[i].lower() and k[i].upper()<box[i].upper() for i in range(N)), 'ROOT_INCLUSION: K not strictly inside'
    rad = [min(y[i].lower()-box[i].lower(),box[i].upper()-y[i].upper()) for i in range(N)]
    qweighted = max(sum(R(absmax(b[i,j]))*R(rad[j])/R(rad[i]) for j in range(N)).upper() for i in range(N))
    assert qweighted<1, 'ROOT_INCLUSION: weighted contraction'
    q = norm(b);assert q<1, 'DERIVATIVE_UNBOUNDED'
    rc = y-vector(R,parent_center)-R(dt)*vector(R,[v.v for v in f0])
    delta = max((R(absmax((c*rc)[i]))+sum(R(absmax(c[i,j]))*R(parent_eta) for j in range(N))).upper() for i in range(N))
    eta = R(delta)/(1-R(q))
    ycentre = [y[i]+R(-eta.upper(),eta.upper()) for i in range(N)]
    assert all(box[i].lower()<=ycentre[i].lower() and ycentre[i].upper()<=box[i].upper() for i in range(N)), 'ROOT_INCLUSION: central error not inside'
    jac,hess,_,_ = derivatives(model,box,dt,c)
    jc,_,_,_ = derivatives(model,ycentre,dt,c)
    return {'y':y,'box':box,'jac':jac,'hess':hess,'centre_jac':jc,'eta':eta.upper(),
            'summary':{'id':site['id'],'K':[enc(v) for v in k],'q_weighted':upper(qweighted),'q_neumann':upper(q),'centre_error_bound':upper(eta),'T_range_K':enc(model.temperature([J(v) for v in box]).v)}}


def affine_observables(model,root,jac,hess,jcentre,eta):
    domain = model.obs(root['box']);centre = model.obs(root['y'])
    out = []
    for k in range(4):
        g = domain[k]
        hj = jac.transpose()*g.h*jac+sum((g.g[i]*hess[i] for i in range(N)),matrix(R,N))
        # Coefficients evaluated at the true central root, not at unvalidated Newton output.
        gc = model.obs([root['y'][i]+R(-eta,eta) for i in range(N)])[k]
        bc = gc.g*jcentre
        coeff = [float(v.center()) for v in bc]
        a = float(centre[k].v.center())
        epsa = R(absmax(centre[k].v-R(a)))+sum(R(absmax(g.g[i]))*R(eta) for i in range(N))
        epsb = [absmax(bc[i]-R(coeff[i])) for i in range(N)]
        rho = R(epsa)+sum(R(epsb[i])*model.d[i] for i in range(N))+R(.5)*sum(R(absmax(hj[i,j]))*model.d[i]*model.d[j] for i in range(N) for j in range(N))
        radius = sum(R(abs(coeff[i]))*model.d[i] for i in range(N))+rho
        out.append({'a':a,'b':coeff,'rho':upper(rho),'public_width':upper(2*radius),'eps_a':upper(epsa),'eps_b':[upper(v) for v in epsb],'M':[[upper(absmax(hj[i,j])) for j in range(N)] for i in range(N)]})
    return out


def check(candidate,manifest,constants):
    for path,expected in manifest['source_identity'].items():
        assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==expected, 'immutable source mismatch: '+path
    model = Model(manifest,constants)
    assert candidate['model_id']==manifest['model_id']
    assert candidate['parent_center_bits']==manifest['actual_center_and_model_bits']['center_bits']
    assert candidate['parent_manifest_sha256']==hashlib.sha256(Path('runs/rei_fastest_v1/map_certificate/parent_manifest.json').read_bytes()).hexdigest()
    assert [s['id'] for s in candidate['sites']]==manifest['source_sites']
    dt = manifest['fixed_model_inputs']['step_h_s']
    full = certify_site(model,candidate['sites'][0],model.p,model.z0,0,dt)
    h1 = certify_site(model,candidate['sites'][1],model.p,model.z0,0,dt/2)
    h2 = certify_site(model,candidate['sites'][2],h1['box'],h1['y'],h1['eta'],dt/2)
    jh = h2['jac']*h1['jac']
    hh = [h1['jac'].transpose()*h2['hess'][i]*h1['jac']+sum((h2['jac'][i,j]*h1['hess'][j] for j in range(N)),matrix(R,N)) for i in range(N)]
    jhc = h2['centre_jac']*h1['centre_jac']
    of = affine_observables(model,full,full['jac'],full['hess'],full['centre_jac'],full['eta'])
    oh = affine_observables(model,h2,jh,hh,jhc,h2['eta'])
    errors = []
    for f,h in zip(of,oh):
        # Shared parent: subtract affine coefficients before bounding. Independent remainders add.
        bound = abs(R(f['a'])-R(h['a']))+sum(abs(R(f['b'][i])-R(h['b'][i]))*model.d[i] for i in range(N))+R(f['rho'])+R(h['rho'])
        errors.append(upper(bound))
    assert max(errors)<manifest['strict_local_error_limit'], 'LOCAL_ERROR'
    assert max(v['public_width'] for v in of+oh)<manifest['strict_public_width_limit'], 'PUBLIC_WIDTH'
    return {'schema':'rei.actual-map-mpfi-certificate.v1','status':'PASS','model_id':manifest['model_id'],
            'sites':[v['summary'] for v in [full,h1,h2]],'full_observables':of,'two_half_observables':oh,
            'joint_full_half_local_bounds':errors,'strict_local_limit':manifest['strict_local_error_limit'],
            'strict_public_width_limit':manifest['strict_public_width_limit'],'original_parent_variables':7,
            'half_composition':'J2 J1; H2[J1,J1]+J2 H1, original parent preserved',
            'physical_fit_error':'NOT_MEASURED','scientific_admission':'HOLD','precision_bits':200}


def main():
    a = argparse.ArgumentParser();a.add_argument('candidate');a.add_argument('--output',required=True);args=a.parse_args()
    manifest = json.loads(Path('runs/rei_fastest_v1/map_certificate/parent_manifest.json').read_text())
    for path,expected in manifest['source_identity'].items():
        assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==expected, 'immutable source mismatch: '+path
    constants = json.loads(Path('.cuh/fastest-track/REI-F04-CERT/model_constants.json').read_text())
    result = check(json.loads(Path(args.candidate).read_text()),manifest,constants)
    Path(args.output).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'site_q':[v['q_weighted'] for v in result['sites']],
                      'local_bounds':result['joint_full_half_local_bounds'],'max_width':max(v['public_width'] for v in result['full_observables']+result['two_half_observables']),
                      'scope':'Actual static FT03 numerical domain only','scientific_admission':'HOLD'}))


if __name__=='__main__':
    main()
