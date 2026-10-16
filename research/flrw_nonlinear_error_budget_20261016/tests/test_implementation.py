import copy
import importlib.util
import json
import math
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

UNIT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(UNIT))
import nonlinear_budget as subject


def packet():
    y=[.2,.1,.1,.001]
    return dict(schema_version=1,input_kind='SYNTHETIC_FIXTURE',state_order=subject.ORDER,
        energy_unit='eV_per_H',method='BACKWARD_EULER_PREPARED_ABSORPTION',state=y,
        old_state=list(y),residual=[0,0,0,0],jacobian=[[int(i==j) for j in range(4)] for i in range(4)],
        residual_evaluation_state=list(y),jacobian_evaluation_state=list(y),context_id='SYNTHETIC_TEST',
        residual_context_id='SYNTHETIC_TEST',jacobian_context_id='SYNTHETIC_TEST',a=.1,dt_s=1,
        f_He=.08,k_B_eV_per_K=.0001,jacobian_kind='ANALYTIC')


class Implementation(unittest.TestCase):
    def hold(self,result,reason=None):
        self.assertEqual(result['status'],'HOLD')
        self.assertIsNone(result['metrics'])
        if reason:self.assertEqual(result['reason'],reason)
        json.dumps(result,allow_nan=False)

    def test_core_shape_bool_nonfinite_scale_singular(self):
        identity=[[int(i==j) for j in range(4)] for i in range(4)]
        for residual,matrix,sr,sy in [([0]*3,identity,[1]*4,[1]*4),([True,0,0,0],identity,[1]*4,[1]*4),
            ([math.nan,0,0,0],identity,[1]*4,[1]*4),([0]*4,identity,[0,1,1,1],[1]*4),
            ([0]*4,[[0]*4 for _ in range(4)],[1]*4,[1]*4),
            ([0]*4,[[1e308,0,0,0],*identity[1:]],[1]*4,[1e308,1,1,1])]:
            with self.subTest(residual=residual,sr=sr):self.hold(subject.solve_scaled(residual,matrix,sr,sy))

    def test_partial_pivot_sign_and_zero_backward_denominator(self):
        j=[[0,1,0,0],[2,0,0,0],[0,0,1,0],[0,0,0,1]]
        result=subject.solve_scaled([-2,-2,-3,-4],j,[1]*4,[1]*4)
        self.assertEqual(result['metrics']['delta'],[1,2,3,4])
        zero=subject.solve_scaled([0]*4,j,[1]*4,[1]*4)
        self.assertEqual(zero['metrics']['linear_backward_error'],0)

    def test_missing_template_and_stale_state_context(self):
        template=json.loads((UNIT/'ACTUAL_STAGE_PACKET_TEMPLATE.json').read_text())
        self.hold(subject.analyze_stage(template),'HOLD_MISSING_STAGE_DATA')
        for name,value in [('jacobian_evaluation_state',[.3,.1,.1,.001]),
                           ('residual_context_id','different'),('jacobian_context_id','different')]:
            p=packet();p[name]=value
            self.hold(subject.analyze_stage(p),'HOLD_STALE_OR_MISMATCHED_STAGE')
        p=packet();del p['input_kind'];self.hold(subject.analyze_stage(p),'HOLD_MISSING_STAGE_DATA')

    def test_actual_shaped_synthetic_metadata_guards_and_boundary(self):
        # These fabricated packets test adapter guards; no actual stage is observed.
        p=packet();p.update(input_kind='ACTUAL_STAGE',iterate_status='ACCEPTED_CHEMICAL_STAGE',
            source_commit='fdfda0fec423ccb7175552c7dc066be93ce347e1',driver_blob_sha=subject.DRIVER_BLOB,
            stage_id='SYNTHETIC_ACTUAL_SHAPE',execution_receipt='SYNTHETIC_NOT_OBSERVED',
            added_rhs_evaluations=0,cost_owner='SYNTHETIC')
        missing=copy.deepcopy(p);del missing['added_rhs_evaluations']
        self.hold(subject.analyze_stage(missing),'HOLD_MISSING_STAGE_DATA')
        wrong=copy.deepcopy(p);wrong['driver_blob_sha']='0'*40
        self.hold(subject.analyze_stage(wrong),'HOLD_SOURCE_BINDING_MISMATCH')
        wrong=copy.deepcopy(p);wrong['added_rhs_evaluations']=True
        self.hold(subject.analyze_stage(wrong),'HOLD_ADDED_RHS_COST')
        p['residual'][0]=1e-11
        self.assertEqual(subject.analyze_stage(p)['status'],'ACTUAL_STAGE_LINEARIZED_DIAGNOSTIC')
        p['residual'][0]=math.nextafter(1e-11,math.inf)
        self.hold(subject.analyze_stage(p),'HOLD_ACCEPTED_STAGE_RESIDUAL_MISMATCH')

    def test_atomic_checkpoint_sequence(self):
        events=[];fsync,replace=os.fsync,os.replace
        def synced(fd):
            events.append('directory_sync' if stat.S_ISDIR(os.fstat(fd).st_mode) else 'file_sync')
            return fsync(fd)
        def replaced(src,dst):
            self.assertEqual(Path(src).parent,Path(dst).parent)
            json.loads(Path(src).read_text());events.append('same_directory_replace')
            return replace(src,dst)
        with tempfile.TemporaryDirectory() as d,patch.object(os,'fsync',synced),patch.object(os,'replace',replaced):
            path=Path(d)/'result.json';subject.atomic_json(path,{'value':1})
            self.assertEqual(json.loads(path.read_text()),{'value':1})
            self.assertFalse(list(Path(d).glob('*.tmp')))
        self.assertEqual(events,['file_sync','same_directory_replace','directory_sync'])

    def test_cli_stdlib_success_missing_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); source=root/'packet.json';source.write_text(json.dumps(packet()))
            cli=[sys.executable,'-S','-B',str(UNIT/'nonlinear_budget.py')]
            success=subprocess.run([*cli,'--input',str(source),'--output',str(root/'ok')],capture_output=True,text=True,timeout=5)
            self.assertEqual(success.returncode,0,success.stderr)
            receipt=json.loads((root/'ok/EXECUTION_RECEIPT.json').read_text())
            self.assertIsNotNone(receipt['input_sha256']);self.assertGreaterEqual(receipt['wall_seconds'],0)
            original=(root/'ok/NONLINEAR_BUDGET_RESULT.json').read_bytes()
            repeated=subprocess.run([*cli,'--input',str(source),'--output',str(root/'ok')],capture_output=True,text=True,timeout=5)
            self.assertEqual(repeated.returncode,2)
            self.assertEqual((root/'ok/NONLINEAR_BUDGET_RESULT.json').read_bytes(),original)
            missing=subprocess.run([*cli,'--input',str(root/'absent'),'--output',str(root/'missing')],capture_output=True,text=True,timeout=5)
            self.assertEqual(missing.returncode,2)
            self.hold(json.loads((root/'missing/NONLINEAR_BUDGET_RESULT.json').read_text()),'HOLD_MISSING_STAGE_DATA')
            self.assertIsNone(json.loads((root/'missing/EXECUTION_RECEIPT.json').read_text())['input_sha256'])


if __name__=='__main__':unittest.main()
