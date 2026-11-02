#!/usr/bin/env python3
"""Independent stdlib audit of 460800 authentic original F05 RHS cell/site rows.

Does not import NumPy or source solver. Re-derives dNe, dB, dU and trajectory
residual/Simpson sums and preserves no claim of certified continuous solution.
"""
import argparse, csv, gzip, hashlib, json, math
from pathlib import Path
N=46080;KB=1.380649e-16;EV=1.602176634e-12
CHIH=13.598434599702;CHI1=24.587389011;CHI2=54.41776
SHA_RAW="4b5d69ef35f9a5c954417d9e2b1460d435523d328ea7c4bac89587dac5ab8352"
SHA_SUM="d5474b5c2b8dbb96bad28da2aaca5fcffd78e7c7d91901ec7c4e04d776e5adc5"
SITES=(0,.25,.5,.75,1)
WEIGHTS=(1/12,4/12,2/12,4/12,1/12)
CODES=("x_HI","x_HeI","r_HeIII","logT")
def need(x,s):
    if not x:raise ValueError("INDEPENDENT_REI_F05_RESIDUAL_"+s)
def digest(p):
    h=hashlib.sha256()
    with Path(p).open("rb") as f:
        for b in iter(lambda:f.read(4<<20),b""):h.update(b)
    return h.hexdigest()
def c(a,b,rel=4e-12,absmin=1e-280):
    return math.isfinite(a) and math.isfinite(b) and abs(a-b)<=rel*max(abs(a),abs(b),absmin)
