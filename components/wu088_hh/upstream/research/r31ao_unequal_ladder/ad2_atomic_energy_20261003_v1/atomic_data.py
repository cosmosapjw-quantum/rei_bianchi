"""Frozen107 atomic certificate reuse and signed channel energies, not a rate solver.

Only exact rational arithmetic is performed. Historical atomic integration is not
imported or executed. All energies are rest-frame Eh, infinite-nuclear-mass model.
"""
from __future__ import annotations
from fractions import Fraction as F
from pathlib import Path
from decimal import Decimal, localcontext
import argparse, hashlib, json, re, sys

class ContractError(ValueError):
    """Malformed or inconsistent finite-model input."""
class SourceUnavailable(ContractError):
    """The requested physical quantity is not supplied by these atomic data."""

def fraction(x) -> F:
    if type(x) is bool or isinstance(x,float):
        raise ContractError('FLOAT_OR_BOOL_NOT_EXACT_INPUT')
    if isinstance(x,F): q=x
    elif type(x) is int: q=F(x)
    elif type(x) is str and len(x)<=20000 and re.fullmatch(r'-?\d+(?:/\d+)?',x):
        try:q=F(x)
        except (ZeroDivisionError,ValueError) as e:raise ContractError('INVALID_RATIONAL') from e
    else:raise ContractError('EXACT_RATIONAL_REQUIRED')
    if max(abs(q.numerator).bit_length(),q.denominator.bit_length())>32768:
        raise ContractError('RATIONAL_WORK_BUDGET')
    return q

def interval(x) -> tuple[F,F]:
    if type(x) is dict:
        if set(x)!={'lo','hi'}:raise ContractError('INTERVAL_FIELDS')
        x=(x['lo'],x['hi'])
    if type(x) not in (tuple,list) or len(x)!=2:raise ContractError('INTERVAL_REQUIRED')
    lo,hi=map(fraction,x)
    if lo>hi:raise ContractError('REVERSED_INTERVAL')
    return lo,hi

def out_iv(lo,hi):return {'lo':str(lo),'hi':str(hi)}
def signed_defect(ionic,ground,active) -> tuple[str,str]:
    e=fraction(ionic);g0,g1=interval(ground);a0,a1=interval(active)
    return str(e-g1-a1),str(e-g0-a0)
def model_affinity(ionic,ground) -> tuple[str,str]:
    e=fraction(ionic);a,b=interval(ground);return str(a-e),str(b-e)
def sign_of(x):
    a,b=interval(x)
    return 'POSITIVE' if a>0 else 'NEGATIVE' if b<0 else 'ZERO' if a==b==0 else 'UNRESOLVED_SIGN'
def check_energy_parts(values):
    q={k:fraction(values[k])for k in ('N','T','T_strong','V_nuclear','V_ee','E')}
    if q['N']<=0 or q['T']!=q['T_strong'] or (q['T']+q['V_nuclear']+q['V_ee'])/q['N']!=q['E']:
        raise ContractError('CERTIFICATE_ENERGY_IDENTITY_MISMATCH')
    return q

def physical_threshold(row):
    raise SourceUnavailable('ATOMIC_SIGNED_DEFECT_IS_NOT_A_PRESCRIBED_TRAJECTORY_THRESHOLD')

def _pairs(pairs):
    d={}
    for k,v in pairs:
        if k in d:raise ContractError('DUPLICATE_JSON_KEY')
        d[k]=v
    return d

def read_json(path):
    return json.loads(Path(path).read_text(),object_pairs_hook=_pairs,
                      parse_constant=lambda x:(_ for _ in ()).throw(ContractError('NONFINITE_JSON')))
def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def verify_sources(root):
    root=Path(root).resolve();lock=read_json(root/'SOURCE_LOCK.json')
    for name,item in lock['files'].items():
        relative=Path(name)
        if relative.is_absolute() or '..' in relative.parts:raise ContractError('UNSAFE_SOURCE_PATH')
        p=root/relative
        if p.is_symlink() or not p.is_file() or not p.resolve().is_relative_to(root):raise ContractError('SOURCE_MISSING_OR_SYMLINK')
        if p.stat().st_size!=item['bytes'] or digest(p)!=item['sha256']:raise ContractError('SOURCE_HASH_MISMATCH:'+name)
    return len(lock['files'])

def parse_stdout(path):
    rows={}
    for line in Path(path).read_text().splitlines():
        k,v=line.split(' ',1)
        if k in rows:raise ContractError('DUPLICATE_CERTIFICATE_KEY')
        rows[k]=v
    return rows

