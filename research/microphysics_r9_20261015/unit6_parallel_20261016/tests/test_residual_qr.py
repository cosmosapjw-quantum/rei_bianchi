"""Bounded, independent checks from the frozen lane-A contract."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("residual_qr", ROOT/"code/residual_qr.py")
qr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(qr)
OBSERVATIONS = []
SEED = 20261016


def hermitian_fixture(N=19, m=5, complex_case=False, nonorthogonal=False):
    rng = np.random.default_rng(SEED)
    M = rng.normal(size=(N, N))
    Q = rng.normal(size=(N, m))
    if complex_case:
        M = M+1j*rng.normal(size=(N, N))
        Q = Q+1j*rng.normal(size=(N, m))
    K = (M+M.conj().T)/2
    V = np.linalg.qr(Q, mode="reduced")[0]
    u = V[:, 0].copy()
    if nonorthogonal:
        V = V @ (np.diag(np.linspace(.8, 1.3, m))+.07*np.ones((m, m)))
        u = u+.03*Q[:, -1]
    return K, V, K@V, u


class ResidualTests(unittest.TestCase):
    def compare(self, name, K, V, KV, u, block_rows, grid=None, etas=None, physical=True):
        grid = np.array([-2., .17, 2., 8.]) if grid is None else np.asarray(grid)
        etas = np.array([.05, .2, 1.]) if etas is None else np.asarray(etas)
        W = 1.7
        output = qr.residual_diagnostic_qr(V, KV, u, W, grid, etas, block_rows, 3)
        C = V.conj().T@KV
        J = (C+C.conj().T)/2
        e1 = np.eye(V.shape[1], dtype=J.dtype)[:, 0]
        d, E = u-V[:, 0], KV-V@J
        delta_row = u.conj()@V-e1.conj()
        norm_u = np.linalg.norm(u)
        norm_error = scaled_norm_error = bound_error = scalar_error = dense_error = 0.
        min_bound_margin = np.inf
        points = []
        for i, eta in enumerate(etas):
            for k, omega in enumerate(grid):
                z = omega+1j*eta
                t = np.linalg.solve(z*np.eye(J.shape[0])-J, e1)
                direct_norm = np.linalg.norm(d+E@t)
                delta = abs(delta_row@t)
                direct_bound = norm_u*direct_norm/eta+delta
                alpha = np.linalg.norm(d)+np.linalg.norm(E)*np.linalg.norm(t)
                rho = norm_u+np.linalg.norm(V[:, 0])+(np.linalg.norm(KV)+np.linalg.norm(V)*np.linalg.norm(J, 2))*np.linalg.norm(t)
                slack = 5e-12*max(1., alpha)+50*np.finfo(float).eps*max(1., rho)
                nerr = abs(output["residual_norm"][i, k]-direct_norm)
                berr = abs(output["scalar_bound"][i, k]-direct_bound)
                serr = abs(output["scalar_resolvent"][i, k]-t[0])
                self.assertLessEqual(nerr, slack, (name, block_rows, z, nerr, slack))
                self.assertLessEqual(berr, norm_u*slack/eta+1e-11*max(1., abs(direct_bound)))
                self.assertLessEqual(serr, 1e-11*max(1., abs(t[0])))
                self.assertLessEqual(abs(output["coordinate_delta"][i, k]-delta), 1e-11*max(1., delta))
                self.assertAlmostEqual(output["density_bound"][i, k], W*output["scalar_bound"][i, k]/np.pi)
                norm_error = max(norm_error, float(nerr))
                scaled_norm_error = max(scaled_norm_error, float(nerr/slack))
                bound_error, scalar_error = max(bound_error, float(berr)), max(scalar_error, float(serr))
                if physical:
                    full = u.conj()@np.linalg.solve(z*np.eye(K.shape[0])-K, u)
                    error = abs(full-output["scalar_resolvent"][i, k])
                    allowance = output["scalar_bound"][i, k]+1e-10*max(1., abs(full))+norm_u*slack/eta
                    self.assertLessEqual(error, allowance, (name, z, error, allowance))
                    dense_error = max(dense_error, float(error))
                    min_bound_margin = min(min_bound_margin, float(allowance-error))
                    points.append({"omega": float(omega), "eta": float(eta), "full_scalar": [float(full.real), float(full.imag)],
                                   "physical_scalar_error": float(error), "B": float(output["scalar_bound"][i,k]),
                                   "rn_direct": float(direct_norm), "rn_qr": float(output["residual_norm"][i,k]), "norm_slack": float(slack)})
        self.assertLessEqual(output["summary"]["max_scaled_solve_defect"], 1e-11)
        OBSERVATIONS.append({"name": name, "seed": SEED, "N": V.shape[0], "m": V.shape[1], "dtype": str(V.dtype),
                             "block_rows": block_rows, "physical_bound_tested": physical,
                             "max_abs_norm_discrepancy": norm_error, "max_scaled_norm_discrepancy": scaled_norm_error,
                             "max_abs_bound_discrepancy": bound_error, "max_abs_scalar_discrepancy": scalar_error,
                             "max_dense_scalar_error": dense_error if physical else None,
                             "min_physical_bound_slack_margin": min_bound_margin if physical else None,
                             "summary": output["summary"], "dense_points": points})
        return output

    def test_exact_real_complex_and_nonorthogonal(self):
        cases = [
            ("exact_real", np.array([[2.,1.],[1.,3.]]), np.array([1.,0.]), np.array([1.,0.]), 2., 1., 0., 1., (1-3j)/5, 1/np.sqrt(5)),
            ("exact_complex", np.diag([1.,3.]), np.array([1.,1j])/np.sqrt(2), np.array([1.,1j])/np.sqrt(2), 2., 1., 0., 1., -.5j, .5),
            ("exact_nonorthogonal", np.diag([2.,3.]), np.array([2.,0.]), np.array([1.,0.]), 8., np.sqrt(145), 1., np.sqrt(145)+1, 1/(6+1j), None),
        ]
        for name, K, v, u, omega, rn, delta, B, full, scalar_error in cases:
            V = v[:, None]
            out = self.compare(name, K, V, K@V, u, 1, [omega], [1.])
            for key, exact in (("residual_norm",rn),("coordinate_delta",delta),("scalar_bound",B)):
                self.assertLessEqual(abs(out[key][0,0]-exact), 1e-12*max(1., abs(exact)))
            actual_full = u.conj()@np.linalg.solve((omega+1j)*np.eye(2)-K,u)
            self.assertLessEqual(abs(actual_full-full), 1e-12*max(1., abs(full)))
            if scalar_error is not None:
                self.assertLessEqual(abs(abs(actual_full-out["scalar_resolvent"][0,0])-scalar_error), 1e-12)

    def test_seeded_real_complex_and_block_shapes(self):
        for complex_case in (False, True):
            K,V,KV,u = hermitian_fixture(complex_case=complex_case)
            p = V.shape[1]+1
            for b in (1,p-1,p,8,100):
                self.compare(f"seeded_{'complex' if complex_case else 'real'}",K,V,KV,u,b)

    def test_nonorthogonal_with_initial_coordinate_defect(self):
        K,V,KV,u = hermitian_fixture(complex_case=True,nonorthogonal=True)
        out=self.compare("nonorthogonal_nonzero_d",K,V,KV,u,7)
        self.assertGreater(float(out["coordinate_delta"].max()),1e-4)

    def test_invariant_rank_deficient_short_and_near_invariant(self):
        K=np.diag(np.arange(1.,10.))
        V=np.eye(9)[:,:3]
        u=V[:,0].copy()
        out=self.compare("exact_invariant_zero_rank",K,V,K@V,u,2)
        self.assertLessEqual(float(out["residual_norm"].max()),1e-12)
        self.assertLessEqual(float(out["scalar_bound"].max()),1e-12)
        # N=m<p gives a reduced trapezoidal factor with fewer rows than columns.
        small=np.eye(2)
        short=qr.streamed_residual_factor(small,np.diag([1.,2.]),small[:,0],1)[1]
        self.assertEqual(short.shape,(2,3))
        K[0,5]=K[5,0]=1e-12
        self.compare("near_invariant_coupling_1e-12",K,V,K@V,u,4)
        A=np.column_stack((np.arange(7.),2*np.arange(7.),np.zeros(7)))
        x=np.array([2.,-1.,3.])
        R=qr.streamed_qr(A[i:i+2] for i in range(0,7,2))
        self.assertLessEqual(np.linalg.norm(R@x),1e-12)
        OBSERVATIONS.append({"name":"rank_deficient_standalone","R_shape":list(R.shape),"norm":float(np.linalg.norm(R@x))})

    def test_tiny_cancellation(self):
        A=np.array([[1.,1.],[0.,1e-10]])
        x=np.array([1.,-1.])
        R=qr.streamed_qr([A[:1],A[1:]])
        rn=float(np.linalg.norm(R@x))
        gram_raw=float(x@(A.T@A)@x)
        self.assertLessEqual(abs(rn-1e-10),1e-6*1e-10+1e-15)
        OBSERVATIONS.append({"name":"tiny_cancellation","rn_qr":rn,"gram_quadratic_raw":gram_raw,"direct_norm":float(np.linalg.norm(A@x))})

    def test_inconsistent_cache_is_algebra_only(self):
        K,V,KV,u=hermitian_fixture(complex_case=True)
        S=1j*np.eye(V.shape[1])*(1e-5/np.sqrt(V.shape[1]))
        bad=KV+V@S
        J,R,delta,norm_u,scales=qr.streamed_residual_factor(V,bad,u,6)
        self.assertGreater(scales["norm_C_minus_J_fro"],1e-6)
        self.compare("inconsistent_cache_algebra_only",K,V,bad,u,6,physical=False)
        OBSERVATIONS.append({"name":"inconsistent_cache_material_skew","norm_S_fro":float(np.linalg.norm(S)),
                             "norm_C_minus_J_fro":scales["norm_C_minus_J_fro"],"physical_bound_tested":False})

    def test_rejected_inputs(self):
        V=np.eye(3)[:,:2]
        u=V[:,0]
        bad_cases=[(V,V[:2],u),(V,V,u[:2]),(V[:,None],V,u),(np.ones((1,2)),np.ones((1,2)),np.ones(1)),
                   (V.astype(int),V,u),(V.astype(object),V,u),(V,np.full_like(V,np.nan),u),(V,V,np.full_like(u,np.inf))]
        for values in bad_cases:
            with self.assertRaises(ValueError):qr.streamed_residual_factor(*values)
        for W,grid,etas in [(-1.,[0.],[.1]),(np.inf,[0.],[.1]),(1j,[0.],[.1]),(1.,[],[.1]),
                            (1.,[np.nan],[.1]),(1.,[1j],[.1]),(1.,[0.],[0.]),(1.,[0.],[-.1]),(1.,[0.],[np.inf])]:
            with self.assertRaises(ValueError):qr.residual_diagnostic_qr(V,V,u,W,grid,etas)
        for b in (0,-1,1.5):
            with self.assertRaises(ValueError):qr.streamed_residual_factor(V,V,u,b)
        with self.assertRaises(ValueError):qr.streamed_qr([np.ones((2,2)),np.ones((2,3))])
        with self.assertRaises(ValueError):qr.streamed_qr([])
        with self.assertRaises(ValueError):qr.streamed_qr([np.ones((2,2),dtype=int)])
        with self.assertRaises(ValueError):qr.streamed_qr([np.array([[np.nan]])])
        OBSERVATIONS.append({"name":"rejected_inputs","cases":len(bad_cases)+9+3+4,"outcome":"all ValueError as specified"})

    def test_cli_synthetic(self):
        result_dir=ROOT/"results/laneA"
        result_dir.mkdir(parents=True,exist_ok=True)
        checkpoint=result_dir/"synthetic_cli_checkpoint.npz"
        out=result_dir/"cli_output"
        np.savez(checkpoint,V=np.eye(4)[:,:2],KV=np.diag([1.,2.,3.,4.])[:,:2],u=np.eye(4)[:,0],ignored=np.array([42]))
        command=[sys.executable,str(ROOT/"code/residual_qr.py"),"postprocess","--checkpoint",str(checkpoint),"--weight","1.25","--out",str(out),"--block-rows","1","--batch-points","13"]
        ran=subprocess.run(command,capture_output=True,text=True,timeout=20)
        (result_dir/"cli_stdout.txt").write_text(ran.stdout)
        (result_dir/"cli_stderr.txt").write_text(ran.stderr)
        self.assertEqual(ran.returncode,0,ran.stderr)
        with np.load(out/"residual.npz",allow_pickle=False) as arrays:
            self.assertEqual(arrays["scalar_bound"].shape,(3,2001))
            self.assertEqual(arrays["scalar_resolvent"].shape,(3,2001))
            np.testing.assert_array_equal(arrays["etas"],[.05,.1,.2])
            self.assertEqual(arrays["grid"][-1],20.)
        summary=json.loads((out/"residual_summary.json").read_text())
        self.assertEqual(summary["physical_H_actions"],0)
        self.assertEqual(summary["evaluation"],"streamed QR")
        rejected=subprocess.run(command,capture_output=True,text=True,timeout=20)
        self.assertNotEqual(rejected.returncode,0)
        (result_dir/"cli_no_overwrite_stderr.txt").write_text(rejected.stderr)
        OBSERVATIONS.append({"name":"CLI_synthetic","command":command,"returncode":ran.returncode,"shape":[3,2001],"repeat_output_returncode":rejected.returncode,"physical_H_actions":0})


if __name__=="__main__":
    unittest.main(verbosity=2)
