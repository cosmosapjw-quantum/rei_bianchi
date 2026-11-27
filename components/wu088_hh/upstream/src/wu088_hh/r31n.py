"""R31N source-bound helpers for mixed O/D, independent dotO, and provider census."""
from __future__ import annotations
import math
import numpy as np

LD=np.longdouble
CD=np.clongdouble
REG=[(0,j) for j in range(24)]+[(1,j) for j in range(1,24)]


def provider_plan(*,anchors,od_nodes,jvp_nodes,ionic_nodes):
    anchors=sorted({float(z) for z in anchors})
    for name,nodes in [('od',od_nodes),('jvp',jvp_nodes),('ionic',ionic_nodes)]:
        vals={float(z) for z in nodes}
        if any(not math.isfinite(z) for z in vals): raise ValueError(f'nonfinite {name} node')
    return {
        'anchors':anchors,
        'missing_od':[int(z) if z.is_integer() else z for z in anchors if z not in {float(x) for x in od_nodes}],
        'missing_jvp':[int(z) if z.is_integer() else z for z in anchors if z not in {float(x) for x in jvp_nodes}],
        'missing_ionic':[int(z) if z.is_integer() else z for z in anchors if z not in {float(x) for x in ionic_nodes}],
    }


def interpolate_pair_costs(lo,hi,w):
    w=float(w)
    if not math.isfinite(w) or not 0<=w<=1: raise ValueError('invalid interpolation weight')
    if set(lo)!=set(hi): raise ValueError('pair cost keys differ')
    out={}
    for k in sorted(lo):
        a=float(lo[k]);b=float(hi[k])
        if not math.isfinite(a) or not math.isfinite(b) or a<=0 or b<=0: raise ValueError('invalid pair cost')
        out[k]=(1-w)*a+w*b
    return out


def jvp_assemble(raw,d,z):
    raw=np.asarray(raw)
    if raw.shape!=(2,2,3,12,12): raise ValueError('JVP raw shape')
    z=LD(z);v=LD(d['v']);tau=z/v
    O=np.empty((47,2),CD);dot=np.empty((47,2),CD)
    for ch,(active,j) in enumerate(REG):
        angle=j//8
        coeff=np.asarray(d['s_C'] if angle==0 else d['p_C'])[:,j%8].astype(LD)
        ground=np.asarray(d['s_C'])[:,0].astype(LD)
        ab=coeff[:,None]*ground[None,:]
        for cusp in (0,1):
            canonical_active=active^cusp;tab=raw[canonical_active,:,angle]
            if canonical_active: tab=tab.transpose(0,2,1)
            pair=np.sum(tab*ab[None],axis=(1,2),dtype=CD)
            parity=-1 if cusp and angle else 1
            deltaE=LD(d['phase_E'][ch])-LD(d['phase_E'][47+cusp])
            phase=np.exp(CD(1j)*(v*z/2+deltaE*tau))
            O[ch,cusp]=parity*phase*pair[0]
            dot[ch,cusp]=parity*phase*(v*pair[1]+CD(1j)*(v*v/2+deltaE)*pair[0])
    return O,dot


def od_finalize(components,d,z):
    comp=np.asarray(components)
    if comp.shape!=(3,47,2): raise ValueError('OD component shape')
    v=LD(d['v']);ks=[v/2,-v/2]
    O=np.asarray(comp[0],dtype=CD)
    Dc=np.empty((47,2),CD);Dr=np.empty((2,47),CD)
    for ch,(active,j) in enumerate(REG):
        for c in (0,1):
            kc=ks[c];ka=ks[active];kb=ks[1-active]
            G1=comp[1,ch,c];G2=comp[2,ch,c]
            Dc[ch,c]=kc*(G1+G2)+CD(1j)*(kc*(2*kc-ka-kb)-LD(d['phase_E'][47+c]))*O[ch,c]
            Dr[c,ch]=-ka*G1.conj()-kb*G2.conj()-CD(1j)*LD(d['phase_E'][ch])*O[ch,c].conj()
    return {'O':O,'O_row':O.conj().T,'D_col':Dc,'D_row':Dr}


def audit_cp4_root(root, expected_hashes):
    from pathlib import Path
    import hashlib
    root=Path(root)
    rows={}
    for rel,expected in expected_hashes.items():
        p=root/rel
        if not p.is_file(): raise FileNotFoundError(p)
        got=hashlib.sha256(p.read_bytes()).hexdigest()
        rows[rel]={'sha256':got,'expected_sha256':expected,'match':got==expected,'bytes':p.stat().st_size}
        if got!=expected: raise ValueError(f'CP4 source identity mismatch: {rel}')
    return {'all_match':True,'files':rows}


def order_pairs_by_cost(costs):
    rows=[]
    for key,value in costs.items():
        k=(int(key[0]),int(key[1]));v=float(value)
        if not math.isfinite(v) or v<=0: raise ValueError('invalid pair cost')
        rows.append((v,k))
    if len({k for _,k in rows})!=len(rows): raise ValueError('duplicate pair key')
    rows.sort(key=lambda x:(-x[0],x[1]))
    return [k for _,k in rows]


def od_contract(raw,sumabs,d,z):
    raw=np.asarray(raw);sumabs=np.asarray(sumabs)
    if raw.shape!=(2,3,3,12,12) or sumabs.shape!=raw.shape: raise ValueError('OD raw shape')
    v=LD(d['v']);ks=[v/2,-v/2];tau=LD(z)/v
    out=np.empty((3,47,2),CD);summed=np.empty((3,47,2),LD);C0=np.asarray(d['s_C'])[:,0].astype(LD)
    for ch,(active,j) in enumerate(REG):
        ang=j//8;C=np.asarray(d['s_C'] if ang==0 else d['p_C'])[:,j%8].astype(LD);coeff=C[:,None]*C0[None,:]
        for c in (0,1):
            act=active^c;par=1 if c==0 or ang==0 else -1;cz=(1 if c==0 else -1)*LD(z)/2
            phase=np.exp(CD(1j)*(2*ks[c]*cz+(LD(d['phase_E'][ch])-LD(d['phase_E'][47+c]))*tau))
            for field in (0,1,2):
                parity=par*(-1 if c and field else 1)
                out[field,ch,c]=phase*parity*np.sum(raw[act,field,ang]*coeff,dtype=CD)
                summed[field,ch,c]=np.sum(sumabs[act,field,ang]*abs(coeff),dtype=LD)
    return out,summed
