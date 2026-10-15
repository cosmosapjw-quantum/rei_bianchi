"""Independent source-birth/Case-A gas ledger, GL16 rate, angular and UV tests."""
import argparse,csv,hashlib,json
from pathlib import Path

QS=(-.005,0.,.005); ETAS=(0.,1e-5); NSTEPS=(1,8,32,128)
FHE=.2454/(4*(1-.2454))
KBEV=1.380649e-16/1.602176634e-12
CHI=(13.598434599702,24.587389011,54.41776)

def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(2**20),b""): h.update(chunk)
    return h.hexdigest()

def csvdict(path):
    with path.open(newline="") as f:r=list(csv.DictReader(f))
    if len(r)!=48:raise ValueError("48 rows required for 24 A/B source cases")
    out={}
    for v in r:
        if None in v or None in v.values(): raise ValueError("CSV alignment")
        k=(float(v["q_ref"]),float(v["eta_initial"]),int(v["substeps"]))
        if k[0] not in QS or k[1] not in ETAS or k[2] not in NSTEPS or \
           v["transport"] not in ("PROJECTED","COVARIANT") or \
           int(v["source_cells_per_segment"])!=16:
            raise ValueError("Source identity changed")
        if v["transport"] in out.setdefault(k,{}):raise ValueError("Duplicate case")
        out[k][v["transport"]]=v
    if len(out)!=24 or any(len(x)!=2 for x in out.values()):raise ValueError("Missing cases")
    return out

def data_reference(path):
    with path.open(newline="") as f:r=list(csv.DictReader(f))
    v={float(x["q_ref"]):x for x in r}
    if set(v)!=set(QS):raise ValueError("Reference missing q")
    return v

def atomic(x,y,z):
    return CHI[0]*x + FHE*(CHI[1]*(y+z)+CHI[2]*z)

