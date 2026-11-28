#!/usr/bin/env python3
"""Original accepted REI F05 tick160 H/He proper opacity; PW19 is a conditional
external test spectrum, NOT the native causal photon owner.
Full source reproduction requires the separately source-locked REC191 ZIP.
No native chemistry/RT/Einstein time integration is performed.
"""
from __future__ import annotations
import argparse,csv,gzip,hashlib,io,json,math,struct,sys,tarfile,zipfile
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[1]
sys.path.insert(0,str(REPO/"research/rei_pw19_spectral_native_bridge_20261101"))
import spectral_physics as sp

REC_SHA="3f6772f54822274bf6228dac1ec629a9d0b0cde9d2a0adbaa08d59a1ac352d0e"
TAR_SHA="a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b"
STATE_SHA="74c7cbb784c3a6fe25e53307f678ef23ab87263f56b314fbaa3ef696433d05f6"
NPZ_SHA="7855f8b5c072da7860e5b0404a5548114ef46a8713840d99e4efa1b009905d2d"
FORCING_SHA="9b33a16956d30d96576e7e189ab11ad67321fd6d2872b8ad68058f7aac3b5268"
DONOR_CSV_SHA="080fb36c9bf4a161f58dcf23c11765bf6eeeaeb537c2fab3fd2b51304d09240b"
DONOR_RESULT_SHA="321aa77723b406631ec54d07cc07d570a0462314b203f1112b51bb0406e46738"
N=46080
MPC_CM=3.085677581491367e24
C_CM_S=2.99792458e10
EV_ERG=1.602176634e-12
Z=5.95
STATE_MEMBER="checkpoints/generations/g-00000003-tick-000160/LOCAL_NEUTRAL_HAZARD_PRIMARY.state"
INIT_MEMBER="research/rec_rei_f05_native_thomson_medium_20261101/source_inputs/ORIGINAL_REI_F05_initial_material_state_z6.npz"
FORCING_MEMBER="research/rec_rei_f05_native_thomson_medium_20261101/source_inputs/ORIGINAL_REI_F05_canonical_time_resolved_forcing_nodes.csv"
TAR_MEMBER="original_REI_immutable/F05_first_interval_original_source.tar.gz"
BANDS=("HI_only","HI_HeI","all_three")
SPECIES=("HI","HeI","HeII")
ATOM_INDEX=np.array([0,2,3],dtype=np.intp)

def digest(b):return hashlib.sha256(b).hexdigest()
def src_intake(reczip):
    raw=Path(reczip).read_bytes()
    if digest(raw)!=REC_SHA:raise ValueError("REC191 exact source ZIP identity mismatch")
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        if z.testzip() is not None:raise ValueError("original REC ZIP member CRC invalid")
        tbytes=z.read(TAR_MEMBER)
        if digest(tbytes)!=TAR_SHA:raise ValueError("original REI source TAR mismatch")
        init=z.read(INIT_MEMBER)
        forcing=z.read(FORCING_MEMBER)
        if digest(init)!=NPZ_SHA or digest(forcing)!=FORCING_SHA:
            raise ValueError("Original W-node/forcing source input mismatch")
        rows=list(csv.DictReader(io.StringIO(forcing.decode())))
        rows0=sorted((row for row in rows if row["interval_index"]=="0"),key=lambda a:int(a["node_index"]))
        if len(rows0)!=17 or [int(q["node_index"]) for q in rows0]!=list(range(17)):
            raise ValueError("first source forcing time nodes incomplete")
        if not all(q["z_mid"]=="5.95" for q in rows0):
            raise ValueError("original z clock has changed")
        if not all(float(a["time_s"])<float(b["time_s"]) for a,b in zip(rows0[:-1],rows0[1:])):
            raise ValueError("source proper time not increasing")
        with tarfile.open(fileobj=io.BytesIO(tbytes),mode="r:gz") as tar:
            source=tar.extractfile(STATE_MEMBER)
            if source is None:raise ValueError("original accepted checkpoint absent")
            payload=source.read()
        if digest(payload)!=STATE_SHA:raise ValueError("original accepted tick160 state drift")
    if payload[:8]!=b"REIADP1\x00":raise ValueError("original binary state format wrong")
    header_size=struct.unpack_from("<Q",payload,8)[0]
    header=json.loads(payload[16:16+header_size].decode())
    if (header.get("population_shape")!=[N,5] or
        header.get("log_temperature_shape")!=[N] or
        header.get("metadata",{}).get("endpoint_tick")!=160 or
        header.get("dtype")!="float64" or header.get("byte_order")!="little"):
        raise ValueError("source accepted checkpoint shape/authority mismatch")
    buff=np.frombuffer(payload,dtype="<f8",offset=16+header_size)
    if buff.size!=2*N*5+2*N:raise ValueError("unexpected state payload bytes")
    plo=buff[:N*5].reshape(N,5).copy()
    phi=buff[N*5:2*N*5].reshape(N,5).copy()
    if not (np.isfinite(plo).all() and np.isfinite(phi).all()
            and (plo>=0).all() and (plo<=phi).all()):
        raise ValueError("original accepted populations invalid")
    with np.load(io.BytesIO(init),allow_pickle=False) as data:
        W=data["W_node"].astype(np.float64)
        NH=(data["N_HI"]+data["N_HII"]).astype(np.float64)
        NHE=(data["N_HeI"]+data["N_HeII"]+data["N_HeIII"]).astype(np.float64)
    if not (len(W)==N and (W>0).all() and np.isfinite(W).all()
            and abs(float(np.sum(W))-1)<2e-14):
        raise ValueError("original native volume weights invalid")
    if not (np.all(plo[:,0]+plo[:,1]<=NH) and np.all(NH<=phi[:,0]+phi[:,1])
            and np.all(np.sum(plo[:,2:5],axis=1)<=NHE)
            and np.all(NHE<=np.sum(phi[:,2:5],axis=1))):
        raise ValueError("original H/He nuclear identities fail enclosing")
    V=W*(MPC_CM**3)/(1+Z)**3
    if not (np.isfinite(V).all() and (V>0).all()):raise ValueError("bad proper volume")
    return V,plo[:,ATOM_INDEX],phi[:,ATOM_INDEX]

