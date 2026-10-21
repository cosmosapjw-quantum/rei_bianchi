#!/usr/bin/env python3
"""D9 saved-sample additive shear budget. No solver/model/moment imports or calls."""
import os
for _key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):
    os.environ[_key]='1'
import argparse, csv, hashlib, io, json, math, pathlib, resource, sys, time, traceback
import numpy as np
import scipy
from scipy.integrate import cumulative_simpson, trapezoid

CONTRACT_SHA='7fb39d92a3a1375c7ca769ac271af6771d68b6cf6f2115978531e897bd6604b9'
LOCKS={'ledger':'10e89609325192e7962e880cbcb0f37c052819963e882e2eba48ff32264ca5e1',
       'ledger_index':'8bc1551f21bdbda1b2a12db64f7ea2f64c56f5f2db24cc9dfec0204fbca936bc',
       'd8':'9c7a3c74cff48bb76d00c6af9795783aae2a7bb4a1e455d07cc1dd89b51e71e8',
       'component_manifest':'c8d57bf81833ee405b8be854166fb58022a960b7fe9e36aa11fa3c6a5ec00e95',
       'extension_manifest':'4f7e599ad9f082be59cbe2203a8b55b7bd9cb21fec9fde55a41afe53b9444853'}
TOL=2e-5
SIGMAS=(0.,.0003,.001,.003,.01,.03,.1)
MATTER=(-.0003,-.0001,0.,.0001,.0003)
RADIATION=(-.001,-.0003,0.,.0003,.001)


def sha(b): return hashlib.sha256(b).hexdigest()
def write_json(path,obj): path.write_text(json.dumps(obj,sort_keys=True,indent=2,allow_nan=False)+'\n')
def read_json(path): return json.loads(pathlib.Path(path).read_bytes())
def require(condition,message):
    if not condition: raise ValueError(message)
def locked(path,key):
    b=pathlib.Path(path).read_bytes(); h=sha(b)
    require(h==LOCKS[key],f'IMMUTABLE_SOURCE_MISMATCH:{key}:{h}')
    return json.loads(b),{'path':str(pathlib.Path(path).resolve()),'sha256':h,'bytes':len(b)}
def csvwrite(path,rows):
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def axes(c): return (c['Sigma_F_i'],c.get('P_m_i',0.),c.get('P_r_i',c['Pi_F_signed_i']))
def near(actual,expected,label,atol=5e-12):
    require(bool(np.allclose(actual,expected,rtol=0,atol=atol)),f'VALUE_CONTRACT_MISMATCH:{label}')


def budget(x,a,h,s,pm,pg,pn):
    """Broadcast cases along leading axes; integrate stored epoch axis once."""
    x=np.asarray(x,dtype=float)
    require(x.ndim==1 and len(x)>=3 and np.isfinite(x).all() and np.all(np.diff(x)>0),'NONMONOTONE_OR_INVALID_GRID')
    a,h,s,pm,pg,pn=[np.asarray(v,dtype=float) for v in (a,h,s,pm,pg,pn)]
    require(all(v.shape==a.shape and v.shape[-1]==len(x) for v in (h,s,pm,pg,pn)),'ARRAY_SHAPE_MISMATCH')
    require(all(np.isfinite(v).all() for v in (a,h,s,pm,pg,pn)),'NONFINITE_SAVED_DATA')
    require(np.all(a>0) and np.all(h>0),'NONPOSITIVE_A_OR_H')
    near(np.log(a/a[...,0,None]),x-x[0],'x=ln(a/a_i)',atol=5e-13)
    m=(a/a[...,0,None])**3*h/h[...,0,None]
    sf=np.sqrt(6.)*s/h
    weighted=m[...,None,:]*np.stack((pm,pg,pn),axis=-2)
    integrals=cumulative_simpson(weighted,x=x,axis=-1,initial=0.)
    im,ig,inu=(integrals[...,i,:] for i in range(3));ir=ig+inu
    q=m*sf;qr=sf[...,0,None]+im+ir;residual=q-qr
    scale=np.maximum.reduce((abs(sf[...,0]),np.max(abs(im)+abs(ir),axis=-1),np.full_like(sf[...,0],1e-12)))
    trap=trapezoid(weighted,x=x,axis=-1)
    return {'M':m,'S_F':sf,'Q':q,'Q_reconstructed':qr,'I_m':im,'I_gamma':ig,'I_nu':inu,'I_r':ir,
            'R':residual,'scale':scale,'scaled_max_residual':np.max(abs(residual),axis=-1)/scale,
            'S_F_reconstructed':qr/m,'endpoint_simpson_minus_trapezoid':integrals[...,-1]-trap}


