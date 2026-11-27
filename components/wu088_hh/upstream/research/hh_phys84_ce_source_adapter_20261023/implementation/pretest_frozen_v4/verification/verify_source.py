"""Independent literal-decimal Fraction source oracle and interface controls.

This invokes the new instantaneous interface only. Persistent runner callbacks
are mocks. No parent scientific kernel, population solver or ODE is imported.
"""
from pathlib import Path
from fractions import Fraction as F
import argparse
import ast
import csv
import hashlib
import json
import math
import platform
import shutil
import sys
import traceback
from unittest.mock import patch

UNIT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(UNIT/'source'))
from source_adapter import SavedSource
import source_adapter
import run_source

CHECKS=[]
CASES=[]
MAXIMA={}
REAL_APPLICATION_CALLBACK_CALLS=[0]
FIXTURE_INTERFACE_EVALUATIONS=[0]
OWNER={'radiative_owner':'detached_own_spontaneous',
       'excited_state_owner':'explicit_1S_2S_2P','native_radiative_owner_active':False}


def check(ok,label):
    CHECKS.append({'label':label,'pass':bool(ok)})
    if not ok:raise AssertionError(label)


def refused(fn,label):
    try:fn()
    except (ValueError,TypeError,FileExistsError,FileNotFoundError,OverflowError) as error:
        check(True,label)
        return str(error)
    check(False,label+' DID_NOT_REFUSE')


def compare(actual,exact,gross,tolerance,label):
    a=F.from_float(actual)
    if gross==0:
        check(a==exact==0,label+':zero_gross')
        return
    ratio=abs(a-exact)/gross
    MAXIMA[label.split(':')[0]]=max(MAXIMA.get(label.split(':')[0],0.),float(ratio))
    check(ratio<=F(tolerance),label)


def oracle(state,rate):
    # All constants here are independently transcribed contract decimal leaves.
    d,k=F('10.20435'),F('0.00008617333262145179')
    n0,ns,np,ne=(state[x] for x in ('n1s','n2s','n2p','ne'))
    r=(ne*n0*rate['2S'][0],ne*n0*rate['2P'][0],
       ne*ns*rate['2S'][1],ne*np*rate['2P'][1],
       ns*F('8.229'),ns*F('0.000002496'),np*F('626000000'))
    dn=(-r[0]-r[1]+r[2]+r[3]+r[4]+r[5]+r[6],
        r[0]-r[2]-r[4]-r[5],r[1]-r[3]-r[6])
    q=d*(-r[0]-r[1]+r[2]+r[3])
    u=d*(r[0]+r[1]-r[2]-r[3]-r[4]-r[5]-r[6])
    e=d*(r[4]+r[5]+r[6])
    ge=sum(r)
    gth=d*sum(r[:4])
    factor=F(2)/(3*k*state['Nthermal'])
    return {'r':r,'dn':dn,'q':q,'u':u,'e':e,'photons':(2*r[4],r[5],r[6]),
            'Tdot':factor*q,'gross':(ge,d*ge,gth,factor*gth)}


