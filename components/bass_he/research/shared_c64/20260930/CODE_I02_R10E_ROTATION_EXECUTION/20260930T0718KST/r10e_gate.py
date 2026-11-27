"""Fresh, fixed R10E rotation convergence and independent ODE audit."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np
from scipy.integrate import solve_ivp

from arseny_reimpl.cross_section import projectile_velocity_au
from arseny_reimpl.rotational import epsilon_rotational, molecular_x_basis, s_sigma_boundary
from bass_he.geometry import atomic_json
from bass_he.rotation import angular_operators
from coulomb_rotation import author_cutoff, coulomb_rotation_batch
from rotation_convergence import fixed_rhos


HERE = Path(__file__).resolve().parent
TABLE = HERE.parents[2] / '20260929/CODE_I02_R10C_EXACT_NODE_EXECUTION/20260929T1842KST/EXACT_NODE_TABLE.json'


def dop853_probability(N: int, l: int, E: float, rho: float, cut: float, *, rtol: float, atol: float):
    """Integrate the Eq.47 generator directly; no Magnus step formula is used."""
    v = projectile_velocity_au(E)
    a = 2.0 / (0.8 * 1836.153 * v * v)
    b = math.hypot(a, rho)
    dim = 2*l+1
    if a+b >= cut:
        return np.eye(l+1), {'success': True, 'nfev': 0, 'accepted_steps': 0, 'entered': False}
    phi_max = math.acos((a + rho*rho/cut)/b)
    xmax = rho*math.tan(phi_max)
    eps = epsilon_rotational(N, l)
    lx, ly, _ = angular_operators(l)
    lx2, ly2, cross = lx@lx, ly@ly, lx@ly+ly@lx

    def rhs(y, flat):
        x = xmax*y
        den = rho*rho+x*x
        radius = rho*rho/(-a+b*rho/math.sqrt(den))
        weight = (radius*radius/den)**2
        H = eps*xmax*weight/v*(x*x*lx2-x*rho*cross+rho*rho*ly2)
        return (-1j*H@flat.reshape(dim, dim)).ravel()

    sol = solve_ivp(rhs, (-1., 1.), np.eye(dim, dtype=complex).ravel(),
                    method='DOP853', rtol=rtol, atol=atol)
    if not sol.success:
        raise RuntimeError('DOP853 failed: '+sol.message)
    m = np.arange(-l,l+1)
    theta_in = math.pi/2+phi_max
    theta_out = math.pi/2-phi_max
    U = (np.exp(-1j*theta_out*m)[:,None] * sol.y[:,-1].reshape(dim,dim)
         * np.exp(1j*theta_in*m)[None,:])
    _, Vx = molecular_x_basis(l)
    Ps = np.abs(Vx.conj().T@U@Vx)**2
    C = (np.abs(m)[None,:] == np.arange(l+1)[:,None]).astype(float)
    Pabs = (C@Ps@C.T)/C.sum(1)[None,:]
    return Pabs, {'success': bool(sol.success), 'nfev': int(sol.nfev),
                  'accepted_steps': len(sol.t)-1, 'entered': True}


def run():
    gate_path = HERE/'GATE_PRECOMMITTED.json'
    gate = json.loads(gate_path.read_text())
    gate_sha = hashlib.sha256(gate_path.read_bytes()).hexdigest()
    nodes = fixed_rhos(TABLE)
    if [float(x).hex() for x in nodes] != gate['rho_hex']:
        raise ValueError('R10E_FIXED_NODE_IDENTITY_MISMATCH')
    records = []
    for combo in gate['combinations']:
        N,l,E,label = combo['N'],combo['l'],combo['energy_keV_u'],combo['cutoff']
        cut = s_sigma_boundary(l) if label == 'CPC' else author_cutoff(l)
        results = {}
        defects = []
        for steps in gate['steps']:
            result = coulomb_rotation_batch(N,l,np.full(105,E),nodes,steps=steps,R_cut=cut)
            U,P = result['U_z'],result['P_abs']
            unit = float(np.max(np.abs(U.conj().swapaxes(-2,-1)@U-np.eye(2*l+1))))
            stoch = float(np.max(np.abs(P.sum(axis=1)-1.)))
            defects.append({'steps':steps,'unitarity':unit,'stochasticity':stoch,
                            'entered_nodes':int(np.count_nonzero(result['entered']))})
            results[steps] = P
        d1 = np.max(np.abs(results[256]-results[512]),axis=(1,2))
        d2 = np.max(np.abs(results[512]-results[1024]),axis=(1,2))
        worst = sorted(range(105),key=lambda i:(-d2[i],float(nodes[i]).hex()))[0]
        p_obs = math.log2(float(d1[worst]/d2[worst])) if d2[worst]>0 and d1[worst]>0 else None
        auditor,meta = dop853_probability(N,l,E,float(nodes[worst]),cut,
                         rtol=gate['auditor']['rtol'],atol=gate['auditor']['atol'])
        audit_diff = float(np.max(np.abs(results[1024][worst]-auditor)))
        rec = {**combo,'rho_of_max_d256_512_hex':float(nodes[int(np.argmax(d1))]).hex(),
               'rho_of_max_d512_1024_hex':float(nodes[worst]).hex(),
               'max_d256_512':float(np.max(d1)),'max_d512_1024':float(np.max(d2)),
               'd256_512_at_d512_1024_worst':float(d1[worst]),
               'd512_1024_at_worst':float(d2[worst]),'observed_order_at_worst':p_obs,
               'step_differences_decrease':bool(np.max(d2)<=np.max(d1)),
               'defects':defects,'auditor':{**meta,'max_probability_difference':audit_diff}}
        records.append(rec)
        atomic_json(HERE/'CONVERGENCE_PROGRESS.json',{'completed':len(records),'records':records,'gate_sha256':gate_sha})
        print('completed',len(records),N,l,E,label,'d2',rec['max_d512_1024'],'audit',audit_diff,flush=True)
    failed = []
    for rec in records:
        combo = {k:rec[k] for k in ('N','l','energy_keV_u','cutoff')}
        if rec['max_d512_1024']>gate['probability_successive_difference_limit'] or not rec['step_differences_decrease']:
            failed.append({'combo':combo,'reason':'STEP_CONVERGENCE'})
        if max(d['unitarity'] for d in rec['defects'])>gate['unitarity_limit'] or max(d['stochasticity'] for d in rec['defects'])>gate['stochasticity_limit']:
            failed.append({'combo':combo,'reason':'UNITARITY_OR_STOCHASTICITY'})
        if combo in gate['original_failed_cases'] and (rec['observed_order_at_worst'] is None or rec['observed_order_at_worst']<gate['minimum_observed_order']):
            failed.append({'combo':combo,'reason':'OBSERVED_ORDER'})
        if not rec['auditor']['success'] or rec['auditor']['max_probability_difference']>gate['auditor']['max_magnus1024_probability_difference']:
            failed.append({'combo':combo,'reason':'DOP853_AUDIT'})
    verdict='R10E_ROTATION_NUMERICS_PASS_EXTENDED_CONTRACT' if not failed else 'R10E_ROTATION_NUMERICS_UNRESOLVED'
    payload={'status':verdict,'gate_sha256':gate_sha,'table_sha256':gate['r10c_table_sha256'],
             'adapter_blob':gate['r10d_adapter_git_blob'],'node_count':105,'combination_count':12,
             'records':records,'failed':failed,'new_contour_solves':0}
    atomic_json(HERE/'EXTENDED_CONVERGENCE.json',payload)
    return payload


if __name__ == '__main__':
    print(run()['status'])
