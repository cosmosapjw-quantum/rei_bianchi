"""Presentation only: consume actual PR171 stored observations, no scientific run."""
import argparse,csv,hashlib,json,math
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
MYR=365.25*86400*1e6
SPECIES=['H_I','H_II','He_I','He_II','He_III','electron']
LABELS=['H I','H II','He I','He II','He III']
COLORS=['#0072B2','#D55E00','#009E73','#CC79A7','#E69F00']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def require(ok,message):
    if not ok:raise ValueError(message)
def write(p,data):p.write_text(json.dumps(data,indent=2)+'\n')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--contract',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    c=json.loads(args.contract.read_text());require(sha(__file__)==c['script_sha256'],'script changed');require(not args.output.exists(),'fresh results required')
    for entry in c['bound_inputs']:require(sha(entry['path'])==entry['sha256'],'immutable selected input mismatch: '+entry['path'])
    args.output.mkdir();case_reports={};outputs=[]
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10})
    for case in c['cases']:
        setup=json.loads(Path(case['setup']).read_text());obs=json.loads(Path(case['observations']).read_text());require(len(obs)==18,'all18 stored samples required')
        f=setup['he_h'];den=1+4*f;require(math.isfinite(f) and f>0,'he_h');require(setup['birth_count']==8,'8birth selection')
        rows=[];last_t=-math.inf;last_x=-math.inf
        for index,o in enumerate(obs):
            p=o['physical'];h,y,z,w=p['flat'][:4];t=p['proper_time_s'];temp=p['temperature_K'];x=o['x']
            require(all(math.isfinite(v) for v in (h,y,z,w,t,temp,x)),'finite native scalar');require(0<=h<=1 and y>=0 and z>=0 and y+z<=1,'fraction simplex')
            require(t>=0 and t>=last_t and x>=last_x and temp>0,'saved chronology/temperature');last_t=t;last_x=x
            require(o['side'] in ('pre','post') and type(o['active']) is int and 0<=o['active']<=8,'pre/post birth metadata')
            yy=[(1-h)/den,h/den,f*(1-y-z)/den,f*y/den,f*z/den,(h+f*(y+2*z))/den]
            require(all(math.isfinite(v) and 0<=v<=1 for v in yy),'finite baryon-normalized proportions')
            gamma=p['Gamma_s'];heat=p['heat_erg_per_absorber_s'];require(len(gamma)==len(heat)==3 and all(math.isfinite(v) and v>=0 for v in gamma+heat),'actual Gamma/heat')
            row={'case':case['label'],'stored_row':index,'ln_a':x,'side':o['side'],'active_cohorts':o['active'],'elapsed_proper_time_s':t,'elapsed_proper_time_Myr':t/MYR,'temperature_K':temp,'h_xHII':h,'y_xHeII':y,'z_xHeIII':z,'w_eV_per_H':w,'he_h':f}
            row.update(zip(SPECIES,yy));row.update(zip(['Gamma_HI_s^-1','Gamma_HeI_s^-1','Gamma_HeII_s^-1'],gamma));row.update(zip(['heat_HI_erg_per_absorber_s','heat_HeI_erg_per_absorber_s','heat_HeII_erg_per_absorber_s'],heat));rows.append(row)
        csvpath=args.output/(case['label']+'_all18_Y.csv')
        with csvpath.open('x',newline='') as stream:
            writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
        yy=np.array([[r[sp] for sp in SPECIES] for r in rows]);zero={sp:int(np.count_nonzero(yy[:,j]==0)) for j,sp in enumerate(SPECIES)}
        baryon_error=max(abs(sum(r[k] for k in ['H_I','H_II'])+4*sum(r[k] for k in ['He_I','He_II','He_III'])-1) for r in rows)
        case_reports[case['label']]={'q':case['q'],'stored_rows':len(rows),'pre_rows':sum(r['side']=='pre' for r in rows),'post_rows':sum(r['side']=='post' for r in rows),'finite_proportions':True,'proportion_min':float(yy.min()),'proportion_max':float(yy.max()),'max_baryon_identity_roundoff':baryon_error,'exact_zero_counts':zero,'he_h':f,'baryon_denominator_1plus4f':den,'time_origin':'native a0; actual serialized elapsed proper_time_s, not absolute cosmic age','initial_observation_time_s':rows[0]['elapsed_proper_time_s'],'last_time_s':rows[-1]['elapsed_proper_time_s'],'first_last_temperature_K':[rows[0]['temperature_K'],rows[-1]['temperature_K']],'all_samples_preserved':True,'zero_floors':False,'T_sorted':False,'Gamma_heat_available_in_all18_rows':True,'native_node_by_node_payload':'not exported in selected observations; exact PreparedAbsorption node sums are used in reviewed source, no new replay','endpoint_Gamma_s':obs[-1]['physical']['Gamma_s'],'endpoint_heat_erg_per_absorber_s':obs[-1]['physical']['heat_erg_per_absorber_s']}
        outputs.append({'path':csvpath.name,'sha256':sha(csvpath),'bytes':csvpath.stat().st_size})
        for coord in ('elapsed_time','Tgas_chronological'):
            xs=np.array([r['elapsed_proper_time_Myr'] if coord=='elapsed_time' else r['temperature_K'] for r in rows])
            fig,(ion,ele)=plt.subplots(2,1,figsize=(10,7.4),sharex=True,gridspec_kw={'height_ratios':[3,1.4]},layout='constrained')
            for j,label in enumerate(LABELS):ion.plot(xs,np.ma.masked_where(yy[:,j]==0,yy[:,j]),label=label,color=COLORS[j],lw=1.4,marker='.',ms=4)
            ele.plot(xs,np.ma.masked_where(yy[:,5]==0,yy[:,5]),color='#333333',label='electron',lw=1.4,marker='.',ms=4)
            for ax in (ion,ele):ax.set_yscale('log');ax.grid(alpha=.2);ax.legend(loc='best',ncol=3 if ax is ion else 1)
            ion.set_ylabel(r'$Y_i=n_i/(n_H+4n_{He})$');ele.set_ylabel(r'$Y_e=n_e/(n_H+4n_{He})$')
            ele.set_xlabel('Elapsed proper time since native a0 = 1/21 [Myr]' if coord=='elapsed_time' else 'Gas temperature [K] — stored chronological path')
            if coord=='elapsed_time':ele.set_xlim(left=0)
            else:
                for j,ax,color in ((0,ion,COLORS[0]),(5,ele,'#333333')):
                    for left,right in ((2,4),(8,10),(14,16)):
                        if yy[left,j]>0 and yy[right,j]>0 and (xs[left]!=xs[right] or yy[left,j]!=yy[right,j]):ax.annotate('',xy=(xs[right],yy[right,j]),xytext=(xs[left],yy[left,j]),arrowprops={'arrowstyle':'->','color':color,'lw':1.3})
            fig.suptitle(case['label']+' | short warm analytic MD14 | delta ln(a) = 0.002\n8-birth conditional positive reference; source-age/spectral/native-time accuracy HOLD')
            ion.text(.01,1.015,'Exact zeros masked: '+', '.join(label+' '+str(zero[sp]) for label,sp in zip(LABELS,SPECIES)),transform=ion.transAxes,fontsize=8)
            ion.text(.01,.015,'All18 stored pre/post samples; initial setup T8000K; no fabricated t0 sample',transform=ion.transAxes,fontsize=8)
            ele.text(.01,.03,'Electron excluded from baryon inventory; exact zeros masked: '+str(zero['electron']),transform=ele.transAxes,fontsize=8)
            name=case['label']+'_Y_vs_'+coord+'.png';fig.savefig(args.output/name,dpi=160);plt.close(fig);path=args.output/name;outputs.append({'path':name,'sha256':sha(path),'bytes':path.stat().st_size})
    write(args.output/'PRESENTATION_RECEIPT.json',{'status':'EXISTING_PR171_REFERENCE_REUSED_PRESENTATION_COMPLETE','source_commit':c['source_commit'],'existing_review_reused':c['review_decisions'],'cases':case_reports,'outputs':outputs,'no_scientific_run':True,'downsampled':False,'D_or_other_isotopes_added':False,'physical_admission':'NOT_ISSUED','new_review_requested':False,'versions':{'numpy':np.__version__,'matplotlib':matplotlib.__version__}})
    print(json.dumps({'figures':4,'CSVs':2,'rows_per_case':18,'status':'EXISTING_PR171_REFERENCE_REUSED_PRESENTATION_COMPLETE'}))
if __name__=='__main__':main()
