"""Independent DOP853 for actual positive MD14 births, signed native geometry.
Shared immutable native coefficients and instantaneous moment reconstruction.
"""
import json,subprocess,sys,time
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp
binary=Path(sys.argv[1]);out=Path(sys.argv[2]);out.mkdir(parents=True,exist_ok=True)
summary=[]
for q in [-.1,0.,.1]:
    subprocess.run([str(binary),'source_native',str(q),str(out)],check=True,timeout=300)
    p=subprocess.Popen([str(binary),'source_rhs',str(q)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,bufsize=1)
    setup=json.loads(p.stdout.readline());(out/f'source_setup_q{q}.json').write_text(json.dumps(setup)+'\n')
    cells=setup['cells'];births=setup['births'];y=np.r_[setup['initial'],np.zeros(len(births)*2*cells)];start=setup['x0'];calls=[0]
    def rhs(x,y):
        calls[0]+=1
        p.stdin.write(' '.join(format(v,'.17e') for v in np.r_[x,y])+'\n');p.stdin.flush()
        line=p.stdout.readline()
        if not line:
            np.save(out/f'first_invalid_trial_q{q}.npy',np.r_[x,y])
            (out/f'first_invalid_trial_q{q}.json').write_text(json.dumps(dict(x=x,calls=calls[0],min_state=float(y[4:].min()),min_number=float(y[4:].reshape(-1,2,cells)[:,0].min()),scope='raw failed DOP853 internal trial; no projection'))+'\n')
            raise RuntimeError(p.stderr.read())
        return np.fromstring(line,sep=' ')
    begin=time.monotonic()
    for i,stop in enumerate([*births,setup['x1']]):
        r=solve_ivp(rhs,(start,stop),y,method='DOP853',rtol=2e-9,atol=np.r_[[2e-13]*3,[2e-12],np.full(y.size-4,1e-15)])
        assert r.success,r.message
        y=r.y[:,-1]
        if i<len(births):y[4+2*cells*i:4+2*cells*(i+1)]+=setup['inject'][i]
        start=stop
    p.stdin.close();p.wait(timeout=30);assert p.returncode==0,p.stderr.read()
    (out/f'source_dop853_q{q}.json').write_text(json.dumps(dict(q=q,endpoint=y.tolist(),calls=calls[0],wall_s=time.monotonic()-begin))+'\n')
    rows=[]
    for level in [1,2,4]:
        v=np.array(json.loads((out/f'source_native_q{q}_level{level}.json').read_text())['state']);delta=np.abs(v-y)
        species=delta[:3];stock=y[4:].reshape(-1,2,cells)
        err=(v[4:]-y[4:]).reshape(-1,2,cells)
        rows.append(dict(level=level,species_abs=species.tolist(),thermal_abs_eV_H=float(delta[3]),cohort_number_abs=float(np.abs(err[:,0]).sum()),cohort_reference_energy_abs=float(np.abs(err[:,1]).sum()),max_cell_abs=float(delta[4:].max())))
    summary.append(dict(q=q,shared_physics='native continuous moment RHS from exact original prepared-node accessor',source='actual native MD14 positive 8-birth midpoint schedule',background='signed native driver geometry',solver='SciPy DOP853',calls=calls[0],wall_s=time.monotonic()-begin,refinement=rows))
(out/'source_matched_independent.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary))