def validate(r):
    get=lambda k:float(r[k])
    eta=get("eta_initial")
    x0=1-eta;y0=eta/2;z0=1-eta
    xe0=x0+FHE*(y0+2*z0)
    thermal0=1.5*KBEV*8.098143045064857*(1+FHE+xe0)
    atomic0=atomic(x0,y0,z0)
    emit=get("emitted_photons_per_H");emit_u=get("emitted_energy_eV_per_H")
    if emit<=0 or emit_u<=0:raise ValueError("MD14 source not positive")
    surv=get("surviving_photons_per_H");boundary=get("boundary_photons_per_H")
    pa=[get(k+"_absorbed_per_H") for k in ("HI","HeI","HeII")]
    ci=[get("CI_"+k+"_per_H") for k in ("HI","HeI","HeII")]
    rr=[get("RR_"+k+"_per_H") for k in ("HII","HeII","HeIII")]
    dr=get("DR_HeII_per_H")
    photon_count_res=emit-surv-boundary-sum(pa)
    photon_energy_res=emit_u - sum(get(k) for k in (
      "final_photon_energy_eV_per_H","binding_eV_per_H","photoheat_eV_per_H",
      "redshift_work_eV_per_H","grid_boundary_energy_eV_per_H"))
    if abs(photon_count_res)>2e-11*emit or abs(photon_energy_res)>2e-11*emit_u:
        raise ValueError("Original MD14 photon birth count or energy ledger")
    x=get("x_HII_final");y=get("x_HeII_final");z=get("x_HeIII_final")
    xexp=x0+pa[0]+ci[0]-rr[0]
    yexp=y0+(pa[1]+ci[1]-rr[1]-dr-pa[2]-ci[2]+rr[2])/FHE
    zexp=z0+(pa[2]+ci[2]-rr[2])/FHE
    if max(abs(x-xexp),abs(y-yexp),abs(z-zexp))>2e-11:
        raise ValueError("H/He nuclei event ledger")
    if x<0 or x>1+1e-12 or y<-1e-12 or z<0 or y+z>1+1e-12:
        raise ValueError("H/He simplex")
    electron=x+FHE*(y+2*z)
    delta_e=electron-xe0-(sum(pa)+sum(ci)-sum(rr)-dr)
    if abs(delta_e)>2e-11 or abs(electron-get("electron_per_H_final"))>2e-12:
        raise ValueError("Charge source")
    u=get("u_thermal_final_eV_per_H")
    t=get("Tgas_final_K")
    if not 1<=t<=1e6 or abs(u-1.5*KBEV*t*(1+FHE+electron))>1e-11:
        raise ValueError("Native EOS")
    binding=atomic(x,y,z)-atomic0-get("binding_eV_per_H")-get("micro_binding_eV_per_H")
    micro=get("micro_thermal_eV_per_H")+get("micro_binding_eV_per_H")+ \
           get("micro_escape_eV_per_H")-get("micro_cmb_to_gas_eV_per_H")
    gas=thermal0+get("photoheat_eV_per_H")+get("micro_thermal_eV_per_H")-\
        u-get("gas_adiabatic_loss_eV_per_H")
    total=emit_u+thermal0+atomic0+get("micro_cmb_to_gas_eV_per_H")-(
        get("final_photon_energy_eV_per_H")+u+atomic(x,y,z)+
        get("micro_escape_eV_per_H")+get("gas_adiabatic_loss_eV_per_H")+
        get("redshift_work_eV_per_H")+get("grid_boundary_energy_eV_per_H"))
    if max(abs(binding),abs(micro),abs(gas),abs(total))>5e-11:
        raise ValueError("Combined atomic/gas/CMB/emitter source energy ledger")
    F=get("final_flux_z_eV_per_H");P=get("final_P2_eV_per_H")
    U=get("final_photon_energy_eV_per_H")
    if U<0 or P<-.5*U-1e-10*U or P>U+1e-10*U or \
        3*F**2>U*(U+2*P)+1e-10*U**2:
        raise ValueError("Photon U,F,P2 positivity cone violated")
    if abs(F)>1e-9*U or abs(get("emitted_flux_z_eV_per_H"))>1e-9*emit_u or \
       abs(get("emitted_P2_eV_per_H"))>1e-9*emit_u:
        raise ValueError("Reflection/isotropic source angular moments mismatch")
    if int(r["number_of_birth_cohorts"])!=int(r["substeps"])*384:
        raise ValueError("Source-age cohort count mismatch")
    if r["transport"]=="COVARIANT" and (
        get("covariant_below_13p6_photons_per_H")!=0 or boundary!=0):
        raise ValueError("True covariant source photon crossed UV support")
    return {"photon_count_error":abs(photon_count_res),
      "photon_energy_error":abs(photon_energy_res),
      "atomic_binding_error":abs(binding),
      "gas_energy_error":abs(gas),
      "micro_energy_error":abs(micro),
      "total_energy_error":abs(total),
      "charge_error":abs(delta_e)}

