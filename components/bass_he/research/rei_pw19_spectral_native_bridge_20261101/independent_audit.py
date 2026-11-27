#!/usr/bin/env python3
"""Same-author adversarial audit with a separate uniform-midpoint integrator.
Does not import the primary implementation; assesses conditional UVB source only.
"""
import bisect,csv,hashlib,io,json,math,zipfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
source=HERE/"source_original_v1.zip"
result=HERE/"PW19_VER96_SOURCE_CONDITIONAL_PHYSICS.json"
SEDS={"HI":(13.6,.4298,54750.,32.88,2.963,0.,0.,0.,13.598434599702),
      "HeI":(24.59,13.61,949.2,1.469,3.188,2.039,.4434,2.136,24.587389011),
      "HeII":(54.42,1.720,13690.,32.88,2.963,0.,0.,0.,54.41776)}
eV=1.602176634e-12
def fetch():
    b=source.read_bytes()
    assert hashlib.sha256(b).hexdigest()=="afd470b9fd934234e7f6e815d6887814a2ff8767e61f0d2a8e6187efde8d0d55"
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        spec={}
        for rs in ("05.807000","06.141000"):
            n=[k for k in z.namelist() if k.endswith("PW19/z_"+rs+".csv")]
            assert len(n)==1
            rows=list(csv.DictReader(io.StringIO(z.read(n[0]).decode())))
            spec[rs]=[(float(r["E (eV)"]),float(r["I (erg/s/cm**2)"])) for r in rows]
    x=[a for a,b in spec["05.807000"]]
    assert x==[a for a,b in spec["06.141000"]] and len(x)==626
    assert sum(y==0 for e,y in spec["05.807000"])==1
    assert sum(y==0 for e,y in spec["06.141000"])==1
    assert x[290]==48.355849560166504
    alpha=(5.95-5.807)/(6.141-5.807)
    all_int=[]
    for a,b in zip(spec["05.807000"],spec["06.141000"]):
        y0=a[1];y1=b[1]
        all_int.append(y0**(1-alpha)*y1**alpha if y0>0 and y1>0 else (1-alpha)*y0+alpha*y1)
    return x,all_int

def xs(e,s):
    th,e0,sigma0,ya,p,yw,y0,y1,chi=SEDS[s]
    if e<th or e>50000:return 0.
    q=e/e0-y0
    u=math.sqrt(q*q+y1*y1)
    return 1e-18*sigma0*((q-1)**2+yw*yw)*math.exp((p/2-5.5)*math.log(u)-p*math.log1p(math.sqrt(u/ya)))

def audit(n=120000):
    energies,intens=fetch()
    nodes=[math.log(k) for k in energies]
    logI=[math.log(v) if v>0 else None for v in intens]
    def intensity(t):
        i=min(max(0,bisect.bisect_right(nodes,t)-1),len(nodes)-2)
        a=(t-nodes[i])/(nodes[i+1]-nodes[i])
        if logI[i] is None or logI[i+1] is None:
            return (1-a)*intens[i]+a*intens[i+1]
        return math.exp((1-a)*logI[i]+a*logI[i+1])
    truth=json.loads(result.read_text())
    target=truth["science"]["z5p95_log"]["rates"]
    report={}
    for s,fit in SEDS.items():
        lo=fit[0]; start=math.log(lo); dx=(math.log(50000)-start)/n
        gamma=0.; absorbed=0.
        # Independent uniform dlnE midpoint, no shared spectral-band endpoint.
        for j in range(n):
            t=start+(j+.5)*dx
            E=math.exp(t)
            term=intensity(t)*xs(E,s)*dx
            absorbed+=term
            gamma+=term/(E*eV)
        heating=absorbed/eV-fit[-1]*gamma
        rrate=target[s]["photo_rate_per_s"]
        rh=target[s]["excess_heat_eV_per_s"]
        delta_g=abs(gamma-rrate)/rrate
        delta_h=abs(heating-rh)/rh
        assert delta_g<0.0003 and delta_h<0.0003,(s,delta_g,delta_h)
        assert gamma>0 and absorbed>heating*eV and heating>0
        report[s]={"independent_midpoint_gamma":gamma,"independent_midpoint_heat_eV_s":heating,
                   "original_gamma_relative_deviation":delta_g,"original_heating_relative_deviation":delta_h,
                   "energy_absorption_erg_per_atom_s":absorbed}
    # Adversarial counterfactual: unweighted D1 cannot be swapped with the spectrum output.
    assert target["HI"]["spectrum_rate_over_D1_effective"]>5
    assert target["HeI"]["spectrum_rate_over_D1_effective"]>5
    dest=HERE/"INDEPENDENT_SOURCE_AUDIT.json"
    full={"type":"SAME_AUTHOR_SEPARATE_ALGORITHM_NOT_DISTINCT_AUTHOR_REFEREE",
          "rows":len(energies),"integral_domain_eV":[13.6,50000],
          "midpoint_subintervals_per_species":n,"source_zero_energy_eV":energies[290],
          "results":report,"status":"PASS_CONDITIONAL","central":"28/88_REPORTED","HE":"14/18_REPORTED"}
    dest.write_text(json.dumps(full,indent=2,sort_keys=True)+"\n")
    print("AUDIT",json.dumps(report,sort_keys=True))
    print("AUDIT_SHA256",hashlib.sha256(dest.read_bytes()).hexdigest())
    print("AUDIT_STATUS PASS_CONDITIONAL")
if __name__=="__main__":audit()