def spectral_moments():
    donor=REPO/"research/rei_pw19_spectral_native_bridge_20261101"
    if digest((donor/"PW19_T160_SPECTRAL_THREE_BAND_SOURCE_DONOR_18ROWS.csv").read_bytes())!=DONOR_CSV_SHA:
        raise ValueError("PW19 18-row spectral donor changed")
    if digest((donor/"NATIVE_T160_PW19_SPECTRAL_DONOR_PHYSICS.json").read_bytes())!=DONOR_RESULT_SHA:
        raise ValueError("PW19 frozen donor primary science receipt changed")
    record=json.loads((donor/"PW19_VER96_SOURCE_CONDITIONAL_PHYSICS.json").read_text())
    if record["original_zip_sha256"]!=sp.ZIP_SHA:raise ValueError("PW19 original source mismatch")
    source=sp.read_source()
    energy,ints,logs,spec=sp.make_spectrum(source,"z5p95_log")
    kernels=[]
    for label,low,high in sp.BANDS:
        x=[low]+[e for e in energy if low<e<high]+[high]
        phi=0.; m1=np.zeros(3);m2=np.zeros((3,3)); samples=[]
        for e0,e1 in zip(x[:-1],x[1:]):
            a=math.log(e0);step=(math.log(e1)-a)/16
            for j in range(17):
                t=a+j*step
                e=math.exp(t)
                f=spec(t)/(e*EV_ERG)
                w=(1 if j in (0,16) else (4 if j%2 else 2))*step/3
                ph=w*f
                sv=np.array([sp.cross(e,s) if (s=="HI" or (s=="HeI" and label!="HI_only") or (s=="HeII" and label=="all_three")) else 0.
                      for s in SPECIES])
                phi+=ph;m1+=ph*sv;m2+=ph*np.outer(sv,sv)
                samples.append((ph,sv))
        if phi<=0:raise ValueError("no original spectral photons")
        mu=m1/phi
        K=m2/phi
        cov=K-np.outer(mu,mu)
        if np.min(np.linalg.eigvalsh(cov)) < -1e-14*np.max(np.abs(K)):
            raise ValueError("invalid spectral covariance")
        rr=record["science"]["z5p95_log"]["bands_16_substeps"]
        corresponding=next(q for q in rr if q["band"]==label)
        if abs(phi-corresponding["exposure_photon_cm2_s"])/phi>3e-13:
            raise ValueError("original spectral photon flux inconsistent")
        for j,s in enumerate(SPECIES):
            observed=corresponding[f"gamma_{s}_per_s"]
            if not math.isclose(phi*mu[j],observed,rel_tol=4e-13,abs_tol=1e-40):
                raise ValueError("original photo rate vs opacity integral disagree")
        kernels.append({"name":label,"phi":phi,"mu":mu,"K":K,"cov":cov,"samples":samples,
                        "qheat":np.array([corresponding[f"heat_{s}_erg_per_atom_s"] for s in SPECIES])})
    return kernels,record

