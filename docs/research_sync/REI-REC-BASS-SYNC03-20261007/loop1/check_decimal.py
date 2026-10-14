#!/usr/bin/env python3
"""Independent Decimal-70 arithmetic for exported aggregate densities.

No BASS code or native q array is used in the reference calculation. Input
endpoints and physical constants are shared intentionally; this is an arithmetic
and contract check, not independent validation of the REI chemistry trajectory.
"""
import csv, decimal, gzip, json, math, pathlib, sys, time
from decimal import Decimal as D

ROOT=pathlib.Path(__file__).resolve().parent
decimal.getcontext().prec=70
C=D.from_float(299792458.0); SIGMA=D.from_float(6.6524587e-29)
ABS_TAU=D('1e-18'); REL_TAU=D('1e-12'); ABS_P=D('2e-12')

def exact(text): return D.from_float(float(text))

def main():
    manifest=json.loads((ROOT/'outputs/NATIVE_SUMMARY.json').read_text())
    histories=[]; failures=[]; total=0
    for h in manifest['histories']:
        with gzip.open(ROOT.parent/h['input'],'rt') as f: src=list(csv.DictReader(f))
        with gzip.open(ROOT.parent/h['output'],'rt') as f: got=list(csv.DictReader(f))
        assert len(src)==len(got)
        times=[exact(r['normal_time_s']) for r in src]
        # Independent density-to-rate expression: exact binary64 source inputs,
        # no auxiliary composition or shared native multiplication sequence.
        rates=[exact(r['ne_proper_cm3'])*D(1000000)*C*SIGMA for r in src]
        depth=[(b-a)*(q0+q1)/D(2) for a,b,q0,q1 in zip(times,times[1:],rates,rates[1:])]
        tau=[D(0)]*len(src)
        for i in range(len(depth)-1,-1,-1):tau[i]=tau[i+1]+depth[i]
        survival=[(-x).exp() for x in tau]
        probability=[survival[i+1]-survival[i] for i in range(len(depth))]+[D(0)]
        tail=D.from_float(0.1); tail_factor=(-tail).exp()
        maximum={'q_relative':D(0),'tau_absolute':D(0),'tau_relative_nonzero':D(0),'survival_absolute':D(0),'probability_absolute':D(0),'tail_tau_absolute':D(0),'tail_scaling_absolute':D(0)}
        checks=0
        for i,row in enumerate(got):
            native={k:exact(v) for k,v in row.items()}
            assert all(v.is_finite() for v in native.values())
            assert native['normal_time_s']==times[i] and native['ne_proper_cm3']==exact(src[i]['ne_proper_cm3']), 'native input identity drift'
            tests=[('q',native['q_normal_s_inverse'],rates[i],D('1e-30')+D('1e-14')*abs(rates[i])),('tau',native['tau_tail0'],tau[i],ABS_TAU+REL_TAU*abs(tau[i])),('survival',native['survival_tail0'],survival[i],ABS_P),('probability',native['cell_probability_tail0'],probability[i],ABS_P),('tail_tau',native['tau_tail01'],tau[i]+tail,ABS_TAU+REL_TAU*abs(tau[i]+tail)),('tail_survival',native['survival_tail01'],survival[i]*tail_factor,ABS_P),('tail_probability',native['cell_probability_tail01'],probability[i]*tail_factor,ABS_P)]
            for key,a,b,tol in tests:
                checks+=1
                if a<0 or abs(a-b)>tol:
                    if len(failures)<20: failures.append({'history':h['history'],'row':i,'field':key,'native':str(a),'reference':str(b),'tolerance':str(tol)})
            maximum['q_relative']=max(maximum['q_relative'],abs(native['q_normal_s_inverse']-rates[i])/rates[i] if rates[i] else D(0))
            maximum['tau_absolute']=max(maximum['tau_absolute'],abs(native['tau_tail0']-tau[i]))
            if tau[i]:maximum['tau_relative_nonzero']=max(maximum['tau_relative_nonzero'],abs(native['tau_tail0']-tau[i])/tau[i])
            maximum['survival_absolute']=max(maximum['survival_absolute'],abs(native['survival_tail0']-survival[i]))
            maximum['probability_absolute']=max(maximum['probability_absolute'],abs(native['cell_probability_tail0']-probability[i]))
            maximum['tail_tau_absolute']=max(maximum['tail_tau_absolute'],abs(native['tau_tail01']-(tau[i]+tail)))
            maximum['tail_scaling_absolute']=max(maximum['tail_scaling_absolute'],abs(native['survival_tail01']-native['survival_tail0']*tail_factor),abs(native['cell_probability_tail01']-native['cell_probability_tail0']*tail_factor))
        for suffix,boundary in [('tail0',D(1)),('tail01',tail_factor)]:
            mass=exact(got[0]['survival_'+suffix])+sum((exact(r['cell_probability_'+suffix]) for r in got[:-1]),D(0))
            checks+=1
            if abs(mass-boundary)>ABS_P:failures.append({'history':h['history'],'field':'mass_'+suffix,'residual':str(mass-boundary)})
            maximum['mass_residual_'+suffix]=abs(mass-boundary)
        total+=checks
        histories.append({'history':h['history'],'checks':checks,'rows':len(src),'reference_tau0':str(tau[0]),'maximum_errors':{k:float(v) for k,v in maximum.items()}})
    result={'schema':'SYNC03_DECIMAL_ORACLE_V1','status':'PASS' if not failures else 'FAIL','precision_digits':70,'checks':total,'histories':histories,'failures':failures,'shared_authorities':['source endpoint densities and times','BASS constant values'],'independence':'independent Decimal arithmetic and analytic finite-cell probabilities; source chemistry not independently recalculated','excluded':'continuum interpolation/chemistry/finite-temperature validity'}
    (ROOT/'evidence/DECIMAL_RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2));return 0 if not failures else 1

if __name__=='__main__':sys.exit(main())
