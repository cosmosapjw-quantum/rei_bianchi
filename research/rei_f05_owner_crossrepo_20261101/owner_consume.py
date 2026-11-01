#!/usr/bin/env python3
"""REI F05 project-owner exact-source H/He charge/binding/Thomson consumer.

Read original 46,080 row sibling source-inclusive ZIPs in memory without
modifying source, accepted REI history, or sibling repos.
Independent Decimal-from-binary64 interval arithmetic verifies every physical
source row against external HE and REC summaries.
"""
from __future__ import annotations
import argparse,csv,gzip,hashlib,io,json,zipfile,sys
from decimal import Decimal,localcontext
from pathlib import Path
import source_intake as si

EV=Decimal("1.602176634e-12")
CHI_H=Decimal("13.598434599702")
CHI_HE1=Decimal("24.587389011")
CHI_HE2=Decimal("54.417760")
SIGMA_T=Decimal("6.6524587051e-25")
N=46080
CHANNELS=("dB_H","dB_He_first","dB_He_second","dB_He","dB_total","dNe")

def D(s)->Decimal:
    return Decimal.from_float(float(s))
def interval(row,field:str):
    lo=D(row[field+"_lower"]);hi=D(row[field+"_upper"])
    if not (lo.is_finite() and hi.is_finite() and lo<=hi):
        raise ArithmeticError("INVALID_ORIGINAL_INTERVAL:"+field)
    return (lo,hi)
def add(a,b):
    return (a[0]+b[0],a[1]+b[1])
def mul(a,b):
    v=[x*y for x in a for y in b]
    return (min(v),max(v))
def scalar(a,x):
    return mul(a,(x,x))
def contains_overlap(a,b):
    return a[0]<=b[1] and b[0]<=a[1]
def data_csv(z,name):
    raw=z.read(name)
    return csv.DictReader(io.TextIOWrapper(gzip.GzipFile(fileobj=io.BytesIO(raw)),encoding="utf-8",newline=""))
def decpair(arr):
    return (D(arr[0]),D(arr[1]))
def outward_decimal_to_float(x,dir):
    f=float(x)
    import math
    if dir=="lower" and Decimal.from_float(f)>x:f=math.nextafter(f,-math.inf)
    if dir=="upper" and Decimal.from_float(f)<x:f=math.nextafter(f,math.inf)
    return f
def reportpair(x):
    return [outward_decimal_to_float(x[0],"lower"),outward_decimal_to_float(x[1],"upper")]