def f(row,name):return float(row[name])
def audit(a):
    need(digest(a.raw)==SHA_RAW,"RAW_SHA")
    need(digest(a.science)==SHA_SUM,"PUBLIC_SHA")
    science=json.loads(Path(a.science).read_text())
    need(science["schema"]=="REI_F05_ORIGINAL_26EVENT_10SITE_CONTINUUM_RESIDUAL_V1","SOURCE_SCHEMA")
    need(science["official_tick161"] is False and science["official_tick162"] is False and science["DAG"]["central"]=="28/88","FALSE_CANONICAL")
    need(science["actual_source_cell_site_rows"]==460800 and science["original_source_point_evaluations"]==10,"PHYSICAL_ROW_COUNT")
    dt=float(science["original_proper_tick_seconds"])
    snapshots={}
    max_local_chem=0.;max_local_thermal=0.;max_residual=0.
    seen=0
    with gzip.open(a.raw,"rt",newline="") as inp:
      reader=csv.DictReader(inp)
      require_names={f"f_{s}" for s in CODES}|{f"res_{s}" for s in CODES}|{f"slope_{s}" for s in CODES}
      need(require_names.issubset(set(reader.fieldnames)),"SOURCE_FIELDS")
      for ix,(ta,tb) in enumerate(((160,161),(161,162))):
        signed=[[0.0]*N for _ in range(4)]
        for k,site in enumerate(SITES):
          arrays={key:[] for key in ("HI","HeI","HeII","Ne","B","U","dNe","Bdot","Udot")}
          maxr=[0.]*4;sumr2=[0.]*4;vmin=1.;vmax=0.
          for node in range(N):
            try:r=next(reader)
            except StopIteration as ex:raise ValueError("RAW_TRUNCATED") from ex
            seen+=1
            need(int(r["interval_a"])==ta and int(r["interval_b"])==tb and int(r["cell"])==node,"SAMPLE_ORDER")
            need(c(f(r,"site"),site,1e-15) and c(f(r,"proper_time_s"),(ta+site)*dt,2e-15),"SOURCE_CLOCK")
            nh=f(r,"N_H");he=f(r,"N_He")
            xa,xb,q,l=(f(r,"y_"+x) for x in CODES)
            fa,fb,fq,fl=(f(r,"f_"+x) for x in CODES)
            v=f(r,"v_source")
            need(nh>0 and he>0 and 0<xa<1 and 0<xb<1 and 0<q<1 and math.isfinite(l) and 0<=v<=1,"PHYSICAL_CONE")
            T=math.exp(l)
            h2=nh*(1-xa);he2=he*(1-xb)*(1-q);he3=he*(1-xb)*q
            Ne=h2+he2+2*he3
            dH2=-nh*fa
            dHe2=-he*((1-q)*fb+(1-xb)*fq)
            dHe3=he*(-q*fb+(1-xb)*fq)
            dNe=dH2+dHe2+2*dHe3
            B=EV*(CHIH*h2+CHI1*(he2+he3)+CHI2*he3)
            Bdot=EV*(CHIH*dH2+CHI1*(dHe2+dHe3)+CHI2*dHe3)
            U=1.5*KB*(nh+he+Ne)*T
            Udot=U*(fl+dNe/(nh+he+Ne))
            values=(Ne,B,U,dNe,Bdot,Udot)
            for key,ref in zip(("N_e","B_erg","U_gas_erg","dNe_dt_s_inv","Bdot_erg_s","Udot_erg_s"),values):
              given=f(r,key)
              if key=="dNe_dt_s_inv":
                need(c(given,ref,2e-11),"ELECTRON_RATE_IDENTITY")
              elif key=="Udot_erg_s":
                need(c(given,ref,2e-11),"GAS_ENERGY_IDENTITY")
              else:need(c(given,ref,2e-11),"THERMOCHEMISTRY_"+key)
            localB=abs(Bdot-f(r,"Bdot_erg_s"))/max(abs(Bdot),abs(f(r,"Bdot_erg_s")),1e-280)
            localU=abs(Udot-f(r,"Udot_erg_s"))/max(abs(Udot),abs(f(r,"Udot_erg_s")),1e-280)
            max_local_chem=max(max_local_chem,localB)
            max_local_thermal=max(max_local_thermal,localU)
            for field,value in (("HI",nh*xa),("HeI",he*xb),("HeII",he*(1-xb)*(1-q)),
                 ("Ne",Ne),("B",B),("U",U),("dNe",dNe),("Bdot",Bdot),("Udot",Udot)):
                arrays[field].append(value)
            for j,name in enumerate(CODES):
                sf=f(r,"slope_"+name);fv=f(r,"f_"+name);R=f(r,"res_"+name)
                need(c(R,sf-fv,5e-11,1e-270),"FIELD_RESIDUAL_"+name)
                signed[j][node]+=dt*WEIGHTS[k]*R
                hR=abs(dt*R)
                maxr[j]=max(maxr[j],hR)
                sumr2[j]+=(dt*R)**2
            vmin=min(vmin,v);vmax=max(vmax,v)
          data=science["epochs"][ix]["source_samples"][k]
          scalar_names={"HI":"global_S_HI","HeI":"global_S_HeI","HeII":"global_S_HeII",
           "Ne":"global_N_e","B":"global_B_erg","U":"global_U_gas_erg",
           "dNe":"global_dNe_dt_s_inv","Bdot":"global_original_Bdot_erg_s","Udot":"global_original_Udot_erg_s"}
          for key,sname in scalar_names.items():
            need(c(math.fsum(arrays[key]),float(data[sname]),8e-11),"SOURCE_AGGREGATE_"+sname)
          for j,name in enumerate(CODES):
            need(c(maxr[j],data["h_times_sample_max_abs_residual"][j],1e-12),"RESIDUAL_MAX_"+name)
            need(c(math.sqrt(sumr2[j]/N),data["h_times_sample_rms_residual"][j],1e-12),"RESIDUAL_RMS_"+name)
          need(c(vmin,data["v_source_minmax"][0],1e-12,1e-14) and c(vmax,data["v_source_minmax"][1],1e-12,1e-14),"ORIGINAL_SOURCE_V")
          snapshots[(ta,tb,k)]={"Bdot":math.fsum(arrays["Bdot"]),"Udot":math.fsum(arrays["Udot"]),
             "Ne":math.fsum(arrays["Ne"]),"HI":math.fsum(arrays["HI"]),"HeII":math.fsum(arrays["HeII"])}
          print("AUDIT_SITE",ta,tb,site,"ROWS",N,flush=True)
        for j,name in enumerate(CODES):
          maxsq=max(abs(x) for x in signed[j])
          rmssq=math.sqrt(math.fsum(x*x for x in signed[j])/N)
          summa=math.fsum(signed[j])
          obj=science["epochs"][ix]
          need(c(maxsq,obj["sampled_simpson_max_abs_residual_by_coord"][j],1e-11),"SIM_MAX_"+name)
          need(c(rmssq,obj["sampled_simpson_rms_residual_by_coord"][j],1e-11),"SIM_RMS_"+name)
          need(c(summa,obj["sampled_simpson_signed_residual_sum"][j],2e-11),"SIM_SUM_"+name)
    with gzip.open(a.raw,"rt",newline="") as check_rows:
      raw_line_count=sum(1 for _ in check_rows)-1
    need(raw_line_count==seen==460800,"RAW_EXACT_ROW_COUNT")
    for q in ("Bdot","Udot","Ne","HI","HeII"):
      need(c(snapshots[(160,161,4)][q],snapshots[(161,162,0)][q],1e-12),"JOIN_POINT_"+q)
    need(c(snapshots[(160,161,0)]["Bdot"],-7.693137946550566e39,1e-12),"ORIGINAL_T160_PREVIOUS_OWNER_SOURCE")
    result={"schema":"REI_F05_CONTINUUM_RESIDUAL_INDEPENDENT_460800_STDLIB_AUDIT_V1",
        "status":"PASS_NUMERIC_SAMPLED_ORIGINAL_SOURCE_ONLY",
        "source_input_sha256":SHA_RAW,"public_science_sha256":SHA_SUM,
        "actual_original_cells_per_site":N,"original_source_rhs_sites":10,"original_cell_site_records":seen,
        "max_relative_chemical_identity_discrepancy":max_local_chem,
        "max_relative_gas_thermal_identity_discrepancy":max_local_thermal,
        "exact_shared_tick161_source_endpoint":"NUMERICALLY_CHECKED_BOTH_PATHS",
        "original_tick160_source_agrees_REI367":True,
        "sampled_residual_is_proven_supremum":False,
        "source_continuum_truncation_error_certified":False,
        "sampled_time_quadrature_error_bounded":False,
        "owner_admission":"SOURCE_SCOPED_POINT_RESIDUAL_AND_ORIGINAL_HHE_ENERGY_TREND_ONLY",
        "official_tick161":False,"official_tick162":False,
        "DAG":{"central":"28/88","working":"33/88_NONADDITIVE","fast":"4/7","delta":0}}
    p=Path(a.out);need(not p.exists(),"NO_OVERWRITE_AUDIT");p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+"\n")
    print(json.dumps({"audit":"PASS","source_cell_site_records":seen,"max_chemical_relative_difference":max_local_chem,
        "max_thermal_relative_difference":max_local_thermal,"audit_sha256":digest(p),"canonical":"28/88"}))
if __name__=="__main__":
    p=argparse.ArgumentParser()
    for arg in ("raw","science","out"):p.add_argument("--"+arg,required=True)
    audit(p.parse_args())
