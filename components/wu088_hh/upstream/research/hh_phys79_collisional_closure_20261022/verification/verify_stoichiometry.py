"""Exact finite-network operator audit; no rate fits or ODE histories are run."""
from fractions import Fraction as F
import json
from pathlib import Path
isotopes = [('H1',1,1),('D',2,1),('T',3,1),('He3',3,2),('He4',4,2),('Li6',6,3),('Li7',7,3),('n',1,0)]
thresholds = {1:[F('13.6')], 2:[F('24.59'),F('54.42')], 3:[F('5.392'),F('75.64'),F('122.5')],0:[]}
species=[]; eps=[]; transitions=[]
for isotope,a,z in isotopes:
    offset=len(species)
    for q in range(z+1):
        species.append((isotope,a,z,q)); eps.append(sum(thresholds[z][:q],F(0)))
    for q in range(z):
        vec=[0]*22; vec[offset+q]=-1; vec[offset+q+1]=1; vec[-1]=1
        transitions.append((isotope,q,vec,thresholds[z][q]))
assert len(species)==21 and len(transitions)==13
isotope_rows=[[int(s[0]==iso) for s in species]+[0] for iso,_,_ in isotopes]
charge=[s[3] for s in species]+[-1]
nucleons=[s[1] for s in species]+[0]
eps=eps+[F(0)]
def dot(a,b): return sum(x*y for x,y in zip(a,b))
ci=[]; cx=[]
for isotope,q,vec,chi in transitions:
    assert all(dot(row,vec)==0 for row in isotope_rows)
    assert dot(charge,vec)==0 and dot(nucleons,vec)==0
    assert sum(vec)==1 and dot(eps,vec)==chi
    ci.append({'isotope':isotope,'initial_charge':q,'binding_change_eV':str(chi),'energy_residual_eV':'0'})
for ia,qa,va,ca in transitions:
    for ib,qb,vb,cb in transitions:
        if ia==ib: continue
        vec=[b-a for a,b in zip(va,vb)]
        assert all(dot(row,vec)==0 for row in isotope_rows)
        assert dot(charge,vec)==0 and dot(nucleons,vec)==0
        assert sum(vec)==0 and vec[-1]==0
        assert dot(eps,vec)==cb-ca
        cx.append({'receiver':ia,'receiver_initial_charge':qa+1,'donor':ib,'donor_initial_charge':qb,'binding_change_eV':str(cb-ca),'energy_residual_eV':'0'})
# New isotope-aware potential for isolated D/H CX only, not PHYS78's global PI+RR model.
kb=F('1.380649e-23')/F('1.602176634e-19'); defect=43*kb
hh=next(t for t in transitions if t[0]=='H1')
dd=next(t for t in transitions if t[0]=='D')
vec=[b-a for a,b in zip(hh[2],dd[2])] # H+ + D -> H + D+
eps_d=list(eps)
d_index=next(i for i,s in enumerate(species) if s[0]=='D' and s[3]==1)
eps_d[d_index]+=defect
assert dot(eps_d,vec)==defect
out={'status':'PASS_EXACT_RATIONAL_ALGEBRA','scope':'13 CI operator and 140 cross-isotope CX operator structures; no physical rate admission','species_count_without_electron':21,'ci_operator_count':len(ci),'cx_operator_count':len(cx),'all_isotope_nucleon_charge_conservation':True,'all_binding_thermal_per_event_residuals_exact_zero':True,'D_H_forward_defect_eV':float(defect),'D_H_forward_defect_exact':str(defect),'PHYS78_potential_for_D_H_defect_eV':str(dot(eps,vec)),'D_H_policy':'new isolated isotope-aware potential; no mutation or rerun of PHYS78','ci':ci,'cx':cx,'ode_runs':0}
p=Path(__file__).with_name('STOICHIOMETRY_EXACT_CHECK.json');p.write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k not in ('ci','cx')},indent=2))
