#!/usr/bin/env python3
"""Assemble metadata from frozen PHYS24 evidence; execute no science."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]


def identity(path):
    p=ROOT/path
    return {'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}


def main():
    contract=json.loads((ROOT/'PHYSICS_CONTRACT.json').read_text())
    exact=json.loads((ROOT/'contributions/curvature/CURVATURE_CERTIFICATE.json').read_text())
    num=json.loads((ROOT/'contributions/numerics/MOMENT_ENVELOPE.json').read_text())
    claims=[
      {'id':'C24.1','statement':'At fixed numerical J the actual HeIII scalar kernel is strictly convex on I, has opposite endpoint signs and exactly one interior zero.',
       'evidence_state':['derived','implementation-verified'],
       'evidence':['contributions/curvature/CURVATURE_DERIVATION_KO.md','contributions/curvature/CURVATURE_CERTIFICATE.json','contributions/curvature/EXECUTION.json'],
       'conditions':['Exact-real source binary64 literals','Serialized numerical J decimals interpreted as exact rationals','I=[13.61,24.58] eV, fixed initial gas'],
       'limits':['J input uncertainty not enclosed','not native arithmetic equivalence','not a proof-assistant kernel certificate']},
      {'id':'C24.2','statement':'The exact fixed-mass/fixed-mean response set is [k(mean), endpoint_chord(mean)]; its interior-mean minimizer and maximizer are unique mono and endpoint laws.',
       'evidence_state':['derived'],
       'evidence':['contributions/moments/MOMENT_EXTREMIZERS_KO.md','PHYS24_REPORT_KO.md sections 4–6'],
       'depends_on':['C24.1'],
       'conditions':['Finite nonnegative Borel photon-number measures; delta lines allowed','Positive fixed q and N0'],
       'limits':['Not additional spectral regularity or variance constraints']},
      {'id':'C24.3','statement':'Every response in the interval can be achieved by at most two spectral lines; the left-endpoint path is continuous and strictly increasing at interior means.',
       'evidence_state':['derived'],
       'evidence':['contributions/moments/MOMENT_EXTREMIZERS_KO.md section 3.1','PHYS24_REPORT_KO.md equation 20'],
       'depends_on':['C24.1','C24.2'],
       'limits':['Uniqueness along that path does not imply global uniqueness of all spectral representations']},
      {'id':'C24.4','statement':'Five mean-energy sign regions follow exactly from the kernel and chord zeros: positive; nonnegative boundary; both signs; nonpositive boundary; negative.',
       'evidence_state':['derived','numerically checked'],
       'evidence':['PHYS24_REPORT_KO.md sections 1 and 7','contributions/numerics/MOMENT_ENVELOPE.json','contributions/moments/MOMENT_EXTREMIZERS_KO.md section 4'],
       'depends_on':['C24.1','C24.2'],
       'numerical_boundaries_eV':{'E_minus':num['mono_zero_inherited']['midpoint_eV'],'E_plus':num['endpoint_chord_zero']['mean_eV']},
       'limits':['Boundary definitions exact, displayed decimals numerical','Numerical brackets are not rigorous input-error enclosures','Zero t4 coefficient leaves next time order unresolved']},
      {'id':'C24.5','statement':'Original-fit Taylor jets and a separate direct finite-difference path agree on seven new curvature samples; fixed-moment examples and one PHYS23 anchor are consistent with the proved interval.',
       'evidence_state':['numerically checked','implementation-verified'],
       'evidence':['contributions/numerics/moment_envelope.py','contributions/numerics/MOMENT_ENVELOPE.json','contributions/numerics/EXECUTION.json','contributions/numerics/INDEPENDENCE_ACTUAL.json'],
       'limits':['Finite numerical samples are not continuum proof','Method design independent, execution nonblind to a success summary','156 assertions are not independent physical laws']}
    ]
    result={
      'task':contract['task'],'title':'FIXED_MOMENT_HEIII_ENVELOPE',
      'decision_authority':'independent/DECISION_REVIEW.json; this frozen summary does not self-promote',
      'owner_self_promotion':False,
      'contract':identity('PHYSICS_CONTRACT.json'),'source_manifest':identity('SOURCE_MANIFEST.json'),
      'report':identity('PHYS24_REPORT_KO.md'),'handoff':identity('PHYS25_NEXT_HANDOFF_KO.md'),
      'input_commit':contract['input_commit'],'input_tree':contract['input_tree'],
      'scientific_src_tree':contract['scientific_src_tree'],
      'definitions':{'I_eV':['13.61','24.58'],'mean':'U0/N0','probability':'dP=dnu0/N0',
                     'F2':'half second epsilon derivative; t4 has no extra factorial',
                     'g':'(Jx C lambda+Jw C[lambda(E)(E-chi)])/4','k':'q N0 g/45',
                     'a4':'integral k dP','g_unit':'s^-2','k_a4_unit':'s^-4',
                     'minimum':'k(mean)','maximum':'[(b-mean)k(a)+(mean-a)k(b)]/(b-a)',
                     'minimizer':'delta_mean','maximizer':'[(b-mean)/(b-a)]delta_a+[(mean-a)/(b-a)]delta_b',
                     'E_minus':'unique zero of k','E_plus':'a+(b-a)k(a)/(k(a)-k(b))'},
      'claims':claims,
      'exact_certificate':{'path':'contributions/curvature/CURVATURE_CERTIFICATE.json',
                           **identity('contributions/curvature/CURVATURE_CERTIFICATE.json'),
                           'passed':exact['pass_count'],'total':exact['check_count'],
                           'curvature_degree':14,'positive_Bernstein_coefficients':15,
                           'curvature_intervals':1,'subdivisions_used':0,
                           'endpoint_polynomial_degrees':[8,8],'endpoint_strict_sign_counts':[9,9],
                           'conclusions':exact['certified_conclusions']},
      'numerical_validation':{'path':'contributions/numerics/MOMENT_ENVELOPE.json',
                              **identity('contributions/numerics/MOMENT_ENVELOPE.json'),
                              'decimal_precision':num['decimal_precision'],'summary':num['summary'],
                              'FD_relative_tolerance':'1e-42','algebra_scaled_tolerance':'1e-130',
                              'inherited_anchor_scaled_tolerance':'1e-95',
                              'FD_method':'Original fit, 13-point log-energy stencil, h=1e-5 and h/2; Richardson 1024',
                              'comparison_method':'Original-fit Taylor jets through derivative order4',
                              'independence_actual':'Design fixed independently before other contributor success summary; execution nonblind to summary, no code/derivation/raw result read.'},
      'endpoint_coefficients':{x:{'energy_eV':v['energy_eV'],'k_s-4':v['k_s-4'],'g_s-2':v['g_s-2']} for x,v in num['endpoint_values'].items()},
      'E_minus':num['mono_zero_inherited'],'E_plus':num['endpoint_chord_zero'],
      'envelope_samples':num['envelope_samples'],
      'sign_partition':num['sign_partition_conditional_on_continuum_convexity'],
      'sign_partition_condition_discharged_by':'C24.1 exact curvature/endpoint theorem, with fixed numerical J ceiling retained',
      'single_inherited_anchor':num['single_inherited_anchor'],
      'new_same_mean_internal_laws':num['additional_moment_laws'],
      'zero_response_mixture_at_mean18':num['full_interval_attainability_samples'][-1],
      'evidence_scope':{'literature':'evidence/LITERATURE_SCOPE.json',
                        'actual_independence':'contributions/numerics/INDEPENDENCE_ACTUAL.json',
                        'format_correction':'contributions/numerics/FORMAT_CORRECTION.json',
                        'scientific_failures':0,'scientific_corrections':0,'tolerance_changes':0,
                        'documentation_format_correction':1},
      'execution_before_portability':{'new_exact_main':1,'new_numerical_main':1,
                                      'native':0,'gas_IVP':0,'closed_PHYS19_to_PHYS23_main_replays':0,
                                      'new_iterative_root_searches':0,'figure_main':1,'figure_display_points':241,
                                      'figure_independent_validation_credit':0},
      'protected':contract['protected'],'physical':'HOLD',
      'next_task':{'name':'PHYS25_HEIII_SIGN_REVERSAL_VARIANCE_COST','status':'PLANNED_NOT_EXECUTED',
                   'question':'At mean18 eV, what is the minimum photon-energy variance permitting nonnegative HeIII initial t4 response?',
                   'handoff':'PHYS25_NEXT_HANDOFF_KO.md'},
      'limits':contract['claim_ceiling']+['No variance-optimality claim for the two-line zero-response path'],
    }
    (ROOT/'RESULTS_SUMMARY.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    nodes=[{'id':'INPUT_SOURCE','kind':'source','state':'established identity only','path':'SOURCE_MANIFEST.json'},
           {'id':'INPUT_J','kind':'numeric input','state':'inherited numerically checked','path':'inputs/PHYS22_INITIAL_COEFFICIENTS.json'},
           {'id':'INHERITED_FUNCTIONAL','kind':'theory input','state':'inherited established within PHYS22 scope','path':'inputs/inherited/PHYS23_REPORT_KO.md'},
           {'id':'GENERAL_MOMENTS','kind':'derived theorem','state':'derived','path':'contributions/moments/MOMENT_EXTREMIZERS_KO.md'}]
    nodes += [{'id':x['id'],'kind':'claim','statement':x['statement'],'evidence_state':x['evidence_state'],
               'evidence':x['evidence'],'decision_authority':'independent/DECISION_REVIEW.json'} for x in claims]
    nodes += [{'id':'PHYSICAL','kind':'admission','state':'HOLD','blockers':'Inherited physical gates and unbounded finite-time/native/J uncertainty'},
              {'id':'PHYS25','kind':'successor','state':'PLANNED_NOT_EXECUTED','path':'PHYS25_NEXT_HANDOFF_KO.md'}]
    edges=[]
    def edge(a,b,rel='supports'):edges.append({'from':a,'to':b,'relation':rel})
    for a in ['INPUT_SOURCE','INPUT_J','INHERITED_FUNCTIONAL']:edge(a,'C24.1')
    edge('INPUT_J','PHYSICAL','limits');edge('GENERAL_MOMENTS','C24.2');edge('GENERAL_MOMENTS','C24.3')
    for c in claims:
        for parent in c.get('depends_on',[]):edge(parent,c['id'])
    edge('C24.5','C24.1','corroborates finite points only');edge('C24.5','C24.4','supports numerical values')
    edge('C24.2','PHYS25','motivates');edge('C24.4','PHYS25','motivates');edge('C24.3','PHYS25','limits: response feasibility is not variance optimality')
    dag={'task':contract['task'],'nodes':nodes,'edges':edges,'protected':contract['protected'],
         'owner_self_promotion':False,'final_decision':'independent/DECISION_REVIEW.json'}
    (ROOT/'CLAIM_DAG.json').write_text(json.dumps(dag,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'summary':identity('RESULTS_SUMMARY.json'),'dag':identity('CLAIM_DAG.json'),'science_executed':False}))


if __name__=='__main__':
    main()
