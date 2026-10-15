#!/usr/bin/env python3
"""Independent same-splitting no-recombination counterfactual for SOURCE07 C11.

This separates genuine RR/DR physics from changing the time integrator:
both 'off' and 'on' use the exact same C11 Strang photon/chemistry layout.
"""
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import casea as x
from rate_table import CaseARates,ConstantRates

FIELDS=("x_HII","x_HeII","x_HeIII","xe_per_H","Tgas_K",
        "thermal_eV_per_H","binding_eV_per_H",
        "photon_U_eV_per_H","radiative_escape_eV_per_H")

def main():
    model=x.C9.Scenario(x.ROOT)
    gas=x.c10.Gas.initial(model)
    he_per_h=gas.nHe/gas.nH
    rows=[]
    for source in ("bb50k","hard"):
        on=x.one_run(0,source,64,compress=True,provider=CaseARates())["final"]
        off=x.one_run(0,source,64,compress=True,provider=ConstantRates())["final"]
        delta={k:on[k]-off[k] for k in FIELDS}
        # Temperature from an ideal mixture EOS. The ratio identity is
        # exact independently of how each trajectory reached its endpoint.
        p_on=1.+he_per_h+on["xe_per_H"]
        p_off=1.+he_per_h+off["xe_per_H"]
        t_ratio=(on["thermal_eV_per_H"]/off["thermal_eV_per_H"])*(p_off/p_on)
        assert abs(t_ratio*off["Tgas_K"]-on["Tgas_K"])<1e-8
        rows.append({"source":source,"dt_s":1e12,
                     "on_provider":"unmodified Grackle derived Case A RR+DR",
                     "off_provider":"manufactured all-zero recombination/cooling, same Strang algorithm",
                     "RR_minus_off":delta,
                     "delta_thermal_energy_sign": "negative" if delta["thermal_eV_per_H"]<0 else "nonnegative",
                     "delta_particle_count_sign":"negative" if delta["xe_per_H"]<0 else "nonnegative",
                     "delta_T_sign":"positive" if delta["Tgas_K"]>0 else "nonpositive",
                     "EOS_temperature_ratio":t_ratio,
                     "cumulative_RR_electrons_per_H":on["cumulative_recombination_electrons_per_H"]})
    result={"schema":"rei.source07.c11.same_step_caseA_vs_off.v1",
            "cases":rows,"equation":"T_on/T_off=(u_on/u_off) *((1+nHe/nH+xe_off)/(1+nHe/nH+xe_on))",
            "wolfram_symbolic_identity":"(u-q)/(D-R)-u/D=(u R-D q)/(D(D-R)); CAS returned {0,True}"}
    (HERE/"ZERO_RATE_CONTROL.json").write_text(json.dumps(result,indent=2)+"\n")
    for row in rows:
        print(row["source"],row["RR_minus_off"])


if __name__=="__main__":
    main()
