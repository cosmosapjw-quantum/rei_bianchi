"""Exact label projection retaining source-native state qualifications."""
import hashlib
import json
from pathlib import Path

TARGETS=(('H1',1,1),('D',1,2),('T',1,3),('He3',2,3),('He4',2,4),('Li6',3,6),('Li7',3,7))
EXPECTED_WU_LABELS=('n:0',)+tuple(name+':'+str(q) for name,Z,A in TARGETS for q in range(Z+1))


def _key(record):
    return (tuple(sorted((c['Z'],c['A'],c['isomer'],c['count']) for c in record['composition'])),record['charge'],record['pool'])


class Projection:
    def __init__(self, source_dir):
        source_dir=Path(source_dir)
        manifest=json.loads((source_dir/'INPUT_MANIFEST.json').read_text())
        inputs={};refs={}
        for row in manifest['inputs']:
            data=(source_dir/row['file']).read_bytes()
            if len(data)!=row['bytes'] or hashlib.sha256(data).hexdigest()!=row['sha256']:
                raise ValueError('IMMUTABLE_INPUT_BYTE_IDENTITY_MISMATCH')
            name=Path(row['file']).name;inputs[name]=json.loads(data);refs[name]=row
        wu=inputs['WU_SPECIES.json'];he=inputs['HE_SPECIES_REGISTRY.json'];rec=inputs['REC_ATOMIC_MODEL.json']
        admission=inputs['WU_R1_ADMISSION.json']
        if admission['reviewed_core_output_sha256']['registry/species.json']!=refs['WU_SPECIES.json']['sha256']:
            raise ValueError('WU_SPECIES_ADMISSION_IDENTITY_MISMATCH')
        if tuple(row['label'] for row in wu['historical_view'])!=EXPECTED_WU_LABELS:
            raise ValueError('HISTORICAL_LABEL_ORDER_MISMATCH')
        self.he={row['supplier_species_id']:row for row in he['species']}
        if len(self.he)!=len(he['species']):raise ValueError('DUPLICATE_HE_ID')
        material={}
        for row in he['species']:
            if row['pool']=='material' and not row['synthetic_extension']:
                key=_key(row)
                if key in material:raise ValueError('AMBIGUOUS_MATERIAL_COMPOSITION')
                material[key]=row
        rows=[];historical_ids=set();rec_indices=[]
        for order,item in enumerate(wu['historical_view']):
            identifier=item['species_id'];native=wu['rows'][identifier];record=native['compiler_record']
            if identifier in historical_ids:raise ValueError('DUPLICATE_WU_ID')
            historical_ids.add(identifier)
            label=item['label'];name,charge=label.split(':');charge=int(charge)
            nuclide=(0,1) if name=='n' else next(((Z,A) for target,Z,A in TARGETS if target==name),None)
            expected={'composition':[{'Z':nuclide[0],'A':nuclide[1],'isomer':'ground','count':1}],'charge':charge,'pool':'material'}
            if _key(record)!=_key(expected):raise ValueError('HISTORICAL_NUCLIDE_CHARGE_MISMATCH')
            target=material.get(_key(record))
            if target is None:raise ValueError('MISSING_HE_MATERIAL_PROJECTION')
            cross=target['rec_population_crosswalk'];index=cross['index'];rec_indices.append(index)
            if rec['species_order'][index]!=cross['label']:raise ValueError('REC_LABEL_INDEX_MISMATCH')
            if record['state'] not in ('population_aggregate_unresolved','bare_nucleus'):
                raise ValueError('UNEXPECTED_WU_HISTORICAL_STATE')
            rows.append({'wu_label':label,'wu_id':identifier,'nuclide':{'Z':nuclide[0],'A':nuclide[1]},
              'charge':charge,'pool':'material','wu_state':record['state'],'he_state':target['state'],
              'he_label':target['supplier_species_id'],'rec_label':cross['label'],'rec_index':index,
              'identity_relation':'NUCLEUS_CHARGE_PROJECTION_ONLY','state_equivalence':False,
              'physical_state_partition':None,'source_qualification':native['qualification'],
              'source_reference':dict(refs['WU_SPECIES.json'],json_pointer='/rows/'+identifier)})
        if len(material)!=21 or sorted(rec_indices)!=list(range(21)):
            raise ValueError('NONBIJECTIVE_21_STATE_PROJECTION')
        self.rows=rows
        self.labels={'wu':tuple(r['wu_label'] for r in rows),
                     'he':tuple(r['he_label'] for r in rows),
                     'rec':tuple(rec['species_order'])}
        self.ids={view:{label:rows[index]['wu_id'] for index,label in enumerate(labels)} for view,labels in self.labels.items() if view!='rec'}
        self.ids['rec']={r['rec_label']:r['wu_id'] for r in rows}
        extensions=[dict(native,source_reference=dict(refs['WU_SPECIES.json'],json_pointer='/rows/'+identifier),
                         consumer_admission='UNADMITTED',active=False,rate=None)
                    for identifier,native in wu['rows'].items() if identifier not in historical_ids]
        if len(wu['rows'])!=92 or len(extensions)!=71:raise ValueError('WU_INVENTORY_COUNT_MISMATCH')
        self.payload={'unit_id':'REI-WU-SPECIES-CONSUMER-PROJECTION-01','historical21':rows,
          'atomic_targets':[{'name':name,'Z':Z,'A':A} for name,Z,A in TARGETS],
          'atomic_charge_states':20,'neutron_material_states':1,'extensions':extensions,
          'synthetic_HE_witnesses':[r for r in he['species'] if r['synthetic_extension']],
          'non_synthetic_HE_rows':[r for r in he['species'] if not r['synthetic_extension']],
          'physical_provider_admitted':False,'full_differential_provider_count':he['summary']['source_qualified_full_differential_providers'],
          'REC_state_convention':rec['state_convention'],'isotope_rate_policy':rec['isotope_rate_policy'],
          'automatic_normalization_conversion':False,'electron_pools_interchangeable':False,
          'state_partition_map':None,'numeric_rates_admitted':False,'WU_aggregation_policy':wu['aggregation']}
        if self.payload['full_differential_provider_count']!=0 or he['physical_provider_admitted'] is not False:
            raise ValueError('UNCONTRACTED_DIFFERENTIAL_ADMISSION_CHANGE')

    def reorder(self,values,input_labels,from_view,to_view,normalization,*,target_normalization=None):
        if not normalization or target_normalization not in (None,normalization):
            raise ValueError('EXPLICIT_NORMALIZATION_REQUIRED_NO_AUTOMATIC_CONVERSION')
        if from_view not in self.ids or to_view not in self.ids:raise ValueError('UNKNOWN_VIEW')
        labels=tuple(input_labels);values=tuple(values)
        if len(labels)!=21 or len(values)!=21 or len(set(labels))!=21 or set(labels)!=set(self.ids[from_view]):
            raise ValueError('MISSING_DUPLICATE_OR_UNKNOWN_LABEL')
        supplied={self.ids[from_view][label]:value for label,value in zip(labels,values)}
        return tuple(supplied[self.ids[to_view][label]] for label in self.labels[to_view])

    def require_identity(self,wu_id,he_label,*,full_state=False):
        matches=[r for r in self.rows if r['wu_id']==wu_id and r['he_label']==he_label]
        if len(matches)!=1:raise ValueError('NUCLIDE_CHARGE_OR_POOL_IDENTITY_MISMATCH')
        if full_state:raise ValueError('SOURCE_STATE_PARTITION_MAP_REQUIRED')
        return matches[0]['identity_relation']

    def require_same_pool(self,left,right):
        if left not in self.he or right not in self.he:raise ValueError('UNKNOWN_HE_SOURCE_ID')
        if self.he[left]['pool']!=self.he[right]['pool']:raise ValueError('ELECTRON_OR_MATERIAL_POOL_MISMATCH')
        return self.he[left]['pool']

    def pair_support(self,left,right):
        if left not in self.he or right not in self.he:raise ValueError('UNKNOWN_HE_SOURCE_ID')
        records=(self.he[left],self.he[right]);synthetic=any(r['synthetic_extension'] for r in records)
        return {'left':left,'right':right,'status':'UNADMITTED_SYNTHETIC_WITNESS' if synthetic else 'INPUT_PENDING',
          'rate':None,'physical_provider_admitted':False,'full_joint_law':None,
          'source_differential_status':[r['differential_exchange_status'] for r in records],
          'scalar_provider_candidates':[r['scalar_provider_ids'] for r in records]}
