#!/usr/bin/env python3
"""BASS_HE: proof of frozen-REI four-photon-group/Puchwein-D1 six-moment cone mismatch.
One source-conditioned physical adapter decision, not a reionization IVP or UVB no-go.
Extended 18-test local implementation and full original archive: see full Drive ZIP.
"""
from __future__ import annotations
import argparse,csv,hashlib,json
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PARENT="research/rei_igm_p19_native_receiver_20261101/"
THIS="research/rei_rux04_p19_native_source_cone_20261101/"
INPUT_SHAS={
 PARENT+"results/SCIENCE_RESULTS.json":"gitblob:c9a088215c48165aa86f07c6470e93b1d2615141",
 PARENT+"results/ORIGINAL_FOUR_GROUP_PHOTON_ENERGY.csv":"76211946a47ce05c2460422d043317f71db230fa39aae28469193dddef1e9c9f",
 PARENT+"inputs/REI_original_heating_moment_owner.csv":"c4764a24083e86748ff52b18d432577c0d60be267d7e73092565ce0c9451b804"}
STATE_SHA="cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01"
ARTIFACT_SHA="4f332c7a9c21f93dcfadb0d7e4e40ef4ec7ec7f150f6d4b8b39f309560155e17"
GROUPS=("G1","G2a","G2b","G3");SPECIES=("HI","HeI","HeII")
EV=F("1.602176634e-12")
def load(root):
 root=Path(root)
 for f,digest in INPUT_SHAS.items():
  data=(root/f).read_bytes(); got=("gitblob:"+hashlib.sha1(f"blob {len(data)}\0".encode()+data).hexdigest()) if digest.startswith("gitblob:") else hashlib.sha256(data).hexdigest()
  if got!=digest:raise ValueError("BASS_HE source pin mismatch "+f)
 sci=json.loads((root/(PARENT+"results/SCIENCE_RESULTS.json")).read_text())
 src=json.loads((root/(THIS+"source/REI_FOUR_GROUP_SOURCE_SHARES.json")).read_text())
 if src["origin_rei_artifact_sha256"]!=ARTIFACT_SHA or src["original_state_array_sha256"]!=STATE_SHA:raise ValueError("REI source owner drift")
 if sci["physical_nodes"]!=46080 or sci["native_source_state_array_sha256"]!=STATE_SHA or sci["z"]!=5.95:raise ValueError("original REI frozen state mismatch")
 with (root/(PARENT+"inputs/REI_original_heating_moment_owner.csv")).open() as f:
  heats={(q["species"],q["group"]):F(q["canonical_excess_eV"]) for q in csv.DictReader(f)}
 if set(heats)!={(s,g) for s in SPECIES for g in GROUPS}:raise ValueError("original 12 energy owners absent")
 rows=src["rows"]
 if len(rows)!=4 or [a["group"] for a in rows]!=list(GROUPS):raise ValueError("4 source groups absent")
 p=[[F(a["p"][s]) for a in rows] for s in SPECIES]
 for j,a in enumerate(rows):
  if any(p[i][j]<0 for i in range(3)) or abs(sum(p[i][j] for i in range(3))+F(a["p_external"])-1)>F("2e-15"):raise ValueError("original photon conservation")
 return sci,p,heats
def compute(root):
 sci,p,h=load(root)
 positive=[j for j in range(4) if p[0][j]>0]
 if not positive:raise ValueError("HI groups absent")
 r=min(p[1][j]/p[0][j] for j in positive)
 dual=[p[1][j]-r*p[0][j] for j in range(4)]
 if min(dual)<0:raise AssertionError("invalid exact rate cone dual")
 Emin=min(h["HI",GROUPS[j]] for j in positive)
 heii=[h["HeII",GROUPS[j]] for j in range(4) if p[2][j]>0]
 if len(set(heii))!=1:raise ValueError("different HeII spectral support")
 out={"schema":"BASS_HE_REI_RUX04_NATIVE_FOUR_GROUP_SIX_MOMENT_CONE_VERIFIER_V1",
 "original_state_array_sha256":STATE_SHA,"central_rei":"28/88_REPORTED","BASS_HE_physical":"14/18_REPORTED",
 "source_group_count":4,"real_original_nodes_reused":46080,"r_min_HeI_per_HI":float(r),
 "native_HI_mean_excess_min_eV":float(Emin),"native_HeII_excess_eV":float(heii[0]),
 "dual_column_slacks":[float(x) for x in dual],"new_cosmological_ivps":0,"canonical_delta":0,
 "rux02":"EFFECTIVE_SOURCE_CONTEXT","rux03":"NATIVE_SPECTRAL_OPACITY_OWNER_MISMATCH","rux04":"NOT_ADMITTED",
 "scope":"original fixed z5.95 REI 46k neutral state, native absorber allocation/energy calibration fixed; allow arbitrary nonnegative 4 group currents, P19 D1 effective target is FORMAL",
 "cases":{}}
 for mode in ("log","linear"):
  a=sci["P19_"+mode+"_counterfactual"];events=[F(str(a["absorbed_events_per_s"][s])) for s in SPECIES]
  heat=[F(str(a["source_excess_heat_erg_s"][s]))/EV for s in SPECIES]
  if not all(x>0 for x in events+heat):raise ValueError("nonpositive P19 formal target")
  dual_violation=r*events[0]-events[1]
  hi_heat_violation=Emin*events[0]-heat[0]
  heii_heat_violation=heat[2]-heii[0]*events[2]
  if not all(x>0 for x in (dual_violation,hi_heat_violation,heii_heat_violation)):raise AssertionError("counterfactual adapter was not actually excluded")
  lower=dual_violation/(r*events[0]+events[1])
  out["cases"][mode]={"HeI_over_HI_target":float(events[1]/events[0]),
    "HeI_HI_event_dual_violation_s":float(dual_violation),
    "rate_relative_minimax_lower_bound":float(lower),
    "HI_excess_target_eV":float(heat[0]/events[0]),
    "HI_excess_energy_cone_violation_eV_s":float(hi_heat_violation),
    "HeII_excess_target_eV":float(heat[2]/events[2]),
    "HeII_energy_equality_violation_eV_s":float(heii_heat_violation),
    "minimum_HeI_events_if_HI_matched_s":float(r*events[0]),
    "minimum_HeI_to_target_factor_if_HI_matched":float(r*events[0]/events[1]),
    "three_rate_nonnegative_current_feasible":False,"six_moment_feasible":False}
 return out
if __name__=="__main__":
 a=argparse.ArgumentParser();a.add_argument("--repo",type=Path,default=ROOT);a.add_argument("--output",type=Path,required=True)
 x=a.parse_args();d=compute(x.repo);x.output.parent.mkdir(parents=True,exist_ok=True)
 x.output.write_text(json.dumps(d,indent=2,sort_keys=True)+"\n")
 print("BASS_HE_REI_RUX04_SOURCE_CONE",json.dumps({"r_min":d["r_min_HeI_per_HI"],"cases":d["cases"],"central":d["central_rei"],"HE":d["BASS_HE_physical"]},sort_keys=True))
