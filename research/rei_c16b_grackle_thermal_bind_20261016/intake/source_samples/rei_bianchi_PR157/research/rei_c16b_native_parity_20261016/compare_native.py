#!/usr/bin/env python3
"""Frozen native point contract; Python survivor/photo calculation is independent."""
import argparse, importlib.util, json, math, sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
REF=HERE.parent/'rei_c16b_thermal_bridge_20261016'
# Explicit source_aware binding, rather than an ambient module search.
spec=importlib.util.spec_from_file_location('source_aware',REF/'source_aware.py')
src=importlib.util.module_from_spec(spec);sys.modules['source_aware']=src;spec.loader.exec_module(src)
spec=importlib.util.spec_from_file_location('native_photo_contract',REF/'src/native_photo_contract.py')
photo_module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=photo_module;spec.loader.exec_module(photo_module)
EPS=2**-52; RTOL=1e-12; EV=1.602176634e-12
checks=[]; independent=[]
def add(case,name,ok,**kw):
    checks.append(dict(case=case,check=name,pass_check=bool(ok),**kw))
def relative(case,name,native,reference):
    scale=max(abs(native),abs(reference))
    err=abs(native-reference)
    add(case,name,err<=RTOL*scale if scale else err==0,kind='positive_relative' if scale else 'exact_zero',native=native,reference=reference,relative_error=err/scale if scale else 0.)
def identity(case,name,terms):
    residual=math.fsum(terms); gross=math.fsum(map(abs,terms)); bound=128*EPS*gross
    add(case,name,abs(residual)<=bound if gross else residual==0,kind='cancellation',residual=residual,gross_scale=gross,roundoff_bound=bound,normalized_residual=abs(residual)/bound if bound else 0.)
def exact(case,name,native,reference):
    add(case,name,native==reference,kind='exact',native=native,reference=reference)
