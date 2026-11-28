"""Separate full signed and reduced amplitude DOP853 at fixed worst query."""
import argparse, json, math, pathlib
import numpy as np
from scipy.integrate import solve_ivp
from scipy.linalg import expm
from reduced_parity import reduced_dop853
from run_equivalence import atomic


def signed_operators(l):
    m=np.arange(-l,l+1)
    plus=np.zeros((2*l+1,2*l+1),complex)
    for i,x in enumerate(m[:-1]):plus[i+1,i]=math.sqrt(l*(l+1)-x*(x+1))
    minus=plus.conj().T
    lx=(plus+minus)/2
    ly=(plus-minus)/(2j)
    lz=np.diag(m).astype(complex)
    return m,lx,ly,lz


def full_signed_dop(N,l,E,rho,cut,trajectory):
    m,lx,ly,lz=signed_operators(l)
    v=math.sqrt(2*E/(27.07*1.836153))
    eps=6*1*2*3**2/(N**3*l*(l+1)*(2*l-1)*(2*l+1)*(2*l+3))
    if trajectory=='COULOMB':
        a=2/(.8*1836.153*v*v);b=math.hypot(a,rho)
        bound=math.acosh((cut-a)/b)
        def h(s):
            R=a+b*math.cosh(s)
            return eps*R**3/v*(lx@lx)-rho/R*lz
    else:
        xbound=math.sqrt(cut*cut-rho*rho)
        bound=xbound
        def h(x):
            R2=rho*rho+x*x
            return eps*R2/v*(lx@lx)-rho/R2*lz
    dim=2*l+1
    def rhs(s,y):return (-1j*h(s)@y.reshape(dim,dim)).ravel()
    sol=solve_ivp(rhs,(-bound,bound),np.eye(dim,dtype=complex).ravel(),
                  method='DOP853',rtol=1e-12,atol=1e-14)
    if not sol.success:raise ArithmeticError(sol.message)
    U=sol.y[:,-1].reshape(dim,dim)
    V=expm(-1j*math.pi/2*ly)
    map_lx=float(np.max(abs(V.conj().T@lx@V-lz)))
    map_lz=float(np.max(abs(V.conj().T@lz@V+lx)))
    Ux=V.conj().T@U@V
    D=np.diag((-1.)**m)
    Ug=D.conj().T@Ux@D
    even=np.zeros((dim,l+1),complex);odd=np.zeros((dim,l),complex)
    even[l,0]=1
    for k in range(1,l+1):
        even[l+k,k]=even[l-k,k]=1/math.sqrt(2)
        odd[l+k,k-1]=1/math.sqrt(2);odd[l-k,k-1]=-1/math.sqrt(2)
    Ueven=even.conj().T@Ug@even
    Uodd=odd.conj().T@Ug@odd
    Ps=abs(Ux)**2
    C=(abs(m)[None,:]==np.arange(l+1)[:,None]).astype(float)
    Pclean=(C@Ps@C.T)/C.sum(1)[None,None,:]
    return {'U_even':Ueven,'U_odd':Uodd,'P_clean':Pclean,'P_even':abs(Ueven)**2,
            'nfev':sol.nfev,'unitarity_defect':float(np.max(abs(U.conj().T@U-np.eye(dim)))),
            'gauge_Lx_difference':map_lx,'gauge_Lz_difference':map_lz,
            'parity_cross_amplitude':float(max(np.max(abs(even.conj().T@Ug@odd)),np.max(abs(odd.conj().T@Ug@even))))}


def main(out,results):
    rows=json.loads(pathlib.Path(results).read_text())['records']
    i=max(range(len(rows)),key=lambda k:rows[k]['max_probability_difference'])
    q=rows[i];N,l,E,rho=q['N'],q['l'],q['energy_keV_u'],float.fromhex(q['rho_hex'])
    cut=((l+.5)**2-(.5 if q['cutoff']=='CPC' else 0))/3
    full=full_signed_dop(N,l,E,rho,cut,q['trajectory'])
    red=reduced_dop853(N,l,E,rho,trajectory=q['trajectory'],cutoff=q['cutoff'])
    result={'schema':'bass_he.r10i.worst_amplitude_audit.v1',
            'query':{k:q[k] for k in ('trajectory','cutoff','energy_keV_u','N','l','rho_hex')},
            'clean_full_dop_nfev':full['nfev'],'reduced_dop_nfev':red['nfev'],
            'clean_full_dop_unitarity_defect':full['unitarity_defect'],
            'reduced_dop_unitarity_defect':red['unitarity_defect'],
            'gauge_Lx_difference':full['gauge_Lx_difference'],'gauge_Lz_difference':full['gauge_Lz_difference'],
            'parity_cross_amplitude':full['parity_cross_amplitude'],
            'max_even_amplitude_difference':float(np.max(abs(full['U_even']-red['U_even']))),
            'max_clean_probability_difference_from_high_resolution':float(np.max(abs(full['P_clean']-np.array(q['clean_collapsed_probability'])))),
            'max_author_probability_difference_from_high_resolution':float(np.max(abs(red['P']-np.array(q['author_reduced_probability'])))),
            'dop_max_author_clean_difference':float(np.max(abs(red['P']-full['P_clean']))),
            'author_even_probability':red['P'].tolist(),'clean_collapsed_probability':full['P_clean'].tolist(),
            'DOP853_not_independent_physical_validation':True}
    assert result['max_even_amplitude_difference']<1e-8
    assert result['max_clean_probability_difference_from_high_resolution']<1e-8
    assert result['max_author_probability_difference_from_high_resolution']<1e-8
    assert result['clean_full_dop_unitarity_defect']<5e-13
    assert result['reduced_dop_unitarity_defect']<5e-13
    atomic(out,result)
    print(json.dumps({k:result[k] for k in ('max_even_amplitude_difference','max_clean_probability_difference_from_high_resolution',
                      'max_author_probability_difference_from_high_resolution','dop_max_author_clean_difference',
                      'clean_full_dop_unitarity_defect','reduced_dop_unitarity_defect','parity_cross_amplitude')},indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--results',required=True);a=p.parse_args()
    main(a.out,a.results)
