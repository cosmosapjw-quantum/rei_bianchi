from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent/'src'))
from nonthermal_d_birth import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
xs=[F(i,10) for i in range(0,31)]
r=[];kin=[];rest=[];ph=[];res=[]; wrong=[]
for x in xs:
    s=birth_source(x,source_class=REQUIRED_CLASS,photon_direction=(0,0,1))
    kin.append(float(s['fast_D_kinetic_J_m3_s']));rest.append(float(s['he4_rest_J_m3_s']+s['fast_D_rest_J_m3_s']));ph.append(float(s['photon_J_m3_s']));res.append(s['event_energy_residual_J_m3_s'])
    wrong.append(float(s['fast_D_kinetic_J_m3_s']+s['he4_rest_J_m3_s']+s['fast_D_rest_J_m3_s']-s['photon_J_m3_s']))
fig,ax=plt.subplots(figsize=(7,4.8))
ax.plot([float(x) for x in xs],kin,label='fast-D kinetic birth')
ax.plot([float(x) for x in xs],rest,label='nuclear rest-mass balance')
ax.plot([float(x) for x in xs],ph,label='photon energy source')
ax.plot([float(x) for x in xs],wrong,label='deliberate photon-sign mutation',linestyle=':')
ax.set(xlabel=r'Manufactured $R$ (events m$^{-3}$ s$^{-1}$)',ylabel=r'Energy source (J m$^{-3}$ s$^{-1}$)',title='Algebraic source ledger, NOT physical prediction')
ax.legend(fontsize=8)
fig.tight_layout(); fig.savefig(Path(__file__).parent/'results'/'manufactured_source_ledger.png',dpi=175)
assert all(x==0 for x in res)
assert wrong[-1]!=0
print('PLOT_CHECK PASS: exact true ledger residual 0 on 31 manufactured rates; sign mutation nonzero')
