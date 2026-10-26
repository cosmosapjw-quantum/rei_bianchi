"""Finite z=2.479 GRID044 donor state mapped into REC119's native Y convention.

Only the adjacent saved abundance and temperature columns are interpolated.
No orbit, spectrum, or physical-time derivative is constructed.
"""
import hashlib
import math
from pathlib import Path
import sys

import numpy as np

UNIT = Path(__file__).resolve().parents[1]
DONOR = UNIT / "intake/donor/event_consumer_20261026/runtime_inputs/endpoint/grid044_history.npz"
DONOR_SHA256 = "ae20c278239787c020e45028a6d6804cb9f056b75076a1d5ab045c0a7389733b"
N_REF0_M3 = 0.19078721280843758
SOURCE_Z = 2.479
DONOR_LABELS_BY_REC = (
    "n", "H1_0", "H1_1", "D_0", "D_1", "T_0", "T_1",
    "He3_0", "He3_1", "He3_2", "He4_0", "He4_1", "He4_2",
    "Li6_0", "Li6_1", "Li6_2", "Li6_3",
    "Li7_0", "Li7_1", "Li7_2", "Li7_3")
READER_DIR = UNIT / "intake/donor/event_consumer_20261026/runtime_inputs/helpers"
sys.path.insert(0, str(READER_DIR))
from donor_projection import SavedBackground


def read_matched_snapshot(network):
    if hashlib.sha256(DONOR.read_bytes()).hexdigest() != DONOR_SHA256:
        raise ValueError("GRID044_DONOR_IDENTITY_MISMATCH")
    with np.load(DONOR, allow_pickle=False) as data:
        eta = np.asarray(data["eta"], dtype=float)
        donor_x = np.asarray(data["atomic_abundance_per_Href"], dtype=float)
        temperature = np.asarray(data["temperature_K"], dtype=float)
        labels = tuple(str(v) for v in data["atomic_state_labels"])
        n_href = np.asarray(data["nH_ref_cm3"], dtype=float)
        redshifts = np.asarray(data["z"], dtype=float)
    if (eta.shape != (201,) or donor_x.shape != (21, 201) or
        temperature.shape != (201,) or len(labels) != 21 or len(set(labels)) != 21 or
        n_href.shape != (201,) or redshifts.shape != (201,) or
        set(labels) != set(DONOR_LABELS_BY_REC) or
        len(network.names) != 21 or
        tuple(network.names) != (
            "n","H1I","H1II","DI","DII","TI","TII","He3I","He3II","He3III",
            "He4I","He4II","He4III","Li6I","Li6II","Li6III","Li6IV",
            "Li7I","Li7II","Li7III","Li7IV") or
        not np.all(np.isfinite(eta)) or not np.all(np.diff(eta) > 0) or
        not np.all(np.isfinite(donor_x)) or
        not np.all(np.isfinite(temperature)) or np.any(temperature <= 0) or
        not np.all(np.isfinite(n_href)) or np.any(n_href <= 0) or
        not np.all(np.isfinite(redshifts))):
        raise ValueError("GRID044_STATE_DOMAIN_OR_LABELS_INVALID")
    eta_star = math.log(21.0/(1.0+SOURCE_Z))
    index = int(np.searchsorted(eta, eta_star, side="right"))-1
    if not 0 <= index < eta.size-1 or not eta[index] <= eta_star <= eta[index+1]:
        raise ValueError("SOURCE_ETA_NOT_IN_UNIQUE_ADJACENT_DONOR_CELL")
    theta = (eta_star-eta[index])/(eta[index+1]-eta[index])
    if not 0 <= theta <= 1:
        raise ValueError("INVALID_CONVEX_SNAPSHOT_WEIGHT")
    z_computed = 21*np.exp(-eta[[index,index+1]])-1
    z_residual = float(np.max(np.abs(z_computed-redshifts[[index,index+1]])/(1+z_computed)))
    if z_residual > 128*np.finfo(float).eps:
        raise ValueError("DONOR_REDSHIFT_ETA_MAPPING_MISMATCH")
    perm = [labels.index(name) for name in DONOR_LABELS_BY_REC]
    endpoint_x = donor_x[perm][:,[index,index+1]]
    if np.any(endpoint_x < 0):
        raise ValueError("MATCHED_BRACKET_POPULATION_NEGATIVE")
    x = (1-theta)*donor_x[perm,index]+theta*donor_x[perm,index+1]
    t = (1-theta)*temperature[index]+theta*temperature[index+1]
    if np.any(x < 0):
        raise ValueError("MATCHED_INTERPOLATED_STATE_NEGATIVE")
    beta = float(network.A @ x)
    if not math.isfinite(beta) or beta <= 0 or not math.isfinite(t) or t <= 0:
        raise ValueError("INVALID_NATIVE_NORMALIZATION_OR_TEMPERATURE")
    r_from_first = float(n_href[0]*math.exp(-3*eta_star)*1e6)
    r_from_today = N_REF0_M3*(1+SOURCE_Z)**3
    r_residual = abs(r_from_first-r_from_today)/r_from_today
    if r_residual > 2e-12:
        raise ValueError("DONOR_REFERENCE_DENSITY_NORMALIZATION_MISMATCH")
    r = r_from_first
    y = x/beta
    nb = beta*r
    background = SavedBackground(DONOR,DONOR_SHA256,
                                 {"eta":[201],"H":[201],"b":[201],"s":[201]})
    h,b,dbdeta = background.fields(eta_star)
    isotope_totals = {name:{"endpoints":[float(np.sum(endpoint_x[list(indices),j])) for j in (0,1)],
                            "snapshot":float(np.sum(x[list(indices)]))}
                      for name,indices in network.isotope_groups.items()}
    return {"Y": y, "temperature_K": float(t), "nb_m3": nb,
            "x_per_Href": x, "reference_density_m3": r,
            "beta_baryons_per_Href": beta, "source_z": SOURCE_Z,
            "eta": eta_star, "bracketing_indices": [index,index+1],
            "bracketing_eta": [float(eta[index]),float(eta[index+1])],
            "theta": theta, "minimum_population": float(np.min(y)),
            "bracketing_z": [float(redshifts[index]),float(redshifts[index+1])],
            "bracketing_x_per_Href": endpoint_x.tolist(),
            "bracketing_temperature_K": [float(temperature[index]),float(temperature[index+1])],
            "isotope_totals": isotope_totals,
            "z_eta_residual": z_residual, "r_reference_relative_residual": r_residual,
            "geometry": {"H_s_inverse":float(h),"b":float(b),
                         "db_deta":float(dbdeta),"s_s_inverse":float(h*dbdeta)},
            "donor_sha256": DONOR_SHA256,
            "representation": "adjacent_convex_eta_on_saved_x_and_T",
            "continuum_interpolation_error": None,
            "not_a_new_trajectory": True}
