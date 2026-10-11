"""Read-only bounded common-final comparison; not a 65/129/full-history test."""
from pathlib import Path
import hashlib,json,math
HERE=Path(__file__).resolve().parent
FIELDS=('xHII','xHeII','xHeIII','T_K','ne_cm3','photon_cm3','GammaHI_s','GammaHeI_s','GammaHeII_s')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    output=HERE/'NATIVE_ENTRY_COMMON_FINAL_COMPARISON.json'
    if output.exists():raise FileExistsError(output)
    paths=[HERE/f'NATIVE_ENTRY_C2_T1E11_N{n}_HEAT.json' for n in (1,2,4)]
    runs=[json.loads(p.read_text()) for p in paths]
    assert all(r['status']=='PASS_BOUNDED_MAP_ONLY' and r['final_s']==1e11 for r in runs)
    assert all(r['identities']==runs[0]['identities'] for r in runs)
    assert all(r['checkpoint_identity']==runs[0]['checkpoint_identity'] for r in runs)
    metrics={}
    for coarse,fine in zip(runs[:-1],runs[1:]):
        a,b=coarse['accepted_boundaries'][-1]['fields'],fine['accepted_boundaries'][-1]['fields']
        vals={}
        for key in FIELDS:
            delta=abs(a[key]-b[key]);amplitude=abs(b[key])
            scaled=delta/amplitude if amplitude else (0. if delta==0 else None)
            vals[key]=dict(coarse=a[key],fine=b[key],fine_amplitude=amplitude,absolute_difference=delta,
                normalized_difference=scaled,budget=2e-6,pass_budget=scaled is not None and scaled<=2e-6)
        metrics[f"{coarse['steps']}_vs_{fine['steps']}"]=dict(fields=vals,
            pass_all_fields=all(v['pass_budget'] for v in vals.values()),
            worst_field=max(vals,key=lambda k: vals[k]['normalized_difference'] if vals[k]['normalized_difference'] is not None else math.inf))
    result=dict(schema='rei.q1b.native_entry_common_final.v1',status='LOCAL_TIME_GATE_FAILED',
        scientific_admission=False,whole_interval=False,epoch_sets_65_129='NOT_EVALUATED',
        source_identity_match=True,checkpoint_identity_match=True,common_final_s=1e11,
        scope='One common-final endpoint, three first-order split-step schedules; opacity/heat/source/newton gates at every accepted boundary. This is not a full time-history comparison.',
        budget=2e-6,zero_fine_requires_exact_zero=True,comparisons=metrics,
        native_calls_total=sum(r['native_calls'] for r in runs),sigma_calls_total=sum(r['opacity_calls'] for r in runs),
        accepted_boundaries=sum(len(r['accepted_boundaries']) for r in runs),
        max_energy_initial_scaled=max(b['ledger']['energy_initial_scaled'] for r in runs for b in r['accepted_boundaries']),
        max_number_nH_initial_scaled=max(b['ledger']['number_nH_initial_scaled'] for r in runs for b in r['accepted_boundaries']),
        actual_restart=runs[-1]['restart_result'],
        input_sha256={p.name:sha(p) for p in paths},analysis_sha256=sha(Path(__file__)),
        interpretation='Conservation, domains and actual boundary restart pass locally. The tested common-final family fails the unchanged time threshold; increasing entry step does not provide admissible time accuracy. Separately saved smaller source trials fail1e-10 quadrature. This is an observed combination, not a proof that no intermediate timestep or precision implementation could work.',
        next_action='Preserve HOLD. Implement explicit source/native coordinate precision representation and establish time convergence before any full-history execution; no photon floor or source tolerance relaxation.')
    output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:result[k] for k in ('status','native_calls_total','sigma_calls_total','max_energy_initial_scaled','max_number_nH_initial_scaled','actual_restart')},indent=2))
    for k,v in metrics.items(): print(k,v['worst_field'],v['fields'][v['worst_field']]['normalized_difference'])
if __name__=='__main__':main()
