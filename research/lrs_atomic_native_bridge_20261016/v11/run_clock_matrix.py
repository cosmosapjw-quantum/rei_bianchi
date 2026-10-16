#!/usr/bin/env python3
"""V11 native-literal source-free CI/CE/FF/CMB component-clock light study."""
from __future__ import annotations
from pathlib import Path
import sys, json, csv, math, platform, time
import numpy as np
import scipy

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE/'src'))
import ci_thermal_clock as v


def run_study():
    out=HERE/'evidence';out.mkdir(exist_ok=True)
    grids=(8,16,32,64,128,256)
    all_cases=(('V10_D1_X1E5',1.,1e-5),('D1_X1E4',1.,1e-4),('D5_X1E5',5.,1e-5))
    selected=sys.argv[1] if len(sys.argv)>1 else None
    cases=tuple(c for c in all_cases if selected is None or c[0]==selected)
    if not cases: raise ValueError('UNKNOWN_CASE')
    data=[];summaries=[]
    base=np.zeros(21);base[:4]=v.initial_state()
    for label,density_factor,xend in cases:
        rad=v.reference(x_end=xend,density_factor=density_factor,rtol=2e-12)
        rad_tight=v.reference(x_end=xend,density_factor=density_factor,rtol=2e-13)
        true=rad.y[:,-1];Ttrue=v.temperature(true)
        T_tighter=v.temperature(rad_tight.y[:4,-1])
        refDelta=abs(Ttrue-T_tighter)
        assert refDelta<5e-9,(label,refDelta)
        for mode,clock in v.CLOCKS.items():
            prior_error=None;records=[]
            for N in grids:
                begin=time.perf_counter()
                approximate,maxroot=v.integrate_clock(clock,N,xend,density_factor)
                runtime=time.perf_counter()-begin
                T=v.temperature(approximate[:4]);err=abs(T-Ttrue)
                p=math.log2(prior_error/err) if prior_error is not None and err>0 else None
                prior_error=err
                sub=abs(v.energy_ledger(approximate,base))
                if not v.valid_state(approximate):raise AssertionError('invalid state')
                if sub>1e-11:raise AssertionError(('energy',label,mode,N,sub))
                row={'case':label,'D':density_factor,'Xend':xend,'mode':mode,'steps':N,
                     'temperature_K':T,'temperature_reference_K':Ttrue,
                     'T_abs_error_K':err,'last_error_order':p,
                     'HII':float(approximate[0]),'HeII':float(approximate[1]),
                     'HeIII':float(approximate[2]),'electron_per_total_H':float(approximate[0]+v.Y*(approximate[1]+2*approximate[2])),
                     'CE_HI_cooling_eV_H':float(approximate[11]),
                     'CE_HeI_cooling_eV_H':float(approximate[12]),
                     'CE_HeII_cooling_eV_H':float(approximate[13]),
                     'FF_cooling_eV_H':float(approximate[14]),
                     'CMB_input_eV_H':float(approximate[15]),
                     'RR_cooling_sum_eV_H':float(np.sum(approximate[16:20])),
                     'CI_binding_eV_H':float(np.dot(approximate[4:7],v.CHI)),
                     'energy_ledger_abs_eV_H':sub,
                     'newton_root_max_residual':maxroot,'wall_seconds':runtime}
                data.append(row);records.append(row)
            sums={'case':label,'mode':mode,'N128_error_K':next(x['T_abs_error_K'] for x in records if x['steps']==128),
                  'finest_N256_error_K':records[-1]['T_abs_error_K'],'last_order':records[-1]['last_error_order'],
                  'N128_T_K':next(x['temperature_K'] for x in records if x['steps']==128),
                  'maximum_energy_residual':max(x['energy_ledger_abs_eV_H'] for x in records),
                  'Radau_reference_K':Ttrue,'Radau_tolerance_difference_K':refDelta}
            summaries.append(sums)
        e0=next(q for q in summaries if q['case']==label and q['mode']=='owner_like_be')['N128_error_K']
        ece=next(q for q in summaries if q['case']==label and q['mode']=='ce_mid')['N128_error_K']
        emid=next(q for q in summaries if q['case']==label and q['mode']=='all_mid')['N128_error_K']
        print(f'{label}: Radau T={Ttrue:.12f} K, BE err={e0:.7g} K, CE clock err={ece:.7g} K, all-mid err={emid:.7g} K, CE reduction={(1-ece/e0)*100:.3f}%, ref diff={refDelta:.3g}',flush=True)
        if label=='V10_D1_X1E5':
            native_T=14988.7611352303
            owner_N128=next(x['temperature_K'] for x in data if x['case']==label and x['steps']==128 and x['mode']=='owner_like_be')
            print(f'V10 published native source-free BE N128: {native_T:.12f} K; Python owner-like: {owner_N128:.12f}; absdiff={abs(native_T-owner_N128):.12e} K',flush=True)
            assert abs(native_T-owner_N128)<2e-8
    raw={'schema':'rei.v11.c8.thermclock.1','label':'Conditional source-free sandbox owner literal rates/EOS; not full native driver',
         'owner_sha':'6ea2b1b4b3875c9163cafc45efe720afded43fc4',
         'parent_v10_sha':'c91ba18a38b744a1e64ff40423f02a35f2999605',
         'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__,
         'grackle_literal_table':v.grackle_literal_table_parity(HERE/'rust/rei_microphysics/tests/data/igm_grackle/grackle_literal_reference.csv'),
         'cases':len(cases),'modes':list(v.CLOCKS),'step_grids':list(grids),'rows':data,'summary':summaries,
         'permitted_claims':['source-free component clock first/second order in smooth nonstiff example','numeric parity to one native V10 endpoint'],
         'hold':['native driver fixed_step per-channel clock toggle execution','source-on actual causal timing attribution','full EoR physical history','nonperturbative Bianchi','Case B','uniform stiff accuracy']}
    stem='C8_MATRIX_'+(selected or 'ALL')
    (out/(stem+'.json')).write_text(json.dumps(raw,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
    with (out/(stem+'.csv')).open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(data[0]));writer.writeheader();writer.writerows(data)
    print('C8 study rows',len(data),'source rate table rows',raw['grackle_literal_table']['rows'],'maximum energy residual',max(x['energy_ledger_abs_eV_H'] for x in data),'PASS',flush=True)
    return raw

if __name__=='__main__':run_study()
