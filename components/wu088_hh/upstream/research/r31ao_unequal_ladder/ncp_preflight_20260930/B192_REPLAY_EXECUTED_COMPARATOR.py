"""Postprocess an authorized existing-data ladder; contains no producer call."""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import numpy as np

LD=np.longdouble
CD=np.clongdouble
FIELDS=('O','dotO','D_col','D_row')


def module(path,name):
    s=importlib.util.spec_from_file_location(name,path)
    obj=importlib.util.module_from_spec(s);s.loader.exec_module(obj)
    return obj


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def wide_norms(raw):
    """Rank<=2 spectral norm by a 2x2 Gram formula, in raw longdouble.

    Only diagnostic arithmetic is scaled. Source matrices are never changed.
    No binary64 SVD or source cast is used for order-difference norms.
    """
    a=np.asarray(raw)
    if a.shape not in ((47,2),(2,47)) or a.dtype!=np.dtype(CD) or not np.isfinite(a).all():
        raise ValueError('finite raw complex256 mixed block required')
    a=a if a.shape==(47,2) else a.conj().T
    scale=np.max(np.abs(a))
    if scale==0:
        return {'spectral_2':LD(0),'frobenius':LD(0),'max_abs':LD(0)}
    b=a/scale
    aa=np.sum(np.abs(b[:,0])**2,dtype=LD)
    dd=np.sum(np.abs(b[:,1])**2,dtype=LD)
    cc=np.sum(b[:,0].conj()*b[:,1],dtype=CD)
    eigen=(aa+dd+np.sqrt((aa-dd)**2+4*np.abs(cc)**2))/2
    return {'spectral_2':scale*np.sqrt(eigen),'frobenius':scale*np.sqrt(aa+dd),'max_abs':scale}


def decimal_norms(raw):
    return {k:str(v) for k,v in wide_norms(raw).items()}


def direction_diagnostics(d12,d23):
    a,b=np.asarray(d12),np.asarray(d23)
    na,nb=wide_norms(a)['frobenius'],wide_norms(b)['frobenius']
    if na==0 or nb==0:
        return {'status':'DIRECTION_UNDEFINED_ZERO_INCREMENT','alignment':None,
                'best_positive_scalar_fit':None,'scalar_fit_residual':None,'certification_threshold':None}
    align=np.sum(((b/nb).conj()*(a/na)).real,dtype=LD)
    alpha=align*na/nb
    if alpha<=0:
        return {'status':'NO_POSITIVE_SCALAR_MINIMIZER','alignment':str(align),
                'best_positive_scalar_fit':None,'scalar_fit_residual':None,
                'positive_fit_infimum_frobenius_at_alpha_zero':str(na),'certification_threshold':None}
    residual=a-alpha*b
    return {'status':'DIRECTION_DIAGNOSTIC_ONLY','alignment':str(align),
            'best_positive_scalar_fit':str(alpha),'scalar_fit_residual':decimal_norms(residual),
            'scalar_fit_relative_frobenius_residual':str(wide_norms(residual)['frobenius']/na),
            'certification_threshold':None}


def compare_raw_blocks(q128,q160,q192,helper):
    a,b,c=map(np.asarray,(q128,q160,q192))
    for arr in (a,b,c): wide_norms(arr)
    if a.shape!=b.shape or b.shape!=c.shape:
        raise ValueError('same raw block ordering/shape required')
    d12=b-a;d23=c-b
    n12,n23=wide_norms(d12)['spectral_2'],wide_norms(d23)['spectral_2']
    diagnostic={'rigorous':False,'stable_matrix_error_direction_required':True}
    if n12==0 or n23==0:
        diagnostic.update({'status':'INCREMENT_RATIO_UNDEFINED','rho':None,'p_cond':None})
    else:
        rho=n12/n23
        diagnostic['rho_longdouble_decimal']=str(rho)
        if rho<=LD(helper.THRESHOLD):
            diagnostic.update({'status':'POSITIVE_POWER_MODEL_INCOMPATIBLE_NORMWISE','p_cond':None})
        else:
            x=helper.conditional_errors(float(n12),float(n23))
            diagnostic.update({'status':'CONDITIONAL_UNEQUAL_RATIO_ASYMPTOTIC_DIAGNOSTIC',**x})
    return d12,d23,{'Delta128160_norms_longdouble_decimal':decimal_norms(d12),
                    'Delta160192_norms_longdouble_decimal':decimal_norms(d23),
                    'raw_dtype':str(a.dtype),'conditional':diagnostic,
                    'direction':direction_diagnostics(d12,d23)}