def numerical(source):
    rates={}
    parent=UNIT.parent/'hh_phys83_ce_completion_20261023'
    with (parent/'results/rate_grid.csv').open() as stream:
        for row in csv.DictReader(stream):
            rates.setdefault(F(row['temperature_K']),{})[row['upper_level']]=(
                F(row['q_up_cm3_s']),F(row['q_down_cm3_s']))
    fixtures=json.loads((UNIT/'source/fixtures.json').read_text(),parse_float=F,parse_int=F)
    observed={}
    check(len(rates)==66 and all(set(x)=={'2S','2P'} for x in rates.values()),'oracle:66_pairs')
    for fixture in fixtures:
        name=fixture['id']
        exact_state={k:v for k,v in fixture.items() if k!='id'}
        state={k:float(v) for k,v in exact_state.items()}
        ref=oracle(exact_state,rates[exact_state['T_K']])
        for route in ('immediate_escape','emissivity_handoff'):
            label=name+'/'+route
            FIXTURE_INTERFACE_EVALUATIONS[0]+=1
            actual=source.evaluate(state,radiation_route=route,**OWNER)
            observed[(name,route)]=actual
            CASES.append(label)
            ge,gen,gth,gt=ref['gross']
            for index,value in enumerate(actual['event_intensities_cm3_s'].values()):
                compare(value,ref['r'][index],ref['r'][index],'2e-12','event:'+label+':'+str(index))
            for index,value in enumerate(actual['level_sources_cm3_s'].values()):
                compare(value,ref['dn'][index],ge,'2e-13','level:'+label+':'+str(index))
            energy_ref=(ref['q'],F(0),ref['u'],ref['e'] if route=='emissivity_handoff' else F(0),
                        ref['e'] if route=='immediate_escape' else F(0),F(0))
            for index,value in enumerate(actual['energy_columns_eV_cm3_s'].values()):
                compare(value,energy_ref[index],gen,'2e-13','energy:'+label+':'+str(index))
            compare(actual['emitted_energy_diagnostic_eV_cm3_s'],ref['e'],ref['e'],'2e-12','emission:'+label)
            for index,value in enumerate(actual['photon_sources_cm3_s'].values()):
                compare(value,ref['photons'][index],ref['photons'][index],'2e-12','photon:'+label+':'+str(index))
            compare(actual['total_photon_source_cm3_s'],sum(ref['photons']),sum(ref['photons']),
                    '2e-12','photon_total:'+label)
            compare(actual['temperature_source_K_s'],ref['Tdot'],gt,'2e-13','temperature:'+label)
            for index,value in enumerate(actual['gross'].values()):
                compare(value,ref['gross'][index],ref['gross'][index],'2e-12','gross:'+label+':'+str(index))
            compare(actual['residuals']['energy_eV_cm3_s'],F(0),gen,'2e-13','energy_residual:'+label)
            compare(actual['residuals']['nuclei_cm3_s'],F(0),ge,'2e-13','nuclei_residual:'+label)
            for field in ('electron_source_cm3_s','thermal_particle_source_cm3_s','charge_source_cm3_s'):
                check(actual[field]==0.,'number_zero:'+label+':'+field)
            check(actual['nuclei_source_cm3_s']==math.fsum(actual['level_sources_cm3_s'].values()),'actual_nuclear_residual:'+label)
            check(actual['residuals']['energy_eV_cm3_s']==math.fsum(actual['energy_columns_eV_cm3_s'].values()),'actual_energy_residual:'+label)
            check(F(actual['stored_temperature_label_K'])==exact_state['T_K'],'exact_saved_label:'+label)
    for fixture in fixtures:
        a=observed[(fixture['id'],'immediate_escape')]
        b=observed[(fixture['id'],'emissivity_handoff')]
        check(a['event_intensities_cm3_s']==b['event_intensities_cm3_s'],'route_same_events:'+fixture['id'])
        check(a['energy_columns_eV_cm3_s']['escaped_radiation']==b['energy_columns_eV_cm3_s']['radiation_injected'],
              'route_exclusive_destination:'+fixture['id'])
        check(a['energy_columns_eV_cm3_s']['radiation_injected']==b['energy_columns_eV_cm3_s']['escaped_radiation']==0.,
              'route_unused_zero:'+fixture['id'])
    ground=observed[('warm_ground','immediate_escape')]
    decay=observed[('pure_2s_decay','immediate_escape')]
    check(ground['energy_columns_eV_cm3_s']['gas_thermal']<0 and ground['emitted_energy_diagnostic_eV_cm3_s']==0,
          'ground_cooling_without_emission')
    check(decay['energy_columns_eV_cm3_s']['gas_thermal']==decay['temperature_source_K_s']==0 and
          decay['emitted_energy_diagnostic_eV_cm3_s']>0,'radiative_decay_without_thermal_source')
    r=decay['event_intensities_cm3_s']
    check(decay['photon_sources_cm3_s']['2gamma']==2*r['RAD_2S_2gamma'],'two_photon_count_doubled')
    compare(decay['emitted_energy_diagnostic_eV_cm3_s'],F('10.20435')*(F('8.229')+F('0.000002496')),
            F('10.20435')*(F('8.229')+F('0.000002496')),'2e-12','two_photon_energy_not_doubled')


