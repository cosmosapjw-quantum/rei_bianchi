#!/usr/bin/env python3
"""Reproduce actual-sample component figures and CSVs; no IVP calls."""
import sys,os,json,csv,math,time
ENTRY_STARTED=time.monotonic()
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
import unified_pilot as u
import numpy as np
os.environ.setdefault('MPLCONFIGDIR','/tmp/rei_matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from collections import OrderedDict
from types import MappingProxyType
READ_CACHE=OrderedDict()
READ_CACHE_MAX=512
OUT=u.ROOT/'z2_extension/figures'
OUT.mkdir(parents=True,exist_ok=True)
plt.rcParams.update({'font.size':10,'axes.labelsize':10,'axes.titlesize':11,'savefig.dpi':180,'pdf.fonttype':42})

def csvwrite(name,rows):
    keys=list(dict.fromkeys(k for r in rows for k in r))
    with (OUT/name).open('w',newline='') as f:w=csv.DictWriter(f,keys);w.writeheader();w.writerows(rows)
HISTORICAL={r['case_id']:r for r in json.loads((u.ROOT/'z2_extension/HISTORICAL_94_RECOVERY.json').read_text())}

def verified_plot_path(c,epoch):
    """Only completed, identity-bound raw enters any endpoint or history plot."""
    identifier=c.get('reuse',{}).get('original_case_id',c['id'])
    historical=('reuse' in c or 'P_m_i' not in c['config'])
    if epoch==2:p=u.ROOT/'z2_extension/results/cases'/identifier/'raw.npz'
    elif 'reuse' in c:p=u.ROOT/c['reuse']['raw_path']
    else:p=u.ROOT/('results/cases/' if historical else 'components/results/cases/')/identifier/'raw.npz'
    receipt=p.parent/'RESULT.json'
    if not receipt.exists():return None
    result=json.loads(receipt.read_text())
    if result.get('status')!='COMPLETED':return None
    expected_config=HISTORICAL[identifier]['config'] if historical else c['config']
    if result.get('id')!=identifier or result.get('config')!=expected_config:
        raise ValueError('PLOT_RESULT_IDENTITY_MISMATCH:'+str(receipt))
    if epoch==4 and historical:
        record=HISTORICAL[identifier]
        if u.sha(receipt)!=record['receipt_sha256'] or u.sha(p.parent/'INPUT.json')!=record['input_sha256']:
            raise ValueError('PLOT_HISTORICAL_RECEIPT_MISMATCH:'+str(receipt))
        expected_hash=record['raw_sha256']
    else:expected_hash=result.get('raw_sha256')
    if not p.exists() or not expected_hash or u.sha(p)!=expected_hash:
        raise ValueError('PLOT_COMPLETED_RAW_HASH_MISMATCH:'+str(p))
    return p

def read(c,epoch):
    identifier=c.get('reuse',{}).get('original_case_id',c['id']);key=(identifier,epoch)
    expected_config=HISTORICAL[identifier]['config'] if ('reuse' in c or 'P_m_i' not in c['config']) else c['config']
    if key in READ_CACHE:
        entry=READ_CACHE[key]
        if entry['config_digest']!=u.ad.digest(expected_config):raise ValueError('PLOT_CACHE_CONFIG_IDENTITY_MISMATCH:'+identifier)
        READ_CACHE.move_to_end(key);return entry['data']
    p=verified_plot_path(c,epoch)
    if p is None:return None
    with np.load(p) as f:r={k:f[k] for k in f.files}
    expected=153 if epoch==2 else 121
    if r.get('x',np.array([])).shape!=(expected,) or r.get('raw_y',np.empty((0,0))).shape[1:]!=(expected,):
        raise ValueError('PLOT_COMPLETED_RAW_SHAPE_MISMATCH:'+str(p))
    r=u.ad.components(r);r['signed_shear']=np.sqrt(6)*r['s']/r['H']
    for value in r.values():value.flags.writeable=False
    r=MappingProxyType(r)
    READ_CACHE[key]={'config_digest':u.ad.digest(expected_config),'data':r}
    if len(READ_CACHE)>READ_CACHE_MAX:READ_CACHE.popitem(last=False)
    return r

def save(fig,name):
    fig.savefig(OUT/(name+'.png'));fig.savefig(OUT/(name+'.pdf'))
    if name in ('opposite_component_histories','radiation_baseline_and_controls'):
        fig.set_size_inches(7.2,6.6 if name=='opposite_component_histories' else 7.4)
        for ax in fig.axes:
            ax.tick_params(labelsize=8)
            ax.xaxis.label.set_size(9);ax.yaxis.label.set_size(9)
            ax.title.set_size(9)
        if name=='opposite_component_histories':
            fig.axes[0].set_title(r'$P_{m,i}=+3\times10^{-4},\ P_{r,i}=-3\times10^{-4}$')
            fig.axes[1].set_title(r'$P_{m,i}=-3\times10^{-4},\ P_{r,i}=+3\times10^{-4}$')
            fig._suptitle.set_text('Initially opposing matter/radiation stresses\n153 epochs z=20→2; dotted line: saved z=4 join')
        else:
            fig._suptitle.set_text('Radiation baseline and scoped numerical checks\nActual endpoints and 64-node brightness samples')
            fig.axes[3].set_title('64-node brightness samples\n231 unique nominal cases')
        fig._suptitle.set_fontsize(11)
        fig.savefig(OUT/(name+'_print.png'));fig.savefig(OUT/(name+'_print.pdf'))
    plt.close(fig)

def selected_joint(comp):
    # One selected joint plane exposes signed-shear reversals and total-stress norm.
    selected=[c for c in comp if c['config']['Sigma_F_i']==.003]
    joint,ja=plt.subplots(2,2,figsize=(7.2,7.0),layout='constrained');joint_rows=[]
    signed_values=[read(c,z)['signed_shear'][-1] for c in selected for z in (4,2) if read(c,z) is not None]
    stress_values=[read(c,z)['Pi_total'][-1] for c in selected for z in (4,2) if read(c,z) is not None]
    signed_bound=max(map(abs,signed_values)) if signed_values else 1.
    stress_bound=max(stress_values) if stress_values else 1.
    for row,key in enumerate(('signed_shear','Pi_total')):
        norm=Normalize(-signed_bound,signed_bound) if row==0 else Normalize(0,stress_bound)
        for col,z in enumerate((4,2)):
            ax=ja[row,col];xx=[];yy=[];vv=[];badx=[];bady=[]
            for c in selected:
                ix=u.ad.MATTER.index(c['config']['P_m_i']);iy=u.ad.RADIATION.index(c['config']['P_r_i']);r=read(c,z)
                if r is None:badx.append(ix);bady.append(iy);continue
                xx.append(ix);yy.append(iy);vv.append(r[key][-1])
                if row==0:joint_rows.append({'id':c['id'],'Sigma_F_i':.003,'P_m_i':c['config']['P_m_i'],'P_r_i':c['config']['P_r_i'],'z_endpoint':z,'signed_shear':float(r['signed_shear'][-1]),'Sigma_F':float(r['Sigma_F'][-1]),'Pi_total':float(r['Pi_total'][-1]),'P_total':float(r['P_total'][-1])})
            sc=ax.scatter(xx,yy,c=vv,norm=norm,cmap='RdBu_r' if row==0 else 'viridis',marker='s',s=140,edgecolors='.35',linewidths=.4)
            ax.scatter(badx,bady,c='gray',marker='x')
            ax.set(xticks=range(5),yticks=range(5),xlim=(-.6,4.6),ylim=(-.6,4.6),title=f'z={z}: '+('signed shear' if row==0 else 'total stress magnitude'))
            ax.set_xticklabels(['−3','−1','0','1','3']);ax.set_yticklabels(['−10','−3','0','3','10'])
            ax.set_xlabel(r'$P_{m,i}$ [$10^{-4}$]');ax.set_ylabel(r'$P_{r,i}$ [$10^{-4}$]')
        cb=joint.colorbar(sc,ax=ja[row,:],fraction=.04,pad=.025);cb.set_label(r'$S_F$' if row==0 else r'$\Pi_F$',fontsize=10);cb.formatter.set_powerlimits((0,0))
    negative_z2=sum(r['signed_shear']<0 for r in joint_rows if r['z_endpoint']==2)
    joint.suptitle(r'$\Sigma_{F,i}=0.003$: $S_F=\sqrt{6}s/H$, $\Pi_F=|P_m+P_r|$'+f'\n25 actual samples; {negative_z2}/25 signed shears negative at z=2',fontsize=11)
    save(joint,'signed_shear_joint_sigma_0p003');csvwrite('signed_shear_joint_sigma_0p003.csv',joint_rows)

def main():
    comp=[c for c in u.component_cases() if not c['config']['guard']];rows=[]
    for c in comp:
        for z in (4,2):
            r=read(c,z);row={'component_case_id':c['id'],'original_reused_id':c.get('reuse',{}).get('original_case_id',''),
              'Sigma_F_i':c['config']['Sigma_F_i'],'P_m_i':c['config']['P_m_i'],'P_r_i':c['config']['P_r_i'],'z_endpoint':z,'state':'COMPLETED' if r is not None else 'PENDING'}
            if r is not None:row.update({k+'_end':float(v[-1]) for k,v in r.items() if v.ndim==1 and k!='x'})
            rows.append(row)
    csvwrite('component_endpoints_175_z4_z2.csv',rows)
    fig,axes=plt.subplots(4,7,figsize=(18.5,11),layout='constrained')
    cmap='RdBu_r'
    for row,(z,key) in enumerate(((4,'P_m'),(4,'P_r'),(2,'P_m'),(2,'P_r'))):
        values=[read(c,z)[key][-1] for c in comp if read(c,z) is not None];bound=max(map(abs,values)) if values else 1.;norm=Normalize(-bound,bound)
        for col,sigma in enumerate(u.ad.SIGMAS):
            ax=axes[row,col];x=[];y=[];v=[];badx=[];bady=[]
            for c in comp:
                if c['config']['Sigma_F_i']!=sigma:continue
                ix=u.ad.MATTER.index(c['config']['P_m_i']);iy=u.ad.RADIATION.index(c['config']['P_r_i']);r=read(c,z)
                if r is None:badx.append(ix);bady.append(iy)
                else:x.append(ix);y.append(iy);v.append(r[key][-1])
            sc=ax.scatter(x,y,c=v,norm=norm,cmap=cmap,marker='s',s=135,edgecolors='none');ax.scatter(badx,bady,c='gray',marker='x')
            ax.set(xticks=range(5),yticks=range(5),xlim=(-.6,4.6),ylim=(-.6,4.6))
            ax.set_xticklabels(['−3','−1','0','1','3'] if row==3 else []);ax.set_yticklabels(['−10','−3','0','3','10'] if col==0 else [])
            if row==0:ax.set_title(r'$\Sigma_{F,i}=$'+f'{sigma:g}')
            if row==3:ax.set_xlabel(r'$P_{m,i}$ [$10^{-4}$]')
            if col==0:ax.set_ylabel(f'z={z}, '+('$P_m$' if key=='P_m' else '$P_r$')+'\n'+r'$P_{r,i}$ [$10^{-4}$]')
        cb=fig.colorbar(sc,ax=axes[row,:],fraction=.015,pad=.01);cb.set_label(f'{key} at z={z} [dimensionless]');cb.formatter.set_powerlimits((0,0))
    fig.suptitle('Independent matter/radiation component endpoints: all 175 nominal samples\nCategorical positions labelled by physical initial values; colors use signed values, no interpolation',fontsize=14)
    save(fig,'component_planes_all175')
    # The full overview is navigation; these seven pages preserve print-size text.
    for sigma in u.ad.SIGMAS:
        detail,detail_axes=plt.subplots(2,2,figsize=(7.2,6.8),layout='constrained')
        for ax,(z,key) in zip(detail_axes.flat,((4,'P_m'),(4,'P_r'),(2,'P_m'),(2,'P_r'))):
            values=[read(c,z)[key][-1] for c in comp if read(c,z) is not None]
            bound=max(map(abs,values)) if values else 1.;norm=Normalize(-bound,bound)
            xx=[];yy=[];vv=[];badx=[];bady=[]
            for c in comp:
                if c['config']['Sigma_F_i']!=sigma:continue
                ix=u.ad.MATTER.index(c['config']['P_m_i']);iy=u.ad.RADIATION.index(c['config']['P_r_i']);r=read(c,z)
                if r is None:badx.append(ix);bady.append(iy)
                else:xx.append(ix);yy.append(iy);vv.append(r[key][-1])
            sc=ax.scatter(xx,yy,c=vv,norm=norm,cmap=cmap,marker='s',s=140,edgecolors='none')
            ax.scatter(badx,bady,c='gray',marker='x')
            ax.set(xticks=range(5),yticks=range(5),xlim=(-.6,4.6),ylim=(-.6,4.6),title=f'z={z}: signed '+key)
            ax.set_xticklabels(['−3','−1','0','1','3']);ax.set_yticklabels(['−10','−3','0','3','10'])
            ax.set_xlabel(r'$P_{m,i}$ [$10^{-4}$]');ax.set_ylabel(r'$P_{r,i}$ [$10^{-4}$]')
            cb=detail.colorbar(sc,ax=ax,fraction=.05,pad=.03);cb.set_label('dimensionless',fontsize=9);cb.formatter.set_powerlimits((0,0))
        detail.suptitle(r'$\Sigma_{F,i}=$'+f'{sigma:g}'+': all 25 actual component samples\nCategorical axes; same color scales as full-grid overview',fontsize=11)
        save(detail,'component_plane_sigma_'+format(sigma,'.4g').replace('.','p'))

    selected_joint(comp)
    # Exactly opposing component controls at zero initial shear.
    fig,axes=plt.subplots(2,2,figsize=(12.5,8.5),layout='constrained');history=[];history_shear_bound=0.
    for col,(m,r0) in enumerate(((.0003,-.0003),(-.0003,.0003))):
        c=next(c for c in comp if u.config_axes(c['config'])==(0.,m,r0));r=read(c,2)
        if r is None:continue
        z=1/r['a']-1
        history_shear_bound=max(history_shear_bound,float(np.max(np.abs(r['signed_shear']))),float(np.max(r['Sigma_F'])))
        for i in range(len(z)):history.append({'case_id':c['id'],'P_m_i':m,'P_r_i':r0,'epoch':i,'zbar':float(z[i]),**{k:float(r[k][i]) for k in ('x','a','elapsed_proper_s','b','P_m','P_r','P_total','Pi_m','Pi_r','Pi_total','signed_shear','Sigma_F','Sigma_half','p_m_J_m3','p_r_J_m3','p_total_J_m3','pi_m_contract_pi_r_J2_m6','cancellation_fraction')}})
        ax=axes[0,col]
        for k,color,label in [('P_m','#b2182b',r'$P_m$ (matter)'),('P_r','#2166ac',r'$P_r$ ($\gamma+\nu$)'),('P_total','#222222',r'$P_m+P_r$')]:ax.plot(z,r[k],color=color,label=label,lw=1.8)
        ax.set_title(f'Initial (ΣF, Pm, Pr) = (0, {m:+.4f}, {r0:+.4f})');ax.set_ylabel(r'Signed $P_X=\sqrt{6}\,\mathcal{K}p_X/H^2$ [dimensionless]'+ '\n'+r'$\mathcal{K}=8\pi G/c^2$');ax.legend(fontsize=9)
        ax=axes[1,col];ax.plot(z,r['signed_shear'],color='#762a83',label=r'signed $\sqrt{6}s/H$');ax.plot(z,r['Sigma_F'],'--',color='#1b7837',label=r'$\Sigma_F=\sqrt{6}|s|/H$');ax.plot(z,r['Sigma_half'],':',color='#e08214',label=r'$\Sigma_{half}=\Sigma_F/\sqrt{2}$');ax.set_ylabel('Shear [dimensionless]');ax.legend(fontsize=9)
        for ax in axes[:,col]:ax.set_xlim(20,2);ax.set_xticks([20,15,10,5,2]);ax.axhline(0,color='.6',lw=.7);ax.axvline(4,color='.6',lw=.7,ls=':');ax.set_xlabel(r'Mean redshift $\bar z$');ax.ticklabel_format(axis='y',style='sci',scilimits=(0,0));ax.grid(alpha=.15)
    for ax in axes[1,:]:ax.set_ylim(-1.05*history_shear_bound,1.05*history_shear_bound)
    fig.suptitle('Initially opposing matter and radiation stresses, evolved from z=20 to z=2\n153 stored epochs; dotted vertical line marks the saved z=4 join',fontsize=14);save(fig,'opposite_component_histories');csvwrite('opposite_component_histories.csv',history)
    # Original radiation-only controls + actual scoped endpoint refinements/brightness.
    fig,axes=plt.subplots(2,2,figsize=(12.5,8.7),layout='constrained');base_rows=[]
    for col,z in enumerate((4,2)):
        ax=axes[0,col]
        for sigma in u.original.SIGMAS:
            line=[]
            for c in u.original.cases():
                if c['config']['guard'] or c['config']['Sigma_F_i']!=sigma:continue
                r=read(c,z)
                if r is None:continue
                line.append((c['config']['Pi_F_signed_i'],r['signed_shear'][-1]));base_rows.append({'id':c['id'],'Sigma_F_i':sigma,'P_r_i':c['config']['Pi_F_signed_i'],'P_m_i':0.,'z_endpoint':z,**{k:float(r[k][-1]) for k in ('P_m','P_r','P_total','signed_shear','Sigma_F','b','H')}})
            line.sort()
            if line:xx,yy=zip(*line);ax.plot(xx,yy,'o-',ms=3,lw=.7,label=f'{sigma:g}')
        ax.set_title(f'Original 91 radiation controls at z={z}');ax.set_xlabel(r'Initial signed $P_r$ ($P_{m,i}=0$)');ax.set_ylabel(r'Final signed $\sqrt{6}s/H$');ax.axhline(0,color='.6',lw=.7);ax.axvline(0,color='.6',lw=.7);ax.ticklabel_format(style='sci',scilimits=(0,0));ax.legend(title=r'$\Sigma_{F,i}$',ncol=2,fontsize=8)
    guard_rows=[]
    for phase in ('b1','b2'):
        p=u.ROOT/('components' if phase=='b1' else 'z2_extension')/'results/CHECK.json'
        if p.exists():
            for j,g in enumerate(json.loads(p.read_text())['refinement_controls']):
                guard_rows.append({'phase':phase,'control':j+1,**g.get('absolute_endpoint_differences',{})})
    ax=axes[1,0]
    for j,k in enumerate(('Sigma_F','P_m','P_r','b','H_relative')):
        vals=[r.get(k,np.nan) for r in guard_rows];ax.scatter(np.arange(len(vals))+(j-2)*.1,vals,s=28,label=k)
    ax.axhline(2e-6,color='black',ls='--',lw=1,label='2×10⁻⁶ gate');ax.set_yscale('symlog',linthresh=1e-12);ax.set_xticks(range(len(guard_rows)),[r['phase']+' #'+str(r['control']) for r in guard_rows],rotation=35);ax.set_title('Selected refined endpoint controls');ax.set_ylabel('Absolute difference; H uses relative difference');ax.legend(fontsize=8,ncol=3)
    ax=axes[1,1];brightness=[]
    for c in [c for c in u.original.cases() if not c['config']['guard']]+[c for c in comp if 'reuse' not in c]:
        r=read(c,2)
        if r is not None:brightness.append({'id':c['id'],'gamma_min':float(r['minimum_brightness_gamma'].min()),'nu_min':float(r['minimum_brightness_nu'].min()),'packet_min':float(r['massive_min_cell_population'].min())})
    for k,color in [('gamma_min','#2166ac'),('nu_min','#b2182b')]:ax.scatter(range(len(brightness)),[r[k] for r in brightness],s=8,label=k,color=color,alpha=.6)
    ax.axhline(-1e-10,color='black',ls='--',label='−10⁻¹⁰ gate');ax.set_title('64-node brightness samples, 231 unique nominals');ax.set_xlabel('Unique nominal case index (categorical)');ax.set_ylabel('Minimum sampled brightness, all153 epochs');ax.legend(fontsize=8)
    fig.suptitle('Radiation baseline and scoped numerical checks\nEndpoint controls and sampled brightness; Hamiltonian residual is construction consistency',fontsize=14)
    save(fig,'radiation_baseline_and_controls');csvwrite('radiation_baseline91_z4_z2.csv',base_rows);csvwrite('refinement_controls.csv',guard_rows);csvwrite('sampled_brightness231.csv',brightness)
    u.atomic_json(OUT/'PLOT_MANIFEST.json',{'source_sha256':u.sha(__file__),'files':{p.name:u.sha(p) for p in OUT.iterdir() if p.is_file() and p.name!='PLOT_MANIFEST.json'},'actual_sample_rows':len(rows),'history_rows':len(history),'baseline_rows':len(base_rows),'no_solver_calls':True,'scope':'fixed collisionless LRS finite-grid preliminary; independent result review pending'})
    u.atomic_json(u.ROOT/'z2_extension/results/controllers'/(str(time.time_ns())+'.json'),{'profile':'sandbox','controller_elapsed_s':time.monotonic()-ENTRY_STARTED,'operation':'plot','argv':sys.argv,'scientific_solver_calls':0})
    print(json.dumps({'directory':str(OUT),'component_endpoint_rows':len(rows),'history_rows':len(history),'baseline_rows':len(base_rows)}))
if __name__=='__main__':main()