def analyze(serial,parallel,gl16,support):
    a=csvdict(serial);b=csvdict(parallel)
    for k,p in a.items():
        for lane,x in p.items():
            for field,v in x.items():
                if field!="case_runtime_ms" and v!=b[k][lane][field]:
                    raise ValueError("Serial/parallel source physics not identical")
    refs=data_reference(gl16);sup=data_reference(support)
    all_errors=[validate(x) for pair in a.values() for x in pair.values()]
    runs=[]
    for (q,eta,n),pair in a.items():
        x=pair["PROJECTED"];y=pair["COVARIANT"]
        if x["emitted_photons_per_H"]!=y["emitted_photons_per_H"] or \
           x["emitted_energy_eV_per_H"]!=y["emitted_energy_eV_per_H"]:
            raise ValueError("Source birth not common to both arms")
        refN=float(refs[q]["N_photons_per_H_GL16"])
        count=float(x["emitted_photons_per_H"])
        err=abs(count-refN)/refN
        if err>1e-7:raise ValueError("Native MD14 photon birth inconsistent with direct GL16")
        if float(sup[q]["min_exact_end_E_ev"])<=13.6:raise ValueError("Physical UV support crossing")
        runs.append({
            "q_ref":q,"eta":eta,"steps":n,
            "source_birth_n_per_H":count,
            "source_birth_energy_ev_per_H":float(x["emitted_energy_eV_per_H"]),
            "birth_GL16_relative_error":err,
            "source_quadrupole_eV_per_H":float(x["emitted_P2_eV_per_H"]),
            "surviving_quadrupole_projected_eV_per_H":float(x["final_P2_eV_per_H"]),
            "surviving_quadrupole_covariant_eV_per_H":float(y["final_P2_eV_per_H"]),
            "projected_boundary_n_per_H":float(x["boundary_photons_per_H"]),
            "projected_boundary_ratio_of_births":float(x["boundary_photons_per_H"])/count,
            "covariant_photons_below_13p6_eV_per_H":float(y["covariant_below_13p6_photons_per_H"]),
            "min_source_true_final_E_eV":float(sup[q]["min_exact_end_E_ev"]),
            "delta_HII":float(x["x_HII_final"])-float(y["x_HII_final"]),
            "delta_HeIII":float(x["x_HeIII_final"])-float(y["x_HeIII_final"]),
            "delta_T_K":float(x["Tgas_final_K"])-float(y["Tgas_final_K"]),
            "delta_photo_HeII_per_H":float(x["HeII_absorbed_per_H"])-float(y["HeII_absorbed_per_H"]),
            "cohort_count":int(x["number_of_birth_cohorts"])
        })
    for q in QS:
        error_by_n={r["steps"]:r["birth_GL16_relative_error"] for r in runs if r["q_ref"]==q and r["eta"]==0}
        if error_by_n[128]>1e-10 or any(error_by_n[NSTEPS[i+1]]>1.05*error_by_n[NSTEPS[i]] for i in range(3)):
            raise ValueError("Source quadrature did not demonstrate expected convergence")
    return {"schema":"he18.axbi.native_MD14_source_casea_continuous_birth.v1",
            "scope":"One source-scoped original MD14 BB50K per-H emitter, 48 spectrum cells, 8 angular rays, cold original Grackle3.4.1 Case-A gas, two alternative photon transport schemes; no emitter star fluid or coupled OTS photon source",
            "status":"SOURCE_BACKED_NUMERICALLY_CHECKED_FULL_EOR_HOLD",
            "q":list(QS),"eta":list(ETAS),"steps":list(NSTEPS),
            "paired_cases":len(a),"individual_lanes":len(all_errors),
            "photon_moment_positivity_verified":True,
            "original_MD14_GL16_reference_sha256":sha(gl16),
            "original_source_support_sha256":sha(support),
            "source_epoch_full_rlib_distinct_from_original_frozen":True,
            "native_subagents":"NOT_RUN",
            "source_emitters_and_recombination_escape_as_physical_stress":False,
            "global_EOR_and_CMB_sci_admission":"HOLD",
            "max_ledger_abs":{k:max(v[k] for v in all_errors) for k in all_errors[0]},
            "measured":runs,
            "serial_sha256":sha(serial),"parallel_sha256":sha(parallel)}
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--serial",type=Path,required=True)
    p.add_argument("--parallel",type=Path,required=True)
    p.add_argument("--gl16",type=Path,required=True)
    p.add_argument("--support",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    data=analyze(a.serial,a.parallel,a.gl16,a.support)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(data,indent=2)+"\n")
    print(json.dumps({"pairs":data["paired_cases"],"lanes":data["individual_lanes"],
      "maxledger":data["max_ledger_abs"],
      "q0eta0_128":next(v for v in data["measured"] if v["q_ref"]==0 and v["eta"]==0 and v["steps"]==128)},indent=2))