def source_inputs(args):
    package=pathlib.Path(args.package).resolve()
    contract=pathlib.Path(args.contract).read_bytes();require(sha(contract)==CONTRACT_SHA,'FROZEN_CONTRACT_MISMATCH')
    comp,ci=locked(package/'components/results/MANIFEST.json','component_manifest')
    ext,ei=locked(package/'z2_extension/results/MANIFEST.json','extension_manifest')
    ledger,li=locked(args.ledger,'ledger');index,ii=locked(args.ledger_index,'ledger_index');d8,di=locked(args.d8,'d8')
    nominal=sorted((c for c in comp['cases'] if not c['config']['guard']),key=lambda c:axes(c['config']))
    require(len(nominal)==175,'NOMINAL_CASE_COUNT')
    require({axes(c['config']) for c in nominal}=={(s,m,r) for s in SIGMAS for m in MATTER for r in RADIATION},'PHYSICAL_AXIS_COVERAGE')
    require(sum('reuse' in c for c in nominal)==35,'REFERENCE_ALIAS_COUNT')
    ex={c['id']:c for c in ext['cases']};lr={r['case_id']:r for r in ledger['rows']};bindings=[];stored=[];common_x=None
    for case in nominal:
        cid=case.get('reuse',{}).get('original_case_id',case['id'])
        require(cid in ex and 'Btail:'+cid in lr,'MISSING_CASE_MANIFEST_OR_LEDGER:'+cid)
        entry=ex[cid];record=lr['Btail:'+cid]
        require(axes(entry['config'])==axes(case['config']),'ALIAS_AXIS_MISMATCH:'+cid)
        if 'reuse' in case:
            alias=lr.get('Bcomponent_alias:'+case['id'])
            require(alias is not None and alias['parent_id']=='Bprefix:'+cid and alias.get('IVP_count_contribution')==0,'ALIAS_LEDGER_MISMATCH:'+cid)
        folder=package/'z2_extension/results/cases'/cid
        rb=(folder/'RESULT.json').read_bytes();result=json.loads(rb)
        ib=(folder/'INPUT.json').read_bytes();inp=json.loads(ib)
        require(result['id']==inp['id']==cid and result['config']==inp['config']==entry['config']==record['config'],'CASE_CONFIG_IDENTITY:'+cid)
        require(result.get('status')=='COMPLETED' and result.get('exit')==0,'VALIDATED_RAW_RESULT_MISSING:'+cid)
        require(sha(rb)==record['receipt_sha256'],'RESULT_LEDGER_HASH:'+cid)
        for key in ('prefix_relative','prefix_raw_sha256','prefix_input_sha256','prefix_result_sha256'):
            require(inp.get(key)==entry.get(key),'PREFIX_MANIFEST_IDENTITY:'+cid+':'+key)
        prefix=pathlib.PurePosixPath(entry['prefix_relative'])
        require(not prefix.is_absolute() and '..' not in prefix.parts,'INVALID_PREFIX_PATH:'+cid)
        for name,key in (('INPUT.json','prefix_input_sha256'),('RESULT.json','prefix_result_sha256'),('raw.npz','prefix_raw_sha256')):
            require(sha((package/prefix/name).read_bytes())==entry[key],'PREFIX_BYTE_IDENTITY:'+cid+':'+name)
        data=(folder/'raw.npz').read_bytes();raw_hash=sha(data)
        require(raw_hash==result.get('raw_sha256')==record.get('combined_raw_sha256'),'RAW_RESULT_LEDGER_HASH:'+cid)
        require(len(data)==result.get('raw_bytes'),'RAW_BYTE_COUNT:'+cid)
        failure=result.get('historical_failure_receipt_sha256');failure_path=None
        if failure:
            candidates=[p for p in folder.glob('RESULT.*.json') if sha(p.read_bytes())==failure]
            require(len(candidates)==1,'HISTORICAL_FAILURE_RECEIPT_MISSING:'+cid)
            failure_path=str(candidates[0].relative_to(package))
        with np.load(io.BytesIO(data),allow_pickle=False) as nz:
            required=('x','a','H','s','Pi_F_signed_matter','Pi_F_signed_gamma','Pi_F_signed_nu','Pi_F_signed')
            require(set(required)<=set(nz.files),'MISSING_STORED_COMPONENT:'+cid)
            raw={k:np.array(nz[k]) for k in required}
            require(all(v.shape==(153,) and np.isfinite(v).all() for v in raw.values()),'RAW_SHAPE_FINITE:'+cid)
            if common_x is None:common_x=raw['x'].copy()
            require(np.array_equal(common_x,raw['x']),'COMMON_GRID_IDENTITY:'+cid)
            require(np.all(raw['a']>0) and np.all(raw['H']>0),'POSITIVE_GEOMETRY:'+cid)
            sf=np.sqrt(6)*raw['s']/raw['H'];pr=raw['Pi_F_signed_gamma']+raw['Pi_F_signed_nu'];pm=raw['Pi_F_signed_matter']
            near([sf[0],pm[0],pr[0]],axes(case['config']),'INITIAL_AXES:'+cid)
            near([raw['a'][0],raw['a'][-1]],[1/21,1/3],'REDSHIFT_ENDPOINTS:'+cid,atol=2e-15)
            require(np.all(np.diff(raw['x'])>0),'NONMONOTONE_SAVED_GRID:'+cid)
            near(raw['Pi_F_signed'],pm+pr,'NORMALIZED_SUM:'+cid,atol=32*np.finfo(float).eps*max(1.,float(np.max(abs(pm)+abs(pr)))))
            for name,expected in [('P_m',pm),('P_r',pr),('P_total',pm+pr),('Sigma_F',abs(sf)),('signed_shear',sf),('S_F',sf)]:
                if name in nz.files:near(nz[name],expected,'OPTIONAL_STORED_ALIAS:'+name+':'+cid,atol=32*np.finfo(float).eps*max(1.,float(np.max(abs(expected)))))
        stored.append(raw)
        bindings.append({'case_id':cid,'component_requested_id':case['id'],'Sigma_F_i':axes(case['config'])[0],'P_m_i':axes(case['config'])[1],'P_r_i':axes(case['config'])[2],
                         'reference_alias':'reuse' in case,'reference_relationship':case.get('reuse',{}).get('relationship','ORIGINAL_COMPONENT_CASE'),
                         'raw_path':str((folder/'raw.npz').relative_to(package)),'raw_sha256':raw_hash,'raw_bytes':len(data),'result_sha256':sha(rb),'input_sha256':sha(ib),
                         'source_configuration':entry['config'],'ledger_case_id':'Btail:'+cid,'validated_raw_status':result['status'],'historical_execution_status':result.get('historical_execution_status',result['status']),
                         'historical_failure_receipt_sha256':failure,'historical_failure_receipt_path':failure_path,
                         'missing_solver_metadata_preserved':result.get('unavailable_metadata_reason')})
    require(len({b['case_id'] for b in bindings})==175,'DUPLICATE_TRAJECTORY')
    arrays={k:np.stack([r[k] for r in stored]) for k in stored[0] if k!='x'}
    manifest={'schema':'rei.d9.input_manifest.v1','contract_sha256':sha(contract),'sources':{'component_manifest':ci,'extension_manifest':ei,'ledger':li,'ledger_index':ii,'accepted_d8':di},
              'raw_source_archive':{'sha256':d8['archive_sha256'],'identity_source':'immutable accepted D8 result; data were previously restored by controller'},
              'selected_nominal_cases':175,'reference_aliases':35,'new_ivps':0,'cases':bindings}
    return common_x,arrays,bindings,manifest,d8