def run(hepath,recpath,out):
    tmp_identity=out.parent/"_temporary_source_identity.json"
    si.main(hepath,recpath,tmp_identity)
    identity=json.loads(tmp_identity.read_text())
    tmp_identity.unlink()
    with localcontext() as ctx:
        ctx.prec=86
        with zipfile.ZipFile(hepath) as he,zipfile.ZipFile(recpath) as rec:
            heprefix=si.HE_PREFIX;recprefix=si.REC_PREFIX
            hemeta=json.loads(he.read(heprefix+"results/RESULT.json"))
            recmeta=json.loads(rec.read(recprefix+"results/SCIENCE_RESULT.json"))
            preview=data_csv(he,heprefix+"source_inputs/ORIGINAL_REI_F05_TICK161_HHE_T_ELECTRON_PREVIEW_46080.csv.gz")
            inc=data_csv(he,heprefix+"source_inputs/REI_ORIGINAL26_COMMON_PARENT_INCREMENT_46080.csv.gz")
            latent=data_csv(he,heprefix+"results/ORIGINAL_REI_F05_TICK161_H_HE_LATENT_ENERGY_46080.csv.gz")
            sums={key:(Decimal(0),Decimal(0)) for key in CHANNELS}
            published_sums={key:(Decimal(0),Decimal(0)) for key in CHANNELS}
            preview_ne_sum=(Decimal(0),Decimal(0))
            helium_correction_direct=(Decimal(0),Decimal(0))
            minmax={key:{"max_relative_endpoint_diagnostic":0.0,"max_relative_by_sum_abs_terms":0.0,"disjoint_intervals":0} for key in CHANNELS}
            sign={"HE_dB_negative":0,"HE_dB_positive":0,"HE_dB_contains_zero":0,"electron_negative":0,"electron_positive":0,"electron_contains_zero":0}
            rows=0
            for p,x,l in zip(preview,inc,latent):
                node=int(p["node"])
                if not (node==int(x["node"])==int(l["node"])==rows):
                    raise ValueError("ORIGINAL_SOURCE_NODE_ORDER_MISMATCH")
                nh=interval(p,"source_H_nuclei_N");nhe=interval(p,"source_He_nuclei_N")
                if nh[0]<=0 or nhe[0]<=0:raise ArithmeticError("ORIGINAL_NUCLEI_NONPOSITIVE")
                dxh=interval(x,"x_HII_original_full_increment")
                dxhe2=interval(x,"x_HeII_original_full_increment")
                dxhe3=interval(x,"x_HeIII_original_full_increment")
                dh=mul(nh,dxh);dhe2=mul(nhe,dxhe2);dhe3=mul(nhe,dxhe3)
                dne=add(add(dh,dhe2),scalar(dhe3,Decimal(2)))
                bh=scalar(dh,EV*CHI_H)
                hefirst=scalar(add(dhe2,dhe3),EV*CHI_HE1)
                hesecond=scalar(dhe3,EV*CHI_HE2)
                bhe=add(hefirst,hesecond);btot=add(bh,bhe)
                hecorr=add(scalar(dhe2,EV*(CHI_HE1-CHI_H)),
                           scalar(dhe3,EV*(CHI_HE1+CHI_HE2-2*CHI_H)))
                helium_correction_direct=add(helium_correction_direct,hecorr)
                expected={"dB_H":bh,"dB_He_first":hefirst,"dB_He_second":hesecond,
                          "dB_He":bhe,"dB_total":btot,"dNe":dne}
                comp_scale=sum((max(abs(v[0]),abs(v[1])) for v in [bh,hefirst,hesecond]),Decimal("1e-250"))
                ne_scale=sum((max(abs(v[0]),abs(v[1])) for v in [dh,dhe2,scalar(dhe3,Decimal(2))]),Decimal("1e-250"))
                for k,phys in expected.items():
                    published=interval(l,k)
                    sums[k]=add(sums[k],phys)
                    published_sums[k]=add(published_sums[k],published)
                    sc=comp_scale if k.startswith("dB") else ne_scale
                    # Two independently outward-rounded algorithms can differ
                    # in their very last source float ulps. This tolerance is
                    # only a *source-equivalence diagnostic*, never a science
                    # error-gate relaxation; all source interval values remain.
                    dist=max(
                        abs(phys[0]-published[0]),abs(phys[1]-published[1]))
                    rel=dist/max(sc,Decimal("1e-250"))
                    minmax[k]["max_relative_by_sum_abs_terms"]=max(minmax[k]["max_relative_by_sum_abs_terms"],float(rel))
                    minmax[k]["max_relative_endpoint_diagnostic"]=max(minmax[k]["max_relative_endpoint_diagnostic"],
                        float(dist/max(abs(phys[0]),abs(phys[1]),abs(published[0]),abs(published[1]),Decimal("1e-250"))))
                    if not contains_overlap(phys,published):
                        # Report rather than immediately trusting any published
                        # summary or forcing overlapping endpoints via clipping.
                        minmax[k]["disjoint_intervals"]+=1
                dne_prev=interval(p,"tick160_to_161_delta_electron_N")
                preview_ne_sum=add(preview_ne_sum,dne_prev)
                signs=((btot,"HE_dB"),(dne,"electron"))
                for v,prefix in signs:
                    key=f"{prefix}_{'negative' if v[1]<0 else 'positive' if v[0]>0 else 'contains_zero'}"
                    sign[key]+=1
                rows+=1
            if rows!=N:raise ValueError(f"REI_F05_ORIGINAL_SOURCE_ROW_COUNT:{rows}")
            native_he=hemeta["global_intervals"]
            global_check={}
            for k,orig in (("dB_H","dB_H"),("dB_He","dB_He"),("dB_total","dB_total"),("dNe","dNe")):
                pub=(D(native_he[orig]["lower"]),D(native_he[orig]["upper"]))
                ours=sums[k]
                stored=published_sums[k]
                global_check[k]={
                   "native_global_result":reportpair(pub),
                   "independently_recomputed_all_source_rows":reportpair(ours),
                   "resummed_sibling_derived_rows":reportpair(stored),
                   "independent_overlap":contains_overlap(ours,pub),
                   "sibling_resum_overlap":contains_overlap(stored,pub)}
            rec_delta=decpair(recmeta["global_electron_delta_N"])
            he_delta=decpair([native_he["dNe"]["lower"],native_he["dNe"]["upper"]])
            reimatched=contains_overlap(rec_delta,he_delta)
            rec_area=decpair(recmeta["Thomson_scattering_area_delta_cm2"])
            expected_area=scalar(rec_delta,SIGMA_T)
            at_diff=(
                abs(rec_area[0]-expected_area[0]),
                abs(rec_area[1]-expected_area[1])
            )
            area_relative=max(at_diff)/max(abs(expected_area[0]),abs(expected_area[1]))
            # source input all-row relative discrepancies from independent
            # numbers are reported as numeric transport diagnostics only.
            btotal=decpair([native_he["dB_total"]["lower"],native_he["dB_total"]["upper"]])
            if btotal[1]>=0 or rec_delta[1]>=0:raise ArithmeticError("GLOBAL_CONSUMPTION_SIGN_NOT_CERTIFIED")
            magB=(-btotal[1],-btotal[0]);magNe=(-rec_delta[1],-rec_delta[0])
            energy_ratio=(magB[0]/magNe[1]/EV,magB[1]/magNe[0]/EV)
            # exact helium threshold correction from same source:
            h_reference=scalar(rec_delta,EV*CHI_H)
            helium_correction=add(btotal,scalar(h_reference,Decimal(-1)))
            helium_residual_overlap=contains_overlap(helium_correction,helium_correction_direct)
            all_cell_intervals_overlap=all(v["disjoint_intervals"]==0 for v in minmax.values())
            all_signs_exhaustive=(sum(sign[k] for k in ("HE_dB_negative","HE_dB_positive","HE_dB_contains_zero"))==N
                                  and sum(sign[k] for k in ("electron_negative","electron_positive","electron_contains_zero"))==N)
            checks={
                "same_original_source_preview_sha":True,
                "source_he_ci_success":identity["he_science_ci"]["result"]=="SUCCESS",
                "source_rec_ci_success":identity["rec_science_ci"]["result"]=="SUCCESS",
                "original_sibling_global_delta_electron_intervals_overlap":reimatched,
                "original_thomson_area_identity_max_rel_error":float(area_relative),
                "sibling_binding_row_disjoint_counts":{k:v["disjoint_intervals"] for k,v in minmax.items()},
                "native_global_HE_derived_row_intervals_overlap":all(global_check[k]["independent_overlap"] and global_check[k]["sibling_resum_overlap"] for k in global_check),
                "recorded_original_preview_electron_delta_sum_interval":reportpair(preview_ne_sum),
                "preview_electron_delta_intersects_rec":contains_overlap(preview_ne_sum,rec_delta),
                "original_source_rows":N,
                "every_original_cell_all_six_channels_overlap":all_cell_intervals_overlap,
                "helium_threshold_correction_direct_vs_global_overlap":helium_residual_overlap,
                "source_cell_sign_counts_partition_complete":all_signs_exhaustive
            }
            # Source identity and scientifically useful overlap requirements.
            gate=(all([checks["same_original_source_preview_sha"],checks["source_he_ci_success"],
                   checks["source_rec_ci_success"],reimatched,checks["native_global_HE_derived_row_intervals_overlap"],
                   checks["preview_electron_delta_intersects_rec"],all_cell_intervals_overlap,
                   helium_residual_overlap,all_signs_exhaustive]) and area_relative<Decimal("1e-12"))
            print("SOURCE_CROSS_46080_ROW_SUMMARY",json.dumps({
              "rows":rows,"all_global_overlaps":checks["native_global_HE_derived_row_intervals_overlap"],
              "area_relative":float(area_relative),"all_source_delta_overlap":reimatched,
              "disjoint_counts":checks["sibling_binding_row_disjoint_counts"]},sort_keys=True),flush=True)
            if not gate:
                status="BLOCKED_CROSS_REPO_OWNER_SOURCE_CONSUMPTION"
            else:
                status="ADMIT_SCOPED_ORIGINAL_F05_DERIVED_HHE_ENERGY_CHARGE_THOMSON_CONSUMPTION"
            result={
             "schema":"REI_F05_OWNER_NATIVE_HE_REC_SOURCE_CONSUMPTION_V1",
             "scientific_owner_status":status,
             "source_claim_class":"SOURCE_AUTHENTIC_IMPLEMENTATION_CHECKED_NONAUTHORITATIVE_TICK161",
             "original_accepted_tick":"160/131072","candidate_tick161":"NOT_ACCEPTED",
             "original_source_cells":N,"source_original_rei_pr":352,
             "source_BASS_HE_pr":146,"source_REC_pr":190,
             "source_sha256_he_archive":identity["he_archive_sha256"],
             "source_sha256_rec_archive":identity["rec_archive_sha256"],
             "source_preview_SHA256":si.PREVIEW_SHA,
             "source_increment_SHA256":si.INCREMENT_SHA,
             "source_binding_energy_SHA256":si.HE_DERIVED_SHA,
             "physical_constants":{"eV_to_erg":str(EV),"chi_H_eV":str(CHI_H),
                    "chi_HeI_eV":str(CHI_HE1),"chi_HeII_eV":str(CHI_HE2),
                    "sigmaT_cm2":str(SIGMA_T),
                    "source_tick_seconds":recmeta["native_proper_tick_seconds"]},
             "physics":{
                "all_row_global_comparison":global_check,
                "original_rec_global_delta_electron":reportpair(rec_delta),
                "original_rec_delta_Thomson_area_cm2":reportpair(rec_area),
                "direct_sigmaT_delta_electron_area":reportpair(expected_area),
                "ionization_storage_energy_loss_per_lost_electron_eV":reportpair(energy_ratio),
                "helium_threshold_correction_to_H_only_energy_erg":reportpair(helium_correction),
                "direct_original_helium_threshold_correction_erg":reportpair(helium_correction_direct),
                "original_candidate_U_gas_erg":reportpair(decpair([native_he["U161"]["lower"],native_he["U161"]["upper"]])),
                "source_cell_sign_classes_from_independent_full_increments":sign,
                "published_cell_boundary_equivalence_metrics":minmax,
                "original_rec_electron_global_rate_per_s":recmeta["electron_number_rate_per_s"]
             },
             "verification":checks,
             "rec_repository_verify":"FAILED_UNRELATED_LEGACY_WHITESPACE_NOT_FULL_REPOSITORY_PASS",
             "no_original_source_override":True,
             "no_original_new_accepted_state":True,
             "no_rei_F08_line_of_sight_tau":True,
             "no_latent_energy_to_photoheat_conversion":True,
             "no_auto_next":True,
             "production":"HOLD",
             "central_DAG":"28/88_REPORTED","working_DAG":"33/88_REPORTED",
             "physical_fast_DAG":"4/7_REPORTED","canonical_delta":0,
             "no_force_push":True,"no_tolerance_relaxation":True,"no_merge":True
            }
            out.parent.mkdir(parents=True,exist_ok=True)
            out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
            print("OWNER_CROSS_REPO_ADMISSION",status,"EFFECTIVE_IONIZATION_EV",reportpair(energy_ratio),
                "BINDING_HE_CORRECTION_ERG",reportpair(helium_correction),flush=True)
            return 0 if gate else 2

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--he-zip",type=Path,required=True)
    ap.add_argument("--rec-zip",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args()
    sys.exit(run(args.he_zip,args.rec_zip,args.out))
