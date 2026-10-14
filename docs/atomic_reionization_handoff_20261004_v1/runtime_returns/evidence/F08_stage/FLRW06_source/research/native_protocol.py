"""I/O and independent comparison for the pending real Rust run."""
from pathlib import Path
import json,math
ROOT=Path(__file__).resolve().parents[1]

def stdin_payload(data):
    lines=[str(len(data['cases']))]
    def nums(values):return ' '.join(str(x) if isinstance(x,str) else repr(float(x)) for x in values)
    for c in data['cases']:
        lines.extend([nums([c['mean_scale_factor'],*c['n']]),str(len(c['nodes']))])
        lines.extend(nums([n['energy_ev'],n['n_comoving_per_cmpc3']]) for n in c['nodes'])
    p=data['photon_input'];lines.append(nums([p['scale_factor'],p['hubble_s'],*p['comoving_photons_cm3'],*p['edge_energy_ev'],*p['edge_n_per_cm3_ev'],*p['source_proper_cm3_s']]))
    return '\n'.join(lines)+'\n'

def validate_records(records,data,ref):
    if len(records)!=len(data['cases'])+1:raise ValueError('NATIVE_RECORD_COUNT')
    worst=0.0;comparisons=0
    def compare(actual,expected):
        nonlocal worst,comparisons
        actual=float(actual);expected=float(expected)
        if not math.isfinite(actual):raise ValueError('NATIVE_NONFINITE_OUTPUT')
        comparisons+=1
        if expected==0:
            if actual!=0:raise ValueError('NATIVE_EXPECTED_EXACT_ZERO')
        else:
            err=abs(actual-expected)/abs(expected);worst=max(worst,err)
            if err>data['tolerance']['relative']:raise ValueError('NATIVE_REFERENCE_DIFFERENCE')
    for index,c in enumerate(data['cases']):
        out=records[index]
        if out.get('kind')!='photo' or out.get('index')!=index:raise ValueError('NATIVE_RECORD_IDENTITY')
        if c.get('expect_error'):
            if out.get('status')!='error':raise ValueError('NATIVE_INVALID_INPUT_ACCEPTED')
            if out.get('error')!=c['expected_error']:raise ValueError('NATIVE_WRONG_ERROR_CLASS')
            continue
        if out.get('status')!='ok':raise ValueError('NATIVE_VALID_INPUT_REJECTED')
        rr=ref['references'][c['id']]
        for k in ['gamma','events','heat','binding']:
            if len(out[k])!=3:raise ValueError('NATIVE_ARRAY_LENGTH')
            for v,w in zip(out[k],rr[k]):compare(v,w)
        for k in ['absorbed','loss_comoving']:compare(out[k],rr[k])
    p=records[-1]
    if p.get('kind')!='photon' or p.get('status')!='ok':raise ValueError('NATIVE_PHOTON_STATUS')
    for k in ['dc','dp','flux']:
        if len(p[k])!=len(ref['photon'][k]):raise ValueError('NATIVE_ARRAY_LENGTH')
        for v,w in zip(p[k],ref['photon'][k]):compare(v,w)
    for k in ['loss','source','absorption']:compare(p[k],ref['photon'][k])
    # Cancellation residual has a scale-aware separate bound, not a relative
    # comparison against a mathematically zero target.
    scale=abs(float(p['source']))+abs(float(p['absorption']))+abs(float(p['loss']))
    res=float(p['residual'])
    if not math.isfinite(res) or abs(res)>5e-14*scale:raise ValueError('NATIVE_NUMBER_LEDGER')
    return {'compared_values':comparisons,'max_relative_difference':worst,'invalid_inputs_rejected':sum(bool(c.get('expect_error')) for c in data['cases']),'photon_residual':res,'photon_residual_scale':scale}

def evidence_gate(receipt):
    # Generated or copied Python expectation files cannot close this gate.
    if receipt.get('compile_exit')!=0 or receipt.get('run_exit')!=0 or receipt.get('source_blobs_verified') is not True:
        raise ValueError('MISSING_NATIVE_EXECUTION_EVIDENCE')
    if not receipt.get('compiler_version') or not receipt.get('stdout_sha256'):
        raise ValueError('MISSING_NATIVE_EXECUTION_IDENTITY')
