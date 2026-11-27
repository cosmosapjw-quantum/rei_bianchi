"""Saved-certificate reader: algebra/inequalities only, no search or optimizer."""
from fractions import Fraction
import hashlib
import json

def verify(c,saved_path,official_path):
    F=Fraction
    def check(value,why):
        if not value: raise ValueError('certificate reader: '+why)
    def vv(xs):return list(map(F,xs))
    def scalar(x,y):return sum((a*b for a,b in zip(x,y)),F(0))
    def poly(p,r):return F(p[0])+F(p[1])*r+F(p[2])*r*r
    raw=saved_path.read_bytes();src=official_path.read_bytes()
    check(hashlib.sha256(raw).hexdigest()=='a8fbe269d3941706a510796963f059d7404f3f4655a6a3163042e85011aa0d45','saved identity')
    check(hashlib.sha256(src).hexdigest()=='b2c1c52931e813dd63fb0e98edfc90088bc2eca497fd9142277e748f0935a82f','official identity')
    source=json.loads(raw);case=next(x for x in source['cases'] if x['energy']==258 and x['case']=='free_N16')
    check(c['energy_MeV']==258 and c['case']=='free_N16','fixed case')
    check(c['source_identities']=={'saved_sha256':hashlib.sha256(raw).hexdigest(),'official_sha256':hashlib.sha256(src).hexdigest()},'source identities')
    check(c['rows']=={r['angle']:r for r in source['rows']},'row binding')
    d=vv(c['D']);check(d==vv(source['D']) and F(c['Dmin'])==F(source['Dmin']) and F(c['B'])==160,'normalization binding')
    check(c['windows']=={'46':['1/20','11/100'],'61':['3/20','31/100'],'73':['9/100','23/100'],'87':['9/50','8/25']},'windows')
    rows={t:vv(r['midpoint']) for t,r in c['rows'].items()};errors={t:F(r['epsilon']) for t,r in c['rows'].items()}
    for mode,sign in [('outer',-1),('inner',1)]:
        windows=c[mode+'_windows']
        for t,(lo,hi) in c['windows'].items():
            check(vv(windows[t])==[F(lo)+sign*errors[t],F(hi)-sign*errors[t]],'window rounding '+mode)
        L=F(windows['61'][0]);U=F(windows['73'][1]);p=c['root_isolation'][mode]['polynomial']
        check(vv(p)==[U*rows['61'][2]-L*rows['73'][2],-2*U*rows['61'][1]+2*L*rows['73'][1],U-L],'root polynomial')
        r=c['root_isolation'][mode];lo,hi=vv(r['bracket'])
        check(F(4,5)<=lo<=hi<=F(9,10),'root location')
        check(poly(p,F(4,5))<0<poly(p,F(9,10)),'initial signs')
        derivative=[F(p[1])+2*F(p[2])*t for t in (F(4,5),F(9,10))]
        check(min(derivative)>0 and vv(r['initial_derivative_endpoints'])==derivative,'root monotonicity')
        check(poly(p,lo)<=0<=poly(p,hi),'root enclosure')
        if r['exact_root']:
            check(lo==hi and poly(p,lo)==0 and 1<=r['bisections']<=80,'exact-root termination')
        else:
            check(r['bisections']==80 and hi-lo==F(1,10*2**80),'80-step width')
    rout=F(c['r_out']);rin=F(c['r_in'])
    check(rout==sum(vv(c['root_isolation']['outer']['bracket']),F(0))/2,'outer midpoint')
    check(rin==F(c['root_isolation']['inner']['bracket'][1]),'inner upper endpoint')
    h=vv(c['h']);check(h==[rows['61'][j]-F(c['outer_windows']['61'][0])/F(c['outer_windows']['73'][1])*rows['73'][j] for j in range(3)],'dual data combination')
    w=c['square_witness'];a=F(w['a']);b=vv(w['coefficients']);den=scalar(d,b)
    check(a>0 and 0<=rin<=1 and F(w['r'])==rin,'square parameters')
    check(b==[a*rin*rin,-2*a*rin,a] and all(abs(x)<=160 for x in b),'square identity and bounds')
    check(den==F(w['denominator']) and den>=F(c['Dmin']),'witness denominator')
    wc=[rin*rin-2*rows[t][1]*rin+rows[t][2] for t in ('61','73')]
    check(min(wc)>0,'scale denominator')
    scale=[F(c['inner_windows']['61'][0])/wc[0],F(c['inner_windows']['73'][1])/wc[1]]
    check(vv(w['scale_interval'])==scale and scale[0]<=scale[1] and a==sum(scale,F(0))/2,'scale interval')
    check(len(w['data'])==4 and {rec['angle'] for rec in w['data']}==set(rows),'witness data shape')
    for rec in w['data']:
        t=rec['angle'];z=scalar(rows[t],b);lo,hi=vv(c['inner_windows'][t])
        check(lo<=z<=hi and F(rec['midpoint_value'])==z and vv(rec['contracted_window'])==[lo,hi],'all contracted windows')
        check(vv(rec['true_value_enclosure'])==[z-errors[t],z+errors[t]],'true row enclosure')
        lower,upper=vv(c['windows'][t]);check(lower<=z-errors[t]<=z+errors[t]<=upper,'all true windows')
    env=c['normalized_envelope'];old=case['polytopes']['outer']
    for key in ('vertices','matrix','rhs'):check(env[key]==old[key],'inherited outer '+key)
    verts=list(map(vv,env['vertices']));matrix=list(map(vv,env['matrix']));rhs=vv(env['rhs']);M=vv(env['M'])
    check(len(verts)==old['unique_vertices'],'vertex count')
    for v in verts:
        check(scalar(d,v)>0 and all(scalar(row,v)<=r for row,r in zip(matrix,rhs)),'outer vertex validity')
    for j in range(3):
        ratios=[abs(v[j])/scalar(d,v) for v in verts]
        check(M[j]==max(ratios) and env['maximizer_indices'][j]==[i for i,x in enumerate(ratios) if x==M[j]],'normalized envelope')
    check(set(c['objectives'])=={'HEMISPHERES','CAPS'},'geometry scope')
    for geom,o in c['objectives'].items():
        moment=source['moments_by_energy']['258'][geom]
        check(o['moment_lower']==moment['lower'] and o['moment_upper']==moment['upper'],'moment binding')
        kl,ku=vv(o['moment_lower']),vv(o['moment_upper']);km=[(l+u)/2 for l,u in zip(kl,ku)]
        check(vv(o['moment_midpoint'])==km,'moment midpoint')
        q=o['dual'];alpha,lam,mu=map(F,(q['alpha'],q['lambda'],q['mu']))
        check(lam>=0 and mu>=0,'dual multiplier sign')
        residual=[km[j]-alpha*d[j]-lam*h[j]-mu*[1,rout,rout*rout][j] for j in range(3)]
        check(residual==[0,0,0] and vv(q['residual'])==residual,'exact dual identity')
        delta=sum((M[j]*(ku[j]-kl[j])/2 for j in range(3)),F(0));check(F(o['Delta_k'])==delta,'moment envelope')
        low=sum((b[j]*(kl[j] if b[j]>=0 else ku[j]) for j in range(3)),F(0))/den
        high=sum((b[j]*(ku[j] if b[j]>=0 else kl[j]) for j in range(3)),F(0))/den
        check(vv(o['witness_ratio'])==[low,high],'signed witness objective')
        bounds=vv(o['minimum_bracket']);check(bounds==[max(F(0),alpha-delta),min(F(1),high)],'final bounds')
        width=bounds[1]-bounds[0];check(F(o['width'])==width and 0<=width<=F(1,10**10),'target width')
        prior=case['objectives'][geom]['minimum_bracket'];check(o['predecessor_minimum_bracket']==prior,'predecessor binding')
        pl,pu=vv(prior);check(pl<=bounds[0]<=bounds[1]<=pu,'predecessor inclusion')
        fl,fu=o['outward_float_bracket'];check(F.from_float(fl)<=bounds[0]<=bounds[1]<=F.from_float(fu),'outward float')
        decimal_lower,decimal_upper=map(F,o['outward_decimal_endpoints'])
        check(decimal_lower<=bounds[0]<=bounds[1]<=decimal_upper,'outward decimal strings')
    return {'status':'PASS','method':'independent saved-certificate exact algebra and inequalities; no candidate search','geometries':['HEMISPHERES','CAPS']}