def pi_bounds(terms=90):
    if type(terms)is not int or not 2<=terms<=512:raise ContractError('PI_WORK_BUDGET')
    def atan_recip(n):
        s=sum((F((-1)**k,(2*k+1)*n**(2*k+1))for k in range(terms)),F(0))
        t=s+F((-1)**terms,(2*terms+1)*n**(2*terms+1))
        return min(s,t),max(s,t)
    a,b=atan_recip(5);c,d=atan_recip(239)
    return 16*a-4*d,16*b-4*c

def display(x):
    with localcontext() as ctx:
        ctx.prec=45;x=fraction(x);return str(Decimal(x.numerator)/Decimal(x.denominator))

def recover(root):
    """Verify binding and consume immutable previous integration outputs."""
    root=Path(root);count=verify_sources(root);s=root/'sources'
    raw=parse_stdout(s/'CP1_ionic_rational.stdout');q=check_energy_parts(raw)
    binary=parse_stdout(s/'CP1_ionic_binary64.stdout');other=parse_stdout(s/'CP1_radial_sum_difference.stdout')
    for key in ('N','T','V_nuclear','V_ee','E'):
        if fraction(other[key])!=q[key] or fraction(binary[key])!=q[key]:raise ContractError('HISTORICAL_OUTPUTS_DISAGREE')
    cert=read_json(s/'CP1_CUSP_CERTIFICATE_90.json');trial=read_json(s/'CP1_CUSP_TRIAL.json');old=read_json(s/'CP1_ATOMIC_RESULTS.json')
    if fraction(cert['zeta'])!=1 or fraction(trial['zeta'])!=1:raise ContractError('EXPONENT_CHANGED')
    if fraction(cert['exact_expression']['N'][0])!=q['N'] or any(fraction(x)!=0 for x in cert['exact_expression']['N'][1:]):raise ContractError('N_EXPRESSION')
    if fraction(cert['exact_expression']['H'][0])!=q['N']*q['E'] or any(fraction(x)!=0 for x in cert['exact_expression']['H'][1:]):raise ContractError('H_EXPRESSION')
    for key,value in [('norm_reduced',q['N']),('energy_Eh',q['E'])]:
        if fraction(cert['intervals'][key]['lower'])!=value or fraction(cert['intervals'][key]['upper'])!=value:raise ContractError('CERTIFICATE_VALUE_MISMATCH')
    if fraction(old['ionic']['N_exact'])!=q['N'] or fraction(old['ionic']['E_exact_Eh'])!=q['E']:raise ContractError('ATOMIC_REPORT_MISMATCH')
    terms=[(a,b,c,fraction(v))for a,b,c,v in trial['polynomial']]
    ct=[(*row['powers'],fraction(row['coefficient']))for row in cert['polynomial']]
    txt=(s/'CP1_ionic_rational.txt').read_text().splitlines()
    tt=[(int(a),int(b),int(c),F(int(n),int(d)))for a,b,c,n,d in (l.split()for l in txt[1:])]
    if not len(terms)==int(txt[0])==107 or len({x[:3]for x in terms})!=107 or terms!=ct or terms!=tt:
        raise ContractError('ORDERED107_IDENTITY_MISMATCH')
    # np.load reads exact stored arrays; no orbital calculation or imported producer.
    import numpy as np
    with np.load(s/'FROZEN_INPUTS.npz',allow_pickle=False) as npz:
        C=npz['C'];pref=F(*float(npz['pref']).as_integer_ratio());v=F(*float(npz['v']).as_integer_ratio())
        if C.shape!=(9,9,9) or C.dtype!=np.dtype('<f8') or int(np.count_nonzero(C))!=107:raise ContractError('FROZEN_COEFFICIENT_LAYOUT')
        if any(F(*float(C[a,b,c]).as_integer_ratio())!=x for a,b,c,x in terms):raise ContractError('REPRESENTED_COEFFICIENT_MISMATCH')
        se=[F(*float(x).as_integer_ratio())for x in npz['s_eps']];pe=[F(*float(x).as_integer_ratio())for x in npz['p_eps']]
        phase=[F(*float(x).as_integer_ratio())for x in npz['phase_E']]
    levels=read_json(s/'AD1_ATOMIC_LEVELS.json');walk=read_json(s/'C0_HH_CHANNEL_CROSSWALK.json')
    frozen_sha=digest(s/'FROZEN_INPUTS.npz')
    if frozen_sha!=levels['common']['input_sha256'] or frozen_sha!=walk['source_input_sha256']:raise ContractError('CROSS_STAGE_INPUT_MISMATCH')
    byid={x['id']:x for x in levels['levels']}
    if len(byid)!=13 or len({x['radial_id']for x in byid.values()})!=9:raise ContractError('AD1_LEVEL_COUNTS')
    for row in levels['levels']:
        energy=(se if row['l']==0 else pe)[int(row['radial_id'].split(':')[1])]
        if energy!=fraction(row['energy_stored_Eh']):raise ContractError('AD1_STORED_ENERGY_MISMATCH')
        interval(row['rayleigh_Eh'])
    neutral=[x for x in walk['rows'] if x['row']<47]
    if [x['row']for x in walk['rows']]!=list(range(49)):raise ContractError('CHANNEL_ORDER_CHANGED')
    for row in neutral:
        expected=(se if row['orbital']=='s' else pe)[row['radial_index']]
        if F(*float.fromhex(row['one_center_energy_hex']).as_integer_ratio())!=expected:raise ContractError('CHANNEL_ENERGY_MISMATCH')
    return q,cert,old,byid,walk,se,pe,phase,pref,v,count

