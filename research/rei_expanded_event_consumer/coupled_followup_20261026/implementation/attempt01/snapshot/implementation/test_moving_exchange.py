"""Seven changed-boundary groups from independent rational references."""
import json
import sys
from moving_exchange import finite_volume_exchange,electron_thermal_cutoff,tag_native_bed_pair


def close(a,b):return abs(a-b)<=2e-13*max(1.,abs(b))
def conserved(terms):
    scale=sum(abs(v) for v in terms)
    return sum(terms)==0 if scale==0 else abs(sum(terms))<=64*sys.float_info.epsilon*scale


def run_tests(contract_path):
    contract=json.loads(contract_path.read_text());fixture=contract['finite_volume_exchange']['fixture'];checks=[]
    exchange=finite_volume_exchange(fixture['centres'],fixture['counts'],fixture['centre_velocities'],fixture['edge_fluxes'],fixture['cutoff'])
    reference=all(close(exchange[key],fixture[key]) for key in ('Phi','resolved_Udot','same_current_moment','reservoir_Udot'))
    checks.append({'name':'moving_three_cell_rational_reference_and_same_flux_conservation',
      'pass':reference and tuple(fixture['count_rhs'])==exchange['count_rhs'] and conserved(exchange['count_rhs']+(exchange['reservoir_Ndot'],)) and conserved((exchange['resolved_Udot'],exchange['reservoir_Udot'])),
      'exchange':exchange})
    omit_mesh=exchange['resolved_Udot']-exchange['mesh_work']+exchange['reservoir_Udot']
    omit_moment=exchange['resolved_Udot']+fixture['cutoff']*exchange['Phi']
    checks.append({'name':'omitted_mesh_work_and_same_current_moment_controls',
      'pass':close(abs(omit_mesh),fixture['omitted_mesh_work_defect']) and not close(omit_mesh,0.) and close(omit_moment,exchange['same_current_moment']) and not close(omit_moment,0.)})
    thermal=electron_thermal_cutoff(1.,2.,10.,1.,3.,4.)
    coupled=electron_thermal_cutoff(1.,2.,10.,1.,3.,4.,I_theta_dot=2.)
    thermal_checks=[]
    for result,Ceff,td,Phi,U in ((thermal,14.,-11/28,-53/14,-81/7),(coupled,16.,-11/32,-59/16,-171/16)):
        thermal_checks.extend(close(result[key],target) for key,target in (('Ceff',Ceff),('theta_dot',td),('Phi',Phi),('reservoir_Udot',U)))
        thermal_checks.append(conserved((result['C']*result['theta_dot'],result['mean_thermal_energy']*result['Phi'],-result['reservoir_Udot'])))
    checks.append({'name':'implicit_thermal_Schur_rational_and_caloric_identities','pass':all(thermal_checks),'zero_mesh_coupling':thermal,'nonzero_mesh_coupling':coupled})
    def rejects(function):
        try:function()
        except (ValueError,TypeError):return True
        return False
    capacity=(rejects(lambda:electron_thermal_cutoff(1,2,2/3,1,3,4)),rejects(lambda:electron_thermal_cutoff(1,2,.5,1,3,4)),rejects(lambda:electron_thermal_cutoff(1,2,10,1,3,4,I_theta_dot=-14)))
    checks.append({'name':'zero_and_negative_effective_capacity_guards','pass':all(capacity)})
    tagged=tag_native_bed_pair(30.,0.,input_kind='NATIVE_BED_KINETIC_eV')
    tag_fixture=contract['tag_native_bed_pair']['fixture']
    checks.append({'name':'native_BED_tagged_pair_and_recovered_physical_energies',
      'pass':close(tagged['xi_input'],tag_fixture['xi_input']) and all(close(a,b) for a,b in zip(tagged['xi_outputs'],tag_fixture['xi_outputs'])) and close(tagged['true_kinetic_outputs'][0],0.) and close(tagged['true_kinetic_outputs'][1],30.-13.6057) and conserved((tagged['xi_input'],-sum(tagged['xi_outputs']),-13.6)) and tagged['old_source_activation'] is False and tagged['physical_source_remap_admitted'] is False,
      'tagged_pair':tagged})
    delta=tagged['delta'];shifted=finite_volume_exchange(tuple(v+delta for v in fixture['centres']),fixture['counts'],fixture['centre_velocities'],fixture['edge_fluxes'],fixture['cutoff']+delta)
    physical_out=(0.,30.-13.6057,13.6057);charges=(-1,-1,1)
    transformed=tuple(E-delta*q for E,q in zip(physical_out,charges))
    gauge=[close(sum(transformed)-sum(physical_out),delta),close(sum(transformed),tagged['xi_input']),
      close(shifted['same_current_moment'],exchange['same_current_moment']),
      close(shifted['resolved_Udot'],exchange['resolved_Udot']-delta*exchange['Phi']),
      close(shifted['reservoir_Udot'],exchange['reservoir_Udot']+delta*exchange['Phi']),
      close(shifted['reservoir_Udot']-delta*shifted['Phi'],exchange['reservoir_Udot']),
      close(thermal['C']-2*((thermal['cutoff']+delta)-(thermal['mean_thermal_energy']+delta)),thermal['Ceff'])]
    checks.append({'name':'all_charge_energy_gauge_and_moving_cutoff_covariance','pass':all(gauge)})
    guards=[rejects(lambda:finite_volume_exchange([2,4,7],[5,6,7],[.1,.2,.3],[-2,3,-1,1],1)),
      rejects(lambda:finite_volume_exchange([2,2],[1,1],[0,0],[0,0,0],1)),
      rejects(lambda:finite_volume_exchange([2],[-1],[0],[0,0],1)),
      rejects(lambda:electron_thermal_cutoff(0,2,10,1,3,4)),
      rejects(lambda:electron_thermal_cutoff(1,2,10,-1,3,4)),
      rejects(lambda:tag_native_bed_pair(30,0,input_kind='CHARGE_GAUGE_TAGGED_ENERGY_eV')),
      rejects(lambda:tag_native_bed_pair(30,0,input_kind='LEGACY_PHYSICAL_SOURCE_KINETIC_eV')),
      rejects(lambda:tag_native_bed_pair(30,0,input_kind=None)),
      rejects(lambda:tag_native_bed_pair(30,0)),
      rejects(lambda:tag_native_bed_pair(13.6057,0,input_kind='NATIVE_BED_KINETIC_eV')),
      rejects(lambda:tag_native_bed_pair(30,9,input_kind='NATIVE_BED_KINETIC_eV'))]
    checks.append({'name':'closed_upper_boundary_domain_and_input_semantics_guards','pass':all(guards),'controls_passed':len(guards)})
    return checks
