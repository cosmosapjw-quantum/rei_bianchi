from pathlib import Path
from fractions import Fraction as F
import json,sys,csv,hashlib,platform
from mpmath import mp,iv
D=Path(__file__).resolve().parents[1];sys.path.insert(0,str(D/'src'));import sheldon_model as M
mp.dps=65;iv.dps=50
P=D/'parent/WU088_HH_PHYS24_20261013/predecessor23/WU088_HH_PHYS23_20261013'
p23=json.loads((P/'results/PHYS23_RESULT.json').read_text());p22=json.loads((P/'inputs/interval_result_v3.json').read_text())
interval=json.loads((D/'results/PARTIAL_RATE_INTERVAL.json').read_text());thr=json.loads((D/'results/THRESHOLD_INTERVAL.json').read_text())
val=json.loads((D/'checks/VALIDATION_BASE.json').read_text());checks=val['checks']
def check(n,b,d=None):
 checks.append({'name':n,'pass':bool(b),'detail':d})
 if not b:raise AssertionError(n)
def mpf(q):
 q=F(q);return mp.mpf(q.numerator)/q.denominator
def fmp(q):return F(str(q))
def rng(x):return list(map(str,x))
kl,ku=map(F,interval['interval_rational']);check('positive_ordered_partial_interval',0<kl<ku)
check('all_512_positive_bins',len(interval['rows'])==512 and all(F(v[2])>=0 and F(v[3])>=F(v[2]) for v in interval['rows']))
check('energy_bin_partition',F(interval['rows'][0][0])==1 and F(interval['rows'][-1][1])==2 and all(a[1]==b[0] for a,b in zip(interval['rows'],interval['rows'][1:])))
check('positive_uniform_derivative_certificates',all(F(x['uniform_derivative_lower'])>0 for x in interval['monotonicity_certificate']))
kr=M.thermal_partial(50000);lcs=mp.mpf(p23['point_rates_cm3_s']['LCS91']);check('independent_partial_quadrature_in_interval',mpf(kl)<=kr<=mpf(ku))
for spin in ['singlet','triplet']:
 for mode in ['source','restored']:
  a,b=map(F,thr[spin][mode]['interval_rational']);x=M.threshold_g(spin,mode);check(f'threshold_integral_in_exact_basis_interval_{spin}_{mode}',mpf(a)<=x<=mpf(b))
# Observed cloud Wolfram output, recorded as selected normalized transcription.
wol={'record_kind':'selected normalized transcription of actual cloud evaluator output; not raw transport bytes','executed_input_sha256':hashlib.sha256((D/'wolfram/verify_sheldon.wl').read_bytes()).hexdigest(),'kernel':'15.0.1 for Linux x86 (64-bit) (July 2, 2026)','xTensor_version':'1.3.0','xPerm_version':'1.2.4','xTensor_sha256':'04e1cf3c7e81f1eff61ca633c84537c3f3cbb0fdd42ea01441e89172086d8b36','tensor_residuals':[0,0],'scalar_residuals':[0]*15,'all_zero':True,'g_source':['0.20923439847033366202965259781780000472657949340153318004338873942838533308356','0.02660216081846962750490834599049155089495112341875417427644206045441398224199'],'g_restored':['0.15210043273427874461059825142438061798491740419297586421747929591399646434494','0.01317020124905616923593291438939613789720246320946400555292712595106067627897'],'unpolarized_threshold_ratio':'0.6629201926999178327249969081045293631758782231934256833519','partial_tagged_network_rate_cm3_s':'1.16947418620134532893138479236127525318044339106e-11','sigma_source_at_2Ry_a02':['3.1997029963095051506946659732196553379802908509269884929487','1.2777498125500189386394939620964234589679302291584718943081','1.7582381084898904916532869648772314287210203846006010439658'],'diagnostics':['Symbol::undefined2 pre-evaluation warning','General::messages summary; all returned residuals were literal zero and numeric results matched separate formulas']}
(D/'wolfram/OBSERVED_RESULTS.json').write_text(json.dumps(wol,indent=2)+'\n')
check('Wolfram_partial_vs_mp65',abs(kr-mp.mpf(wol['partial_tagged_network_rate_cm3_s']))/kr<mp.mpf('1e-34'))
for i,spin in enumerate(['singlet','triplet']):
 check('Wolfram_threshold_'+spin,abs(M.threshold_g(spin,'restored')-mp.mpf(wol['g_restored'][i]))<mp.mpf('1e-55'))
