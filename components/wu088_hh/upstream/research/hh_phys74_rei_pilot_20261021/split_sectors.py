"""Read-only PHYS74 history postprocessing; never import or run an ODE solver."""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import platform
import numpy as np
from sector_diagnostics import lrs_sector_norms

KAPPA_TIME = 8*math.pi*6.67430e-11/299792458.0**2
HERE = Path(__file__).resolve().parent

def canonical(x):
    return (json.dumps(x, indent=2, sort_keys=True, allow_nan=False)+'\n').encode()

def sha(data):
    return hashlib.sha256(data).hexdigest()

def scalar(x):
    x = np.asarray(x).item()
    return None if isinstance(x, float) and not math.isfinite(x) else x

def write_csv(path, rows):
    with path.open('x', newline='') as stream:
        w = csv.DictWriter(stream, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)

def process(source, out):
    source, out = Path(source).resolve(), Path(out).resolve()
    identity_path = source/'IDENTITY.json'
    identity = json.loads(identity_path.read_text())
    pin = sha(canonical(identity))
    paths = sorted((source/'cases').glob('case-*.json'))
    if len(paths) != 63:
        raise ValueError('this observer is bound to the complete PHYS74 control63 only')
    rows, endpoints, inputs, seen = [], [], {}, set()
    max_norm_residual = max_work_residual = max_old_total_difference = 0.
    for path in paths:
        data = path.read_bytes(); inputs[str(path.relative_to(source))] = sha(data)
        envelope = json.loads(data); result = envelope['result']; req = result['request']
        if envelope['identity_sha256'] != pin or envelope['result_sha256'] != sha(canonical(result)):
            raise ValueError('input content/identity binding failed: '+path.name)
        if req['case_id'] in seen:raise ValueError('duplicate physical case ID')
        seen.add(req['case_id'])
        history = result['history']
        if len(history) != req['points'] or req['points'] != 81:
            raise ValueError('incomplete stored history')
        h = np.array([z['H_per_s'] for z in history])
        s = np.array([z['s_per_s'] for z in history])
        pm = np.array([z['pi_s_massive_J_m3'] for z in history])
        # Both named radiation species remain exported; only their signed sum forms r.
        pr = np.array([math.fsum((z['pi_s_gamma_J_m3'],z['pi_s_nu_J_m3'])) for z in history])
        d = lrs_sector_norms(h, s, pm, pr, kappa_time=KAPPA_TIME)
        scale = np.maximum(d['Pi_m_F']**2+d['Pi_r_F']**2, np.finfo(float).tiny)
        nr = float(np.max(np.abs(d['norm_square_residual'])/scale))
        wscale = np.maximum(np.abs(d['work_m'])+np.abs(d['work_r']), np.finfo(float).tiny)
        wr = float(np.max(np.abs(d['work_additivity_residual'])/wscale))
        max_norm_residual=max(max_norm_residual,nr);max_work_residual=max(max_work_residual,wr)
        old_total = np.array([z['Pi_F'] for z in history])
        diff = np.abs(d['Pi_total_F']-old_total)
        bound = 64*np.finfo(float).eps*np.maximum(d['Pi_m_F']+d['Pi_r_F'],np.finfo(float).tiny)
        if np.any(diff > bound) or nr>1e-13 or wr>1e-13:
            raise ArithmeticError('sector algebra consistency failed')
        max_old_total_difference=max(max_old_total_difference,float(np.max(diff)))
        block=[]
        for j,z in enumerate(history):
            record={'case_id':req['case_id'],'sample':j,'x':z['x'],'zbar':z['zbar'],
                    'H_per_s':z['H_per_s'],'s_per_s':z['s_per_s'],
                    'pi_s_gamma_J_m3':z['pi_s_gamma_J_m3'],'pi_s_nu_J_m3':z['pi_s_nu_J_m3']}
            record.update({key:scalar(value[j]) for key,value in d.items()})
            block.append(record)
        rows.extend(block)
        endpoint={'case_id':req['case_id'],'input_Sigma0_signed':req['Sigma0_signed'],
                  'input_Pi_total0_signed':req['Pi0_signed'],'initial_matter_A':0.}
        for position,index in (('initial',0),('final',-1)):
            for key in ('Sigma_F','Sigma_signed','Pi_m_F','Pi_r_F','Pi_total_F','Pi_m_signed',
                        'Pi_r_signed','Pi_total_signed','work_m','work_r','work_total'):
                endpoint[position+'_'+key]=block[index][key]
        endpoints.append(endpoint)
    initial_m = [q['initial_Pi_m_F'] for q in endpoints]
    summary={'schema':'PHYS74_SECTOR_POSTPROCESS_V1','histories':len(paths),'samples':len(rows),
             'new_IVP_runs':0,'benchmarks':0,'NCP_runs':0,'native_subagent':'NOT_RUN',
             'primary_observables':['Sigma_F','Pi_m_F','Pi_r_F','work_m','work_r'],
             'total_is_auxiliary':True,'matter_initial_control':'A_m=0 fixed; numerical residual retained',
             'independent_matter_radiation_initial_sweep':False,
             'initial_Pi_m_range':[min(initial_m),max(initial_m)],
             'final_Pi_m_range':[min(q['final_Pi_m_F'] for q in endpoints),max(q['final_Pi_m_F'] for q in endpoints)],
             'final_Pi_r_range':[min(q['final_Pi_r_F'] for q in endpoints),max(q['final_Pi_r_F'] for q in endpoints)],
             'max_scaled_norm_square_residual':max_norm_residual,
             'max_scaled_work_additivity_residual':max_work_residual,
             'max_abs_difference_from_saved_total_Pi':max_old_total_difference,
             'HHe_feedback':False,'ionizing_source':False,'continuum_error_certified':False,'HH_R10':'OFF'}
    contract={'schema':'PHYS74_SECTOR_CONTRACT_V1','frame':'common normal orthonormal; non-tilted LRS',
              'H_unit':'s^-1 proper time','stress_unit':'J/m^3','norm':'full Frobenius; half outputs retained',
              'kappa_time_SI':KAPPA_TIME,'stress_representation':'pi_s=(P_parallel-P_perp)/3',
              'matter':['canonical finite-mass nonbaryonic species','remaining pressureless dust: zero stress by owner model'],
              'radiation':['photons','massless neutrino model'],
              'species_partition_rule':'fixed source-bound assignment; no equation-of-state-based switching or double counting',
              'radiation_species_retained':True,'missing_sectors_are_not_zero_filled':True,
              'next_initial_scan':['signed_Sigma0','signed_Pi_m0','signed_Pi_r0'],
              'next_scan_status':'NOT_EXECUTED; needs independently varied admissible matter and radiation distributions',
              'closed_two_sector_energy_exchange':'Q_m+Q_r=0 only if no external donor/escape sector'}
    # Fail before touching output if any input is invalid. Never overwrite earlier plots/raw.
    out.mkdir(parents=True,exist_ok=False)
    write_csv(out/'SECTOR_HISTORY.csv', rows);write_csv(out/'SECTOR_ENDPOINTS.csv',endpoints)
    (out/'SUMMARY.json').write_bytes(canonical(summary));(out/'SECTOR_CONTRACT.json').write_bytes(canonical(contract))
    receipt={'input_identity_sha256':pin,'input_files':inputs,'input_identity_file_sha256':sha(identity_path.read_bytes()),
             'source_files':{name:sha((HERE/name).read_bytes()) for name in ('sector_diagnostics.py','split_sectors.py','tensor_adapter.py')},
             'python':platform.python_version(),'numpy':np.__version__, 'new_IVP_runs':0}
    (out/'POSTPROCESS_RECEIPT.json').write_bytes(canonical(receipt))
    print(json.dumps(summary,indent=2));return summary


