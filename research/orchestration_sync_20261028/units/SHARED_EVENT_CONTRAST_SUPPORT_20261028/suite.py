from pathlib import Path
from fractions import Fraction as F
import hashlib,json,sys
sys.dont_write_bytecode=True
import primary as p
import independent as reference
U=Path(__file__).resolve().parent

def dump(name,obj):
    def convert(x):
        if isinstance(x,F):return str(x)
        if isinstance(x,dict):return {str(k):convert(v) for k,v in x.items()}
        if isinstance(x,(tuple,list)):return [convert(v) for v in x]
        return x
    (U/name).write_text(json.dumps(convert(obj),indent=2,allow_nan=False)+'\n')

def reject(fn):
    try:fn()
    except ValueError:return True
    raise AssertionError('INVALID_INPUT_ACCEPTED')

def identity(source,clock,metric,state,rates,weights,units):
    return dict(source=source,clock=clock,metric=metric,state=state,rates=rates,weights=weights,units=units)

def pair(ident):return {'expected':ident,'actual':ident}

def main():
    manifest=json.loads((U/'INPUT_BINDINGS.json').read_text());saved={}
    assert len(manifest['files'])==7
    for row in manifest['files']:
        data=Path(row['path']).read_bytes();assert hashlib.sha256(data).hexdigest()==row['sha256'],'SOURCE_BYTE_CHANGE';saved[row['id']]=json.loads(data)
    # REC/WU: exact source defects propagated through a NEW declared WU-shaped history.
    rec=saved['REC'];wu=next(x for x in saved['WU']['cases'] if x['id']=='cubic_plus');W=F(wu['integrated_forcing']);assert W==F(3,8) and wu['units']['integrated_forcing']=='1'
    edges=rec['edges'];assert len(edges)==8 and [x['line_id'] for x in edges]==list(range(1,9)) and rec['exact_checks_pass']
    h=F(rec['constants']['h_J_s']);literal=[F(x['frequency_Hz']) for x in edges];level=[F(x['level_defined_frequency_Hz']) for x in edges];defects=[F(x['signed_energy_defect_J_event-1']) for x in edges]
    assert all(h*(a-b)==v for a,b,v in zip(literal,level,defects))
    A=[[-h*x for x in level],[h*x for x in literal]];B=[[F(int(i==j),2) for j in range(8)] for i in range(8)];r0=[F(1)]*8
    rr=p.affine_support(A,B,r0,[[W,0],[0,W]],[1,1],[[0],[0]])
    assert rr['central']==W*sum(defects,F(0)) and rr['correlated_radius']==W/2*sum(map(abs,defects),F(0))
    assert rr['independent_box_radius']==W/2*sum((h*(a+b) for a,b in zip(literal,level)),F(0)) and 0<rr['correlated_radius']<rr['independent_box_radius']
    corners=reference.corners(level,literal,h,W);assert len(corners)==256
    assert min(x['integrated_residual'] for x in corners)==rr['lower'] and max(x['integrated_residual'] for x in corners)==rr['upper']
    assert all(all(a>=0 for a in x['amplitudes']) for x in corners)
    recout={**rr,'unit':'J m^-3','energy_per_event_map_J_event':A,'event_amplitude_center_m3':r0,'event_amplitude_B_m3':B,'W_dimensionless':W,'source_defects_J_event':defects,'lower_attaining_corner':next(x['signs'] for x in corners if x['integrated_residual']==rr['lower']),'upper_attaining_corner':next(x['signs'] for x in corners if x['integrated_residual']==rr['upper']),'interpretation':'Literal source defect under declared nonnegative event-amplitude density and WU-shaped p(t), not actual HD evolution or thermal heating'}
    # CR: direct support on the supplied complete case-A fixture; no BFS/mincut replay.
    cr=next(x for x in saved['CR']['cases'] if x['id']=='A');assert cr['finite_count']==3 and cr['pass'] and saved['CR']['exact_checks_pass']
    labels=cr['column_labels'];vertices=[[F(x) for x in row['marginal_solution']] for row in cr['vertices']];coeff=[F(2459,100) if lab[0]=='single' else F(7901,100) for lab in labels]
    cs=p.finite_support(vertices,coeff);cref=reference.cr_vertices(labels,vertices)
    assert cs['minimum']==F(4918,100) and cs['maximum']==F(7901,100)
    boxmax=sum((max(v[j] for v in vertices)*a for j,a in enumerate(coeff)),F(0));assert boxmax==F(33539,200)>cs['maximum']
    for original,x in zip(cr['vertices'],cref):
        assert x['marginals']==[F(1),F(1)] and x['d']==F(original['d'])
        # Original case A: L=S=D=1; saved C=0; 2d-C <= L+S.
        assert F(original['C'])==0 and 2*x['d']-F(original['C'])<=2 and x['d']<=1
        assert 2-2*x['d']+F(original['C'])==F(original['new_facet_slack'])
    assert cs['values']==[x['value_eV_m3'] for x in cref]
    crout={**cs,'unit':'eV m^-3','original_event_mass_units':'m^-3 s^-2','declared_history_weight_s2':F(1),'column_labels':labels,'vertices':vertices,'coefficient_eV':coeff,'independent_coordinate_box_upper':boxmax,'strict_upper_gap':boxmax-cs['maximum'],'marginals_per_vertex':[x['marginals'] for x in cref],'facet':'case A L=S=D=1, C=0; d<=D and 2d-C<=L+S','completeness_source':'Saved full case-A small-fixture BFS with 3 vertices; no claim for actual 3200-atom source'}
    # HE: declared rank-one PSD covariance, no hard-support conversion.
    he=saved['HE'];row=next(x for x in he['rows'] if x['sample']=='fixed_witness' and x['aperture']=='FULL');v=F(row['daughter_variance_MeV2'][0]);assert v>0 and all(F(x)==v for x in row['daughter_variance_MeV2']) and all(F(x)==-v for x in row['daughter_covariance_MeV2'])
    assert F(row['pair_kinetic_total_MeV'])==2*F(row['daughter_mean_MeV'])==2*F(he['constants']['K0_MeV'])
    assert F(row['pair_kinetic_total_variance_MeV2'])==0
    V=[[v,-v],[-v,v]];ht=p.covariance_projection(V,[1,1],validated_psd=True);hi=p.covariance_projection(V,[1,-1],validated_psd=True);href=reference.daughter_variances(v)
    assert ht['contraction']==href['total']==0 and hi['contraction']==href['imbalance']==4*v and href['independent_total']==2*v
    heout={'unit':'MeV^2 per event distribution','v':v,'V':V,'PSD_basis':'v>0 times outer((1,-1),(1,-1))','total':ht,'imbalance':hi,'independent_daughter_variance':2*v,'pair_mean_MeV':F(row['pair_kinetic_total_MeV']),'independent_covariance_can_underbound':hi['contraction']>2*v,'hard_support_inferred':False,'physical_flux_normalization':None,'thermalization':None}
    # REI: reuse D only, abstract dimensionless response fixture.
    D=saved['REI']['D'];assert len(D)==6 and all(len(r)==7 for r in D)
    integerD=[[int(x) for x in row] for row in D];assert all(x==i for row,ints in zip(D,integerD) for x,i in zip(row,ints))
    assert integerD==[[-1 if k==j else 1 if k==j+1 else 0 for k in range(7)] for j in range(6)] and all(sum(row)==0 for row in integerD)
    l=integerD[0];R=[[1,0],[0,1]]+[[0,0] for _ in range(5)];qq=p.affine_support([[1,0],[0,1]],[[1],[1]],[2,3],R,l,[[1] for _ in range(7)])
    assert qq['central']==1 and qq['correlated_radius']==0 and qq['independent_box_radius']==2
    beta=F(7,3);assert sum(a*beta for a in l)==0
    cells=[F(1),F(-1)];assert abs(sum(cells))==0 and sum(map(abs,cells))==2
    qout={**qq,'unit':'abstract dimensionless normalized observable','D_read_from_new_REI_output':integerD,'D_scope':'Only D1=0; actual Q and LOO not recomputed or assigned energy response','R_declared':R,'U_ones':[[1]]*7,'common_offset':beta,'offset_contrast':F(0),'two_cell_common_latent_coefficients':cells,'two_cell_shared_radius':F(0),'two_cell_independent_radius':F(2),'actual_response_inferred':False}
    # Separate actual numerical interfaces; fusion rejected on explicit identity mismatch.
    bass=saved['BASS'];vigi=saved['VIGILODE'];bounds=list(map(F,bass['conditional_enclosure']['entries'][0][1]));kc=max(map(abs,bounds));gamma=F(vigi['uniform_bound']['Gamma'])
    assert bounds[0]<=bounds[1] and gamma>=0 and list(map(F,bass['weights']))==[F(2),F(3),F(5)] and list(map(F,vigi['weights']))==[F(1),F(1,100),F(1,10000)]
    source=bass['binding']['bass_commit']+':'+bass['binding']['binding_id'];clock=bass['binding']['clock']
    bi=identity(source,clock,'SCALAR_COMPONENT_ABSOLUTE_VALUE','BASS_SUPPLIED_FIELD_BOX',bass['conditional_enclosure']['rate_intervals'],bass['weights'],'Fchem per dimensionless x, declared geometry coordinate')
    vi=identity(source,vigi['binding']['clock'],vigi['uniform_bound']['fixed_norm_identity'],'VIGILODE_FIXED_METRIC_DIAGNOSTIC',vigi['uniform_bound']['intervals'],vigi['weights'],'same-norm residual diagnostic, no actual response map')
    bn=p.numerical_scalar_bound(kc,'1/1000',0,0,0,0,1,pair(bi));vn=p.numerical_scalar_bound(0,0,gamma,'1/1000','1/100','1/1000000',1,pair(vi))
    assert bn['epsilon']==kc/F(1000) and vn['epsilon']==gamma/F(1000000)+F(1,100000)+F(1,1000000)
    assert bass['weights']!=vigi['weights']
    weight_only={**bi,'weights':vigi['weights']};mismatch=reject(lambda:p.numerical_scalar_bound(kc,'1/1000',gamma,'1/1000','1/100','1/1000000',1,{'expected':bi,'actual':weight_only}))
    assert reject(lambda:p.numerical_scalar_bound(1,1,1,1,1,1,1,{'expected':bi,'actual':vi}))
    si=identity('SYNTHETIC_SCALAR','declared clock','absolute value','same scalar state','same supplied coefficients',[1],'consistent synthetic source units')
    sn=p.numerical_scalar_bound(2,'1/10',3,'1/5','1/2','1/100',2,pair(si));sref=reference.scalar_oracle();assert sn['epsilon']==sref['epsilon']==F(43,100) and sn['projected_bound']==sref['projected']==F(86,100)
    assert sref['omitted_mismatch']==F(33,100)<sn['epsilon'] and sn['epsilon']-sref['omitted_mismatch']==F(1,10)
    nout={'BASS_component':{**bn,'k_cross':kc,'zeta':F(1,1000)},'VigilODE_fixed_metric':{**vn,'Gamma':gamma,'rho':F(1,1000),'deltaJ':F(1,100),'eta':F(1,1000000)},'incompatible_weights_rejected':mismatch,'equal_basecommit_binding_is_insufficient':True,'consistent_synthetic_scalar':sn,'synthetic_omitted_mismatch_epsilon':sref['omitted_mismatch'],'actual_response_bound_1':'SUPPLIED_DIAGNOSTIC_PREMISE_NOT_PROVED','numerical_controls':4,'actual_joint_BASS_VIGILODE_budget':None}
    validation=all([reject(lambda:p.affine_support([[1]],[[1]],[1],[[1]],[1],[[1]])),reject(lambda:p.finite_support([[1,2]],[1])),reject(lambda:p.exact(0.1)),reject(lambda:p.numerical_scalar_bound(-1,1,1,1,1,1,1,pair(si)))])
    tests={'REC_256_shared_latent_corners_and_strict_gap':True,'CR_3_complete_fixture_vertices_marginals_facet_and_strict_gap':True,'HE_2_contrasts_shared_covariance_and_pair_mean':True,'quotient_2_controls_nuisance_and_common_cells':True,'numeric_4_controls_actual_separate_mismatch_consistent_scalar':True,'kernel_dimension_exact_input_nuisance_nonnegative_rejections':validation}
    assert all(tests.values())
    result={'unit':'SHARED_EVENT_CONTRAST_SUPPORT_20261028','status':'PASS_SCOPED_FINITE_COMPOSITION_PENDING_C9','tests':tests,'control_groups':len(tests),'counts':{'REC_corners':256,'CR_vertices':3,'HE_contrasts':2,'quotient_controls':2,'numerical_controls':4},'REC_WU':recout,'CR':crout,'HE':heout,'quotient':qout,'numerical':nout,'source_admission_dependency':'ROOT_GO_SCOPED_REUSE; final admission waits fresh source and synthesis reviews','theorem':'Correlate AB before projection/absolute values; finite support exact under supplied complete latent box or vertex family; covariance contraction does not imply hard support','unresolved_physical_mappings':['Actual common source histories and reservoir normalization','Actual observable response/propagator and response norm','BASS/Vigi matching weights, norms, source corridors','All physical cross-project maps; no universal conversion between J, eV and MeV instances'],'canonical_progress':'28/88 unchanged','canonical_delta':0,'physicalcompletion':None,'production':'HOLD','L4':False,'whole_domain_certificate':False,'actual_ode_solution_enclosure':False,'old_producer_imports':0,'new_trajectories':0}
    dump('RESULTS.json',result);dump('REFERENCE.json',{'REC_corners':corners,'CR_vertices':cref,'HE':href,'synthetic_scalar':sref,'production_imported':False});dump('EXACT_INPUTS.json',{'REC_A':A,'REC_B':B,'REC_r0':r0,'WU_W':W,'CR_labels':labels,'CR_vertices':vertices,'CR_coefficients':coeff,'HE_V':V,'quotient_R':R,'quotient_l':l,'quotient_U':[[1]]*7,'BASS_identity':bi,'Vigi_identity':vi,'synthetic_identity':si})
    figure(result)
    print('PASS: 256 REC corners, 3 CR vertices, 2 HE contrasts, 2 quotient and 4 numerical controls; six groups')

