"""Finite candidate qualification; full first-interval admission is separate."""
import importlib.util,json,math,hashlib,subprocess,time
from pathlib import Path
from sage.all import RealIntervalField
P=Path('.cuh/fastest-track/REI-F05');R=RealIntervalField(200)
SOURCE=Path('docs/atomic_reionization_handoff_20261004_v1/runtime_returns/evidence/F04_certificate/checker.py')
s=importlib.util.spec_from_file_location('independent_ft03',SOURCE);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
manifest=json.loads(Path('runs/rei_fastest_v1/map_certificate/parent_manifest.json').read_text());constants=json.loads(Path('docs/atomic_reionization_handoff_20261004_v1/runtime_inputs/ft03_map_constants.json').read_text());lock=json.loads(Path('docs/atomic_reionization_handoff_20261004_v1/runtime_inputs/ft03_first_interval.json').read_text())


def state_scaled(state,model):
    return [R(float(x)) for x in state[:3]]+[R(float(state[3]))/(model.nh*model.ev)]+[R(float(x))/model.nh for x in state[4:7]]


def ledger_check(old,new,events,model):
    # Endpoint event counts are proper cm^-3. Compare source stoichiometry and
    # three photon owners, plus augmented thermal/binding/photon/escape energy.
    nh,nhe,ev=float(model.nh.center()),float(model.nhe.center()),float(model.ev.center());chi=[float(x.center()) for x in model.chi];energy=[float(x.center()) for x in model.energy]
    photo,ci,rr,dr=events['photo'],events['collision'],events['recombination'],events['dr']
    assert len(photo)==3 and all(len(row)==3 for row in photo) and len(ci)==len(rr)==3 and len(dr)==2
    assert all(math.isfinite(v) and v>=0 for v in [*ci,*rr,*dr,*[v for row in photo for v in row]])
    j=[math.fsum(photo[a])+ci[a]-rr[a] for a in range(3)];j[1]-=math.fsum(dr)
    residuals=[abs(nh*(new[0]-old[0])-j[0])/nh,abs(nhe*(new[1]-old[1])-j[1]+j[2])/nhe,abs(nhe*(new[2]-old[2])-j[2])/nhe]
    residuals += [abs(old[4+k]-new[4+k]-math.fsum(photo[a][k] for a in range(3)))/old[4+k] for k in range(3)]
    def total(s):
        return math.fsum([s[3],s[7],nh*chi[0]*ev*s[0],nhe*chi[1]*ev*s[1],nhe*(chi[1]+chi[2])*ev*s[2],*[s[4+k]*energy[k]*ev for k in range(3)]])
    residuals.append(abs(total(new)-total(old))/total(old))
    assert max(residuals)<=lock['floating_ledger_scaled_tolerance'],('LEDGER',residuals)
    return max(residuals)


def certify_record(record,previous_box,previous_state):
    assert record['accepted'] is True
    assert record['parent_box']==previous_box,'parent enclosure reset or stale transfer'
    assert record['old_state']==previous_state,'accepted parent state transfer mismatch'
    assert record['model_id']==lock['model_id']
    model=m.Model(manifest,constants)
    # The actual Rust scaled coordinate is part of the numerical experiment.
    # Account for the exact-CGS to binary64 transform by including it in P.
    central=[float(x) for x in record['parent_center']];model.z0=[R(x) for x in central]
    model.p=[R(float(a),float(b)) for a,b in previous_box]
    exact=state_scaled(previous_state,model)
    assert all(model.p[i].lower()<=exact[i].lower() and exact[i].upper()<=model.p[i].upper() for i in range(7)),'parent doesnot include CGS transform'
    model.d=[R(m.absmax(model.p[i]-model.z0[i])) for i in range(7)]
    dt=float(record['dt_s']);sites=record['sites'];assert [v['id'] for v in sites]==manifest['source_sites']
    full=m.certify_site(model,sites[0],model.p,model.z0,0,dt)
    h1=m.certify_site(model,sites[1],model.p,model.z0,0,dt/2)
    h2=m.certify_site(model,sites[2],h1['box'],h1['y'],h1['eta'],dt/2)
    jh=h2['jac']*h1['jac'];hh=[h1['jac'].transpose()*h2['hess'][i]*h1['jac']+sum((h2['jac'][i,j]*h1['hess'][j] for j in range(7)),m.matrix(R,7)) for i in range(7)]
    of=m.affine_observables(model,full,full['jac'],full['hess'],full['centre_jac'],full['eta']);oh=m.affine_observables(model,h2,jh,hh,h2['centre_jac']*h1['centre_jac'],h2['eta'])
    bounds=[]
    for f,h in zip(of,oh):
        v=abs(R(f['a'])-R(h['a']))+sum(abs(R(f['b'][i])-R(h['b'][i]))*model.d[i] for i in range(7))+R(f['rho'])+R(h['rho']);bounds.append(m.upper(v))
    assert max(bounds)<lock['gate_local_error_strict'],'LOCAL_ERROR'
    # Two conservative upper bounds need not equal or dominate each other.
    # MPFI supplies the admission bound; independently check the Rust report
    # against a rigorous central-value lower bound and the unchanged gate.
    for k,(f,h) in enumerate(zip(of,oh)):
        lower=max(0,(abs(R(f['a'])-R(h['a']))-R(f['rho'])-R(h['rho'])).lower())
        claimed=float(record['local_bounds'][k]);assert math.isfinite(claimed) and lower<=R(claimed).lower()<lock['gate_local_error_strict'],'Invalid Rust local gate report'
    widths=[[x['public_width'] for x in out] for out in [of,oh]]
    assert max(v for row in widths for v in row)<lock['gate_public_width_strict'],'PUBLIC_WIDTH'
    for a,out in enumerate([of,oh]):
        for k,v in enumerate(out):
            lower=max(0,(sum(R(abs(v['b'][i]))*(R(float(previous_box[i][1]))-R(float(previous_box[i][0]))) for i in range(7))-2*R(v['rho'])).lower())
            claimed=float(record['public_widths'][a][k]);assert math.isfinite(claimed) and lower<=R(claimed).lower()<lock['gate_public_width_strict'],'Invalid Rust publicwidth gate report'
    nextbox=record['next_box'];assert len(nextbox)==7
    assert all(R(float(nextbox[i][0])).lower()<=h2['box'][i].lower() and h2['box'][i].upper()<=R(float(nextbox[i][1])).upper() for i in range(7)),'next parent fails to retain certifiedhalf2 box'
    newer=record['state'];assert len(newer)==8 and all(math.isfinite(v) for v in newer)
    assert all(R(float(nextbox[i][0])).lower()<=state_scaled(newer,model)[i].lower() and state_scaled(newer,model)[i].upper()<=R(float(nextbox[i][1])).upper() for i in range(7)),'next box excludes actualCGS transform'
    lr=ledger_check(previous_state,newer,record['events'],model)
    return {'max_local':max(bounds),'max_width':max(v for row in widths for v in row),'max_ledger':lr,'q':max(v['summary']['q_weighted'] for v in [full,h1,h2])}


