"""Synthetic receipt arithmetic only; no native execution is represented by fixtures."""
import copy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from fractions import Fraction as Q
import join as j


def reseal(obj,field='result_sha256'):
    obj[field]=j.digest({k:v for k,v in obj.items() if k!=field});return obj


def interval(lo='0',hi='0',exp='0'):
    return {'lower_mantissa':lo,'upper_mantissa':hi,'exponent2':exp}


def fixtures(context,index=0):
    plan=context.plan;task=plan['tasks'][index];manifest=context.manifest;limits=context.limits
    tail=j.endpoint._base_result(plan,index)
    tail.update(status='CONDITIONAL_TAIL_BOUND',endpoint_radius='1/8',engine_calls=2,
        terms=[{'i':0,'j':0,'k':0,'coefficient_abs':'1','field_majorant':'1',
                'complement_mass_bound':'1/8','contribution':'1/8'}])
    reseal(tail)
    native={'schema':'WU088_NATIVE_INTERIOR_RESULT_V1','status':'RADIUS_MET','accepted':True,'index':index,
        'task_sha256':task['task_sha256'],'plan_sha256':plan['plan_sha256'],
        'archive_sha256':manifest['archive_sha256'],'input_record_sha256':manifest['input_record_sha256'],
        'build_source_sha256':manifest['source']['sha256'],'precision_bits':limits['precision_bits'],
        'accepted_component_radius_exp':limits['radius_exp'],
        'rectangle':{'real':interval('3','3'),'imag':interval('4','4')},
        'dispatched_evaluations':1,'integration_calls':1,'analytic_box_refusals':0,'callback_calls':1,
        'callback_refusals':0,'flint_status':0,'endpoint_included':False,'normalization_applied':False,
        'full_domain_integral':False,'scientific_admission':False,'production_admission':False}
    native['wrapper']={'schema':'WU088_NATIVE_INTERIOR_WRAPPER_V1','build_manifest_sha256':manifest['manifest_sha256'],
        'native_limits':limits,'command':['/synthetic/primitive_worker',str(index),
            *[plan['window'][k] for k in ('l_t','T_t','l_u','T_u')],
            *[str(limits[k]) for k in ('precision_bits','radius_exp','relative_goal','max_evaluations',
                'max_integration_calls','wall_seconds','queued_panels','degree_limit')],task['task_sha256'],plan['plan_sha256']],
        'native_stdout_sha256':'b'*64,'native_execution_observed':True,'scope':'CONDITIONAL_COMPACT_INTERIOR_ONLY',
        'endpoint_plan_module_sha256':context.identity['module_hashes']['endpoint_tasks/planner.py'],
        'historical_abi_admission':False,'independent_scientific_review':False,
        'evidence_contract':'SOURCE_BOUND_NATIVE_OUTPUT_ASSUMED_NOT_INDEPENDENTLY_REPLAYED',
        'validation_level':'BYTE_IDENTITY_AND_REPORTED_RADIUS_ONLY'}
    return tail,reseal(native)


class JoinTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.path.insert(0,str(j.ROOT/'endpoint_tasks'))
        try:
            from test_endpoint_tasks import toy_record, WINDOW
            record,archive=toy_record()
        finally:sys.path.pop(0)
        plan=j.endpoint.build_plan(record,WINDOW,precision_bits=24,panels=1,source_archive_bytes=archive)
        manifest={'schema':'WU088_NATIVE_DRIVER_BUILD_V1','source':j.native.source_identity(),
            'archive_sha256':plan['archive_sha256'],'input_record_sha256':plan['input_record_sha256'],
            'binary_sha256':'a'*64,'backend_provenance_sha256':'c'*64}
        reseal(manifest,'manifest_sha256')
        cls.context=j.Context(plan,manifest,j.native.DEFAULT_LIMITS,source_archive_bytes=archive)
        cls.joined=[j.join_task(cls.context,*fixtures(cls.context,i)) for i in range(j.COUNT)]
        cls.coverage=j.collect(cls.context,reversed(cls.joined))

    def test_native_wrapper_contract_success_and_once_only_sum(self):
        result=self.joined[0]
        self.assertEqual(result['rectangle'],{'real':{'lo':'23/8','hi':'25/8'},'imag':{'lo':'31/8','hi':'33/8'}})
        self.assertEqual(result['endpoint_additions'],1)
        self.assertIs(result['production_admission'],False)
        tail,interior=fixtures(self.context)
        interior['endpoint_included']=True;reseal(interior)
        with self.assertRaises(j.JoinError):j.join_task(self.context,tail,interior)

    def test_complete_unordered_coverage_retains_exact_canonical_indices(self):
        self.assertEqual(self.coverage['primitive_count'],2592)
        self.assertEqual(self.coverage['ordered_result_sha256'],[r['result_sha256'] for r in self.joined])
        self.assertEqual(self.joined[-1]['indices'],{'active':1,'field':2,'orbital':2,'ia':11,'ib':11})

    def test_missing_duplicate_mixed_coverage_rejected(self):
        with self.assertRaises(j.JoinError):j.collect(self.context,self.joined[:-1])
        with self.assertRaises(j.JoinError):j.collect(self.context,[self.joined[0],self.joined[0]])
        for key in ('archive_sha256','backend_provenance_sha256','native_binary_sha256','native_source_sha256'):
            result=copy.deepcopy(self.joined[0]);result['execution_identity'][key]='d'*64
            result['execution_identity_sha256']=j.digest(result['execution_identity']);reseal(result)
            with self.subTest(key=key),self.assertRaises(j.JoinError):j.collect(self.context,[result])

    def test_wrong_task_window_caps_source_and_extra_keys_rejected(self):
        for change in ('index','window','caps','source','extra','unwrapped'):
            tail,interior=fixtures(self.context)
            if change=='index':interior['index']=1
            if change=='window':interior['wrapper']['command'][2]='1/8'
            if change=='caps':interior['wrapper']['native_limits']={**interior['wrapper']['native_limits'],'max_evaluations':1}
            if change=='source':interior['build_source_sha256']='d'*64
            if change=='extra':interior['unrecognized']=True
            if change=='unwrapped':interior.pop('wrapper')
            reseal(interior)
            with self.subTest(change=change),self.assertRaises(j.JoinError):j.join_task(self.context,tail,interior)

    def test_failed_endpoint_or_native_caps_are_not_joined(self):
        tail,interior=fixtures(self.context)
        tail.update(status='INCONCLUSIVE_RESOURCE_LIMIT',endpoint_radius=None,reason='fixture cap')
        reseal(tail)
        with self.assertRaises(j.JoinError):j.join_task(self.context,tail,interior)
        tail,interior=fixtures(self.context);interior['dispatched_evaluations']=1000001;reseal(interior)
        with self.assertRaises(j.JoinError):j.join_task(self.context,tail,interior)

    def test_corrupt_join_arithmetic_or_duplicate_addition_rejected(self):
        for key,value in [('endpoint_additions',2),('rectangle',{'real':{'lo':'0','hi':'9'},'imag':{'lo':'0','hi':'9'}})]:
            result=copy.deepcopy(self.joined[0]);result[key]=value;reseal(result)
            with self.assertRaises(j.JoinError):j.validate_joined(self.context,result)

    def test_initializer_preserves2592_slots_and_exact_center_radius(self):
        code=j.initializer(self.coverage)
        self.assertEqual(code.count('\n wu088_set_component('),2592*2)
        self.assertIn('integrals[2591].value),"3","1/8",p)',code)
        self.assertIn('integrals[0].value),"4","1/8",p)',code)
        self.assertIn('arb_add_error(out,error)',code)

    def test_final_rectangle_corner_disk_is_outward_and_binding_safe(self):
        rectangle={'real':interval('-3','3'),'imag':interval('-4','4')}
        final={'schema':'WU088_FINAL_D_RECTANGLES_V1','coverage_sha256':self.coverage['coverage_sha256'],
            'execution_identity_sha256':self.context.sha256,'archive_sha256':self.context.identity['archive_sha256'],
            'input_record_sha256':self.context.identity['input_record_sha256'],
            'assembler_source_sha256':j.hashlib.sha256((j.HERE/'assembly_exporter.cpp').read_bytes()).hexdigest(),
            'precision_bits':128,'D_col':[[rectangle]*2 for _ in range(47)],'D_row':[[rectangle]*47 for _ in range(2)],
            'scientific_admission':False,'production_admission':False}
        imported=j.import_final_disks(self.context,self.coverage,final)
        self.assertEqual(imported['target_disks']['data']['D_col'][0][0],{'center':['0','0'],'radius':'5'})
        self.assertIs(imported['production_admission'],False)
        final['input_record_sha256']='d'*64
        with self.assertRaises(j.JoinError):j.import_final_disks(self.context,self.coverage,final)

    def test_noncanonical_rationals_and_negative_tail_refused(self):
        for value in ('NaN','2/4','-0',0.5,'-1'):
            with self.subTest(value=value),self.assertRaises(j.JoinError):
                j.join_rectangle({'real':interval(),'imag':interval()},value)

    def test_preparation_checks_generated_header_before_output(self):
        context=self.context
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);build=root/'build';build.mkdir()
            header=b'// synthetic header bytes only; never compiled\n'
            manifest=copy.deepcopy(context.manifest)
            manifest.update(generated_header_sha256=j.hashlib.sha256(header).hexdigest(),prefix='/synthetic/prefix',
                compiler={'path':'/synthetic/c++','sha256':'f'*64,'size':1})
            reseal(manifest,'manifest_sha256')
            c=j.Context(context.plan,manifest,context.limits)
            records=[j.join_task(c,*fixtures(c,i)) for i in range(j.COUNT)]
            coverage=j.collect(c,records)
            j.write_new(build/'BUILD.json',manifest)
            (build/'frozen107_generated.hpp').write_bytes(header)
            constants={'WU088_ARCHIVE_SHA256':c.identity['archive_sha256'],'WU088_RECORD_SHA256':c.identity['input_record_sha256'],
                       'WU088_BUILD_SOURCE_SHA256':c.identity['native_source_sha256']}
            (build/'build_identity.hpp').write_text('#pragma once\n'+''.join('#define '+k+' "'+v+'"\n' for k,v in constants.items()))
            receipt=j.prepare_assembly(c,coverage,build,root/'prepared')
            self.assertIs(receipt['native_compiled'],False)
            self.assertEqual((root/'prepared/frozen107_generated.hpp').read_bytes(),header)
            (build/'frozen107_generated.hpp').write_bytes(header+b'// swapped\n')
            with self.assertRaises(j.JoinError):j.prepare_assembly(c,coverage,build,root/'refused')
            self.assertFalse((root/'refused').exists())


if __name__=='__main__':unittest.main(verbosity=2)
