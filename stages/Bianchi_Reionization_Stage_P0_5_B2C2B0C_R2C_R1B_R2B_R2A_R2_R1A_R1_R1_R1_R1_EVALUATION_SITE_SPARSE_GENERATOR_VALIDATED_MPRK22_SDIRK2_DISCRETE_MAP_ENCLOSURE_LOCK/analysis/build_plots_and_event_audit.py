#!/usr/bin/env python3
from __future__ import annotations
import json, math
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

HERE=Path(__file__).resolve().parent;STAGE=HERE.parent;REPO=STAGE.parents[1]
local=json.loads((STAGE/'data/LOCAL_IMPLICIT_AUDIT.json').read_text())
witness=json.loads((STAGE/'data/STAGEWISE_WITNESS_REPLAY.json').read_text())
r1a=next(REPO.glob('stages/*R2_R1A_FOUR_CORNER*'))
r1a_results=json.loads((r1a/'results.json').read_text())
npz=np.load(r1a/'data/lane_workers/local_neutral_hazard_primary.npz')

# Pointwise distance of the inherited strict-corner temperature envelope to the
# Hummer-Seaton source-table topology surfaces.  This is an auditor only: it is
# not a continuous-family event certificate.
lo=np.asarray(npz['log_T_lower'],dtype=float);hi=np.asarray(npz['log_T_upper'],dtype=float)
knots=np.log(10.0**(4.0+0.25*np.arange(5,dtype=float)))
dists=[]
for knot in knots:
    d=np.where((lo<=knot)&(knot<=hi),0.0,np.minimum(np.abs(lo-knot),np.abs(hi-knot)))
    dists.append(d)
distance=np.min(np.stack(dists),axis=0)
auditor={
 'classification':'INHERITED_STRICT_CORNER_TABLE_EVENT_DISTANCE_AUDITOR',
 'load_bearing_continuous_certificate':False,
 'node_count':int(distance.size),
 'minimum_log_temperature_distance':float(np.min(distance)),
 'p01_log_temperature_distance':float(np.quantile(distance,0.01)),
 'median_log_temperature_distance':float(np.median(distance)),
 'zero_distance_count':int(np.count_nonzero(distance==0.0)),
 'knots_log_temperature':knots.tolist(),
 'claim_boundary':'Distances cover the inherited strict-corner endpoint envelope only; the unclosed four-site nonlinear remainder could alter event reachability.',
}
(STAGE/'data/TABLE_EVENT_DISTANCE_AUDITOR.json').write_text(json.dumps(auditor,indent=2,sort_keys=True)+'\n')

# Plot 1: local implicit contraction margins.
row=local['rows'][0]
labels=['MPRK1 H','MPRK1 He','MPRK2 H','MPRK2 He','SDIRK stage','SDIRK final']
values=[row['stage1_H']['max_row_sum_bound'],row['stage1_He']['max_row_sum_bound'],
        row['stage2_H']['max_row_sum_bound'],row['stage2_He']['max_row_sum_bound'],
        row['thermal']['stage_max_contraction_bound'],row['thermal']['final_max_contraction_bound']]
fig,ax=plt.subplots(figsize=(8.0,4.8))
ax.bar(labels,values)
ax.axhline(1.0,linestyle='--',label='Krawczyk gate')
ax.set_yscale('log');ax.set_ylabel('maximum contraction / row-sum bound')
ax.set_title('Frozen-state local implicit certificate margins')
ax.tick_params(axis='x',rotation=25);ax.legend();fig.tight_layout()
fig.savefig(STAGE/'plots/local_implicit_certificate_margins.png',dpi=200)
plt.close(fig)

# Plot 2: Krawczyk image radius relative to the chosen scalar tube.
labels2=['SDIRK stage','SDIRK final']
ratios=[row['thermal']['stage_max_krawczyk_radius_ratio'],row['thermal']['final_max_krawczyk_radius_ratio']]
fig,ax=plt.subplots(figsize=(6.4,4.6))
ax.bar(labels2,ratios)
ax.axhline(1.0,linestyle='--',label='strict inclusion gate')
ax.set_yscale('log');ax.set_ylabel('max Krawczyk image radius / tube radius')
ax.set_title('Scalar thermal-root Krawczyk inclusion')
ax.legend();fig.tight_layout()
fig.savefig(STAGE/'plots/thermal_root_krawczyk_inclusion.png',dpi=200)
plt.close(fig)

# Plot 3: the fresh stagewise witness escape from the inherited static hull.
wr=witness['rows'][0]
coords=['x_HII','x_HeII','x_HeIII','log T']
frac=wr['maximum_outside_fraction_by_coordinate']
fig,ax=plt.subplots(figsize=(7.0,4.6))
ax.bar(coords,frac)
ax.axhline(0.0,linestyle='--')
ax.set_ylabel('outside distance / inherited static width')
ax.set_title('Admissible stagewise schedule versus static-corner hull')
fig.tight_layout()
fig.savefig(STAGE/'plots/stagewise_witness_static_hull_escape.png',dpi=200)
plt.close(fig)

# Plot 4: inherited observable widths relative to the public uncertainty gate.
widths=r1a_results['overall_widths'];gate=float(r1a_results['uncertainty_gate'])
order=['x_HII','x_HeII','x_HeIII','log_T']
relative=[float(widths[k])/gate for k in order]
fig,ax=plt.subplots(figsize=(7.0,4.6))
ax.bar(order,relative)
ax.axhline(1.0,linestyle='--',label='public-width gate')
ax.set_yscale('log');ax.set_ylabel('inherited strict-corner width / 2e-3')
ax.set_title('Numerically narrow corners are not a continuous-family proof')
ax.legend();fig.tight_layout()
fig.savefig(STAGE/'plots/inherited_widths_vs_public_gate.png',dpi=200)
plt.close(fig)

# Plot 5: event-distance distribution for the inherited endpoint envelope.
fig,ax=plt.subplots(figsize=(7.2,4.6))
ax.hist(distance,bins=80)
ax.set_yscale('log');ax.set_xlabel('distance to nearest Hummer-Seaton knot in log T')
ax.set_ylabel('node count');ax.set_title('Inherited strict-corner table-event distance (auditor)')
fig.tight_layout()
fig.savefig(STAGE/'plots/inherited_table_event_distance.png',dpi=200)
plt.close(fig)

print(json.dumps(auditor,indent=2))
