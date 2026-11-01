#!/usr/bin/env python3
"""Actual REI-F08 matched S0 electron-screen observer sky in prescribed Bianchi I.

This does NOT execute F09 atomic provider, a new ionization IVP, or the blocked
original 26-event canonical first interval. Original sampled ne(t) and input
byte identities are inherited unmodified. c and sigma_T retain CGS units.
"""
from __future__ import annotations
import argparse,bisect,csv,gzip,hashlib,io,json,math,statistics
from pathlib import Path

N_SOURCE=16001
N_ACCEPTED=16000
N_TIMESTEPS=4
WINDOW_FRACTIONS=(0.25,0.50,0.75,0.95)
ANGULAR_GRIDS=((8,16),(16,32),(32,64))
C_CGS=29979245800.0
SIGMA_T_CM2=6.6524587051e-25
SOURCE_SHA={
    "S0_FLRW-electron_density.csv.gz":"0b81cae87d6f90888d1d3def1995cd8d029625d1cc1dd11bffab94e8d30e7efa",
    "S0_BI-electron_density.csv.gz":"663911291bea564d314e1d46df9750c03a39fd5d9404eca6a7485776d894f723",
    "science_scenario_v1.json":"c83d2d43adda663707f99af2b45576eb4478cd94d3440a21fd21eaed32b5f2c1",
}
SOURCE_PAIR_ID="0a2bec874a5aa1b12f882033a08497b913b44447148b50b6082093bb354868e8"
GATE=2e-4
WIDTH=2e-3
CENTRAL="28/88_REPORTED"
WORKING="33/88_REPORTED"
FAST="4/7_REPORTED"

def sha(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda:f.read(1048576),b""):
            h.update(block)
    return h.hexdigest()

class History:
    def __init__(self,rows,original_nh0,helium_fraction,Hmean,end_time):
        self.t=[];self.nh=[];self.nhe=[];self.ne=[];self.lo=[];self.hi=[]
        if len(rows)!=N_SOURCE:raise ValueError("expected original 16001 S0 rows")
        prev=-1.0
        for i,r in enumerate(rows):
            t=float(r["normal_time_s"])
            nh=float(r["nH_proper_cm3"])
            nhe=float(r["nHe_proper_cm3"])
            ne=float(r["ne_proper_cm3"])
            low=float(r["ne_conditional_lo"])
            high=float(r["ne_conditional_hi"])
            doppler=float(r["D_gas_normal_observer"])
            if not all(map(math.isfinite,(t,nh,nhe,ne,low,high,doppler))):
                raise ValueError("nonfinite original H/He source electron history")
            if t<=prev or nh<=0 or nhe<=0 or low<=0 or low>ne or ne>high:
                raise ValueError("non-monotone original time or invalid source electron range")
            if abs(doppler-1)>5e-15:raise ValueError("original F08 gas is not comoving")
            if abs(nhe/nh-helium_fraction)>5e-13:raise ValueError("original helium fraction drift")
            expect=original_nh0*math.exp(-3*Hmean*t)
            if abs(nh/expect-1)>6e-12:raise ValueError("original paired source has wrong H volume evolution")
            self.t.append(t);self.nh.append(nh);self.nhe.append(nhe)
            self.ne.append(ne);self.lo.append(low);self.hi.append(high)
            prev=t
        if self.t[0]!=0 or abs(self.t[-1]-end_time)>0.02:
            raise ValueError("original S0 endpoint clock changed")
        self.end_time=end_time
    @classmethod
    def read(cls,path,nh0,fhe,Hmean,end_time):
        with gzip.open(path,"rt",encoding="utf8",newline="") as f:
            rows=list(csv.DictReader(f))
        return cls(rows,nh0,fhe,Hmean,end_time)

class ScreenIntegral:
    """Cumulative positive Thomson integral of sampled piecewise-linear proper ne."""
    def __init__(self,time,ne):
        if len(time)<3 or len(time)!=len(ne):raise ValueError("empty source history")
        self.t=list(map(float,time));self.n=list(map(float,ne))
        self.right=[0.]*len(time)
        for j in range(len(time)-2,-1,-1):
            dt=self.t[j+1]-self.t[j]
            if dt<=0 or min(self.n[j],self.n[j+1])<0:raise ValueError("bad source time/density")
            self.right[j]=self.right[j+1]+0.5*(self.n[j]+self.n[j+1])*dt
    def value(self,t):
        if not (self.t[0]<=t<=self.t[-1]):raise ValueError("emission outside original source interval")
        i=min(max(bisect.bisect_right(self.t,t)-1,0),len(self.t)-2)
        t0,t1=self.t[i:i+2]
        fraction=(t-t0)/(t1-t0)
        return self.n[i]+fraction*(self.n[i+1]-self.n[i])
    def integral(self,t):
        if not (self.t[0]<=t<=self.t[-1]):raise ValueError("outside original source interval")
        i=min(max(bisect.bisect_right(self.t,t)-1,0),len(self.t)-2)
        t0,t1=self.t[i:i+2]
        val=self.n[i]+((t-t0)/(t1-t0))*(self.n[i+1]-self.n[i])
        return self.right[i+1]+0.5*(val+self.n[i+1])*(t1-t)
    def coarsened(self,stride):
        if stride<1 or (len(self.t)-1)%stride:raise ValueError("invalid original grid coarsening")
        return ScreenIntegral(self.t[::stride],self.n[::stride])