def plot_saved(out, figures):
    """Separate primary sector views from already-exported rows; no synthetic data."""
    import matplotlib.pyplot as plt
    out, figures=Path(out),Path(figures);figures.mkdir(parents=True,exist_ok=False)
    with (out/'SECTOR_HISTORY.csv').open() as stream:rows=list(csv.DictReader(stream))
    with (out/'SECTOR_ENDPOINTS.csv').open() as stream:ends=list(csv.DictReader(stream))
    chosen={(0.,.001),(.001,0.),(.001,.001),(.001,-.001),(.004,.001)}
    selected=[q for q in ends if (float(q['input_Sigma0_signed']),float(q['input_Pi_total0_signed'])) in chosen]
    for sector,scale,label in (('m',1e6,'Matter'),('r',1e3,'Radiation')):
        fig,ax=plt.subplots(figsize=(8.4,5.5),layout='constrained')
        for q in selected:
            b=[r for r in rows if r['case_id']==q['case_id']]
            text=f"S0={float(q['input_Sigma0_signed'])*1e3:g}, P_r0={float(q['initial_Pi_r_signed'])*1e3:.3g}"
            ax.plot([float(z['Sigma_F'])*1e3 for z in b],
                    [float(z['Pi_'+sector+'_F'])*scale for z in b],
                    marker='o',markevery=[0],label=text)
        ax.set_xlabel(r'$\Sigma=\|\sigma\|_F/H\quad[10^{-3}]$')
        exponent=-6 if sector=='m' else -3
        ax.set_ylabel(r'$\Pi_'+sector+r'=\kappa_t\|\pi^{('+sector+r')}\|_F/H^2\quad[10^{'+str(exponent)+r'}]$')
        ax.set_title(label+' stress: collisionless LRS Bianchi I\n'+r'$z:20\to4$; initial matter anisotropy fixed ($A_m=0$)',fontsize=12)
        ax.legend(title=r'Signed initial values [$10^{-3}$]',fontsize=8,title_fontsize=9)
        fig.suptitle('PRELIMINARY CONTROL: no H/He chemistry or ionizing source',fontsize=10)
        fig.savefig(figures/('SIGMA_PI_'+sector+'_trajectories.png'),dpi=170);plt.close(fig)
    q=next(q for q in selected if float(q['input_Sigma0_signed'])==.004)
    b=[r for r in rows if r['case_id']==q['case_id']]
    fig,ax=plt.subplots(figsize=(8.4,5.5),layout='constrained')
    for sector,style,label in (('m','--','Matter'),('r','-','Radiation')):
        ax.plot([float(z['x']) for z in b],[float(z['Pi_'+sector+'_signed']) for z in b],linestyle=style,label=label)
    ax.set_yscale('symlog',linthresh=1e-8);ax.set_xlabel(r'$\ln(a/a_0)$')
    ax.set_ylabel(r'Signed $P_X=\sqrt{6}\,\kappa_t p_X/H^2$ (symlog)')
    ax.set_title(r'Sector-resolved signed stress: $\Sigma_0=0.004$, $P_{r0}\simeq0.001$'+'\n'+r'$z:20\to4$; initial matter anisotropy fixed ($A_m=0$)',fontsize=12)
    ax.legend();fig.suptitle('PRELIMINARY COLLISIONLESS CONTROL; not an independent matter scan',fontsize=10)
    fig.savefig(figures/'SIGNED_MATTER_RADIATION.png',dpi=170);plt.close(fig)
    (figures/'FIGURE_MANIFEST.json').write_bytes(canonical({p.name:sha(p.read_bytes()) for p in sorted(figures.glob('*.png'))}))


def main(argv=None):
    ap=argparse.ArgumentParser();ap.add_argument('--input',required=True,type=Path);ap.add_argument('--out',required=True,type=Path)
    args=ap.parse_args(argv);process(args.input,args.out)
if __name__=='__main__':main()
