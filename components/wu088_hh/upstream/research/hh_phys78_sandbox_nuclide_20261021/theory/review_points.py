"""C9 independent pointwise physics checks; no ODE integration."""
from pathlib import Path
import sys, json, hashlib, math
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"phys78_impl"/"source"))
import atomic_network as at
import coupled_model as cm

def kinetic_directional_derivative(k,x,b,w):
    r=math.exp(-x)
    p2=r*r*k.q2*math.exp(2*b)*(1-k.mu2)
    z2=r*r*k.q2*math.exp(-4*b)*k.mu2
    energy=np.sqrt(k.mass*k.mass+p2+z2)
    de=((-1+w)*p2+(-1-2*w)*z2)/energy
    dm=float(np.sum(k.weights*r**3*(de-3*energy)))
    rp=math.exp(2*b)*(1-k.rmu2)
    rz=math.exp(-4*b)*k.rmu2
    er=np.sqrt(rp+rz)
    dr=float(np.sum(k.rweights*r**4*(w*(rp-2*rz)/er-4*er)))
    return dm,dr

cases=[]
for sigma,am,ar,x,b in [(.1,.8,-.8,0.,0.),(-.1,-.8,.8,.7,.03),(.001,0.,0.,1.6,-.02)]:
    case={"sigma0_F_signed":sigma,"A_m":am,"A_r":ar,"uv_scale":1.}
    m=cm.CoupledModel(case)
    y=m.initial_state.copy()
    initial=m.environment(0,y)
    initial_sigma=math.sqrt(6)*initial["s_over_H"]
    y[cm.I_B]=b
    # Interior atom populations exercise every PI/RR pair as a point control,
    # not as a proposed primordial abundance/ionization donor or trajectory.
    for iso,total in zip(at.ISOTOPES,m.isotope_totals):
        idx=[i for i,s in enumerate(at.SPECIES) if s.isotope==iso]
        if total:
            weights=np.arange(len(idx),0,-1,dtype=float)
            y[cm.S_Y][idx]=total*weights/weights.sum()
    particles=y[cm.S_Y].sum()+at.CHARGE@y[cm.S_Y]
    y[cm.I_U]=1.5*at.KB_EV_K*12000*particles
    y[cm.S_N]=[1e-10,2e-10,3e-10]
    y[cm.S_U]=y[cm.S_N]*[17.,28.,58.]
    y[cm.I_R]=.2
    dy,e=m.evaluate(x,y,allow_solver_extension=False)
    dm,dr=kinetic_directional_derivative(m.kinetic,x,b,e["s_over_H"])
    mom=m.kinetic.moments(x,b)
    expected_m=-3*(mom["rho_m"]+mom["pbar_m"])-6*e["s_over_H"]*mom["pi_m"]
    expected_r=-4*mom["rho_r"]-6*e["s_over_H"]*mom["pi_r"]
    dgas=e["eV_density_norm"]*(dy[cm.I_U]+m.atomic.binding_eV@dy[cm.S_Y]+dy[cm.I_RESERVOIR]
            -3*(m.rest_energy_per_H+y[cm.I_U]+e["binding_eV_per_H"]+y[cm.I_RESERVOIR]))
    dgray=e["eV_density_norm"]*(dy[cm.S_U].sum()+dy[cm.I_R]
            -3*(y[cm.S_U].sum()+y[cm.I_R]))
    drho=-3*e["rho_cold"]+cm.OMEGA_WARM/cm.A0**3*dm+cm.OMEGA_R/cm.A0**4*dr+dgas+dgray
    target=-3*(e["rho_total"]+e["pbar_total"])-6*e["s_over_H"]*(e["pi_m"]+e["pi_r"])
    hp=(cm.H0**2*drho+2*e["s"]*cm.HREF*dy[cm.I_Q])/(2*e["H"])
    htarget=-(1.5*cm.H0**2*(e["rho_total"]+e["pbar_total"])+3*e["s"]**2)/e["H"]
    aa=m.arrays(np.array([x]),y[None,:])
    signedtotal=aa["signed_Pi_m_F"][0]+aa["signed_Pi_r_F"][0]
    metrics={
        "sigma0_abs_error":abs(initial_sigma-sigma),
        "massive_continuity_relative":abs(dm-expected_m)/max(abs(dm),abs(expected_m),1e-300),
        "radiation_continuity_relative":abs(dr-expected_r)/max(abs(dr),abs(expected_r),1e-300),
        "total_density_continuity_relative":abs(drho-target)/max(abs(drho),abs(target),1e-300),
        "friedmann_raychaudhuri_directional_relative":abs(hp-htarget)/max(abs(hp),abs(htarget),1e-300),
        "gray_exchange_relative":abs(e["energy_balance_rel"]),
        "norm_half_difference":float(abs(aa["Pi_total_F"][0]-math.sqrt(2)*aa["Pi_total_half"][0])),
        "signed_total_before_norm_difference":float(abs(aa["Pi_total_F"][0]-abs(signedtotal))),
        "isotope_rhs_abs_max":float(np.max(np.abs(at.ISOTOPE_SUM@dy[cm.S_Y]))),
        "initial_v2_energy_weighted":float(3*m.kinetic.moments(0,0)["pbar_m"]/m.kinetic.moments(0,0)["rho_m"])
    }
    for k,v in metrics.items():
        if k!="initial_v2_energy_weighted":
            assert v<5e-13,(k,v)
    cases.append({"case":case,"x":x,"beta":b,"metrics":metrics})
source_dir=ROOT/"phys78_impl"/"source"
out={"status":"PASS_SCOPED_INDEPENDENT_ANALYTIC_POINT_CHECK","point_count":len(cases),
     "criterion":"each listed algebraic/relative residual <5e-13; isotope RHS absolute residual <5e-13/H/x",
     "cases":cases,"ode_integrations":0,"benchmarks":0,"state_source":"constructed interior point controls, not scientific trajectories",
     "source_sha256":{p.name:hashlib.sha256(p.read_bytes()).hexdigest()
                      for p in (source_dir/"kinetic.py",source_dir/"coupled_model.py",source_dir/"atomic_network.py")}}
(ROOT/"phys78_physics"/"COUPLED_POINT_CHECK.json").write_text(json.dumps(out,indent=2)+"\n")
print(json.dumps(out,indent=2))

