"""Exact synthetic theorem witnesses; never load scientific arrays."""
from fractions import Fraction as Q
import unittest
import t5_sharp_residual as t5
from t5_sharp_residual import (gram, matrix, interval, sharp, rectangular_disk,
                              k_disks, intersect, gap, raw_gap_tube, subtract)


class T5Tests(unittest.TestCase):
    def test_rectangle_corner_needs_euclidean_radius(self):
        disk=rectangular_disk(Q(-3),Q(3),Q(-4),Q(4))
        self.assertEqual(disk.center,(Q(0),Q(0)))
        self.assertEqual(disk.radius,Q(5));self.assertGreater(disk.radius,Q(4))

    def test_complex_gram_and_adjoint(self):
        a=[[(Q(1),Q(0)),(Q(0),Q(1))],[(Q(0),Q(1)),(Q(-1),Q(0))]]
        self.assertEqual(gram.gram2(a),(Q(2),(Q(0),Q(2)),Q(2)))
        self.assertEqual(gram.spectral_norm(a),interval(2,2))
        self.assertEqual(gram.spectral_norm(gram.adjoint(a)),interval(2,2))

    def test_frobenius_fails_valid_spectral_budget(self):
        a=Q(1,1000);budget=Q(1,800);raw=matrix([[a,0],[0,a]])
        disks=[[gram.ComplexDisk(z,Q(0)) for z in row] for row in matrix([[0,0],[0,0]])]
        result=sharp(raw,disks)
        self.assertEqual(result['interval'],interval(a,a));self.assertLess(result['interval'].hi,budget)
        self.assertGreater(2*a*a,budget*budget)
        self.assertGreater(gram.source_error_bound_disk(raw,disks),budget)

    def test_nonzero_disks_preserve_improvement(self):
        a=Q(1,1000);r=a/100;budget=Q(1,800)
        disks=[[gram.ComplexDisk((Q(0),Q(0)),r) for _ in range(2)] for _ in range(2)]
        result=sharp(matrix([[a,0],[0,a]]),disks)
        self.assertEqual(result['rho_upper'],2*r)
        self.assertEqual(result['interval'].hi,51*a/50)
        self.assertLess(result['interval'].hi,budget)
        self.assertGreater(gram.source_error_bound_disk(matrix([[a,0],[0,a]]),disks),budget)

    def test_refinement_does_not_remove_fixed_raw_error(self):
        a=Q(1,1000);previous=None
        for n in range(2,16):
            r=a/Q(2**n)
            disks=[[gram.ComplexDisk((Q(0),Q(0)),r) for _ in range(2)] for _ in range(2)]
            result=sharp(matrix([[a,0],[0,a]]),disks);i=result['interval']
            self.assertLessEqual(i.lo,a);self.assertGreaterEqual(i.hi,a)
            self.assertEqual(i.hi-a,2*r)
            if previous is not None:self.assertLess(i.hi-i.lo,previous)
            previous=i.hi-i.lo
        self.assertGreater(i.lo,0)

    def test_drifting_centers_contain_same_target(self):
        a=Q(1,1000)
        for n in (4,8,16):
            r=a/Q(2**n)
            centers=matrix([[r,0],[0,r]])
            disks=[[gram.ComplexDisk(z,r if i==j else Q(0)) for j,z in enumerate(row)] for i,row in enumerate(centers)]
            result=sharp(matrix([[a,0],[0,a]]),disks,precision=80)
            self.assertLessEqual(result['interval'].lo,a);self.assertGreaterEqual(result['interval'].hi,a)
            self.assertLessEqual(result['interval'].hi-result['interval'].lo,
                                 result['center_norm'].hi-result['center_norm'].lo+2*result['rho_upper'])

    def test_k_center_cancellation_and_stored_model_k(self):
        a=Q(1,1000);c0=matrix([[a,0],[0,a]]);r0=gram.adjoint(c0)
        zero=[[gram.ComplexDisk((Q(0),Q(0)),Q(0)) for _ in range(2)] for _ in range(2)]
        kr=gram.construct_k(c0,r0);kd=k_disks(zero,zero)
        k=sharp(kr,kd);c=sharp(c0,zero);r=sharp(r0,zero)
        self.assertEqual(k['interval'],interval(0,0))
        self.assertEqual((c['interval'].hi+r['interval'].hi)/2,a)
        stored_model_k=matrix([[2*a,0],[0,2*a]])
        self.assertEqual(sharp(stored_model_k,kd)['interval'],interval(2*a,2*a))
        self.assertEqual(gram.construct_k(matrix([[0,0],[0,0]]),matrix([[0,0],[0,0]])),matrix([[0,0],[0,0]]))

    def test_k_disk_conjugation_transpose_and_radius(self):
        c=[[gram.ComplexDisk((Q(3),Q(4)),Q(1)),gram.ComplexDisk((Q(1),Q(2)),Q(2))]]
        r=[[gram.ComplexDisk((Q(1),Q(6)),Q(3))],[gram.ComplexDisk((Q(5),Q(8)),Q(4))]]
        result=k_disks(c,r)
        self.assertEqual(result[0][0].center,(Q(1),Q(5)))
        self.assertEqual(result[0][1].center,(Q(-2),Q(5)))
        self.assertEqual([x.radius for x in result[0]],[Q(2),Q(3)])

    def test_direct_target_gap_refines_raw_tube(self):
        a=Q(1,1000);zero=[[gram.ComplexDisk((Q(0),Q(0)),Q(0)) for _ in range(2)] for _ in range(2)]
        local=matrix([[0,0],[0,0]]);other=matrix([[2*a,0],[0,2*a]])
        direct=gap(sharp(local,zero)['interval'],sharp(other,zero)['interval'])
        raw=matrix([[a,0],[0,a]])
        rawgap=gap(gram.spectral_norm(subtract(local,raw)),gram.spectral_norm(subtract(other,raw)))
        # Direct exact residuals are -aI and +aI, so both raw errors are exactly a.
        self.assertEqual(gram.spectral_norm(matrix([[-a,0],[0,-a]])),interval(a,a))
        self.assertEqual(gram.spectral_norm(raw),interval(a,a))
        tube=raw_gap_tube(rawgap,a)
        self.assertEqual(direct,interval(2*a,2*a));self.assertEqual(tube,interval(-2*a,2*a))
        self.assertEqual(intersect(direct,tube),direct)
        self.assertGreater(direct.lo,a);self.assertLess(tube.lo,a)

    def test_max_switch_and_empty_intersection(self):
        self.assertEqual(gram.interval_max(interval(1,3),interval(2,4)),interval(2,4))
        with self.assertRaises(ValueError):intersect(interval(0,1),interval(2,3))

    def test_uniform_gram_radical_width_bound(self):
        a=matrix([[1,2],[3,5],[7,11]])
        for p in (2,4,8,16,32,64):
            i=gram.spectral_norm(a,precision=p);delta=Q(1,2**p)
            remaining=max(Q(0),i.hi-i.lo-2*delta)
            self.assertLessEqual(remaining*remaining,delta/2)
            self.assertEqual(i,gram.spectral_norm(gram.adjoint(a),precision=p))

    def test_negative_radius_rejected(self):
        with self.assertRaises(gram.ContractError):gram.ComplexDisk((Q(0),Q(0)),Q(-1))

    def test_fixed_shape_rational_radius_allocation(self):
        margin=Q(1);r=margin/160;w=margin/8
        rho=t5.fixed94_radius_bound(r)
        self.assertEqual(rho,10*r)
        self.assertLessEqual(94*r*r,rho*rho)
        self.assertEqual(2*w+4*rho,margin/2)
        # A coarsely rounded sqrt is not automatically this small.
        coarse=gram.sqrt_interval(94*r*r,precision=1).hi
        self.assertGreater(coarse,rho)


if __name__=='__main__':unittest.main(verbosity=2)
