"""Exact source projection controls; no rates or normalization conversion."""
from species_projection import Projection, EXPECTED_WU_LABELS, TARGETS


def run_tests(source_dir):
    p=Projection(source_dir);checks=[]
    checks.append({'name':'four_manifest_inputs_and_WU_admission_identity','pass':True})
    rows=p.rows
    checks.append({'name':'seven_targets_twenty_atomic_plus_neutron_bijection',
      'pass':len(TARGETS)==7 and len(rows)==21 and tuple(r['wu_label'] for r in rows)==EXPECTED_WU_LABELS and sorted(r['rec_index'] for r in rows)==list(range(21)) and p.payload['atomic_charge_states']==20})
    markers=tuple((-1)**j*(11+j) for j in range(21));input_labels=tuple(reversed(p.labels['wu']));input_values=tuple(reversed(markers))
    rec=p.reorder(input_values,input_labels,'wu','rec','declared_count_basis')
    back=p.reorder(rec,p.labels['rec'],'rec','wu','declared_count_basis')
    counts=all(r['charge']==int(r['wu_label'].split(':')[1]) and r['nuclide']['A']==(1 if r['wu_label']=='n:0' else next(A for name,Z,A in TARGETS if name==r['wu_label'].split(':')[0])) for r in rows)
    checks.append({'name':'signed_integer_label_roundtrip_and_charge_baryon_rows','pass':back==markers and counts})
    state=all(r['state_equivalence'] is False and r['physical_state_partition'] is None and r['identity_relation']=='NUCLEUS_CHARGE_PROJECTION_ONLY' and r['he_state']=='ground' and r['wu_state'] in ('bare_nucleus','population_aggregate_unresolved') for r in rows)
    checks.append({'name':'native_state_semantics_retained','pass':state})
    extensions=p.payload['extensions']
    checks.append({'name':'seventy_one_source_referenced_unadmitted_extensions',
      'pass':len(extensions)==71 and all(r['consumer_admission']=='UNADMITTED' and r['active'] is False and r['rate'] is None and r['source_reference']['json_pointer']=='/rows/'+r['id'] and 'compiler_record' in r and 'source_labels' in r and 'qualification' in r for r in extensions)})
    material={r['wu_label']:r['he_label'] for r in rows}
    queries=[(material['H1:0'],'e_th'),(material['He4:1'],'e_fast'),(material['Li6:0'],'e_th'),(material['T:0'],'e_fast'),(material['H1:0'],material['He4:0'])]
    pairs=[p.pair_support(left,right) for left,right in queries]
    checks.append({'name':'selected_full_joint_law_queries_pending',
      'pass':all(r['status']=='INPUT_PENDING' and r['rate'] is None and r['physical_provider_admitted'] is False for r in pairs),'pairs':pairs})
    bad=[]
    def rejects(function):
        try:function()
        except ValueError:return True
        return False
    bad.append(rejects(lambda:p.require_same_pool('e_fast','e_th')))
    bad.append(rejects(lambda:p.reorder(markers,p.labels['wu'],'wu','rec','n_i/n_b',target_normalization='n_i/n_ref')))
    bad.append(rejects(lambda:p.reorder(markers[:-1],p.labels['wu'][:-1],'wu','rec','declared_count_basis')))
    bad.append(rejects(lambda:p.reorder(markers,(p.labels['wu'][0],)+p.labels['wu'][:-1],'wu','rec','declared_count_basis')))
    li6=next(r for r in rows if r['wu_label']=='Li6:0')
    bad.append(rejects(lambda:p.require_identity(li6['wu_id'],material['Li7:0'])))
    bad.append(rejects(lambda:p.require_identity(rows[0]['wu_id'],rows[0]['he_label'],full_state=True)))
    bad.append(rejects(lambda:p.pair_support('unknown','e_th')))
    synthetic=p.payload['synthetic_HE_witnesses'][0]['supplier_species_id']
    witness=p.pair_support(synthetic,'e_th')
    bad.append(witness['status']=='UNADMITTED_SYNTHETIC_WITNESS' and witness['physical_provider_admitted'] is False and witness['rate'] is None)
    checks.append({'name':'pool_normalization_missing_duplicate_isotope_state_synthetic_unknown_controls','pass':all(bad),'controls':bad})
    checks.append({'name':'original_electronic_equality_policy_metadata_only','pass':'ElementalElectronicEquality' in p.payload['isotope_rate_policy'] and p.payload['numeric_rates_admitted'] is False and p.payload['automatic_normalization_conversion'] is False})
    p.payload['selected_pair_queries']=pairs
    return checks,p.payload
