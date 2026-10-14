#!/usr/bin/env python3
"""Bounded display only: 161 W samples, frozen GL16 nodes, no root search.

Scientific evidence is the separate first Decimal result and theory. This
binary64 plot does not add numerical validation or physical uncertainty credit.
"""
from pathlib import Path
import hashlib
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
SOURCE = ROOT / 'contributions/numerics/FINITE_WIDTH_FIRST.json'
raw = SOURCE.read_bytes()
assert hashlib.sha256(raw).hexdigest() == '3b2c71b7c2d650ac92e78e6eed041039ddd41f0d9e48cdfa95d9ebfec1448314'
r = json.loads(raw)
c = {k: float(v) for k, v in r['constants'].items() if isinstance(v, str)}
t = {k: float(v) for k, v in r['threshold_comparison'].items() if k.endswith('eV2')}
rule = r['quadrature_rules'][0]
assert rule['order'] == 16
nodes = np.array([float(x['x']) for x in rule['nodes_and_weights']])
weights = np.array([float(x['w']) for x in rule['nodes_and_weights']])
evaluations = 0

def kernel(e):
    global evaluations
    e = np.asarray(e)
    evaluations += e.size
    x = e/c['E0_eV']
    z = np.sqrt(x/c['ya'])
    p = c['P']
    sigma = c['sigma0']*c['area_cm2']*(x-1)**2*x**(p/2-5.5)*(1+z)**(-p)
    ell1 = 2*x/(x-1)+p/2-5.5-p*z/(2*(1+z))
    ell2 = -2*x/(x-1)**2-p*z/(4*(1+z)**2)
    s2 = ell1**2+ell2
    jx, jw = c['J_h2_x'], c['J_h2_w']
    return c['factor_q_N0_kappa_over_180']*sigma*((s2+3*ell1)*(jx+jw*(e-c['chi_eV']))+(2*ell1+4)*jw*e)

def average(center):
    center = np.asarray(center)
    return (kernel(center[..., None]+0.05*nodes)*weights).sum(axis=-1)/2

prior_path = HERE/'DISPLAY_RECEIPT.json'
prior = json.loads(prior_path.read_text()) if prior_path.exists() else {}
cache_path = HERE/'DISPLAY_DATA.json'
if cache_path.exists():
    cache = json.loads(cache_path.read_text())
    w, lower, upper, lower0, upper0 = [np.array(cache[key]) for key in
        ['W_eV2','finite_lower_s-4','finite_upper_s-4','PHYS26_lower_s-4','PHYS26_upper_s-4']]
else:
    w = np.linspace(c['W_photon_min_eV2'], c['W_photon_max_eV2'], 161)
    v = w-c['variance_offset_eV2']
    ka, kb = average(13.66), average(24.53)
    upper = (v*ka+4.34**2*average(18+v/4.34))/(4.34**2+v)
    lower = (6.53**2*average(18-v/6.53)+v*kb)/(6.53**2+v)
    ka0, kb0 = kernel(13.61), kernel(24.58)
    upper0 = (w*ka0+4.39**2*kernel(18+w/4.39))/(4.39**2+w)
    lower0 = (6.58**2*kernel(18-w/6.58)+w*kb0)/(6.58**2+w)

plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11,
                     'axes.spines.top': False, 'axes.spines.right': False,
                     'axes.labelsize': 12, 'axes.titlesize': 13,
                     'svg.fonttype': 'none'})
fig, (ax, bx) = plt.subplots(2, 1, figsize=(11.7, 9.0), gridspec_kw={'height_ratios': [1.32, 1]})
fig.subplots_adjust(left=.095, right=.97, bottom=.105, top=.87, hspace=.47)
fig.suptitle('Finite spectral width narrows the attainable initial response', fontsize=17, x=.095, ha='left', y=.975)
fig.text(.095, .94, r'PHYS27  |  mean 18 eV  |  uniform full width 0.10 eV  |  frozen kernel and numerical J', color='#475569', fontsize=11)
blue, orange, gray = '#1767A8', '#C75523', '#78808A'
ax.fill_between(w, lower0/1e-65, upper0/1e-65, color='#BBC1C9', alpha=.45, label='PHYS26: delta lines allowed')
ax.plot(w, lower0/1e-65, '--', color=gray, lw=1)
ax.plot(w, upper0/1e-65, '--', color=gray, lw=1)
ax.fill_between(w, lower/1e-65, upper/1e-65, color='#8CBCE0', alpha=.65, label='PHYS27: uniform-band mixtures')
ax.plot(w, lower/1e-65, color=orange, lw=2.0, label=r'Lower bound $A_{\delta,-}$')
ax.plot(w, upper/1e-65, color=blue, lw=2.0, label=r'Upper bound $A_{\delta,+}$')
ax.axhline(0, color='#1E293B', lw=1)
ws, wz = t['W_star_delta_eV2'], t['W_0_delta_eV2']
ax.plot([ws, wz], [0, 0], 'o', color='#1E293B', ms=4)
ax.annotate(r'$W_{*,\delta}=16.629459$', (ws, 0), xytext=(ws-6.2, 2.1),
            arrowprops={'arrowstyle': '-', 'color': '#64748B'}, fontsize=10)
