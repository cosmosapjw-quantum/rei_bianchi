#!/usr/bin/env python3
"""Read saved final-source native output. Never imports/executes native solvers."""
from pathlib import Path
import datetime
import hashlib
import json
import math
import tarfile

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "implementation/receipts"
WORK = ROOT.parent
Y = 0.2454 / (4 * (1 - 0.2454))
CHI = (13.598434599702, 24.587389011, 54.41776)
EV = 1.602176634e-12
KB = 1.380649e-16
C = 29979245800.
HPLANCK = 6.62607015e-27
SIGMA_T = 6.6524587051e-25
ME = 9.1093837139e-28
B = ((16-math.sqrt(6))/36, (16+math.sqrt(6))/36, 1/9)
ARAD = 8 * math.pi**5 * KB**4 / (15 * HPLANCK**3 * C**3)
CMB_COEFF = 4 * SIGMA_T * ARAD * KB / (ME * C)
source_names = [
    "v16_work/implementation/src/lib.rs",
    "v16_work/implementation/src/main.rs",
    "v16_work/implementation/tests/focused.rs",
    "v15_work/native_owner/rust/rei_microphysics/src/axbi_native_rhs.rs",
    "v15_work/native_owner/rust/rei_microphysics/src/axbi_covariant_transport.rs",
    "v15_work/native_owner/rust/rei_microphysics/src/igm_state.rs",
    "v15_work/native_owner/rust/rei_microphysics/src/igm_thermal.rs",
    "v15_work/native_owner/rust/rei_microphysics/src/axbi_rates.rs",
    "v16_work/vigilode_intake/native_source_closure/crates/rodas5p-integrators/src/radau.rs",
    "v16_work/vigilode_intake/native_source_closure/crates/rodas5p-integrators/src/nonlinear.rs",
    "v16_work/vigilode_intake/native_source_closure/crates/rodas5p-integrators/src/problem.rs",
]

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def read(p):
    return json.loads(p.read_text())

stats = {}
counts = {"stages": 0, "chemicals": 0, "negative_cmb_stages": 0,
          "positive_cmb_stages": 0, "zero_cmb_stages": 0,
          "stage_domain_failures": 0, "empty_layout_stages": 0,
          "photon_cells_checked": 0, "point_cells_checked": 0,
          "post_birth_layout_connections": 0}
failures = []
temperatures = []
reported_solver_maxima = {"max_scaled_stage_residual": 0., "max_scaled_endpoint_closure": 0., "library_wrms": 0.}
max_affine_mismatch_by_component = [0.]*6
max_physical_endpoint_by_component = [0.]*6

def compare(name, actual, expected, scale=None):
    error = abs(actual-expected)
    scale = max(abs(actual), abs(expected), 1e-300) if scale is None else max(scale, 1e-300)
    value = stats.setdefault(name, {"max_absolute": 0., "max_scaled": 0., "count": 0})
    value["max_absolute"] = max(value["max_absolute"], error)
    value["max_scaled"] = max(value["max_scaled"], error/scale)
    value["count"] += 1

def flatten(obj, prefix=""):
    if isinstance(obj, dict):
        for k,v in obj.items():
            yield from flatten(v, prefix+"/"+k)
    elif isinstance(obj, list):
        for k,v in enumerate(obj):
            yield from flatten(v, prefix+"/"+str(k))
    else:
        yield prefix, obj

def physical_photons(ch, vector):
    ns=[]; us=[]
    for cell in ch["cell_coordinates"]:
        n=vector[cell["number_index"]] * cell["nscale"]
        j=cell["offset_index"]
        u=cell["lo"]*n + (0. if j is None else vector[j]*(cell["hi"]-cell["lo"])*cell["nscale"])
        ns.append(n); us.append(u)
    return math.fsum(ns), math.fsum(us)

def endpoints(ch):
    end=ch["stages"][2]["scaled_state"]
    start=[v-math.fsum(B[j]*ch["stages"][j]["increments"][k] for j in range(3)) for k,v in enumerate(end)]
    return start, end