def portable_save(out,x,arrays,bindings,manifest,d8):
    """Lossless derived input view from the already loaded raw arrays."""
    out.mkdir()
    data=out/'D9_COMPACT_INPUT.npz'
    np.savez_compressed(data,x=x,case_ids=np.array([r['case_id'] for r in bindings]),
                        physical_axes=np.array([[r[k] for k in ('Sigma_F_i','P_m_i','P_r_i')] for r in bindings]),**arrays)
    expected={'x':x,'case_ids':np.array([r['case_id'] for r in bindings]),
              'physical_axes':np.array([[r[k] for k in ('Sigma_F_i','P_m_i','P_r_i')] for r in bindings]),**arrays}
    with np.load(data,allow_pickle=False) as z:
        require(set(z.files)==set(expected),'COMPACT_ROUNDTRIP_KEYS')
        for k,v in expected.items():require(np.array_equal(z[k],v),'COMPACT_ROUNDTRIP_ARRAY:'+k)
    meta={'schema':'rei.d9.compact_saved_input.v1','derived_view_not_replacement_raw':True,'contract_sha256':CONTRACT_SHA,
          'compact_npz_sha256':sha(data.read_bytes()),'compact_npz_bytes':data.stat().st_size,
          'roundtrip':'EXACT_ARRAY_IDENTITY_PASS','source_input_manifest':manifest,'accepted_D8_result':d8,
          'source_D8_canonical_json_sha256':sha(json.dumps(d8,sort_keys=True,separators=(',',':')).encode()),
          'required_sources_preserved':'Full original raw/receipts remain in the archive cited by source_input_manifest. No historical receipt is relabeled.'}
    write_json(out/'D9_COMPACT_IDENTITY.json',meta)
    identity_sha=sha((out/'D9_COMPACT_IDENTITY.json').read_bytes())
    write_json(out/'COMPACT_ROUNDTRIP.json',{'status':'EXACT_ARRAY_IDENTITY_PASS','arrays':sorted(expected),'cases':175,'epochs':153,
                                         'compact_npz_sha256':meta['compact_npz_sha256'],'compact_identity_sha256':identity_sha,'new_ivps':0})
    return identity_sha


