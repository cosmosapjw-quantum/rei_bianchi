#!/usr/bin/env python3
"""Source-conditional PW19 spectral H/He photoionization/heating intake.
Taira et al. Zenodo v1.0.0 binned I(E)=4*pi*nu*J_nu [erg/s/cm^2].
No equivalence to REI original local photon groups or source admission is implied.
"""
import bisect, csv, hashlib, io, json, math, zipfile
from pathlib import Path

HERE=Path(__file__).resolve().parent
ZIP=HERE/"source_original_v1.zip"
ZIP_SHA="afd470b9fd934234e7f6e815d6887814a2ff8767e61f0d2a8e6187efde8d0d55"
EV_ERG=1.602176634e-12
Z0,Z1,ZTARGET=5.807,6.141,5.95
# Verner et al. (1996) Table 1 first 3 rows, sigma0 in megabarns.
# Key = (Z,number electrons); [Eth,Emax,E0,sigma0,ya,P,yw,y0,y1].
VERNER={
 "HI":(13.60,5.0e4,.4298,5.475e4,32.88,2.963,0.,0.,0.),
 "HeI":(24.59,5.0e4,13.61,949.2,1.469,3.188,2.039,.4434,2.136),
 "HeII":(54.42,5.0e4,1.720,1.369e4,32.88,2.963,0.,0.,0.),
}
CHI={"HI":13.598434599702,"HeI":24.587389011,"HeII":54.41776}
BANDS=[("HI_only",13.60,24.59),("HI_HeI",24.59,54.42),("all_three",54.42,5.0e4)]
ORIGINAL_D1_AT_Z5P95={"HI":6.491041172084541e-14,"HeI":4.658184761206645e-14,"HeII":8.951802738113886e-18}

def sha(b):return hashlib.sha256(b).hexdigest()
def cross(e,s):
    eth,emax,e0,s0,ya,p,yw,y0,y1=VERNER[s]
    # log/exp of an exact integration boundary can be a few ULP below Eth.
    if e<eth*(1-4e-15) or e>emax*(1+4e-15):return 0.0
    e=min(max(e,eth),emax)
    x=e/e0-y0
    y=math.hypot(x,y1)
    f=((x-1.0)**2+yw*yw)*y**(p/2.0-5.5)/(1+math.sqrt(y/ya))**p
    return s0*f*1.e-18

def read_source():
    raw=ZIP.read_bytes()
    if sha(raw)!=ZIP_SHA:raise ValueError("Zenodo v1 source ZIP SHA mismatch")
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        if z.testzip() is not None:raise ValueError("source ZIP CRC failure")
        names=z.namelist()
        data={}
        for zl in [Z0,Z1]:
            target=f"/data_tables/PW19/z_{zl:09.6f}.csv"
            candidates=[n for n in names if n.endswith(target)]
            if len(candidates)!=1:raise ValueError("PW19 source member mismatch "+target)
            content=z.read(candidates[0])
            rows=list(csv.DictReader(io.StringIO(content.decode("utf8"))))
            en=[float(r["E (eV)"]) for r in rows]
            fl=[float(r["I (erg/s/cm**2)"]) for r in rows]
            if len(rows)!=626 or not (all(math.isfinite(a) and a>0 for a in en) and all(math.isfinite(a) and a>=0 for a in fl)):
                raise ValueError("PW19 source shape/value mismatch")
            if not all(en[i]<en[i+1] for i in range(len(en)-1)):
                raise ValueError("PW19 energy grid nonmonotonic")
            data[zl]={"E":en,"I":fl,"sha256":sha(content),"member":candidates[0]}
        if data[Z0]["E"]!=data[Z1]["E"]:raise ValueError("PW19 grids differ")
    return data

def make_spectrum(data,model):
    y0,y1=data[Z0]["I"],data[Z1]["I"]
    a=(ZTARGET-Z0)/(Z1-Z0)
    if model=="z5p807": intens=y0
    elif model=="z6p141": intens=y1
    elif model=="z5p95_log":intens=[math.exp((1-a)*math.log(x)+a*math.log(y)) if x>0 and y>0 else (1-a)*x+a*y for x,y in zip(y0,y1)]
    elif model=="z5p95_linear":intens=[(1-a)*x+a*y for x,y in zip(y0,y1)]
    else:raise ValueError("unapproved interpolation")
    energy=data[Z0]["E"]
    logs=[math.log(e) for e in energy]
    lnI=[math.log(i) if i>0 else None for i in intens]
    def source(t):
        k=bisect.bisect_right(logs,t)-1
        k=min(max(k,0),len(logs)-2)
        a=(t-logs[k])/(logs[k+1]-logs[k])
        return (math.exp((1-a)*lnI[k]+a*lnI[k+1]) if lnI[k] is not None and lnI[k+1] is not None else (1-a)*intens[k]+a*intens[k+1])
    return energy,intens,logs,source

