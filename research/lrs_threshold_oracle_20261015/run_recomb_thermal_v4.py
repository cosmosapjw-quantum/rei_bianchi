"""Produce reproducible conditional H/He temperature and ion histories.

All histories are prescribed-H, source-free toy experiments; never label
physical cosmological reionization or production BBN abundance predictions.
"""
import csv
import json
import sys
from dataclasses import asdict
from pathlib import Path
import numpy as np

from lrs_threshold_oracle import Ray,GAUSS8
from dynamic_chemistry import Gas
from recomb_thermal import PhotoRecombRates,evolve_thermal

HERE=Path(__file__).resolve().parent
EVIDENCE=HERE/'evidence'/'v4_recomb_thermal'
EVIDENCE.mkdir(parents=True,exist_ok=True)

# Keep the original independent V3 reference initial composition unchanged.
GAS=Gas(.37,.03,.085,.012,.003)
RATES=PhotoRecombRates(photo_per_mb=2.0,recomb_at_tref=(.32,.15,.12),
                       temperature_ref_K=10000.0,temperature_power=(.7,.7,.7))
END=.65

def rays(s):
    return tuple(Ray(e,float(mu),.5*float(weight)*count,s)
                 for e,count in ((110.,.12),(72.,.08),(43.,.06))
                 for mu,weight in GAUSS8)

# Direct RHS has a different implementation of photo/recomb and energy.
sys.path.insert(0,str(HERE/'tests'))
from test_recomb_thermal import independent_continuous,state_array


def execute():
    trials=[]
    tracks=[]
    for s in (-.04,0.,.04):
        ray_set=rays(s)
        ref=independent_continuous(ray_set,GAS,END,8000.0,RATES)
        for h in (.08,.04,.02,.01,.005):
            r=evolve_thermal(ray_set,GAS,END,max_step=h,rates=RATES,
                              temperature_initial_K=8000.,history=(h==.005))
            delta=state_array(r)-ref
            row={"s_over_h":s,"Sigma":3**.5*abs(s),"max_step":h,
                 "steps":r.steps,"max_abs_discrepancy":float(np.max(abs(delta))),
                 "weighted_error":float(np.max(abs(delta)/np.maximum(1.,abs(ref)))),
                 "Tgas_K":r.final_temperature_K,
                 "electron":r.final.electrons,
                 "HII_H":r.final.HII/r.final.hydrogen,
                 "HeI_He":r.final.HeI/r.final.helium,
                 "HeII_He":r.final.HeII/r.final.helium,
                 "HeIII_He":r.final.HeIII/r.final.helium,
                 "photon_electron_residual":r.photon_reaction_residual,
                 "electron_reaction_residual":r.electron_reaction_residual,
                 "gas_H_residual":r.hydrogen_residual,
                 "gas_He_residual":r.helium_residual,
                 "total_energy_residual_ev":r.energy_residual_ev,
                 "photo_events":list(r.photo_events),
                 "recomb_events":list(r.recomb_events),
                 "work_photon_ev":r.photo_redshift_work_ev,
                 "work_gas_ev":r.gas_adiabatic_work_ev,
                 "recomb_escaped_ev":r.escaped_recomb_energy_ev}
            if h==.005:
                for q in r.history:
                    hist={"s_over_h":s,"Sigma":3**.5*abs(s),
                          "X":q['X'],"Tgas_K":q['Tgas_K'],
                          "n_e":q['ne'],"HII_over_H":q['stocks']['HII']/GAS.hydrogen,
                          "HeI_over_He":q['stocks']['HeI']/GAS.helium,
                          "HeII_over_He":q['stocks']['HeII']/GAS.helium,
                          "HeIII_over_He":q['stocks']['HeIII']/GAS.helium,
                          "remaining_photons":q['photons'],
                          "pi_over_u":q['pi_over_u']}
                    tracks.append(hist)
            trials.append(row)
            print(f"s/H={s:+.3f} step={h:.3f} nsteps={r.steps} err={row['max_abs_discrepancy']:.6g} ne={row['electron']:.8g} T={row['Tgas_K']:.5g}",flush=True)
    (EVIDENCE/'convergence.json').write_text(json.dumps({
        "status":"NUMERICALLY_CHECKED_IN_CHATGPT_SANDBOX_CONDITIONAL_TOY",
        "date":"2026-10-16",
        "assumptions":"fixed H/H0=1, no source/recomb photon retransport, approximate alpha(T) exponents, toy coefficients",
        "initial_gas":asdict(GAS),"rates":asdict(RATES),
        "initial_temperature_K":8000.,"X_end":END,
        "comparison":"independent continuous SciPy Radau, exact ray threshold partition, rtol=3e-11 atol=4e-13",
        "results":trials},indent=2,sort_keys=True)+'\n')
    with (EVIDENCE/'temperature_ion_history.csv').open('w',newline='') as fh:
        writer=csv.DictWriter(fh,fieldnames=list(tracks[0]))
        writer.writeheader();writer.writerows(tracks)
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        # No color, style, or accuracy embellishment: matplotlib defaults.
        for metric,title,ylabel,filename in [
            ('HII_over_H','H II fraction','n_HII / n_H','HII_history.png'),
            ('HeII_over_He','He II fraction','n_HeII / n_He','HeII_history.png'),
            ('HeIII_over_He','He III fraction','n_HeIII / n_He','HeIII_history.png'),
            ('Tgas_K','Gas temperature','T_gas [K]','Tgas_history.png')]:
            fig,ax=plt.subplots(figsize=(6.0,3.7))
            for s in (-.04,0.,.04):
                arr=[r for r in tracks if r['s_over_h']==s]
                ax.plot([r['X'] for r in arr],[r[metric] for r in arr],
                        label=f's/H={s:+.2f}')
            ax.set(xlabel=r'$X=\ln(a/a_0)$',ylabel=ylabel,title=title)
            ax.legend(); fig.tight_layout()
            fig.savefig(EVIDENCE/filename,dpi=155)
            plt.close(fig)
    except ImportError:
        print('matplotlib not installed: skipping optional figures')
    return trials

if __name__=='__main__':execute()
