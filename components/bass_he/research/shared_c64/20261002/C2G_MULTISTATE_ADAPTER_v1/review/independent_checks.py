"""Independent C2g manufactured/contract checks; no molecular eigensolves."""
from pathlib import Path
import hashlib, json, sys, tempfile, unittest, copy
from dataclasses import replace
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'code'))
from optimized_solver import PartialWaveState, MultiStateResult, RESIDUAL_DEFINITION, _finish_eigenpairs
from multistate_provider import save_sector,load_sector
from common_embedding import build_common_grid,embed_state,write_source_binding,snapshot_from_archives,EmbeddingError
from projector import validate_snapshot,ValidationTolerances,TargetSpec,transport_frames

def fixture(m,mesh,R=4.):
    mesh=np.array(mesh,dtype=np.float64); degree=2; L=float(mesh[-1])
    ls=np.arange(m,6 if m==0 else 4,dtype=np.int64)
    radial_nodes=np.unique(np.r_[mesh,(mesh[:-1]+mesh[1:])/2])
    radial=np.sqrt(30/L**5)*radial_nodes*(L-radial_nodes)
    energies=[-3.,-1.2,-1.1,-1.,-.4,-.2] if m==0 else [-1.15,-.5,-.3]
    meta={'origin_center':'O','origin_shift_center_to_O':0.,'units':'a_A,E_A','radial_quadrature':4,
          'residual_definition':RESIDUAL_DEFINITION,'backend':'manufactured-test',
          'source_files_sha256':{'independent_checks.py':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}}
    states=[]
    for j,E in enumerate(energies):
        coeff=np.zeros((len(ls),len(radial_nodes)),dtype=np.float64);coeff[j]=radial
        states.append(PartialWaveState(R,1.,2.,m,ls.copy(),mesh.copy(),degree,coeff,E,0.,1.,float(np.max(np.abs(coeff))),{**meta,'source_ordinal':j}))
    C=np.column_stack([s.coefficients[:,1:-1].reshape(-1) for s in states])
    return MultiStateResult(tuple(states),np.diag(energies),np.eye(len(states)),C,meta)