def angular_grid(n_mu,n_phi):
    if n_mu<2 or n_phi<4 or n_phi%2:raise ValueError("invalid equal-area angular quadrature")
    for i in range(n_mu):
        mu=-1.+2*(i+0.5)/n_mu
        radial=math.sqrt(max(0.,1.-mu*mu))
        for j in range(n_phi):
            phi=2*math.pi*(j+.5)/n_phi
            yield i,j,mu,phi,(radial*math.cos(phi),radial*math.sin(phi),mu)

def log_redshift(H,n,Delta):
    weights=[n[i]*n[i]*math.exp(2*H[i]*Delta) for i in range(3)]
    return 0.5*math.log(math.fsum(weights))

def lookback(H,n,z_rel,tmax):
    if z_rel<=0 or tmax<=0 or any(h<=0 for h in H):
        raise ValueError("expected positive prescribed source-redshift")
    want=math.log1p(z_rel)
    if log_redshift(H,n,tmax)+5e-15<want:
        raise ValueError("requested redshift unavailable in original F08 time interval")
    low=0.;high=tmax
    for _ in range(57):
        mid=(low+high)/2
        if log_redshift(H,n,mid)<want:low=mid
        else:high=mid
    delta=(low+high)/2
    if delta<0 or delta>tmax or abs(log_redshift(H,n,delta)-want)>3e-14:
        raise ValueError("Bianchi emission clock root not certified")
    return delta

def effective_H(H,n,Delta):
    weight=[n[i]*n[i]*math.exp(2*H[i]*Delta) for i in range(3)]
    return math.fsum(H[i]*weight[i] for i in range(3))/math.fsum(weight)

def physics_row(H,original_H,sBI,sFL,frac,nmu,nphi,idx,original_time,opacity):
    i,j,mu,phi,n=idx
    t0=original_time
    Delta_f=frac*t0
    z_rel=math.expm1(original_H*Delta_f)
    Delta=lookback(H,n,z_rel,t0)
    te=t0-Delta;tref=t0-Delta_f
    tau_bi=opacity*sBI.integral(te)
    tau_fl=opacity*sFL.integral(tref)
    tau_bi_fixed_time=opacity*sBI.integral(tref)
    Hdir=effective_H(H,n,Delta)
    gBI=opacity*sBI.value(te)/((1+z_rel)*Hdir)*math.exp(-tau_bi)
    gFL=opacity*sFL.value(tref)/((1+z_rel)*original_H)*math.exp(-tau_fl)
    shear=[h-original_H for h in H]
    linear_geo=-opacity*sBI.value(tref)*(Delta_f/original_H)*sum(shear[k]*n[k]*n[k] for k in range(3))
    material=tau_bi_fixed_time-tau_fl
    geometry=tau_bi-tau_bi_fixed_time
    difference=tau_bi-tau_fl
    if not (0<=te<=t0 and tau_bi>=0 and tau_fl>=0 and Hdir>0):
        raise ValueError("invalid original proper-time Thomson source")
    if abs(difference-(material+geometry))>1e-20:
        raise ValueError("material/geometry source decomposition not closed")
    return {
        "window_fraction":frac,"angular_nmu":nmu,"angular_nphi":nphi,
        "mu_bin":i,"phi_bin":j,"mu":mu,"phi_rad":phi,
        "nx":n[0],"ny":n[1],"nz":n[2],
        "relative_redshift":z_rel,"emission_time_s":te,
        "flrw_reference_emission_time_s":tref,
        "directional_redshift_residual":log_redshift(H,n,Delta)-math.log1p(z_rel),
        "ne_BI_emitter_cm3":sBI.value(te),
        "tau_BI":tau_bi,"tau_FLRW":tau_fl,
        "tau_BI_conditional_sample_lo":None,"tau_BI_conditional_sample_hi":None,
        "tau_BI_fixed_FLRW_emission_time":tau_bi_fixed_time,
        "transmission_BI":math.exp(-tau_bi),"transmission_FLRW":math.exp(-tau_fl),
        "visibility_BI_per_relative_z":gBI,"visibility_FLRW_per_relative_z":gFL,
        "delta_tau_total":difference,"delta_tau_material_fixed_time":material,
        "delta_tau_geometry_fixed_relative_z":geometry,
        "delta_tau_geometry_shear_linear":linear_geo,
        "delta_tau_geometry_linear_residual":geometry-linear_geo,
        "effective_directional_H_s_inv":Hdir
    }