def compare_frozen(predictions,raw_truth,primary,secondary,refinement):
    """Reuse parent metric arithmetic and decision expressions unchanged."""
    truth=tuple(np.asarray(raw_truth[k],dtype=np.complex128) for k in FIELDS)
    truth+=((truth[2]-truth[3].conj().T)/2,)
    errors={name:secondary.errors(pred,truth) for name,pred in predictions.items()}
    metrics=('E_K_per_ta','E_Dmax_per_ta');tol=1e-10
    local,glob=errors['R31AK'],errors['R31Z']
    local_support=all(local[k]<=glob[k]+tol for k in metrics) and any(glob[k]-local[k]>tol for k in metrics)
    global_support=all(glob[k]<=local[k]+tol for k in metrics) and any(local[k]-glob[k]>tol for k in metrics)
    if local_support and global_support:raise ValueError('inconsistent frozen rule')
    pv='PARETO_SUPPORTED_AT_SELECTED_HOLDOUT' if local_support else 'GLOBAL_SUPPORTED_AT_SELECTED_HOLDOUT' if global_support else 'TRADEOFF_UNRESOLVED'
    sv=refinement.pareto_verdict([errors['R31AK'][k] for k in metrics],
                                [errors['R31AD'][k] for k in metrics],tol)
    return {'primary_verdict':pv,'secondary_verdict':sv,'model_errors':errors,
            'direct_metric_identity_residual_primary_arithmetic':primary.n2(raw_truth['dotO']-raw_truth['D_col']-raw_truth['D_row'].conj().T),
            'direct_metric_identity_residual_secondary_arithmetic':secondary.n2(truth[1]-truth[2]-truth[3].conj().T),
            'metric_residual_is_source_error_bound':False,
            'metric_arithmetic':'Unchanged frozen parent complex128 diagnostic comparison; raw order differences and their norms remain complex256/longdouble.',
            'comparison_tolerance_per_ta':tol,'weighted_score_used':False}


def load_predictions(repo,secondary_prereg):
    pins=secondary_prereg['locked_files']
    with np.load(repo/pins['R31AK_prediction_npz']['path'],allow_pickle=False) as f:
        predictions={name:tuple(f['z0p75_'+name+'_'+k] for k in ('O','dotO','Dcol','Drow','K')) for name in ('R31AK','R31Z')}
    with np.load(repo/pins['R31AD_coarse_npz']['path'],allow_pickle=False) as f:
        predictions['R31AD']=tuple(f['z0p75_R31AD_'+k] for k in ('O','dotO','Dcol','Drow','K'))
    return predictions