def validate_run(directory,pilot):
    results=[];total=0
    for level,factor in enumerate(lock['time_refinement_factors']):
        summary=json.loads((directory/f'level_{level}_summary.json').read_text());assert summary['refinement_factor']==factor
        assert summary['mode']==('PILOT' if pilot else 'FULL')
        previous_box=summary['initial_parent_box'];previous_state=summary['initial_state'];accepted=0;rejected=0;time_s=0;maxima={'max_local':0,'max_width':0,'max_ledger':0,'q':0}
        z=manifest['actual_center_and_model_bits']['center_bits'];initial=[m.bits(v) for v in z]
        assert all(R(float(previous_box[i][0])).lower()<R(initial[i]).lower() and R(initial[i]).upper()<R(float(previous_box[i][1])).upper() for i in range(7))
        # Reject narrowing the originally prescribed independent parent radius.
        assert all(R(float(previous_box[i][0])).lower()<=(R(initial[i])-R(float(lock['initial_parent_radii'][i]))).lower() and (R(initial[i])+R(float(lock['initial_parent_radii'][i]))).upper()<=R(float(previous_box[i][1])).upper() for i in range(7))
        for line in (directory/f'level_{level}_transactions.jsonl').open():
            record=json.loads(line);assert record['t0_s']==time_s
            if record['accepted']:
                r=certify_record(record,previous_box,previous_state);accepted+=1;total+=1;time_s+=record['dt_s'];previous_box=record['next_box'];previous_state=record['state']
                for key in maxima:maxima[key]=max(maxima[key],r[key])
                if not pilot and total%100==0:print(json.dumps({'validated_trials':total,'time_s':time_s,'level':level,'maxima':maxima}),flush=True)
            else:
                rejected+=1;assert record['state']==previous_state and record['next_box']==previous_box,'REJECTED_CANDIDATE_COMMITTED'
        assert accepted==summary['accepted_steps'] and rejected==summary['rejected_steps'] and summary['final_state']==previous_state and summary['t_end_s']==time_s
        assert len(summary['all_seven_ledgers'])==7 and set(summary['all_seven_ledgers'])==set(lock['all_seven_ledgers'])
        assert all(math.isfinite(v) and abs(v)<=lock['floating_ledger_scaled_tolerance'] for v in summary['all_seven_ledgers'].values())
        if pilot:assert accepted==3 and time_s==3*lock['initial_trial_dt_s']*factor
        else:assert time_s==lock['time_interval_s'][1] and summary['finished'] is True
        results.append({'level':level,'factor':factor,'accepted':accepted,'rejected':rejected,'t_end_s':time_s,'maxima':maxima})
    return {'status':'PASS','pilot_only':pilot,'uniformly_certified_trials':total,'levels':results,'scientific_admission':'HOLD','claim':'Finitecandidatequalificationonly' if pilot else 'WholepredeclaredstaticFT03firstinterval, no expandingorphysicalpromotion'}


def main():
    cargo='/home/cosmosapjw/.cargo/bin/cargo';crate='rust/rei_microphysics/Cargo.toml'
    subprocess.run([cargo,'test','--manifest-path',crate,'--test','adaptive_history','--locked'],check=True)
    sourcefiles=['rust/rei_microphysics/src/adaptive_history.rs','rust/rei_microphysics/examples/first_interval.rs','rust/rei_microphysics/src/lib.rs']
    sid=hashlib.sha256(b''.join(Path(f).read_bytes() for f in sourcefiles)).hexdigest();out=P/'pilot'/sid;out.mkdir(parents=True,exist_ok=True)
    subprocess.run([cargo,'run','--quiet','--release','--manifest-path',crate,'--example','first_interval','--locked','--','--input','docs/atomic_reionization_handoff_20261004_v1/runtime_inputs/ft03_first_interval.json','--output',str(out),'--pilot'],check=True)
    result=validate_run(out,True);(P/'qualification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))


if __name__=='__main__':
    main()
