#!/usr/bin/env python3
"""C9 independent captured-data review only; never executes native code."""
import datetime
from decimal import Decimal, localcontext
import hashlib
import json
from pathlib import Path
import tarfile

import audit_fixed_gate as g

ROOT = Path(__file__).resolve().parents[2]
REC = ROOT/'v16_work/implementation/receipts'

def combined_events(record, mode, method):
    report = record['report']
    if mode == 'fixed':
        return g.quadrature(report['stages']) if method == 'radau' else {k:g.d(v) for k,v in g.flatten_events(report['integrated']).items()}
    total = None
    for segment in report['segments']:
        if method == 'radau':
            current = g.quadrature(segment['chemical']['stages'])
        else:
            ev = {k:segment[k] for k in ['p','c','r','d','photo_binding','photo_heat','ce','ff','cmb','escape']}
            ev['rr'],ev['dr'] = segment['rrdr'][:3],segment['rrdr'][3]
            current = {k:g.d(v) for k,v in g.flatten_events(ev).items()}
        if total is None:
            total = {k:Decimal(0) for k in current}
        for k,v in current.items():
            total[k] += v
    return total

def reference_inventory(report, endpoint=False):
    """Independent affine inventory from raw scales, states and increments."""
    states = report['stages']
    y = list(map(g.d,states[2]['scaled_state'])) if endpoint else [
        g.d(states[0]['scaled_state'][k])-sum((g.d(g.A[0][j])*g.d(states[j]['increments'][k]) for j in range(3)),Decimal(0))
        for k in range(report['dimension'])]
    n, u = Decimal(0),Decimal(0)
    for c in report['cell_coordinates']:
        cn = g.d(c['nscale'])*(y[c['number_index']] if endpoint else 1)
        cu = g.d(c['lo'])*cn
        if c['offset_index'] is not None:
            cu += g.d(c['hi']-c['lo'])*g.d(c['nscale'])*y[c['offset_index']]
        n += cn;u += cu
    return n,u

def balances_with_work_and_source(before,after,events,source_n,source_u,aref):
    balances=g.chemical_balances(before,after,events)
    wg=g.d(after['ledgers']['thermal_work'])-g.d(before['ledgers']['thermal_work'])
    wp=g.d(after['ledgers']['photon_work'])-g.d(before['ledgers']['photon_work'])
    pu1=g.exact_sum(after['energy_ref'])*g.d(aref/after['a'])
    pu0=g.exact_sum(before['energy_ref'])*g.d(aref/before['a'])
    ref_delta=g.exact_sum(after['energy_ref'])-g.exact_sum(before['energy_ref'])
    balances['photon_N_per_H']-=source_n
    balances['thermal_eV_per_H']+=wg
    balances['gas_plus_binding_eV_per_H']+=wg
    balances['photon_U_eV_per_H']+=pu1-pu0-ref_delta+wp-source_u
    balances['full_photon_gas_binding_eV_per_H']+=pu1-pu0-ref_delta+wg+wp-source_u
    return balances

