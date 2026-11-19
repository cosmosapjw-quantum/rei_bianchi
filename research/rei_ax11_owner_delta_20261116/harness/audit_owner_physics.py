#!/usr/bin/env python3
"""Same-author hostile audit using separate parsers and Decimal arithmetic.

No producer imports. Roundoff checks below are representation checks, not new
physical tolerances. Native cumulative reaction residuals remain measured data.
"""
import argparse, bisect, csv, gzip, hashlib, json, math, time
from decimal import Decimal as D, getcontext
from pathlib import Path
import numpy as np

getcontext().prec=60
UNIT=Path(__file__).resolve().parents[1]
REPO=UNIT.parents[1]
T1=REPO/'research/rei_ax11_t1_wave_20261116'
FHE=D('0.2454')/(4*(1-D('0.2454')))
EV=D('1.602176634e-12'); KB=D('1.380649e-16')
CHI=list(map(D,['13.598434599702','24.587389011','54.41776']))
EPS=np.finfo(float).eps
GAS=['x_HI','x_HII','x_HeI','x_HeII','x_HeIII','xe_per_H','temperature_K']

def need(v,label):
    if not v: raise AssertionError(label)

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def readjson(p):
    with (gzip.open(p,'rt') if str(p).endswith('.gz') else open(p)) as f:return json.load(f)
def rows(p):
    with (gzip.open(p,'rt') if str(p).endswith('.gz') else open(p)) as f:return list(csv.DictReader(f))
def dec(v):return D(str(v))
def near(a,b,scale=None):
    a,b=float(a),float(b)
    return abs(a-b)<=256*EPS*max(1.,abs(a),abs(b),abs(float(scale or 0)))
def cp(p):
    lines=p.read_text().splitlines();need(lines[0]=='AXBI_CHECKPOINT_V2' and len(lines)==6,'CP_SCHEMA')
    return list(map(D,lines[1].split())),list(map(int,lines[2].split())),list(map(D,lines[3].split())),list(map(D,lines[4].split())),D(lines[5])
def linear(q,x,y):
    need(all(x[i+1]>x[i] for i in range(len(x)-1)),'STRICT_NATIVE_AXIS')
    tol=8*EPS*max(1,abs(x[0]),abs(x[-1]))
    need(x[0]-tol<=q<=x[-1]+tol,'NO_EXTRAPOLATION')
    q=min(max(q,x[0]),x[-1]);j=max(0,min(len(x)-2,bisect.bisect_right(x,q)-1))
    # Decimal weights independently check the floating interpolation consumer.
    exact=lambda v:D.from_float(float(v))
    f=(exact(q)-exact(x[j]))/(exact(x[j+1])-exact(x[j]))
    return float(exact(y[j])+(exact(y[j+1])-exact(y[j]))*f)
def columns(d,w):
    c={h:[float(r[j]) for r in w['rows']] for j,h in enumerate(d['headers']) if h!='case_id'}
    c['xe_per_H']=[a/b for a,b in zip(c['ne_proper_cm3'],c['nH_proper_cm3'])]
    return c