def check_chemical(ch, a, aref, label):
    counts["chemicals"] += 1
    for key in reported_solver_maxima:
        reported_solver_maxima[key]=max(reported_solver_maxima[key],ch[key])
    for j in range(6):
        max_affine_mismatch_by_component[j]=max(max_affine_mismatch_by_component[j],abs(ch["affine_identity_mismatch"][j]))
        max_physical_endpoint_by_component[j]=max(max_physical_endpoint_by_component[j],abs(ch["physical_endpoint_closure"][j]))
    dt=ch["dt_s"]
    start, _ = endpoints(ch)
    compare("fresh_w_coordinate", start[3], 1.)
    for cell in ch["cell_coordinates"]:
        compare("fresh_number_coordinate", start[cell["number_index"]], 1.)
    if len(ch["stages"]) != 3:
        failures.append([label, "wrong_stage_count"])
    for stage in ch["stages"]:
        counts["stages"] += 1
        st=stage["scaled_state"]; x,y,z=st[:3]
        temperature=2 * stage["w_ev"] * EV / (3 * KB * (1+Y+x+Y*(y+2*z)))
        temperatures.append(temperature)
        valid=0<=x<=1 and y>=0 and z>=0 and y+z<=1 and st[3]>0 and 1<=temperature<=1e6
        valid=valid and len(st)==ch["dimension"] and all(math.isfinite(v) for v in st)
        for cell in ch["cell_coordinates"]:
            counts["photon_cells_checked"] += 1
            n=st[cell["number_index"]]; j=cell["offset_index"]
            valid=valid and n>0 and cell["nscale"]>0
            if j is None:
                counts["point_cells_checked"] += 1
                valid=valid and cell["lo"]==cell["hi"]
            else:
                valid=valid and 0<=st[j]<=n and cell["hi"]>cell["lo"]
        if not valid:
            counts["stage_domain_failures"] += 1
            failures.append([label, stage["stage"], "stage_domain"])
        compare("gas_w_decode", stage["w_ev"], st[3]*ch["wscale"])
        compare("stage_weight", stage["weight"], B[stage["stage"]])
        compare("stage_dt", stage["dt_s"], dt)
        ev=stage["events_per_h_s"]
        sign="negative" if ev["cmb"]<0 else "positive" if ev["cmb"]>0 else "zero"
        counts[sign+"_cmb_stages"] += 1
        expected_cmb=CMB_COEFF*(x+Y*(y+2*z))*(2.7255/a)**4*(2.7255/a-temperature)/EV
        compare("signed_cmb_native_constant_reconstruction", ev["cmb"], expected_cmb)
        if not ch["cell_coordinates"]:
            counts["empty_layout_stages"] += 1
            if stage["nodes"] != 0 or any(ev["p"]) or ev["photo_heat"] != 0 or ev["photo_binding"] != 0:
                failures.append([label, stage["stage"], "empty_layout_photo_nonzero"])
        for j in range(3):
            compare("photo_species_node_ownership", ev["p"][j], stage["node_photo_per_h_s"][j])
        compare("photo_binding_node_ownership", ev["photo_binding"], stage["node_binding_ev_per_h_s"])
        compare("photo_heat_node_ownership", ev["photo_heat"], stage["node_heat_ev_per_h_s"])
        binding_p=math.fsum(CHI[j]*ev["p"][j] for j in range(3))
        compare("photo_binding_stoichiometry", ev["photo_binding"], binding_p)
        radiation=math.fsum(ev["ce"]+ev["rr"]+[ev["dr"],ev["ff"]])
        escape=math.fsum(CHI[j]*ev["r"][j] for j in range(3))+CHI[1]*ev["d"]+radiation
        compare("escape_ownership", ev["escape"], escape)
        f=[(k-1e-13*r)/dt for k,r in zip(stage["increments"],stage["scaled_residual"])]
        net=[ev["p"][j]+ev["c"][j]-ev["r"][j] for j in range(3)]
        total_event_scale=math.fsum(ev["p"]+ev["c"]+ev["r"]+[ev["d"]])
        compare("H_rhs_from_raw_stage_residual", f[0], net[0], total_event_scale)
        compare("HeII_rhs_from_raw_stage_residual", Y*f[1], net[1]-ev["d"]-net[2], total_event_scale)
        compare("HeIII_rhs_from_raw_stage_residual", Y*f[2], net[2], total_event_scale)
        compare("electron_rhs_from_raw_stage_residual", f[0]+Y*(f[1]+2*f[2]), math.fsum(net)-ev["d"], total_event_scale)
        ci=math.fsum(CHI[j]*ev["c"][j] for j in range(3))
        thermal=ev["photo_heat"]-ci-radiation+ev["cmb"]
        compare("thermal_rhs_native_ownership", f[3]*ch["wscale"], thermal, abs(ev["photo_heat"])+ci+radiation+abs(ev["cmb"]))
        ndot, udot=physical_photons(ch,f)
        compare("photon_number_rhs", ndot, -math.fsum(ev["p"]), total_event_scale)
        compare("photon_proper_energy_rhs", udot*aref/a, -ev["photo_heat"]-binding_p, abs(ev["photo_heat"])+binding_p)
    leaves=[dict(flatten(st["events_per_h_s"])) for st in ch["stages"]]
    for name, reported in flatten(ch["integrated"]):
        expected=math.fsum(dt*B[j]*leaves[j][name] for j in range(3))
        compare("common_stage_event_quadrature",reported,expected)
    for j in range(6):
        expected=(ch["weighted_physical_stage_residual"][j]+ch["physical_endpoint_closure"][j]+ch["weighted_native_point_identity"][j])
        compare("affine_decomposition_absolute_only",ch["invariant_defect"][j],expected,1.)

