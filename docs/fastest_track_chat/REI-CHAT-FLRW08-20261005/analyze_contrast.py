"""Exact binary-sample diagnostics for completed F08; no trajectory execution.

Richardson values and contraction thresholds are conditional diagnostics, never
continuous-solution certificates. Fractions retain exact stored binary64 values.
"""
from pathlib import Path
from fractions import Fraction as Q
import argparse, csv, gzip, hashlib, json, math, struct

LEVELS = ('T0', 'T1', 'T2')
OBS = ('x_HII', 'temperature_K', 'photon_n', 'photon_u_ev_per_h')
DT = {'T0':1250000000, 'T1':625000000, 'T2':312500000}
END = 10000000000000

def number(text):
    x = float(text)
    if not math.isfinite(x):
        raise ValueError('nonfinite sample')
    return Q(x)

def pack(x):
    return {'approx':float(x), 'exact':str(x)}

def rows(path):
    out = {}
    with gzip.open(path, 'rt') as f:
        for row in csv.DictReader(f):
            t = number(row['time_s'])
            if t in out or t <= 0 or (out and t <= next(reversed(out))):
                raise ValueError('duplicate/nonincreasing time')
            out[t] = {key:number(row[key]) for key in OBS}
    if not out or max(out) != END:
        raise ValueError('incomplete history')
    return out

def checkpoint(path, level):
    lines = path.read_text().splitlines()
    h = lines[0].split()
    def binary(x):
        return number(struct.unpack('>d', bytes.fromhex(x))[0])
    if h[0] not in ('REI_F08_PAIRED_CHECKPOINT_V1','REI_F08_PAIRED_CHECKPOINT_V2') or list(map(int,h[1:4])) != [8,8,16]:
        raise ValueError('checkpoint grid mismatch')
    if int(h[4]) != END//DT[level] or int(h[5]) != 0 or binary(h[6]) != DT[level]:
        raise ValueError('checkpoint history mismatch')
    state = list(map(binary, lines[1].split()))
    box = list(map(binary, lines[3].split()))
    if state[0] != END or len(box) != 8:
        raise ValueError('checkpoint endpoint mismatch')
    for i in range(4):
        if not box[2*i] <= state[i+1] <= box[2*i+1]:
            raise ValueError('checkpoint point outside box')
    return state[1], (box[0],box[1])

