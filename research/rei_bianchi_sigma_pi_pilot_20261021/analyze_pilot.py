#!/usr/bin/env python3
"""Descriptive endpoint calculations only; no new ODE solves or error bound claim."""
import argparse,csv,json,math
from pathlib import Path
import numpy as np

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run',type=Path,required=True);a=ap.parse_args()
    rows=list(csv.DictReader((a.run/'endpoints.csv').open()))
    if len(rows)!=625:raise ValueError('625 endpoints required')
    def point(r):return float(r['eps_sigma'])*float(r['Sigma0']),float(r['eps_pi'])*float(r['Pi0'])
    d={point(r):r for r in rows}
    x=np.array([point(r) for r in rows]);y=np.array([math.sqrt(3)*float(r['s_over_H']) for r in rows])
    coeff,_,_,_=np.linalg.lstsq(x,y,rcond=None);pred=x@coeff;residual=y-pred;scale=float(np.max(abs(y)))
    min_sigma=min(float(r['Sigma0']) for r in rows if float(r['Sigma0'])>0);min_pi=min(float(r['Pi0']) for r in rows if float(r['Pi0'])>0)
    def signed_sigma(p):return math.sqrt(3)*float(d[p]['s_over_H'])
    slopes={'Sigma_axis_central':(signed_sigma((min_sigma,0.))-signed_sigma((-min_sigma,0.)))/(2*min_sigma),
            'Pi_axis_central':(signed_sigma((0.,min_pi))-signed_sigma((0.,-min_pi)))/(2*min_pi),
            'Sigma_axis_positive':signed_sigma((min_sigma,0.))/min_sigma,'Sigma_axis_negative':signed_sigma((-min_sigma,0.))/(-min_sigma),
            'Pi_axis_positive':signed_sigma((0.,min_pi))/min_pi,'Pi_axis_negative':signed_sigma((0.,-min_pi))/(-min_pi)}
    def compact(r):return {'case_id':r['id'],'signed_Sigma0':point(r)[0],'signed_Pi0':point(r)[1],'signed_Sigma_end':math.sqrt(3)*float(r['s_over_H']),**{k:float(r[k]) for k in ('Sigma','Pi','signed_Pi','b','E0','E2')}}
    nontrivial=[r for r in rows if point(r)!=(0.,0.)];minimum=min(nontrivial,key=lambda r:float(r['Sigma']))
    reversals=[(abs(float(r['Sigma'])-float(d[(-point(r)[0],-point(r)[1])]['Sigma'])),r,d[(-point(r)[0],-point(r)[1])]) for r in rows]
    maxreverse=max(reversals,key=lambda z:z[0])
    result={'scope':'Empirical descriptive calculations over 625 actual endpoint rows; no new solves, certified interpolation bound or general closure claim.',
      'least_squares_through_origin':{'formula':'signed_Sigma_end = A*(eps_sigma*Sigma0) + B*(eps_pi*Pi0)', 'A':float(coeff[0]),'B':float(coeff[1]),'max_abs_residual':float(np.max(abs(residual))),'rms_abs_residual':float(np.sqrt(np.mean(residual**2))),'global_max_abs_signed_Sigma_end':scale,'max_abs_residual_over_global_max':float(np.max(abs(residual))/scale),'rms_abs_residual_over_global_max':float(np.sqrt(np.mean(residual**2))/scale),'B_over_A_cancellation_Sigma0_over_Pi0':float(coeff[1]/coeff[0]),'cancellation_sign_condition':'opposite signed Sigma0 and Pi0'},
      'near_origin':{'minimum_nonzero_Sigma0':min_sigma,'minimum_nonzero_Pi0':min_pi,**slopes},
      'corners':[compact(r) for r in rows if int(r['sigma_index'])==12 and int(r['pi_index'])==12],
      'Pi_axis_largest':[compact(d[(0.,p)]) for p in (.001,-.001)],'Sigma_axis_largest':[compact(d[(s,0.)]) for s in (.004,-.004)],
      'minimum_nontrivial_grid_Sigma':compact(minimum),
      'maximum_simultaneous_sign_reversal_magnitude_difference':{'absolute':maxreverse[0],'over_global_max':maxreverse[0]/scale,'case':compact(maxreverse[1]),'reversed_case':compact(maxreverse[2])}}
    target=a.run/'analysis.json'
    if target.exists():raise FileExistsError(target)
    target.write_text(json.dumps(result,indent=2)+'\n')
    fit=result['least_squares_through_origin'];rev=result['maximum_simultaneous_sign_reversal_magnitude_difference']
    text=f'''# Descriptive endpoint analysis\n\nThese calculations use the existing 625 endpoint rows. They perform no ODE solves. The fit is empirical and supplies no certified interpolation bound.\n\nThe through-origin least-squares fit to signed final shear magnitude `sqrt(3)*s/H` is\n\n`S_end = {fit['A']:.12g} * signed_Sigma0 + {fit['B']:.12g} * signed_Pi0`.\n\nThe maximum absolute residual is {fit['max_abs_residual']:.12g} and the RMS residual is {fit['rms_abs_residual']:.12g}. Relative to the global maximum |S_end|={scale:.12g}, these are {fit['max_abs_residual_over_global_max']:.12g} and {fit['rms_abs_residual_over_global_max']:.12g}. The fitted opposite-sign cancellation ratio Sigma0/Pi0 is B/A={fit['B_over_A_cancellation_Sigma0_over_Pi0']:.12g}.\n\nCentered near-origin slopes on the smallest nonzero axis values are A={slopes['Sigma_axis_central']:.12g} and B={slopes['Pi_axis_central']:.12g}. One-sided slopes and all four corners plus largest axis controls are preserved in analysis.json.\n\nThe smallest nonzero-input grid endpoint Sigma is {float(minimum['Sigma']):.12g}, at signed Sigma0={point(minimum)[0]:.12g}, signed Pi0={point(minimum)[1]:.12g} ({minimum['id']}). This is a discrete-grid minimum, not a continuous cancellation solution.\n\nThe maximum simultaneous-sign-reversal magnitude difference is {rev['absolute']:.12g}, or {rev['over_global_max']:.12g} of the global maximum endpoint magnitude. The corresponding pair is recorded in analysis.json; the data do not establish exact simultaneous-sign symmetry.\n'''
    (a.run/'analysis.md').write_text(text);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