matrix=read(BASE/"MATRIX_RECEIPT.json")
binary=ROOT/"implementation/target/release/rei-vigilode-radau-research"
binary_sha256=sha(binary)
cases=[]
loaded={}
for case in matrix["cases"]:
    p=WORK/case["receipt"]
    inputs=read(p/"inputs.json"); outcome=read(p/"outcome.json"); raw=read(p/"raw.json")
    source_matches={name:sha(WORK/name)==inputs["source_sha256"][name] for name in source_names}
    with tarfile.open(p/"sources.tar.gz","r:gz") as tar:
        archive_source_matches={name:hashlib.sha256(tar.extractfile(name).read()).hexdigest()==inputs["source_sha256"][name] for name in source_names}
    source_tar_match=sha(p/"sources.tar.gz")==inputs["source_archive_sha256"]
    stdout=(p/"stdout.txt").read_text(); stderr=(p/"stderr.txt").read_text()
    log_hash_matches=sha(p/"stdout.txt")==outcome["stdout_sha256"] and sha(p/"stderr.txt")==outcome["stderr_sha256"]
    terminal=f'COMPLETE native_rhs={raw["native_rhs_attempts_including_fd_replay"]}'
    completion=(outcome["exit_code"]==0 and not outcome["truncated"] and raw["completed"] and raw["failure"] is None and len(raw["records"])==case["N"] and terminal in stderr and not stdout)
    source_binding=all(source_matches.values()) and all(archive_source_matches.values()) and source_tar_match and log_hash_matches and list(inputs["executables_sha256"].values())==[binary_sha256] and matrix["binary_sha256"]==binary_sha256
    if not completion or not source_binding:
        failures.append([p.name,"receipt_or_source_binding"])
    cases.append({"case":p.name,"mode":raw["mode"],"method":raw["method"],"N":raw["N"],"exit_code":outcome["exit_code"],"truncated":outcome["truncated"],"completion_checks":completion,"source_binding_checks":source_binding,"started_utc":inputs["started_utc"],"finished_utc":outcome["finished_utc"],"native_rhs_attempts":raw["native_rhs_attempts_including_fd_replay"],"files":{name:sha(p/name) for name in ["inputs.json","outcome.json","raw.json","stdout.txt","stderr.txt","sources.tar.gz"]}})
    loaded[(raw["mode"],raw["method"],raw["N"])]=raw
    if raw["method"]!="radau":
        continue
    aref=raw["initial"]["a"]
    for rec in raw["records"]:
        label=f'{p.name}/step{rec["step"]}'
        rep=rec["report"]
        if raw["mode"]=="fixed":
            check_chemical(rep,aref,aref,label)
        else:
            for j,seg in enumerate(rep["segments"]):
                check_chemical(seg["chemical"],seg["midpoint"],aref,label+f'/segment{j}')
            for j,birth in enumerate(rep["births"]):
                prev=rep["segments"][j]["chemical"]; nex=rep["segments"][j+1]["chemical"]
                prev_end=endpoints(prev)[1]; next_start=endpoints(nex)[0]
                pn,pu=physical_photons(prev,prev_end); nn,nu=physical_photons(nex,next_start)
                # Stage 3 is the stiffly accurate accepted endpoint up to float summation.
                compare("post_birth_new_layout_N",nn-pn,birth["added_n"],max(nn,pn,birth["added_n"]))
                added_uref=birth["added_u"]*birth["a"]/aref
                compare("post_birth_new_layout_Uref",nu-pu,added_uref,max(nu,pu,added_uref))
                counts["post_birth_layout_connections"] += 1

