import ast
from copy import deepcopy
import csv
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from fixtures import BASE, UNIT, analyzer, case, reader, saved_fixture
from pair_diagnostics import diagnose_pair, write_diagnostics


class PairImplementation(unittest.TestCase):
    def test_constant_tie_and_serialization(self):
        result=diagnose_pair(case([0,0.5,1],[0,0,0],'R'),case([0,1],[2,2],'C'))
        row=result['summary'][0]
        self.assertEqual(result['union_knots'],3)
        self.assertEqual((row['sup_absolute_difference'],row['ln_a_at_sup'],row['l1_integral'],
                          row['l2_squared_integral'],row['rms_difference']),(2,0,2,4,2))
        with tempfile.TemporaryDirectory() as d:
            write_diagnostics(result,d)
            self.assertEqual(json.loads((Path(d)/'full_pair_continuous_diagnostics.json').read_text()),result)
            rows=list(csv.DictReader((Path(d)/'full_pair_continuous_summary.csv').open()))
            self.assertEqual(len(rows),1)
            self.assertEqual(set(rows[0]),set(row))

    def test_partial_overlap_and_distinct_knots(self):
        result=diagnose_pair(case([0,1,2],[0,0,0]),case([0.5,1.5,3],[2,2,2]))
        self.assertEqual(result['overlap'],[0.5,2])
        self.assertEqual(result['union_knots'],4)
        self.assertEqual(result['summary'][0]['l1_integral'],3)
        tiny=math.nextafter(0.5,1)
        result=diagnose_pair(case([0,0.5,1],[0,0,0]),case([0,tiny,1],[0,1,0]))
        self.assertEqual(result['union_knots'],4)
        self.assertEqual(result['summary'][0]['ln_a_at_sup'],tiny)

    def test_invalid_shape_domain_and_nonfinite(self):
        reference=case([0,1],[0,0])
        bad=[case([0],[0]),case([0,0],[0,1]),case([2,3],[0,0]),
             case([0,1],[0]),case([0,1],[math.nan,0]),case([0,math.inf],[0,1])]
        for candidate in bad:
            with self.subTest(candidate=candidate), self.assertRaises(ValueError):
                diagnose_pair(reference,candidate)
        for fields in ([],['L'],['x_HII','x_HII'],['absent']):
            with self.subTest(fields=fields), self.assertRaises(ValueError):
                diagnose_pair(reference,reference,fields)

    def test_arithmetic_overflow_rejects(self):
        with self.assertRaisesRegex(ValueError,'NONFINITE'):
            diagnose_pair(case([0,1],[-1e308,-1e308]),case([0,1],[1e308,1e308]))
        with self.assertRaisesRegex(ValueError,'NONFINITE'):
            diagnose_pair(case([0,1],[0,0]),case([0,1],[1e308,1e308]))

    def test_opt_in_caller_default_preserved(self):
        tree=ast.parse((BASE/'postprocess_flrw.py').read_text())
        function=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='run')
        self.assertEqual(function.args.args[-1].arg,'continuous_pair_diagnostics')
        self.assertIs(function.args.defaults[-1].value,False)
        branches=[n for n in ast.walk(function) if isinstance(n,ast.If)
                  and isinstance(n.test,ast.Name) and n.test.id=='continuous_pair_diagnostics']
        self.assertEqual(len(branches),1)
        called={n.func.id for n in ast.walk(branches[0]) if isinstance(n,ast.Call)
                and isinstance(n.func,ast.Name)}
        self.assertEqual(called,{'diagnose_pair','write_diagnostics'})
        # Old sampled filenames and milestone assignment remain in the caller.
        source=ast.unparse(function)
        for name in ('full_pair_sampled_diagnostics.csv','full_pair_summary.csv','full_pair_milestones.json'):
            self.assertIn(name,source)


