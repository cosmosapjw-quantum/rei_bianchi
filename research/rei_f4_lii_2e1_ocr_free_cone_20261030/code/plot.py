"""Plot original saved epoch source response and exact-in-model envelope vertices."""
import csv,pathlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
ROOT=pathlib.Path(__file__).resolve().parents[1]
with (ROOT/'results/CONE_EPOCH_193.csv').open() as f:rows=list(csv.DictReader(f))
z=np.array([float(r['z']) for r in rows]); r=lambda k:np.array([float(row[k]) for row in rows])
for metric,label,basename in [
 ('P2','Probability of two first photoabsorptions','CONE_P2_BOUNDS_193.png'),
 ('N','Expected first photoelectrons / pair','CONE_ELECTRON_BOUNDS_193.png')]:
 fig,ax=plt.subplots(figsize=(7,4.5))
 ax.fill_between(z,r('positive_'+metric+'_min'),r('positive_'+metric+'_max'),alpha=.15,label='21-knot positive cone')
 ax.fill_between(z,r('monotone_'+metric+'_min'),r('monotone_'+metric+'_max'),alpha=.3,label='21-knot monotone cone')
 ax.plot(z,r('PR284_'+metric),label='PR284 OCR-conditional witness',lw=1.5)
 ax.set(xlabel='Original BASS21 saved redshift z',ylabel=label,title='Spectrum ordinate-independent sharp-in-family bounds')
 ax.legend(loc='best',fontsize=8);fig.tight_layout();fig.savefig(ROOT/'results'/basename,dpi=170);plt.close(fig)
print('FIGURES=2')
