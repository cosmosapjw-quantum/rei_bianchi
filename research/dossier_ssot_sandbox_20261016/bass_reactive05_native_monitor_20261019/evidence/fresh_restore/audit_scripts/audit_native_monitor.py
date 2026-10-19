#!/usr/bin/env python3
"""Independent streaming audit of BR05 actual-birth/retained-cohort CSVs.

All joins, clocks, source modulation, Killing kinematics, rates, populations,
and template aggregate fields are checked. Decimal90 quantile-space W1/CDF
checks cover every shared rule and one predeclared template per rule.
"""
from __future__ import annotations
import argparse
import csv
from decimal import Decimal, localcontext
import hashlib
import itertools
import json
import math
from pathlib import Path
import struct
import sys
import time

from monitor_reference import age_reference, opacity, ray_from_killing, sfr_from_volume, CHI, EV_J

ROOT = Path(__file__).resolve().parents[1]
SPECIES = ('Neutron', 'H1Neutral', 'H1Ionized', 'DNeutral', 'DIonized', 'TNeutral', 'TIonized',
           'He3Neutral', 'He3SinglyIonized', 'He3DoublyIonized', 'He4Neutral', 'He4SinglyIonized', 'He4DoublyIonized')
CHARGE = (0, 0, 1, 0, 1, 0, 1, 0, 1, 2, 0, 1, 2)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def csv_rows(path):
    with path.open(newline='') as stream:
        for row in csv.DictReader(stream):
            require(None not in row and None not in row.values(), f'partial CSV: {path}')
            yield row


def bit(x):
    return struct.pack('>d', float(x))


def file_sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024*1024), b''):
            h.update(chunk)
    return h.hexdigest()


class Checks:
    def __init__(self):
        self.counts = {}
        self.maxima = {}

    def close(self, name, actual, expected, rtol=3e-13, atol=0.0):
        a, b = float(actual), float(expected)
        require(math.isfinite(a) and math.isfinite(b), f'{name}: nonfinite')
        error = abs(a-b)
        scale = max(abs(a), abs(b))
        self.counts[name] = self.counts.get(name, 0)+1
        self.maxima[name] = max(self.maxima.get(name, 0.0), error/scale if scale else 0.0)
        require(error <= atol+rtol*scale, f'{name}: {a:.17e} vs {b:.17e}')


def index_rows(path, fields):
    result = {}
    for row in csv_rows(path):
        key = tuple(int(row[x]) for x in fields)
        require(key not in result, f'duplicate key {key}: {path}')
        result[key] = row
    return result


def certificate_checks(check, row, prefix, tau, nodes, count_scale=1.0):
    reference = age_reference(tau, nodes)
    mapping = {'exact_mass': 'exact_mass', 'discrete_mass': 'mass',
               'cdf_sup': 'cdf_sup', 'w1_normalized': 'w1',
               'exact_mean': 'exact_mean', 'discrete_mean': 'mean',
               'exact_second': 'exact_second', 'discrete_second': 'second'}
    for suffix, key in mapping.items():
        expected = reference[key] * (count_scale if suffix.endswith('mass') else 1)
        check.close('certificate_'+suffix, row[prefix+suffix], expected, rtol=0,
                    atol=2e-12 * (count_scale if suffix.endswith('mass') else 1))
    check.close('certificate_relative_mass_defect', row[prefix+'relative_mass_defect'],
                reference['relative_mass_defect'], rtol=0, atol=2e-12)
    return reference