def analyze(root, helper):
    weights = list(map(Q,helper['richardson_weights']))
    polynomial = list(map(Q,helper['invisible_shift_coefficients']))
    nodes = [Q(1),Q(1,2),Q(1,4)]
    if len(weights)!=3 or len(polynomial)!=4 or any(sum(w*z**k for w,z in zip(weights,nodes)) != (1 if k==0 else 0) for k in range(3)):
        raise ValueError('invalid Richardson moments')
    P = lambda z:sum(a*z**i for i,a in enumerate(polynomial))
    if P(0)!=1 or any(P(z)!=0 for z in nodes):
        raise ValueError('invalid invisible-shift witness')
    histories = {}; inputs = {}; endpoints = {}
    def bind(p):
        inputs[str(p.relative_to(root))] = hashlib.sha256(p.read_bytes()).hexdigest()
    for level in LEVELS:
        endpoints[level] = {}
        for geo in ('BI','FLRW'):
            label=level+'_'+geo
            p=root/'curves'/(label+'.csv.gz');bind(p);histories[label]=rows(p)
            if list(histories[label]) != [Q(DT[level]*k) for k in range(1,END//DT[level]+1)]:
                raise ValueError('unexpected time grid')
            p=root/'receipts'/(label+'-checkpoint.dat');bind(p)
            point, box = checkpoint(p,level)
            if histories[label][Q(END)]['x_HII'] != point:
                raise ValueError('curve/checkpoint point mismatch')
            endpoints[level][geo]=(point,box)
    common = list(histories['T0_FLRW'])
    measured = {}
    for obs in OBS:
        C = [[histories[level+'_BI'][t][obs]-histories[level+'_FLRW'][t][obs] for t in common] for level in LEVELS]
        a=[y-x for x,y in zip(C[0],C[1])];b=[y-x for x,y in zip(C[1],C[2])]
        i=max(range(len(common)),key=lambda k:abs(b[k]));ratio=None
        if b[-1]!=0:
            ratio=pack(abs(a[-1]/b[-1]))
        measured[obs]={'matched_endpoints':len(common),'final_contrasts':[pack(v[-1]) for v in C],
            'final_changes':[pack(a[-1]),pack(b[-1])],
            'max_abs_change_01':pack(max(map(abs,a))), 'max_abs_change_12':pack(abs(b[i])),
            'time_of_max_change_12_s':pack(common[i]), 'final_change_ratio_01_over_12':ratio,
            'richardson_quadratic_final':pack(sum(w*v[-1] for w,v in zip(weights,C))),
            'richardson_authority':'CONDITIONAL_POINT_ESTIMATE_ONLY'}
    intervals = {}
    for level in LEVELS:
        bi=endpoints[level]['BI'][1];fl=endpoints[level]['FLRW'][1]
        intervals[level]=(bi[0]-fl[1],bi[1]-fl[0])
    delta=(intervals['T2'][0]-intervals['T1'][1],intervals['T2'][1]-intervals['T1'][0])
    bound=max(map(abs,delta));signal=intervals['T2'][0]
    if signal<=0:
        raise ValueError('expected positively separated discrete contrast')
    budget=signal/10
    return {'task_id':'REI-CHAT-FLRW08_PAIRED_TIME_ERROR_CONTROL','input_sha256':inputs,
        'comparison_time_s':END, 'matched_common_grid_points':len(common), 'measured':measured,
        'independent_endpoint_xHII_contrasts':{k:[pack(x) for x in v] for k,v in intervals.items()},
        'independent_T2_minus_T1_interval':[pack(x) for x in delta], 'delta2_bound':pack(bound),
        'conditional_tail':{'equation':'If |delta_(k+1)| <= q |delta_k| for every k>=2 and C_k converges to the SAME fixed spectral/angular continuous-time model: |C_inf-C2| <= q/(1-q) * delta2_bound.',
            'signal_fraction_target':'1/10 of certified T2 discrete lower signal; diagnostic choice, not a changed acceptance gate',
            'target_absolute_error':pack(budget),'q_strict_upper_for_target':pack(budget/(budget+bound)),
            'q_strict_upper_for_sign':pack(signal/(signal+bound)),
            'future_uniform_contraction':'NOT_ESTABLISHED','consistent_continuous_limit':'NOT_ESTABLISHED'},
        'refinement_only_falsifier':{'polynomial_constant_first':list(map(str,polynomial)),
            'formula':'Add A*P(h/h0) to any quadratic sample interpolant. The three observed samples are unchanged, but its h=0 limit shifts by A.',
            'scope':'Nonidentifiability from three samples alone; not an alternative solution of the frozen physical ODE or a counterexample to its consistency.',
            'exact_values_at_0_1_half_quarter':[str(P(z)) for z in [Q(0),*nodes]]},
        'new_campaign_executions':0,'continuum_time_error_certificate':'NOT_ESTABLISHED','scientific_admission':'HOLD'}

def plot(root, out):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    data={l+'_'+g:rows(root/'curves'/(l+'_'+g+'.csv.gz')) for l in LEVELS for g in ('BI','FLRW')}
    ts=list(data['T0_FLRW']);fig,axes=plt.subplots(2,1,figsize=(9,7),sharex=True)
    for l in LEVELS:
        y=[float(data[l+'_BI'][t]['x_HII']-data[l+'_FLRW'][t]['x_HII']) for t in ts]
        axes[0].plot([float(t)/1e13 for t in ts],y,label=l,lw=1)
    for lo,hi in (('T0','T1'),('T1','T2')):
        y=[float((data[hi+'_BI'][t]['x_HII']-data[hi+'_FLRW'][t]['x_HII'])-(data[lo+'_BI'][t]['x_HII']-data[lo+'_FLRW'][t]['x_HII'])) for t in ts]
        axes[1].plot([float(t)/1e13 for t in ts],y,label=hi+' - '+lo,lw=1)
    axes[0].set_ylabel('Discrete BI - FLRW xHII');axes[1].set_ylabel('Change in discrete contrast');axes[1].set_xlabel('Normal time / 1e13 s')
    for ax in axes:ax.grid(alpha=.2);ax.legend()
    fig.suptitle('Fixed S0 model, spectral and angular grids\nMeasured time refinement; continuum time certificate NOT_ESTABLISHED; physical HOLD')
    fig.tight_layout();fig.savefig(out/'contrast.png',dpi=150);fig.savefig(out/'contrast.pdf');plt.close(fig)

if __name__ == '__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--repo-root',type=Path,default=Path(__file__).resolve().parents[3]);parser.add_argument('--out',type=Path,required=True);parser.add_argument('--plot',action='store_true');args=parser.parse_args()
    here=Path(__file__).resolve().parent;helper=json.loads((here/'helper_coefficients.json').read_text());root=args.repo_root/'runs/rei_fastest_v1/paired'
    result=analyze(root,helper);args.out.mkdir(parents=True,exist_ok=True);(args.out/'RESULTS.json').write_text(json.dumps(result,indent=2)+'\n')
    if args.plot:plot(root,args.out)
    print(json.dumps({'task_id':result['task_id'],'points':result['matched_common_grid_points'],'certificate':result['continuum_time_error_certificate']}))
