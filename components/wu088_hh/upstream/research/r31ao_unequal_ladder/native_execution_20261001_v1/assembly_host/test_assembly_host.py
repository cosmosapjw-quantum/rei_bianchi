"""Guarded process and exact artifact boundaries; no actual HH/native assembly."""
import copy
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock
import assembly_host as h


class ProcessTests(unittest.TestCase):
    def test_real_subprocess_success_and_exact_argv(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)
            report=h.bounded_process([sys.executable,'-c','import sys; print(sys.argv[1])','x;$(false)'],
                {'PATH':'/usr/bin:/bin'},dict(h.BUILD_LIMITS),p/'out',p/'err')
            self.assertEqual(report['exit_code'],0)
            self.assertEqual((p/'out').read_text(),'x;$(false)\n')
            self.assertFalse(report['timed_out'])

    def test_hard_wall_limit_kills_process_group(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)
            report=h.bounded_process([sys.executable,'-c','import time; time.sleep(30)'],{},
                {**h.BUILD_LIMITS,'wall_seconds':1},p/'out',p/'err')
            self.assertTrue(report['timed_out']);self.assertLess(report['exit_code'],0)

    def test_file_output_limit_refuses_incomplete_result(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)
            report=h.bounded_process([sys.executable,'-c','import os; os.write(1,b"x"*200000); os.write(1,b"y")'],{},
                {**h.BUILD_LIMITS,'file_bytes':4096},p/'out',p/'err')
            self.assertNotEqual(report['exit_code'],0)
            self.assertLessEqual((p/'out').stat().st_size,4096)

    def test_address_space_cap_is_enforced(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)
            report=h.bounded_process([sys.executable,'-c','a=bytearray(512*1024*1024)'],{},
                {**h.BUILD_LIMITS,'memory_mib':256},p/'out',p/'err')
            self.assertNotEqual(report['exit_code'],0)
            self.assertIn('MemoryError',(p/'err').read_text())

    def test_existing_logs_refuse_before_process_launch(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory);(p/'out').write_text('original')
            with mock.patch.object(h.subprocess,'Popen') as launch:
                with self.assertRaises(FileExistsError):h.bounded_process([sys.executable],{},h.BUILD_LIMITS,p/'out',p/'err')
                launch.assert_not_called()
            self.assertEqual((p/'out').read_text(),'original')

    def test_failure_preserves_process_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)
            with self.assertRaises(h.ChildFailure) as caught:
                h.checked_process([sys.executable,'-c','raise SystemExit(7)'],{},h.BUILD_LIMITS,p/'out',p/'err')
            h.failure_record(p,'TEST',caught.exception)
            self.assertEqual(h.read_json(p/'FAILURE.json')['process']['exit_code'],7)

    def test_invalid_limits_and_json(self):
        for limits in ({**h.RUN_LIMITS,'precision_bits':True},{**h.RUN_LIMITS,'wall_seconds':0},
                       {**h.RUN_LIMITS,'memory_mib':8193},{**h.RUN_LIMITS,'extra':1}):
            with self.assertRaises(h.HostError):h.validate_limits(limits)
        for data in (b'{"a":1,"a":2}',b'{"x":NaN}',b'{"x":1.5}'):
            with self.assertRaises(h.HostError):h.parse_json(data)

    def test_existing_build_and_run_directories_fail_before_authority_load(self):
        with tempfile.TemporaryDirectory() as directory,mock.patch.object(h,'load_authority') as load:
            with self.assertRaises(FileExistsError):h.build({}, {}, directory)
            with self.assertRaises(FileExistsError):h.run('/missing','a'*64,directory)
            load.assert_not_called()


class AuthorityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory();root=Path(cls.tmp.name);cls.root=root
        cls.join,cls.gate,_=h.configured_modules()
        sys.path.insert(0,str(h.PRODUCTION/'endpoint_tasks'))
        try:
            from test_endpoint_tasks import toy_record,WINDOW
            record,archive=toy_record()
        finally:sys.path.pop(0)
        plan=cls.join.endpoint.build_plan(record,WINDOW,precision_bits=24,panels=1,source_archive_bytes=archive)
        native_dir=root/'native';native_dir.mkdir();prefix=root/'prefix';prefix.mkdir()
        compiler=h.identity(sys.executable)
        header=cls.join.endpoint.adapter.generate_cpp(record,source_archive_bytes=archive).encode()
        provenance=root/'backend.json';provenance.write_text('{}')
        manifest={'schema':'WU088_NATIVE_DRIVER_BUILD_V1','source':cls.join.native.source_identity(),
            'archive_sha256':plan['archive_sha256'],'input_record_sha256':plan['input_record_sha256'],
            'binary_sha256':'a'*64,'backend_provenance_sha256':h.digest(provenance.read_bytes()),
            'backend_provenance':str(provenance),'generated_header_sha256':h.digest(header),
            'prefix':str(prefix),'compiler':compiler}
        manifest['manifest_sha256']=cls.join.digest(manifest)
        cls.context=cls.join.Context(plan,manifest,cls.join.native.DEFAULT_LIMITS,source_archive_bytes=archive)
        sys.path.insert(0,str(h.PRODUCTION/'primitive_join'))
        try:import test_join
        finally:sys.path.pop(0)
        records=[cls.join.join_task(cls.context,*test_join.fixtures(cls.context,i)) for i in range(2592)]
        cls.coverage=cls.join.collect(cls.context,records)
        cls.join.write_new(native_dir/'BUILD.json',manifest);(native_dir/'frozen107_generated.hpp').write_bytes(header)
        constants={'WU088_ARCHIVE_SHA256':cls.context.identity['archive_sha256'],
            'WU088_RECORD_SHA256':cls.context.identity['input_record_sha256'],
            'WU088_BUILD_SOURCE_SHA256':cls.context.identity['native_source_sha256']}
        (native_dir/'build_identity.hpp').write_text('#pragma once\n'+''.join('#define '+k+' "'+v+'"\n' for k,v in constants.items()))
        prep=cls.join.prepare_assembly(cls.context,cls.coverage,native_dir,root/'prepared')
        cls.paths={'plan':str(root/'plan.json'),'native_build_directory':str(native_dir),
            'native_limits':str(root/'limits.json'),'coverage':str(root/'coverage.json'),
            'preparation':str(root/'prepared'),'input_npz':str(root/'synthetic.npz')}
        for path,obj in ((cls.paths['plan'],plan),(cls.paths['native_limits'],cls.join.native.DEFAULT_LIMITS),
                         (cls.paths['coverage'],cls.coverage)):h.write_new(path,obj)
        Path(cls.paths['input_npz']).write_bytes(archive)
        cls.expected={'native_build_sha256':manifest['manifest_sha256'],'coverage_sha256':cls.coverage['coverage_sha256'],
            'preparation_sha256':h.digest(h.canonical(prep))}
        cls.fake_gate=mock.Mock()
        cls.fake_gate.file_identity.side_effect=lambda p,wanted=None:h.identity(p)
        cls.fake_gate.verify_backend.return_value={'libraries':{},'verification':{'status':'SYNTHETIC_TEST_FIXTURE_ONLY'}}

    @classmethod
    def tearDownClass(cls):cls.tmp.cleanup()

    def load(self):
        with mock.patch.object(h,'configured_modules',return_value=(self.join,self.fake_gate,None)):
            return h.load_authority(self.paths,self.expected)

    def test_source_bound_preparation_and_headers_are_accepted(self):
        authority=self.load()
        self.assertEqual(authority['context'].sha256,self.context.sha256)
        self.assertEqual(authority['coverage']['primitive_count'],2592)

    def test_changed_prepared_header_refused_before_backend(self):
        path=Path(self.paths['preparation'])/'frozen107_generated.hpp';original=path.read_bytes()
        try:
            path.write_bytes(original+b'// mismatch\n')
            with self.assertRaises(h.HostError):self.load()
        finally:path.write_bytes(original)

    def test_rehashed_arbitrary_compile_command_is_rejected(self):
        path=Path(self.paths['preparation'])/'PREPARATION.json';original=path.read_bytes()
        changed=h.parse_json(original);changed['compile_command']=['/bin/sh','-c','false']
        expected=self.expected.copy();expected['preparation_sha256']=h.digest(h.canonical(changed))
        try:
            path.write_bytes(h.canonical(changed))
            with mock.patch.object(h,'configured_modules',return_value=(self.join,self.fake_gate,None)):
                with self.assertRaises(h.HostError):h.load_authority(self.paths,expected)
        finally:path.write_bytes(original)

    def test_requested_coverage_hash_is_enforced(self):
        expected={**self.expected,'coverage_sha256':'d'*64}
        with mock.patch.object(h,'configured_modules',return_value=(self.join,self.fake_gate,None)):
            with self.assertRaises(h.HostError):h.load_authority(self.paths,expected)

    def test_export_precision_identity_shape_and_corner_radius(self):
        rectangle={'real':{'lower_mantissa':'-3','upper_mantissa':'3','exponent2':'0'},
                   'imag':{'lower_mantissa':'-4','upper_mantissa':'4','exponent2':'0'}}
        final={'schema':'WU088_FINAL_D_RECTANGLES_V1','coverage_sha256':self.coverage['coverage_sha256'],
            'execution_identity_sha256':self.context.sha256,'archive_sha256':self.context.identity['archive_sha256'],
            'input_record_sha256':self.context.identity['input_record_sha256'],
            'assembler_source_sha256':h.digest(h.read_bytes(h.PRODUCTION/'primitive_join/assembly_exporter.cpp')),
            'precision_bits':128,'D_col':[[rectangle]*2 for _ in range(47)],'D_row':[[rectangle]*47 for _ in range(2)],
            'scientific_admission':False,'production_admission':False}
        authority={'join':self.join,'context':self.context,'coverage':self.coverage}
        imported=h.validate_export(authority,final,128)
        self.assertEqual(imported['target_disks']['data']['D_col'][0][0]['radius'],'5')
        for mutation in ('precision','source','shape','admission'):
            bad=copy.deepcopy(final)
            if mutation=='precision':bad['precision_bits']=256
            if mutation=='source':bad['input_record_sha256']='d'*64
            if mutation=='shape':bad['D_row'].pop()
            if mutation=='admission':bad['scientific_admission']=True
            with self.subTest(mutation=mutation),self.assertRaises(ValueError):h.validate_export(authority,bad,128)

    def test_override_hash_and_path_fail_closed(self):
        with self.assertRaises(h.HostError):h.configured_modules('/etc/passwd','a'*64)
        with self.assertRaises(h.HostError):h.configured_modules(h.PRODUCTION/'native_driver/driver.py','a'*64)


if __name__=='__main__':unittest.main(verbosity=2)
