from warm_interval import *
import json,sys

def export(r):
    return {'gas':[[record(x) for x in j.c] for j in r['gas']],
            'photon':[[record(x) for x in j.c] for j in r['photon']],
            'env':{k:[record(x) for x in v.c] for k,v in r['env'].items()},
            'nodes':[{k:([record(x) for x in v] if k=='sigma' else record(v)) for k,v in node.items()} for node in r['nodes']],
            'gamma':[[record(x) for x in j.c] for j in r['gamma']],
            'qphoto':[[record(x) for x in j.c] for j in r['qphoto']],
            'seconds':r['seconds']}
if __name__=='__main__':
    kind=sys.argv[1] if len(sys.argv)>1 else 'mid'
    s=WarmSource();r=s.evaluate(V('.5') if kind=='mid' else bound(0,1),3,kind)
    out=export(r);out['shear_anchor']=s.shear_anchor_log
    out['stage']='HE18_C3';out['domain']='1/2' if kind=='mid' else '[0,1]';out['order']=3
    out['arithmetic']='mpmath.iv 70 decimal digits; normalized Taylor derivatives, NOT sampled suprema'
    p=ROOT/'results'/f'{kind}_jets.json';tmp=p.with_suffix('.tmp');tmp.write_text(json.dumps(out));tmp.replace(p)
    print(kind,'saved',p.stat().st_size,'gas_residual_mid_or_range',[str(j.c[0]/s.h) for j in r['gas']],flush=True)