def portable_inputs(args):
    identity=pathlib.Path(args.portable_manifest);raw=identity.read_bytes()
    require(bool(args.portable_manifest_sha) and sha(raw)==args.portable_manifest_sha,'PORTABLE_EXTERNAL_IDENTITY_MISMATCH')
    meta=json.loads(raw);require(meta['contract_sha256']==CONTRACT_SHA,'PORTABLE_CONTRACT_IDENTITY')
    require(sha(pathlib.Path(args.contract).read_bytes())==CONTRACT_SHA,'FROZEN_CONTRACT_MISMATCH')
    manifest=meta['source_input_manifest'];bindings=manifest['cases'];d8=meta['accepted_D8_result']
    require(manifest['contract_sha256']==CONTRACT_SHA and len(bindings)==175,'PORTABLE_POPULATION_CONTRACT')
    require({(r['Sigma_F_i'],r['P_m_i'],r['P_r_i']) for r in bindings}=={(s,m,r) for s in SIGMAS for m in MATTER for r in RADIATION},'PORTABLE_AXIS_COVERAGE')
    require(len({r['case_id'] for r in bindings})==175 and sum(r['reference_alias'] for r in bindings)==35,'PORTABLE_CASE_ALIAS_IDENTITY')
    for key,source_key in [('component_manifest','component_manifest'),('extension_manifest','extension_manifest'),('ledger','ledger'),('ledger_index','ledger_index'),('d8','accepted_d8')]:
        require(manifest['sources'][source_key]['sha256']==LOCKS[key],'PORTABLE_SOURCE_IDENTITY:'+key)
    require(sha(json.dumps(d8,sort_keys=True,separators=(',',':')).encode())==meta['source_D8_canonical_json_sha256'],'PORTABLE_D8_CONTENT_IDENTITY')
    data=pathlib.Path(args.portable_input).read_bytes();require(sha(data)==meta['compact_npz_sha256'] and len(data)==meta['compact_npz_bytes'],'PORTABLE_NPZ_BYTE_IDENTITY')
    with np.load(io.BytesIO(data),allow_pickle=False) as nz:
        require(np.array_equal(nz['case_ids'],[r['case_id'] for r in bindings]),'PORTABLE_CASE_ORDER')
        near(nz['physical_axes'],[[r[k] for k in ('Sigma_F_i','P_m_i','P_r_i')] for r in bindings],'PORTABLE_AXES',atol=0)
        x=np.array(nz['x']);arrays={k:np.array(nz[k]) for k in nz.files if k not in ('x','case_ids','physical_axes')}
    require(x.shape==(153,) and np.all(np.diff(x)>0),'PORTABLE_GRID')
    require(all(v.shape==(175,153) and np.isfinite(v).all() for v in arrays.values()),'PORTABLE_ARRAYS')
    require(np.all(arrays['a']>0) and np.all(arrays['H']>0),'PORTABLE_POSITIVE_GEOMETRY')
    sf=np.sqrt(6)*arrays['s']/arrays['H'];pm=arrays['Pi_F_signed_matter'];pr=arrays['Pi_F_signed_gamma']+arrays['Pi_F_signed_nu']
    near(np.stack((sf[:,0],pm[:,0],pr[:,0]),axis=-1),[[r[k] for k in ('Sigma_F_i','P_m_i','P_r_i')] for r in bindings],'PORTABLE_INITIAL_AXES')
    near(arrays['Pi_F_signed'],pm+pr,'PORTABLE_SUM',atol=32*np.finfo(float).eps*max(1.,float(np.max(abs(pm)+abs(pr)))))
    near(arrays['a'][:,[0,-1]],np.tile([1/21,1/3],(175,1)),'PORTABLE_REDSHIFT_ENDPOINTS',atol=2e-15)
    require(np.all(np.diff(arrays['a'],axis=-1)>0),'PORTABLE_NONMONOTONE_A')
    manifest={**manifest,'reader_mode':'compact_derived_input','compact_manifest_sha256':sha(raw),'compact_npz_sha256':sha(data)}
    return x,arrays,bindings,manifest,d8


