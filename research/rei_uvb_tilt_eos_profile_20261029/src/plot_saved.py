"""Draw saved input/profile results only; no new science execution."""
import os,time,resource,json,math
from pathlib import Path
os.environ.setdefault('MPLBACKEND','Agg')
import matplotlib.pyplot as plt
P=Path(__file__).resolve().parents[1]
r=json.loads((P/'results/PRIMARY.json').read_text())
a,b,c=r['Q2_quadratic_coefficients']; th=[-1+2*i/300 for i in range(301)]
q2=[a+b*t+c*t*t for t in th]
# Amplitude-only Q(theta) at its fixed source points is quadratic too; reconstruct coefficients without replay of the observations.
pm=r['theta_minus']['Q0'];p0=r['theta0']['Q0'];pp=r['theta_plus']['Q0'];A=(pm+pp-2*p0)/2;B=(pp-pm)/2
qa=[p0+B*t+A*t*t for t in th]
fig,ax=plt.subplots(figsize=(8.6,4.8))
ax.plot(th,qa,label='Amplitude only: beta + bounded EOS')
ax.plot(th,q2,label='Amplitude + redshift tilt + bounded EOS')
ax.scatter([1],[r['best_profile']['Q2']],s=40,zorder=3)
ax.set_xlabel(r'BB13 EOS shift $\theta=(\gamma_{\rm TDR}-1.4)/0.2$')
ax.set_ylabel(r'Conditional statistical residual $\chi^2$')
ax.set_title('Fixed full covariance and Puchwein template: EOS nuisance profile')
ax.set_xlim(-1,1);ax.grid(alpha=.2);ax.legend(loc='upper right')
ax.text(.01,.015,'Same 7 observations; no Jeans covariance or physical posterior',transform=ax.transAxes,fontsize=9)
fig.tight_layout();fig.savefig(P/'figures/Q_VS_EOS.png',dpi=155);fig.savefig(P/'figures/Q_VS_EOS.svg');plt.close(fig)
fig,ax=plt.subplots(figsize=(8.6,4.8));kv=[r['kappa_theta0']+t*r['kappa_dtheta'] for t in th]
ax.plot(th,kv,label=r'Conditional $\hat\kappa(\theta)$')
ax.axhline(0,linestyle=':',linewidth=1)
ax.fill_between(th,[k-r['conditional_sigma_kappa'] for k in kv],[k+r['conditional_sigma_kappa'] for k in kv],alpha=.18,label=r'Fixed-$\theta$ statistical $1\sigma$ (not marginal)')
ax.set_xlabel(r'BB13 EOS shift $\theta$');ax.set_ylabel('kappa [dex per unit redshift]')
ax.set_xlim(-1,1);ax.set_title('EOS-versus-UVB redshift-slope covariance');ax.grid(alpha=.2);ax.legend(loc='upper right')
ax.text(.01,.015,'Conditional model only; full source and systematic uncertainty unknown',transform=ax.transAxes,fontsize=9)
fig.tight_layout();fig.savefig(P/'figures/KAPPA_VS_EOS.png',dpi=155);fig.savefig(P/'figures/KAPPA_VS_EOS.svg');plt.close(fig)
print(json.dumps({'figures':[str(p.relative_to(P)) for p in (P/'figures').iterdir()],'profile_source':'results/PRIMARY.json'},indent=2))
