#!/usr/bin/env python3
"""Reproduce original BASS21 -> 17 Li6 source-only F/J diagnostics; no IVP."""
import argparse, hashlib, importlib, json, sys, tempfile, zipfile
from pathlib import Path
import numpy as np
ARCHIVE_SHA='df871a18f297da15d05a5dadbad55e2aa29571217ad9136d9c4826921d1a11db'
TRAJECTORY_SHA='37d1bab173e81449cf474b21a678077edd0150cf0b2cb386d014764580678086'
U=np.r_[np.arange(13),np.arange(17,21)]
V=np.arange(13,17)
def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main(path):
    if sha(path)!=ARCHIVE_SHA:raise ValueError('PR278_SOURCE_SHA_MISMATCH')
    with tempfile.TemporaryDirectory() as td:
        root=Path(td)
        with zipfile.ZipFile(path) as z:
            if z.testzip() is not None:raise ValueError('ZIP_CRC')
            if any(x.startswith('/') or '..' in Path(x).parts for x in z.namelist()):raise ValueError('ZIP_PATH')
            z.extractall(root)
        if sha(root/'trajectory.npz')!=TRAJECTORY_SHA:raise ValueError('TRAJECTORY_SHA')
        sys.path.insert(0,str(root/'code'))
        src=importlib.import_module('native_full_rate')
        src.source_manifest_check()
        net=src.new_native_network()
        with np.load(root/'trajectory.npz',allow_pickle=False) as saved:
            Y=saved['Y'].copy();zs=saved['z'].copy()
            diag={name:saved['diagnostics'][:,i].copy() for i,name in enumerate(saved['diagnostic_names'])}
        assert Y.shape==(193,21) and len(U)==17 and len(V)==4
        assert [net.names[i] for i in V]==['Li6I','Li6II','Li6III','Li6IV']
        mx={'max_li6_electron_fraction':0.0,'max_delta_F17_baryon_inv_s':0.0,'max_delta_J17_s_inv':0.0,'max_J_UV_s_inv':0.0,'max_same_U_two_Li6_lift_baryon_inv_s':0.0}
        for k in range(193):
            y=Y[k];u=y[U];v=y[V];n=float(diag['nb_m3'][k])
            T=float(diag['T_K'][k]);uv=float(diag['uv_scale'][k]);rate=net.rates(T,uv)
            A=rate['G0']+rate['D'];B=rate['Gne'];bu=B[np.ix_(U,U)]
            if np.any(A[np.ix_(U,V)]) or np.any(B[np.ix_(U,V)]) or np.any(A[np.ix_(V,U)]) or np.any(B[np.ix_(V,U)]):raise AssertionError('DIRECT_LI6_BLOCK')
            res=net.evaluate(y,T,uv,n);f=res['dY_dt'];J=res['jac'];w=bu@u
            electron_v=float(net.q[V]@v)
            cross=n*np.outer(w,net.q[V]);native_cross=J[np.ix_(U,V)]
            np.testing.assert_allclose(native_cross,cross,rtol=1e-14,atol=0.0)
            np.testing.assert_allclose(f,(A+res['ne']*B)@y,rtol=1e-13,atol=1e-29)
            np.testing.assert_allclose(J,A+res['ne']*B+n*np.outer(B@y,net.q),rtol=1e-13,atol=1e-29)
            mx['max_li6_electron_fraction']=max(mx['max_li6_electron_fraction'],electron_v)
            mx['max_delta_F17_baryon_inv_s']=max(mx['max_delta_F17_baryon_inv_s'],float(np.max(np.abs(n*electron_v*w))))
            mx['max_delta_J17_s_inv']=max(mx['max_delta_J17_s_inv'],float(np.max(np.abs(n*electron_v*bu))))
            mx['max_J_UV_s_inv']=max(mx['max_J_UV_s_inv'],float(np.max(np.abs(cross))))
            mx['max_same_U_two_Li6_lift_baryon_inv_s']=max(mx['max_same_U_two_Li6_lift_baryon_inv_s'],float(np.max(np.abs(3*n*np.sum(v)*w))))
        print(json.dumps({'points':193,'native':'BASS21','retained':17,'omitted_Li6':4,'new_ivp':0,'not_full_REI17':True,**mx},indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('archive',type=Path)
    main(p.parse_args().archive)