def d8_checks(bindings,arrays,b,d8):
    byid={r['case_id']:i for i,r in enumerate(bindings)};checks=[]
    for prior in d8['cases']:
        cid=prior['case_id'];require(cid in byid,'D8_FOCUS_CASE_NOT_SELECTED:'+cid);i=byid[cid]
        require(bindings[i]['raw_sha256']==prior['raw_sha256'],'D8_RAW_IDENTITY:'+cid)
        for bracket in prior['strict_adjacent_sign_change_brackets']:
            ix=np.asarray(bracket['index_pair'],dtype=int)
            require(ix.shape==(2,) and np.all((ix>=0)&(ix<153)),'D8_ACCEPTED_INDICES_INVALID')
            near(1/arrays['a'][i,ix]-1,bracket['redshift_descending'],'D8_Z_BINDING:'+cid,atol=2e-12)
            near(b['S_F'][i,ix],bracket['S_F_signed'],'D8_SAVED_S_BINDING:'+cid,atol=2e-15)
            actual=b['Q'][i,ix];recon=b['Q_reconstructed'][i,ix];r=b['R'][i,ix]
            same=np.sign(actual)==np.sign(recon);small=abs(r)<.1*abs(actual)
            checks.append({'case_id':cid,'accepted_D8_label':prior['case_label'],'index_pair':ix.tolist(),'redshift_descending':bracket['redshift_descending'],
                           'Q_saved':actual.tolist(),'Q_reconstructed':recon.tolist(),'R':r.tolist(),'R_over_abs_Q':(abs(r)/abs(actual)).tolist(),
                           'saved_signs_preserved':bool(same.all()),'residual_below_tenth_saved_Q':bool(small.all()),'budget_resolved':bool(same.all() and small.all())})
    require(len(checks)==4,'D8_ACCEPTED_BRACKET_COUNT')
    return checks


