#!/usr/bin/env python3
"""Source-conditional HD19 original-REI diagnostics, not REI observable plots."""
import csv, json, pathlib
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=pathlib.Path(__file__).resolve().parent/'results'
rows=list(csv.DictReader((R/'R48_REI_NODE_SUMMARY_5616.csv').open()))
T=np.array([float(r['T_K_lo'])/2+float(r['T_K_hi'])/2 for r in rows])
gap=np.array([float(r['ratio_gap_Hplus_over_H']) for r in rows]);tail=np.array([float(r['LTE_Q52_outside_Hplus19_mid']) for r in rows]);rmin=np.array([float(r['ratio_min_171_outer_lower']) for r in rows])
fig,ax=plt.subplots(figsize=(8,5));ax.scatter(T,np.log10(gap),s=4,alpha=.55);ax.set_xlabel('REI source gas temperature at accepted tick160 (K)');ax.set_ylabel(r'$\log_{10}(\lambda_{\rm gap,H^+}/\lambda_{\rm gap,H})$');ax.set_title('WU HD19 collision-only thermal relaxation: actual source-supported REI cells');ax.grid(alpha=.25);fig.tight_layout();fig.savefig(R/'R48_HD19_SPECTRAL_GAP_SOURCE.png',dpi=170);fig.savefig(R/'R48_HD19_SPECTRAL_GAP_SOURCE.svg');plt.close(fig)
fig,ax=plt.subplots(figsize=(8,5));ax.scatter(T,tail,s=4,alpha=.65);ax.set_xlabel('REI source gas temperature at accepted tick160 (K)');ax.set_ylabel('52-level LTE fraction outside H+ 19-level support');ax.set_title('EMAA original finite-52 LTE weight excluded from H+ collision coverage');ax.grid(alpha=.25);fig.tight_layout();fig.savefig(R/'R48_EMAA52_LTETAIL_OUTSIDE19.png',dpi=170);fig.savefig(R/'R48_EMAA52_LTETAIL_OUTSIDE19.svg');plt.close(fig)
fig,ax=plt.subplots(figsize=(8,5));ax.scatter(T,np.log10(rmin),s=4,alpha=.6);ax.set_xlabel('REI source gas temperature at accepted tick160 (K)');ax.set_ylabel('log10(min across 171 proton/H outer-bound ratio)');ax.set_title('Original REI xHII and EMAA H/H+ full 19-state source competition');ax.grid(alpha=.25);fig.tight_layout();fig.savefig(R/'R48_TRANSITION_MIN_RATIO_SOURCE.png',dpi=170);fig.savefig(R/'R48_TRANSITION_MIN_RATIO_SOURCE.svg');plt.close(fig)
print('R48 original-data plots',len(rows), 'rows, 3 PNG + 3 SVG')
