"""Frozen instantaneous composition: one build and one native campaign."""
import decimal,hashlib,json,pathlib,subprocess,time
ROOT=pathlib.Path(__file__).resolve().parent
decimal.getcontext().prec=80
D=decimal.Decimal
f=D.from_float
def dump(name,value): (ROOT/'evidence'/name).write_text(json.dumps(value,indent=2)+'\n')
def scaled(value,oracle,scale):
    return float(abs(f(value)-oracle)/scale) if scale else (0.0 if f(value)==oracle else float('inf'))
def checksha(path,sha): assert hashlib.sha256(path.read_bytes()).hexdigest()==sha,str(path)
rows=[]
for label,sha in {'baseline':'f39c09cac72359ecff4366ba5e0828d75c7d44185d126fd499f9e741bfb5005e','refined':'4204d0ea44b23c868e5c5e330029bc35303ae85466cdb4671e60ba9d4a140611'}.items():
    path=ROOT.parent/'rec_rei_cold_intake01_20261011'/'inputs'/f'{label}.json';checksha(path,sha)
    for row in json.loads(path.read_bytes()): rows.append((label,row['endpoint']))
repo=ROOT.parent.parent
for path,sha in {
    'research/cold_hii_rr_component01_20261011/source/HG97_astro-ph_9612232v1.pdf':'6ea0b803b554c91d598705f96416e1a8b67549fb02cb567944eaacdba5d148b0',
    'research/cold_compton_component01_20261011/source/history.c':'8ffe38f0431fcd1ae04b55f855f36e8643b1c5eb33a947f581f95d628611f976',
    'rust/rei_microphysics/src/cold_hii_rr.rs':'a92fb4952cd93475616f93b4d1161c109eac0738402ce1c6c229a83c030a0b00',
    'rust/rei_microphysics/src/cold_compton.rs':'2748809df576a95461e1d4ed4a530cd5691701741dbb332602186af0d7f33bbc',
    'rust/rei_microphysics/src/axisym_coupling.rs':'6bb3feb6a290894bd8bdd45f9745f28329265cee8ce89589a11960b523e6b008'}.items():checksha(repo/path,sha)
(ROOT/'evidence').mkdir(exist_ok=True)
stdin=''.join(' '.join(repr(e[k]) for k in ['a','H_s1','Tm_K','nH_m3','nHe_m3','xe_per_H','Tgamma_K'])+'\n' for _,e in rows)
binary=ROOT/'native'/'target'/'release'/'cold_stage_composition01'
for phase,command,limit,inp in [('BUILD',['cargo','build','--release','--locked','--manifest-path',str(ROOT/'native'/'Cargo.toml')],300,None),('CAMPAIGN',[str(binary)],120,stdin)]:
    start=time.monotonic(); proc=subprocess.run(command,input=inp,text=True,capture_output=True,timeout=limit)
    (ROOT/'evidence'/f'FIRST_{phase}.stdout').write_text(proc.stdout)
    (ROOT/'evidence'/f'FIRST_{phase}.stderr').write_text(proc.stderr)
    receipt={'command':command,'exit':proc.returncode,'wall_s':time.monotonic()-start,'timeout_s':limit}
    if phase=='CAMPAIGN':receipt.update(stdin=stdin,binary_sha256=hashlib.sha256(binary.read_bytes()).hexdigest())
    dump(f'{phase}_RECEIPT.json',receipt)
    assert proc.returncode==0,f'{phase} first failure: stop for Astra'
out=[json.loads(line) for line in proc.stdout.splitlines()]
assert len(out)==10 and out[-1]['controls']=='PASS' and out[-1]['derivative_attempts']==16
reports=[]
for o in out[:-1]:
    t,nh,nhe,xe,p,u,h,hi,hii,tg=(f(o[k]) for k in ['T','nh','nhe','xe','particles','u','H','HI','HII','Tgamma'])
    kb=f(1.380649e-23);chi=f(13.598434599702*1.602176634e-19)
    lam=D('315614')/t
    alpha=D('1.269e-13')*lam**D('1.503')/(1+(lam/D('.522'))**D('.470'))**D('1.923')*D('1e-6')
    cool=D('1.778e-29')*t*lam**D('1.965')/(1+(lam/D('.541'))**D('.502'))**D('2.697')*D('1e-13')
    r=alpha*(nh*xe)**2;c=cool*(nh*xe)**2
    q=f(1.5)*kb*nh*xe*f(4.91466895548409e-22)*tg**4*(tg-t)
    ub=chi*hii
    oracle={'r':r,'C':c,'q':q,'du':-5*h*u-c+q,'dnHI':-3*h*hi+r,'dnHII':-3*h*hii-r,
        'dnHeI':-3*h*nhe,'dne':-3*h*hii-r,'dparticles':-3*h*p-r,'binding':ub,'dbinding':-3*h*ub-chi*r,
        'thermal_source':-c+q,'internal':-chi*r,'escape':chi*r+c,'external':q,'bath':-q,
        'dT':-2*h*t+(-c+q)/(f(1.5)*kb*p)+t*r/p}
    scales={k:abs(v) for k,v in oracle.items()}
    scales.update(du=abs(5*h*u)+abs(c)+abs(q),dnHI=abs(3*h*hi)+abs(r),thermal_source=abs(c)+abs(q),
        dT=abs(2*h*t)+(abs(c)+abs(q))/(f(1.5)*kb*p)+abs(t*r/p))
    errors={k:scaled(o[k],v,scales[k]) for k,v in oracle.items()}
    assert max(errors.values())<=3e-12,(o['label'],errors)
    identities=[([o['thermal_source'],o['internal'],o['escape'],-o['external']]),
        [o['du'],o['dbinding'],o['escape'],o['bath'],5*o['H']*o['u'],3*o['H']*o['binding']],
        [o['sources_species'][1],o['sources_species'][2]],
        [o['sources_species'][2],o['r']]]
    residuals=[float(abs(sum(map(f,terms)))/sum(map(lambda x:abs(f(x)),terms))) if any(terms) else 0.0 for terms in identities]
    assert max(residuals)<=1e-13,(o['label'],residuals)
    assert o['dnphoton']==o['duphoton']==0
    assert all(o['species'][i]==o['sources_species'][i]==0 for i in range(13) if i not in [1,2,10])
    assert o['sources_species'][10]==0
    reports.append({'label':o['label'],'state':o,'oracle_errors':errors,'scaled_residuals':residuals})
refinement={k:max(abs(reports[i]['state'][k]-reports[i+2]['state'][k])/abs(reports[i+2]['state'][k]) for i in [0,1]) for k in ['T','r','C','q','dT','du']}
result={'unit':'COLD_STAGE_COMPOSITION01','status':'PASS_SCOPED','rows':reports,'controls':out[-1],
    'build_count':1,'campaign_count':1,'history_executions':0,'solver_steps':0,'harness_status':'HARNESS_UNAVAILABLE',
    'baseline_refined_relative_differences':refinement,'scientific_admission':'HOLD'}
dump('VALIDATION.json',result)
print(json.dumps({'status':'PASS_SCOPED','max_oracle_error':max(max(r['oracle_errors'].values()) for r in reports),'max_residual':max(max(r['scaled_residuals']) for r in reports),'derivative_attempts':16}))
