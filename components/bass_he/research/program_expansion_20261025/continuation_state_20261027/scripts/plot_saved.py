"""Render only already-saved numerical data; no scientific module imports."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1];src=ROOT/'evidence/validation/SAVED_PLOT_DATA.json';data=json.loads(src.read_text());out=ROOT/'evidence/plot';out.mkdir(parents=True,exist_ok=True)
fig,ax=plt.subplots(1,2,figsize=(11,4.5),layout='constrained');hd=data['hd'];ax[0].loglog([x['T_K'] for x in hd],[x['down_m3_s'] for x in hd],'o-',label='Native downward');ax[0].loglog([x['T_K'] for x in hd],[x['up_m3_s'] for x in hd],'s-',label='Derived upward (thermal reciprocity)');ax[0].plot([3005],[float(data['hd_3005_native_hold'])*1e-6],'x',label='3005 K native: held');ax[0].set(xlabel='Temperature (K)',ylabel='Coefficient (m³ s⁻¹)',title='HD + H⁺ selected level edge');ax[0].legend(fontsize=7)
for key,label in [('lih_old','Bennett 2003 historical'),('lih_corrected','Bennett 2008 corrected')]:
 rows=data[key];ax[1].loglog([float(x[0]) for x in rows],[float(x[1]) for x in rows],'o-',label=label)
ax[1].set(xlabel='Temperature (K)',ylabel='Printed coefficient (10⁻²⁰ cm³ s⁻¹)',title='LiH spontaneous association');ax[1].legend(fontsize=8);fig.savefig(out/'STATE04_SOURCE_COMPARISON.png',dpi=150);fig.savefig(out/'STATE04_SOURCE_COMPARISON.svg');(out/'PLOT_DATA.json').write_bytes(src.read_bytes())