def fmt(x):return format(float(x),".17g")
def write_gzip(rows,fields,path):
    buf=io.StringIO(newline="")
    w=csv.DictWriter(buf,fieldnames=fields,lineterminator="\n")
    w.writeheader();w.writerows(rows)
    data=io.BytesIO()
    with gzip.GzipFile(fileobj=data,mode="wb",filename="",mtime=0,compresslevel=6) as f:
        f.write(buf.getvalue().encode())
    path.write_bytes(data.getvalue())
    return len(rows),digest(data.getvalue())

def compute(reczip,outdir):
    out=Path(outdir);out.mkdir(parents=True,exist_ok=True)
    V,p_lo,p_hi=src_intake(reczip)
    kernels,source=spectral_moments()
    nlo=p_lo/V[:,None];nhi=p_hi/V[:,None];nmid=(nlo+nhi)/2
    fields=["node","volume_cm3"]+[f"n_{s}_{bound}_cm3" for s in SPECIES for bound in ("lo","hi")]
    fields += [f"{name}_{key}" for name in BANDS for key in ("kappa_lo_inv_cm","kappa_hi_inv_cm",
                      "mfp_lo_cm","mfp_hi_cm","CV2_mid")]
    fields += ["HeII_hard_opacity_fraction_mid"]
    cols=[np.arange(N),V]
    for j,s in enumerate(SPECIES):cols.extend([nlo[:,j],nhi[:,j]])
    totals={}
    photon_consistent=[]
    for k in kernels:
        mu=k["mu"];meanLo=nlo@mu;meanHi=nhi@mu;meanMid=nmid@mu
        if not (np.isfinite(meanLo).all() and (meanLo>0).all() and
                np.all(meanLo<=meanMid) and np.all(meanMid<=meanHi)):
            raise ValueError("original source local opacity not positive")
        cov=k["cov"];var=np.einsum("ni,ij,nj->n",nmid,cov,nmid,optimize=True)
        if (var<-(3e-13)*meanMid**2).any():raise ValueError("negative spectral variance")
        cv=np.maximum(var,0)/meanMid**2
        # Local material opacity is exact at L=0 under the imposed PW19 spectrum.
        gamma=k["phi"]*mu
        Rlo=float(np.sum(p_lo@gamma));Rhi=float(np.sum(p_hi@gamma))
        Hlo=float(np.sum(p_lo@k["qheat"]));Hhi=float(np.sum(p_hi@k["qheat"]))
        if not (0<=Rlo<=Rhi and Hlo>=0 and Hlo<=Hhi):
            raise ValueError("real source photon-gas interaction totals invalid")
        if not np.allclose(C_CM_S*(k["phi"]/C_CM_S)*meanMid,nmid@gamma,rtol=2e-14,atol=0):
            raise ValueError("per-volume microscopic photon rate inconsistent")
        totals[k["name"]]={"phi_photons_cm2_s":k["phi"],"sigma_mean_cm2":mu.tolist(),
            "sigma_cov_cm4":cov.tolist(),"global_photoevents_per_s_endpoint_interval":[Rlo,Rhi],
            "global_photoexcessheat_erg_s_endpoint_interval":[Hlo,Hhi],
            "kappa_cm_inv_extrema":[float(meanLo.min()),float(meanHi.max())],
            "lambda_cm_extrema":[float((1/meanHi).min()),float((1/meanLo).max())],
            "CV2_photon_cross_section_cell_median":float(np.median(cv)),
            "CV2_photon_cross_section_cell_max":float(cv.max()),
            "volume_weighted_kappa_cm_inv":float(np.sum(V*meanMid)/np.sum(V)),
            "spatial_opacity_clumping":float(np.sum(V*meanMid**2)*np.sum(V)/(np.sum(V*meanMid)**2))}
        cols.extend([meanLo,meanHi,1/meanHi,1/meanLo,cv])
        photon_consistent.append(k["name"])
    hard=kernels[2]
    hardDen=nmid@hard["mu"]
    hardShare=nmid[:,2]*hard["mu"][2]/hardDen
    cols.append(hardShare)
    for s in SPECIES:
        j=SPECIES.index(s)
        lo=float(np.sum(p_lo[:,j]));hi=float(np.sum(p_hi[:,j]))
        t=source["science"]["z5p95_log"]["rates_16_substeps"][s]
        # PR147 inherited global neutral count was a point source within original accepted intervals.
        import json as json_alias
        point=json_alias.loads((REPO/"research/rei_igm_p19_native_receiver_20261101/results/SCIENCE_RESULTS.json").read_text())["native_global_neutral_counts"][s]
        if not (lo<=point<=hi):raise ValueError("previous source neutral point outside exact tick160 interval")
    donor=json.loads((REPO/"research/rei_pw19_spectral_native_bridge_20261101/NATIVE_T160_PW19_SPECTRAL_DONOR_PHYSICS.json").read_text())
    totLo=sum(v["global_photoevents_per_s_endpoint_interval"][0] for v in totals.values())
    totHi=sum(v["global_photoevents_per_s_endpoint_interval"][1] for v in totals.values())
    prev=donor["source_scenarios"]["z5p95_log"]["global"]["photoionizations_per_s"]
    if not totLo<=prev<=totHi:raise ValueError("previous native source point outside source-state population interval")
    records=[dict(zip(fields,[fmt(col[i]) if col.dtype.kind=="f" else int(col[i]) for col in cols])) for i in range(N)]
    output=out/"ORIGINAL_REI_T160_PW19_LOCAL_PHOTO_OPACITY_46080.csv.gz"
    nrows,h=write_gzip(records,fields,output)
    diagnostics=[]
    for k in kernels:
        meanMid=nmid@k["mu"]
        for q in (0.,.5,1.):
            target=float(np.quantile(meanMid,q))
            index=int(np.argmin(abs(meanMid-target)))
            L=1/float(meanMid[index])
            real=math.fsum(weight*math.exp(-L*float(nmid[index]@sigma)) for weight,sigma in k["samples"])/k["phi"]
            grey=math.exp(-1)
            if real<grey-3e-12 or real>1+3e-12:raise ValueError("exact Jensen physical redirection failed")
            diagnostics.append({"band":k["name"],"native_node":index,"quantile":q,
                 "diagnostic_length_cm":L,"frequency_resolved_transmission":real,
                 "grey_transmission":grey,"spectral_hardening_gap":real-grey})
    result={"schema":"BASS_HE_NATIVE_REI_F05_T160_PW19_LOCAL_ABSORBING_MEDIUM_V1",
            "claim":"SOURCE_CONDITIONAL_LOCAL_MATERIAL_PHOTO_OPACITY_NO_CAUSAL_PHOTON_OWNER",
            "source_original_REC191_full_zip_sha256":REC_SHA,
            "source_original_REI_tar_sha256":TAR_SHA,"source_tick160_native_state_sha256":STATE_SHA,
            "source_original_initial_state_npz_sha256":NPZ_SHA,
            "source_original_forcing_sha256":FORCING_SHA,
            "source_PW19_zip_sha256":sp.ZIP_SHA,
            "source_PW19_donor_CSV_sha256":DONOR_CSV_SHA,
            "original_accepted_tick":160,"node_count":N,"source_z_mid":Z,
            "native_total_proper_volume_cm3":float(V.sum()),
            "native_state_inherited_interval_arithmetic":"source_NPZ_and_REIADP1_float64_not_MPFR",
            "kappa_claim":"proper H/He local material coefficient at incident unattenuated PW19 spectrum",
            "photon_transport":"NOT_ADMITTED_NOT_COMPUTED",
            "jensen":"T_full(L)>=exp(-L*kappa_mean) for frozen homogeneous material; equality at L=0 or spectrally constant kappa",
            "native_PW19_rate_inherited_total_interval":[totLo,totHi],
            "native_PW19_donor_point_total":prev,
            "helium_HeII_hard_band_volume_weighted_share":float(np.sum(V*nmid[:,2]*hard["mu"][2])/np.sum(V*hardDen)),
            "helium_HeII_hard_band_cell_share_quantiles":np.quantile(hardShare,[0.,.5,1.]).tolist(),
            "bands":totals,"Jensen_one_local_mfp_diagnostics":diagnostics,
            "data_csv_rows":nrows,"data_csv_sha256":h,
            "central_DAG":"28/88_REPORTED","working_DAG":"33/88_REPORTED",
            "physical_fast_DAG":"4/7_REPORTED","BASS_HE_physical_DAG":"14/18_REPORTED",
            "canonical_delta":0,"production":"HOLD","official_tick161":False,
            "original_owner_mutation":False}
    path=out/"SCIENCE_RESULT.json"
    path.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("SCIENCE_RESULT",json.dumps({name:result[name] for name in
          ["native_total_proper_volume_cm3","native_PW19_rate_inherited_total_interval",
           "helium_HeII_hard_band_volume_weighted_share",
           "helium_HeII_hard_band_cell_share_quantiles","data_csv_sha256"]},sort_keys=True))
    print("DIAGNOSTICS",json.dumps(diagnostics,sort_keys=True))
    print("SHA256_RESULT",digest(path.read_bytes()),"DAG","28/88","14/18","DELTA",0)
    return result

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--rec-zip",required=True,type=Path,help="REC191 exact source-inclusive original bundle")
    p.add_argument("--out",type=Path,default=HERE/"results")
    a=p.parse_args()
    compute(a.rec_zip,a.out)