def audit(monitor, native, output):
    started = time.perf_counter()
    paths = {key: monitor/f'MONITOR_{key}.csv' for key in
             ('STEPS','RULES','PANELS','TEMPLATES','BIRTHS','FINAL_COHORTS')}
    inputs = [{'path': str(p), 'bytes': p.stat().st_size, 'sha256': file_sha(p)} for p in [*paths.values(), native]]
    check = Checks()
    steps = index_rows(paths['STEPS'], ('step',))
    rules = index_rows(paths['RULES'], ('step','rule_id'))
    panels = index_rows(paths['PANELS'], ('step','rule_id','panel_id'))
    templates = index_rows(paths['TEMPLATES'], ('step','template_id'))
    native_rows = list(csv_rows(native))
    require(len(native_rows) == len(steps), 'native/monitor step count')
    final_native = native_rows[-1]
    final_step = steps[(len(steps),)]
    final_a = [float(final_step[f'end_a{i}']) for i in (1,2,3)]
    final_time = float(final_step['t1_s'])
    for native_row in native_rows:
        step = steps[(int(native_row['step']),)]
        for field, key in [('photons_com3','retained_count_com3'),('source_count','source_count_com3'),
                           ('source_energy','source_energy_j_com3'),('absorbed_com3','absorbed_count_com3'),
                           ('geom_work','geometry_work_j_com3'),('survivor_age_com_s','retained_age_sum_com_s'),
                           ('survivor_age2_com_s2','retained_age2_sum_com_s2')]:
            check.close('native_step_'+field, step[key], native_row[field])
        for prefix in ('rate','accepted'):
            density = [float(step[f'{prefix}_{sp}_m3']) for sp in SPECIES]
            require(all(math.isfinite(x) and x >= 0 for x in density), f'negative/nonfinite {prefix} gas')
            thermal = float(step[f'{prefix}_thermal_j_m3'])
            require(math.isfinite(thermal) and thermal >= 0, 'thermal population')
            particles = math.fsum(n*(1+z) for n,z in zip(density,CHARGE))
            temp = thermal/(1.5*1.380649e-23*particles)
            check.close(prefix+'_eos', step['rate_temperature_K'] if prefix=='rate' else native_row['T_K'], temp)
            if prefix == 'accepted':
                binding = EV_J*(CHI[0]*density[2]+CHI[1]*density[11]+(CHI[1]+CHI[2])*density[12]+CHI[3]*density[4])
                check.close('accepted_binding_owner',step['accepted_binding_j_m3'],binding)
                vol=float(step['end_volume'])
                for key, col in [('thermal','gas_thermal_com3'),('binding','gas_binding_com3'),
                                  ('escaped','escaped_com3'),('cmb_reservoir','cmb_reservoir_com3')]:
                    check.close('accepted_'+key+'_volume',float(step[f'accepted_{key}_j_m3'])*vol,native_row[col])
    for (st,rid), rule in rules.items():
        step=steps[(st,)]
        density=[float(step[f'rate_{sp}_m3']) for sp in SPECIES]
        energy=float(rule['energy_ev'])
        require(f'{struct.unpack(">Q",bit(energy))[0]:016x}'==rule['energy_bits'], 'energy bits')
        rates=opacity(energy,density)
        for species,k in zip(('HI','HeI','HeII','DI'),rates):
            check.close('opacity_'+species,rule[f'k_{species}_per_s'],k)
        check.close('tau_selector',rule['tau'],math.fsum(rates)*float(step['dt_s']))
    rule_nodes={key:{} for key in rules}
    selected_templates={}
    all_aggregates=[]
    final_sums=[]
    max_clock_s=max_normalized_clock_s=max_source_ratio_defect=max_panel_width_s=max_optical_width=0.0
    zero_native=positive_native=0
    cohort_count=0
    final_iter=iter(csv_rows(paths['FINAL_COHORTS']))
    for key, group in itertools.groupby(csv_rows(paths['BIRTHS']),lambda row:(int(row['step']),int(row['template_id']))):
        batch=list(group)
        st,tid=key
        tpl=templates[key];rid=int(tpl['rule_id']);rule=rules[st,rid];step=steps[(st,)]
        require(len(batch)==int(tpl['birth_count'])==int(rule['nodes']), 'template node count')
        dt=float(step['dt_s']);t1=float(step['t1_s']);tau=float(rule['tau'])
        base=float(tpl['constant_j_born_com3'])
        check.close('template_base',base,float(tpl['midpoint_rate_com3_s'])*dt)
        direction=[float(tpl[f'raw_birth_direction{i}']) for i in (1,2,3)]
        norm=math.hypot(math.hypot(direction[0],direction[1]),direction[2])
        n_unit=[x/norm for x in direction]
        born=[];accepted=[];photo=[];age1=[];age2=[];frozen=[]
        f_count=[];f_age=[];f_age2=[];f_energy=[];f_q2=[];f_width=[];f_optical=[];a_width=[]
        nodes_actual=[]
        for node_id,row in enumerate(batch):
            final=next(final_iter,None);require(final is not None,'missing final cohort')
            require(int(row['cohort_index'])==int(final['cohort_index'])==cohort_count,'cohort appendindex join')
            require(cohort_count==int(tpl['first_cohort_index'])+node_id,'template first index')
            require(int(row['node_id'])==node_id and int(row['rule_id'])==rid and int(row['panel_id'])==node_id//2,'birth node/panel join')
            pair=(row['target_age_x'],row['emission_weight'])
            if node_id in rule_nodes[st,rid]:
                require(all(bit(x)==bit(y) for x,y in zip(pair,rule_nodes[st,rid][node_id])),'shared rule changed by label')
            else:
                rule_nodes[st,rid][node_id]=pair
            target=float(pair[0]);weight=float(pair[1]);tb=float(row['actual_birth_time_s'])
            require(bit(tb)==bit(t1-dt*target),'actual birth clock bit mismatch')
            x=(t1-tb)/dt
            require(bit(x)==bit(row['actual_clock_age_x']),'actual age bit mismatch')
            check.close('clock_defect',row['clock_age_defect_x'],x-target,rtol=0,atol=1e-30)
            clock_s=(t1-tb)-dt*target
            require(bit(row['clock_age_defect_s'])==bit(clock_s),'physical clock defect')
            max_clock_s=max(max_clock_s,abs(clock_s))
            max_normalized_clock_s=max(max_normalized_clock_s,abs(x-target)*dt)
            require(0<=x<=1 and float(step['t0_s'])<=tb<t1,'birth clock support')
            panel=panels[st,rid,node_id//2]
            left,right=float(panel['left_x']),float(panel['right_x'])
            require(left<target<right and bit(2*weight)==bit(right-left),'actual panel support/weight')
            ratio=float(row['source_amplitude_ratio'])
            birth_a=[float(row[f'birth_a{i}']) for i in (1,2,3)]
            birth_volume=math.prod(birth_a)
            expected_ratio=sfr_from_volume(birth_volume)/sfr_from_volume(float(step['mid_volume']))
            check.close('source_amplitude_MD14',ratio,expected_ratio)
            max_source_ratio_defect=max(max_source_ratio_defect,abs(ratio-1))
            nb,na,np=float(row['born_count_com3']),float(row['accepted_count_com3']),float(row['after_photo_count_com3'])
            nf=float(final['retained_count_com3'])
            require(0<=nf<=na<=nb and 0<=np<=nb,'negative/increasing photon survival')
            require((row['born_count_underflow']=='true')==(float(tpl['midpoint_rate_com3_s'])>0 and nb==0),'born underflow flag')
            require(bit(na)==bit(np),'afterphoto/accepted photon count changed')
            check.close('born_source_weight',nb,base*weight*ratio)
            ns=nb*math.exp(-tau*x)
            check.close('native_source_frozen_weight',row['native_source_frozen_survivor_com3'],ns,atol=5e-324)
            require((row['native_source_frozen_underflow']=='true')==(nb>0 and ns==0),'frozen underflow flag')
            energy0=float(tpl['energy_ev'])
            killing=[float(row[f'K{i}_ev_scale']) for i in (1,2,3)]
            for i in range(3):
                check.close('Killing_birth_constant',killing[i],birth_a[i]*energy0*n_unit[i])
            e,di=ray_from_killing(killing,[float(step[f'end_a{i}']) for i in (1,2,3)])
            check.close('Killing_step_energy',row['end_energy_ev'],e)
            for i in range(3):
                check.close('Killing_step_direction',row[f'end_direction{i+1}'],di[i],atol=2e-15)
            ef,df=ray_from_killing(killing,final_a)
            check.close('Killing_final_energy',final['energy_ev'],ef)
            for i in range(3):
                check.close('Killing_final_direction',final[f'direction{i+1}'],df[i],atol=2e-15)
            age=t1-tb;af=final_time-tb
            require(bit(final['final_time_s'])==bit(final_time) and bit(final['age_s'])==bit(af),'final age/time')
            born.append(nb);accepted.append(na);photo.append(np);age1.append(na*age);age2.append(na*age*age);frozen.append(ns)
            f_count.append(nf);f_age.append(nf*af);f_age2.append(nf*af*af);f_energy.append(nf*ef*EV_J)
            f_q2.append(nf*ef*EV_J*(1.5*df[2]*df[2]-.5))
            f_width.append(nf*dt*(right-left));f_optical.append(nf*tau*(right-left))
            a_width.append(na*dt*(right-left))
            nodes_actual.append((row['actual_clock_age_x'],nb/base))
            if nf==0:zero_native+=1
            else:positive_native+=1
            cohort_count+=1
        totals={k:math.fsum(vals) for k,vals in [('born',born),('accepted',accepted),('photo',photo),('age1',age1),('age2',age2),('source_frozen',frozen)]}
        for source,col in [('born','native_born_com3'),('accepted','accepted_count_com3'),('photo','after_photo_count_com3'),
                           ('age1','accepted_age_sum_com_s'),('age2','accepted_age2_sum_com_s2')]:
            check.close('template_'+source,tpl[col],totals[source])
        check.close('template_source_frozen_mass',tpl['native_source_frozen_survivor_discrete_mass'],totals['source_frozen'])
        exact=base*(-math.expm1(-tau)/tau if tau else 1)
        all_aggregates.append({'step':st,'template_id':tid,'rule_id':rid,'exact_constant_source_frozen':exact,
                               'accepted_width_weighted_sum':math.fsum(a_width),**totals})
        final_sums.append([math.fsum(x) for x in (f_count,f_age,f_age2,f_energy,f_q2,f_width,f_optical)])
        if (st,rid) not in selected_templates:
            selected_templates[st,rid]=(tid,nodes_actual)
    require(next(final_iter,None) is None,'extra final cohort')
    require(cohort_count==int(final_step['prior_cohorts'])+int(final_step['newborn_cohorts']),'final cohort count')
    require(positive_native==int(final_step['positive_cohorts']) and zero_native==int(final_step['zero_cohorts']),'final zero accounting')
    totals=[math.fsum(x[i] for x in final_sums) for i in range(7)]
    for field,expected in zip(('photons_com3','survivor_age_com_s','survivor_age2_com_s2','photon_energy_com3'),totals[:4]):
        check.close('final_aggregate_'+field,final_native[field],expected)
    check.close('final_energy_weighted_q2',final_native['q2'],totals[4]/totals[3],rtol=0,atol=5e-14)
    rule_results=[]
    for (st,rid), rule in sorted(rules.items()):
        nodes=[rule_nodes[st,rid][i] for i in range(int(rule['nodes']))]
        a=certificate_checks(check,rule,'kernel_emitted_unit_',0,nodes)
        b=certificate_checks(check,rule,'kernel_survivor_unit_',rule['tau'],nodes)
        tid,actual=selected_templates[st,rid]
        template=templates[st,tid]
        certificate_checks(check,template,'native_source_frozen_emitted_',0,actual,float(template['constant_j_born_com3']))
        source=certificate_checks(check,template,'native_source_frozen_survivor_',rule['tau'],actual,float(template['constant_j_born_com3']))
        dt=float(steps[(st,)]['dt_s']);tau=float(rule['tau'])
        rule_results.append({'step':st,'rule_id':rid,'sampled_template_id':tid,'energy_ev':float(rule['energy_ev']),
                             'tau':tau,'nodes':len(nodes),'kernel_mass_defect':b['relative_mass_defect'],
                             'kernel_cdf_sup':b['cdf_sup'],'kernel_W1_x':b['w1'],'kernel_W1_s':dt*b['w1'],
                             'kernel_W1_optical':tau*b['w1'],'source_clock_mass_defect':source['relative_mass_defect']})
        recurrence_left=0.0
        for j in range(int(rule['panels'])):
            panel=panels[st,rid,j];left=float(panel['left_x']);right=float(panel['right_x']);r=int(rule['refinement'])
            target=1/r if tau<=1 else min(1/tau+left,1)/r
            require(bit(left)==bit(recurrence_left) and bit(right)==bit(min(left+target,1)),'panel recurrence')
            width=right-left;theta=tau*width
            require(panel['width_bits_match']=='true' and bit(panel['width_from_actual_weights'])==bit(width),'panel width bits')
            for name,expected in [('nominal_width_s',dt*width),('optical_width',theta),
                                  ('represented_birth_left_s',float(steps[(st,)]['t1_s'])-dt*right),
                                  ('represented_birth_right_s',float(steps[(st,)]['t1_s'])-dt*left)]:
                require(bit(panel[name])==bit(expected),'panel '+name)
            check.close('panel_reference_mass',panel['exact_survival_per_unit_born'],
                        math.exp(-tau*left)*width*(-math.expm1(-theta)/theta if theta else 1),atol=5e-324)
            max_panel_width_s=max(max_panel_width_s,dt*width);max_optical_width=max(max_optical_width,theta)
            recurrence_left=right
        require(recurrence_left==1.0,'full panel coverage')
    step_results=[]
    for st,group in itertools.groupby(all_aggregates,key=lambda x:x['step']):
        data=list(group)
        sums={k:math.fsum(row[k] for row in data) for k in ('exact_constant_source_frozen','source_frozen','accepted','born','accepted_width_weighted_sum')}
        ref=sums['exact_constant_source_frozen']
        step_results.append({'step':st,**sums,'source_clock_relative_shift':(sums['source_frozen']-ref)/ref,
                             'transport_relative_shift':(sums['accepted']-sums['source_frozen'])/ref,
                             'combined_relative_shift':(sums['accepted']-ref)/ref,
                             'accepted_mean_panel_width_s':sums['accepted_width_weighted_sum']/sums['accepted']})
    output.mkdir(parents=True,exist_ok=True)
    for name,data in [('RULE_REFERENCE_COMPARISON',rule_results),('NEWBORN_MEASURE_COMPARISON',step_results)]:
        with (output/(name+'.csv')).open('w',newline='') as stream:
            writer=csv.DictWriter(stream,fieldnames=list(data[0]));writer.writeheader();writer.writerows(data)
    result={'schema':'rei.br05.native_monitor_independent.v1','status':'PASS_SCOPED','inputs':inputs,
            'steps':len(steps),'rules_all':len(rules),'panels_all':len(panels),'templates_all':len(templates),
            'birth_rows_all':cohort_count,'final_rows_all':cohort_count,'final_positive':positive_native,'final_zero':zero_native,
            'full_shape_reference_rules':len(rule_results),'actual_source_shape_templates_sampled':len(selected_templates),
            'sampling':'First template in each shared (step,rule); all template masses and raw moments checked separately.',
            'decimal_precision':90,'certificate_fields_per_measure':9,'numeric_checks':check.counts,'max_relative_discrepancies':check.maxima,
            'max_clock_defect_s':max_clock_s,'max_normalized_clock_defect_times_dt_s':max_normalized_clock_s,
            'max_source_amplitude_ratio_defect':max_source_ratio_defect,
            'final_retained_mean_panel_width_s':totals[5]/totals[0],
            'final_retained_mean_selector_optical_panel_width':totals[6]/totals[0],
            'width_interpretation':'Actual retained-weighted panel width; conditional W1 bound only for hypothetical measures matching these panel masses/supports.',
            'max_nominal_panel_width_s':max_panel_width_s,'max_optical_panel_width':max_optical_width,
            'newborn_measure_comparison':step_results,'rule_reference_summary':{
                'max_kernel_mass_defect':max(abs(row['kernel_mass_defect']) for row in rule_results),
                'W1_s_range':[min(row['kernel_W1_s'] for row in rule_results),max(row['kernel_W1_s'] for row in rule_results)],
                'cdf_sup_range':[min(row['kernel_cdf_sup'] for row in rule_results),max(row['kernel_cdf_sup'] for row in rule_results)]},
            'wall_s':time.perf_counter()-started,'python':sys.version,'script_sha256':file_sha(Path(__file__)),
            'reference_sha256':file_sha(Path(__file__).with_name('monitor_reference.py')),
            'scope':'Counterfactual frozen reference diagnostics and native export/owner checks; no nonlinear gas absolute error bound.'}
    (output/'MONITOR_INDEPENDENT_VERIFICATION.json').write_text(json.dumps(result,indent=2)+'\n')
    return result


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--monitor',type=Path,required=True)
    parser.add_argument('--native',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();r=audit(args.monitor,args.native,args.output)
    print(json.dumps({key:r[key] for key in ('status','steps','rules_all','panels_all','birth_rows_all','wall_s')},indent=2))


if __name__=='__main__':main()