class Checks(unittest.TestCase):
    def test_nontrivial_mass_eigenpair_postprocess(self):
        # Three FEM interior coefficients, nontrivial diagonal mass, eigenpairs deliberately unordered/sign-flipped.
        M=np.diag([2.,3.,5.]); E=np.array([-3.,-1.,.4]); Q=np.array([[1.,2.,2.],[2.,1.,-2.],[2.,-2.,1.]])/3
        C=np.diag(1/np.sqrt(np.diag(M)))@Q
        H=M@C@np.diag(E)@C.T@M
        order=[2,0,1];vectors=C[:,order]*np.array([-5.,2.,-3.])
        result=_finish_eigenpairs(H,M,E[order],vectors,R=4.,ZA=1.,ZB=2.,m=0,ls=np.array([0]),boundaries=np.array([0.,1.,2.]),degree=2,nroots=3,metadata={})
        np.testing.assert_allclose([s.energy for s in result.states],E,atol=0,rtol=0)
        np.testing.assert_allclose(result.mass_gram,np.eye(3),atol=8e-16)
        np.testing.assert_allclose(result.projected_operator,np.diag(E),atol=2e-15)
        self.assertLess(max(s.residual for s in result.states),2e-15)
        self.assertTrue(np.all(result.coefficient_vectors[np.argmax(np.abs(result.coefficient_vectors),axis=0),np.arange(3)]>0))
    def test_exact_common_grid_across_nonnested_meshes(self):
        a=fixture(0,[0,.3,1.1,2]).states[0];b=fixture(0,[0,.7,1.6,2],R=4.25).states[0]
        grid=build_common_grid([a,b],radial_order=3,eta_order=6,phi_count=5)
        va,vb=embed_state(a,grid),embed_state(b,grid)
        np.testing.assert_allclose(va,vb,atol=8e-16,rtol=1e-14)
        self.assertLess(abs(np.vdot(va,grid.weights*va)-1),4e-15)
        self.assertTrue(np.all(grid.weights>0));self.assertFalse(grid.weights.flags.writeable)
    def test_complex_partner_conjugacy_and_orthogonality(self):
        s=fixture(1,[0,.6,1.3,2]).states[0];grid=build_common_grid([s])
        p=embed_state(s,grid,m_signed=1);n=embed_state(s,grid,m_signed=-1)
        np.testing.assert_array_equal(n,p.conj())
        self.assertLess(abs(np.vdot(p,grid.weights*n)),1e-15)
        self.assertLess(abs(np.vdot(p,grid.weights*p)-1),4e-15)
        bright=(p+n)/np.sqrt(2);dark=(p-n)/(1j*np.sqrt(2))
        self.assertLess(np.max(abs(bright.imag)),1e-16);self.assertLess(np.max(abs(dark.imag)),1e-16)
    def test_quadrature_alias_and_origin_rejected(self):
        s=fixture(1,[0,.6,1.3,2]).states[0]
        for kwargs in ({'phi_count':2},{'radial_order':2},{'eta_order':3}):
            with self.assertRaises(EmbeddingError):build_common_grid([s],**kwargs)
        with self.assertRaises(EmbeddingError):build_common_grid([replace(s,metadata={**s.metadata,'origin_center':'B'})])
    def test_analytic_r2_and_half_box_concentration_are_span_invariants(self):
        from analyze_reference import normalized_observables
        states=fixture(0,[0,.3,1.1,2]).states[:3]
        grid=build_common_grid(states,radial_order=4,extra_radial_knots=(1.,))
        frame=np.column_stack([embed_state(s,grid) for s in states])
        radius=np.repeat(grid.r,grid.shape[1]*grid.shape[2])
        values,_=normalized_observables(frame,grid.weights,radius,(1.,2.))
        # u(r) ∝ r(2-r): <r²>=8/7 and half-box probability=1/2 analytically.
        self.assertAlmostEqual(values['trace_r2'],24/7,places=13)
        self.assertAlmostEqual(values['outer_layer_probability_max'],.5,places=13)
        mixing=np.array([[1.,.2j,.3],[.1,1.2,.1j],[.4,0.,.8]],dtype=np.complex128)
        changed,_=normalized_observables(frame@mixing,grid.weights,radius,(1.,2.))
        self.assertAlmostEqual(changed['trace_r2'],24/7,places=12)
        self.assertAlmostEqual(changed['outer_layer_probability_max'],.5,places=12)
        self.assertGreater(changed['selected_Gram_operator_norm_error'],.1)

    def test_exact_physical_contract_rejects_unregistered_layout_and_mesh(self):
        from physical_contract import load_manifest,validate_manifest,validate_request,validate_review
        from runtime_support import ContractError
        manifest=load_manifest(ROOT/'contract/PHYSICAL_TASKS.json')
        host={'effective_cpu_budget':8,'memory_available_bytes':8*1024**3,'physical_cores_in_affinity':{str(i):[i] for i in range(8)}}
        validate_request(manifest,'serial','numpy',None,1,1,'none',host)
        for layout in [('serial','numpy',None,1,2,'none'),('mpi','native',str(ROOT/'native/build/libbass_element.so'),2,4,'none'),('serial','numpy',None,1,1,'core')]:
            with self.assertRaises(ContractError):validate_request(manifest,*layout,host)
        bad=copy.deepcopy(manifest);t=bad['tasks'][0];radius=t['R']*t['ZA']/(t['ZA']+t['ZB']);t['boundaries'].remove(radius)
        with self.assertRaises(ContractError):validate_manifest(bad)
        review={'schema':'bass-he.c2g.physical-launch-review.v1','status':'PASS','approved_manifest_sha256':'0'*64,'approved_preregistration_sha256':'1'*64,'reviewer':'independent-fixture','evidence_scope':'finite_basis_electronic_reference_pilot'}
        with self.assertRaises(ContractError):validate_review(review,{'sha256':'2'*64},{'sha256':'1'*64})

    def test_equal_norm_in_memory_source_substitution_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'m0.npz';save_sector(fixture(0,[0,.3,1.1,2]),path,'independent-source')
            archive=load_sector(path)
            # Swapping normalized modes preserves every norm, but changes their energy/source association.
            a,b=archive.result.states[:2]
            a.coefficients,b.coefficients=b.coefficients,a.coefficients
            with self.assertRaises(EmbeddingError):
                write_source_binding([archive],Path(d)/'bad.json',source_id='mutated-memory')
            self.assertFalse((Path(d)/'bad.json').exists())

    def test_archives_to_complete_selected_guard_snapshot(self):
        with tempfile.TemporaryDirectory() as d:
            paths=[]
            for m,mesh in [(0,[0,.3,1.1,2]),(1,[0,.7,1.6,2])]:
                p=Path(d)/f'm{m}.npz';save_sector(fixture(m,mesh),p,f'independent-m{m}');paths.append(p)
            arcs=[load_sector(p) for p in paths];grid=build_common_grid([s for a in arcs for s in a.result.states])
            bind=Path(d)/'binding.json';write_source_binding(arcs,bind,source_id='independent-snapshot')
            result=snapshot_from_archives(arcs,grid,source_binding_path=bind,gram_identity_atol=2e-12)
            diag=validate_snapshot(result.snapshot,TargetSpec.large_R_rank5(),ValidationTolerances(2e-12,1e-12,1e-10,1e-4),backend='reference')
            self.assertEqual((diag.selected_rank,diag.guard_count),(5,7));self.assertFalse(diag.full_H_certificate)
            np.testing.assert_allclose(np.diag(result.snapshot.selected_projected_operator),[-1.2,-1.1,-1.,-1.15,-1.15],atol=0,rtol=0)
            self.assertTrue(all(s.known_degenerate_partners for s in result.snapshot.states if s.m!=0))
            with self.assertRaises(FileExistsError):save_sector(fixture(0,[0,.3,1.1,2]),paths[0],'overwrite')
            data=bytearray(paths[0].read_bytes());data[-1]^=1;paths[0].write_bytes(data)
            with self.assertRaises((EmbeddingError,ValueError)):
                snapshot_from_archives(arcs,grid,source_binding_path=bind,gram_identity_atol=2e-12)

if __name__=='__main__':unittest.main(verbosity=2)