rl,ru=map(F,thr['unpolarized_ratio']['interval_rational']);check('restoration_ratio_strict_between_zero_one',0<rl<ru<1)
# Keep the original exact receiver gas box and thermal threshold.
nl,nu=map(F,p22['nH_box']);g0=list(map(F,p22['gas_initial_exact']));rad=list(map(F,p22['gas_radii']));f=F(3,38);h=F(10**11)
xlo,xhi=g0[0]-rad[0],g0[0]+rad[0];ql=nl*(1-xhi)**2*kl;qu=nu*(1-xlo)**2*ku
geL=F('0.9657383453960767');geU=F('1.0342616546039233');gtL=F('70796.35234679');gtU=F('72894.51840866')
ch=F('13.598434599702');oldqU=F(p22['qHH_box'][1]);oldpic=list(map(F,p22['tube_picard_upper']))
newpic=[oldpic[i]+h*abs(v)*max(F(0),qu-oldqU) for i,v in enumerate([1,0,0,-ch])]
check('truncated_source_common_tube_closes',all(a<b for a,b in zip(newpic,rad)))
check('truncated_rate_below_parent_tube_ceiling',ku<F(p23['common_tube_k_upper_ceiling_cm3_s']))
eI=(geL*h*ql,geU*h*qu);tI=(-gtU*h*qu,-gtL*h*ql)
sT=F('6.6524587051e-25');cc=F(29979245800)
tauI=(cc*sT*nl*geL*ql*h*h/2,cc*sT*nu*geU*qu*h*h/2)
e0lo=g0[0]+f*(g0[1]+2*g0[2])-rad[0]-f*(rad[1]+2*rad[2]);e0hi=g0[0]+f*(g0[1]+2*g0[2])+rad[0]+f*(rad[1]+2*rad[2]);relI=(eI[0]/e0hi,eI[1]/e0lo)
check('truncated_diagnostic_positive_electron_negative_temperature',eI[0]>0 and tI[1]<0)
check('truncated_relative_source_exceeds_64eps_lower',relI[0]>F(64,2**52))
# Source-model output table; no experimental-data label.
rows=[]
for e in ['1','1.01','1.05','1.1','1.2','1.25','1.5','1.75','2']:
 v=[mp.mpf(e),mp.mpf(e)*mp.mpf(M.I_RY_EV),2*mp.mpf(e)*mp.mpf(M.I_RY_EV)]+[M.sigma_tag_a02(e,s) for s in ['singlet','triplet','unpolarized']]
 rows.append([mp.nstr(x,22) for x in v]+[mp.nstr(v[-1]*(100*mp.mpf(M.A0_M))**2,22)])
with (D/'results/S65_SOURCE_CROSS_SECTIONS.csv').open('w') as o:
 w=csv.writer(o);w.writerow(['E_CM_over_I_Ry','E_CM_eV','E_lab_eV','sigma_singlet_a02','sigma_triplet_a02','sigma_unpolarized_a02','sigma_unpolarized_cm2']);w.writerows(rows)
res={'unit':'PHYS25','decision':'ADOPT_SOURCE_RECONSTRUCTION_AND_RESTORED_DIRECT_MODEL_THRESHOLD','physical_calibration':'unresolved; model-scope correction is derived, not an empirical envelope','source_model':'Sheldon1965 NASA TN D-3134 Eqs2-18','source_pdf_sha256':'61d91628383e2d4932592ba5dedc32381fb36a2f63ee99cdaae430f9c86d5a9f','scope_energy_CM_over_Ry':[1,2],'normalization':'tagged product-state single-electron channel; explicit symmetric exclusive-branch adapter sigma_event=2sigma_tag and k=<sigma_tag v>','source_threshold_eV':M.I_RY_EV,'receiver_thermal_threshold_eV':M.I_RECEIVER_EV,'Tbox_K':M.T_BOX,'mass_approximation_kg':M.M_H_KG,'partial_rate_cm3_s_interval_rational':rng([kl,ku]),'partial_rate_point_mp65':mp.nstr(kr,60),'partial_rate_to_LCS_full_point':mp.nstr(kr/lcs,35),'threshold_ratio_interval_rational':rng([rl,ru]),'threshold_relative_reduction_percent':mp.nstr((1-mp.mpf(wol['unpolarized_threshold_ratio']))*100,35),'threshold_ratio_is_not_used_as_finite_energy_correction':True,'tagged_threshold_limit':thr,'truncated_channel_diagnostic':{'definition':'Declare sigma_tag=source expression on [I_Ry,2I_Ry] and zero outside ONLY for this diagnostic. Physical tail remains separate. Reuse same exact P01 IC/background/source/closure and 4+2904 active variables.','q_s_interval_rational':rng([ql,qu]),'delta_e_perH_rational':rng(eI),'delta_T_K_rational':rng(tI),'delta_tau_rational':rng(tauI),'relative_rate_at_endpoint_rational':rng(relI),'ratio_to_64eps_reference':[float(x/F(64,2**52)) for x in relI],'max_common_tube_ratio':float(max(x/y for x,y in zip(newpic,rad)))},'tail_contract':{'full_rate':'k_total=k_near+k_tail','physical_tail_upper':None,'full_corrected_finite_momentum_rate':None},'physical_omission_budget':None,'new_ODE_runs':0,'new_native_receiver_runs':0,'new_ab_initio_scattering_runs':0,'atomic_model_integrals_executed':True,'external_review':False,'xAct_residuals':2,'scalar_CAS_residuals':15,'python_checks':len(checks)}
(D/'results/PHYS25_RESULT.json').write_text(json.dumps(res,indent=2)+'\n')
val.update({'passed':sum(c['pass'] for c in checks),'failed':sum(not c['pass'] for c in checks),'checks':checks,'scope':'Separate mpmath direct integrals/derivatives; exact Fraction state, response and saved-interval comparisons. Producer continuous enclosures separately certified by mpmath interval/E1-series mathematics.'})
(D/'checks/FINAL_VALIDATION.json').write_text(json.dumps(val,indent=2)+'\n')
for k in ['partial_rate_point_mp65','partial_rate_to_LCS_full_point','threshold_relative_reduction_percent']:print(k,res[k])
for k,v in res['truncated_channel_diagnostic'].items():
 if k.endswith('_rational'):print(k,[float(F(x)) for x in v])
 else:print(k,v)
print('CHECKS',val['passed'],val['failed'])
