from __future__ import annotations
import sys,unittest,tempfile,zipfile,gzip
from pathlib import Path
import numpy as np
import pandas as pd
SRC=Path(__file__).resolve().parents[1]/'src';sys.path.insert(0,str(SRC))
from run_node_lift import lift_macro_case, read_gzipped_csv_member, copy_inherited_csv_exact

class MacroLiftIntegrationTest(unittest.TestCase):



 def test_canonical_package_sources_match_stage_snapshot(self):
  repo=Path(__file__).resolve().parents[3]
  self.assertEqual((repo/"src/rei_bianchi/node_lift_operator.py").read_bytes(),(SRC/"node_lift_operator.py").read_bytes())
  self.assertEqual((repo/"src/rei_bianchi/run_node_lift.py").read_bytes(),(SRC/"run_node_lift.py").read_bytes())

 def test_copies_inherited_csv_byte_exact(self):
  with tempfile.TemporaryDirectory() as td:
   src=Path(td)/"source.csv"; dst=Path(td)/"copy.csv"
   payload=b"x\n5.3640286157926174e+60\n"
   src.write_bytes(payload)
   copy_inherited_csv_exact(src,dst)
   self.assertEqual(dst.read_bytes(),payload)

 def test_reads_gzipped_csv_member_from_zip_stream(self):
  raw=b"a,b\n1,2\n"
  with tempfile.TemporaryDirectory() as td:
   zp=Path(td)/"x.zip"
   with zipfile.ZipFile(zp,"w") as z:
    z.writestr("data/table.csv.gz",gzip.compress(raw))
   with zipfile.ZipFile(zp) as z:
    df=read_gzipped_csv_member(z,"data/table.csv.gz")
   self.assertEqual(df.to_dict("records"),[{"a":1,"b":2}])
 def test_one_macro_closes_nested_moments(self):
  nodes=pd.DataFrame({
    'micro_index':np.arange(6),
    'w_micro':[0.05,0.10,0.15,0.20,0.25,0.25],
    'delta_total':[0.3,0.6,0.9,1.2,1.8,2.5],
    'T_K':[6000,8000,10000,14000,18000,24000],
    'xHII':[0.2,0.4,0.7,0.85,0.95,0.99],
  })
  macro={
   'shape_lane':'TEST','interval_index':0,'substep':1,'z_mid':5.95,'macro_index':0,
   'M_sink_H_cMpc3':2.5e64,'J_sink_G1_s_inv_cMpc3':4.0e48,'J_sink_G2a_s_inv_cMpc3':1.0e48,
   'kappa_sink_G1_cMpc_inv':2.0e-4,'kappa_sink_G2a_cMpc_inv':1.0e-4,
   'cycling_capacity_macro_s_inv_cMpc3':5.5e48,'mass_transfer_rate_macro_H_s_inv_cMpc3':-2.0e46,
  }
  global_row={'x_HII_sink_global':0.82,'T_sink_global_K':15000.0,'dt_Myr':10.0}
  q=np.array([[.35,.05],[.25,.10],[.15,.20],[.10,.25],[.10,.25],[.05,.15]])
  out=lift_macro_case(nodes,macro,global_row,q)
  m=out['mass'];x=out['xHII'];T=out['T_K'];J=out['J'];kap=out['kappa'];cap=out['capacity'];net=out['transfer_net']
  self.assertLess(abs(m.sum()-macro['M_sink_H_cMpc3'])/macro['M_sink_H_cMpc3'],2e-14)
  self.assertLess(abs(np.dot(m,x)/m.sum()-global_row['x_HII_sink_global']),2e-13)
  self.assertLess(abs(np.dot(m,T)/m.sum()-global_row['T_sink_global_K'])/global_row['T_sink_global_K'],2e-13)
  np.testing.assert_allclose(J.sum(0),[macro['J_sink_G1_s_inv_cMpc3'],macro['J_sink_G2a_s_inv_cMpc3']],rtol=2e-11)
  np.testing.assert_allclose(kap.sum(0),[macro['kappa_sink_G1_cMpc_inv'],macro['kappa_sink_G2a_cMpc_inv']],rtol=2e-11)
  self.assertTrue(np.all(J.sum(1)<=cap+1e-8*max(cap)))
  self.assertLess(abs(net.sum()-macro['mass_transfer_rate_macro_H_s_inv_cMpc3'])/abs(macro['mass_transfer_rate_macro_H_s_inv_cMpc3']),2e-14)
  self.assertLess(out['certificate']['max_stationarity_residual'],2e-9)

if __name__=='__main__':unittest.main()
