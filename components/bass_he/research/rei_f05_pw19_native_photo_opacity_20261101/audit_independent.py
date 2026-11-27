#!/usr/bin/env python3
"""Independent-formula same-author audit: no import of native_photo_opacity.py.
Original source interval pop + W, previously published PW19 18-row sigma,
separate uniform-logE quadrature for Jensen physical diagnostics.
"""
import argparse,bisect,csv,gzip,hashlib,io,json,math,struct,tarfile,zipfile
from pathlib import Path
import numpy as np
SRCZIP_SHA="3f6772f54822274bf6228dac1ec629a9d0b0cde9d2a0adbaa08d59a1ac352d0e"
STATE_SHA="74c7cbb784c3a6fe25e53307f678ef23ab87263f56b314fbaa3ef696433d05f6"
NPZ_SHA="7855f8b5c072da7860e5b0404a5548114ef46a8713840d99e4efa1b009905d2d"
SED_SHA="afd470b9fd934234e7f6e815d6887814a2ff8767e61f0d2a8e6187efde8d0d55"
DONOR_CSV_SHA="080fb36c9bf4a161f58dcf23c11765bf6eeeaeb537c2fab3fd2b51304d09240b"
MPC_CM=3.085677581491367e24
EV=1.602176634e-12
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
SPECIES=("HI","HeI","HeII")
BANDS=(("HI_only",13.60,24.59),("HI_HeI",24.59,54.42),("all_three",54.42,50000.))
VERNER={
"HI":(13.60,.4298,54750.,32.88,2.963,0.,0.,0.),
"HeI":(24.59,13.61,949.2,1.469,3.188,2.039,.4434,2.136),
"HeII":(54.42,1.720,13690.,32.88,2.963,0.,0.,0.)}
def sha(b):return hashlib.sha256(b).hexdigest()
def original_native(p):
    b=Path(p).read_bytes()
    if sha(b)!=SRCZIP_SHA:raise ValueError("REC input SHA")
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        original=z.read("original_REI_immutable/F05_first_interval_original_source.tar.gz")
        binit=z.read("research/rec_rei_f05_native_thomson_medium_20261101/source_inputs/ORIGINAL_REI_F05_initial_material_state_z6.npz")
        if sha(binit)!=NPZ_SHA:raise ValueError("NPZ raw source")
        with tarfile.open(fileobj=io.BytesIO(original),mode="r:gz") as t:
            binary=t.extractfile("checkpoints/generations/g-00000003-tick-000160/LOCAL_NEUTRAL_HAZARD_PRIMARY.state").read()
    if sha(binary)!=STATE_SHA:raise ValueError("tick160 raw checkpoint")
    nheader=struct.unpack_from("<Q",binary,8)[0]
    obj=json.loads(binary[16:16+nheader])
    if obj["metadata"]["endpoint_tick"]!=160 or obj["population_shape"]!=[46080,5]:
        raise ValueError("raw checkpoint dimension")
    data=np.frombuffer(binary,dtype="<f8",offset=16+nheader)
    l=data[:230400].reshape((46080,5))[:,[0,2,3]]
    h=data[230400:460800].reshape((46080,5))[:,[0,2,3]]
    with np.load(io.BytesIO(binit)) as z:
        volume=np.asarray(z["W_node"])*(MPC_CM**3)/(6.95**3)
    return l/volume[:,None],h/volume[:,None],volume

def weights():
    p=ROOT/"research/rei_pw19_spectral_native_bridge_20261101/PW19_T160_SPECTRAL_THREE_BAND_SOURCE_DONOR_18ROWS.csv"
    if sha(p.read_bytes())!=DONOR_CSV_SHA:raise ValueError("original donor has changed")
    with p.open() as f:
        rr=list(csv.DictReader(f))
    subset=[r for r in rr if r["spectrum"]=="z5p95_log"]
    if len(subset)!=9:raise ValueError("band species missing")
    sigma=np.array([[float(next(r["effective_sigma_cm2"] for r in subset if r["band"]==band and r["species"]==s))
                     for s in SPECIES] for band,*_ in BANDS])
    return sigma

def dense_spectrum():
    path=ROOT/"research/rei_pw19_spectral_native_bridge_20261101/source_original_v1.zip"
    b=path.read_bytes()
    if sha(b)!=SED_SHA:raise ValueError("spectral donor original raw SHA")
    out={}
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        for label in ("05.807000","06.141000"):
            n=[name for name in z.namelist() if name.endswith("/PW19/z_"+label+".csv")]
            if len(n)!=1:raise ValueError("spectral member")
            with io.StringIO(z.read(n[0]).decode()) as f:
                rr=list(csv.DictReader(f))
            out[label]=([float(q["E (eV)"]) for q in rr],
                        [float(q["I (erg/s/cm**2)"]) for q in rr])
    E,I0=out["05.807000"]; E1,I1=out["06.141000"]
    if E!=E1 or len(E)!=626:raise ValueError("original energy grid mismatch")
    a=(5.95-5.807)/(6.141-5.807)
    I=[x**(1-a)*y**a if x>0 and y>0 else 0.0 for x,y in zip(I0,I1)]
    return np.log(np.array(E)),np.array(I)

