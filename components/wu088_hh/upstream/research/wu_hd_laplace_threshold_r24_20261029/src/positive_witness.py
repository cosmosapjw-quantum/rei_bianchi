"""Constructive finite-Laplace-sample noninjectivity on POSITIVE DISCRETE measures.

This is not a native GL2022 scattering computation. Smooth positive bump
counterexamples follow by matrix continuity and coefficient compensation.
"""
from __future__ import annotations
import json
from pathlib import Path
import mpmath as mp


def build_witness(temperatures=(15,55,105,255,505,1005,1505,2005,2505,3005),dps=125):
    if len(temperatures)!=10 or len(set(temperatures))!=10:
        raise ValueError('exact ten distinct temperature measurements required')
    with mp.workdps(dps):
        kb=mp.mpf('1.380649e-23')/mp.mpf('1.602176634e-19')*1000
        beta=[1/(kb*mp.mpf(t)) for t in temperatures]
        centers=[mp.mpf(20+3*j) for j in range(10)]  # supported from 20 meV
        added=mp.mpf(12) # alternative has extra positive measure at 12 meV
        M=mp.matrix([[mp.exp(-b*x) for x in centers] for b in beta]);
        v=mp.matrix([mp.exp(-b*added) for b in beta])
        coeff=mp.lu_solve(M,-v)
        amplitude=mp.mpf('0.5')/max(abs(x) for x in coeff)
        alternative=[1+amplitude*c for c in coeff]
        if min(alternative)<=0 or amplitude<=0:
            raise AssertionError('invalid positive witness')
        lbase=[mp.fsum(M[i,j] for j in range(10)) for i in range(10)]
        lalt=[mp.fsum(M[i,j]*alternative[j] for j in range(10))+amplitude*v[i] for i in range(10)]
        err=max(abs(a-b) for a,b in zip(lbase,lalt))
        relerr=max(abs(a-b)/abs(a) for a,b in zip(lbase,lalt))
        return {
            'schema':'wu.r24.positive_discrete_laplace_nonunique_witness.v1',
            'scope':'synthetic positive energy-weighted spectral MEASURES, not GL2022 experimental cross sections',
            'temperature_nodes_K':[str(x) for x in temperatures],
            'first_onset_meV':'20', 'second_onset_meV':'12',
            'baseline_support_meV':[str(x) for x in centers],
            'baseline_weights':['1']*10,
            'alternative_weights':[mp.nstr(x,35) for x in alternative],
            'added_12meV_weight':mp.nstr(amplitude,35),
            'minimum_alternative_high_energy_weight':mp.nstr(min(alternative),35),
            'max_abs_Laplace_residual':mp.nstr(err,25),
            'max_rel_Laplace_residual':mp.nstr(relerr,25),
            'dps':dps,
            'negative_result':'Not a proof that the actual 10 GL2022 rates admit both supports; illustrates non-injectivity of the finite Laplace measurement operator',
            'canonical_DAG':'34/49_UNCHANGED','GL2022_PES_native_Q':None
        }


def main():
    import argparse
    a=argparse.ArgumentParser();a.add_argument('--out',type=Path,required=True);args=a.parse_args()
    r=build_witness();args.out.parent.mkdir(parents=True,exist_ok=True)
    with args.out.open('x',encoding='utf8') as f:
        json.dump(r,f,indent=2,ensure_ascii=False);f.write('\n')

if __name__=='__main__':main()
