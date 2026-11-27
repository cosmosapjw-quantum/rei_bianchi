"""One-time exact-SI conversion and explicit finite-model source admission."""
from pathlib import Path
from decimal import Decimal as D, localcontext
import copy, hashlib, json
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'source_data/ADMITTED_FINITE_CI_REGISTRY.json'

def main():
    if OUT.exists():raise FileExistsError('ADMISSION_ALREADY_CREATED; reuse rather than recalculate')
    src=ROOT/'source_data/PHYS81_ATOMIC_CI_SOURCE_REGISTRY.json';r=json.loads(src.read_text())
    before=copy.deepcopy(r['source_curves'][2])
    with localcontext() as ctx:
        ctx.prec=60
        hc_cm_eV=D('6.62607015e-34')*D('299792458')*D(100)/D('1.602176634e-19')
        li7=D('43487.15940')*hc_cm_eV
        unc=D('0.00018')*hc_cm_eV
        threshold=li7+D('59.020708')
        difference=li7-D(before['chemical_I_eV'])
    li=r['source_curves'][2]
    li.update(chemical_I_eV=str(li7),chemical_I_uncertainty_eV=str(unc),chemical_source_url='https://www.pnnl.gov/publications/ionization-energy-li-6li-7-determined-triple-resonance-laser-spectroscopy',chemical_source_sha256='dfe6056f9915ddbf0ef98bfa7e28b24606e7f484c81979ec650ecd45ebaab1e0',chemical_reference_doi='10.1103/PhysRevA.75.052503',chemical_literal_cm_inverse='43487.15940',chemical_literal_uncertainty_cm_inverse='0.00018',excited_residual_internal_threshold_eV=str(threshold))
    r.update(schema='PHYS81_ADMITTED_FINITE_OPERATOR_REGISTRY_V2',status='ADMITTED_EXPLICIT_FINITE_MODEL_ONLY',parent_registry_SHA256=hashlib.sha256(src.read_bytes()).hexdigest(),energy_contract='H1 ASD/HDEL under ordinary-hydrogen convention; He4 explicitly qualified neutral ASD; Li7 original isotope-qualified Bushaw2007 literal converted with exact SI hc/eV. Chemical defects differ from source support floors.',stationary_target_approximation='Electron-mass Maxwell average of incident-energy table. Shared common-T reservoir/EOS does not make this a finite-mass double-Maxwell collision closure.',numerical_temperature_domain_K=[255.0,50000.0],physical_full_rate_admission='NOT_ISSUED',Li7_correction={'previous_elemental_ASD_entry':before,'reason':'Original-author 7Li spectroscopic limit differs from generic ASD Li entry; generic value is not silently isotope-qualified. No claim that the latter is a natural-isotope average.','exact_SI_hc_cm_eV':str(hc_cm_eV),'new_minus_previous_eV':str(difference),'changed_dependencies':['chemical potential','Li daughter excited threshold sum','parcel thermal/Jacobian map'],'unchanged_dependencies':['literal cross sections','energy grid','finite Maxwell integrals','no source-axis isotope shift']})
    OUT.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
    receipt={'source_conversion_evaluations':1,'ODE':0,'LI7_I_eV':str(li7),'LI7_I_uncertainty_eV':str(unc),'LI7_excited_residual_threshold_eV':str(threshold),'LI7_delta_to_generic_ASD_eV':str(difference),'admission_SHA256':hashlib.sha256(OUT.read_bytes()).hexdigest()}
    (ROOT/'verification/LI7_SOURCE_CORRECTION.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt))

if __name__=='__main__':main()