def evaluate(row):
    c=row['id']; nh=row['nh']; yy=row['yhe']; x,y,z=row['fractions']; dt=row['dt_s']
    gas=src.Gas(1-x,x,yy*(1-(y+z)),yy*y,yy*z)
    initial=[src.Node(q,mu,n) for q,mu,n in zip(row['q_ev'],row['mu0'],row['input_counts'])]
    energies=[src.physical_energy(p,row['a'],row['b']) for p in initial]
    absorber=(gas.h_i,gas.he_i,gas.he_ii)
    sigmas=[[src.verner_mb(i,e)*src.MB_CM2 for i in range(3)] for e in energies]
    kappa=[math.fsum(nh*a*s for a,s in zip(absorber,sigma)) for sigma in sigmas]
    exposures=[dt*src.C_CM_S*k for k in kappa]
    survivor=[p.n_per_h/(1+expo) for p,expo in zip(initial,exposures)]
    state=src.State(tuple(src.Node(p.q_ev,p.mu0,n) for p,n in zip(initial,survivor)),gas,row['a'],row['b'])
    photo=photo_module.photo_point(state,nh)
    expected_events=[dt*a*g for a,g in zip(absorber,photo.gamma_s)]
    expected_bind=math.fsum(a*chi for a,chi in zip(expected_events,src.CHI_EV))
    expected_heat=math.fsum(dt*a*h/EV for a,h in zip(absorber,photo.heat_erg_per_absorber_s))
    independent.append(dict(id=c,dt_s=dt,energies_ev=energies,sigma_cm2=sigmas,kappa_cm1=kappa,exposures=exposures,survivors=survivor,gamma_s=photo.gamma_s,heat_erg_per_absorber_s=photo.heat_erg_per_absorber_s,events_per_h=expected_events,binding_ev_per_h=expected_bind,heat_ev_per_h=expected_heat))
    exact(c,'node_count',row['node_count'],len(initial)); exact(c,'single_transport_worker',row['transport_workers'],1)
    for i,e in enumerate(energies):
        relative(c,f'geometry_energy[{i}]',row['actual_energy_ev'][i],e)
        for a in range(3):
            relative(c,f'sigma[{i},{a}]',row['sigma_cm2'][i][a],sigmas[i][a])
            exact(c,f'fit_branch[{i},{a}]',row['fit_active'][i][a],e>=src.VERNER_ROWS[a][0])
    if c.startswith('threshold') and '_equal_' in c:
        a=int(c[len('threshold')]); exact(c,'threshold_exact_energy',row['actual_energy_ev'][0],src.VERNER_ROWS[a][0])
        add(c,'threshold_equal_positive_heat',row['heat_erg_per_absorber_s'][a]>0,kind='condition')
    for i,(native,ref) in enumerate(zip(row['survivors_cells'],survivor+[0.]*(3-len(survivor)))):
        relative(c,f'survivor[{i}]',native,ref)
        if i<len(initial): relative(c,f'survivor_energy_ref[{i}]',row['survivor_energy_ref_cells'][i],initial[i].q_ev*survivor[i])
    for i in range(3):
        relative(c,f'gamma[{i}]',row['gamma_s'][i],photo.gamma_s[i])
        relative(c,f'heat[{i}]',row['heat_erg_per_absorber_s'][i],photo.heat_erg_per_absorber_s[i])
        relative(c,f'absorbed[{i}]',row['absorbed_per_h'][i],expected_events[i])
        relative(c,f'absorber[{i}]',row['absorbers_cm3'][i],nh*absorber[i])
    relative(c,'binding_absorbed',row['binding_ev_per_h'],expected_bind)
    relative(c,'heat_absorbed',row['heat_ev_per_h'],expected_heat)
    sink_terms=[term for n,s in zip(row['input_number_cells'],row['survivors_cells']) for term in (n,-s)]
    identity(c,'photon_sink',sink_terms+[-v for v in row['absorbed_per_h']])
    # The participating subtraction operands define the cancellation scale.
    energy_operands=[]
    for i,e in enumerate(row['actual_energy_ev']):energy_operands += [e*row['input_counts'][i],-e*row['survivors_cells'][i]]
    identity(c,'photon_energy_ledger',energy_operands+[-row['binding_ev_per_h'],-row['heat_ev_per_h']])
    on=row['on']; off=row['off']; chi=src.CHI_EV
    for label,rhs in [('on',on),('off',off)]:
        d=rhs['species_chemical_cm3_s']; events=rhs['photo_events_cm3_s']
        identity(c,label+'_H',d[:2]);identity(c,label+'_He',d[2:5]);identity(c,label+'_charge',[d[5],-d[1],-d[3],-2*d[4]])
        identity(c,label+'_micro_energy',[rhs['thermal_micro_erg_cm3_s'],rhs['binding_micro_erg_cm3_s'],rhs['escape_erg_cm3_s'],-rhs['cmb_to_gas_erg_cm3_s'],-rhs['photo_input_erg_cm3_s']])
        identity(c,label+'_binding_from_species',[EV*chi[0]*d[1],EV*chi[1]*d[3],EV*chi[1]*d[4],EV*chi[2]*d[4],-rhs['binding_micro_erg_cm3_s']])
        identity(c,label+'_w_from_thermal',[nh*rhs['w_dt_erg_per_h_s'],-rhs['thermal_micro_erg_cm3_s']])
        particles=nh+nh*yy+row['ne']; temp=row['temperature']; kb=row['kb_erg_k']
        identity(c,label+'_dT_EOS',[rhs['temperature_dt_k_s'], -2*nh*rhs['w_dt_erg_per_h_s']/(3*kb*particles),temp*d[5]/particles])
        for i,j,denom in [(0,1,nh),(1,3,nh*yy),(2,4,nh*yy)]:
            if denom:identity(c,f'{label}_fraction[{i}]',[rhs['fraction_dt'][i],-d[j]/denom])
            else:exact(c,f'{label}_noHe_fraction[{i}]',rhs['fraction_dt'][i],0.)
        # Exported native process decomposition independently recomposes each owner.
        photoheat=math.fsum(row['absorbers_cm3'][i]*row['heat_erg_per_absorber_s'][i] for i in range(3)) if label=='on' else 0.
        phbind=[EV*chi[i]*events[i] for i in range(3)]
        ci=rhs['ci_thermal_sink_erg_cm3_s']; rr=rhs['rr_thermal_sink_erg_cm3_s']; dr=rhs['dr_thermal_sink_erg_cm3_s']; ce=rhs['ce_thermal_sink_erg_cm3_s']; ff=rhs['freefree_thermal_sink_erg_cm3_s']
        identity(c,label+'_thermal_owners',[rhs['thermal_micro_erg_cm3_s'],-photoheat,*ci,*rr,dr,*ce,ff,-rhs['cmb_to_gas_erg_cm3_s']])
        capture=[EV*chi[i]*rhs['rr_events_cm3_s'][i] for i in range(3)]+[EV*chi[1]*rhs['dr_events_cm3_s']]
        identity(c,label+'_binding_owners',[rhs['binding_micro_erg_cm3_s'],*[-v for v in phbind],*[-v for v in ci],*capture])
        identity(c,label+'_escape_owners',[rhs['escape_erg_cm3_s'],*[-v for v in capture],*[-v for v in rr],-dr,*[-v for v in ce],-ff])
    for i in range(3):relative(c,f'event_from_native_rhs[{i}]',row['absorbed_per_h'][i],dt*on['photo_events_cm3_s'][i]/nh)
    identity(c,'photon_energy_rhs',energy_operands+[-dt*on['photo_input_erg_cm3_s']/(nh*EV)])
    pe=on['photo_events_cm3_s']; stoich=[[-pe[0]],[pe[0]],[-pe[1]],[pe[1],-pe[2]],[pe[2]],[pe[0],pe[1],pe[2]]]
    for j in range(6):identity(c,f'on_off_species[{j}]',[on['species_chemical_cm3_s'][j],-off['species_chemical_cm3_s'][j],*[-v for v in stoich[j]]])
    phheat=[row['absorbers_cm3'][i]*row['heat_erg_per_absorber_s'][i] for i in range(3)]
    phbind=[EV*chi[i]*pe[i] for i in range(3)]
    for key,terms in [('thermal_micro_erg_cm3_s',phheat),('binding_micro_erg_cm3_s',phbind),('photo_input_erg_cm3_s',phheat+phbind)]:
        identity(c,'on_off_'+key,[on[key],-off[key],*[-v for v in terms]])
    identical=['ci_events_cm3_s','rr_events_cm3_s','dr_events_cm3_s','ci_thermal_sink_erg_cm3_s','rr_thermal_sink_erg_cm3_s','dr_thermal_sink_erg_cm3_s','ce_thermal_sink_erg_cm3_s','freefree_thermal_sink_erg_cm3_s','escape_erg_cm3_s','cmb_to_gas_erg_cm3_s','expansion_work_erg_cm3_s','ci_floor_events_cm3_s','ce_cap_cooling_erg_cm3_s','excluded_dr_cooling_erg_cm3_s']
    for key in identical:exact(c,'on_off_identical_'+key,on[key],off[key])
    relative(c,'EOS_ne',row['ne'],nh*x+nh*yy*(y+2*z))
    relative(c,'EOS_temperature',row['temperature'],2*nh*row['w']/(3*row['kb_erg_k']*(nh+nh*yy+row['ne'])))
    relative(c,'EOS_u',row['u'],nh*row['w'])
    rates=row['rates']; ne=row['ne']; ions=[nh*x,nh*yy*y,nh*yy*z]
    for i in range(3):
        relative(c,f'CI_rate_event[{i}]',on['ci_events_cm3_s'][i],ne*row['absorbers_cm3'][i]*rates['ci_cm3_s'][i])
        relative(c,f'RR_rate_event[{i}]',on['rr_events_cm3_s'][i],ne*ions[i]*rates['rr_cm3_s'][i])
    relative(c,'DR_rate_event',on['dr_events_cm3_s'],ne*ions[1]*rates['dr_cm3_s'])
    if dt==1e16:add(c,'stiff_exposure',max(exposures)>=1e6 and all(v>0 for v in survivor),kind='condition',maximum_exposure=max(exposures))

