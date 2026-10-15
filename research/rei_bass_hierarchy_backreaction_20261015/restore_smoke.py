#!/usr/bin/env python3
"""Cold-restore executable scientific smoke test from bundled bytes alone.

Full original AX08 ~159MB history is deliberately excluded and not inferred.
Uses SHA-qualified 8193-node derived physical electron donor to run the real
BASS native Einstein-Vlasov and new REI gamma/neutrino Thomson+Pi background.
Also invokes original REI C11 Case-A/Grackle photon chemistry from the restored
C12 source dependencies, testing the actual short receiver coupling.

A PASS proves replayability of this *scoped* source and output, not continuum
EoR/AX11, full polarized collision, or original 312238-row donor restoration.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import sys
import numpy as np

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
sys.path.insert(0,str(HERE/"suppliers/bass/rei_axbi_initial_stress_20261015"))

from einstein_vlasov import Initial,KineticStressBackground
from lrs_boltzmann import SmoothElectronHistory,HierarchyBackground
from run_hierarchy import source_lock,public_sigma_from_q
from species_hierarchy import SpeciesHierarchy
from receiver_coupled import real_C11,Receiver

def digest(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""):
            h.update(b)
    return h.hexdigest()

def verify():
    input_file=HERE/"results/portable_electron_source_8193.csv"
    record=json.loads((HERE/"results/portable_electron_source_manifest.json").read_text())
    assert record["original_source_history_rows"]==312238
    assert record["saved_knots"]==8193
    assert record["original_historical_RAW_HISTORY_NOT_UPLOADED"]
    if digest(input_file)!=record["saved_file_sha256"]:
        raise RuntimeError("PORTABLE_DONOR_BYTES_CHANGED")
    knots=np.loadtxt(input_file,delimiter=",",skiprows=1,dtype=float)
    assert knots.shape==(8193,2)
    surrogate=SmoothElectronHistory(knots[:,0],knots[:,1],nodes=8193)
    assert np.max(abs(surrogate.density(knots[:,0])/knots[:,1]-1))<1e-10
    base=source_lock()
    actual=KineticStressBackground(Initial(0.,+.2))
    expected=actual.at_a(base.aend)
    no_thomson=SpeciesHierarchy(base,2.7255,8,kappa_gamma=.2,kappa_nu=.2)
    source_thomson=SpeciesHierarchy(base,2.7255,8,kappa_gamma=.2,kappa_nu=.2,
                                   ne_source=surrogate)
    sa,aa,_=no_thomson.integrate(n=101)
    sb,bb,_=source_thomson.integrate(n=101)
    assert abs(sa.y[1,-1]-expected["b"])<1e-10
    assert bb[-1]["E_gamma"][2]<aa[-1]["E_gamma"][2]
    assert abs(bb[-1]["N_gamma"][0]-1)<3e-12
    assert abs(bb[-1]["N_nu"][0]-1)<3e-12
    old_results=json.loads((HERE/"results/gamma_neutrino_separate.json").read_text())
    historical=old_results["case_results"][2]
    delta_source=float(bb[-1]["Sigma"]-historical["endpoint_Sigma"])
    # This uses reconstructed exact same positive C2 nodes; rounding of
    # recorded double numbers may shift an ODE run by about local solver rtol.
    if abs(delta_source)>2e-10:
        raise RuntimeError("RESTORED_REI_EINSTEIN_THOMSON_NOT_EQUIVALENT")
    c11=real_C11(nsteps=32,nmu=8,ne=8)
    assert abs(c11["final"]["x_HII"]-.7513295747730638)<3e-11
    assert c11["max_energy_eV_H"]<1e-10
    # Actual short receiver: BASS independent initial radiation, real CaseA ne.
    new=HierarchyBackground(base,8,1.,+.2,0.,0.)
    pre,_=new.integrate(n=101)
    initial=np.r_[base.xmax,pre.y[1:,-1]]
    path1,diag1,_=Receiver(new,c11,True).solve(initial,n=61)
    path0,diag0,_=Receiver(new,c11,False).solve(initial,n=61)
    diff=diag1[-1]["radiation_J2"]-diag0[-1]["radiation_J2"]
    if not(-1e-7<diff<-1e-9):
        raise RuntimeError("RESTORED_REI_C11_THOMSON_DRIVEN_QUAD_OUTSIDE_VALIDATED_SCALE")
    result={
        "schema":"rei.bass_hierarchy_backup_standalone_restore_replay.v1",
        "status":"PASS_BASS_EINSTEIN_VLASOV_GAMMA_NU_C11_ACTUAL_CODE",
        "source_historical_raw_data_loaded":False,
        "portable_derived_source_sha256":record["saved_file_sha256"],
        "source_original_history_sha256":record["original_OWNER_history_sha256"],
        "BASS_frozen_case_b_mismatch":float(sa.y[1,-1]-expected["b"]),
        "restored_coupled_Sigma_minus_reference":delta_source,
        "sampled_gamma_number_N0":float(bb[-1]["N_gamma"][0]),
        "sampled_nu_number_N0":float(bb[-1]["N_nu"][0]),
        "actual_C11_HHe_recombination_energy_residual_eV_H":c11["max_energy_eV_H"],
        "actual_C11_HHe_final_x_HII":c11["final"]["x_HII"],
        "short_receiver_delta_J2_with_true_C11_electrons":float(diff),
        "numerical_scientific_equivalence_scope":"actual source-dependent small positive electron donor; full original 312238 raw source not included; no global new reionization physics",
        "scientific_admission":"NOT_ISSUED"
    }
    return result

if __name__=="__main__":
    print(json.dumps(verify(),indent=2))
