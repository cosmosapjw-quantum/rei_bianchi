"""Independent frozen EE/Wolfram and native BED scalar anchors, no integral."""
import json
import math
from stopping_components import ee_coefficients,ee_flux,bed_sdcs_m2_per_eV,bed_total_support,paired_event,B_NATIVE


def run_tests(contract_path):
    contract=json.loads(contract_path.read_text());ee=contract['EE'];bed=contract['BED'];tol=contract['tests']
    T=ee['T_K'];ne=ee['n_e_thermal_m3'];log=ee['lnLambda'];checks=[]
    ee_errors=[];coefficients=[]
    for reference in ee['references']:
        value=ee_coefficients(reference['E_eV'],T,ne,log);coefficients.append({'E_eV':reference['E_eV'],**value})
        ee_errors.extend(abs(value[key]/reference[key]-1) for key in ('A_eV_s','D_eV2_s'))
    checks.append({'name':'four_EE_independent_high_precision_anchors','pass':max(ee_errors)<=tol['EE_high_precision_relative'],'max_relative':max(ee_errors)})
    a=T/10000.;beta=(ne*log/(140000.*20.))*a**(-1.5);dilation=[]
    for E0 in (1.,10.):
        old=ee_coefficients(E0,10000.,140000.,20.);new=ee_coefficients(a*E0,T,ne,log)
        dilation.extend((abs(new['A_eV_s']/(beta*a*old['A_eV_s'])-1),abs(new['D_eV2_s']/(beta*a*a*old['D_eV2_s'])-1)))
    checks.append({'name':'exact_EE_temperature_density_dilation','pass':max(dilation)<=tol['EE_dilation_relative'] and abs(beta/ee['formula']['generator_scale_fixed_log20']-1)<=tol['EE_dilation_relative'],'max_relative':max(dilation),'generator_scale':beta})
    flux_errors=[]
    for E in (.011,13.6):
        theta=ee_coefficients(E,T,ne,log)['theta_eV'];N=math.sqrt(E)*math.exp(-E/theta)
        Nprime=N*(1/(2*E)-1/theta);D=ee_coefficients(E,T,ne,log)['D_eV2_s']
        flux_errors.append(abs(ee_flux(E,T,ne,log,N,Nprime))/(D*abs(N)/theta))
    checks.append({'name':'Maxwell_zero_current','pass':max(flux_errors)<=tol['EE_zero_flux_scaled'],'max_scaled':max(flux_errors)})
    bed_values=[bed_sdcs_m2_per_eV(30.,W)*1e20 for W in bed['reference_W_eV']]
    strict=[abs(a/b-1) for a,b in zip(bed_values,bed['reference_Wolfram_printed_parameter_A2_per_eV'])]
    native=[abs(a/b-1) for a,b in zip(bed_values,bed['reference_nist_printed_A2_per_eV'])]
    checks.append({'name':'ten_BED_independent_displayed_parameter_anchors','pass':max(strict)<=tol['BED_high_precision_relative'],'max_relative':max(strict)})
    checks.append({'name':'ten_BED_native_rounded_transcription_anchors','pass':max(native)<=tol['BED_native_printed_relative'],'max_relative':max(native),'accuracy_scope':'rounded native source consistency only'})
    pairs=[];energy_residual=[]
    for E,W in ((30.,0.),(30.,8.19715),(150.,20.)):
        event=paired_event(E,W);pairs.append({'E_eV':E,'W_eV':W,**event})
        energy_residual.append(abs(E-sum(event['output_energies_eV'])-event['binding_gain_eV']))
    integer_ok=all(len(p['output_energies_eV'])-1==p['number_delta']==1 and p['HI_delta']+p['HII_delta']==0 and p['HII_delta']+p['fast_electron_charge_delta']==0 and p['extra_factor_2'] is False and p['thermal_heat'] is None and p['old_network_activation'] is False for p in pairs)
    checks.append({'name':'three_paired_number_charge_energy_ledgers','pass':max(energy_residual)<=tol['paired_energy_absolute_eV'] and integer_ok,'max_energy_absolute_eV':max(energy_residual)})
    bad=[]
    def rejects(fn):
        try:fn()
        except ValueError:return True
        return False
    for function in (lambda:paired_event(30,1,ledger_binding_eV=13.6),lambda:paired_event(30,1,pair_factor=2),lambda:bed_sdcs_m2_per_eV(151,0),lambda:bed_sdcs_m2_per_eV(30,9),lambda:bed_sdcs_m2_per_eV(30,-1),lambda:ee_coefficients(.01,T,ne,log),lambda:ee_coefficients(151,T,ne,log),lambda:ee_coefficients(1,-T,ne,log),lambda:ee_coefficients(1,T,-ne,log),lambda:ee_coefficients(1,T,ne,-log),lambda:ee_coefficients(math.nan,T,ne,log)):
        bad.append(rejects(function))
    checks.append({'name':'binding_factor_support_and_parameter_negative_guards','pass':all(bad),'controls':bad})
    low=coefficients[0];cold=-low['b0_eV_s'];drop_ne=ee_coefficients(.011,T,1.,log)['A_eV_s'];wrong_cgs=ee_coefficients(.011,T,ne/1e6,log)['A_eV_s']
    checks.append({'name':'warm_drift_and_absolute_density_discriminating_controls','pass':cold<0<low['A_eV_s'] and abs(drop_ne/low['A_eV_s']-1)>tol['EE_high_precision_relative'] and abs(wrong_cgs/low['A_eV_s']-1)>tol['EE_high_precision_relative']})
    checks.append({'name':'native_threshold_zero_width_total_channel','pass':bed_total_support(B_NATIVE)['zero_total_channel'] is True and bed_total_support(13.)['zero_total_channel'] is True and rejects(lambda:paired_event(B_NATIVE,0.)) and bed_sdcs_m2_per_eV(B_NATIVE,0.)>=0})
    payload={'unit_id':contract['unit_id'],'EE_anchor_results':coefficients,'BED_T30_A2_per_eV':bed_values,
      'paired_events':pairs,'EE_dilation':{'old_T_K':10000.,'old_ne_m3':140000.,'old_lnLambda':20.,'temperature_scale':a,'generator_scale':beta},
      'native_binding_eV':B_NATIVE,'old_network_binding_eV':13.6,'old_network_activation':False,
      'full_stopping':'PARTIAL_INPUT_DEPENDENCIES','thermal_heat':None,'source_atom_scans':0,'integrations':0}
    return checks,payload
