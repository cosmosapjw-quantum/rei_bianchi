from pathlib import Path
import csv,json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def plot(root):
 root=Path(root);rows=list(csv.DictReader((root/'results/R38_SPECTRAL_R37_FIRST_EXIT_Q_1920.csv').open(newline='')))
 sel=[x for x in rows if x['Tgas_K']=='105' and x['n_Hplus_cm_minus3']=='1000.0' and x['spin_policy']=='eq6_7_spin_weighted']
 zvals=['OFF','0','10','30','100','300']
 fig,ax=plt.subplots(figsize=(8,4.7))
 for j in range(5):
  d={x['z_boundary']:float(x['conditional_Q_spectral_K']) for x in sel if int(x['initial_v0_J'])==j}
  assert len(d)==6
  ax.plot(range(6),[d[z] for z in zvals],'-o',label=f'Initial HD J={j}',markersize=3.7)
 ax.axhline(0,lw=.8,ls='--');ax.set_xticks(range(6),zvals)
 ax.set_xlabel('Externally prescribed blackbody boundary z_rad (OFF is no background)')
 ax.set_ylabel('Conditional chemical Q/k_B (K)')
 ax.set_title('Velilla native spectral BO channel Q × GL2022/EMAA first-exit chemistry')
 ax.legend(ncol=2,fontsize=8);fig.tight_layout();fig.savefig(root/'results/FIG01_Q_CONDITIONAL_105K.png',dpi=160);plt.close(fig)
 fig,ax=plt.subplots(figsize=(6.8,4.4))
 d=list(csv.DictReader((root/'results/BO_FD_SPECTRAL_CHANNEL_CROSSCHECK_190.csv').open(newline='')))
 v0=[x for x in d if x['HD_v']=='0'];v1=[x for x in d if x['HD_v']=='1']
 ax.plot(range(len(v0)),[float(x['spectral_minus_FD_K']) for x in v0],'.',ms=2,label='HD v0 channels')
 ax.plot(range(len(v1)),[float(x['spectral_minus_FD_K']) for x in v1],'.',ms=2,label='HD v1 channels')
 ax.axhline(0,ls='--',lw=.8);ax.set_xlabel('Channel index within vibrational class');ax.set_ylabel('Spectral minus FD signed ΔE / k_B (K)')
 ax.set_title('Independent radial BO discretizations: channel energy comparison')
 ax.legend();fig.tight_layout();fig.savefig(root/'results/FIG02_FD_SPECTRAL_CROSSCHECK.png',dpi=160);plt.close(fig)
if __name__=='__main__':plot(Path(__file__).resolve().parents[1])
