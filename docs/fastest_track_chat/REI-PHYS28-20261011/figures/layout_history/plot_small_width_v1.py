#!/usr/bin/env python3
"""Display frozen PHYS28 arithmetic only; no kernel or root execution."""
from pathlib import Path
import json
import hashlib
from datetime import datetime, timezone
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
SOURCE = ROOT/'contributions/numerics/SMALL_WIDTH_FIRST.json'
EXPECTED = '563e52f9ed2dec6ef379a2e26ca3ec14d06679fef02c2bd0c7328e3022182c84'
source_bytes = SOURCE.read_bytes()
if hashlib.sha256(source_bytes).hexdigest() != EXPECTED:
    raise ValueError('Frozen first result changed')
raw = json.loads(source_bytes)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.titlesize':13,
                     'axes.labelsize':11,'axes.spines.top':False,'axes.spines.right':False,
                     'savefig.facecolor':'white','figure.facecolor':'white'})
fig = plt.figure(figsize=(13.2,8.0))
gs = GridSpec(2,2,figure=fig,height_ratios=[3.2,1.55],hspace=.43,wspace=.40)
colors=['#D39232','#248A96','#8B71B0','#234560']
labels=['Endpoint motion','Interior-center motion','Probability adjustment','Total sensitivity']
display = {'source_sha256':EXPECTED,'source_file':str(SOURCE.relative_to(ROOT)),
           'derived_display_only':True,'new_kernel_derivative_evaluations':0,
           'new_root_searches':0,'branches':{}}
for col,(branch,title,tag) in enumerate([
        ('upper_root','First existence of a nonnegative response',r'$c_*$'),
        ('lower_root','Every admissible response is nonnegative',r'$c_0$')]):
    item=raw['sensitivity']['jet'][branch]
    values=[float(item['coefficient_decomposition_eV'][k]) for k in
            ['endpoint_motion','moving_center_motion','weight_motion']]
    values.append(float(item['coefficient_c_eV']))
    ax=fig.add_subplot(gs[0,col])
    ax.barh(range(4),values,color=colors,height=.57)
    ax.invert_yaxis()
    ax.axvline(0,color='#7C8792',lw=.85)
    ax.axhline(2.5,color='#D2D8DD',lw=.8)
    ax.set_yticks(range(4),labels)
    ax.set_xlim(-10.9,16.1)
    ax.set_xticks([-10,-5,0,5,10,15])
    ax.grid(axis='x',color='#E5E8EB',lw=.6)
    ax.set_axisbelow(True)
    ax.set_xlabel('Contribution to '+tag+r'  [eV]')
    ax.set_title(title,pad=15,loc='left',fontweight='bold')
    for row,value in enumerate(values):
        ax.text(value+(.28 if value>=0 else -.28),row,f'{value:+.6f}',
                ha='left' if value>=0 else 'right',va='center',fontsize=10,
                fontweight='bold' if row==3 else 'normal',color='#213240')
    display['branches'][branch]={'c_contributions_eV':item['coefficient_decomposition_eV'],
                                'c_total_eV':item['coefficient_c_eV']}

table_ax=fig.add_subplot(gs[1,:]); table_ax.axis('off')
table_ax.set_title(r'One inherited-width comparison: $\delta=0.05$ eV (full band width 0.10 eV)',
                   loc='left',fontweight='bold',fontsize=13,pad=12)
rows=[]
for branch,name in [('upper_root',r'Existence threshold $W_*$'),('lower_root',r'Universal threshold $W_0$')]:
    c=raw['delta_005_comparison'][branch]
    rows.append([name,f"{float(c['linear_shift_at_delta_005_eV2']):+.10f}",
                 f"{float(c['actual_shift_at_delta_005_eV2']):+.10f}",
                 f"{float(c['residual_actual_minus_linear_eV2']):+.10f}",
                 f"{float(c['absolute_residual_relative_to_actual_shift_percent']):.6f}%"])
table=table_ax.table(cellText=rows,
                    colLabels=['Physical-variance threshold','Linear shift [eV²]','PHYS27 shift [eV²]',
                               'Actual − linear [eV²]','|Residual / shift|'],
                    colWidths=[.265,.195,.195,.195,.15],cellLoc='center',bbox=[0,.08,1,.78])
table.auto_set_font_size(False); table.set_fontsize(10)
for (row,col),cell in table.get_celld().items():
    cell.set_edgecolor('#DCE2E6');cell.set_linewidth(.6)
    if row==0:
        cell.set_facecolor('#EAF0F4');cell.set_text_props(fontweight='bold',color='#233C4D')
    else:cell.set_facecolor('#F8FAFB' if row==1 else 'white')
fig.suptitle('PHYS28  |  Why the variance thresholds move at first order',
             x=.08,y=.968,ha='left',fontsize=19,fontweight='bold',color='#19364A')
fig.text(.08,.917,r'Fixed photon variance $W$: symmetric band averaging and $V=W-\delta^2/3$ each contribute zero at first order.',
         fontsize=11,color='#4D5F6D')
fig.text(.08,.031,'Frozen source/J model · One-width residual is descriptive; no error bound or convergence-rate certificate · Physical HOLD',
         fontsize=9.1,color='#5F6B74')
fig.subplots_adjust(left=.16,right=.965,top=.835,bottom=.10)
target=HERE/'PHYS28_SMALL_WIDTH_SENSITIVITY.png'
fig.savefig(target,dpi=220)
plt.close(fig)
(HERE/'DISPLAY_DATA.json').write_text(json.dumps(display,ensure_ascii=False,indent=2)+'\n')
receipt={'task':'REI-PHYS28-20261011','utc':datetime.now(timezone.utc).isoformat(),
         'display_program':str(Path(__file__).relative_to(ROOT)),
         'source_sha256':EXPECTED,'matplotlib_version':matplotlib.__version__,
         'render_invocations':1,'kernel_derivative_evaluations':0,'physical_root_searches':0,
         'data_origin':'Selected frozen first-result fields; decimal-to-binary64 conversion only for display',
         'source_scientific_main_reexecution':False,
         'image':{'filename':target.name,'bytes':target.stat().st_size,
                  'sha256':hashlib.sha256(target.read_bytes()).hexdigest()},
         'visual_inspection':'Pending owner actual view; this script cannot self-certify layout'}
(HERE/'DISPLAY_RECEIPT.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(receipt,ensure_ascii=False))