def guards(source,work):
    state={'T_K':10000.,'n1s':1.,'n2s':0.,'n2p':0.,'ne':1.,'Nthermal':2.}
    def run(st=None,**kw):
        return source.evaluate(state if st is None else st,radiation_route=kw.pop('radiation_route','immediate_escape'),**(OWNER|kw))
    CASES.append('source_domain_owner_guards')
    for key in ('n1s','n2s','n2p','ne'):
        for value in (True,-1.,math.nan,math.inf,1.0001e18):
            refused(lambda key=key,value=value:run(state|{key:value}),'density_guard:'+key+':'+str(value))
    for value in (True,0.,-1.,math.nan,math.inf,1e21,1.):
        refused(lambda value=value:run(state|{'Nthermal':value}),'Nthermal_guard:'+str(value))
    for value in (True,254.,50001.,10001.,math.nan,math.inf):
        refused(lambda value=value:run(state|{'T_K':value}),'temperature_guard:'+str(value))
    refused(lambda:run({k:v for k,v in state.items() if k!='n2s'}),'missing_state')
    refused(lambda:run(state|{'unexpected':1.}),'extra_state')
    for route in ('both','',None,['immediate_escape','emissivity_handoff']):
        refused(lambda route=route:run(radiation_route=route),'route_guard:'+str(route))
    refused(lambda:run(radiative_owner='native'),'wrong_radiative_owner')
    for active in (True,0,None):
        refused(lambda active=active:run(native_radiative_owner_active=active),'owner_conflict:'+str(active))
    refused(lambda:run(excited_state_owner='ground_only'),'ground_only_owner')
    refused(lambda:run(excited_state_owner=None),'missing_excited_owner')
    refused(lambda:run(state|{'T_K':255.,'n1s':1e-200,'ne':1e-200}),'positive_event_underflow')
    refused(lambda:run(state|{'n1s':0.,'ne':0.,'n2s':5e-324,'Nthermal':1.}),'radiative_branch_underflow')
    refused(lambda:source_adapter.product(1e308,1e308),'positive_product_overflow')
    refused(lambda:source_adapter.temperature_source(5e-324,1e20),'temperature_division_underflow')
    refused(lambda:run(state|{'ne':10**1000}),'integer_overflow')
    # All four wrong-pin controls use copies and never modify the inherited unit.
    parent=UNIT.parent/'hh_phys83_ce_completion_20261023'
    for target in ('results/rate_grid.csv','CONTRACT.json','results/SCIENCE_IDENTITY.json','results/COMPLETE.json'):
        copy=work/('wrong_pin_'+target.replace('/','_'))
        copy.mkdir()
        for name in source_adapter.PINS:
            path=copy/name
            path.parent.mkdir(exist_ok=True)
            shutil.copyfile(parent/name,path)
        with (copy/target).open('ab') as stream:stream.write(b'\n')
        refused(lambda copy=copy:SavedSource(parent=copy),'wrong_pin:'+target)
    badcontract=work/'bad_adapter_contract.json'
    badcontract.write_bytes((UNIT/'CONTRACT.json').read_bytes()+b'\n')
    refused(lambda:SavedSource(contract=badcontract),'wrong_adapter_contract_pin')
    raw=(parent/'results/rate_grid.csv').read_bytes()
    refused(lambda:SavedSource._parse(raw+raw.splitlines(keepends=True)[1]),'duplicate_row')
    refused(lambda:SavedSource._parse(b'\n'.join(raw.splitlines()[:-1])),'missing_pair')
    refused(lambda:SavedSource._parse(raw.replace(b'1.2039644274430618e-209',b'0.0',1)),'zero_stored_rate')


