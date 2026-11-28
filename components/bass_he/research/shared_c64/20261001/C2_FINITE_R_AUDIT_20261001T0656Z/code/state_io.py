"""Exact archived prolate coefficients; reconstruction never solves an eigenproblem."""
import io,json
from pathlib import Path
import numpy as np
from spheroidal_tail import SpheroidalConfig,SpheroidalState,_Axis

def state_record(s):
    return {'R':s.R,'ZA':s.ZA,'ZB':s.ZB,'m':s.m,'config':s.metadata()['config'],
            'energy':s.energy,'separation_radial':s.separation_radial,
            'separation_angular':s.separation_angular,'normalization':s.normalization,
            'root_derivative':s.root_derivative,'residuals':s.residuals}

def pair_bytes(states):
    payload={}
    for key,s in zip(('g','b'),states):
        payload[key+'_record']=np.asarray(json.dumps(state_record(s),sort_keys=True,allow_nan=False))
        for attr in ('radial_coefficients','angular_coefficients'):
            payload[key+'_'+attr]=getattr(s,attr)
        payload[key+'_radial_edges']=s._radial.edges
        payload[key+'_angular_edges']=s._angular.edges
    stream=io.BytesIO();np.savez_compressed(stream,**payload);return stream.getvalue()

def load_pair(path):
    result=[]
    with np.load(Path(path),allow_pickle=False) as data:
        for key in ('g','b'):
            record=json.loads(str(data[key+'_record']));cfg=SpheroidalConfig(**record.pop('config'))
            m=record['m'];radial=_Axis(data[key+'_radial_edges'],cfg.degree,cfg.quadrature_order,m,True)
            angular=_Axis(data[key+'_angular_edges'],cfg.degree,cfg.quadrature_order,m,False)
            result.append(SpheroidalState(**record,config=cfg,
                radial_coefficients=data[key+'_radial_coefficients'],
                angular_coefficients=data[key+'_angular_coefficients'],_radial=radial,_angular=angular))
    return tuple(result)
