"""Read exact PR159 22 original NCP outputs and classify convergence evidence.

Consecutive-difference ratios are NOT convergence order proofs. Use signed
Richardson diagnostics with the same case/initial state/final log-scale, and
preserve 4/8/16 endpoint raw values. Designed to falsify incorrect attribution
of raw radiation-source quadrature errors to nonasymptotic thermal chemistry.
"""
from __future__ import annotations
import base64,csv,hashlib,json,math
from pathlib import Path

ROOT=Path(__file__).resolve().parent
RAW=ROOT/'evidence'/'raw'
FIELDS=('temperature_k','x_hii','x_heii','source_n_per_h','source_u_ev_per_h')

def sha(b):return hashlib.sha256(b).hexdigest()

def load_raw(root:Path=RAW):
    if not (root/'RAW_IDENTITY.json').exists():
        compact=json.loads((root.parent/'RAW_SNAPSHOT.json').read_text())
        receipt=compact['receipt'];raw={}
        assert receipt['case_count']==22 and len(receipt['files'])==44
        for item in receipt['files']:
            data=base64.b64decode(compact['base64_files'][item['path']],validate=True)
            assert sha(data)==item['sha256'] and len(data)==item['size_bytes']
            if item['path'].endswith('/result.json'):
                raw[item['path'].split('/')[0]]=json.loads(data)
        assert len(raw)==22
        return raw,receipt
    receipt=json.loads((root/'RAW_IDENTITY.json').read_text())
    assert receipt['case_count']==22 and len(receipt['files'])==44
    raw={}
    for item in receipt['files']:
        p=root/item['path']; data=p.read_bytes()
        assert sha(data)==item['sha256'] and len(data)==item['size_bytes'],item['path']
        if item['path'].endswith('/result.json'):
            d=json.loads(data)
            raw[p.parent.name]=d
    assert len(raw)==22
    return raw,receipt

def fit_q(y4,y8,y16):
    """Local three-value quadratic interpolant, NOT an established asymptotic law.

    y(h)=limit+A*h+B*h*h with finest step h. Returns dimensionful A*h,B*h².
    """
    dc=y4-y8;df=y8-y16
    second=(dc-2*df)/6
    first=df-3*second
    lim=y16-first-second
    predicted32=lim+first/2+second/4
    return {'coarse_signed':dc,'fine_signed':df,
            'observed_abs_ratio':abs(dc/df) if df else None,
            'effective_p_log2':math.log2(abs(dc/df)) if df and dc else None,
            'first_term_Ah':first,'second_term_Bh2':second,
            'B_h_over_A':second/first if first else None,
            'quadratic_limit_conditional':lim,
            'next_32_predicted_conditional':predicted32}

def analyze(raw=None):
    if raw is None:raw,_=load_raw()
    report={'schema':'rei.bass.pr159.longstep.adversarial.v1','origin':'PR159 original NCP 22 results',
            'cases':{},'warning':'Three values fit a quadratic but do not prove asymptotic first-order convergence'}
    for tag in ('cold','signed'):
        per={}
        for segment in ('short','long'):
            names=[f'release_{tag}_{segment}_{kind}' for kind in ('g481','t8','t16')]
            rows=[raw[n] for n in names]
            assert len({row['case'] for row in rows})==1
            assert len({row['grid_points'] for row in rows})==1
            assert len({row['steps']*row['dln_a'] for row in rows})==1
            assert all(row['restart_max_abs']==0.0 for row in rows)
            assert all(row['adaptive_status']=='ACCEPTED' for row in rows)
            out={}
            for k in FIELDS:
                out[k]=fit_q(*(row[k] for row in rows))
            per[segment]={'step_dln_a':[row['dln_a'] for row in rows],
                          'values':{k:[row[k] for row in rows] for k in FIELDS},
                          'newton_residual':[row['newton_residual'] for row in rows],
                          'final_scale_factor':[row['a'] for row in rows],
                          'proper_time_s':[row['time_s'] for row in rows],
                          'diagnostics':out}
        report['cases'][tag]=per
    # Geometry and initial-source differences should not be conflated with a
    # signed temperature difference across unmatched cosmological eras.
    report['cross_case_similarity']={k:abs(report['cases']['cold']['long']['diagnostics'][k]['observed_abs_ratio']-
        report['cases']['signed']['long']['diagnostics'][k]['observed_abs_ratio']) for k in FIELDS}
    report['hypotheses']={
        'newborn_full_cell_exposure':'source mixed at midpoint then photon+gas backward Euler consumes full proper-time slab',
        'opposite_biases':'old BE photons underabsorbed, uniformly born BE photons overabsorbed versus constant-hazard exact transport',
        'near_acceptance_newton':'long 16-step max Newton norm close to 1e-11 while long 4/8 ~1e-16',
        'source_counts':'source_n ratio ~4 is consistent with midpoint quadrature in this sample and not chemistry temperature order',
        'not_proven':'No native ablation of birth handling, tolerance, and opacity yet; PR159 long chemistry remains HOLD'}
    return report

if __name__=='__main__':
    data=analyze()
    out=ROOT/'evidence'/'PR159_RAW_AUDIT.json'
    out.write_text(json.dumps(data,indent=2,sort_keys=True)+'\n')
    for tag in ('cold','signed'):
        vals=data['cases'][tag]['long']['diagnostics']
        print(tag,'T_ratio',vals['temperature_k']['observed_abs_ratio'],
              'source_count_ratio',vals['source_n_per_h']['observed_abs_ratio'],
              'T_pred_t32_conditional',vals['temperature_k']['next_32_predicted_conditional'],
              'Newton_residuals',data['cases'][tag]['long']['newton_residual'])