def figure(result):
    # Separate axes and unit labels; approximate display only, exact values in JSON.
    panels=[('REC + declared WU history','J m^-3', [('shared',result['REC_WU']['correlated_radius']),('independent',result['REC_WU']['independent_box_radius'])]),('CR case-A upper support','eV m^-3',[('vertices',result['CR']['maximum']),('coordinate box',result['CR']['independent_coordinate_box_upper'])]),('HE daughter variance','MeV^2 / event distribution',[('total shared',F(0)),('total independent',2*result['HE']['v']),('imbalance shared',4*result['HE']['v']),('imbalance independent',2*result['HE']['v'])]),('Nuisance contrast support','abstract dimensionless',[('shared latent',F(0)),('independent box',F(2))])]
    s=['<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="780" role="img"><title>Shared event correlation and independent box comparisons in separate units</title><rect width="100%" height="100%" fill="white"/><g font-family="sans-serif" fill="#172635"><text x="30" y="30" font-size="21">Preserve shared-event structure before bounding</text><text x="30" y="53">Four conditional instances. Each panel has its own scale and units; no common physical response is inferred.</text>']
    for k,(title,unit,items) in enumerate(panels):
        ox=35+(k%2)*550;oy=85+(k//2)*325;top=max(float(v) for _,v in items) or 1
        s.append(f'<text x="{ox}" y="{oy}" font-size="17">{title}</text><text x="{ox}" y="{oy+22}" font-size="12">{unit}</text><path d="M{ox+35} {oy+45}V{oy+210}H{ox+480}" fill="none" stroke="#172635"/>')
        for j,(label,v) in enumerate(items):
            x=ox+85+j*(380/max(1,len(items)-1));height=140*float(v)/top;yy=oy+210-height;color='#1768a2' if 'independent' not in label and 'box' not in label else '#d58628'
            s.append(f'<rect x="{x-22}" y="{yy}" width="44" height="{height}" fill="{color}"/><text x="{x}" y="{yy-8}" text-anchor="middle" font-size="12">{float(v):.5g}</text><text x="{x}" y="{oy+230}" text-anchor="middle" font-size="10">{label}</text>')
    s.append('<text x="30" y="750" font-size="12">Labels are approximate displays. Exact fractions, witnesses, units, assumptions and source hashes are saved with this figure.</text></g></svg>')
    (U/'correlation_gaps.svg').write_text(''.join(s)+'\n')

if __name__=='__main__':
    try:main()
    except Exception as exc:
        dump('FAILURE.json',{'status':'FAIL_STOP_FOR_AUTHORITY','type':type(exc).__name__,'message':str(exc)})
        raise