def load_raw(od,jvp,order,contract,adapter):
    identity=adapter.check_files(od,jvp,order,contract)
    with np.load(od,allow_pickle=False) as f:raw={k:f[k] for k in ('O','D_col','D_row')}
    with np.load(jvp,allow_pickle=False) as f:raw['dotO']=f['dotO'];other_O=f['O']
    shapes={'O':(47,2),'dotO':(47,2),'D_col':(47,2),'D_row':(2,47)}
    if any(raw[k].shape!=shapes[k] for k in FIELDS) or other_O.shape!=(47,2):
        raise ValueError('mixed block shape/order drift')
    for value in (*raw.values(),other_O):wide_norms(value)
    gap=other_O-raw['O']
    identity['OD_JVP_O_gap_raw_norms']=decimal_norms(gap)
    identity['array_contract']={k:{'shape':list(v.shape),'raw_dtype':str(v.dtype),'array_bytes_sha256':hashlib.sha256(v.tobytes()).hexdigest()} for k,v in raw.items()}
    return raw,identity


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--lock',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True);ap.add_argument('--b192-only',action='store_true')
    for n in (128,160,192):
        ap.add_argument('--od'+str(n),type=Path);ap.add_argument('--jvp'+str(n),type=Path)
    args=ap.parse_args();repo=args.repo.resolve();lock=json.loads(args.lock.read_text())
    if args.out.exists():raise FileExistsError(args.out)
    for pin in lock['files']:
        p=Path(pin['path']);p=p if p.is_absolute() else repo/p
        if digest(p)!=pin['sha256']:raise ValueError('pre-output pin drift: '+str(p))
    base=repo/'research/r31ao_unequal_ladder'
    adapter=module(base/'order_metadata_adapter.py','r31ao_adapter')
    helper=module(base/'unequal_order_ladder.py','r31ao_helper')
    primary=module(repo/'research/r31ak_eight_node/compare_future_holdout.py','r31ao_parent_primary')
    secondary=module(repo/'research/r31al_z075_gate/compare_secondary_refinement.py','r31ao_parent_secondary')
    refinement=module(repo/'research/r31al_z075_gate/refinement_gain.py','r31ao_parent_refinement')
    prereg=json.loads((repo/'research/r31al_z075_gate/ncp_followup_20260930/SECONDARY_REFINEMENT_PREREGISTRATION.json').read_text())
    predictions=load_predictions(repo,prereg)
    contract=json.loads((repo/lock['source_contract_path']).read_text())
    orders=(192,) if args.b192_only else (128,160,192)
    raw={};identities={};verdicts={}
    for n in orders:
        od=getattr(args,'od'+str(n));jvp=getattr(args,'jvp'+str(n))
        if od is None or jvp is None:raise ValueError('complete order paths required')
        raw[n],identities[n]=load_raw(od,jvp,n,contract,adapter)
        # PRIMARY result is calculated before SECONDARY for each reference.
        verdicts[n]=compare_frozen(predictions,raw[n],primary,secondary,refinement)
    result={'schema':'WU088_R31AO_FINITE_ORDER_REPLAY_V1','order_identities':identities,
            'verdicts':verdicts,'SOURCE_ACCURACY_BOUND':'SOURCE_ACCURACY_BOUND_UNAVAILABLE',
            'rigorous':False,'science_producer_commands':0,'new_science_nodes':0}
    for n in orders:
        if digest(getattr(args,'od'+str(n)))!=identities[n]['OD'] or digest(getattr(args,'jvp'+str(n)))!=identities[n]['JVP']:
            raise ValueError('source array file mutated during postprocessing')
    if args.b192_only:
        result['status']='B192_ONLY_REPLAY__FULL_LADDER_NOT_EVALUATED'
    else:
        signatures={(v['primary_verdict'],v['secondary_verdict']) for v in verdicts.values()}
        baseline=(lock['baseline_verdicts']['primary'],lock['baseline_verdicts']['secondary'])
        result['status']='B_ORDER_VERDICT_STABLE_OVER_128_160_192' if signatures=={baseline} else 'FINITE_ORDER_VERDICTS_DIFFER'
        differences={};blocks={}
        for k in (*FIELDS,'K'):
            values=[raw[n][k] if k!='K' else (raw[n]['D_col']-raw[n]['D_row'].conj().T)/2 for n in orders]
            d12,d23,blocks[k]=compare_raw_blocks(*values,helper)
            differences['Delta128160_'+k]=d12;differences['Delta160192_'+k]=d23
        path=args.out.with_suffix('.differences.npz')
        if path.exists():raise FileExistsError(path)
        with path.open('xb') as f:np.savez(f,**differences)
        result['raw_difference_artifact']={'path':str(path),'sha256':digest(path),'bytes':path.stat().st_size,'dtype':str(np.dtype(CD))}
        result['blocks']=blocks
    with args.out.open('x') as f:f.write(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps(result,indent=2,allow_nan=False))


if __name__=='__main__':main()
