import hashlib, tempfile, unittest
from pathlib import Path
from receiver_binding import call_inventory,verify_sources,require_g7_context,request_physical_rates,SourceUnavailable

class BindingTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
        self.source=self.root/'sample.py';self.source.write_text("raise RuntimeError('MUST NOT EXECUTE')\nx=r2n.alpha_b_hii(T)\ny=r2n.beta_hi(T)\n")
        self.lock=[{'path':'sample.py','bytes':self.source.stat().st_size,'sha256':hashlib.sha256(self.source.read_bytes()).hexdigest()}]
        self.ctx={'geometry':'Bianchi_I_fixed_principal_or_commuting','measure':'initial_isotropic','matter_frame':'non_tilted','quantity':'log_energy_ratio_after_isotropic_redshift'}
    def test_ast_calls_no_execution(self):
        r=call_inventory(self.source)
        self.assertEqual([(x['function'],x['line']) for x in r],[('alpha_b_hii',2),('beta_hi',3)])
    def test_positive_source_binding(self): self.assertEqual(verify_sources(self.root,self.lock),{'verified':1})
    def test_hash_mismatch(self):
        self.lock[0]['sha256']='0'*64
        with self.assertRaises(ValueError):verify_sources(self.root,self.lock)
    def test_size_mismatch(self):
        self.lock[0]['bytes']+=1
        with self.assertRaises(ValueError):verify_sources(self.root,self.lock)
    def test_missing_file(self):
        self.source.unlink()
        with self.assertRaises(ValueError):verify_sources(self.root,self.lock)
    def test_escape(self):
        self.lock[0]['path']='../sample.py'
        with self.assertRaises(ValueError):verify_sources(self.root,self.lock)
    def test_absolute_path(self):
        self.lock[0]['path']=str(self.source)
        with self.assertRaises(ValueError):verify_sources(self.root,self.lock)
    def test_symlink(self):
        p=self.root/'link.py';p.symlink_to(self.source);self.lock[0]['path']='link.py'
        with self.assertRaises(ValueError):verify_sources(self.root,self.lock)
    def test_duplicate_source(self):
        with self.assertRaises(ValueError):verify_sources(self.root,self.lock*2)
    def test_bool_size(self):
        self.lock[0]['bytes']=True
        with self.assertRaises(ValueError):verify_sources(self.root,self.lock)
    def test_no_empty_lock(self):
        with self.assertRaises(ValueError):verify_sources(self.root,[])
    def test_canonical_context(self): self.assertEqual(require_g7_context(self.ctx),True)
    def test_later_sky_measure_rejected(self):
        self.ctx['measure']='final_sky'
        with self.assertRaises(ValueError):require_g7_context(self.ctx)
    def test_noncommuting_rejected(self):
        self.ctx['geometry']='general_time_ordered_Bianchi'
        with self.assertRaises(ValueError):require_g7_context(self.ctx)
    def test_tilt_rejected(self):
        self.ctx['matter_frame']='tilted'
        with self.assertRaises(ValueError):require_g7_context(self.ctx)
    def test_unknown_context_key(self):
        self.ctx['z']=7
        with self.assertRaises(ValueError):require_g7_context(self.ctx)
    def test_rate_no_fallback(self):
        with self.assertRaises(SourceUnavailable):request_physical_rates(temperature_K=10000)
    def test_fake_flag_no_promotion(self):
        with self.assertRaises(SourceUnavailable):request_physical_rates(temperature_K=10000,admitted=True)
    def test_missing_context(self):
        self.ctx.pop('measure')
        with self.assertRaises(ValueError):require_g7_context(self.ctx)
if __name__=='__main__':unittest.main()
