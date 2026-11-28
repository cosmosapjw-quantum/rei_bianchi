#!/usr/bin/env python3
"""Plot native-PES derived data without inventing rates or observables."""
import csv
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent
D=ROOT/'results'
def read(fname):
    with (D/fname).open() as f:return list(csv.DictReader(f))
rows=read('NATIVE_PES_LEGENDRE_168.csv')
fig,ax=plt.subplots(figsize=(8,5))
for label in ('Hplus_HD','Dplus_H2'):
    r=[v for v in rows if v['arrangement']==label and v['r_index']=='1' and float(v['R_bohr'])>=12]
    ax.plot([float(x['R_bohr']) for x in r], [float(x['C4_iso_at_R_hartree_a0_4']) for x in r],marker='o',markersize=3,label=label)
ax.set(xlabel='Atom-diatom COM separation R (Bohr)', ylabel='-R⁴ <V-V_diatom> (Eh a0⁴)',title='Native Velilla PES: orientational mean long-range tail');ax.legend();fig.tight_layout();fig.savefig(D/'FIG01_C4_VS_R.png',dpi=180);fig.savefig(D/'FIG01_C4_VS_R.svg');plt.close(fig)
fig,ax=plt.subplots(figsize=(8,5))
for label in ('Hplus_HD','Dplus_H2'):
    r=[v for v in rows if v['arrangement']==label and v['r_index']=='1' and float(v['R_bohr'])>=10]
    ax.plot([float(x['R_bohr']) for x in r], [float(x['Legendre_a1_hartree'])*315775.024804 for x in r],marker='o',markersize=3,label=label)
ax.set(xlabel='COM separation R (Bohr)',ylabel='Legendre a₁ (K)',title='Odd multipole from COM anchoring: exact electronic-midpoint test');ax.legend();fig.tight_layout();fig.savefig(D/'FIG02_ODD_COM_MULTIPOLE.png',dpi=180);fig.savefig(D/'FIG02_ODD_COM_MULTIPOLE.svg');plt.close(fig)
rows=read('ISOTROPIC_C4_CENTRIFUGAL_24.csv')
fig,ax=plt.subplots(figsize=(8,5))
for label in ('Hplus_HD','Dplus_H2'):
    r=[v for v in rows if v['arrangement']==label]
    ax.plot([int(x['orbital_l']) for x in r],[float(x['barrier_K']) for x in r],marker='o',label=label)
ax.set(xlabel='Relative orbital angular momentum ℓ',ylabel='Isotropic -C₄/R⁴ centrifugal maximum (K)',title='Model-only barriers: no S matrix or reactive capture probability',yscale='log');ax.legend();fig.tight_layout();fig.savefig(D/'FIG03_C4_BARRIERS.png',dpi=180);fig.savefig(D/'FIG03_C4_BARRIERS.svg');plt.close(fig)
rows=read('PUBLISHED_THERMAL_ERRATUM_12.csv')
fig,ax=plt.subplots(figsize=(8,5))
Ts=[float(x['T_K']) for x in rows]
for col,label in [('original_2019_fit_cm3_s','2019 as published (superseded)'),('erratum_2021_corrected_total_fit_cm3_s','2021 corrected total'),('erratum_para_fit_cm3_s','2021 corrected para'),('erratum_ortho_fit_cm3_s','2021 corrected ortho')]:
    ax.plot(Ts,[float(x[col]) for x in rows],marker='o',markersize=3,label=label)
ax.set(xlabel='Temperature (K)',ylabel='Published analytic-fit k (cm³/s)',title='Lepers et al. 2021 erratum: nuclear-spin corrected literature fit',yscale='log');ax.legend();fig.tight_layout();fig.savefig(D/'FIG04_LITERATURE_ERRATUM.png',dpi=180);fig.savefig(D/'FIG04_LITERATURE_ERRATUM.svg');plt.close(fig)
print('plots generated: 4 PNG + 4 SVG')