birth_layouts={}
for mode in ["birth","disabled"]:
    for n in [4,8,16]:
        r=loaded[(mode,"radau",n)]; s=loaded[(mode,"ssprk",n)]
        birth_layouts[f'{mode}_n{n}']={"first_dimensions":[x["chemical"]["dimension"] for x in r["records"][0]["report"]["segments"]],"first_nodes":[[t["nodes"] for t in x["chemical"]["stages"]] for x in r["records"][0]["report"]["segments"]]}
        for ri,si in zip(r["records"],s["records"]):
            for rb,sb in zip(ri["report"]["births"],si["report"]["births"]):
                for key in rb:
                    compare("matched_method_birth_"+key,rb[key],sb[key])

baseline=read(ROOT/"BASE_NATIVE_MANIFEST.json")
preservation={}
for rel,expected in baseline.items():
    data=(WORK/"v15_work/native_owner/rust/rei_microphysics"/rel).read_bytes()
    if rel=="src/axbi_covariant_transport.rs":
        data=data.split(b"\n// Opt-in direct-node ODE adapter seam; original transport bytes preserved above.")[0]
    preservation[rel]=hashlib.sha256(data).hexdigest()==expected
if not all(preservation.values()):
    failures.append(["native_prefix_preservation",[k for k,v in preservation.items() if not v]])

result={"schema":"v16-independent-c9-readonly-crosscheck-v1","reviewer":"/root/drive_v15_intake (actual independent Astra subagent; no different-model claim)","utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"activity":"Saved-output analysis only; 0 native runs; 0 source edits; 0 cloud mutations", "source_sha256":{name:sha(WORK/name) for name in source_names},"matrix_receipt_sha256":sha(BASE/"MATRIX_RECEIPT.json"),"cases":cases,"counts":counts,"temperature_range_k":[min(temperatures),max(temperatures)],"raw_crosscheck_metrics":stats,"first_birth_layouts":birth_layouts,"native_preexisting_files":len(preservation),"native_preexisting_prefixes_preserved":all(preservation.values()),"structural_failures":failures,"limitations":["All-stage statements concern the 594 stored accepted/replayed Radau stages; transient Newton/FD trial states are not individually persisted.","Photon RHS reconstruction uses K minus the saved stage residual, not an independent native rerun.","Inferred chemical endpoints for birth layout checks use Radau stiff accuracy; summation error is retained in the measured residual.","No new refinement campaign, no nonlinear positivity theorem, no uniform stiff, signed Bianchi, Case B or full EoR admission.","Signed CMB is checked by an independent evaluation of the unchanged native analytic formula; the present hot-gas matrix samples its negative branch only."]}
result.update({"actual_binary_sha256":binary_sha256,"reported_solver_maxima":reported_solver_maxima,"max_affine_mismatch_by_component":max_affine_mismatch_by_component,"max_physical_endpoint_by_component":max_physical_endpoint_by_component})
(Path(__file__).parent/"C9_RUNTIME_CROSSCHECK.json").write_text(json.dumps(result,indent=2)+"\n")
print(json.dumps({"counts":counts,"structural_failures":failures,"temperatures":result["temperature_range_k"],"metric_maxima":{k:v for k,v in stats.items()},"native_preexisting_prefixes_preserved":result["native_preexisting_prefixes_preserved"]},indent=2))