def figures(out,x,arrays,b,bindings,focus,checks,endpoint_only=False):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.size':10,'axes.titlesize':11,'axes.labelsize':10,'xtick.labelsize':9,'ytick.labelsize':9,'legend.fontsize':9,'savefig.dpi':170,'pdf.fonttype':42})
    palette=['#0072B2','#D55E00','#009E73','#CC79A7','#6F4E7C'];z=1/arrays['a'][0]-1
    labels=[f"$P_{{m,i}}={bindings[i]['P_m_i']:+.4f}$" for i in focus]
    def save(fig,name):
        fig.savefig(out/(name+'.png'),bbox_inches='tight');fig.savefig(out/(name+'.pdf'),bbox_inches='tight');plt.close(fig)
    if not endpoint_only:
        fig,axes_=plt.subplots(3,1,figsize=(7.2,8.2),sharex=True,layout='constrained')
        for ax,key,title in zip(axes_,('Q','I_m','I_r'),('Expansion-damping-removed signed shear','Accumulated matter source','Accumulated radiation source (photons + neutrinos)')):
            for color,i,label in zip(palette,focus,labels):ax.plot(z,b[key][i],color=color,label=label,lw=1.5)
            ax.axhline(0,color='.5',lw=.7);ax.axvline(4,color='.5',ls=':',lw=.8);ax.set_ylabel(key+' [dimensionless]');ax.set_title(title);ax.ticklabel_format(axis='y',style='sci',scilimits=(-2,2))
        axes_[0].set_xlim(float(z[0]),float(z[-1]));axes_[0].legend(ncol=3,loc='best');axes_[-1].set_xlabel('Redshift z (decreasing as time advances)')
        fig.suptitle('Five focus histories: $\\Sigma_{F,i}=0.003$, $P_{r,i}=-0.001$\n153 saved samples; connected lines are visual guides; dotted line: z=4',fontsize=12)
        save(fig,'focus_integrating_factor_budget')
        fig,axes_=plt.subplots(2,1,figsize=(7.2,6.6),sharex=True,layout='constrained')
        for color,i,label in zip(palette,focus,labels):
            axes_[0].plot(z,b['S_F'][i],color=color,lw=1.7,label=label);axes_[0].plot(z,b['S_F_reconstructed'][i],color=color,ls='--',lw=.9)
            axes_[1].plot(z,b['R'][i]/b['scale'][i],color=color,lw=1.5)
        for check in checks:
            i=next(i for i in focus if bindings[i]['case_id']==check['case_id']);j=focus.index(i);ix=check['index_pair']
            axes_[0].scatter(z[ix],b['S_F'][i,ix],s=22,marker='o',facecolors='none',edgecolors=palette[j],zorder=5)
        for ax in axes_:ax.axhline(0,color='.5',lw=.7);ax.axvline(4,color='.5',ls=':',lw=.8)
        axes_[0].set_xlim(float(z[0]),float(z[-1]));axes_[0].legend(ncol=3);axes_[0].set_ylabel('Signed $S_F$ [dimensionless]');axes_[0].set_title('Solid: saved shear; dashed: reconstructed; circles: accepted D8 bracket samples')
        axes_[1].set_ylabel('Signed R / case scale');axes_[1].set_xlabel('Redshift z (decreasing as time advances)');axes_[1].ticklabel_format(axis='y',style='sci',scilimits=(-2,2))
        fig.suptitle('Saved-sample budget reconstruction\nNo continuous zero or dense output is inferred; lines are visual guides',fontsize=12)
        save(fig,'focus_shear_reconstruction')
    fig,axes_=plt.subplots(2,1,figsize=(7.2,6.8),layout='constrained')
    for sigma in SIGMAS:
        inds=[i for i,r in enumerate(bindings) if r['Sigma_F_i']==sigma]
        axes_[0].scatter(inds,b['scaled_max_residual'][inds],s=16,label=f'$\\Sigma_{{F,i}}={sigma:g}$')
    axes_[0].axhline(TOL,color='black',ls='--',lw=1,label='Fixed diagnostic threshold: 2e-5');axes_[0].set_yscale('symlog',linthresh=1e-14);axes_[0].set_xlabel('Case index, sorted by initial (Sigma_F, P_m, P_r)');axes_[0].set_ylabel('max |R| / case scale');axes_[0].legend(ncol=3,loc='lower center',bbox_to_anchor=(.5,1.12));axes_[0].set_title('All 175 nominal cases: sampled-data consistency diagnostic')
    ix=np.arange(5);width=.23
    for offset,key,color in [(-width,'I_m','#0072B2'),(0,'I_r','#D55E00'),(width,'Q','#009E73')]:axes_[1].bar(ix+offset,b[key][focus,-1],width,color=color,label=key+' at z=2')
    axes_[1].axhline(.003,color='#6F4E7C',ls=':',label='Initial signed shear: 0.003');axes_[1].axhline(0,color='.5',lw=.7);axes_[1].set_xticks(ix,[f'{bindings[i]["P_m_i"]:+.4f}' for i in focus]);axes_[1].set_xlabel('Initial matter stress P_m,i (focus set)');axes_[1].set_ylabel('Dimensionless endpoint budget');axes_[1].legend(ncol=2);axes_[1].set_title('Additive accounting on each coupled trajectory: Q = S_F,i + I_m + I_r')
    fig.suptitle('Component-budget diagnostic and endpoint accounting\nQuadrature sensitivity is reported separately; no convergence certificate',fontsize=12)
    save(fig,'all175_consistency_and_focus_endpoints')


