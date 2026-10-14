#!/usr/bin/env python3
"""Plot actual local coefficient decompositions; no finite-time history shown."""
import argparse
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path,required=True);ap.add_argument('--output-dir',type=Path,required=True);a=ap.parse_args()
    stem='PHYS22_initial_response_decomposition'
    a.output_dir.mkdir(parents=True,exist_ok=True)
    for ext in ['png','pdf','json']:
        if (a.output_dir/(stem+'.'+ext)).exists():raise FileExistsError('Use fresh output files')
    data=json.loads(a.input.read_text())['results']['actual_shear_time_coefficients']
    tp=data['temperature_t3_parts_K_s3'];he=data['He_t4_parts']
    panels=[('Temperature: leading '+r'$t^3$'+' coefficient',['Thermal energy','Particle count','Total'],[float(tp['thermal_energy']),float(tp['particle_count']),float(data['temperature_t3_K_s3'])],1e-42,r'$10^{-42}\ {\rm K\,s^{-3}}$'),
            ('He II: leading '+r'$t^4$'+' coefficient',['Electron density','Temperature','Total'],[float(he['HeII']['electron_density']),float(he['HeII']['temperature']),float(he['HeII']['total_u4'])],1e-62,r'$10^{-62}\ {\rm s^{-4}}$'),
            ('He III: leading '+r'$t^4$'+' coefficient',['Electron density','Temperature','Total'],[float(he['HeIII']['electron_density']),float(he['HeIII']['temperature']),float(he['HeIII']['total_u4'])],1e-64,r'$10^{-64}\ {\rm s^{-4}}$')]
    plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False})
    fig,axes=plt.subplots(1,3,figsize=(13.5,4.8))
    for ax,(title,labels,vals,unit,ylab) in zip(axes,panels):
        vs=[x/unit for x in vals];colors=['#4f7794','#d28a48','#353d49']
        bars=ax.bar(range(3),vs,color=colors,width=.62)
        ax.axhline(0,color='#6f7780',lw=.8);ax.set_xticks(range(3),labels,rotation=17,ha='right')
        ax.set_title(title,fontsize=12,pad=14);ax.set_ylabel(ylab);ax.grid(axis='y',alpha=.2);ax.set_axisbelow(True)
        span=max(vs+[0])-min(vs+[0]);ax.set_ylim(min(vs+[0])-.27*span,max(vs+[0])+.25*span)
        for bar,v in zip(bars,vs):
            ax.text(bar.get_x()+bar.get_width()/2,v+(.05*span if v>=0 else -.05*span),f'{v:+.4f}',ha='center',va='bottom' if v>=0 else 'top',fontsize=10)
    fig.suptitle('PHYS22 | Initial scalar response to shear',fontsize=16,y=.99)
    fig.text(.5,.018,r'Coefficients of $[\epsilon^2]y(t)$; physical shear included. $E_b=13.7$ eV, $T_*=5\times10^4$ K. Local expansion, no finite-time solution.',ha='center',fontsize=10)
    fig.tight_layout(rect=(0,.08,1,.94))
    fig.savefig(a.output_dir/(stem+'.png'),dpi=170);fig.savefig(a.output_dir/(stem+'.pdf'))
    (a.output_dir/(stem+'.json')).write_text(json.dumps({'task':'PHYS22','scope':'Actual leading-time coefficient decomposition, not history or remainder certificate','epsilon_coefficient':'half second derivative','physical_shear_included':True,'panels':[{'title':p[0],'labels':p[1],'values':p[2],'display_unit_scale':p[3]} for p in panels]},indent=2)+'\n')
    print(json.dumps({'figure':stem,'panels':3,'finite_time_solution':False}))

if __name__=='__main__':main()