def build_data(root):
    q,cert,old,byid,walk,se,pe,phase,pref,v,count=recover(root)
    E=q['E'];Eg=interval(byid['s:0']['rayleigh_Eh']);aff=tuple(map(fraction,model_affinity(E,Eg)))
    common={'model_id':'CP1_FROZEN107_PLUS_AD1_H12G_V1','energy_unit':'Eh','energy_zero':'infinite_mass_nonrelativistic_separated_bare_nuclei_and_free_electrons',
            'atomic_input_sha256':digest(Path(root)/'sources/FROZEN_INPUTS.npz'),'physical_data_admitted':False,'source_integrations_replayed':0}
    ionic={'schema':'WU088_AD2_IONIC_PROPERTIES_V1','common':common,'trial_energy_Eh':str(E),'reduced_norm':str(q['N']),
           'normalized_components_Eh':{k:str(q[k]/q['N'])for k in ('T','V_nuclear','V_ee')},
           'virial_defect_Eh':str((2*q['T']+q['V_nuclear']+q['V_ee'])/q['N']),
           'analytic_H_dissociation_margin_Eh':str(-F(1,2)-E),
           'finite_H_model_affinity_Eh':out_iv(*aff),
           'finite_H_ground_ionization_Eh':out_iv(-Eg[1],-Eg[0]),
           'residual_Eh_inherited':cert['intervals']['residual_Eh'],
           'residual_squared_Eh2_inherited':cert['intervals']['residual_squared_Eh2'],
           'residual_semantics':cert['graph_gram_semantics'],
           'physical_Hminus_eigenvalue':None,'physical_rate':None,
           'historical_review_scope':'CP1 atomic_exact_integration_and_fixed_registry PROMOTE_SCOPED; not a new AD2 independent review',
           'original_projector_status':cert['projector_status']}
    rows=[]
    for row in walk['rows'][:47]:
        rid=row['row'];orb=row['orbital'];idx=row['radial_index'];key=f'{orb}:{idx}'
        stored=(se if orb=='s' else pe)[idx]
        item={'row':rid,'active_center':row['active_center'],'orbital':orb,'radial_index':idx,
              'input_kind':row['kind'],'spectator':'s:0_other_center','ionic_output_rows':[47,48],
              'two_orientations_energy_equal_not_two_independent_events':True,
              'stored_Ritz_sum_Eh':str(stored+se[0]),
              'stored_Ritz_signed_defect_Eh':str(E-stored-se[0]),
              'stored_Ritz_is_not_expectation_substitute':True,
              'phase_E_used_for_atomic_energy':False,'physical_threshold_J':None,'sigma':None,'rate':None}
        if key in byid:
            Ea=interval(byid[key]['rayleigh_Eh']);df=tuple(map(fraction,signed_defect(E,Eg,Ea)))
            item.update({'neutral_model_expectation_Eh':out_iv(Eg[0]+Ea[0],Eg[1]+Ea[1]),
                         'ionic_minus_neutral_Eh':out_iv(*df),'neutral_minus_ionic_Eh':out_iv(-df[1],-df[0]),
                         'sign':sign_of(df),'status':'FINITE_BOUNDLIKE_CHANNEL_ENERGY_EVALUATED',
                         'AD1_atomic_level_id':key})
        else:
            item.update({'neutral_model_expectation_Eh':None,'ionic_minus_neutral_Eh':None,'neutral_minus_ionic_Eh':None,
                         'sign':None,'status':'POSITIVE_RITZ_DIAGNOSTIC_ONLY_EXPECTATION_UNAVAILABLE','AD1_atomic_level_id':None})
        rows.append(item)
    channel={'schema':'WU088_AD2_CHANNEL_DEFECTS_V1','common':common,'rows':rows,'summary':{'neutral_rows':47,'boundlike_expectation_rows':sum(x['ionic_minus_neutral_Eh']is not None for x in rows),'pseudostate_rows_without_expectation':sum(x['ionic_minus_neutral_Eh']is None for x in rows),'ionic_orientations':2}}
    plo,phi=pi_bounds();factor=8*pref*pref*q['N'];norm=(factor*plo*plo,factor*phi*phi)
    diagnostics={'schema':'WU088_AD2_REPRESENTATION_V1','coefficient_count':107,'coefficient_difference_count':0,
                 'signed_ordered_polynomial_preserved':True,'original_pref_exact':str(pref),
                 'represented_full_norm':out_iv(*norm),'represented_norm_minus_one':out_iv(norm[0]-1,norm[1]-1),
                 'old_binary64_display_norm_error':old['ionic']['represented_norm_error'],
                 'old_float_diagnostic_not_rewritten':True,
                 'normalization_is_new_scalar_algebra_not_new_atomic_integral':True,
                 'stored_ionic_phase_minus_rest_and_ETF_Eh':[str(phase[j]-E-v*v/4)for j in (47,48)],
                 'phase_check_is_diagnostic_only_no_threshold_admission':True,
                 'source_files_verified':count,'exact_energy_parts_identity':True,'historic_independent_N_T_V_E_equal':True}
    completeness={'schema':'WU088_AD2_COMPLETENESS_V1','ionic_expectation':'CERTIFICATE_REUSED_WITH_EXACT_SOURCE_BINDING',
                  'channel_energies':'25_BOUNDLIKE_ROWS_PLUS22_STORED_RITZ_DIAGNOSTICS','physical_affinity':'NOT_SUBSTITUTED',
                  'actual_sigma':None,'actual_rate':None,'actual_epsilon_C':None,'actual_epsilon_R':None,
                  'accepted_cells':20,'total_cells':289,'missing_unbounded_cells':269,'B22':'OPEN_UNDETERMINED',
                  'Bianchi_or_thermal_solver_changed':False,'historical_science_runs':0,
                  'NCP_scopes_consumed':False,'scientific_admission':False,'production_admission':False,
                  'new_independent_science_review':False,
                  'next_action':'AD3_BOUNDLIKE_E1_CASCADE_DATA_AND_LIFETIME_FACTORS'}
    return {'IONIC_PROPERTIES.json':ionic,'CHANNEL_ENERGY_DEFECTS.json':channel,'REPRESENTATION_DIAGNOSTICS.json':diagnostics,'COMPLETENESS.json':completeness}