def main():
    start=time.monotonic();cpu_start=time.process_time()
    ap=argparse.ArgumentParser(description=__doc__);mode=ap.add_mutually_exclusive_group(required=True);mode.add_argument('--package');mode.add_argument('--portable-input');ap.add_argument('--portable-manifest');ap.add_argument('--portable-manifest-sha');ap.add_argument('--ledger');ap.add_argument('--ledger-index');ap.add_argument('--d8');ap.add_argument('--contract',default=str(pathlib.Path(__file__).with_name('EXECUTION_CONTRACT.md')));ap.add_argument('--out',required=True);args=ap.parse_args()
    out=pathlib.Path(args.out);out.mkdir(parents=True,exist_ok=False)
    receipt={'schema':'rei.d9.run_receipt.v1','argv':sys.argv,'status':'RUNNING','ode_calls':0,'ivps':0,'moment_recomputations':0,'main_processes':1,'threads':1,'NCP_execution':'NOT_RUN','contract_sha256':CONTRACT_SHA}
    write_json(out/'RUN_RECEIPT.json',receipt)
    try:
        x,arrays,bindings,manifest,d8=portable_inputs(args) if args.portable_input else source_inputs(args);write_json(out/'INPUT_MANIFEST.json',manifest)
        if not args.portable_input:
            receipt['compact_identity_sha256']=portable_save(out/'portable_input',x,arrays,bindings,manifest,d8)
        b=budget(x,arrays['a'],arrays['H'],arrays['s'],arrays['Pi_F_signed_matter'],arrays['Pi_F_signed_gamma'],arrays['Pi_F_signed_nu'])
        checks=d8_checks(bindings,arrays,b,d8)
        focus=[i for i,r in enumerate(bindings) if r['Sigma_F_i']==.003 and r['P_r_i']==-.001];require(len(focus)==5,'FOCUS_COUNT')
        rows=[]
        for i,bind in enumerate(bindings):
            row={k:bind[k] for k in ('case_id','component_requested_id','reference_alias','Sigma_F_i','P_m_i','P_r_i')}
            row.update({key:float(b[key][i,-1]) for key in ('M','S_F','S_F_reconstructed','Q','Q_reconstructed','I_m','I_gamma','I_nu','I_r','R')})
            row.update(scale=float(b['scale'][i]),max_abs_residual=float(np.max(abs(b['R'][i]))),scaled_max_residual=float(b['scaled_max_residual'][i]),sampled_consistency_pass=bool(b['scaled_max_residual'][i]<=TOL),
                       Simpson_minus_trapezoid_m=float(b['endpoint_simpson_minus_trapezoid'][i,0]),Simpson_minus_trapezoid_gamma=float(b['endpoint_simpson_minus_trapezoid'][i,1]),Simpson_minus_trapezoid_nu=float(b['endpoint_simpson_minus_trapezoid'][i,2]))
            row['Simpson_minus_trapezoid_r']=row['Simpson_minus_trapezoid_gamma']+row['Simpson_minus_trapezoid_nu'];rows.append(row)
        csvwrite(out/'endpoints_175.csv',rows);write_json(out/'endpoints_175.json',rows)
        histories=[]
        for i in focus:
            history=[]
            for j in range(len(x)):
                row={'case_id':bindings[i]['case_id'],'Sigma_F_i':.003,'P_m_i':bindings[i]['P_m_i'],'P_r_i':-.001,'sample_index':j,'x':float(x[j]),'z':float(1/arrays['a'][i,j]-1),'P_m':float(arrays['Pi_F_signed_matter'][i,j]),'P_gamma':float(arrays['Pi_F_signed_gamma'][i,j]),'P_nu':float(arrays['Pi_F_signed_nu'][i,j])}
                row.update({k:float(b[k][i,j]) for k in ('M','S_F','S_F_reconstructed','Q','Q_reconstructed','I_m','I_gamma','I_nu','I_r','R')});row['scaled_R']=row['R']/b['scale'][i];history.append(row)
            name='focus_history_Pm_'+format(bindings[i]['P_m_i'],'+.4f').replace('+','plus').replace('-','minus').replace('.','p')+'.csv';csvwrite(out/name,history);histories+=history
        csvwrite(out/'focus_histories_5.csv',histories)
        np.savez_compressed(out/'sampled_diagnostics_175.npz',x=x,case_ids=np.array([r['case_id'] for r in bindings]),**b)
        write_json(out/'D8_ACCEPTED_BRACKET_BUDGET_CHECKS.json',{'source_sha256':LOCKS['d8'],'source_status':'immutable accepted D8 brackets reused; not recomputed','continuous_roots_inferred':False,'checks':checks})
        passes=bool(np.all(b['scaled_max_residual']<=TOL));bracket_pass=all(c['budget_resolved'] for c in checks)
        result={'schema':'rei.d9.result.v1','status':'PASS_SAMPLED_COMPONENT_BUDGET' if passes and bracket_pass else 'HOLD_SAMPLED_BUDGET_DIAGNOSTIC',
                'cases':175,'stored_epochs':153,'aliases':35,'focus_cases':5,'accepted_D8_brackets':4,'max_scaled_residual':float(np.max(b['scaled_max_residual'])),'fixed_threshold':TOL,'threshold_pass':passes,'bracket_budget_resolved':bracket_pass,
                'failed_case_ids':[bindings[i]['case_id'] for i in np.flatnonzero(b['scaled_max_residual']>TOL)],'max_endpoint_Simpson_trapezoid_difference_m':float(np.max(abs(b['endpoint_simpson_minus_trapezoid'][:,0]))),'max_endpoint_Simpson_trapezoid_difference_r':float(np.max(abs(b['endpoint_simpson_minus_trapezoid'][:,1:].sum(axis=1)))),
                'ode_calls':0,'ivps':0,'moment_recomputations':0,'NCP_execution':'NOT_RUN','focus_endpoints':[rows[i] for i in focus],
                'limitations':['Saved-sample quadrature diagnostic; fixed threshold is not a rigorous global error bound.','Simpson/trapezoid difference is sensitivity, not a convergence certificate.','Additive accounting on each solved coupled trajectory; altered-initial-data trajectories do not superpose.','D8 stored adjacent-sample brackets reused; no continuous crossing time or dense output inferred.','Historical failed-worker receipts remain distinct from validated saved-raw receipts; unavailable solver metadata remains unavailable.','Production admission, AGE convergence and Grackle bounds are outside this unit.']}
        write_json(out/'RESULT.json',result)
        if not passes or not bracket_pass:
            receipt['status']=result['status'];return 2
        require(time.process_time()-cpu_start<100,'CPU_BUDGET_BEFORE_PLOTS')
        figures(out,x,arrays,b,bindings,focus,checks)
        write_json(out/'PLOT_DATA_MAP.json',{'focus_integrating_factor_budget':'focus_histories_5.csv: Q,I_m,I_r vs z','focus_shear_reconstruction':'focus_histories_5.csv: S_F,S_F_reconstructed,scaled_R vs z; D8_ACCEPTED_BRACKET_BUDGET_CHECKS.json','all175_consistency_and_focus_endpoints':'endpoints_175.csv: scaled_max_residual; focus endpoint Q,I_m,I_r','connected_lines':'visual guides through stored samples only','plot_count':3})
        receipt['status']='COMPLETED_DATA_ONLY_AWAITING_ASTRA_REVIEW'
        return 0
    except Exception as exc:
        receipt.update(status='EXECUTION_FAILED',error=type(exc).__name__+': '+str(exc));(out/'ERROR.txt').write_text(traceback.format_exc());raise
    finally:
        receipt.update(wall_seconds=time.monotonic()-start,process_cpu_seconds=time.process_time()-cpu_start,versions={'python':sys.version,'numpy':np.__version__,'scipy':scipy.__version__},source_sha256=sha(pathlib.Path(__file__).read_bytes()),max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
        write_json(out/'RUN_RECEIPT.json',receipt)
        files=[{'path':str(p.relative_to(out)),'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())} for p in sorted(out.rglob('*')) if p.is_file() and p.name!='OUTPUT_MANIFEST.json']
        write_json(out/'OUTPUT_MANIFEST.json',{'files':files})
        print(json.dumps({'status':receipt['status'],'wall_seconds':receipt['wall_seconds'],'process_cpu_seconds':receipt['process_cpu_seconds'],'out':str(out.resolve())},sort_keys=True))

if __name__=='__main__':
    raise SystemExit(main())
