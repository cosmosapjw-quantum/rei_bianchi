"""Read saved ANALYSIS.json only; no kernel import or new numerical sampling."""
import datetime
import hashlib
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

UNIT=Path(__file__).resolve().parents[1]
source=UNIT/'results/ANALYSIS.json'
raw=source.read_bytes();data=json.loads(raw)
if not data.get('pass'):
    raise ValueError('Saved analysis must pass before figure production')
fig,axes=plt.subplots(1,2,figsize=(12.8,4.8),layout='constrained')
rows=data['illustration'];angles=[r['oriented_ejected_angle_degree'] for r in rows]
axes[0].plot(angles,[r['cba_tdcs_per_eV'] for r in rows],label='Direct CBA',color='#1565a7',linewidth=2)
axes[0].plot(angles,[r['plane_tdcs_per_eV'] for r in rows],label='Direct plane wave',color='#bc5a1b',linestyle='--',linewidth=1.8)
axes[0].set(xlabel='Oriented ejected angle (degree)',ylabel='TDCS [a0 squared / (eV sr squared)]',
            title='Fixed-centre labelled direct model\n250 eV incident, 5 eV ejected, 3 degree scattered')
axes[0].legend();axes[0].grid(alpha=.25)
colors={'parallel':'#1565a7','transverse':'#8a3b97'}
zeros=[]
for direction in ['parallel','transverse']:
    values=[r for r in data['tiny_transfer'] if r['direction']==direction]
    for key,label,style in [('stable_true_relative_error','stable Eq5','-'),('generic_true_relative_error_DIAGNOSTIC_ONLY','generic Eq2',':')]:
        positive=[r for r in values if r[key]>0]
        axes[1].loglog([r['t_binary64'] for r in positive],[r[key] for r in positive],style,
                       marker='o',markersize=3,color=colors[direction],label=direction+' '+label)
        zeros.extend({'direction':direction,'formula':label,'t':r['t_binary64']} for r in values if r[key]==0)
axes[1].axhline(data['acceptance']['matched_tiny_transfer_relative'],color='#555555',linestyle='--',label='stable tolerance')
axes[1].set(xlabel='Transfer parameter t (dimensionless)',ylabel='True relative error against mp80',
            title='Small-transfer conditioning fixtures\nGeneric cancellation is diagnostic only')
axes[1].legend(fontsize=8);axes[1].grid(alpha=.25,which='both')
fig.suptitle('Analytic direct CBA model and finite numerical controls — physical provider admission pending',fontsize=12)
folder=UNIT/'results/figures';folder.mkdir(exist_ok=True)
outputs=[]
for suffix in ['png','svg']:
    path=folder/('CBA_NORDSIECK.'+suffix)
    fig.savefig(path,dpi=160)
    b=path.read_bytes();outputs.append({'path':str(path.relative_to(UNIT)),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
plt.close(fig)
receipt={'saved_input':str(source.relative_to(UNIT)),'input_bytes':len(raw),'input_sha256':hashlib.sha256(raw).hexdigest(),
         'outputs':outputs,'new_scientific_sampling':0,'kernel_imports':0,'zero_relative_errors_omitted_from_log_axis':zeros,
         'visual_review':'PENDING_ACTUAL_ASTRA_INSPECTION','generated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
(folder/'PLOT_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt))