def review():
    matrix=json.loads((REC/'MATRIX_RECEIPT.json').read_text())
    max_values={};cumulative_max={};cases=[];case_identities=set();archive_payload_hash_sets=set()
    def note(name,value):
        max_values[name]=max(max_values.get(name,0.),float(abs(value)))
    total_rhs=0;total_native_wall=0.;total_process_wall=0.;macro_count=0;chem_count=0;stage_count=0
    dimension_counts={};birth_layouts={};stage_nodes=set();native_residual_max=0.;library_wrms_max=0.;ssprk_tau_max=0.
    for entry in matrix['cases']:
        directory=ROOT/entry['receipt'];raw=json.loads((directory/'raw.json').read_text())
        inp=json.loads((directory/'inputs.json').read_text());out=json.loads((directory/'outcome.json').read_text())
        identity=(raw['mode'],raw['method'],raw['N']);assert identity not in case_identities;case_identities.add(identity)
        assert raw['completed'] and raw['failure'] is None and out['exit_code']==0 and not out['truncated']
        assert len(raw['records'])==raw['N'] and g.sha(directory/'stdout.txt')==out['stdout_sha256'] and g.sha(directory/'stderr.txt')==out['stderr_sha256']
        assert matrix['binary_sha256'] in inp['executables_sha256'].values()
        assert g.sha(directory/'sources.tar.gz')==inp['source_archive_sha256']
        manifest=inp['source_sha256']
        with tarfile.open(directory/'sources.tar.gz') as archive:
            for name, expected in manifest.items():
                assert hashlib.sha256(archive.extractfile(name).read()).hexdigest()==expected,name
        archive_payload_hash_sets.add(hashlib.sha256(json.dumps(manifest,sort_keys=True).encode()).hexdigest())
        total_rhs+=raw['native_rhs_attempts_including_fd_replay'];total_native_wall+=raw['wall_s'];total_process_wall+=out['wall_s']
        mode,method,N=identity;before=raw['initial'];aref=before['a'];eventsum=None;source_n=Decimal(0);source_u=Decimal(0);last_balances=None
        layouts=[];case_native_calls=0
        for record in raw['records']:
            macro_count+=1;after=record['state'];report=record['report'];q=combined_events(record,mode,method)
            if eventsum is None:eventsum={k:Decimal(0) for k in q}
            for key,value in q.items():eventsum[key]+=value
            births=[] if mode=='fixed' else report['births'];bn=g.exact_sum(b['added_n'] for b in births);bu=g.exact_sum(b['added_u'] for b in births)
            source_n+=bn;source_u+=bu
            balances=balances_with_work_and_source(before,after,q,bn,bu,aref)
            dwork_g=g.d(after['ledgers']['thermal_work'])-g.d(before['ledgers']['thermal_work'])
            dwork_p=g.d(after['ledgers']['photon_work'])-g.d(before['ledgers']['photon_work'])
            last_balances=balances
            for key,value in balances.items():note(key,value)
            prefix_balances=balances_with_work_and_source(raw['initial'],after,eventsum,source_n,source_u,aref)
            for key,value in prefix_balances.items():cumulative_max[key]=max(cumulative_max.get(key,0.),float(abs(value)))
            note('source_N_ledger',g.d(after['ledgers']['source_n'])-g.d(before['ledgers']['source_n'])-bn)
            note('source_U_ledger',g.d(after['ledgers']['source_u'])-g.d(before['ledgers']['source_u'])-bu)
            for base,channel in [('photo','p'),('ci','c'),('rr','r')]:
                for j in range(3):note('event_ledger_'+base,g.d(after['ledgers'][base][j])-g.d(before['ledgers'][base][j])-q[f'{channel}[{j}]'])
            for name,channel in [('dr','d'),('escaped_u','escape'),('cmb_input','cmb')]:note('event_ledger_'+name,g.d(after['ledgers'][name])-g.d(before['ledgers'][name])-q[channel])
            for s in [before,after]:
                assert s['pools'][2:]==[0.,0.]
                assert s['ledgers']['boundary_n']==0. and s['ledgers']['boundary_u']==0.
                note('electron_state_per_H',g.d(s['electron_per_h'])-g.electron(s))
                note('pool_N_per_H',g.exact_sum(s['number'])-g.d(s['pools'][0]))
                note('pool_U_eV_per_H',g.exact_sum(s['energy_ref'])*g.d(aref/s['a'])-g.d(s['pools'][1]))
                w_eos=g.d(1.5)*g.d(g.KB)/g.d(g.EV)*g.d(s['temperature_k'])*(1+g.d(g.Y)+g.electron(s))
                note('EOS_w_eV_per_H',g.d(s['w_ev'])-w_eos)
            if method=='radau':
                chemical=[report] if mode=='fixed' else [s['chemical'] for s in report['segments']]
                layouts.append([c['dimension'] for c in chemical]);chem_count+=len(chemical)
                for c in chemical:
                    case_native_calls+=c['native_rhs_calls'];dimension_counts[str(c['dimension'])]=dimension_counts.get(str(c['dimension']),0)+1
                    assert c['dimension']==4+sum(1+(x['offset_index'] is not None) for x in c['cell_coordinates'])
                    qchem=g.quadrature(c['stages']);reported=g.flatten_events(c['integrated'])
                    for key,value in qchem.items():note('Radau_shared_quadrature_'+key,value-g.d(reported[key]))
                    library_wrms_max=max(library_wrms_max,c['library_wrms']);native_residual_max=max(native_residual_max,c['max_scaled_stage_residual'])
                    for st in c['stages']:
                        stage_count+=1;stage_nodes.add(st['nodes'])
                        assert 0<=st['fractions'][0]<=1 and 0<=st['fractions'][1] and 0<=st['fractions'][2] and sum(st['fractions'][1:])<=1 and st['w_ev']>0
                        for coord in c['cell_coordinates']:
                            number=st['scaled_state'][coord['number_index']];assert number>0
                            if coord['offset_index'] is not None:assert 0<=st['scaled_state'][coord['offset_index']]<=number
                        for j in range(3):note('node_point_P_rate',g.d(st['node_photo_per_h_s'][j])-g.d(st['events_per_h_s']['p'][j]))
                        note('node_point_binding_rate',g.d(st['node_binding_ev_per_h_s'])-g.d(st['events_per_h_s']['photo_binding']))
                        note('node_point_heat_rate',g.d(st['node_heat_ev_per_h_s'])-g.d(st['events_per_h_s']['photo_heat']))
                if mode!='fixed':
                    segments=report['segments'];assert len(segments)==3 and len(births)==2
                    dln=((g.d(after['a'])-g.d(before['a']))/g.d(before['a'])+1).ln()
                    for birth in births:note('GL2_half_weight_dln_a',g.d(birth['weight_dln_a'])-dln/2)
                    gas_work=Decimal(0);photon_work=Decimal(0)
                    for j,segment in enumerate(segments):
                        b,m,e=map(g.d,[segment['begin'],segment['midpoint'],segment['end']]);assert b<m<e
                        c=segment['chemical'];n0,u0=reference_inventory(c);n1,u1=reference_inventory(c,True)
                        gas_work+=g.d(c['wscale'])*((m/b)**2-1)+g.d(c['stages'][2]['w_ev'])*(1-(m/e)**2)
                        photon_work+=g.d(aref)*((1/b-1/m)*u0+(1/m-1/e)*u1)
                        if j==0:note('initial_segment_N_layout',n0-g.exact_sum(before['number']))
                        if j<2:
                            nxt=segments[j+1]['chemical'];nn,uu=reference_inventory(nxt);birth=births[j]
                            assert segment['end']==birth['a']==segments[j+1]['begin']
                            note('postbirth_N_layout',nn-n1-g.d(birth['added_n']))
                            note('postbirth_U_layout',g.d(aref/float(e))*(uu-u1)-g.d(birth['added_u']))
                        else:
                            assert segment['end']==after['a']
                            note('final_segment_N_layout',n1-g.exact_sum(after['number']))
                            note('final_segment_U_layout',u1-g.exact_sum(after['energy_ref']))
                    note('independent_adiabatic_work_eV_per_H',gas_work-dwork_g)
                    note('independent_photon_work_eV_per_H',photon_work-dwork_p)
            else:ssprk_tau_max=max(ssprk_tau_max,report['tau1'],report['tau2'])
            before=after
        if method=='radau':assert case_native_calls==raw['native_rhs_attempts_including_fd_replay']
        birth_layouts[f'{mode}/{method}/N{N}']=layouts
        cases.append({'mode':mode,'method':method,'N':N,'raw_sha256':g.sha(directory/'raw.json'),
                      'outcome_sha256':g.sha(directory/'outcome.json'),'source_archive_sha256':g.sha(directory/'sources.tar.gz'),
                      'source_payload_count':len(manifest),'actual_exit':out['exit_code'],'actual_completed':raw['completed'],
                      'native_rhs_attempts':raw['native_rhs_attempts_including_fd_replay'],'native_wall_s':raw['wall_s'],'process_wall_s':out['wall_s'],
                      'source_birth_N':float(source_n),'source_birth_U':float(source_u),
                      'final_record_balances':{k:float(v) for k,v in last_balances.items()},
                      'whole_history_balances':{k:float(v) for k,v in prefix_balances.items()}})
    assert len(case_identities)==19 and total_rhs==matrix['unique_total_native_rhs_attempts']
    return {'schema':'independent_c9_native_matrix_raw_review_v1','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'reviewer':'/root/dropbox_v15_intake (Astra), not new adapter author',
            'method':'Read-only Decimal60 balances on exact binary64 values; no new native execution. No reported energy/audit residual column used for independent balances.',
            'unique_cases':len(cases),'accepted_macro_records':macro_count,'Radau_chemical_segments':chem_count,'Radau_accepted_stages':stage_count,
            'Radau_dimension_counts':dimension_counts,'Radau_prepared_node_counts':sorted(stage_nodes),
            'native_rhs_attempts':total_rhs,'native_wall_s':total_native_wall,'captured_process_wall_s':total_process_wall,
            'source_payload_manifests_distinct':len(archive_payload_hash_sets),'verified_source_payload_counts':sorted(set(c['source_payload_count'] for c in cases)),
            'frozen_binary_sha256':matrix['binary_sha256'],'max_abs_independent_audits':max_values,
            'max_abs_cumulative_balances_over_all_prefixes':cumulative_max,
            'reported_Radau_max_scaled_component_residual':native_residual_max,'reported_Radau_max_library_wrms':library_wrms_max,
            'SSPRK_accepted_max_tau':ssprk_tau_max,'birth_layouts':birth_layouts,'cases':cases,
            'limits':['This audit does not establish convergence order, a rigorous reference error bound, or stiff uniform accuracy.',
                      'Reference-energy moment arrays are mapped with the actual tested FLRW q=0 scale a_ref/a; signed Bianchi is not audited.',
                      'Independent geometric-work reconstruction uses declared raw segment endpoints and affine decoded moments; floating reconstruction uncertainty is retained.',
                      'Empty initial source-on photon layout is 4D; positive layouts are rebuilt after actual births. No clipping is inferred from endpoint conservation alone.',
                      'SSPRK raw config newton_atol_scaled labels the Radau configuration; actual SSPRK native coupling tolerance is 1e-15 from source_clocks.',
                      'No optional large-optical-depth diagnostic or additional refinement was run.']}

if __name__=='__main__':
    with localcontext() as context:
        context.prec=60
        result=review()
    output=ROOT/'v16_work/c9_code/MATRIX_INDEPENDENT_RAW_AUDIT.json'
    output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['unique_cases','accepted_macro_records','Radau_chemical_segments','Radau_accepted_stages','native_rhs_attempts','native_wall_s','source_payload_manifests_distinct','max_abs_cumulative_balances_over_all_prefixes']},indent=2))