def quad_stats(rows,H,Hmean,screenBI,opacity,frac,tobs,nmu,nphi):
    expected=nmu*nphi
    if len(rows)!=expected:raise ValueError("angular-grid missing sky rays")
    skies=[(r["nx"],r["ny"],r["nz"]) for r in rows]
    arr=[r["delta_tau_geometry_fixed_relative_z"] for r in rows]
    vals=[r["tau_BI"] for r in rows]
    gvals=[r["visibility_BI_per_relative_z"] for r in rows]
    mean=statistics.fmean(arr)
    centered=[v-mean for v in arr]
    Q=[[statistics.fmean(centered[a]*(skies[a][i]*skies[a][j]-(1./3 if i==j else 0))
        for a in range(expected)) for j in range(3)] for i in range(3)]
    dip=[statistics.fmean(centered[a]*skies[a][i] for a in range(expected)) for i in range(3)]
    rms=math.sqrt(statistics.fmean(v*v for v in centered))
    rms_linear=math.sqrt(statistics.fmean(r["delta_tau_geometry_shear_linear"]**2 for r in rows))
    rms_rem=math.sqrt(statistics.fmean(r["delta_tau_geometry_linear_residual"]**2 for r in rows))
    if rms_linear<=0 or rms_rem/rms_linear>0.025:
        raise ValueError("shear-linear quadrupole control invalid")
    if math.sqrt(sum(v*v for v in dip))>max(1e-19,rms*2e-8):
        raise ValueError("Bianchi sky produced forbidden odd-parity dipole")
    seen={(r["mu_bin"],r["phi_bin"]):r for r in rows}
    max_parity=0.
    for r in rows:
        pair=seen[(nmu-1-r["mu_bin"],(r["phi_bin"]+nphi//2)%nphi)]
        max_parity=max(max_parity,abs(r["tau_BI"]-pair["tau_BI"]),
                       abs(r["visibility_BI_per_relative_z"]-pair["visibility_BI_per_relative_z"]))
    if max_parity>1e-17:raise ValueError("Bianchi n to minus n parity")
    if abs(sum(Q[i][i] for i in range(3)))>max(1e-18,rms*1e-9):
        raise ValueError("quadrupole not traceless")
    shear=[h-Hmean for h in H]
    tref=tobs*(1-frac)
    factor=opacity*screenBI.value(tref)*(frac*tobs/Hmean)
    analyticQ=[-(2./15.)*factor*s for s in shear]
    return {
        "fraction":frac,"z_rel":rows[0]["relative_redshift"],"angular_nmu":nmu,
        "angular_nphi":nphi,"number_of_physical_numerical_rays":expected,
        "source_BI_tau_mean":statistics.fmean(vals),
        "source_BI_tau_min":min(vals),"source_BI_tau_max":max(vals),
        "source_FLRW_tau":rows[0]["tau_FLRW"],
        "delta_material_same_time":rows[0]["delta_tau_material_fixed_time"],
        "delta_geometry_sky_mean":mean,
        "delta_geometry_sky_rms_centered":rms,
        "delta_geometry_exact_minus_linear_rms_over_linear":rms_rem/rms_linear,
        "dipole_xyz":dip,"quadrupole_xyz":Q,
        "first_order_continuum_quadrupole_diagonal":analyticQ,
        "visibility_BI_sky_mean":statistics.fmean(gvals),
        "visibility_FLRW":rows[0]["visibility_FLRW_per_relative_z"],
        "maximum_exact_geometry_abs":max(abs(x) for x in arr),
        "sky_even_parity_max_abs":max_parity,
        "maximum_directional_redshift_residual":max(abs(r["directional_redshift_residual"]) for r in rows)
    }

def write_gzip_csv(path,rows):
    keys=list(rows[0])
    with path.open("wb") as f:
        with gzip.GzipFile(fileobj=f,filename="",mode="wb",mtime=0,compresslevel=6) as z:
            with io.TextIOWrapper(z,encoding="utf8",newline="") as txt:
                writer=csv.DictWriter(txt,fieldnames=keys)
                writer.writeheader()
                for row in rows:writer.writerow(row)
    return sha(path),len(keys)

def run(repo,out):
    here=Path(__file__).resolve().parent
    origin=here/"source_inputs"
    manifest=json.loads((here/"SOURCE_PROVENANCE.json").read_text())
    for name,digest in SOURCE_SHA.items():
        if sha(origin/name)!=digest or manifest["source_inputs"][name]["sha256"]!=digest:
            raise ValueError("original F08 S0 model source identity drift: "+name)
    if manifest["source_pair_id"]!=SOURCE_PAIR_ID:
        raise ValueError("original pair source identity mismatch")
    if manifest["original_F08_return"]["scientific_admission"]!="HOLD":
        raise ValueError("original provisional source admission accidentally promoted")
    if manifest["original_F09_blocker"]["kind"]!="EXTERNAL_PROVIDER_DOMAIN_AND_BINDING_BLOCKED":
        raise ValueError("original external F09 blocker silently changed")
    scenario=json.loads((origin/"science_scenario_v1.json").read_text())
    if scenario["source"]["family"]!="S0" or scenario["background"]["tilt"]!=[0.,0.,0.]:
        raise ValueError("unexpected original source or noncomoving gas")
    if scenario["source"]["time_support_s"]!=[0.,1e13]:
        raise ValueError("original S0 source interval differs")
    if scenario["constants"]["c_cm_s"]!=C_CGS:
        raise ValueError("original source owner c changed")
    if manifest["original_sigma_T_cm2"]!=SIGMA_T_CM2:
        raise ValueError("original Thomson scattering source owner changed")
    H=tuple(float(x) for x in scenario["background"]["pairs"]["BIANCHI_I"]["H_per_s"])
    Hbar=scenario["background"]["H_mean_per_s"]
    HF=tuple(float(x) for x in scenario["background"]["pairs"]["FLRW"]["H_per_s"])
    if abs(sum(H)/3-Hbar)>1e-28 or any(abs(h-Hbar)>1e-28 for h in HF):
        raise ValueError("original FLRW/Bianchi mean expansion not matched")
    if scenario["background"]["a0"]!=[1.,1.,1.]:
        raise ValueError("original Bianchi scale factor normalization differs")
    tmax=float(scenario["time"]["t_end_s"])
    nh0=float(scenario["initial_state"]["nH0_cm3"])
    fhe=float(scenario["initial_state"]["fHe"])
    histories={}
    for label in ("S0_FLRW","S0_BI"):
        histories[label]=History.read(origin/(label+"-electron_density.csv.gz"),
                                     nh0,fhe,Hbar,tmax)
    FL=histories["S0_FLRW"];BI=histories["S0_BI"]
    if FL.t!=BI.t:raise ValueError("original paired F08 source times differ")
    op=C_CGS*SIGMA_T_CM2
    IBI=ScreenIntegral(BI.t,BI.ne);IFL=ScreenIntegral(FL.t,FL.ne)
    IBIlo=ScreenIntegral(BI.t,BI.lo);IBIhi=ScreenIntegral(BI.t,BI.hi)
    coarsen={factor:(IBI.coarsened(factor),IFL.coarsened(factor)) for factor in (2,4)}
    all_rows=[];summaries=[];maximum_time_coarse_rel=0.
    for nmu,nphi in ANGULAR_GRIDS:
        for frac in WINDOW_FRACTIONS:
            rows=[]
            for record in angular_grid(nmu,nphi):
                q=physics_row(H,Hbar,IBI,IFL,frac,nmu,nphi,record,tmax,op)
                te=q["emission_time_s"]
                low=op*IBIlo.integral(te);high=op*IBIhi.integral(te)
                if low>q["tau_BI"]+1e-18 or high<q["tau_BI"]-1e-18:
                    raise ValueError("original source samplewise electron band fails tau inclusion")
                q["tau_BI_conditional_sample_lo"]=low
                q["tau_BI_conditional_sample_hi"]=high
                for factor,(sc_b,sc_f) in coarsen.items():
                    d=abs(op*sc_b.integral(te)-q["tau_BI"])
                    d+=abs(op*sc_f.integral(q["flrw_reference_emission_time_s"])-q["tau_FLRW"])
                    maximum_time_coarse_rel=max(maximum_time_coarse_rel,d/max(q["tau_BI"],1e-100))
                rows.append(q)
            stats=quad_stats(rows,H,Hbar,IBI,op,frac,tmax,nmu,nphi)
            summaries.append(stats)
            all_rows.extend(rows)
            print("ORIGINAL_F08_S0_THOMSON_SKY",json.dumps({"grid":[nmu,nphi],
                "fraction":frac,"z_rel":stats["z_rel"],
                "tau_BI_mean":stats["source_BI_tau_mean"],
                "delta_material":stats["delta_material_same_time"],
                "delta_geometry_rms":stats["delta_geometry_sky_rms_centered"],
                "q_diag":[stats["quadrupole_xyz"][i][i] for i in range(3)],
                "g_BI_mean":stats["visibility_BI_sky_mean"]},sort_keys=True),flush=True)
    expected=sum(mu*phi for mu,phi in ANGULAR_GRIDS)*len(WINDOW_FRACTIONS)
    if len(all_rows)!=expected or maximum_time_coarse_rel>1e-4:
        raise ValueError("original angular source/time quadrature size or resolution gate failed")
    primary=[x for x in summaries if x["angular_nmu"]==16]
    fine=[x for x in summaries if x["angular_nmu"]==32]
    angular={}
    for a,b in zip(primary,fine):
        qa=[a["quadrupole_xyz"][i][i] for i in range(3)]
        qb=[b["quadrupole_xyz"][i][i] for i in range(3)]
        rel=max(abs(v-w) for v,w in zip(qa,qb))/max(max(abs(w) for w in qb),1e-100)
        angular[str(a["fraction"])]=rel
        if rel>0.04:raise ValueError("original Bianchi angular quadrature did not converge")
    out=Path(out).resolve();out.mkdir(parents=True,exist_ok=True)
    path=out/"ORIGINAL_F08_S0_BIANCHI_THOMSON_SKY.csv.gz"
    digest,ncols=write_gzip_csv(path,all_rows)
    summary={"schema":"REI_F08_S0_ACTUAL_BIANCHI_THOMSON_OBSERVER_SKY_V1",
        "status":"SOURCE_AUTHENTIC_PRESCRIBED_BIANCHI_OBSERVER_CONDITIONAL_NUMERICALLY_CHECKED",
        "time_interval_s":[0,tmax],"observer_cosmic_time_s":tmax,
        "source_original_accepted_steps_each":N_ACCEPTED,
        "source_original_history_rows_each":N_SOURCE,
        "source_inputs_sha256":SOURCE_SHA,
        "source_pair_id":SOURCE_PAIR_ID,
        "source_original_F08_scientific_admission":"HOLD",
        "source_original_F09":"BLOCKED_EXTERNAL_ATOMIC_PROVIDER_DOMAIN",
        "observer_relative_redshift_not_absolute_cosmic_z":True,
        "original_prescribed_H_s_inv":H,"flrw_H_s_inv":Hbar,
        "original_thomson_sigma_cm2":SIGMA_T_CM2,"original_c_cm_s":C_CGS,
        "ray_count":expected,"numerical_source_angle_count_not_independent_observations":True,
        "physical_science_columns":ncols-1 if "node" in all_rows[0] else ncols,
        "new_physical_ray_rows":expected,"source_sky_csv":path.name,"source_sky_csv_sha256":digest,
        "angular_quadrature_checks_main_vs_fine":angular,
        "max_time_quadrature_coarsen_relative":maximum_time_coarse_rel,
        "sky_windows":summaries,
        "numerical_sky_isotropy_at_fixed_time":"TAU_DIRECTION_INDEPENDENT_AT_EQUAL_PROPER_TIME",
        "material_vs_geometry_decomposition":"EXACT_SAMPLED_SOURCE_TIME_INTERPOLATED",
        "plasma_sampled_lo_hi_not_continuum_interval":True,
        "first_order_shear_only_conditional":True,
        "source_owner_unchanged":True,"new_atomic_provider_call":False,
        "new_cosmological_ionization_ivp":False,"no_new_canonical_nodes":True,
        "central_DAG":CENTRAL,"working_DAG":WORKING,"physical_fast_DAG":FAST,
        "canonical_delta":0,"original_26event_first_canonical_interval":"BLOCKED_TICK160/131072",
        "production":"HOLD","no_merge":True,"no_force_push":True,"auto_next":False}
    (out/"RESULT.json").write_text(json.dumps(summary,sort_keys=True,indent=2)+"\n")
    print("REI_F08_OBSERVER_FINAL",json.dumps({"rows":expected,"columns":ncols,
        "source_sha256":digest,"time_quad_max_rel":maximum_time_coarse_rel,
        "main_to_fine_quad_rel":angular,"central":CENTRAL,"canonical_delta":0},
        sort_keys=True),flush=True)
    return summary

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    run(None,args.out)

if __name__=="__main__":main()
