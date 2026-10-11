#!/usr/bin/env python3
"""Saved-grid HM12 source/IC attribution; no native RHS or ODE execution.

The analytic reference calls the source-pinned HM12Table.moment method.
It is exact for the declared binary64 piecewise-linear interpolation, up to
floating-point roundoff; it is not an exact physical-continuum HM12 model.
"""
from __future__ import annotations
from decimal import Decimal
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import numpy as np

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
ROOT=HERE.parents[2]
PHYSICAL=ROOT/'research/physical_provider_20261010'
BANDS={'full':[10.,50000.], 'HI_ionizing':[13.60,50000.],
       'HeI_ionizing':[24.59,50000.], 'HeII_ionizing':[54.42,50000.]}
EV=1.602176634e-12

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m

def checked_table_arithmetic(table,zlower,zupper):
    """Report literal underflow and input magnitudes; no zeros are changed."""
    raw=PHYSICAL/'sources'/table.source_name
    data=[x.split() for x in raw.read_text().splitlines() if x.strip() and not x.lstrip().startswith('#')][1:]
    lost=sum(Decimal(v)!=0 and float(v)==0 for row in data for v in row[1:])
    if lost:raise ValueError('POSITIVE_NATIVE_LITERAL_UNDERFLOW')
    en=table.energies_eV
    ix=np.flatnonzero((en>=10.)&(en<=50000.))
    ix=np.unique(np.r_[ix,max(0,int(ix[0])-1),min(len(en)-1,int(ix[-1])+1)])
    cols=[]
    for z in (zlower,zupper):
        i=int(np.searchsorted(table.redshifts,z));cols.extend([max(0,i-1),i])
    columns=np.arange(min(cols),max(cols)+1)
    selected=table.spectra[::-1][ix][:,columns]
    positive=selected[selected>0]
    if len(positive)==0:raise ValueError('UNEXPECTED_ALL_ZERO_RELEVANT_TABLE')
    factors=[table.proper_photon_factor(z) for z in (zlower,zupper)]
    # Restrict this check to source rows and redshift columns relevant to Q0;
    # the full UVB table legitimately contains irrelevant subnormal ordinates.
    if positive.min()*min(factors) <= np.finfo(float).tiny:
        raise ValueError('RELEVANT_NORMAL_RANGE_UNDERFLOW_RISK')
    return dict(provenance=table.provenance(),positive_literals_parsed_as_zero=int(lost),
        global_subnormal_positive_ordinates=int(np.count_nonzero((table.spectra>0)&(table.spectra<np.finfo(float).tiny))),
        relevant_native_minimum_positive=float(positive.min()),relevant_native_zero_ordinates=int(np.count_nonzero(selected==0)),
        relevant_converted_minimum_positive_bound=float(positive.min()*min(factors)),
        relevant_redshift_columns=table.redshifts[columns].tolist(),
        interpretation='native zeros retained; no log(ordinate), floor, clipping, zero replacement, or extrapolation')

def summarize(approx,exact,z):
    a=np.asarray(approx);e=np.asarray(exact);d=a-e
    if not np.isfinite(np.r_[a,e,d]).all():raise ValueError('NONFINITE_MOMENT_COMPARISON')
    amplitude=float(np.max(np.abs(e)))
    if amplitude==0:
        if np.any(a!=0):raise ValueError('ZERO_EXACT_REFERENCE_NONZERO_APPROXIMATION')
        return dict(exact_history_amplitude=0.,max_absolute_error=0.,normalized_error=None,
                    normalization='both exactly zero; no denominator floor',max_pointwise_relative_error=None)
    i=int(np.argmax(np.abs(d)))
    nonzero=e!=0
    return dict(exact_history_amplitude=amplitude,max_absolute_error=float(abs(d[i])),
        normalized_error=float(abs(d[i])/amplitude),normalization='max|approx-exact| / max|exact| over this epoch set; attribution only',
        diagnostic_target=1e-3,diagnostic_within_target=bool(abs(d[i])/amplitude<=1e-3),
        signed_error_at_max=float(d[i]),z_at_max=float(z[i]),sample_index_at_max=i,
        minimum_signed_error=float(d.min()),maximum_signed_error=float(d.max()),
        max_pointwise_relative_error=float(np.max(abs(d[nonzero]/e[nonzero]))),
        zero_exact_epochs=int(np.count_nonzero(~nonzero)))

