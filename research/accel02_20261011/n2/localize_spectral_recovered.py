#!/usr/bin/env python3
"""Saved-state band accounting at actual worst epochs; no ODE or RHS calls."""
import argparse,json
from pathlib import Path
import numpy as np
from postprocess_moments_recovered import module,sha,EV,C,CHI,HERE
import characteristics

def main():
    p=argparse.ArgumentParser();p.add_argument('coarse',type=Path);p.add_argument('fine',type=Path);p.add_argument('comparison',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
    if a.output.exists():raise FileExistsError(a.output)
    comparison=json.loads(a.comparison.read_text());fields=comparison['comparisons']['129']['fields']
    focus=['GammaHI_s','GammaHeI_s','source_number_ref_cm3_s','total_photoheat_proper_erg_cm3_s']
    indices=sorted(set(fields[k]['worst_epoch_index'] for k in focus))
    edges=np.array([0,13.6,24.59,54.42,100.,300.,1000.,50000.,np.inf])
    n1=module('band_moment_n1',HERE.parent/'n1/provider.py');native=n1.Native(HERE.parent/'n1/native/target/release/rei_n1_native');data={}
    try:
        for tag,run in [('coarse',a.coarse),('fine',a.fine)]:
            identity=json.loads((run/'IDENTITY.json').read_text());m=json.loads((run/'MOMENTS_RECOVERED.json').read_text())
            if m['max_one_sided_relative_energy_shift']!=0:raise ValueError('LOCALIZER_REQUIRES_NONBOUNDARY_SAVED_EPOCHS')
            if native.binary_sha256!=identity['native_sha']:raise ValueError('BINARY_IDENTITY')
            provider=n1.HistoryProvider(identity['args']['shear'])
            if provider.identity!=identity['input_identity']:raise ValueError('INPUT_IDENTITY')
            with np.load(run/'history.npz') as f:q=f['q'];mu=f['mu'];weights=f['weights'];u=f['u'];states=f['scaled_states']*f['scales']
            rows=[]
            for i in indices:
                t=float(u[i]*provider.end_time_s);g=provider.geometry(t);E,_,ratio=characteristics.geometry_nodes(q,mu,g);vol=g['a_rel']**3
                y=states[i];N=y[4:4+len(q)]/E;h,he1,he2=y[:3]
                sigma=np.zeros((len(q),3));active=E<=50000.;sigma[active]=native.call('SIGMA',E[active]).reshape(-1,3)
                absorbers=np.array([g['nH']*(1-h),g['nHe']*(1-he1-he2),g['nHe']*he1])
                source=characteristics.source_reference(q,mu,weights,g,provider.tables['emissivity'])
                heat=C*EV*np.sum(N[:,None]*sigma*(E[:,None]-CHI)*absorbers,axis=1)/vol
                per_node={'GammaHI_s':C*N*sigma[:,0]/vol,'GammaHeI_s':C*N*sigma[:,1]/vol,
                    'GammaHeII_s':C*N*sigma[:,2]/vol,'source_number_ref_cm3_s':source,
                    'source_energy_ref_erg_cm3_s':source*E*EV,'total_photoheat_proper_erg_cm3_s':heat}
                bands=[]
                for lo,hi in zip(edges[:-1],edges[1:]):
                    mask=(E>=lo)&(E<hi)
                    bands.append(dict(energy_eV=[float(lo),None if not np.isfinite(hi) else float(hi)],
                        nodes=int(sum(mask)),**{k:float(v[mask].sum()) for k,v in per_node.items()}))
                reconstruction={k:float(v.sum()) for k,v in per_node.items()}
                for k,x in reconstruction.items():
                    expected=m['history'][i][k]
                    if not np.isclose(x,expected,rtol=1e-13,atol=0):raise ValueError('BAND_SUM_MISMATCH:'+k)
                rows.append(dict(epoch_index=i,z=g['z'],time_s=t,bands=bands,totals=reconstruction))
            data[tag]=rows
    finally:native.close()
    out=dict(status='DIAGNOSTIC_NOT_CAUSAL_PROOF',focus_field_worst_epochs={k:fields[k]['worst_epoch_index'] for k in focus},
        edges_eV=[None if not np.isfinite(x) else float(x) for x in edges],runs=data,
        hypothesis='fixed-logq midpoint integration samples moving atomic/source discontinuities differently; event time splitting resolves chronology but does not itself remove energy quadrature error. Band accounting localizes differences, not a proof that thresholds alone cause all differences.',
        no_rhs_or_ode=True,code_sha256=sha(Path(__file__)),comparison_sha256=sha(a.comparison))
    a.output.write_text(json.dumps(out,indent=2)+'\n')
if __name__=='__main__':main()
