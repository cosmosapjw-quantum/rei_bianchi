"""Explicit bridge to the separately compiled original Rust HE22 point evaluator.

No guessed rates, no fallback on subprocess failure, no cross-source cache.
Native computation is not available in this ChatGPT container.
"""
from __future__ import annotations
from pathlib import Path
import subprocess, math
import numpy as np
from he21_photo import Y_HE
from he22_contract import NativePoint

REQUIRED=('NH_CM3','NHE_CM3','FRACTION_DT','W_DT_EV_PER_H_S','TEMP_K',
          'PHOTO_EVENTS','THERMAL_MICRO','BINDING_MICRO','ESCAPE','CMB_TO_GAS',
          'PHOTO_INPUT','CI_EVENTS','RR_EVENTS','DR_EVENTS')

def parse_native_point(text: str, expected_nh: float) -> NativePoint:
    rows=text.strip().splitlines()
    if not rows or rows[0]!='HE22_NATIVE_POINT_V1':
        raise ValueError('HE22_NATIVE_SCHEMA_MISMATCH')
    fields={}
    for line in rows[1:]:
        cols=line.split('\t')
        if len(cols)<2 or cols[0] in fields:
            raise ValueError('HE22_NATIVE_DUPLICATE_OR_EMPTY_FIELD')
        fields[cols[0]]=np.array([float(v) for v in cols[1:]])
    if not set(REQUIRED).issubset(fields):
        raise ValueError('HE22_NATIVE_FIELDS_MISSING')
    if not all(np.isfinite(v).all() for v in fields.values()):
        raise ValueError('HE22_NATIVE_NONFINITE')
    scalar=('NH_CM3','NHE_CM3','W_DT_EV_PER_H_S','TEMP_K','THERMAL_MICRO',
            'BINDING_MICRO','ESCAPE','CMB_TO_GAS','PHOTO_INPUT','DR_EVENTS')
    vector=('FRACTION_DT','PHOTO_EVENTS','CI_EVENTS','RR_EVENTS')
    if any(len(fields[k])!=1 for k in scalar) or any(len(fields[k])!=3 for k in vector):
        raise ValueError('HE22_NATIVE_BAD_FIELD_SHAPE')
    nh=fields['NH_CM3'][0]; nhe=fields['NHE_CM3'][0]
    if not (nh>0 and nhe>0 and expected_nh>0):
        raise ValueError('HE22_NATIVE_DENSITY_DOMAIN')
    if abs(nh/expected_nh-1)>1e-9 or abs(nhe/nh/Y_HE-1)>1e-9:
        raise AssertionError('HE22_NATIVE_DENSITY_OR_HELIUM_SOURCE_MISMATCH')
    if fields['TEMP_K'][0]<=0:
        raise ValueError('HE22_NATIVE_NEGATIVE_TEMPERATURE')
    f=fields
    return NativePoint(f['FRACTION_DT'],float(f['W_DT_EV_PER_H_S'][0]),
        float(f['TEMP_K'][0]),f['PHOTO_EVENTS'],
        float(f['THERMAL_MICRO'][0]),float(f['BINDING_MICRO'][0]),
        float(f['ESCAPE'][0]),float(f['CMB_TO_GAS'][0]),
        float(f['PHOTO_INPUT'][0]))


class NativeRustPoint:
    def __init__(self, executable: str|Path, scale_factor: float,
                 expected_nh: float, timeout_s: float=20.):
        self.exe=Path(executable)
        if not self.exe.is_file(): raise FileNotFoundError(self.exe)
        if not math.isfinite(scale_factor) or not 1/21 <= scale_factor <= 1/5:
            raise ValueError('HE22_NATIVE_SCALE_DOMAIN')
        self.a=scale_factor
        self.nh=expected_nh
        self.timeout_s=timeout_s
        self.calls=0
    def __call__(self,gas,gamma,power):
        g=np.asarray(gas,dtype=float)
        gr=np.asarray(gamma,dtype=float)
        ph=np.asarray(power,dtype=float)
        if g.shape!=(4,) or gr.shape!=(3,) or ph.shape!=(3,) or (
            not np.isfinite(g).all() or not np.isfinite(gr).all() or
            not np.isfinite(ph).all() or (gr<0).any() or (ph<0).any()):
            raise ValueError('HE22_NATIVE_CLIENT_INPUT')
        argv=[str(self.exe),*[format(float(v),'.17e')
              for v in (self.a,*g,*gr,*ph)]]
        p=subprocess.run(argv,capture_output=True,text=True,timeout=self.timeout_s,check=False)
        self.calls+=1
        if p.returncode:
            raise RuntimeError('HE22_NATIVE_RUST_ERROR: '+p.stderr.strip()[:300])
        return parse_native_point(p.stdout,self.nh)