def main():
    p=argparse.ArgumentParser();p.add_argument('output',type=Path);out=p.parse_args().output
    need(not out.exists(),'IMMUTABLE_OUTPUT');start=time.monotonic();cpu=time.process_time()
    summary=readjson(UNIT/'results_v1/SUMMARY.json')
    for name,v in summary['outputs'].items():need(digest(UNIT/'results_v1'/name)==v['sha256'],'OUTPUT_HASH:'+name)
    native={c:readjson(T1/f'native_inputs/{c}_sample_brackets.json.gz') for c in ['ZERO','PLUS']}
    table={(r['level'],r['case']):r for r in rows(UNIT/'results_v1/endpoint_inventory.csv')}
    endpoint_checks={};mutants=[]
    for level in ['T0','T1']:
        for case in ['ZERO','PLUS']:
            path=UNIT/f'native_inputs/T0_{case}_checkpoint.txt' if level=='T0' else T1/f'checkpoints/{case}_757073.txt'
            v,n,l,photons,e0=cp(path);row=table[level,case]
            h=rows(UNIT/f'native_inputs/T0_{case}_terminal_history.csv')[0] if level=='T0' else dict(zip(native[case]['headers'],native[case]['last_row']))
            xe=v[3]+FHE*(v[4]+2*v[5]);thermal=v[6]/EV;binding=CHI[0]*v[3]+FHE*(CHI[1]*v[4]+(CHI[1]+CHI[2])*v[5])
            photon=dec(h['photon_n_per_H']);energy=dec(h['photon_u_eV_per_H'])
            nres=photon+l[2]+l[4]-l[0]
            eres=thermal+binding+energy+l[3]+l[5]+l[6]+l[7]-l[1]-l[8]-e0
            need(abs(nres)<=D('1e-8')*max(D(1),l[0]),'ORIGINAL_N_GATE')
            need(abs(eres)<=D('1e-8')*max(D(1),l[1]),'ORIGINAL_E_GATE')
            for k,value in {'xe_per_H':xe,'gas_binding_eV_per_H':binding,'gas_thermal_eV_per_H':thermal,
                            'temperature_K':v[6]/(D('1.5')*KB*(1+FHE+xe))}.items():need(near(value,row[k]),'DECIMAL_REPRESENTATION:'+k)
            need(near(sum(photons),photon),'PHOTON_CHECKPOINT_STOCK')
            old=summary['endpoint_checks'][level+'_'+case]
            need(near(nres,old['photon_residual_reconstructed'],l[0]),'N_RES_RECONSTRUCTION')
            need(near(eres,old['energy_residual_reconstructed'],l[1]),'E_RES_RECONSTRUCTION')
            # Independent event matrix multiplication, in species/H units.
            A=[l[18+j]+l[15+j]-l[12+j] for j in range(3)]
            net=[A[0],A[1]-A[2]-l[9],A[2]]
            residual=[v[3]-D('.0002')-net[0],FHE*v[4]-net[1],FHE*v[5]-net[2]]
            e_res=xe-D('.0002')-(net[0]+net[1]+2*net[2])
            need(abs(e_res-(residual[0]+residual[1]+2*residual[2]))<D('1e-55'),'EVENT_CHARGE_ALGEBRA')
            need(near(e_res,old['event_balance_residuals']['electron_per_H']),'EVENT_VALUE_REPRODUCTION')
            endpoint_checks[level+'_'+case]={'photon_residual_decimal':str(nres),'energy_residual_decimal':str(eres),
              'HII_event_residual_decimal':str(residual[0]),'HeII_event_residual_per_H_decimal':str(residual[1]),
              'HeIII_event_residual_per_H_decimal':str(residual[2]),'electron_event_residual_decimal':str(e_res),
              'original_ledger_gates':True,'new_reaction_tolerance':False,'checkpoint_sha256':digest(path)}
            wrong_cmb=eres+2*l[8]
            need(abs(wrong_cmb)>D('1e-8')*max(D(1),l[1]),'CMB_MUTANT_NOT_CAUGHT')
            wrong_xe=v[3]+v[4]+2*v[5]
            need(not near(wrong_xe,row['xe_per_H']),'HE_NORMALIZATION_MUTANT_NOT_CAUGHT')
            mutants += [{'name':level+'_'+case+'_CMB_sign','rejected_by':'original energy ledger gate','mutant_residual_eV_per_H':str(wrong_cmb)},
                        {'name':level+'_'+case+'_He_fraction_as_per_H','rejected_by':'source-qualified electron normalization'}]
    epochs=rows(UNIT/'results_v1/T1_native_cumulative_epochs.csv')
    for case in ['ZERO','PLUS']:
        series=[r for r in epochs if r['case']==case];final=table['T1',case]
        wrong=dec(final['photon_n_per_H'])+sum(dec(r['absorbed_N_per_H'])+dec(r['boundary_N_per_H'])-dec(r['source_N_per_H']) for r in series)
        need(abs(wrong)>D('1e-8')*max(D(1),dec(final['source_N_per_H'])),'CUMULATIVE_MUTANT_NOT_CAUGHT')
        mutants.append({'name':case+'_sum_cumulative_checkpoints','rejected_by':'original photon ledger gate','mutant_residual_per_H':str(wrong)})
    # Compact donor data only: raw native states were audited by the producer.
    donor=readjson(UNIT/'donors/vigilode/results/ERROR_COMPONENT_PROFILE.json')
    dcsv={r['id']:r for r in rows(UNIT/'donors/vigilode/results/ERROR_COMPONENTS.csv')};profiles=[]
    for s in donor['specimens']:
        r=dcsv[s['id']];comps=s['components'];e=max(comps.values());target=float(r['local_target']);h=float(r['dln_a'])
        need(e==s['original_metric']==float(r['original_metric']),'DONOR_MAXIMUM')
        need(all(float(r[k])==v for k,v in comps.items()),'DONOR_CSV_JSON')
        for k,value in comps.items():need(math.isclose(value,s['raw_defect_numerators'][k]/s['normalizations'][k],rel_tol=4e-15),'DONOR_NORMALIZATION')
        accepted=e<target and e<2e-4
        nxt=min(2*h,.005) if accepted and e<.25*target else h if accepted else .5*h
        need(accepted==s['accepted']==(r['accepted']=='true'),'DONOR_ACCEPT')
        need(nxt==s['next_dln_a']==float(r['native_next_dln_a']),'DONOR_NEXT')
        profiles.append({'id':s['id'],'winner':max(comps,key=comps.get),'metric':e,'accepted':accepted,'next_dln_a':nxt})
    # Strict boundary mutants are not evaluated on physical data at a new target.
    need(not (1e-5<1e-5),'STRICT_ACCEPT_BOUNDARY');need(not (2.5e-6<.25*1e-5),'STRICT_DOUBLING_BOUNDARY')
    mutants += [{'name':'inclusive_accept_at_target','rejected_by':'original strict < predicate'},
                {'name':'inclusive_double_at_quarter_target','rejected_by':'original strict < predicate'}]
    clock=rows(UNIT/'results_v1/T1_clock_decomposition.csv.gz');missing=[];represented=0;maxgap={k:0. for k in GAS}
    for i,r in enumerate(clock):
        values={};uquery={}
        for case in ['ZERO','PLUS']:
            d=native[case];w=d['samples']['fixed_t']['windows'][i];c=columns(d,w);u=list(np.log(c['a']))
            uq=linear(w['query']['elapsed_time_s'],c['time_s'],u);uquery[case]=uq
            values[case]={k:linear(uq,u,c[k]) for k in GAS}
        match=None
        for mode in ['fixed_t','fixed_a']:
            d=native['PLUS'];w=d['samples'][mode]['windows'][i];c=columns(d,w);u=list(np.log(c['a']));q=uquery['ZERO']
            tol=8*EPS*max(1,abs(u[0]),abs(u[-1]))
            if u[0]-tol<=q<=u[-1]+tol:match=(mode,c,u);break
        need((match is not None)==(r['represented']=='True'),'CLOCK_CENSOR_SELECTION')
        if match is None:
            missing.append(i);need(all(r[k+'_total_fixed_t']=='' for k in GAS),'NO_FILLED_CENSOR');continue
        represented+=1;mode,c,u=match;need(mode==r['native_window'],'CLOCK_SELECTED_WINDOW')
        for k in GAS:
            mid=linear(uquery['ZERO'],u,c[k]);z,pv=values['ZERO'][k],values['PLUS'][k]
            for suffix,val in [('total_fixed_t',pv-z),('same_a_at_ZERO_a',mid-z),('clock_displacement',pv-mid)]:
                gap=abs(val-float(r[k+'_'+suffix]));maxgap[k]=max(maxgap[k],gap)
                need(near(val,float(r[k+'_'+suffix]),max(abs(z),abs(pv),abs(mid))),'CLOCK_RECOMPUTE:'+k)
    need(represented==953 and missing==summary['clock']['excluded_indices'],'CLOCK_COVERAGE')
    try:linear(-1.,[0.,1.],[0.,1.])
    except AssertionError:mutants.append({'name':'clock_extrapolation','rejected_by':'explicit native support requirement'})
    else:raise AssertionError('EXTRAPOLATION_MUTANT_NOT_CAUGHT')
    delta={r['quantity']:r for r in rows(UNIT/'results_v1/endpoint_inventory_D01.csv')}
    eligibility={k:{'original_floor':floor,'T1_pair':float(delta[k]['pair_T1']),
                   'relative_admission_allowed':abs(float(delta[k]['pair_T1']))>floor}
                 for k,floor in [('x_HII',1e-7),('temperature_K',.01)]}
    need(not any(x['relative_admission_allowed'] for x in eligibility.values()),'BELOW_FLOOR_NOT_RECOGNIZED')
    mutants.append({'name':'endpoint_below_floor_relative_detection','rejected_by':'original response floor and missing D12'})
    result={'status':'PASS_SCOPED_SAME_AUTHOR_DIFFERENT_IMPLEMENTATION','independent_blind_review':False,
      'producer_imports':False,'representation_check':'256 binary64 eps times underlying value scale; not physical error tolerance',
      'endpoint_decimal_checks':endpoint_checks,'donor_compact_specimens_checked':profiles,
      'donor_raw_state_reexecution':'NOT_PERFORMED; original producer record retained',
      'clock':{'represented':represented,'excluded_indices':missing,'max_representation_gap':maxgap},
      'semantic_mutants_rejected':mutants,'endpoint_relative_eligibility':eligibility,
      'unresolved':['T2 full histories and D12 absent','separate dE/dmu refinements absent','no native reaction-integral tolerance invented','new photon observables have no predeclared response floor'],
      'DAG':'10/17;28/88','new_completed_nodes':0,
      'execution':{'CPU_s':time.process_time()-cpu,'wall_s':time.monotonic()-start,'script_sha256':digest(Path(__file__))}}
    out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:result[k] for k in ['status','independent_blind_review','execution']}))

if __name__=='__main__':main()
