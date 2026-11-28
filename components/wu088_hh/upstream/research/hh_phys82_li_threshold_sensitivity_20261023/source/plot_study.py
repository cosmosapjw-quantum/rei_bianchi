"""Render frozen PHYS82 results only; no physical-rate callbacks."""
from pathlib import Path
import argparse, hashlib, json, math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
COLORS={'L0':'#0072B2','L1':'#56B4E9','W0':'#D55E00','W1':'#E69F00','ZA1969':'#009E73'}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,default=ROOT);a=ap.parse_args();root=a.root
    src=root/'results/THRESHOLD_STUDY.json';raw=src.read_bytes();d=json.loads(raw)
    if d['status']!='COMPLETE_SCOPED':raise ValueError('COMPLETE_SAVED_RESULT_REQUIRED')
    out=root/'figures';out.mkdir(exist_ok=True)
    names=['01_rates_and_enhancement','02_gap_fraction_and_energy','03_prescribed_exposure']
    if any((out/(n+ext)).exists() for n in names for ext in ['.png','.pdf']):raise FileExistsError('FIGURE_OUTPUT_EXISTS')
    rows={n:sorted([r for r in d['rate_rows'] if r['model']==n],key=lambda r:r['T_K']) for n in COLORS}
    base=sorted(d['baseline_rows'],key=lambda r:r['T_K']);T=np.array([r['T_K'] for r in base])
    plt.rcParams.update({'font.size':10,'axes.titlesize':12,'axes.spines.top':False,'axes.spines.right':False,'figure.dpi':140,'savefig.dpi':170})
    def axes(title):
        f,axs=plt.subplots(1,2,figsize=(11.6,4.5),layout='constrained');f.suptitle(title,fontsize=14)
        for ax in axs:ax.set_xscale('log');ax.set_xlabel('Prescribed electron temperature T [K]');ax.grid(alpha=.22)
        return f,axs
    def save(f,n):
        f.savefig(out/(n+'.png'));f.savefig(out/(n+'.pdf'));plt.close(f)
    f,axs=axes('PHYS82 | Conditional Li7 threshold-gap models')
    axs[0].plot(T,[r['rate']['logK_cm3_s']/math.log(10) for r in base],color='#333333',ls=':',label='CCC 6–15 eV only')
    for n,rr in rows.items():
        style='--' if n=='ZA1969' else '-'
        axs[0].plot(T,[r['total']['logK_cm3_s']/math.log(10) for r in rr],color=COLORS[n],ls=style,label=n)
        axs[1].plot(T,[r['total_over_baseline'] for r in rr],color=COLORS[n],ls=style,label=n)
    axs[0].set_ylabel('log10 K [cm³ s⁻¹]');axs[0].legend(fontsize=8,loc='lower right')
    axs[1].set_yscale('log');axs[1].set_ylabel('K(total finite) / K(CCC only)');axs[1].legend(fontsize=8)
    axs[0].set_title('Absolute rates vanish toward low T');axs[1].set_title('Relative enhancement can grow strongly')
    save(f,names[0])
    f,axs=axes('PHYS82 | Source-gap weight and reaction-selected energy')
    axs[1].plot(T,[r['rate']['mean_excess_over_chemical_eV'] for r in base],color='#333333',ls=':',label='CCC only')
    for n,rr in rows.items():
        style='--' if n=='ZA1969' else '-'
        axs[0].plot(T,[100*r['gap_fraction'] for r in rr],color=COLORS[n],ls=style,label=n)
        axs[1].plot(T,[r['total']['mean_excess_over_chemical_eV'] for r in rr],color=COLORS[n],ls=style,label=n)
    axs[0].set_ylabel('Gap contribution to total finite rate [%]');axs[0].set_ylim(-2,102)
    axs[1].set_ylabel('Reaction-selected mean (E − I) [eV]')
    axs[0].set_title('Conditional source dependence');axs[1].set_title('Thermal loss per event remains I = 5.39172 eV')
    axs[0].legend(fontsize=8);axs[1].legend(fontsize=8);save(f,names[1])
    f,axs=axes('PHYS82 | Prescribed exposure diagnostic; coupled feedback excluded')
    exps=sorted({r['exposure_cm3_inverse_s'] for r in d['exposure_rows']})
    er={(n,L):sorted([r for r in d['exposure_rows'] if r['model']==n and r['exposure_cm3_inverse_s']==L],key=lambda r:r['T_K']) for n in COLORS for L in exps}
    axs[0].plot(T,[r['baseline_probability'] for r in er['L0',1e11]],color='#333333',ls=':',label='CCC only')
    for n in COLORS:axs[0].plot(T,[r['total_probability'] for r in er[n,1e11]],color=COLORS[n],ls='--' if n=='ZA1969' else '-',label=n)
    for L,col in zip(exps,['#0072B2','#D55E00','#CC79A7']):
        lo=np.array([r['delta_probability'] for r in er['W0',L]]);hi=np.array([r['delta_probability'] for r in er['L1',L]])
        axs[1].fill_between(T,lo,hi,color=col,alpha=.25)
        axs[1].plot(T,(lo+hi)/2,color=col,label=f'Λ = {L:.0e} cm⁻³ s')
        axs[1].plot(T,[r['delta_probability'] for r in er['ZA1969',L]],color=col,ls='--',lw=1)
    for ax in axs:ax.set_xlim(1000,50000);ax.legend(fontsize=8)
    axs[0].set_ylabel('Ionization probability P');axs[0].set_title('Λ = 10¹¹ cm⁻³ s; T and nₑ imposed')
    axs[1].set_ylabel('Gap-induced probability increment ΔP');axs[1].set_title('Shading: matched family; dashed: ZA1969')
    save(f,names[2])
    keys=[255.,1000.,3000.,10000.,25370.66308424773,50000.]
    summary={'schema':'PHYS82_POSTPROCESS_V1','input_SHA256':hashlib.sha256(raw).hexdigest(),'science_id':d['science_id'],'scientific_rate_callbacks':0,'ODE':0,'key_rates':[r for r in d['rate_rows'] if r['T_K'] in keys],'source_consistency':d['source_consistency'],'exposure_peaks':[max([r for r in d['exposure_rows'] if r['model']==n and r['exposure_cm3_inverse_s']==L],key=lambda r:r['delta_probability']) for L in exps for n in COLORS],'sampled_family_width_max':max(d['family_envelope_rows'],key=lambda r:r['upper_over_lower_rate']),'figures':[]}
    for n in names:
        for ext in ['.png','.pdf']:
            p=out/(n+ext);b=p.read_bytes();summary['figures'].append({'path':p.relative_to(root).as_posix(),'bytes':len(b),'SHA256':hashlib.sha256(b).hexdigest()})
    with (root/'results/POSTPROCESS.json').open('x') as f:json.dump(summary,f,indent=2);f.write('\n')
    print(json.dumps({'status':'SAVED_RESULT_POSTPROCESS_COMPLETE','science_callbacks':0,'figures':len(summary['figures'])}))

if __name__=='__main__':main()
