#!/usr/bin/env python3
"""Read actual frozen Aug-29 REI FLRW IGM accepted-state bytes, never mutate owners."""
import argparse, csv, gzip, hashlib, json, struct, tarfile
from pathlib import Path
import numpy as np

EXPECTED_SHA = "a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b"
MAGIC=b"REIADP1\x00"
N=46080
KB=1.380649e-16

def inspect_state(data,name,output_dir=None):
    if not data.startswith(MAGIC):
        return None
    count=struct.unpack_from("<Q",data,len(MAGIC))[0]
    if not 0 < count < 65536:raise ValueError("invalid state header length")
    offset=len(MAGIC)+8
    h=json.loads(data[offset:offset+count].decode("ascii"))
    if h.get("population_shape") != [N,5] or h.get("log_temperature_shape") != [N]:
        raise ValueError("original 46080-node state identity mismatch")
    if h.get("array_order") != ["population_lower","population_upper","log_temperature_lower","log_temperature_upper"]:
        raise ValueError("original state order mismatch")
    raw=data[offset+count:]
    if len(raw) != (2*N*5+2*N)*8:raise ValueError("original state length mismatch")
    a=np.frombuffer(raw,dtype="<f8");k=N*5
    low=a[:k].reshape(N,5);high=a[k:2*k].reshape(N,5)
    tlo=a[2*k:2*k+N];thi=a[2*k+N:2*k+2*N]
    if not np.isfinite(a).all() or (low<=0).any() or (high<low).any() or (thi<tlo).any():
        raise ValueError("nonphysical state enclosure")
    hl=low[:,0]+low[:,1];hh=high[:,0]+high[:,1]
    hel=low[:,2:5].sum(axis=1);heh=high[:,2:5].sum(axis=1)
    el=low[:,1]+low[:,3]+2*low[:,4];eh=high[:,1]+high[:,3]+2*high[:,4]
    def extrema(xlo,xhi):
        return {"min":float(np.min(xlo)), "max":float(np.max(xhi)),
                "median_lower":float(np.median(xlo)), "median_upper":float(np.median(xhi))}
    tl=np.exp(tlo);th=np.exp(thi)
    u_lo=1.5*KB*tl*(low.sum(axis=1)+el)/hh
    u_hi=1.5*KB*th*(high.sum(axis=1)+eh)/hl
    xe_lo=el/hh;xe_hi=eh/hl
    xhii_lo=low[:,1]/hh;xhii_hi=high[:,1]/hl
    xheii_lo=low[:,3]/heh;xheii_hi=high[:,3]/hel
    xheiii_lo=low[:,4]/heh;xheiii_hi=high[:,4]/hel
    percentile_bands={}
    for key,l,upperarr in (("x_HII",xhii_lo,xhii_hi),("x_HeII",xheii_lo,xheii_hi),
                    ("x_HeIII",xheiii_lo,xheiii_hi),("T_K",tl,th),
                    ("xe_per_H",xe_lo,xe_hi),("U_thermal_erg_per_H",u_lo,u_hi)):
        percentile_bands[key]={str(q):[float(np.percentile(l,q)),float(np.percentile(upperarr,q))]
                               for q in (1,5,25,50,75,95,99)}
    lane=h.get("metadata",{}).get("lane","UNKNOWN")
    body_sha256=hashlib.sha256(raw).hexdigest()
    if output_dir is not None:
        csvfile=output_dir/("NODEWISE_"+lane+"_46080_PHYSICAL.csv.gz")
        names=("lane","node","x_HII_lo","x_HII_hi","x_HeII_lo","x_HeII_hi",
          "x_HeIII_lo","x_HeIII_hi","T_K_lo","T_K_hi",
          "xe_per_H_lo","xe_per_H_hi","U_thermal_erg_per_H_lo","U_thermal_erg_per_H_hi")
        with gzip.open(csvfile,"wt",encoding="utf-8",newline="") as gz:
            writer=csv.writer(gz);writer.writerow(names)
            for i in range(N):
                writer.writerow([lane,i,*[format(float(v[i]),".17g") for v in
                    (xhii_lo,xhii_hi,xheii_lo,xheii_hi,xheiii_lo,xheiii_hi,
                     tl,th,xe_lo,xe_hi,u_lo,u_hi)]])
    return {"member":name,"sha256":hashlib.sha256(data).hexdigest(),
        "state_array_sha256":body_sha256,"percentiles":percentile_bands,
        "metadata":h.get("metadata",{}),"nodes":N,
        "x_HII":extrema(low[:,1]/hh,high[:,1]/hl),
        "x_HeII":extrema(low[:,3]/heh,high[:,3]/hel),
        "x_HeIII":extrema(low[:,4]/heh,high[:,4]/hel),
        "T_K":extrema(tl,th),
        "U_thermal_erg_per_H":extrema(u_lo,u_hi)}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--archive",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    x=ap.parse_args()
    digest=hashlib.sha256(x.archive.read_bytes()).hexdigest()
    if digest != EXPECTED_SHA:raise ValueError("IMMUTABLE_ARCHIVE_SHA_MISMATCH:"+digest)
    rows=[];names=[]
    x.output.parent.mkdir(parents=True,exist_ok=True)
    with tarfile.open(x.archive,"r:gz") as z:
        for member in z:
            if not member.isfile():continue
            p=Path(member.name)
            if p.is_absolute() or ".." in p.parts:raise ValueError("unsafe source member")
            names.append({"name":member.name,"size":member.size})
            if 9 < member.size < 8000000:
                data=z.extractfile(member).read()
                row=inspect_state(data,member.name,x.output.parent)
                if row is not None:rows.append(row)
    output={"schema":"REI_FROZEN_REAL_STATE_READBACK_V1","archive_sha256":digest,
      "original_accepted_tick":160,"original_total_ticks":131072,"original_accepted_endpoints":3,
      "members":names,"physical_states":rows,
      "status":"SOURCE_AUTHENTIC_PHYSICAL_STATE_EXTRACTED" if rows else "BLOCKED_SOURCE_STATE_UNAVAILABLE",
      "canonical_delta":0,"central_DAG":"28/88","working_DAG":"33/88","physical_fast":"4/7"}
    x.output.parent.mkdir(parents=True,exist_ok=True)
    x.output.write_text(json.dumps(output,indent=2,sort_keys=True)+"\n")
    print("ARCHIVE_MEMBERS",len(names),"AUTHENTIC_STATE_ROWS",len(rows),"STATUS",output["status"])
    print("ACTUAL_PHYSICAL_H_HE_T",json.dumps(rows[:12],sort_keys=True))
    if not rows:raise SystemExit(3)
if __name__=="__main__":main()
