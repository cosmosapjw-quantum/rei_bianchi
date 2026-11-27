"""Read-only matter/radiation shear attribution on a supplied LRS history.

No Einstein, Boltzmann, chemistry or rate solver is executed. All signed
variables must use ONE common norm and the SAME instantaneous Hubble rate.
Finite sampled quadrature differences are diagnostics, never error bounds.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
from typing import Sequence


def _prefix_fsum(terms: Sequence[float]) -> list[float]:
    """Neumaier prefix sum, preserving input order."""
    total = correction = 0.0
    out = [0.0]
    for term in terms:
        candidate = total + term
        if abs(total) >= abs(term):
            correction += (total - candidate) + term
        else:
            correction += (term - candidate) + total
        total = candidate
        out.append(total + correction)
    return out


def decompose(n: Sequence[float], h: Sequence[float], shear: Sequence[float],
              matter: Sequence[float], radiation: Sequence[float],
              *, norm: str) -> dict:
    """Return conditional impulse attribution and normalized anisotropic work.

    n=ln(a), h=H in proper seconds^-1 > 0. For norm='half', shear=
    sqrt(3)*s/H and matter/radiation=sqrt(3)*(8*pi*G/c**2)*p_X/H**2.
    For norm='frobenius', replace sqrt(3) by sqrt(6) everywhere.
    pi_X=diag(-p_X,-p_X,2*p_X). Signed values, not norms, are inputs.
    """
    if norm not in ('half', 'frobenius'):
        raise ValueError('norm must explicitly be half or frobenius')
    arrays = [list(map(float, q)) for q in (n, h, shear, matter, radiation)]
    n, h, shear, matter, radiation = arrays
    count = len(n)
    if count < 2 or any(len(q) != count for q in arrays):
        raise ValueError('equal-length histories of at least two samples required')
    if not all(math.isfinite(x) for q in arrays for x in q):
        raise ValueError('nonfinite history')
    if any(x <= 0.0 for x in h) or any(b <= a for a, b in zip(n, n[1:])):
        raise ValueError('H must be positive and ln(a) strictly increasing')
    log_i = [3.0*(x-n[0])+math.log(y)-math.log(h[0]) for x,y in zip(n,h)]
    shift = max(log_i)
    weights = [math.exp(x-shift) for x in log_i]
    if min(weights) == 0.0:
        raise ValueError('integrating factor underflow; split the history, do not clip')
    def impulse(p):
        terms = [0.5*(n[j+1]-n[j]) *
                 math.fsum((weights[j]*p[j],weights[j+1]*p[j+1]))
                 for j in range(count-1)]
        return [value/w for value,w in zip(_prefix_fsum(terms),weights)]
    jm, jr = impulse(matter), impulse(radiation)
    free = [weights[0]*shear[0]/w for w in weights]
    prediction = [math.fsum(row) for row in zip(free,jm,jr)]
    defect = [actual-predicted for actual,predicted in zip(shear,prediction)]
    total = [math.fsum((m,r)) for m,r in zip(matter,radiation)]
    work_factor = 2.0 if norm == 'half' else 1.0
    wm = [work_factor*s*p for s,p in zip(shear,matter)]
    wr = [work_factor*s*p for s,p in zip(shear,radiation)]
    cancellation = [0.0 if abs(m)+abs(r)==0 else
                    1.0-abs(t)/(abs(m)+abs(r))
                    for m,r,t in zip(matter,radiation,total)]
    coarse = None
    if count >= 5:
        indices = list(range(0,count,2))
        if indices[-1] != count-1: indices.append(count-1)
        nc,hc,sc,mc,rc = [[q[i] for i in indices] for q in arrays]
        # One direct endpoint trapezoid, avoiding recursive coarsening.
        lc=[3*(x-nc[0])+math.log(y)-math.log(hc[0]) for x,y in zip(nc,hc)]
        wc=[math.exp(x-max(lc)) for x in lc]
        coarse={}
        for label,p,full in [('matter',mc,jm[-1]),('radiation',rc,jr[-1])]:
            val=math.fsum(0.5*(nc[j+1]-nc[j]) *
                          math.fsum((wc[j]*p[j],wc[j+1]*p[j+1]))
                          for j in range(len(nc)-1))/wc[-1]
            coarse[label+'_fine_minus_coarse']=full-val
    rows=[dict(ln_a=n[i],H_per_s=h[i],signed_shear=shear[i],
               signed_Pi_m=matter[i],signed_Pi_r=radiation[i],
               signed_Pi_total=total[i],Pi_m=abs(matter[i]),Pi_r=abs(radiation[i]),
               Pi_total=abs(total[i]),free_shear=free[i],matter_impulse=jm[i],
               radiation_impulse=jr[i],predicted_shear=prediction[i],
               sampled_closure_defect=defect[i],cancellation_fraction=cancellation[i],
               normalized_work_m=wm[i],normalized_work_r=wr[i]) for i in range(count)]
    return dict(schema='LRS_COMPONENT_SHEAR_ATTRIBUTION_V1', norm=norm,
                mathematical_scope='CONDITIONAL_ON_THE_SAME_STORED_TRAJECTORY',
                quadrature='COMPOSITE_TRAPEZOID_NEUMAIER_PREFIX',
                continuous_error_certified=False,causal_component_ablation=False,
                samples=count,endpoint=rows[-1],
                max_abs_sampled_closure_defect=max(map(abs,defect)),
                endpoint_coarsening_diagnostic=coarse,rows=rows)


def analyze_csv(input_path: Path, mapping_path: Path, output_dir: Path) -> dict:
    spec=json.loads(mapping_path.read_text(encoding='utf-8'))
    if spec.get('signed_inputs') is not True:
        raise ValueError('mapping must affirm signed_inputs=true')
    required={'time','H','shear','matter','radiation','norm','time_kind'}
    if not required <= spec.keys(): raise ValueError('incomplete explicit column mapping')
    if spec['time_kind'] not in ('a','ln_a'): raise ValueError('time_kind must be a or ln_a')
    with input_path.open(encoding='utf-8-sig',newline='') as f:
        reader=csv.DictReader(f); header=reader.fieldnames or []
        fields=[spec[x] for x in ('time','H','shear','matter','radiation')]
        if any(field not in header for field in fields): raise ValueError('mapped column missing')
        groups={}
        for row in reader:
            key=row[spec['case_id']] if spec.get('case_id') else 'single'
            values=[float(row[field]) for field in fields]
            if spec['time_kind']=='a':
                if values[0] <= 0: raise ValueError('a <= 0')
                values[0]=math.log(values[0])
            groups.setdefault(key,[]).append(values)
    output_dir.mkdir(parents=True,exist_ok=False)
    summaries=[]
    for index,(key,records) in enumerate(sorted(groups.items())):
        # Preserve recorded order, so duplicate/reversed epochs are errors.
        values=list(zip(*records))
        result=decompose(*values,norm=spec['norm'])
        rows=result.pop('rows'); result['case_id']=key
        filename=f'case_{index:06d}.csv'
        with (output_dir/filename).open('x',encoding='utf-8',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
        result['history_file']=filename;summaries.append(result)
    report=dict(schema='LRS_COMPONENT_POSTPROCESS_RECEIPT_V1',
                input_sha256=hashlib.sha256(input_path.read_bytes()).hexdigest(),
                mapping_sha256=hashlib.sha256(mapping_path.read_bytes()).hexdigest(),
                source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                new_ode_integrations=0,new_benchmarks=0,new_NCP_launches=0,
                continuous_error_certified=False,cases=summaries)
    (output_dir/'ATTRIBUTION.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',required=True,type=Path)
    parser.add_argument('--mapping',required=True,type=Path)
    parser.add_argument('--out',required=True,type=Path)
    args=parser.parse_args()
    report=analyze_csv(args.input,args.mapping,args.out)
    print(json.dumps({'cases':len(report['cases']),'new_ode_integrations':0,
                      'receipt':str(args.out/'ATTRIBUTION.json')}))