def main():
    out=HERE/'Q0_SOURCE_ATTRIBUTION.json'
    report=HERE/'Q0_SOURCE_ATTRIBUTION.md'
    if out.exists() or report.exists():raise FileExistsError('Q0 output is create-only')
    n1=module('q0_source_n1',BASE/'n1/provider.py')
    char=module('q0_source_characteristics',BASE/'n2/characteristics.py')
    provider=n1.HistoryProvider(0.)
    if EV!=n1.EV_ERG:raise ValueError('ENERGY_UNIT_MISMATCH')
    arithmetic={key:checked_table_arithmetic(table,15.9 if key=='uvb' else 4.,15.9)
                for key,table in provider.tables.items()}
    exact_rows=[]
    times=np.linspace(0.,1.,129)*provider.end_time_s
    geometry=[provider.geometry(float(t)) for t in times]
    geometry_error=0.
    for t,g in zip(times,geometry):
        e,mu,r=char.geometry_nodes(np.array([10.,50000.]),np.array([-.5773502691896257,.5773502691896257]),g)
        geometry_error=max(geometry_error,float(np.max(abs(r*g['a_rel']-1.))))
        if g['b']!=0. or g['s']!=0. or geometry_error>1e-14:raise ValueError('Q0_REFERENCE_IS_FLRW_ONLY')
        row={'time_s':float(t),'z':float(g['z']),'a_rel':float(g['a_rel'])}
        for band,(lo,hi) in BANDS.items():
            for p,label,factor in [(0,'number',1.),(1,'energy',EV)]:
                value=provider.tables['emissivity'].moment(lo,hi,g['z'],power=p,reference_eV=1.,proper_photons=True)*factor
                if not np.isfinite(value) or value<=0:raise ValueError('INVALID_EXACT_SOURCE_MOMENT')
                row[f'{band}_{label}_proper']=float(value)
                row[f'{band}_{label}_ref']=float(value*g['a_rel']**3)
        exact_rows.append(row)
    runs={}
    for name in ['EVENT_COUPLED002','EVENT_COUPLED003_RECOVERED']:
        run=BASE/'n2/evidence'/name
        ident=json.loads((run/'IDENTITY.json').read_text())
        result=json.loads((run/'RESULT.json').read_text())
        previous=json.loads((run/'MOMENTS_RECOVERED.json').read_text())
        checks={'provider_bytes':sha(BASE/'n1/provider.py')==ident['n1_sha'],
                'source_input_bytes':provider.identity==ident['input_identity'],
                'source_identity_matches_postprocessing':all(sha(run/f)==h for f,h in previous['saved_file_sha256'].items()),
                'complete_saved_result':result['status']=='COMPUTED_NOT_REVIEWED' and len(result['history'])==129,
                'FLRW_only':ident['args']['shear']==0.}
        with np.load(run/'history.npz') as data:
            q=data['q'];mu=data['mu'];weights=data['weights'];u=data['u']
            y0=data['scaled_states'][0]*data['scales']
        expected_grid=char.make_grid(ident['args']['energy'],ident['args']['angle'],provider.q_max_eV)
        checks['saved_grid_matches_published_grid']=all(np.array_equal(a,b) for a,b in zip((q,mu,weights),expected_grid))
        checks['exact_common_epochs']=np.array_equal(u,np.linspace(0,1,129)) and np.array_equal(times,[r['time_s'] for r in result['history']])
        if not all(checks.values()):raise ValueError(f'RUN_IDENTITY_MISMATCH:{name}:{checks}')
        rows=[]
        source_reconstruction_error=0.
        for i,(t,g) in enumerate(zip(times,geometry)):
            energy,_,_=char.geometry_nodes(q,mu,g)
            # Invoke the existing source function, not a reimplemented source law.
            source=char.source_reference(q,mu,weights,g,provider.tables['emissivity'])
            reference=previous['history'][i]
            for value,key in [(source.sum(),'source_number_ref_cm3_s'),(EV*np.dot(source,energy),'source_energy_ref_erg_cm3_s')]:
                old=reference[key]
                if old==0:
                    if value!=0:raise ValueError('SOURCE_RECONSTRUCTION_ZERO_MISMATCH')
                else:source_reconstruction_error=max(source_reconstruction_error,float(abs(value-old)/abs(old)))
            row={'time_s':float(t),'z':float(g['z'])}
            for band,(lo,hi) in BANDS.items():
                select=(energy>=lo)&(energy<=hi)
                for p,label,factor in [(0,'number',1.),(1,'energy',EV)]:
                    v=float(np.sum(source[select]*energy[select]**p)*factor)
                    row[f'{band}_{label}_ref']=v;row[f'{band}_{label}_proper']=v/g['a_rel']**3
            rows.append(row)
        if source_reconstruction_error>1e-13:raise ValueError('SOURCE_DIFFERS_FROM_AS_RUN_EVENT_CONVENTION')
        initial=provider.initial_photons(q,weights)
        saved_initial=y0[4:4+len(q)]/q
        ic_roundtrip=float(max(abs(initial-saved_initial))/max(abs(initial)))
        if ic_roundtrip>1e-13:raise ValueError('SAVED_IC_DIFFERS_FROM_PROVIDER')
        initial_comparison={}
        for band,(lo,hi) in BANDS.items():
            select=(q>=lo)&(q<=hi)
            for p,label,factor in [(0,'number',1.),(1,'energy',EV)]:
                a=float(np.sum(initial[select]*q[select]**p)*factor)
                e=provider.tables['uvb'].moment(lo,hi,provider.z_initial,power=p,reference_eV=1.,proper_photons=True)*factor
                if not e>0:raise ValueError('INVALID_EXACT_IC_MOMENT')
                initial_comparison[f'{band}_{label}']={'approximate':a,'exact_declared_interpolation':e,'signed_relative_error':(a-e)/e,'absolute_relative_error':abs(a-e)/e}
        metrics={}
        fields=[k for k in exact_rows[0] if k not in ['time_s','z','a_rel']]
        for epochset,indices in [('shared129',np.arange(129)),('original65',np.arange(0,129,2))]:
            metrics[epochset]={key:summarize([rows[i][key] for i in indices],[exact_rows[i][key] for i in indices],[rows[i]['z'] for i in indices]) for key in fields}
        runs[name]={'identity_checks':checks,'saved_sha256':{f:sha(run/f) for f in ['IDENTITY.json','RESULT.json','history.npz','MOMENTS_RECOVERED.json']},
            'energy_bins':ident['args']['energy'],'source_vs_existing_event_postprocess_max_relative_error':source_reconstruction_error,
            'initial_saved_roundtrip_max_scaled_error':ic_roundtrip,'source_moment_metrics':metrics,'initial_UVB_moment_comparison':initial_comparison,'source_history':rows}
    output={'schema':'rei.q0_source_attribution.v1','status':'COMPUTED_SOURCE_AND_IC_ATTRIBUTION_ONLY','execution':{'ODE':0,'native_RHS':0,'native_SIGMA':0,'RUN002_replay':0},
        'implementation_sha256':sha(__file__),'source_implementation_sha256':{'provider.py':sha(BASE/'n1/provider.py'),'characteristics.py':sha(BASE/'n2/characteristics.py'),'hm12_data.py':sha(PHYSICAL/'hm12_data.py')},
        'characteristics_identity_caveat':'Original run IDENTITY did not separately pin characteristics.py; current published implementation is hashed and saved grids checked exactly.',
        'exactness':'HM12Table.moment analytic piecewise integral of declared binary64 linear-ordinate in log(E) and z interpolation, up to floating-point roundoff; not a physical-continuum certificate',
        'units':{'number_proper':'cm^-3 s^-1','number_ref':'photons per initial-reference cm^3 per s','energy_proper':'erg cm^-3 s^-1','energy_ref':'erg per initial-reference cm^3 per s','initial_number':'cm^-3','initial_energy':'erg cm^-3'},
        'bands_eV':BANDS,'geometry':'FLRW r=0 only; E=q/a_rel and source_ref=a_rel^3 source_proper; all input spectra retain10..50000eV physical source band',
        'max_R_a_minus_one':geometry_error,'arithmetic_audit':arithmetic,
        'limitations':['Source-only errors are independent of the evolved gas and therefore identify an input quadrature error directly.','They do not apportion the evolved Gamma, x, T or heat error among source, initial field, opacity quadrature and nonlinear gas feedback.','No exact cumulative temporal integral is claimed; stored ODE source counters were not repaired or replaced.','Q0 normalizes to exact-reference full-history amplitude for attribution; this does not replace the official fine-grid-amplitude spectral comparison.','HI/HeI/HeII bands are threshold-selected source moments, not cross-section-weighted photoionization or heat integrals.','No floor, clipping, extrapolation, log-ordinate interpolation, or native-cross-section replacement is used.'],
        'exact_source_history':exact_rows,'runs':runs}
    out.write_text(json.dumps(output,indent=2,allow_nan=False)+'\n')
    lines=['# Q0 source/initial-field quadrature attribution','','Status: computed without ODE or native RHS/SIGMA calls. The source is unchanged. Both saved grids use the same pinned HM12 tables and the same actual source function. All129 epochs and the original65 subset are retained in the companion JSON.','','The analytic reference is exact up to floating-point roundoff for the declared piecewise-linear HM12 interpolation, not for a physical continuum model. It uses `HM12Table.moment`; FLRW source reference density is a_rel^3 times proper density. No native cross section is replaced.','','## Instantaneous full-band source errors','','Errors below are max|sampled-exact| / max|exact| across the129 epochs. They are attribution diagnostics, not replacements for the formal spectral pair test.','','| Energy bins | Number, reference | Energy, reference | Number, proper | Energy, proper |','|---|---:|---:|---:|---:|']
    for run in runs.values():
        m=run['source_moment_metrics']['shared129'];keys=['full_number_ref','full_energy_ref','full_number_proper','full_energy_proper']
        lines.append('| '+str(run['energy_bins'])+' | '+' | '.join(f'{m[k]["normalized_error"]:.9g}' for k in keys)+' |')
    lines+=['','## Initial UVB errors','','The initial radiation is independently discretized. These are signed relative errors against the exact declared interpolation at z=15.9.','','| Energy bins | Full-band N | Full-band energy | HI-ionizing N | HeI-ionizing N | HeII-ionizing N |','|---|---:|---:|---:|---:|---:|']
    for run in runs.values():
        m=run['initial_UVB_moment_comparison'];keys=['full_number','full_energy','HI_ionizing_number','HeI_ionizing_number','HeII_ionizing_number']
        lines.append('| '+str(run['energy_bins'])+' | '+' | '.join(f'{m[k]["signed_relative_error"]:.9g}' for k in keys)+' |')
    lines+=['','## Arithmetic and interpretation','','Both tables have zero positive decimal literals silently parsed as zero. The complete UVB table includes subnormal ordinates outside the relevant rows/initial-redshift columns. The relevant UVB inputs have minimum positive native ordinate7.965e-34; native zeros remain zeros. The source inputs over the relevant band and redshift columns have minimum positive native ordinate1.686e18. No relevant underflow or floor is used; interpolation is linear in ordinates, including zeros, and native jumps have zero integration measure. All source sums reproduce the prior event-aware saved-state postprocessing within the recorded roundoff check.','','A nonzero source-only error is established independently of gas feedback. Initial UVB discretization also has directly measured error. These findings do not uniquely explain the evolved Gamma, temperature or ion-fraction discrepancy. The next patch must propagate any improved quadrature through the common photon/gas/counter operator; changing only a plot, Gamma diagnostic, or source counter is not allowed. The Q0 results do not relax any scientific gate or admit CR/RCT/secondary physics.','','See `Q0_SOURCE_ATTRIBUTION.json` for threshold-selected source moments, signed errors, locations,129/65 epoch summaries, input hashes and full histories.']
    report.write_text('\n'.join(lines)+'\n')
    print(json.dumps({'output':str(out),'report':str(report),'summary':{n:r['source_moment_metrics']['shared129']['full_number_ref'] for n,r in runs.items()}},indent=2))

if __name__=='__main__':main()