def xs(E,key):
    eth,e0,s0,ya,p,yw,y0,y1=VERNER[key]
    x=E/e0-y0
    y=np.hypot(x,y1)
    val=1e-18*s0*((x-1)**2+yw*yw)*np.exp((p/2-5.5)*np.log(y)-p*np.log1p(np.sqrt(y/ya)))
    return np.where((E>=eth)&(E<=50000),val,0.)

def dense_transmission(spectrum,nvec,low,high,L,n=40000):
    logE,intens=spectrum
    t=np.linspace(math.log(low),math.log(high),n+1)
    E=np.exp(t)
    ix=np.clip(np.searchsorted(logE,t,side="right")-1,0,len(logE)-2)
    f=(t-logE[ix])/(logE[ix+1]-logE[ix])
    f=np.clip(f,0,1)
    A=intens[ix];B=intens[ix+1]
    Il=np.exp((1-f)*np.log(np.maximum(A,1e-300))+f*np.log(np.maximum(B,1e-300)))
    Il=np.where((A>0)&(B>0),Il,(1-f)*A+f*B)
    ph=Il/(E*EV)
    kappa=np.zeros_like(E)
    for j,s in enumerate(SPECIES):
        kappa+=nvec[j]*xs(E,s)
    w=np.ones(n+1);w[1:-1:2]=4;w[2:-1:2]=2
    p=w*ph
    full=float(np.sum(p*np.exp(-L*kappa))/np.sum(p))
    return full

def run(src):
    lo,hi,V=original_native(src)
    sigma=weights()
    ref=json.loads((HERE/"results/SCIENCE_RESULT.json").read_text())
    with gzip.open(HERE/"results/ORIGINAL_REI_T160_PW19_LOCAL_PHOTO_OPACITY_46080.csv.gz","rt") as f:
        rr=list(csv.DictReader(f))
    if len(rr)!=46080:raise ValueError("published 46k rows")
    maxk=0.
    for g,(name,_,_) in enumerate(BANDS):
        ol=lo@sigma[g]
        ou=hi@sigma[g]
        nativeL=np.array([float(r[name+"_kappa_lo_inv_cm"]) for r in rr])
        nativeU=np.array([float(r[name+"_kappa_hi_inv_cm"]) for r in rr])
        diff=max(float(np.max(abs(nativeL-ol)/ol)),float(np.max(abs(nativeU-ou)/ou)))
        maxk=max(maxk,diff)
        if diff>8e-13:raise AssertionError((name,"all-row opacity disagreement",diff))
    source=dense_spectrum()
    physical={}
    for item in ref["Jensen_one_local_mfp_diagnostics"]:
        band=item["band"]
        loe,hie=next((a,b) for name,a,b in BANDS if name==band)
        j=item["native_node"]
        nvec=(lo[j]+hi[j])/2
        lens=item["diagnostic_length_cm"]
        k= sigma[next(k for k,(name,_,_) in enumerate(BANDS) if name==band)]@nvec
        if abs(lens*k-1)>4e-13:raise ValueError("diagnostic mean free path mismatch")
        t=dense_transmission(source,nvec,loe,hie,lens)
        err=abs(t-item["frequency_resolved_transmission"])
        if t+3e-7<math.exp(-1) or err>4e-4:
            raise AssertionError(("spectral hardening mismatch",band,j,t,err))
        physical[f"{band}_{j}"]={"frequency_resolved_T":t,"reported_T":item["frequency_resolved_transmission"],"abs_difference":err}
    out={"schema":"BASS_HE_REI_T160_PW19_OPACITY_INDEPENDENT_ORIGINAL_SOURCE_AUDIT",
         "source_REC191_sha256":SRCZIP_SHA,"source_PW19_sha256":SED_SHA,"native_node_count":len(rr),
         "all_row_max_relative_kappa_disagreement":maxk,
         "independent_dense_40000_per_band_spectral_diagnostics":physical,
         "same_author_independence":"SEPARATE_IMPLEMENTATION_NOT_DIFFERENT_AUTHOR",
         "status":"PASS_SOURCE_CONDITIONAL","central_DAG":"28/88_REPORTED","BASS_HE_DAG":"14/18_REPORTED",
         "canonical_delta":0}
    path=HERE/"results/INDEPENDENT_AUDIT.json"
    path.write_text(json.dumps(out,sort_keys=True,indent=2)+"\n")
    print("AUDIT",json.dumps(out,sort_keys=True))
    print("SHA",sha(path.read_bytes()))
    return out

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--rec-zip",type=Path,required=True)
    run(p.parse_args().rec_zip)
