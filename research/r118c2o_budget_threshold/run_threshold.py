import json,hashlib
from pathlib import Path
import numpy as np
from threshold_transport import *
D=Path(__file__).resolve().parent;I=D.parents[1];H=Path('/home/cosmosapjw/Downloads');B=Path('/home/cosmosapjw/worktrees/bass-r109-native-20261124')
def j(p):return json.loads(p.read_text())
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def verify(p,hash_):assert sha(p)==hash_
# A. Reconstruct actual BASS packet spectrum with N/U and with threshold subcells.
br=j(B/'research/r118c2m_energy_budget/RESULTS.json')
static={}
for rec in br['results']:
    if rec['name'] not in ('base','time2','cross'):continue
    root=Path(br['raw'])/rec['name'];p=root/'packets.tsv';verify(p,rec['hashes']['packets.tsv'])
    x=np.genfromtxt(p,names=True,delimiter='\t');E=x['energy_eV'];w=x['N_per_H'];ray=x['ray'].astype(int)
    history=root/'history.tsv';verify(history,rec['hashes']['history.tsv'])
    nh=np.genfromtxt(history,names=True,delimiter='\t',usecols=['nH_m3'])['nH_m3'][-1]*1e-6
    scale=5/21;q=E/scale
    oracle=np.array([C*nh*(w@sigma(E)),C*nh*(w@(sigma(E)*(E-BIND))),w[E>=T].sum()])
    rows=[]
    for n in (16,32,64,128,256):
        edges=np.geomspace(13.6,512,n+1);idx=np.searchsorted(edges,q,side='right')-1
        # No dropped packet: extend edge index for any out-of-range source.
        allcells=[];sub=[];cross=0
        for k in sorted(set(zip(ray,idx))):
            mask=(ray==k[0])&(idx==k[1]);qs=np.asarray(q[mask],dtype=L);ws=np.asarray(w[mask],dtype=L)
            c=from_nodes(qs,ws,float(qs.min()),float(qs.max()));allcells.append(c)
            if c.lo<T/scale<=c.hi:cross+=1
            for above in (False,True):
                m=(qs>=T/scale)==above
                if np.any(m):sub.append(from_nodes(qs[m],ws[m],float(qs[m].min()),float(qs[m].max())))
        c=combine(allcells);s=combine(sub)
        assert abs(c.n-s.n)<2e-13*c.n and abs(c.u-s.u)<2e-13*c.u
        full=rates(allcells,scale,nh);spl=rates(sub,scale,nh)
        row=dict(n=n,crossing_cells=cross,full=full.tolist(),split=spl.tolist(),full_relative=(full/oracle-1).tolist(),split_relative=(spl/oracle-1).tolist())
        rows.append(row);print('static',rec['name'],n,row['full_relative'],row['split_relative'],flush=True)
    static[rec['name']]=dict(oracle=oracle.tolist(),rows=rows,packet_sha=sha(p))
# B. Source-off HeII absorption/redshift on actual q256 prefix; exact per-node
# reference initialized from fine exponential closure, coarse parent q64.
old=j(I/'research/r118c2n_spectral/Q256.json');p=Path(old['segments'][0]['raw_path']);r=Path(old['segments'][1]['raw_path'])
for qroot,rec in [(p,old['segments'][0]),(r,old['segments'][1])]:
    for n in ('checkpoint.txt','history.csv'):verify(qroot/n,rec['hashes'][n])
