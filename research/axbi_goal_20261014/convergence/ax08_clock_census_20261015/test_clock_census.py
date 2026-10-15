#!/usr/bin/env python3
"""Public small fixtures for AX08 matching-clock and 6-species census contract."""
from __future__ import annotations
import csv,math,tempfile,unittest
from pathlib import Path
import numpy as np
import clock_census as cc

class ClockCensus(unittest.TestCase):
    def test_baryon_registry_mass_per_nucleus(self):
        # Ybaryon is n_i/n_b. Multiply by A=4 for helium.
        self.assertAlmostEqual(.7546+4*.06135,1.,places=15)
        self.assertGreater(abs(.7546+.06135-1),.18)

    def test_exact_clock_split_manufactured(self):
        a=np.linspace(.05,.2,201)
        Z=np.zeros((len(a),len(cc.COLS)))
        S=np.zeros_like(Z)
        for arr,scale in ((Z,1.),(S,.96)):
            arr[:,0]=scale*(a-.05)*1e6
            arr[:,1]=a
            arr[:,2]=1/a-1
            arr[:,3]=1-.01-2*a
            arr[:,4]=.01+2*a
            arr[:,5]=1-.05-.3*a
            arr[:,6]=.05+.3*a
            arr[:,7]=0
            arr[:,8]=1e-3/a**3
            arr[:,9]=arr[:,8]*(arr[:,4]+.0813*arr[:,6])
            arr[:,10]=20+150*a
            arr[:,11]=0
        result,grid,plot,*_=cc.compare(Z,S,nodes=97)
        self.assertEqual(result["matched_time_nodes"],97)
        for name in ("x_HII","x_HeII","temperature_K"):
            v=result["observables"][name]
            self.assertLess(v["max_abs_delta_fixed_scale"],1e-13)
            self.assertGreater(v["max_abs_clock_contribution"],0)
            self.assertLess(v["exact_discrete_decomposition_error"],1e-13)

    def test_full_synthetic_six_nuclear_rows(self):
        with tempfile.TemporaryDirectory() as td:
            fn=Path(td)/"abundances.csv"
            hdr=["run_id","time_s","species_id","nproper","element_fraction",
                 "Ybaryon","electron_xe","charge","A","Tgas_K"]
            times=(0,100)
            H=np.zeros((2,len(cc.COLS)))
            # nH=1, nHe=.1; so baryon denominator 1.4.
            with fn.open("w",newline="") as f:
                out=csv.writer(f)
                out.writerow(hdr)
                for k,t in enumerate(times):
                    hion=.2+.2*k
                    heion=.1+.2*k
                    hepp=.05+.01*k
                    amounts=[1-hion,hion,.1*(1-heion-hepp),.1*heion,.1*hepp]
                    electron=amounts[1]+amounts[3]+2*amounts[4]
                    H[k,0]=t;H[k,1]=.1+.01*k;H[k,2]=1/H[k,1]-1
                    H[k,3:8]=[1-hion,hion,1-heion-hepp,heion,hepp]
                    H[k,8]=1;H[k,9]=electron;H[k,10]=1000+30*k
                    for i,name in enumerate(cc.SPECIES):
                        ni=amounts[i] if i<5 else electron
                        frac=([1-hion,hion,1-heion-hepp,heion,hepp][i] if i<5 else "")
                        y=(ni/1.4 if i<5 else 0.)
                        out.writerow(["ZERO",t,name,ni,frac,y,
                                      electron if i==5 else "",
                                      (-1 if i==5 else 1), (1 if i<2 else 4 if i<5 else 0),
                                      H[k,10]])
            old=cc.N
            try:
                cc.N=2
                result=cc.census(fn,H,"ZERO")
            finally:
                cc.N=old
            self.assertEqual(result["rows"],12)
            self.assertLess(max(result["max_abs_residuals"].values()),5e-9)
            self.assertAlmostEqual(result["initial_nHe_per_nH"],.1)

    def test_malformed_initial_source_case_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"source.csv"
            with p.open("w") as f:
                f.write(",".join(cc.COLS)+"\n"+"1,2\n")
            with self.assertRaises(ValueError):
                cc.history(p)

    def test_reject_incomplete_synthetic_census(self):
        with tempfile.TemporaryDirectory() as td:
            f=Path(td)/"abundances.csv"
            f.write_text("run_id,time_s,species_id,nproper,element_fraction,Ybaryon,electron_xe,charge,A,Tgas_K\n")
            old=cc.N
            try:
                cc.N=2
                with self.assertRaisesRegex(ValueError,"TRUNCATED_6_SPECIES_GROUP"):
                    cc.census(f,np.zeros((2,len(cc.COLS))),"ZERO")
            finally:cc.N=old

if __name__=="__main__":
    unittest.main()