def persistent_controls(work):
    CASES.append('mock_only_persistence')
    baseline_identity=run_source.build_identity()
    with patch.object(platform,'python_version',return_value='999.0.RUNTIME_ONLY_DIAGNOSTIC'), \
         patch.object(platform,'python_implementation',return_value='MOCK_RUNTIME'):
        check(run_source.build_identity()==baseline_identity,'runtime_version_does_not_change_scientific_identity')
    callback_count=[0]
    def callback():
        callback_count[0]+=1
        return [{'MOCK_ONLY':True,'index':k} for k in range(16)]
    ident={'schema':'MOCK_ONLY_PHYS84_TEST','pin':'A'}
    out=work/'MOCK_ONLY_complete'
    refused(lambda:run_source.persist(out,ident,callback),'new_requires_authorization')
    check(not out.exists(),'no_creation_without_authorization')
    new=run_source.persist(out,ident,callback,allow_new=True)
    check(new['callback_calls']==1 and callback_count==[1],'mock_new_one_callback')
    before={p.name:p.read_bytes() for p in out.iterdir()}
    resumed=run_source.persist(out,ident,callback,resume=True)
    check(resumed['callback_calls']==0 and callback_count==[1],'mock_resume_zero_callback')
    check(before=={p.name:p.read_bytes() for p in out.iterdir()},'mock_resume_bytes_unchanged')
    refused(lambda:run_source.persist(out,ident,callback,allow_new=True),'create_only_refusal')
    refused(lambda:run_source.persist(out,ident|{'pin':'B'},callback,resume=True),'identity_mismatch_refusal')
    refused(lambda:run_source.persist(work/'missing',ident,callback,resume=True),'resume_missing_refusal')
    for file in ('source_rows.json','IDENTITY.json','COMPLETE.json'):
        case=work/('MOCK_ONLY_corrupt_'+file)
        shutil.copytree(out,case)
        with (case/file).open('ab') as stream:stream.write(b' ')
        # COMPLETE whitespace is a byte corruption too: result/identity compare is exact,
        # and the completion must also retain its original canonical bytes.
        refused(lambda case=case:run_source.persist(case,ident,callback,resume=True),'corrupt_refusal:'+file)
    incomplete=work/'MOCK_ONLY_incomplete'
    incomplete.mkdir()
    refused(lambda:run_source.persist(incomplete,ident,callback,resume=True),'incomplete_refusal')
    extra=work/'MOCK_ONLY_extra'
    shutil.copytree(out,extra)
    (extra/'EXTRA').write_text('mock')
    refused(lambda:run_source.persist(extra,ident,callback,resume=True),'extra_file_refusal')
    def fail():raise RuntimeError('EXPECTED_MOCK_FAILURE')
    failed=work/'MOCK_ONLY_failed'
    try:run_source.persist(failed,ident,fail,allow_new=True)
    except RuntimeError:check(True,'mock_failure_preserved')
    check(failed.exists() and (failed/'IDENTITY.json').exists() and not (failed/'COMPLETE.json').exists(),'failed_directory_retained')
    refused(lambda:run_source.persist(failed,ident,callback,resume=True),'failed_completion_refusal')
    check(callback_count==[1],'all_refused_resumes_zero_callbacks')


def static_controls():
    CASES.append('no_old_scientific_callbacks')
    forbidden=('matched_ce','frozen_star','nuclear_ownership','ci_finite_c22d')
    check(not any(x in sys.modules for x in forbidden),'forbidden_modules_absent')
    for name in ('source_adapter.py','run_source.py'):
        tree=ast.parse((UNIT/'source'/name).read_text())
        imports=[]
        for node in ast.walk(tree):
            if isinstance(node,ast.Import):imports.extend(a.name for a in node.names)
            if isinstance(node,ast.ImportFrom):imports.append(node.module or '')
        check(not any(any(x in imp for x in forbidden) for imp in imports),'no_parent_science_import:'+name)
    check(REAL_APPLICATION_CALLBACK_CALLS==[0], 'real_callback_zero_invocations')


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--attempt',type=Path,required=True)
    a=p.parse_args()
    a.attempt.mkdir(exist_ok=False)
    source_files={str(p.relative_to(UNIT)):hashlib.sha256(p.read_bytes()).hexdigest()
                  for folder in ('source','verification') for p in sorted((UNIT/folder).glob('*.py'))}
    report={'schema':'PHYS84_INDEPENDENT_SOURCE_VERIFICATION_V1','source_SHA256':source_files,
            'real_application_callback_calls':0,'old_rate_callbacks':0,'old_population_callbacks':0,
            'old_ODE_callbacks':0,'historical_replays':0,'expected_fixture_interface_evaluations':16,
            'persistent_callback_kind':'MOCK_ONLY','inherited_budget_remaining':None}
    def forbidden_real_callback():
        REAL_APPLICATION_CALLBACK_CALLS[0]+=1
        raise AssertionError('REAL_APPLICATION_CALLBACK_FORBIDDEN_IN_VERIFICATION')
    run_source.real_callback=forbidden_real_callback
    try:
        source=SavedSource()
        numerical(source)
        guards(source,a.attempt)
        persistent_controls(a.attempt)
        static_controls()
        report['status']='PASS'
    except Exception:
        report['status']='FAIL_FIRST_ATTEMPT_PRESERVED'
        report['failure_traceback']=traceback.format_exc()
        raise
    finally:
        report.update(cases=CASES,case_count=len(CASES),assertion_count=len(CHECKS),
                      assertions=CHECKS,max_normalized_errors=MAXIMA,
                      real_application_callback_calls=REAL_APPLICATION_CALLBACK_CALLS[0],
                      fixture_interface_evaluations=FIXTURE_INTERFACE_EVALUATIONS[0])
        with (a.attempt/'REPORT.json').open('x') as stream:json.dump(report,stream,indent=2);stream.write('\n')
        print(json.dumps({k:report[k] for k in ('status','case_count','assertion_count','max_normalized_errors')},sort_keys=True))


if __name__=='__main__':main()
