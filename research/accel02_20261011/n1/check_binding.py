"""New adapter point checks. No trajectory integration or RUN002 replay."""
import csv,hashlib,json,time
from pathlib import Path
import numpy as np
from provider import HistoryProvider,Native,HERE,REPO,EV_ERG

def main():
    started=time.perf_counter()
    binary=HERE/'native/target/release/rei_n1_native'
    native=Native(binary)
    rate_rows=[]
    try:
        rows=list(csv.DictReader((REPO/'rust/rei_microphysics/tests/data/igm_grackle/grackle_literal_reference.csv').open()))
        # Selected endpoints and joins verify that the linked provider is the import.
        # Existing complete96-row point suite is not replayed.
        selected=[min(rows,key=lambda row:abs(float(row['T_K'])-target)) for target in [1,20,100,5500,9284,1e4,1e5,1e6]]
        columns=['k2_HII_rr','k4_HeII_rr','k6_HeIII_rr','k1_HI_ci','k3_HeI_ci','k5_HeII_ci','k4_HeII_dr','reHII','reHeII1','reHeIII','reHeII2_matched','brem']
        for row in selected:
            actual=native.call('RATES',[float(row['T_K'])]);expected=np.array([float(row[k]) for k in columns])
            rel=np.divide(abs(actual-expected),abs(expected),out=np.zeros(12),where=expected!=0)
            assert np.all(actual[expected==0]==0)
            assert rel.max()<1e-11
            rate_rows.append({'T_K':float(row['T_K']),'max_relative':float(rel.max())})
        points=[]; source=[]
        for r in [0.,.1,-.1]:
            p=HistoryProvider(r)
            for t in np.linspace(0,p.end_time_s,17):
                g=p.geometry(float(t));gas=p.initial_gas.copy();gas[3]/=g['a_rel']**2
                # Constant fractions/adiabatic gas path is a point-domain probe,
                # not a coupled solution. Photons follow true pinned initial+source data.
                q=np.array([20.,40.,100.,6e4]);mu0=np.zeros(4);weights=np.full(4,.1)
                E,mu,_=p.ray(q,mu0,t);N=p.initial_photons(q,weights)
                S=p.source_reference(q,mu0,weights,t)
                nodes=np.column_stack([E,mu,N,S]);out=native.rhs(float(t),g,gas,nodes)
                assert max(abs(out[12]),abs(out[13]))<1e-12
                assert 1<=out[11]<=1e6
                points.append({'r':r,'time_s':float(t),'z':g['z'],'T_K':float(out[11]),'max_scaled_ledger':float(max(abs(out[12]),abs(out[13]))),'cmb_to_gas_ref':float(out[14])})
            if r==0:
                for z in [15.9,12.,8.,4.]:
                    em=p.tables['emissivity'];uv=p.tables['uvb'];emax=float(em.energies_eV[-1])
                    band=em.moment(13.598434599702,50000,z,proper_photons=True)
                    high=em.moment(50000,emax,z,proper_photons=True)
                    band_energy=em.moment(13.598434599702,50000,z,power=1,proper_photons=True)*EV_ERG
                    high_energy=em.moment(50000,emax,z,power=1,proper_photons=True)*EV_ERG
                    source.append({'source_ionizing_band_energy_erg_cm3_s':band_energy,'source_above50keV_energy_erg_cm3_s':high_energy,'omitted_high_energy_fraction':high_energy/(band_energy+high_energy),'z':z,'source_ionizing_band_per_cm3_s':band,'source_above50keV_per_cm3_s':high,'omitted_high_photon_fraction':high/(band+high),'initial_UVB_used':z==15.9})
        result={'claim':'implementation-verified bounded N1 adapter; point probes NOT coupled trajectories','binary_sha256':native.binary_sha256,'rates_selected_reference':rate_rows,'point_probes':points,'source_domain_points':source,'all_pass':True,'max_local_scaled_ledger':max(x['max_scaled_ledger'] for x in points),'checks_wall_s':time.perf_counter()-started,'criteria_unchanged':True,'RUN002_replayed':False}
        (HERE/'evidence/BINDING_CHECKS.json').write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps({k:v for k,v in result.items() if k not in ['point_probes','rates_selected_reference']},indent=2))
    finally:native.close()
if __name__=='__main__':main()
