"""Independent adversarial tests at the new adapter boundary; no native execution."""
import copy, importlib.util, json, pathlib, sys, unittest
from fractions import Fraction
from unittest.mock import patch
HERE=pathlib.Path(__file__).resolve().parent
P=HERE.parent/'tile_runner/runner.py'
spec=importlib.util.spec_from_file_location('independent_w1_runner',P)
r=importlib.util.module_from_spec(spec);sys.modules[spec.name]=r;spec.loader.exec_module(r)

class AdapterReview(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.ctx=r.context();cls.ctx['global_plan']=cls.ctx['d'].parse_json(r.read(r.GLOBAL))
  cls.grid=r.bound_grid(cls.ctx,cls.ctx['global_plan'],0,3)
  cls.plan=cls.ctx['d'].parse_json(r.read(r.PRIOR/'plans/00.json'))
  cls.raw=r.read(r.IMPORTED)
 def normalize(self,raw=None,grid=None,plan=None,tile_id=0,origin='imported',path=None):
  return r.normalize(self.ctx,grid or self.grid,plan or self.plan,tile_id,self.raw if raw is None else raw,origin=origin,receipt_path=path or r.IMPORTED)
 def test_exact_old_receipt_adopted_without_dispatch(self):
  with patch.object(self.ctx['d'],'run_task',side_effect=AssertionError('HH dispatch forbidden')):
   n=self.normalize()
  old=json.loads(self.raw)
  self.assertEqual(n['native_receipt_sha256'],r.IMPORTED_SHA)
  for part in ('real','imag'):
   v=old['rectangle'][part];lo=int(v['lower_mantissa'])*Fraction(2)**int(v['exponent2']);hi=int(v['upper_mantissa'])*Fraction(2)**int(v['exponent2'])
   self.assertEqual(n['rectangle'][part],{'lower':str(lo),'upper':str(hi)})
   self.assertEqual(Fraction(n['reported_radius'][part]),(hi-lo)/2)
 def test_resealed_import_forgery_rejected(self):
  q=json.loads(self.raw);q['rectangle']['real']['lower_mantissa']='0';q.pop('result_sha256');q=r.sealed(q,'result_sha256')
  with self.assertRaises(r.TileError):self.normalize(raw=r.canonical(q))
 def test_import_origin_cannot_reassign_tile(self):
  with self.assertRaises(r.TileError):self.normalize(tile_id=1)
 def test_import_cannot_claim_new_execution(self):
  with self.assertRaises(r.TileError):self.normalize(origin='new')
 def test_same_bytes_unpinned_path_rejected(self):
  with self.assertRaises(r.TileError):self.normalize(path=HERE/'fabricated_old.json')
 def test_resealed_global_radius_relaxation_rejected(self):
  g=copy.deepcopy(self.grid);g['global_radius_exp']=-47;g['tile_radius_exp']=-51;g.pop('plan_sha256');g=r.sealed(g,'plan_sha256')
  with self.assertRaises(ValueError):self.normalize(grid=g)
 def test_resealed_validator_authority_swap_rejected(self):
  g=copy.deepcopy(self.grid);g['bindings']['validator_source_sha256']='0'*64;g.pop('plan_sha256');g=r.sealed(g,'plan_sha256')
  with self.assertRaises(ValueError):self.normalize(grid=g)
 def test_wrong_local_plan_rejected(self):
  p=self.ctx['d'].parse_json(r.read(r.PRIOR/'plans/01.json'))
  with self.assertRaises(ValueError):self.normalize(plan=p)

if __name__=='__main__':unittest.main(verbosity=2)