class StandaloneImplementation(unittest.TestCase):
    def test_success_single_stream_and_relocation(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); path,prior,runs,bindings=saved_fixture(root)
            for spec in prior['validated_complete_inputs']:
                for role in ('history','abundances','config','source_identity','terminal','binding'):
                    spec[role]['path']='/not-present/'+spec['id']+'/'+Path(spec[role]['path']).name
            path.write_text(json.dumps(prior))
            opened=[]; original=Path.open
            def audited_open(path,*args,**kwargs):
                self.assertNotIn('MUST_NOT_OPEN',str(path))
                opened.append((str(path),args[0] if args else kwargs.get('mode','r')))
                return original(path,*args,**kwargs)
            with patch.object(Path,'open',audited_open):
                receipt=analyzer.run(path,root/'out',runs,bindings)
            self.assertEqual(receipt['status'],'PAIR_DIAGNOSTICS_COMPLETE',receipt)
            self.assertEqual(receipt['input_kind'],'SYNTHETIC_ONLY_NOT_FULL005_ADMISSION')
            self.assertEqual(len(receipt['metrics']['summary']),16)
            for spec in prior['validated_complete_inputs']:
                for filename in ('history.csv','abundances.csv'):
                    expected=str(runs/spec['id']/filename)
                    self.assertEqual([(p,m) for p,m in opened if p==expected],[(expected,'rb')])
            self.assertEqual(receipt['ledger_reads'],0)
            self.assertEqual(receipt['checkpoint_reads'],0)

    def test_import_isolation_and_cli_exit(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); path,_,_,_=saved_fixture(root)
            code=('import builtins,runpy,sys; original=builtins.__import__; '
                  'exec("def guarded(name,*a,**k):\\n if name.split(\'.\')[0] in '
                  '(\'numpy\',\'matplotlib\',\'postprocess_flrw\'): raise AssertionError(name)'
                  '\\n return original(name,*a,**k)"); builtins.__import__=guarded; '
                  'sys.argv=[sys.argv[1],"--validated-receipt",sys.argv[2],"--output",sys.argv[3]]; '
                  'runpy.run_path(sys.argv[0],run_name="__main__")')
            process=subprocess.run([sys.executable,'-S','-B','-c',code,str(UNIT/'analyze_saved_pair.py'),
                                    str(path),str(root/'out')],capture_output=True,text=True)
            self.assertEqual(process.returncode,0,process.stdout+process.stderr)
            self.assertIn('PAIR_DIAGNOSTICS_COMPLETE',process.stdout)
            missing=subprocess.run([sys.executable,'-S','-B',str(UNIT/'analyze_saved_pair.py'),
                                    '--validated-receipt',str(root/'absent'), '--output',str(root/'missing')],
                                    capture_output=True,text=True)
            self.assertEqual(missing.returncode,2)
            self.assertIsNone(json.loads((root/'missing/PAIR_DIAGNOSTICS_RECEIPT.json').read_text())['metrics'])

    def test_hash_mismatch_and_missing_inputs_hold(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); path,prior,_,_=saved_fixture(root)
            history=Path(prior['validated_complete_inputs'][0]['history']['path'])
            history.write_bytes(history.read_bytes()+b'\n')
            result=analyzer.run(path,root/'mismatch')
            self.assertTrue(result['status'].startswith('HOLD'))
            self.assertIn('HASH_MISMATCH',result['reason'])
            self.assertIsNone(result['metrics'])
            history.unlink()
            result=analyzer.run(path,root/'missing')
            self.assertTrue(result['status'].startswith('HOLD'))
            self.assertFalse((root/'missing/full_pair_continuous_summary.csv').exists())
            with self.assertRaisesRegex(ValueError,'FRESH_OUTPUT'):
                analyzer.run(path,root/'missing')

    def test_receipt_and_alignment_failures_hold(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); path,prior,_,_=saved_fixture(root)
            prior['pair_source_relation']='UNBOUND'
            path.write_text(json.dumps(prior))
            self.assertIn('SOURCE_RELATION',analyzer.run(path,root/'relation')['reason'])
            prior['pair_source_relation']='BYTE_IDENTICAL_COMPILED_SOURCE'
            spec=prior['validated_complete_inputs'][0]
            abundance=Path(spec['abundances']['path'])
            abundance.write_text(abundance.read_text().replace('H_I,','INVALID_SPECIES,'))
            import hashlib
            spec['abundances']['sha256']=hashlib.sha256(abundance.read_bytes()).hexdigest()
            path.write_text(json.dumps(prior))
            self.assertIn('SPECIES_ALIGNMENT',analyzer.run(path,root/'alignment')['reason'])


if __name__=='__main__':
    unittest.main()
