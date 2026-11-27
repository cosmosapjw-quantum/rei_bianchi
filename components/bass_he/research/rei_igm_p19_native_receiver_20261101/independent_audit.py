#!/usr/bin/env python3
"""Independent audit of derived 46,080-row published source transfer; no import crosswalk."""
from pathlib import Path
import csv,gzip,hashlib,json,math
from decimal import Decimal,localcontext

def D(x):return Decimal(x)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def audit(root:Path):
    data=json.loads((root/'results/SCIENCE_RESULTS.json').read_text())
    file=root/'results'/data['source_data_csv']
    assert sha(file)==data['source_data_csv_sha256']
    groups=list(csv.DictReader((root/'results/ORIGINAL_FOUR_GROUP_PHOTON_ENERGY.csv').open()))
    assert len(groups)==4
    with localcontext() as ctx:
        ctx.prec=72
        accum={k:Decimal(0) for k in ['N_HI','N_HeI','N_HeII','native_HI_events_s','native_HeI_events_s','native_HeII_events_s','P19log_HI_events_s','P19log_HeI_events_s','P19log_HeII_events_s','native_photoheat_erg_s','P19log_excess_heat_erg_s','P19linear_excess_heat_erg_s']}
        rows=0;negative_counts=0;max_native_ratio_err=Decimal(0)
        snapshots=[]
        with gzip.open(file,'rt') as f:
            for rec in csv.DictReader(f):
                rows+=1
                assert int(rec['node'])==rows-1
                if float(rec['N_HI'])<=0 or float(rec['N_HeI'])<=0 or float(rec['N_HeII'])<=0:negative_counts+=1
                for key in accum:accum[key]+=D(rec[key])
                for sp in ('HI','HeI'):
                    quotient=D(rec[f'native_{sp}_events_s'])/D(rec[f'N_{sp}'])
                    target=D(repr(data['native_gammas_per_target_s'][sp]))
                    error=abs(quotient/target-1)
                    max_native_ratio_err=max(max_native_ratio_err,error)
                if rows in (1,2,3,256,4096,12001,23040,35001,46080):snapshots.append(rec)
        assert rows==46080 and negative_counts==0
        checks={}
        for species in ('HI','HeI','HeII'):
            y=D(repr(data['native_global_neutral_counts'][species]))
            if abs(accum[f'N_{species}']/y-1)>D('3e-7'):raise AssertionError('original element totals mismatch: '+species)
            n=D(repr(data['native_source_events_per_s'][species]))
            if n and abs(accum[f'native_{species}_events_s']/n-1)>D('1e-12'):raise AssertionError('original source rate mismatch: '+species)
            checks[species]={'source_neutral_count_relative':str(accum[f'N_{species}']/y-1),
                             'native_photo_events_relative':str(accum[f'native_{species}_events_s']/n-1) if n else 'EXACT_ZERO'}
            pn=D(repr(data['P19_log_counterfactual']['absorbed_events_per_s'][species]))
            if abs(accum[f'P19log_{species}_events_s']/pn-1)>D('3e-7'):raise AssertionError('P19 formal event budget mismatch')
        for channel,kind in [('native_photoheat_erg_s',None),('P19log_excess_heat_erg_s','log'),('P19linear_excess_heat_erg_s','linear')]:
            expected=(data['native_total_photoheat_erg_s'] if kind is None else data[f'P19_{kind}_counterfactual']['total_excess_heat_erg_s'])
            rel=accum[channel]/D(repr(expected))-1
            if abs(rel)>D('1e-10'):raise AssertionError('total photoheating source discrepancy')
            checks[channel]={'relative_error':str(rel)}
        ws=list(csv.DictReader((root/'results/NINE_ORIGINAL_NODE_WITNESSES.csv').open()))
        assert len(ws)==9
        assert all(a['node']==b['node'] and a['P19log_HI_events_s']==b['P19log_HI_events_s'] for a,b in zip(ws,snapshots))
        g_native=sum((D(x['species_HI_photons_s'])+D(x['species_HeI_photons_s'])+D(x['species_HeII_photons_s']) for x in groups),Decimal(0))
        native_tot=sum((D(repr(x)) for x in data['native_source_events_per_s'].values()),Decimal(0))
        assert abs(g_native/native_tot-1)<D('2e-12')
        passed={'schema':'BASS_HE_TO_REI_CROSSWALK_INDEPENDENT_AUDIT_V1','unique_original_physical_nodes':rows,
                'source_group_rows':len(groups),'witnesses':len(ws),'invalid_positive_populations':negative_counts,
                'max_uniform_native_gamma_relative_error':str(max_native_ratio_err),'diagnostics':checks,
                'data_sha256':sha(file),'original_sources_used':data['source_input_immutable_sha256'],
                'status':'NUMERICALLY_CHECKED_SOURCE_CONDITIONAL_ONLY','REI_DAG':'28/88','BASS_HE_DAG':'14/18','canonical_delta':0}
        (root/'results/INDEPENDENT_AUDIT.json').write_text(json.dumps(passed,indent=2,sort_keys=True)+'\n')
        print(json.dumps({'rows':rows,'max_uniform_native_gamma_relative_error':str(max_native_ratio_err),'status':passed['status']},sort_keys=True))
        return passed

if __name__=='__main__':audit(Path(__file__).resolve().parent)