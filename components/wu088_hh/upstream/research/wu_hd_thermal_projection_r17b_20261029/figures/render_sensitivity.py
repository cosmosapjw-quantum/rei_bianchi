"""Source K at ONLY two printed T; rotational levels explicitly synthetic."""
import math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path

root=Path(__file__).resolve().parent
B=np.linspace(20,100,321)
fig,ax=plt.subplots(figsize=(7.2,4.4))
for T,K in [(205,1.21),(295,2.21)]:
    y=[]
    for theta in B:
        b=[(2*j+1)*math.exp(-theta*j*(j+1)/T) for j in range(9)]
        p=b[2]/sum(b)
        y.append(K/(p*(3/4)))
    ax.plot(B,y,label=f'{T} K, printed total K={K}')
ax.set_xlabel(r'Synthetic $\theta_{\rm rot}$ (K); $\Delta E_j/k_B=\theta_{\rm rot}j(j+1)$')
ax.set_ylabel('Conditional sharp cap on k(2→1) (printed rate units)')
ax.set_title('Illustrative sensitivity; NO HD level energies or source rows inferred')
ax.grid(alpha=.3);ax.legend();fig.tight_layout()
for ext in ('png','svg'):fig.savefig(root/f'synthetic_weight_sensitivity.{ext}',dpi=190)
plt.close(fig)
print('SYNTHETIC_PLOT_SAVED',root)