def quadrature(data,model,substeps=8):
    energy,intens,logs,source=make_spectrum(data,model)
    if substeps<=0 or substeps%2:raise ValueError("even substeps needed")
    rows=[]
    for label,lo,hi in BANDS:
        grid=[lo]+[e for e in energy if lo<e<hi]+[hi]
        total=[0.,0.,0.]
        by={s:[0.,0.] for s in VERNER}
        # Integrate in d lnE, with I(E)=4*pi*nu*Jnu.
        for e0,e1 in zip(grid[:-1],grid[1:]):
            x0=math.log(e0); dx=(math.log(e1)-x0)/substeps
            for j in range(substeps+1):
                x=x0+j*dx
                e=math.exp(x); rad=source(x)
                weight=(1 if j in (0,substeps) else (4 if j%2 else 2))*dx/3
                # Photon number exposure per area, energy above threshold.
                total[0]+=weight*rad/(e*EV_ERG)
                total[1]+=weight*rad
                for s in VERNER:
                    # Spectral bands are half-open in species support: count each edge once.
                    active=(s=="HI" or (s=="HeI" and label!="HI_only") or (s=="HeII" and label=="all_three"))
                    sigma=cross(e,s) if active else 0.0
                    gamma=rad*sigma/(e*EV_ERG)
                    by[s][0]+=weight*gamma
                    by[s][1]+=weight*gamma*(e-CHI[s])*EV_ERG
        result={"band":label,"energy_low_eV":lo,"energy_high_eV":hi,
                "exposure_photon_cm2_s":total[0],
                "exposure_erg_cm2_s":total[1]}
        for s in VERNER:
            result[f"gamma_{s}_per_s"]=by[s][0]
            result[f"heat_{s}_erg_per_atom_s"]=by[s][1]
        rows.append(result)
    rates={}
    for s in VERNER:
        rate=math.fsum(x[f"gamma_{s}_per_s"] for x in rows)
        heat=math.fsum(x[f"heat_{s}_erg_per_atom_s"] for x in rows)
        # Interpolated upper-fit-model predicts conditional per-neutral response.
        rates[s]={"photo_rate_per_s":rate,"excess_heat_eV_per_s":heat/EV_ERG,
                  "mean_excess_eV":heat/(rate*EV_ERG) if rate else 0.,
                  "comparison_P19_D1_effective_rate":ORIGINAL_D1_AT_Z5P95[s],
                  "spectrum_rate_over_D1_effective":rate/ORIGINAL_D1_AT_Z5P95[s]}
    return rows,rates

def independent_energy_closure(bands,rates):
    for s in VERNER:
        g=math.fsum(b[f"gamma_{s}_per_s"] for b in bands)
        h=math.fsum(b[f"heat_{s}_erg_per_atom_s"] for b in bands)
        absorption=math.fsum(
            b[f"heat_{s}_erg_per_atom_s"]+CHI[s]*EV_ERG*b[f"gamma_{s}_per_s"]
            for b in bands)
        assert math.isclose(absorption,h+CHI[s]*EV_ERG*g,rel_tol=2e-14,abs_tol=0)
        assert g>0 and h>0
    assert cross(13.59,"HI")==0 and cross(24.58,"HeI")==0
    assert cross(54.41,"HeII")==0 and cross(50001,"HI")==0

def main():
    data=read_source()
    checks={}
    calculations={}
    for scenario in ["z5p807","z5p95_log","z5p95_linear","z6p141"]:
        rows,rates=quadrature(data,scenario,8)
        independent_energy_closure(rows,rates)
        refined,rates16=quadrature(data,scenario,16)
        for s in VERNER:
            eps=abs(rates[s]["photo_rate_per_s"]-rates16[s]["photo_rate_per_s"])/rates16[s]["photo_rate_per_s"]
            epsh=abs(rates[s]["excess_heat_eV_per_s"]-rates16[s]["excess_heat_eV_per_s"])/rates16[s]["excess_heat_eV_per_s"]
            if max(eps,epsh)>1e-4:raise AssertionError(f"quadrature inadequate {scenario} {s} rate={eps:.9g} heat={epsh:.9g}")
        calculations[scenario]={"bands":rows,"rates":rates,
                                 "bands_16_substeps":refined,"rates_16_substeps":rates16}
        checks[scenario]="PASS_QUAD8_VS_QUAD16"
    result={"science_status":"PW19_REFORMATTED_UVB_SPECTRAL_CONDITIONAL_NOT_SOURCE_ADMITTED",
            "original_zip_sha256":ZIP_SHA,"original_zenodo_record":"10.5281/zenodo.15367103",
            "source_members":{str(k):{"sha256":v["sha256"],"member":v["member"],"rows":len(v["E"])} for k,v in data.items()},
            "spectrum_semantics":"I(E)=4*pi*nu*Jnu, integrate dln E; not local REI J_g and not P19 D1 effective rate",
            "energy_fit_domain_eV":[13.60,50000],"z_target":ZTARGET,
            "original_P19_D1_effective_rates_not_asserted_spectral_equal":ORIGINAL_D1_AT_Z5P95,
            "verner_cross_sections":"Verner et al 1996 ApJ 465 487 Table1 H I, He I, He II; thresholds distinct from chi reservoir",
            "science":calculations,"numerics":checks,"REI_central":"28/88_REPORTED",
            "BASS_HE_physical":"14/18_REPORTED","canonical_delta":0,"production":"HOLD"}
    dest=HERE/"PW19_VER96_SOURCE_CONDITIONAL_PHYSICS.json"
    dest.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("RESULT_JSON",dest,"SHA256",sha(dest.read_bytes()))
    print("SOURCE_MEMBER_SHA",result["source_members"])
    print("SCENARIO_RATES")
    for sc in calculations:
        print(sc,json.dumps(calculations[sc]["rates"],sort_keys=True))
    print("BANDS_Z5P95",json.dumps(calculations["z5p95_log"]["bands"]))
    print("TESTS",checks)
if __name__=="__main__":main()