ax.annotate(r'$W_{0,\delta}=23.300866$', (wz, 0), xytext=(wz-1.1, -4.4),
            arrowprops={'arrowstyle': '-', 'color': '#64748B'}, fontsize=10)
ax.plot([19.74,19.74], [-2.697002899664,1.448412710093], color='#364152', lw=1.3)
ax.set(xlim=(0,29), ylim=(-12.5,6.2), xlabel=r'Physical photon variance $W$ (eV$^2$)',
       ylabel=r'Initial response $A$ ($10^{-65}$ s$^{-4}$)')
ax.set_title('(a) Exact envelope formulas, shown with 161 display samples', loc='left', pad=13)
ax.grid(axis='y', color='#E2E8F0', lw=.7)
ax.set_axisbelow(True)
ax.legend(loc='lower right', frameon=False, fontsize=9.5)

case = next(x for x in r['physical_variance_cases'] if x['label']=='mixed_W19_74')
for family, color, label in [('upper',blue,r'Upper spectrum: $A=+1.44841271009\times10^{-65}$ s$^{-4}$'),
                              ('lower',orange,r'Lower spectrum: $A=-2.69700289966\times10^{-65}$ s$^{-4}$')]:
    for i, band in enumerate(case[family]['bands']):
        lo, hi = map(float, band['band_eV'])
        height = float(band['density_eV-1'])
        bx.add_patch(Rectangle((lo,0), hi-lo, height, facecolor=color, edgecolor=color,
                              alpha=.84, label=label if i==0 else None))
        center = (lo+hi)/2
        bx.annotate(f"{100*float(band['probability']):.2f}%", (center,height),
                    xytext=(0,7), textcoords='offset points', ha='center', color=color, fontsize=9.5)
bx.axvline(18, lw=1, color='#64748B', ls=':')
bx.text(18.14,5.7,'shared mean', color='#64748B', fontsize=10)
bx.set(xlim=(13.2,25.0), ylim=(0,8.8), xlabel='Photon energy E (eV)',
       ylabel=r'Photon-number density $p(E)$ (eV$^{-1}$)')
bx.set_xticks([13.61,15,18,21,24.58])
bx.set_xticklabels(['13.61','15','18','21','24.58'])
bx.set_title(r'(b) Opposite signs at the same $W=19.74$ eV$^2$: two explicit band spectra', loc='left', pad=13)
bx.grid(axis='y', color='#E2E8F0', lw=.7)
bx.set_axisbelow(True)
bx.legend(loc='upper center', bbox_to_anchor=(.63,.985), frameon=False, fontsize=10)
fig.text(.095,.035,'All band widths are drawn to scale. Root digits are numerical approximations; Physical HOLD remains.',
         color='#475569', fontsize=10)

out = HERE/'PHYS27_FINITE_WIDTH_ENVELOPE.png'
fig.savefig(out, dpi=180, facecolor='white')
plt.close(fig)
data = {'W_eV2':w.tolist(), 'finite_lower_s-4':lower.tolist(), 'finite_upper_s-4':upper.tolist(),
        'PHYS26_lower_s-4':lower0.tolist(), 'PHYS26_upper_s-4':upper0.tolist()}
(HERE/'DISPLAY_DATA.json').write_text(json.dumps(data, indent=2)+'\n')
receipt = {
    'classification':'DISPLAY_ONLY; no independent scientific validation',
    'raw_source_sha256': hashlib.sha256(raw).hexdigest(),
    'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    'W_display_samples':161, 'half_width_cases':1,
    'kernel_scalar_values_evaluated_this_render':evaluations,
    'cumulative_display_kernel_values':prior.get('cumulative_display_kernel_values', prior.get('kernel_scalar_values_evaluated',0))+evaluations,
    'render_invocations':prior.get('render_invocations',1 if prior else 0)+1,
    'prior_figure_sha256':prior.get('figure_sha256'),
    'layout_revision':'Spacing and legend placement after actual image inspection; cached values reused' if prior else None,
    'new_physical_root_searches':0, 'quadrature_node_solutions':0,
    'quadrature_nodes':'Float casts of frozen first-result GL16 nodes; no new node solve',
    'old_main_or_suite_invocations':0, 'new_science_main_invocations':0,
    'arithmetic':'NumPy binary64; matplotlib rendering',
    'environment':{'numpy':np.__version__,'matplotlib':matplotlib.__version__},
    'not_claimed':['Additional theorem validation','An interval or physical uncertainty band','New root evidence'],
    'figure_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),
    'figure_bytes':out.stat().st_size,
}
(HERE/'DISPLAY_RECEIPT.json').write_text(json.dumps(receipt, indent=2)+'\n')
print(json.dumps(receipt))