lines=(p/'checkpoint.txt').read_text().splitlines();assert lines[0]=='AXBI_CHECKPOINT_V4';a0=np.fromstring(lines[1],sep=' ')[0]
n,u,lo,hi=[np.fromstring(lines[k],sep=' ') for k in (4,5,6,7)]
raw=np.genfromtxt(r/'history.csv',names=True,delimiter=',');assert raw['a'][0]==a0 and raw['a'][-1]==.2
fhe=.2454/(4*(1-.2454));nh0=raw['nH_proper_cm3'];HeII=nh0*fhe*raw['x_HeII']
groups={}
for k in range(len(n)):
    if n[k]>0:groups.setdefault((k//256,(k%256)//4),[]).append(Cell(n[k],u[k],lo[k],hi[k]))
groups={k:v for k,v in groups.items() if max(c.hi for c in v)/(21*a0)>=T}
initialN=sum((L(c.n) for v in groups.values() for c in v),L(0));initialU=sum((L(c.u) for v in groups.values() for c in v),L(0))
def campaign(steps,order):
    aa=np.geomspace(a0,.2,steps+1);mid=np.sqrt(aa[1:]*aa[:-1]);tt=np.interp(aa,raw['a'],raw['time_s']);dt=np.diff(tt);he=np.interp(mid,raw['a'],HeII)
    cuts=T*21*np.r_[aa,mid];scale0=1/(21*a0);scalef=5/21
    # Reference quadrature explicitly resolves every moving threshold in this schedule.
    ref=[];initial_split={};initial_full={}
    for key,cs in groups.items():
        q=[];w=[]
        for c in cs:
            x,y=nodes(c,cuts,order);q.extend(x);w.extend(y)
        q=np.array(q,dtype=L);w=np.array(w,dtype=L);ref.append((q,w.copy()))
        whole=combine(cs);initial_full[key]=[whole];csplit=[]
        for c in cs:
            x,y=split(c,T/scale0,order)
            csplit.append((x,y))
        initial_split[key]=[c for i in (0,1) if (c:=combine([x[i] for x in csplit])) is not None]
    def represented(mode):
        state={k:list(v) for k,v in (initial_split if mode=='split' else initial_full).items()}
        N=U=heat=L(0)
        for a,h,t,den in zip(aa[1:],mid,dt,he):
            cut=T*21*a;scale=1/(21*h)
            for key,cs in list(state.items()):
                new=[]
                for c in cs:
                    out,dn,du,dheat=debit(c,scale,t,den,cut,mode=='split',order)
                    new.extend(out);N+=dn;U+=du;heat+=dheat
                if mode=='split':
                    below=[c for c in new if c.hi<=cut and c.lo<cut]
                    above=[c for c in new if c.lo>=cut]
                    assert len(below)+len(above)==len(new)
                    state[key]=[c for c in (combine(below),combine(above)) if c is not None]
                else:state[key]=[c for c in [combine(new)] if c is not None]
        cells=[c for v in state.values() for c in v];m=combine(cells)
        nerr=abs(m.n+N-initialN)/initialN;uerr=abs(m.u+U-initialU)/initialU
        assert max(nerr,uerr)<2e-10
        return dict(rate=rates(cells,scalef,nh0[-1]).tolist(),absorbed_N=float(N),absorbed_Uref=float(U),heating=float(heat),N_defect=float(nerr),U_defect=float(uerr))
    refN=refU=refHeat=L(0)
    for idx,(q,w) in enumerate(ref):
        for h,t,den in zip(mid,dt,he):
            E=q/(21*h);opacity=L(C*t*den)*sigma(E);lost=w*(-np.expm1(-opacity));w=w*np.exp(-opacity)
            refN+=lost.sum();refU+=lost@q;refHeat+=lost@(E-BIND)
        ref[idx]=(q,w)
    q=np.concatenate([x[0] for x in ref]);w=np.concatenate([x[1] for x in ref]);E=q*scalef;S=sigma(E)
    reference=dict(rate=[float(C*nh0[-1]*(w@S)),float(C*nh0[-1]*(w@(S*(E-BIND)))),float(w[E>=T].sum())],absorbed_N=float(refN),absorbed_Uref=float(refU),heating=float(refHeat))
    assert abs(w.sum()+refN-initialN)/initialN<2e-11 and abs(w@q+refU-initialU)/initialU<2e-11
    initial_rate=rates([c for v in groups.values() for c in v],scale0,nh0[0])
    out=dict(steps=steps,order=order,reference=reference,initial_rate=initial_rate.tolist())
    for mode in ('full','split'):
        v=represented(mode)
        v['rate_relative']=[float(x/y-1) if y>1e-12*ini else None for x,y,ini in zip(v['rate'],reference['rate'],initial_rate)]
        v['terminal_absolute_error_over_initial_rate']=[float(abs(x-y)/ini) if ini>0 else None for x,y,ini in zip(v['rate'],reference['rate'],initial_rate)]
        v['absorbed_N_relative']=v['absorbed_N']/reference['absorbed_N']-1
        v['heating_relative']=v['heating']/reference['heating']-1
        out[mode]=v
    print('moving',steps,order,out,flush=True);return out
moving=[campaign(k,24) for k in (8,16,32,64)]+[campaign(32,40)]
out=dict(status='PASS_SCOPED_THRESHOLD_PILOT',scope='BASS terminal positive packet moment diagnostic; source-off HeII absorption + redshift on q256 prefix selected coarse parents, prescribed original gas, no coupled moving owner',static=static,moving=moving,groups=len(groups),initial_N=float(initialN),initial_Uref=float(initialU),prefix_sha=sha(p/'checkpoint.txt'),gas_history_sha=sha(r/'history.csv'))
(D/'THRESHOLD_RESULTS.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
