"""Small independent HE34-SCR theory checks; does not import author code.

No background IVP and no old HE33 suite are executed.  These finite checks
corroborate the written algebra; they do not turn binary64 into interval proof.
"""
from fractions import Fraction as F
from pathlib import Path
import hashlib
import json
import random
import xml.etree.ElementTree as ET
import mpmath as mp

ROOT = Path('/tmp/he34_scope_review')
UNIT = Path('/tmp/he32_resume_20261022/repos/BASS_HE/research/he34_sandbox_certified_relaxation_20261022')
mp.mp.dps = 80

def rational_elimination():
    rng = random.Random(340061)
    for i in range(48):
        x, y, a, b, u, r, A = [F(rng.randrange(1,31), rng.randrange(1,19)) for _ in range(7)]
        cH, cHe, co = u*(F(6,5)*A*r+2), u*(F(6,5)*A/r+2), u*(F(6,5)*A-2)
        g11, g22, g12 = x*x*a+x*y*cH, y*y*b+x*y*cHe, x*y*co
        det = g11*g22-g12*g12
        contraction = F(12,5)*A*u*u*(r+1/r+2)
        assert cH*cHe-co*co == contraction
        numerator = u*(F(6,5)*A*(x*x/r-2*x*y+y*y*r)+2*(x+y)**2)+x*y*(a+b)
        denominator = x*x*cHe*a+y*y*cH*b+x*y*(a*b+contraction)
        assert det == x*y*denominator
        assert x*x*g22-2*x*y*g12+y*y*g11 == x*y*numerator
        assert (x*x*g22-2*x*y*g12+y*y*g11)/det == numerator/denominator
        assert u*(F(6,5)*A/r+2)/(cHe*a) == 1/a
        assert u*(F(6,5)*A*r+2)/(cH*b) == 1/b
    return {'cases':48, 'arithmetic':'exact Fraction', 'identities':['determinant','quadratic form','pure endpoints'], 'passed':True}

def constant_layer_checks():
    cases = [('0','3','1','.4'),('.3','10','-.5','.1'),('-.8','.1','.4','.7'),('.25','100','.9','1'),('1e-20','1','0','2'),('.4','1e8','.8','.1')]
    rows=[]
    for s, chi, r0, h in cases:
        s, chi, r0, h = map(mp.mpf,(s,chi,r0,h))
        D=mp.sqrt(chi*chi+4*chi*s+36*s*s)
        b=-4*s/(chi+2*s+D)
        delta0=r0-b
        c=4*s*delta0/D
        den=1-c*(-mp.expm1(-D*h))
        candidate=b+delta0*mp.exp(-D*h)/den
        u_candidate=-4*s*b*h+mp.log(den)
        # This independently evolves the two expansion-factored eigenpressures.
        M=mp.matrix([[2*s-chi/3,chi/3],[2*chi/3,-4*s-2*chi/3]])
        state=mp.expm(h*M)*mp.matrix([1-r0,1+2*r0])
        p=(2*state[0]+state[1])/3
        q=(state[1]-state[0])/3
        exact_r=q/p
        exact_u=mp.log(p)
        er, eu=abs(candidate-exact_r),abs(u_candidate-exact_u)
        assert er<mp.mpf('1e-65') and eu<mp.mpf('1e-65')
        rows.append({'S':str(s),'chi':str(chi),'r0':str(r0),'h':str(h),'ratio_abs':str(er),'u_abs':str(eu),'positive_eigenpressures':all(t>=0 for t in state),'formula_cone': bool(-mp.mpf('.5')<=candidate<=1)})
    return {'precision_decimal_digits':mp.mp.dps,'reference':'mpmath matrix exponential of independent eigenpressure generator','cases':rows}

def data_checks():
    source=Path('/tmp/he34_transport_sources/upstream/collisions.xml')
    data_path=UNIT/'data/NEUTRAL_H_HE_TRANSPORT_SUBSET.json'
    data=json.loads(data_path.read_text())
    xml=ET.fromstring(source.read_text())
    rows=[]
    for row in data['fits']:
        pair=next(p for p in xml.iter('pair') if (p.attrib.get('s1'),p.attrib.get('s2'))==tuple(row['pair']))
        elem=pair.find(row['kind'])
        source_coeffs=list(map(mp.mpf,elem.text.split()))
        input_coeffs=list(map(lambda x:mp.mpf(str(x)),row['coefficients']))
        assert source_coeffs==input_coeffs
        vals={}
        for T in ['50','300','20000','50000']:
            z=mp.log(mp.mpf(T)); a=source_coeffs
            e1=mp.exp((z-a[2])/a[3]); e2=mp.exp((z-a[5])/a[6])
            raw=(a[0]+a[1]*z)*e1/(e1+1/e1)+a[4]*e2/(e2+1/e2)
            Q=mp.pi*mp.mpf('1e-20')*raw
            assert Q>0
            vals[T]=str(Q)
        rows.append({'pair':row['pair'],'kind':row['kind'],'source_coefficients_equal':True,'Qbar_m2':vals})
    blob=hashlib.sha1(b'blob '+str(len(source.read_bytes())).encode()+b'\0'+source.read_bytes()).hexdigest()
    assert blob==data['upstream']['blob']
    return {'json_sha256':hashlib.sha256(data_path.read_bytes()).hexdigest(),'xml_git_blob':blob,'rows':rows}

if __name__=='__main__':
    results={'unit':'HE34-SCR','physics_checks':{'viscosity':rational_elimination(),'constant_layer':constant_layer_checks(),'data':data_checks()},'old_HE32_background_runs':0,'old_HE33_test_runs':0}
    (ROOT/'INDEPENDENT_CHECKS.json').write_text(json.dumps(results,indent=2)+'\n')
    print(json.dumps(results,indent=2))
