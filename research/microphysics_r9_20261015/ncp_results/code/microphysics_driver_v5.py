#!/usr/bin/env python3
"""R9 additive finite-Gaussian FCI worker; no physical continuum or rates.

One isolated subprocess per immutable case. Artifacts include CI vectors, orbital
matrices and original-Hamiltonian residuals. See CONTRACT_MICROPHYSICS.md.
"""
from __future__ import annotations
import argparse, datetime, hashlib, json, math, os, platform, resource, subprocess, sys, time, traceback
from pathlib import Path


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dump(path, value):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix(path.suffix+'.tmp');tmp.write_text(json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n');tmp.replace(path)


def system_info():
    import numpy as np, scipy, pyscf
    try:
        from threadpoolctl import threadpool_info
        pools=threadpool_info()
    except ImportError:pools=[]
    return dict(python=sys.version,numpy=np.__version__,scipy=scipy.__version__,pyscf=pyscf.__version__,platform=platform.platform(),cpu_count=os.cpu_count(),thread_pools=pools,source_sha256=sha(__file__))


class Deferred(RuntimeError):pass


def estimate(norb,nelec,limit_gib,extra_vectors=0):
    d=math.comb(norb,nelec[0])*math.comb(norb,nelec[1]);eri=norb**4*8
    # Conservative in-core AO/MO ERI copies + Davidson basis/action vectors.
    rss=4*eri+(2*40+16+extra_vectors)*d*8+512*1024**2
    est=dict(norb=norb,nelec=list(nelec),determinants=d,dense_eri_bytes=eri,estimated_rss_bytes=rss,job_limit_bytes=int(limit_gib*1024**3))
    if d>10_000_000 or eri>8*1024**3 or rss>.75*limit_gib*1024**3:raise Deferred(json.dumps(est))
    return est


def basis_record(mol):
    return {'expanded_basis':mol._basis,'expanded_basis_sha256':hashlib.sha256(json.dumps(mol._basis,sort_keys=True).encode()).hexdigest(),'cartesian':bool(mol.cart),'ecp':mol._ecp}


def mol_build(atom,basis,charge,spin,memory,symmetry=False):
    from pyscf import gto
    return gto.M(atom=atom,basis=basis,charge=charge,spin=spin,unit='Bohr',cart=False,symmetry='C2v' if symmetry else False,verbose=0,max_memory=int(memory*1024*.70))


def raw_action(h,eri,norb,nelec):
    from pyscf import fci
    heff=fci.direct_spin1.absorb_h1e(h,eri,norb,nelec,.5)
    return lambda c:fci.direct_spin1.contract_2e(heff,c,norb,nelec)



def solve_twoelectron_matrix(mol,C,h,eri,case):
    """Exact singlet FCI in an orthonormal symmetric-matrix coordinate basis."""
    import numpy as np
    from scipy.sparse.linalg import LinearOperator,eigsh
    from pyscf import ao2mo
    n=C.shape[1]
    if tuple(mol.nelec)!=(1,1) or mol.spin!=0:raise ValueError('exact matrix backend requires 2e singlet')
    erifull=ao2mo.restore(1,eri,n)
    rows,cols=np.triu_indices(n,1);root2=np.sqrt(2.);dim=n*(n+1)//2
    def expand(v):
        mat=np.zeros((n,n));mat[np.diag_indices(n)]=v[:n]
        mat[rows,cols]=v[n:]/root2;mat[cols,rows]=v[n:]/root2
        return mat
    def pack(mat):return np.concatenate([np.diag(mat),root2*mat[rows,cols]])
    def action(mat):return h@mat+mat@h.T+np.einsum('prqs,rs->pq',erifull,mat,optimize=False)
    def matvec(v):
        hc=action(expand(v));return pack((hc+hc.T)/2)
    op=LinearOperator((dim,dim),matvec=matvec,dtype=float);v0=pack(np.eye(n)/np.sqrt(n))
    t=time.monotonic();values,vectors=eigsh(op,k=1,which='SA',v0=v0,ncv=min(40,dim),maxiter=200,tol=case.get('fci_tol',1e-11))
    ci=expand(vectors[:,0]);ci/=np.linalg.norm(ci)
    if ci.ravel()[np.argmax(abs(ci))]<0:ci=-ci
    hc=action(ci);ee=float(np.vdot(ci,hc).real);res=float(np.linalg.norm(hc-ee*ci))
    rdm=ci@ci.T+ci.T@ci;spin2=float(1-np.vdot(ci,ci.T).real)
    S=mol.intor('int1e_ovlp');orth=float(np.linalg.norm(C.T@S@C-np.eye(n),np.inf))
    checks={'norm_error':abs(float(np.vdot(ci,ci))-1),'orthogonality_inf':orth,'rdm_trace_error':abs(float(np.trace(rdm))-2),'spin_error':abs(spin2),'original_H_residual_Eh':res,'fci_converged':True,'energy_solver_original_difference_Eh':abs(float(values[0])-ee),'CI_symmetry_error':float(np.linalg.norm(ci-ci.T))}
    ok=checks['norm_error']<=1e-10 and orth<=1e-8 and checks['rdm_trace_error']<=1e-8 and abs(spin2)<=1e-6 and res<=1e-7
    info={'E_BO_Eh':ee+mol.energy_nuc(),'E_electronic_Eh':ee,'nuclear_repulsion_Eh':float(mol.energy_nuc()),'spin_squared':spin2,'nelec':[1,1],'norb':n,'fci_wall_s':time.monotonic()-t,'checks':checks,'finite_model_numerics_passed':ok,'two_electron_residual_target_met':res<=1e-9,'basis':basis_record(mol),'solver_backend':'exact_two_electron_singlet_symmetric_matrix_LinearOperator','symmetric_dimension':dim}
    if not ok:raise RuntimeError('finite_model_gate_failed: '+json.dumps(info))
    arrays={'CI':ci,'orbital_matrix':np.asarray(C),'rdm1':rdm,'AO_overlap_eigenvalues':np.linalg.eigvalsh(S)}
    return info,arrays,action


def solve_integrals(mol,C,h,eri,case,orbsym=None):
    import numpy as np
    from pyscf import fci
    n=C.shape[1]; desired=mol.spin/2*(mol.spin/2+1)
    if n>=64:
        if tuple(mol.nelec)==(1,1) and mol.spin==0:return solve_twoelectron_matrix(mol,C,h,eri,case)
        raise Deferred(json.dumps(dict(norb=n,nelec=list(mol.nelec),reason='native_FCI_bitstring_backend_requires_norb_below64_for_more_than2e')))

    solver=fci.direct_spin1_symm.FCI(mol) if orbsym is not None else fci.direct_spin1.FCI(mol)
    if orbsym is not None:solver.orbsym=orbsym;solver.wfnsym='A1'
    solver=fci.addons.fix_spin_(solver,shift=2.,ss=desired)
    solver.nroots=1;solver.conv_tol=case.get('fci_tol',1e-11);solver.conv_tol_residual=case.get('residual_tol',1e-10 if mol.nelectron==2 else 5e-8);solver.lindep=1e-24;solver.max_cycle=200;solver.max_space=40
    t=time.monotonic();e,c=solver.kernel(h,eri,n,mol.nelec,ecore=mol.energy_nuc())
    c=np.asarray(c);c/=np.linalg.norm(c)
    if c.ravel()[np.argmax(abs(c))]<0:c=-c
    act=raw_action(h,eri,n,mol.nelec);hc=act(c)
    e_original=float(np.vdot(c,hc).real+mol.energy_nuc());res=float(np.linalg.norm(hc-(e_original-mol.energy_nuc())*c))
    s2=float(fci.spin_op.spin_square(c,n,mol.nelec)[0]);rdm=fci.direct_spin1.make_rdm1(c,n,mol.nelec)
    S=mol.intor('int1e_ovlp');orth=float(np.linalg.norm(C.T@S@C-np.eye(n),np.inf))
    checks={'norm_error':abs(float(np.vdot(c,c))-1),'orthogonality_inf':orth,'rdm_trace_error':abs(float(np.trace(rdm))-mol.nelectron),'spin_error':abs(s2-desired),'original_H_residual_Eh':res,'fci_converged':bool(np.all(solver.converged)),'energy_solver_original_difference_Eh':abs(float(e)-e_original)}
    ok=checks['norm_error']<=1e-10 and orth<=1e-8 and checks['rdm_trace_error']<=1e-8 and checks['spin_error']<=1e-6 and res<=1e-7 and checks['fci_converged']
    info={'E_BO_Eh':e_original,'E_electronic_Eh':e_original-mol.energy_nuc(),'nuclear_repulsion_Eh':float(mol.energy_nuc()),'spin_squared':s2,'nelec':list(mol.nelec),'norb':n,'fci_wall_s':time.monotonic()-t,'checks':checks,'finite_model_numerics_passed':ok,'two_electron_residual_target_met':res<=1e-9 if mol.nelectron==2 else None,'basis':basis_record(mol)}
    if not ok:raise RuntimeError('finite_model_gate_failed: '+json.dumps(info))
    return info,{'CI':c,'orbital_matrix':np.asarray(C),'rdm1':rdm,'AO_overlap_eigenvalues':np.linalg.eigvalsh(S)},act


def stationary(mol,case):
    import numpy as np
    from pyscf import scf,ao2mo,symm
    est=estimate(mol.nao_nr(),mol.nelec,case['memory_gib'],extra_vectors=2*case.get('lanczos_max',0))
    if mol.nao_nr()>=64 and mol.nelectron!=2:
        raise Deferred(json.dumps(dict(norb=mol.nao_nr(),nelec=list(mol.nelec),reason='native_FCI_bitstring_backend_requires_norb_below64_for_more_than2e')))
    mf=scf.RHF(mol) if mol.spin==0 else scf.ROHF(mol)
    mf.conv_tol=1e-12;mf.max_cycle=150;scf_error=None
    try:mf.kernel()
    except Exception as exc:scf_error=type(exc).__name__+': '+str(exc)
    S=mol.intor('int1e_ovlp');C=getattr(mf,'mo_coeff',None);orbsym=None
    valid=C is not None
    if valid:
        C=np.asarray(C)
        valid=C.ndim==2 and C.shape==(mol.nao_nr(),mol.nao_nr()) and np.all(np.isfinite(C))
        if valid:valid=np.linalg.norm(C.T@S@C-np.eye(C.shape[1]),np.inf)<=1e-8
    if valid and mol.symmetry:
        try:orbsym=symm.label_orb_symm(mol,mol.irrep_id,mol.symm_orb,C)
        except Exception:valid=False
    scf_converged=bool(getattr(mf,'converged',False))
    if valid:
        orbital_source='converged_SCF_full_MOs' if scf_converged else 'unconverged_SCF_full_orthonormal_MOs'
    else:
        cutoff=1e-10*float(np.linalg.eigvalsh(S).max())
        if mol.symmetry:
            blocks=[];labels=[]
            for irrep,block in zip(mol.irrep_id,mol.symm_orb):
                ev,U=np.linalg.eigh(block.T@S@block);keep=ev>cutoff
                if np.any(keep):
                    blocks.append(block@U[:,keep]/np.sqrt(ev[keep]));labels.extend([irrep]*int(sum(keep)))
            C=np.column_stack(blocks);orbsym=np.asarray(labels,dtype=int)
            orbital_source='canonical_AO_metric_orthogonalization_by_C2v_irrep'
        else:
            ev,U=np.linalg.eigh(S);keep=ev>cutoff;C=U[:,keep]/np.sqrt(ev[keep])
            orbital_source='canonical_AO_metric_orthogonalization'
    h=C.T@(mol.intor('int1e_kin')+mol.intor('int1e_nuc'))@C
    eri=ao2mo.kernel(mol,C)
    info,arrays,act=solve_integrals(mol,C,h,eri,case,orbsym)
    scf_energy=getattr(mf,'e_tot',None)
    if scf_energy is not None:scf_energy=float(scf_energy) if np.isfinite(scf_energy) else None
    info.update(scf_converged=scf_converged,scf_energy_Eh=scf_energy,scf_error=scf_error,scf_cycles_completed=int(mf.cycles) if getattr(mf,'cycles',None) is not None else None,resource_estimate=est,orbital_source=orbital_source,retained_orbital_rank=C.shape[1],AO_metric_relative_cutoff=1e-10 if not valid else None)
    arrays['h1']=h
    mol.set_common_orig_((0,0,0));rmo=np.einsum('pi,xpq,qj->xij',C,mol.intor('int1e_r',comp=3),C)
    dip=-np.einsum('xij,ji->x',rmo,arrays['rdm1'])+np.einsum('a,ax->x',mol.atom_charges(),mol.atom_coords())
    arrays['dipole_ea0']=dip;arrays['position_mo']=rmo
    return info,arrays,act


SPECIES={'Li':('Li',0,1),'Li+':('Li',1,0),'He':('He',0,0),'H':('H',0,1),'H-':('H',-1,0)}


def atomic(case):
    atom,charge,spin=SPECIES[case['species']]
    m=mol_build([(atom,(0,0,0))],case['basis'],charge,spin,case['memory_gib'])
    i,a,_=stationary(m,case);i['physical_scope']='clamped_infinite_mass_all_electron_finite_Gaussian_FCI_ground_target';return i,a


def quench(case):
    import numpy as np
    from pyscf import gto,ao2mo
    # Element-specific union shells remain identical for BOTH Hamiltonians.
    elements=case.get('basis_elements',[case.get('basis_element','Li')])
    b=[]
    for element in elements:b.extend(gto.basis.load(case['basis'],element))
    initial=case.get('initial_symbol','He');final=case.get('final_symbol','Li');spin=case.get('spin',0)
    mi=mol_build([(initial,(0,0,0))],{initial:b},case.get('initial_charge',0),spin,case['memory_gib'])
    mf=mol_build([(final,(0,0,0))],{final:b},case.get('final_charge',1),spin,case['memory_gib'])
    if mi.nelec!=mf.nelec:raise ValueError('quench must preserve alpha/beta electron numbers')

    S=mi.intor('int1e_ovlp');ss,U=np.linalg.eigh(S);keep=ss>case.get('s_cutoff',1e-10)*ss.max();X=U[:,keep]/np.sqrt(ss[keep])
    est=estimate(X.shape[1],mi.nelec,case['memory_gib'])
    if X.shape[1]>=64 and mi.nelectron!=2:
        raise Deferred(json.dumps(dict(norb=X.shape[1],nelec=list(mi.nelec),reason='native_FCI_bitstring_backend_requires_norb_below64_for_more_than2e')))
    eri=ao2mo.kernel(mi,X)
    def target(m):
        h=X.T@(m.intor('int1e_kin')+m.intor('int1e_nuc'))@X
        return solve_integrals(m,X,h,eri,case)
    ii,ai,_=target(mi);fi,af,hf=target(mf);ci=ai['CI'];cf=af['CI'];A=np.vdot(cf,ci);p=float(abs(A)**2);q=ci-A*cf;comp=float(np.vdot(q,q).real);cross=float(abs(np.vdot(cf,q)))
    hci=hf(ci);mean=float(np.vdot(ci,hci).real);h2=float(np.vdot(hci,hci).real)
    gates={'closure_error':abs(p+comp-1),'ground_complement_overlap':cross}
    ok=gates['closure_error']<=1e-10 and cross<=1e-10
    if not ok:raise RuntimeError('quench closure failed')
    info={'physical_scope':f'correlated_{mi.nelectron}_electron_{initial}_to_{final}_sudden_common_space_projection','parent':ii,'daughter':fi,'P_ground':p,'A_ground_real':float(A.real),'unresolved_excitation_including_bound_probability':comp,'daughter_energy_mean_Eh':mean,'daughter_energy_second_moment_Eh2':h2,'daughter_energy_variance_Eh2':h2-mean**2,'checks':gates,'finite_model_numerics_passed':ok,'resource_estimate':est,'retained_ao_rank':int(sum(keep)),'ao_rank':len(ss),'s_cutoff_relative':case.get('s_cutoff',1e-10)}
    info.update(basis_elements=elements,initial_symbol=initial,final_symbol=final,common_expanded_basis=b,common_expanded_basis_sha256=hashlib.sha256(json.dumps(b,sort_keys=True).encode()).hexdigest())
    arrays={'CI_parent':ci,'CI_daughter_ground':cf,'CI_complement':q,'common_orbital_matrix':X,'AO_overlap_eigenvalues':ss,'rdm1_parent':ai['rdm1'],'rdm1_daughter':af['rdm1']}
    return info,arrays


def molecule(case):
    import numpy as np
    atoms=['Li','H'] if case['molecule']=='LiH' else ['Li','He'];spin=0 if atoms[1]=='H' else 1;r=case['R_a0'];coords=[(0,0,-r/2),(0,0,r/2)]
    m=mol_build(list(zip(atoms,coords)),case['basis'],0,spin,case['memory_gib'],True)
    info,arrays,_=stationary(m,case);own=[];ghost=[]
    for j,atom in enumerate(atoms):
        q,s=SPECIES[atom][1:]
        ma=mol_build([(atom,(0,0,0))],case['basis'],q,s,case['memory_gib']);ia,_,_=stationary(ma,case);own.append(ia)
        spec=[(a if k==j else 'ghost-'+a,coords[k]) for k,a in enumerate(atoms)]
        mg=mol_build(spec,case['basis'],q,s,case['memory_gib']);ig,_,_=stationary(mg,case);ghost.append(ig)
    info.update(physical_scope='neutral_ground_state_clamped_finite_basis_BO_with_counterpoise',R_a0=r,molecule=case['molecule'],fragment_own=own,fragment_counterpoise=ghost,V_raw_Eh=info['E_BO_Eh']-sum(i['E_BO_Eh'] for i in own),V_CP_Eh=info['E_BO_Eh']-sum(i['E_BO_Eh'] for i in ghost))
    info['BSSE_CP_minus_raw_Eh']=info['V_CP_Eh']-info['V_raw_Eh'];arrays['atom_coordinates_a0']=m.atom_coords();arrays['atom_charges']=m.atom_charges()
    return info,arrays


def lanczos_chain(b,act,E,m):
    import numpy as np
    beta0=float(np.linalg.norm(b));q=b/beta0;basis=[];alpha=[];off=[];qprev=np.zeros_like(q);prev=0.
    for j in range(m):
        basis.append(q.copy());z=act(q)-E*q-prev*qprev;a=float(np.vdot(q,z).real);alpha.append(a);z-=a*q
        # Two-pass full reorthogonalization suppresses ghost Ritz roots.
        for _ in range(2):
            for v in basis:z-=np.vdot(v,z)*v
        beta=float(np.linalg.norm(z))
        if j==m-1 or beta<1e-13:break
        off.append(beta);qprev=q;q=z/beta;prev=beta
    T=np.diag(alpha)+np.diag(off,1)+np.diag(off,-1);w,v=np.linalg.eigh(T);weights=beta0**2*v[0]**2
    Q=np.asarray([v.ravel() for v in basis]);gram=float(np.linalg.norm(Q@Q.T-np.eye(len(Q)),np.inf))
    return w,weights,gram


def response(case):
    import numpy as np
    from pyscf import fci
    c2=dict(case);c2['species']='Li';c2['lanczos_max']=max(case.get('lengths',[32,64,128]));m=mol_build([('Li',(0,0,0))],case['basis'],0,1,case['memory_gib']);info,a,act=stationary(m,c2)
    c=a['CI'];E=info['E_electronic_Eh'];n=info['norb'];mom=np.zeros(3);starts=[]
    for r in a['position_mo']:
        dc=fci.direct_spin1.contract_1e(r,c,n,m.nelec);b=dc-np.vdot(c,dc)*c;kb=act(b)-E*b
        mom+=np.array([np.vdot(b,b).real,np.vdot(b,kb).real,np.vdot(kb,kb).real]);starts.append(b)
    omega=np.arange(1001)*.002;etas=case.get('etas_Eh',[.02,.01,.005]);records=[]
    for length in case.get('lengths',[32,64,128]):
        ws=[];ps=[];grams=[]
        for b in starts:
            if np.linalg.norm(b)<1e-14:continue
            w,p,g=lanczos_chain(b,act,E,length);ws.extend(w);ps.extend(p);grams.append(g)
        w=np.asarray(ws);p=np.asarray(ps);mom_l=np.array([sum(p*w**k) for k in range(3)]);errors=abs(mom_l-mom);gram=max(grams,default=0.)
        for eta in etas:
            S=np.sum(p[:,None]*eta/(np.pi*((omega[None,:]-w[:,None])**2+eta**2)),axis=0)
            window=float(np.sum(p*(np.arctan((2-w)/eta)-np.arctan(-w/eta))/np.pi))
            a[f'response_L{length}_eta{eta:g}']=S
            records.append({'length':length,'eta_Eh':eta,'window_weight':window,'missing_window_weight':float(mom[0]-window)})
        a[f'ritz_omega_L{length}_Eh']=w;a[f'ritz_weights_L{length}']=p
        records.append({'length':length,'gram_defect_inf':gram,'moment_errors':errors.tolist(),'moment_gate':bool(np.all(errors<=1e-8*np.maximum(1,abs(mom)))),'negative_weight_min':float(p.min()),'negative_excitation_min_Eh':float(w.min()),'lanczos_dimension_summed_axes':len(w)})
    info.update(physical_scope='finite_Gaussian_projected_dipole_response',state_label='pseudostate',physical_continuum_status='missing_provider_or_boundary_validation',direct_moments_au=mom.tolist(),TRK_diagnostic=float(2/3*mom[1]),lanczos_records=records)
    info['response_internal_numerics_passed']=all(x.get('moment_gate',True) and x.get('gram_defect_inf',0)<=1e-8 for x in records)
    info['finite_model_numerics_passed']=info['finite_model_numerics_passed'] and info['response_internal_numerics_passed']
    convergence=[]
    if 64 in case.get('lengths',[32,64,128]) and 128 in case.get('lengths',[32,64,128]):
        for eta in etas:
            x=a[f'response_L64_eta{eta:g}'];y=a[f'response_L128_eta{eta:g}'];rel=float(np.sum(abs(x-y))/max(np.sum(abs(y)),1e-300));convergence.append({'eta_Eh':eta,'L64_L128_relative_L1':rel,'target_met':rel<=1e-3})
    info['response_krylov_convergence']=convergence;a['omega_grid_Eh']=omega;a['direct_moments_au']=mom
    return info,a


def execute_case(case,out):
    import numpy as np
    from pyscf import lib
    # Some container runtimes expose /proc/self but a different numeric PID namespace.
    try:lib.current_memory()
    except FileNotFoundError:
        def self_memory():
            vals=Path('/proc/self/statm').read_text().split();page=os.sysconf('SC_PAGE_SIZE')
            return int(vals[1])*page/1e6,int(vals[0])*page/1e6
        lib.current_memory=self_memory
    lib.num_threads(case['threads']);out=Path(out);out.mkdir(parents=True,exist_ok=True);t=time.monotonic()
    receipt={'case':case,'case_sha256':hashlib.sha256(json.dumps(case,sort_keys=True).encode()).hexdigest(),'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'runtime':system_info(),'implementation_checked':True,'finite_model_numerics_passed':False,'basis_target_met':None,'remaining_dependencies':['basis_convergence','finite_nuclear_mass_relativistic_and_HFS_terms','physical_continuum_scattering_provider','channel_specific_molecular_reaction_calculation']}
    code=0
    try:
        info,arrays={'atomic':atomic,'quench':quench,'molecule':molecule,'response':response}[case['kind']](case);receipt.update(info);receipt['status']='finite_model_computed'
        tmp=out/'data.tmp.npz';np.savez_compressed(tmp,**arrays);tmp.replace(out/'data.npz');receipt['data_sha256']=sha(out/'data.npz')
        # Small reviewable scalar table accompanies complete NPZ/JSON.
        scalars={k:v for k,v in receipt.items() if isinstance(v,(float,int,str,bool)) or v is None}
        import csv
        with (out/'scalars.csv').open('w',newline='') as f:
            w=csv.writer(f);w.writerow(['key','value']);w.writerows(scalars.items())
    except Deferred as e:receipt.update(status='resource_deferred',resource_estimate=json.loads(str(e)));code=3
    except Exception as e:receipt.update(status='failed',error=str(e),traceback=traceback.format_exc());code=1
    receipt.update(wall_s=time.monotonic()-t,peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,exit_code=code,completed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());dump(out/'receipt.json',receipt)
    print(json.dumps({'case':case['id'],'status':receipt['status'],'wall_s':receipt['wall_s'],'out':str(out)},sort_keys=True),flush=True)
    return code


def default_cases(contract=None):
    cases=[]
    def add(id,kind,**kw):cases.append(dict(id=id,kind=kind,**kw))
    if contract is None:contract=json.loads((Path(__file__).resolve().parent.parent/'CONTRACT_MICROPHYSICS.json').read_text())
    at=contract['atomic'];q=contract['quench'];response_deck=contract['response']
    for state in at['required_species']:
        s=state['id'].replace('_plus','+')
        for b in at['bases']+(at['diffuse_bases'] if state['id'] in at['diffuse_species'] else []):add('atom_'+s.replace('+','plus')+'_'+b,'atomic',species=s,basis=b)
    for b in q['mandatory']['bases']:add('quench_He_Liplus_'+b,'quench',basis=b,s_cutoff=q['orthogonalization']['relative_eigenvalue_cutoff'])
    add('quench_He_Liplus_'+q['mandatory']['bases'][0]+'_cutoff1e-9','quench',basis=q['mandatory']['bases'][0],s_cutoff=q['orthogonalization']['sensitivity_cutoff'])
    for molecular in contract['molecular']['cases']:
        name=molecular['id'];grid=molecular['R_a0'];bases=molecular['bases']
        for b in bases:
            for r in grid:add(f'{name}_{b}_R{r:g}','molecule',molecule=name,basis=b,R_a0=r)
    for b in response_deck['bases']:add('response_Li_'+b,'response',basis=b,lengths=response_deck['lanczos_steps'],etas_Eh=response_deck['eta_Eh'])
    return cases


def pilot_cases(contract):
    cases=[]
    for c in contract['pilots']:
        family=c['family'];kind='molecule' if family=='molecular' else family
        case=dict(kind=kind,basis=c['basis'])
        if kind=='atomic':case['species']=c['species'].replace('_plus','+')
        if kind=='molecule':case.update(molecule=c['id'],R_a0=c['R_a0'])
        if kind=='response':case['lengths']=[c['lanczos_steps']]
        case['id']='pilot_'+kind+'_'+c.get('species',c.get('id',''))+'_'+c['basis']+('_R'+str(c['R_a0']) if 'R_a0' in c else '')
        cases.append(case)
    return cases


def verify(out):
    import numpy as np
    receipts=[]
    for p in sorted(Path(out).glob('*/receipt.json')):
        r=json.loads(p.read_text());r['receipt_path']=str(p)
        if 'data_sha256' in r:r['data_hash_verified']=sha(p.parent/'data.npz')==r['data_sha256']
        receipts.append(r)
    # Matching Li aliases guarantee balanced Li/Li+ AO spaces.
    ion=[]
    for r in receipts:
        c=r['case']
        if c['kind']=='atomic' and c['species']=='Li' and r.get('status')=='finite_model_computed':
            matches=[x for x in receipts if x['case'].get('species')=='Li+' and x['case']['basis']==c['basis'] and x.get('status')=='finite_model_computed']
            if matches:ion.append(dict(basis=c['basis'],I_Li_Eh=matches[0]['E_BO_Eh']-r['E_BO_Eh'],I_Li_eV=(matches[0]['E_BO_Eh']-r['E_BO_Eh'])*27.211386245981))
    curves=[]
    from pyscf import gto,fci
    groups={}
    for r in receipts:
        c=r['case']
        if c['kind']=='molecule' and r.get('status')=='finite_model_computed':groups.setdefault((c['molecule'],c['basis']),[]).append(r)
    for (name,basis),rows in groups.items():
        rows.sort(key=lambda x:x['case']['R_a0']);links=[]
        for old,new in zip(rows,rows[1:]):
            co=old['case'];cn=new['case'];atoms=['Li','H' if name=='LiH' else 'He'];spin=0 if name=='LiH' else 1
            def rebuild(c):
                R=c['R_a0'];return mol_build([(atoms[0],(0,0,-R/2)),(atoms[1],(0,0,R/2))],basis,0,spin,c['memory_gib'],True)
            mo=rebuild(co);mn=rebuild(cn);ao=np.load(Path(old['receipt_path']).parent/'data.npz');an=np.load(Path(new['receipt_path']).parent/'data.npz');old_rank=ao['orbital_matrix'].shape[1];new_rank=an['orbital_matrix'].shape[1]
            if old_rank!=new_rank:
                links.append(dict(R_old_a0=co['R_a0'],R_new_a0=cn['R_a0'],status='overlap_unavailable_rank_change',old_retained_rank=old_rank,new_retained_rank=new_rank))
                continue
            s=ao['orbital_matrix'].T@gto.intor_cross('int1e_ovlp',mo,mn)@an['orbital_matrix'];ov=float(fci.addons.overlap(ao['CI'],an['CI'],old_rank,mo.nelec,s=s));links.append(dict(R_old_a0=co['R_a0'],R_new_a0=cn['R_a0'],signed_overlap=ov,absolute_overlap=abs(ov)))
        curves.append(dict(molecule=name,basis=basis,points=[{k:r[k] for k in ['R_a0','E_BO_Eh','V_raw_Eh','V_CP_Eh','BSSE_CP_minus_raw_Eh']} for r in rows],adjacent_geometry_overlaps=links))
    summary={'receipt_count':len(receipts),'statuses':{s:sum(r.get('status')==s for r in receipts) for s in sorted({r.get('status') for r in receipts})},'ionization_series':ion,'curves':curves,'claim':'finite_model_results_only; no complete_basis_or_physical_continuum_claim'};dump(Path(out)/'summary.json',summary);return summary


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=['preflight','pilot','run','case','verify']);p.add_argument('--contract',type=Path);p.add_argument('--out',type=Path,required=True);p.add_argument('--case-file',type=Path);p.add_argument('--threads',type=int,default=4);p.add_argument('--memory-gib',type=float,default=16);p.add_argument('--workers',type=int,default=1);p.add_argument('--cpu-cap',type=int,default=48);p.add_argument('--memory-cap-gib',type=float,default=96);p.add_argument('--wall-s',type=int);p.add_argument('--family-wall-s',type=int,default=21600);p.add_argument('--only',nargs='*');p.add_argument('--fci-tol',type=float);p.add_argument('--residual-tol',type=float);p.add_argument('--label',default='');args=p.parse_args()
    if args.mode=='case':
        case=json.loads(args.case_file.read_text());limit=int(case['memory_gib']*1024**3);resource.setrlimit(resource.RLIMIT_AS,(limit,limit))
        return execute_case(case,args.out)
    if args.mode=='verify':print(json.dumps(verify(args.out),indent=2));return 0
    if args.threads<1 or args.workers<1 or args.workers*args.threads>min(48,args.cpu_cap) or args.workers*args.memory_gib>min(96,args.memory_cap_gib):p.error('aggregate allocation exceeds frozen CPU/RAM caps')
    if args.contract is None or not args.contract.exists():p.error('frozen contract file required')
    contract=json.loads(args.contract.read_text());args.out.mkdir(parents=True,exist_ok=True)
    if args.mode=='preflight':dump(args.out/'preflight.json',dict(runtime=system_info(),contract_sha256=sha(args.contract),meminfo=Path('/proc/meminfo').read_text(),allocation=vars(args)|{'out':str(args.out),'contract':str(args.contract),'case_file':None}));return 0
    cases=(contract.get('pilot_execution_cases') or pilot_cases(contract)) if args.mode=='pilot' else (contract.get('execution_cases') or default_cases(contract))
    if args.only:cases=[c for c in cases if any(x in c['id'] for x in args.only)]
    for c in cases:c.update(threads=args.threads,memory_gib=args.memory_gib,contract_sha256=sha(args.contract),contract_id=contract.get('contract_id',contract.get('id','R9-FCI-BO-QUENCH-RESPONSE-v1')))
    for c in cases:
        if args.fci_tol is not None:c['fci_tol']=args.fci_tol
        if args.residual_tol is not None:c['residual_tol']=args.residual_tol
        if args.label:c['id']+='_'+args.label
    dump(args.out/'case_deck.json',cases)
    # Root decides concurrency; ThreadPool merely supervises isolated native workers.
    import concurrent.futures
    started=time.monotonic()
    import threading
    active={};active_lock=threading.Lock()
    def rss_kib(pid):
        try:
            text=Path(f'/proc/{pid}/status').read_text()
            return next(int(line.split()[1]) for line in text.splitlines() if line.startswith('VmRSS:'))
        except (OSError,StopIteration):return 0
    def launch(c):
        out=args.out/c['id'];out.mkdir(parents=True,exist_ok=True)
        if (out/'receipt.json').exists():return {'case':c['id'],'status':'existing_preserved'}
        if time.monotonic()-started>args.family_wall_s:return {'case':c['id'],'status':'family_wall_deferred'}
        casefile=out/'input.json';dump(casefile,c);env=os.environ|{'OMP_NUM_THREADS':str(args.threads),'OPENBLAS_NUM_THREADS':'1','MKL_NUM_THREADS':'1','NUMEXPR_NUM_THREADS':'1'}
        command=[sys.executable,str(Path(__file__).resolve()),'case','--case-file',str(casefile),'--out',str(out)];dump(out/'launch.json',{'command':command,'case_sha256':sha(casefile),'source_sha256':sha(__file__),'wall_limit_s':args.wall_s or (1800 if args.mode=='pilot' else 7200)})
        with (out/'stdout.log').open('w') as stdout,(out/'stderr.log').open('w') as stderr:
            proc=subprocess.Popen(command,env=env,stdout=stdout,stderr=stderr);wall_start=time.monotonic();peak=0;stop_reason=None
            with active_lock:active[proc.pid]=c['id']
            while proc.poll() is None:
                own=rss_kib(proc.pid);peak=max(peak,own)
                with active_lock:aggregate=sum(rss_kib(pid) for pid in active)+resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
                mem=Path('/proc/meminfo').read_text();available=next(int(line.split()[1]) for line in mem.splitlines() if line.startswith('MemAvailable:'))/1024**2
                if time.monotonic()-wall_start>(args.wall_s or (1800 if args.mode=='pilot' else 7200)):stop_reason='wall_deferred'
                elif time.monotonic()-started>args.family_wall_s:stop_reason='family_wall_deferred'
                elif own>args.memory_gib*1024**2:stop_reason='memory_cap_stopped'
                elif aggregate>min(args.memory_cap_gib,96)*1024**2:stop_reason='aggregate_memory_cap_stopped'
                elif available<20:stop_reason='host_headroom_stopped'
                if stop_reason:proc.kill();break
                time.sleep(.5)
            rc=proc.wait()
            with active_lock:active.pop(proc.pid,None)
        if stop_reason:rc=124 if 'wall' in stop_reason else 137
        if not (out/'receipt.json').exists():dump(out/'receipt.json',{'case':c,'status':'wall_deferred' if rc==124 else 'worker_failed','exit_code':rc,'implementation_checked':False,'finite_model_numerics_passed':False,'basis_target_met':None})
        r=json.loads((out/'receipt.json').read_text());r.update(supervisor_peak_rss_kib=peak,supervisor_stop_reason=stop_reason,executed_command=command,input_sha256=sha(casefile));dump(out/'receipt.json',r)
        return {'case':c['id'],'exit_code':rc}
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        for result in pool.map(launch,cases):print(json.dumps(result),flush=True)
    dump(args.out/'run_manifest.json',{'case_count':len(cases),'wall_s':time.monotonic()-started,'contract_sha256':sha(args.contract),'source_sha256':sha(__file__)})
    return 0

if __name__=='__main__':sys.exit(main())
