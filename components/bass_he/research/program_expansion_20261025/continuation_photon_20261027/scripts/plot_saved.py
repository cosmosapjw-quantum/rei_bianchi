"""Plot saved PHOTON05 numerical results only; no science-module imports."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1];src=ROOT/'evidence/validation/SAVED_PLOT_DATA.json';data=json.loads(src.read_text());out=ROOT/'evidence/plot';out.mkdir(parents=True,exist_ok=True)
fig,ax=plt.subplots(1,2,figsize=(12,4.5),layout='constrained')
for energy in ('213.','258.','330.'):
 rows=[x for x in data['native'] if x['values']['EN']==energy];angles=[float(x['values']['ANG-CM']) for x in rows]
 for j,(key,style) in enumerate((('plus','o-'),('minus','s--'))):
  ax[0].plot(angles,[x['event'][key]['kinetic'] for x in rows],style,label=energy+' MeV '+key)
  ax[1].plot(angles,[x['same_momentum_NR_relative_excess'][j] for x in rows],style,label=energy+' MeV '+key)
ax[0].set(xlabel='CM angle (degrees)',ylabel='Daughter kinetic energy (MeV)',title='Native angles; explicit φ=0 plane');ax[1].set(xlabel='CM angle (degrees)',ylabel='(K_NR − K) / K',title='Same-momentum NR energy excess');ax[0].legend(fontsize=7,ncol=2);ax[1].legend(fontsize=7,ncol=2);fig.savefig(out/'PHOTON05_NATIVE_RECOIL.png',dpi=150);fig.savefig(out/'PHOTON05_NATIVE_RECOIL.svg');(out/'PLOT_DATA.json').write_bytes(src.read_bytes())