def main():
    parser=argparse.ArgumentParser();parser.add_argument('raw',type=Path);parser.add_argument('--out',type=Path,default=HERE/'evidence/native');args=parser.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    rows=[json.loads(line) for line in args.raw.read_text().splitlines() if line]
    for row in rows:evaluate(row)
    exact('matrix','case_count',len(rows),48)
    # Representative active native owners and both signs, no demand on each case.
    for name,test in [('RR',lambda r:any(v>0 for v in r['on']['rr_events_cm3_s'])),('CI',lambda r:any(v>0 for v in r['on']['ci_events_cm3_s'])),('DR_high',lambda r:r['on']['dr_events_cm3_s']>0),('DR_low',lambda r:r['rates']['dr_low_branch'] and r['on']['dr_events_cm3_s']==0),('CE',lambda r:any(v>0 for v in r['on']['ce_thermal_sink_erg_cm3_s'])),('freefree',lambda r:r['on']['freefree_thermal_sink_erg_cm3_s']>0),('CI_floor',lambda r:any(v>0 for v in r['on']['ci_floor_events_cm3_s'])),('CE_cap',lambda r:any(v>0 for v in r['on']['ce_cap_cooling_erg_cm3_s'])),('CMB_heating',lambda r:r['on']['cmb_to_gas_erg_cm3_s']>0),('CMB_cooling',lambda r:r['on']['cmb_to_gas_erg_cm3_s']<0)]:
        hits=[r['id'] for r in rows if test(r)];add('matrix','representative_'+name,bool(hits),kind='coverage',cases=hits)
    nonstiff=[max(v['exposures']) for v in independent if v['id'].startswith('mixed_b0_T10000_') and v['dt_s']==1e9]
    add('matrix','nonstiff_exposure',bool(nonstiff) and all(.1<=v<=1 for v in nonstiff),kind='condition',exposures=nonstiff)
    failures=[v for v in checks if not v['pass_check']]
    relative_checks=[v for v in checks if v['kind']=='positive_relative']; cancellations=[v for v in checks if v['kind']=='cancellation']
    summary=dict(status='PASS' if not failures else 'HOLD',cases=len(rows),checks=len(checks),failures=len(failures),relative_tolerance=RTOL,cancellation_factor_eps=128,max_positive_relative_error=max(v['relative_error'] for v in relative_checks),exact_zero_comparisons=sum(v['kind']=='exact_zero' for v in checks),max_cancellation_normalized_residual=max(v['normalized_residual'] for v in cancellations),claim_ceiling='native point photo parity and energy ownership with fixed-opacity finite-dt absorption',independent_python_source=str(REF/'source_aware.py'))
    species_summary={}
    for quantity in ['gamma','heat']:
        entries=[]
        for i,species in enumerate(src.SPECIES):
            selected=[v for v in checks if v['check']==f'{quantity}[{i}]']
            nonzero=[v for v in selected if v['kind']=='positive_relative']
            entries.append(dict(species=species,unit='s^-1 per absorber' if quantity=='gamma' else 'erg per absorber s^-1',max_absolute_error=max(abs(v['native']-v['reference']) for v in selected),max_relative_error=max((v['relative_error'] for v in nonzero),default=0.),nonzero_comparisons=len(nonzero),exact_zero_comparisons=len(selected)-len(nonzero)))
        species_summary[quantity]=entries
    summary['photo_component_errors']=species_summary
    groups=[('hydrogen','cm^-3 s^-1',lambda n:n.endswith('_H')),('helium','cm^-3 s^-1',lambda n:n.endswith('_He')),('charge','cm^-3 s^-1',lambda n:n.endswith('_charge')),('photon_number','per H',lambda n:n=='photon_sink'),('photon_energy','eV per H',lambda n:n in ['photon_energy_ledger','photon_energy_rhs']),('micro_energy_including_signed_CMB','erg cm^-3 s^-1',lambda n:n.endswith('_micro_energy')),('binding_from_species','erg cm^-3 s^-1',lambda n:n.endswith('_binding_from_species')),('temperature_EOS','K s^-1',lambda n:n.endswith('_dT_EOS'))]
    summary['residual_maxima']={}
    for label,unit,predicate in groups:
        selected=[v for v in cancellations if predicate(v['check'])]
        raw=max(selected,key=lambda v:abs(v['residual'])); normalized=max(selected,key=lambda v:v['normalized_residual'])
        summary['residual_maxima'][label]=dict(unit=unit,max_absolute_residual=abs(raw['residual']),signed_residual_at_max=raw['residual'],gross_scale_at_max=raw['gross_scale'],roundoff_bound_at_max=raw['roundoff_bound'],case_at_max=raw['case'],check_at_max=raw['check'],max_normalized_residual=normalized['normalized_residual'],case_at_max_normalized=normalized['case'])
    summary['CMB_exchange']=dict(unit='erg cm^-3 s^-1',minimum_into_gas=min(r['on']['cmb_to_gas_erg_cm3_s'] for r in rows),maximum_into_gas=max(r['on']['cmb_to_gas_erg_cm3_s'] for r in rows),reservoir_sign='negative of native cmb_to_gas',ledger_group='micro_energy_including_signed_CMB')
    for name,value in [('checks.json',checks),('independent_python.json',independent),('summary.json',summary),('first_failures.json',failures)]:
        dest=args.out/name
        if name=='first_failures.json' and dest.exists():dest=args.out/'latest_failures.json'
        dest.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
    print(json.dumps(summary,indent=2));return 0 if not failures else 1
if __name__=='__main__':sys.exit(main())