def generate(root,output):
    # Build entirely before creating output. Existing output is never replaced.
    output=Path(output)
    if output.exists():raise ContractError('OUTPUT_ALREADY_EXISTS')
    data=build_data(root);output.mkdir(parents=False)
    for name,obj in data.items():
        with (output/name).open('x')as f:json.dump(obj,f,indent=2,ensure_ascii=False);f.write('\n')
    return data

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,default=Path(__file__).parent);ap.add_argument('--output',type=Path);ap.add_argument('--row',type=int);ap.add_argument('--physical',action='store_true');args=ap.parse_args()
    try:
        if args.physical:physical_threshold(None)
        if args.output:result=generate(args.root,args.output);print(json.dumps({'status':'ATOMIC_CERTIFICATE_REUSED_DATA_GENERATED','files':list(result),'physical_admission':False}));return 0
        data=build_data(args.root)
        if args.row is not None:
            if not 0<=args.row<47:raise ContractError('NEUTRAL_ROW_REQUIRED')
            data=data['CHANNEL_ENERGY_DEFECTS.json']['rows'][args.row]
        else:data=data['IONIC_PROPERTIES.json']
        print(json.dumps(data,indent=2));return 0
    except (ContractError,KeyError,ValueError,OSError)as e:
        print(json.dumps({'status':'REJECTED','reason':str(e)}),file=sys.stderr);return 2
if __name__=='__main__':sys.exit(main())
