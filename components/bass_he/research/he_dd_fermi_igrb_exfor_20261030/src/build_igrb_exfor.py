"""Source-backed 2015 Fermi IGRB × Arends-EXFOR conditional diagnostic.

The Fermi intensities are measured integrated photon number per energy BIN.
EXFOR gives only six source-reported SIG point values, not event calibration.
The rate-like numerical diagnostic is NOT R_event and NOT deposited heat.
No inferred redshift history, helium target environment or hot D transport.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path

from scipy.integrate import quad

C_CMS = 2.99792458e10
NB_CM2 = 1e-33
M_ALPHA_C2 = 3727.3794118  # exact frozen parent decimal, MeV
M_D_C2 = 1875.61294500
Q_MEV = 2 * M_D_C2 - M_ALPHA_C2
FERMI_CURATED_SHA256 = '8d0ec7ed7f62882a73e74ccd7485b80bdca5db3e7a61b7f432ee4ac59deee777'
EXFOR_CURATED_SHA256 = '2e14076cffe194bfa87ebb61748cf13ed095bd93139d1018ffc13cfdf23de559'
SPECTRAL_INDEX = 2.32              # Fermi 2015 fitted Model A
CUTOFF_MEV = 279000.0             # Fermi 2015 fitted Model A, 279 GeV


def load_data(root: Path):
    fermi_bytes = (root / "data/fermi_2015_table3_two_bins.json").read_bytes()
    exfor_bytes = (root / "data/exfor_M0475_SIG6.json").read_bytes()
    if hashlib.sha256(fermi_bytes).hexdigest() != FERMI_CURATED_SHA256:
        raise ValueError("CURATED_FERMI_DATA_IDENTITY_MISMATCH")
    if hashlib.sha256(exfor_bytes).hexdigest() != EXFOR_CURATED_SHA256:
        raise ValueError("CURATED_EXFOR_DATA_IDENTITY_MISMATCH")
    fermi = json.loads(fermi_bytes)
    exfor = json.loads(exfor_bytes)
    if fermi["doi"] != "10.1088/0004-637X/799/1/86" or fermi["foreground_model"] != "A":
        raise ValueError("UNQUALIFIED_FERMI_INPUT")
    if fermi["bins"][0]["energy_min_MeV"] != 200 or fermi["bins"][1]["energy_max_MeV"] != 400:
        raise ValueError("FERMI_ENERGY_RANGE_CHANGED")
    if exfor["raw_source_git_blob"] != "c49433293921dbb012d7f1b0387745732a598efa":
        raise ValueError("EXFOR_SOURCE_IDENTITY_CHANGED")
    if [r[0] for r in exfor["rows"]] != [201,225,253,285,320,359]:
        raise ValueError("EXFOR_ENERGY_COORDINATES_CHANGED")
    return fermi, exfor


def interpolate_sigma(E: float, rows):
    """Explicit piecewise-linear model, ONLY 201 <= E <= 359 MeV."""
    if not (rows[0][0] <= E <= rows[-1][0]):
        raise ValueError("NO_UNMEASURED_ENERGY_EXTRAPOLATION")
    for (x0,s0,_), (x1,s1,_) in zip(rows,rows[1:]):
        if x0 <= E <= x1:
            return float(s0) + (float(s1)-float(s0))*(E-x0)/(x1-x0)
    raise AssertionError("interval not found")


def spectral_shape(E: float, mode: str):
    """Dimensionless within-bin source-model, NOT a measured intra-bin spectrum."""
    if mode == "fermi_global_fit":
        return (E/100)**(-SPECTRAL_INDEX) * math.exp(-E/CUTOFF_MEV)
    if mode == "flat_within_bin":
        return 1.0
    raise ValueError("UNKNOWN_SPECTRAL_MODEL")


def integral_with_knots(fn, lo: float, hi: float, knots):
    nodes = [lo] + [x for x in knots if lo < x < hi] + [hi]
    return sum(quad(fn,a,b,epsabs=1e-14,epsrel=1e-11)[0] for a,b in zip(nodes,nodes[1:]))


def compute(root: Path, mode="fermi_global_fit"):
    fermi, exfor = load_data(root)
    rows = exfor["rows"]
    sigma_knots = [float(row[0]) for row in rows]
    out = {
        "schema": "BASS_HE_FERMI_IGRB_EXFOR_LOCAL_REPORTED_SIG_DIAGNOSTIC_V1",
        "observable": "per_helium_source_reported_cross_section_weighted_flux_only",
        "fermi_source": fermi["doi"], "exfor_raw_git_blob": exfor["raw_source_git_blob"],
        "scenario": "observer-local Fermi 2015 IGRB/EGB as isotropic He-rest photon field",
        "intra_bin_model": mode, "cross_section_model": "linear_between_measured_EXFOR_SIG_points_only",
        "energy_restriction_MeV": [201,359],
        "Fermi_shape_gamma": SPECTRAL_INDEX if mode == "fermi_global_fit" else None,
        "Fermi_shape_Ecut_MeV": CUTOFF_MEV if mode == "fermi_global_fit" else None,
        "mass_defect_Q_MeV": Q_MEV,
        "bins": [], "totals": {},
        "event_normalization": None, "cosmological_redshift_history": None,
        "R_event": None, "heat_rate": None, "D_fast_transport": None,
        "physical_activation": False, "L4": False, "production": "HOLD",
        "uncertainty_limitations": [
            "EXFOR per-row statistical uncertainty not treated as joint covariance",
            "Fermi foreground uncertainty across bins correlated unknown",
            "interpolation curvature and spectral shape within bin not statistically bounded",
            "two sources sample different experiments/epochs and unknown proper He frame",
            "both energy-edge regions [200,201] and [359,400] excluded, not extrapolated"]
    }
    for key in ("IGRB","EGB"):
        totals = {"rate_like_per_He_s_minus1":0.0,"kinetic_like_MeV_per_He_s":0.0,
                  "photon_number_density_in_two_bins_cm_minus3":0.0,
                  "Fermi_stat_sd_independent_only_s_minus1":0.0,
                  "Fermi_foreground_plus_s_minus1":0.0,"Fermi_foreground_minus_s_minus1":0.0}
        stat_var = 0.0
        for b in fermi["bins"]:
            b_lo,b_hi = b["energy_min_MeV"],b["energy_max_MeV"]
            lo,hi = max(b_lo,201),min(b_hi,359)
            I = float(b[f"{key}_intensity"])
            stat = float(b[f"{key}_stat_sd"])
            fgplus=float(b[f"{key}_fg_plus"])
            fgminus=float(b[f"{key}_fg_minus"])
            denominator=integral_with_knots(lambda E:spectral_shape(E,mode),b_lo,b_hi,[])
            if lo>=hi:
                raise ValueError("EMPTY_COVERED_ENERGY_DOMAIN")
            def weight(E):
                return spectral_shape(E,mode)/denominator
            fraction=integral_with_knots(weight,lo,hi,[])
            effsigma=integral_with_knots(lambda E: weight(E)*interpolate_sigma(E,rows),lo,hi,sigma_knots)
            effenergy=integral_with_knots(lambda E: weight(E)*interpolate_sigma(E,rows)*(E-Q_MEV),lo,hi,sigma_knots)
            coeff = 4*math.pi*NB_CM2*effsigma
            rate=I*coeff
            kinetic=I*4*math.pi*NB_CM2*effenergy
            stat_var+=(stat*coeff)**2
            totals["rate_like_per_He_s_minus1"]+=rate
            totals["kinetic_like_MeV_per_He_s"]+=kinetic
            totals["photon_number_density_in_two_bins_cm_minus3"]+=4*math.pi*I/C_CMS
            totals["Fermi_foreground_plus_s_minus1"]+=fgplus*coeff
            totals["Fermi_foreground_minus_s_minus1"]+=fgminus*coeff
            out["bins"].append({
                "component":key,"Fermi_bin_MeV":[b_lo,b_hi],"included_support_MeV":[lo,hi],
                "measured_integrated_intensity_cm_minus2_s_minus1_sr_minus1":I,
                "measured_stat_sd":stat,"measured_fg_model_plus":fgplus,"measured_fg_model_minus":fgminus,
                "modeled_fraction_within_EXFOR_support":fraction,
                "conditional_flux_weighted_sigma_nb":effsigma,
                "conditional_flux_weighted_sigma_K_nb_MeV":effenergy,
                "conditional_rate_like_per_He_s_minus1":rate,
                "conditional_born_kinetic_like_MeV_per_He_s":kinetic})
        totals["Fermi_stat_sd_independent_only_s_minus1"] = math.sqrt(stat_var)
        out["totals"][key] = totals
    return out


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--root',type=Path,required=True)
    p.add_argument('--mode',choices=['fermi_global_fit','flat_within_bin'],default='fermi_global_fit')
    p.add_argument('--out',type=Path,default=None)
    args=p.parse_args()
    result=compute(args.root,args.mode)
    output=json.dumps(result,indent=2,sort_keys=True)+'\n'
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(output)
    else:print(output)

if __name__=='__main__':main()
