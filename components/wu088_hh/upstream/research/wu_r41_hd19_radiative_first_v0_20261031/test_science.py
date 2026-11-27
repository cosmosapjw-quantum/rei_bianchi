#!/usr/bin/env python3
"""R41 independent formula-, input-, and actual-data checks; same author, not distinct-author R6/C9."""
import csv,json,hashlib,unittest,math
from pathlib import Path
import numpy as np
from mpmath import mp
from scipy.constants import h,c,k as KB
from generate import ROOT,TGRID,DENSITIES,ZGRID,T0,EXPECTED,assert_sources,data_model,prepare,radiative_components,source_owned_external_radiative_exit,solve_source_open_boundary,solve_case,owner

def load_csv(name):
    with (ROOT/'results'/name).open(newline='') as f:return list(csv.DictReader(f))
class R41OriginalSourceTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
    cls.data,cls.over,cls.missing=data_model(ROOT);cls.A,cls.U,cls.E=prepare(cls.data)
    cls.S=load_csv('R41_FIRST_V0_MECHANISM_SUMMARY_3500.csv')
    cls.B=load_csv('R41_FIRST_V0_TERMINAL_BRANCHES_126000.csv')
    cls.L=load_csv('R41_PHOTON_LINE_EVENTS_4704.csv')
 def test_01_immutable_sources(self):
    assert_sources(ROOT)
    self.assertEqual(hashlib.sha256((ROOT/'source_private/R40_FIRST_V0_HIT_BRANCHES_1680.csv').read_bytes()).hexdigest(),'3b67e252498cca0b04a099d8f9b52b0c4bd7e9a689a93ce21f71e7e4c1ce561a')
 def test_02_source_counter(self):
    self.assertEqual(len(self.data['radiative']),368)
    self.assertEqual(len(self.data['partners'][7]['rates']),171)
    self.assertEqual(len(self.over),1548)
    self.assertEqual(len(self.missing),16)
 def test_03_radiative_source_within19(self):
    (rs,ri,ra),lines=radiative_components(self.data,'300')
    self.assertEqual(len(lines),63)
    self.assertEqual(sum(z['up_v']==1 and z['low_v']==0 for z in lines),31)
    self.assertEqual(sum(z['up_v']==1 and z['low_v']==1 for z in lines),11)
 def test_04_R36_radiation_exact_equivalence(self):
    for z in ['0','30','100','300']:
       mats,_=radiative_components(self.data,z)
       Q,lines=owner.radiative_generator(self.data,T0*(1+int(z)))
       self.assertLess(np.max(abs(sum(mats)-Q)),16*np.finfo(float).eps*np.max(abs(Q))) # different summation order, roundoff bound
       self.assertEqual(len(lines),63)
 def test_05_OFF_spontaneous_not_zero(self):
    (rs,stim,absorp),lines=radiative_components(self.data,'OFF')
    self.assertGreater(rs.max(),0)
    self.assertTrue(np.all(stim==0))
    self.assertTrue(np.all(absorp==0))
 def test_06_generator_column_conservation(self):
    C=owner.bath_rates(self.data,55.,1.e5,self.over)
    rr,_=radiative_components(self.data,'300')
    self.assertLess(np.max(abs((C+sum(rr)).sum(axis=0))),5e-19)
 def test_07_nonnegativity_and_mass(self):
    self.assertEqual(len(self.S),3500)
    self.assertTrue(all(float(v['P_sum'])>1-1e-12 for v in self.S))
    self.assertLess(max(abs(float(v['P_sum'])-1) for v in self.S),1e-12)
    self.assertTrue(all(min(float(v[x]) for x in ['P_first_v0_by_collision','P_first_v0_by_spontaneous','P_first_v0_by_stimulated'])>=0 for v in self.S))
 def test_08_branch_rows_count(self):
    self.assertEqual(len(self.B),126000)
    self.assertEqual(len(load_csv('R41_SOURCE_CONTRAST_1750.csv')),1750)
    self.assertEqual(len(load_csv('R41_HALF_RADIATIVE_DENSITY_700.csv')),700)
    self.assertEqual(len(load_csv('R41_19LEVEL_RADIATIVE_LINES_63.csv')),63)
    self.assertEqual(len(load_csv('R41_HALF_DENSITY_SOURCE_CONTRAST_350.csv')),350)
 def test_09_off_no_stim(self):
    self.assertTrue(all(float(v['P_first_v0_by_stimulated'])==0 and float(v['expected_photons_absorbed'])==0 for v in self.S if v['z_boundary']=='OFF'))
 def test_10_cosmic_blackbody_photons_present(self):
    subset=[v for v in self.S if v['z_boundary']=='300' and v['T_gas_K']=='105.0' and v['initial_HD_J']=='2']
    self.assertTrue(subset)
    self.assertTrue(all(float(v['expected_photons_absorbed'])>0 and float(v['P_first_v0_by_stimulated'])>0 for v in subset))
 def test_11_total_energy_path_identity(self):
    self.assertLess(max(abs(float(v['Q_net_to_radiation_J_per_initial'])+float(v['Q_net_to_collisional_bath_J_per_initial'])-float(v['Q_net_internal_release_J_per_initial'])) for v in self.S),1e-31)
 def test_12_photon_mark_counts_with_spectra(self):
    self.assertEqual(len(self.L),4704)
    example=[v for v in self.L if v['T_gas_K']=='55.0' and v['n_Hplus_cm_minus3']=='1000.0' and v['z_boundary']=='300' and v['initial_HD_J']=='6' and v['source_lane']=='EMAA_primary']
    self.assertEqual(len(example),42)
    row=next(v for v in self.S if v['T_gas_K']=='55.0' and v['n_Hplus_cm_minus3']=='1000.0' and v['z_boundary']=='300' and v['initial_HD_J']=='6' and v['source_lane']=='EMAA_primary')
    for field,fieldrow in [('count_spontaneous','expected_photons_spontaneous'),('count_stimulated','expected_photons_stimulated'),('count_absorbed','expected_photons_absorbed')]:
       self.assertLess(abs(sum(float(v[field]) for v in example)-float(row[fieldrow])),2e-12)
    self.assertLess(abs(sum(float(v['net_energy_to_radiation_J']) for v in example)-float(row['Q_net_to_radiation_J_per_initial'])),3e-31)
 def test_13_crossovers_brent(self):
    roots=load_csv('R41_HALF_RADIATIVE_DENSITY_700.csv')
    self.assertTrue(all(abs(float(v['P_radiative_at_root'])-.5)<2e-11 for v in roots))
    self.assertTrue(all(1.e3<float(v['nHplus_radiative_collision_equal_cm_minus3'])<1.e6 for v in roots))
 def test_14_parent_collision_only_exact_result(self):
    with (ROOT/'source_private/R40_FIRST_V0_HIT_BRANCHES_1680.csv').open(newline='') as f:
        par=list(csv.DictReader(f))
    x={(float(v['T_K']),int(v['initial_J']),int(v['final_v0_J']),v['source_lane']):float(v['P_first_v0_hit']) for v in par}
    for T in (55.,1005.):
      for label,over in [('EMAA_primary',None),('GL_printed_hybrid',self.over)]:
       C=owner.bath_rates(self.data,T,1.,over)
       z=np.zeros_like(C)
       rr=solve_case(self.data,self.A,self.U,self.E,C,[z,z,z])
       for j in range(7):
        for ak,aidx in enumerate(self.A):
          self.assertLess(abs(rr['B'][ak,j]-x[(T,j,self.data['levels'][aidx+1]['J'],label)]),2e-14)
 def test_15_80_digit_independent_inverse(self):
    mp.dps=80
    for T,n,z in [(55.,1.e3,'OFF'),(105.,1.e5,'300')]:
     r,_=radiative_components(self.data,z)
     for lab,ov in [('EMAA',None),('GL',self.over)]:
      C=owner.bath_rates(self.data,T,n,ov);K=C+sum(r)
      u,a=self.U,self.A
      H=mp.matrix([[mp.mpf(str(-K[i,j])) for j in u] for i in u]);S=mp.matrix([[mp.mpf(str(K[i,j])) for j in u] for i in a])
      rr=solve_case(self.data,a,u,self.E,C,r)
      for j in (0,3,6):
       e=mp.matrix([int(t==j) for t in range(7)])
       dwell=mp.lu_solve(H,e);p=S*dwell
       for ai in range(12):self.assertLess(abs(float(p[ai])-rr['B'][ai,j]),5.e-13)
 def test_16_density_suppression_of_source_difference(self):
    s=load_csv('R41_SOURCE_CONTRAST_1750.csv')
    def at(n):return float(next(v for v in s if v['T_gas_K']=='55.0' and v['n_Hplus_cm_minus3']==str(float(n)) and v['z_boundary']=='OFF' and v['initial_HD_J']=='6')['P_first_v0_destination_L1_GL_minus_EMAA'])
    self.assertGreater(at(1.e6),.17)
    self.assertLess(at(1.),.0002)
 def test_17_source_protected_no_new_smatrix(self):
    s=json.loads((ROOT/'results/SUMMARY.json').read_text());self.assertEqual(s['canonical_DAG'],'34/49_UNCHANGED')
    self.assertEqual(s['R6_distinct_author'],'NOT_RUN');self.assertEqual(s['C9_distinct_author'],'NOT_RUN')
    self.assertEqual(s['owner_ack'],'NOT_OBTAINED')
 def test_18_MECHANISM_are_distinct(self):
    for x in self.S:
     self.assertAlmostEqual(float(x['P_first_v0_by_radiative']),float(x['P_first_v0_by_spontaneous'])+float(x['P_first_v0_by_stimulated']),places=13)

 def test_19_external_source_known_links(self):
    S,Eoutside,rows=source_owned_external_radiative_exit(self.data,self.U,'300')
    self.assertEqual(len(rows),62)
    self.assertEqual(S.shape,(33,7));self.assertGreater(S.sum(),0)
    self.assertEqual(source_owned_external_radiative_exit(self.data,self.U,'OFF')[0].sum(),0)
 def test_20_radiative_external_exit_probability_partition(self):
    x=load_csv('R41_KNOWN_RADIATIVE_OUTSIDE_EXIT_3500.csv')
    self.assertEqual(len(x),3500)
    self.assertLess(max(abs(float(v['P_sum'])-1) for v in x),1.e-12)
    self.assertTrue(all(abs(float(v['P_first_v0_any'])+float(v['P_first_radiative_exit_outside_HD19'])-1)<1.e-12 for v in x))
 def test_21_no_external_boundary_when_radiation_off(self):
    x=load_csv('R41_KNOWN_RADIATIVE_OUTSIDE_EXIT_3500.csv')
    self.assertTrue(all(float(v['P_first_radiative_exit_outside_HD19'])==0 for v in x if v['z_boundary']=='OFF'))
    old={(float(v['T_gas_K']),float(v['n_Hplus_cm_minus3']),v['z_boundary'],int(v['initial_HD_J']),v['source_lane']):v for v in self.S}
    for v in x:
     if v['z_boundary']!='OFF':continue
     w=old[float(v['T_gas_K']),float(v['n_Hplus_cm_minus3']),v['z_boundary'],int(v['initial_HD_J']),v['source_lane']]
     self.assertLess(abs(float(v['P_first_v0_collision'])-float(w['P_first_v0_by_collision'])),1.e-12)
 def test_22_high_z_external_exit(self):
    x=load_csv('R41_KNOWN_RADIATIVE_OUTSIDE_EXIT_3500.csv')
    z=next(v for v in x if v['T_gas_K']=='55.0' and v['n_Hplus_cm_minus3']=='1000.0' and v['z_boundary']=='300' and v['initial_HD_J']=='6' and v['source_lane']=='EMAA_primary')
    self.assertGreater(float(z['P_first_radiative_exit_outside_HD19']),.14)
    self.assertLess(float(z['P_first_radiative_exit_outside_HD19']),.16)
 def test_23_external_line_probability_sum(self):
    x=load_csv('R41_OUTSIDE_RADIATIVE_ESCAPE_LINES_124.csv')
    self.assertEqual(len(x),124)
    group={}
    for row in x:group.setdefault(row['source_lane'],[]).append(row)
    self.assertEqual(set(group),{'EMAA_primary','GL_printed_hybrid'})
    expected=load_csv('R41_KNOWN_RADIATIVE_OUTSIDE_EXIT_3500.csv')
    for label,rows in group.items():
     self.assertEqual(len(rows),62)
     v=next(z for z in expected if z['T_gas_K']=='55.0' and z['n_Hplus_cm_minus3']=='1000.0' and z['z_boundary']=='300' and z['initial_HD_J']=='6' and z['source_lane']==label)
     self.assertLess(abs(sum(float(r['P_exit_via_this_radiative_line']) for r in rows)-float(v['P_first_radiative_exit_outside_HD19'])),2e-13)
 def test_24_external_open_energy_identity(self):
    x=load_csv('R41_KNOWN_RADIATIVE_OUTSIDE_EXIT_3500.csv')
    self.assertLess(max(abs(float(v['net_energy_to_radiation_J_per_initial'])+float(v['net_energy_to_collisional_bath_J_per_initial'])-float(v['net_internal_release_J_per_initial'])) for v in x),1.e-31)
 def test_25_external_mpmath80(self):
    mp.dps=80
    for T,n,z in [(55.,1.e3,'300'),(1005.,1.e6,'100')]:
      rr,_=radiative_components(self.data,z)
      S,Eout,_=source_owned_external_radiative_exit(self.data,self.U,z)
      C=owner.bath_rates(self.data,T,n)
      K=C+sum(rr)
      uu=np.ix_(self.U,self.U)
      Kuu=K[uu]-np.diag(S.sum(axis=0))
      H=mp.matrix([[mp.mpf(str(-Kuu[i,j])) for j in range(7)] for i in range(7)])
      sink=mp.matrix([[mp.mpf(str(x)) for x in row] for row in S])
      done=solve_source_open_boundary(self.data,self.A,self.U,self.E,C,rr,S,Eout)
      for j in (0,3,6):
         v=mp.matrix([int(k==j) for k in range(7)])
         d=mp.lu_solve(H,v);pe=sink*d
         self.assertLess(abs(float(sum(pe))-float(done['B_out'][:,j].sum())),2e-13)

if __name__=='__main__':unittest.main(verbosity=2)
