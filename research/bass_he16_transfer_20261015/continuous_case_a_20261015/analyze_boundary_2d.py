"""Native original MD14 source-only photon leakage in (energy bins, time steps).

These are 20 SOURCE-ONLY controls, not the coupled H/He solution.
They audit native Driver::deposit and geometry_map and distinguish a
fixed-grid artificial lower boundary stock from centroid physical support.
"""
import csv
import json
import hashlib
from pathlib import Path
import argparse

BINS=(4,8,16,32,64)
STEPS=(1,8,32,128)

def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1<<20),b""):
            h.update(block)
    return h.hexdigest()

def audit(path):
    with path.open(newline="") as stream:
        rows=list(csv.DictReader(stream))
    if len(rows)!=len(BINS)*len(STEPS):
        raise ValueError(f"Expected 20 native 2D controls; got {len(rows)}")
    keyed={}
    for row in rows:
        if None in row or any(v is None for v in row.values()):
            raise ValueError("Malformed source control record")
        m=int(row["cells_per_segment"])
        n=int(row["substeps"])
        if m not in BINS or n not in STEPS or (m,n) in keyed:
            raise ValueError("Unexpected case or duplicate")
        x={k:float(v) for k,v in row.items()}
        if abs(x["photon_count_residual_per_H"])>5e-16:
            raise ValueError("Native number conservation ledger failed")
        E_floor=x["native_lower_node_eV"]
        if not 13.599999999<=E_floor<=13.600000001:
            raise ValueError("Different original spectral boundary")
        if x["min_exact_source_centroid_end_eV"]<=E_floor:
            raise ValueError("Original finite source-centroid actually crossed boundary")
        if not 0.49<x["first_source_weight_on_lower_node"]<0.53:
            raise ValueError("Unexpected interpolation geometry")
        if abs(x["boundary_n_fraction"]-x["boundary_n_per_H"]/x["source_n_per_H"])>2e-14:
            raise ValueError("Native boundary ratio inconsistent with stocks")
        if abs(x["predicted_first_node_fraction"]-
               x["first_source_weight_on_lower_node"]*x["first_cell_photon_fraction"])>2e-14:
            raise ValueError("First source cell projection fraction inconsistent")
        if n==1 and abs(x["boundary_n_fraction"]-x["predicted_first_node_fraction"])>2e-14:
            raise ValueError("Single native step not equal to exact first-cell projection")
        keyed[m,n]=x
    if len(keyed)!=20:
        raise ValueError("Incomplete energy-time grid")
    for n in STEPS:
        sequence=[keyed[m,n]["boundary_n_fraction"] for m in BINS]
        if any(sequence[i+1]>=sequence[i] for i in range(4)):
            raise ValueError("Energy refinement did not reduce fixed-grid UV loss")
    for m in BINS:
        loss=[keyed[m,n]["boundary_n_fraction"] for n in STEPS]
        if any(v<=0 for v in loss):
            raise ValueError("Unexpected removal of source-grid ghost under time refinement")
        if loss[-1]<.999*loss[0]:
            raise ValueError("Time refinement unexpectedly removed source-grid first node")
        if abs(loss[-1]-loss[0])>0.0002*loss[0]*m:
            raise ValueError("Residual time-dependence unexpectedly large")
    convergence=[]
    for m in BINS:
        base=keyed[m,1]
        refined=keyed[m,128]
        convergence.append({
            "source_cells_per_threshold_segment":m,
            "time_steps_low":1,
            "time_steps_high":128,
            "loss_fraction_one_step":base["boundary_n_fraction"],
            "loss_fraction_128_steps":refined["boundary_n_fraction"],
            "loss_percent_one_step":100*base["boundary_n_fraction"],
            "loss_percent_128_steps":100*refined["boundary_n_fraction"],
            "initial_two_node_exact_loss":base["predicted_first_node_fraction"],
            "m_times_loss_fraction_128":m*refined["boundary_n_fraction"],
            "source_first_centroid_eV":refined["first_source_centroid_eV"],
            "minimum_exact_centroid_endpoint_eV":refined["min_exact_source_centroid_end_eV"],
            "relative_change_from_1_to_128":(
                refined["boundary_n_fraction"]/base["boundary_n_fraction"]-1),
            "photon_number_error_per_H":refined["photon_count_residual_per_H"]
        })
    scaling=[]
    for m,ne in zip(BINS[:-1],BINS[1:]):
        f=keyed[m,128]["boundary_n_fraction"]
        g=keyed[ne,128]["boundary_n_fraction"]
        scaling.append({"bins_from":m,"bins_to":ne,
                        "boundary_ratio_fine_over_coarse":g/f})
    return {
        "schema":"rei.md14.native_source_energy_time_convergence.v1",
        "scientific_scope":"Native cold MD14 original source + native deposit/geometry_map; no absorption, recombination or CMB; finite source-cell centroid representation, not the continuous BB50K SED",
        "cases":len(keyed),
        "source_energy_bins_per_segment":list(BINS),
        "time_steps":list(STEPS),
        "source_original_proper_clock":True,
        "exact_initial_first_cell_projection_identity":True,
        "all_finite_source_centroids_physically_above_13p6_at_endpoint":True,
        "source_only_no_gas":True,
        "source_only_binary_original_rlib_epoch":"fa00a6f73f45e8ac391b5bb723b30d162005bf79750138b1a13e84ec82248f67",
        "observed_fixed_resolution_time_refinement_nonvanishing":True,
        "empirical_energy_grid_scaling":"approximately first order 1/N_E for tested group sizes, NOT a rigorous continuum SED limit",
        "grid":convergence,
        "energy_refinement_pairs":scaling,
        "input_sha256":sha(path),
        "scientific_admission":"SCOPED_SOURCE_ONLY_C8_NUMERICALLY_CHECKED_NOT_FULL_EOR"
    }

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--csv",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    result=audit(args.csv)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({"cases":result["cases"],"grid":result["grid"],
         "energy_refinement_pairs":result["energy_refinement_pairs"]},indent=2))
