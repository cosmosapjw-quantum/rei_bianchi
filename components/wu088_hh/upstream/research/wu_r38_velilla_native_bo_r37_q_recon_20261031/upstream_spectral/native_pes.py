"""R38 native Velilla PES (2008) isotope-dependent diatomic BO asymptote study.

Scientific boundary: source h3plus.f evaluates clamped-nuclei PES, NOT isotope
reaction dynamics or state-to-state reaction rates. Nuclear rovibrational energy
is calculated independently using bare nucleus masses and the native H2 curve.
"""
from __future__ import annotations
import argparse, csv, ctypes, hashlib, json, math, re, subprocess, sys
from itertools import permutations
from pathlib import Path
import numpy as np
from scipy.linalg import eigh_tridiagonal
from scipy.fft import dst, idst
from scipy.sparse.linalg import LinearOperator, eigsh
from scipy.optimize import minimize_scalar
from scipy.special import gammaincc

HARTREE_TO_EV = 27.211386245981
HARTREE_TO_CM = 219474.6313632
HARTREE_TO_K = 315775.024804  # E_h/k_B
MP_ME = 1836.152673426  # NIST CODATA 2022
MD_ME = 3670.482967655  # NIST CODATA 2022
MU_H2 = MP_ME / 2
MU_HD = MP_ME * MD_ME / (MP_ME + MD_ME)
ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SOURCE_SHA = '8dbf8b7e3852d02504ba92317f79593051d689f1357263ac0891a3a24084ed8c'
R37_SOURCE_SHA = '4ea1e3e725cdc7d181ad2c155a2184b23de6c70b41b31ddcfda596277cf0a1a0'

class NativeVelilla:
    def __init__(self, library: Path):
        self.lib = ctypes.CDLL(str(library.resolve()))
        self.lib.h2_.argtypes = [ctypes.POINTER(ctypes.c_double)]
        self.lib.h2_.restype = ctypes.c_double
        self.lib.dimh3p_.argtypes = [ctypes.POINTER(ctypes.c_double)] * 6
        self.lib.dimh3p_.restype = None

    def h2(self, r: float) -> float:
        if r <= 0 or not math.isfinite(r):
            raise ValueError('invalid bond length')
        x = ctypes.c_double(r)
        return self.lib.h2_(ctypes.byref(x))

    def h3(self, a: float, b: float, c: float) -> tuple[float,float,float]:
        if min(a,b,c) <= 0 or max(a,b,c) >= (a+b+c)-max(a,b,c):
            raise ValueError('invalid triangle geometry')
        args = [ctypes.c_double(z) for z in [a,b,c,0.,0.,0.]]
        self.lib.dimh3p_(*[ctypes.byref(z) for z in args])
        values = tuple(z.value for z in args[3:])
        if not all(map(math.isfinite, values)):
            raise ArithmeticError('nonfinite native potential')
        return values


def assert_input_source(source: Path) -> None:
    sha = hashlib.sha256(source.read_bytes()).hexdigest()
    if sha != EXPECTED_SOURCE_SHA:
        raise ValueError(f'native Fortran source identity conflict {sha}')


def compile_native(source: Path, output: Path) -> dict:
    assert_input_source(source)
    output.parent.mkdir(parents=True,exist_ok=True)
    cmd=['gfortran','-std=legacy','-O2','-fPIC','-ffixed-line-length-none','-shared',str(source),'-llapack','-lblas','-o',str(output)]
    r=subprocess.run(cmd,text=True,capture_output=True)
    if r.returncode != 0: raise RuntimeError(r.stderr)
    return {'command':cmd,'stderr':r.stderr,'returncode':r.returncode,
            'binary_sha256':hashlib.sha256(output.read_bytes()).hexdigest()}


def rovib_levels(pes: NativeVelilla, mu: float, states: list[tuple[int,int]], step: float=0.01,
                 rmin: float=0.60,rmax: float=16.0) -> dict[tuple[int,int],float]:
    """Dirichlet 1D radial diatomic Schrodinger equation, energy relative to separated atoms.

    u(0)=u(infinity)=0, H = -1/(2mu) d^2/dr^2+J(J+1)/(2mu r^2)+V_native(r)+1.
    Bohr, Hartree, electron mass atomic units. No other approximations to native H2 PES.
    """
    n=int(round((rmax-rmin)/step))-1
    h=(rmax-rmin)/(n+1)
    r=rmin+(np.arange(n)+1)*h
    V=np.array([pes.h2(float(x))+1.0 for x in r])
    off=np.full(n-1,-1/(2*mu*h*h),dtype=float)
    out={}
    for J in sorted(set(J for _,J in states)):
        target_v=max(v for v,j in states if j==J)
        diag=V+1/(mu*h*h)+J*(J+1)/(2*mu*r*r)
        ew=eigh_tridiagonal(diag,off,select='i',select_range=(0,target_v),eigvals_only=True,check_finite=True)
        for v,j in states:
            if j==J: out[v,J]=float(ew[v])
    return out


def rovib_levels_spectral(pes: NativeVelilla, mu: float, states: list[tuple[int,int]],
                          N: int=2500, rmin: float=.60, rmax: float=16.) -> dict[tuple[int,int],float]:
    """Independent sine-pseudospectral BO radial Hamiltonian; boundary Dirichlet.
    Original native H2 curve only; not the full three-body isotope scattering problem.
    """
    L=rmax-rmin
    rr=rmin+L*np.arange(1,N+1)/(N+1)
    V=np.array([pes.h2(float(x))+1.0 for x in rr])
    kinetic=(np.pi*np.arange(1,N+1)/L)**2/(2*mu)
    out={}
    for J in sorted({j for _,j in states}):
        vpot=V+J*(J+1)/(2*mu*rr*rr)
        def matvec(x):
            return idst(kinetic*dst(x,type=1,norm='ortho'),type=1,norm='ortho')+vpot*x
        h=LinearOperator((N,N),matvec=matvec,dtype=float)
        k=max(v for v,j in states if j==J)+2
        initial=np.exp(-0.5*((rr-1.5)/0.25)**2)
        w=np.sort(eigsh(h,k=k,which='SA',tol=1e-12,maxiter=20000,
                         v0=initial,return_eigenvectors=False))
        for v,j in states:
            if j==J:out[v,J]=float(w[v])
    return out


def write_csv(path: Path, header: list[str], rows: list[dict]):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=header,lineterminator='\n');w.writeheader();w.writerows(rows)


def get_emaa_temperatures(radex: Path) -> list[float]:
    lines=radex.read_text().splitlines()
    for i,line in enumerate(lines):
        if line.startswith('! COLLISIONS BETWEEN') and i+1<len(lines) and lines[i+1].lstrip().startswith('7 '):
            for j in range(i+1, min(i+12,len(lines))):
                if lines[j].strip()=='! TEMPERATURES':
                    vals=[float(x) for x in lines[j+1].split()]
                    if len(vals)!=25:raise ValueError('EMAA temp count not 25')
                    return vals
    raise ValueError('no authenticated proton EMAA temperature grid')


def jacobi_sides(r: float,R: float, cos_theta: float):
    return (r, math.sqrt(R*R+r*r/4+R*r*cos_theta),
                math.sqrt(R*R+r*r/4-R*r*cos_theta))


def gl_printed_joins(thresholds:list[dict], gl_path:Path, output:Path)->dict:
    """Cross source BO kinematic thresholds with safe GL2022 printed rates.
    Exclusions: J_i=5 duplicated source row, T=15 zero notation, T=2505 exponent.
    These are printed SQM rates, NOT a recalculation of the scattering amplitudes.
    """
    gl=json.loads(gl_path.read_text())
    if gl['shape'] != [10,7,10] or len(gl['tokens_jprime_j_T'])!=10:
        raise ValueError('GL source dimensions changed')
    dictionary={(int(t['HD_v']),int(t['HD_J']),int(t['H2_v']),int(t['H2_J'])):t for t in thresholds}
    safe_t=[55,105,255,505,1005,1505,2005,3005]
    temps=gl['temperature_nodes_K']
    details=[]; aggregates=[]
    for ji in (0,1,2,3,4,6):
        for T in safe_t:
            selected=[]
            for jf in range(10):
                tok=gl['tokens_jprime_j_T'][jf][ji][temps.index(T)]
                match=re.fullmatch(r'(\d*\.?\d+)\((\d+)\)',str(tok).strip())
                if not match or float(match.group(1))==0:
                    raise ValueError(f'invalid or zero-ambiguous GL token j={ji},jp={jf},T={T}: {tok}')
                rate=float(match.group(1))*10.**(-int(match.group(2)))
                th=dictionary[(0,ji,0,jf)]
                entry={'HD_J':ji,'H2_J':jf,'T_K':T,'GL_printed_rate_cm3_s':f'{rate:.12e}',
                       'BO_threshold_K':th['threshold_K'],'BO_exothermic':th['exo_at_zero_energy'],
                       'GL_original_source_token':tok}
                details.append(entry);selected.append((rate,th))
            total=sum(r for r,th in selected)
            endo=sum(r for r,th in selected if th['exo_at_zero_energy']==0)
            thermal_threshold=sum(r*float(th['threshold_K']) for r,th in selected)/total
            aggregates.append({'HD_J':ji,'T_K':T,'total_printed_SQM_rate_cm3_s':f'{total:.12e}',
                               'endothermic_channel_printed_rate_fraction':f'{endo/total:.12e}',
                               'rate_weighted_positive_threshold_K':f'{thermal_threshold:.12e}',
                               'included_final_J_count':10})
    write_csv(output/'GL2022_NATIVE_BO_RATE_JOIN_480.csv',list(details[0]),details)
    write_csv(output/'GL2022_NATIVE_BO_RATE_PARTITIONS_48.csv',list(aggregates[0]),aggregates)
    return {'original_SQM_join_rows':len(details),'rate_partition_rows':len(aggregates),
            'GL_selected_HD_J':[0,1,2,3,4,6],'GL_selected_T_K':safe_t,
            'source_gl_rate_semantics':'printed_SQM_not_new_scattering'}


def generate(pes: NativeVelilla, radex: Path, output: Path, gl_path:Path|None=None) -> dict:
    output.mkdir(parents=True,exist_ok=True)
    temps=get_emaa_temperatures(radex)
    Hdstates=[(0,j) for j in range(12)]+[(1,j) for j in range(7)]
    H2states=[(0,j) for j in range(10)]+[(1,j) for j in range(3)]
    Hdstates=list(dict.fromkeys(Hdstates));H2states=list(dict.fromkeys(H2states))
    hd=rovib_levels_spectral(pes,MU_HD,Hdstates)
    h2=rovib_levels_spectral(pes,MU_H2,H2states)
    levels=[]
    for (v,j),energy in sorted(hd.items()):
        levels.append({'molecule':'HD','v':v,'J':j,'energy_hartree':f'{energy:.16e}',
                      'energy_cm1':f'{energy*HARTREE_TO_CM:.10f}'})
    for (v,j),energy in sorted(h2.items()):
        levels.append({'molecule':'H2','v':v,'J':j,'energy_hartree':f'{energy:.16e}',
                      'energy_cm1':f'{energy*HARTREE_TO_CM:.10f}'})
    write_csv(output/'DIATOMIC_BO_LEVELS_32.csv',list(levels[0]),levels)
    thresholds=[];tails=[]
    for vi,ji in Hdstates:
        for vf,jf in H2states:
            delta=h2[(vf,jf)]-hd[(vi,ji)]
            threshold=max(0.,delta)
            pair=f'HD_{vi}_{ji}__H2_{vf}_{jf}'
            thresholds.append({'pair':pair,'HD_v':vi,'HD_J':ji,'H2_v':vf,'H2_J':jf,
                               'delta_E_hartree':f'{delta:.16e}',
                               'threshold_K':f'{threshold*HARTREE_TO_K:.16e}',
                               'threshold_cm1':f'{threshold*HARTREE_TO_CM:.10f}',
                               'Q_eV':f'{-delta*HARTREE_TO_EV:.12e}',
                               'exo_at_zero_energy':int(delta<=0),
                               'GL2022_reactive_v0_source_pair':int(vi==0 and ji<=8 and vf==0 and jf<=9)})
            for T in temps:
                # Maxwell kinetic-energy *probability* P(Ecoll>=threshold). Not a reaction rate.
                tail=float(gammaincc(1.5,threshold*HARTREE_TO_K/T))
                tails.append({'pair':pair,'T_K':f'{T:.1f}','threshold_K':f'{threshold*HARTREE_TO_K:.16e}',
                              'maxwell_energy_tail_probability':f'{tail:.15e}',
                              'GL2022_reactive_v0_source_pair':int(vi==0 and ji<=8 and vf==0 and jf<=9)})
    write_csv(output/'BO_ISOTOPE_THRESHOLDS_247.csv',list(thresholds[0]),thresholds)
    write_csv(output/'MAXWELL_KINEMATIC_TAIL_6175.csv',list(tails[0]),tails)
    geometries=[]
    for r in (1.2,1.4,1.65,1.85,2.1,2.4):
        for R in (2.4,3.,4.,5.,7.,10.,14.,20.,35.,60.):
            for cos_theta in (-0.95,-0.5,0.0,0.5,0.95):
                a,b,c=jacobi_sides(r,R,cos_theta)
                E=pes.h3(a,b,c)[0]
                geometries.append({'bond_r_a0':f'{r:.4f}','Jacobi_R_a0':f'{R:.4f}',
                                   'cos_theta':f'{cos_theta:.2f}',
                                   'native_ground_E_hartree':f'{E:.16e}',
                                   'source_h2_E_hartree':f'{pes.h2(r):.16e}',
                                   'interaction_cm1':f'{(E-pes.h2(r))*HARTREE_TO_CM:.11e}'})
    write_csv(output/'NATIVE_PES_GEOMETRY_300.csv',list(geometries[0]),geometries)
    h3min=minimize_scalar(lambda r:pes.h3(r,r,r)[0],bounds=(1.4,1.9),method='bounded',options={'xatol':1e-12})
    h2min=minimize_scalar(lambda r:pes.h2(r),bounds=(1.2,1.65),method='bounded',options={'xatol':1e-12})
    bomaxdiff=(h2[(0,0)]-hd[(0,0)])
    # ground-to-ground endothermic reaction threshold Q: E_HD - E_H2 = -delta.
    results={'unit':'WU_R38_VELILLA_NATIVE_PES_AND_BO_ISOTOPE_THRESHOLDS','native_pes':'ORIGINAL_VELILLA_2008_FORTRAN',
             'original_PES_SHA256':EXPECTED_SOURCE_SHA,'temperature_input':'EMAA_original_HD_Hplus_25nodes',
             'R37_parent_SHA256':R37_SOURCE_SHA,
             'mp_me_CODATA2022':MP_ME,'md_me_CODATA2022':MD_ME,'mu_H2_me':MU_H2,'mu_HD_me':MU_HD,
             'radial_solver':'sine_pseudospectral_Dirichlet_0.60_to_16.0_bohr_N2500',
             'h2_electronic_equilibrium_r_bohr':float(h2min.x),
             'h2_electronic_equilibrium_E_hartree':float(h2min.fun),
             'h3_equilateral_min_r_bohr':float(h3min.x),
             'h3_equilateral_min_E_hartree':float(h3min.fun),
             'electronic_PES_depth_cm1':float((h2min.fun-h3min.fun)*HARTREE_TO_CM),
             'H2_ground_E_relative_separated_atom_hartree':h2[(0,0)],
             'HD_ground_E_relative_separated_atom_hartree':hd[(0,0)],
             'HD_v0J0_to_H2_v0J0_endothermic_threshold_K':float(bomaxdiff*HARTREE_TO_K),
             'HD_v0J0_to_H2_v0J0_endothermic_threshold_eV':float(bomaxdiff*HARTREE_TO_EV),
             'HD_v0J0_to_H2_v0J0_endothermic_threshold_cm1':float(bomaxdiff*HARTREE_TO_CM),
             'energy_levels':len(levels),'kinematic_threshold_pairs':len(thresholds),'maxwell_tail_rows':len(tails),
             'native_geometry_rows':len(geometries),
             'rate_input_unchanged':True,'PES_NATIVE_THRESHOLD_GATE':'PARTIAL_BO_DIATOMIC_ONLY',
             'PHYSICAL_Q_GATE':'HOLD_FULL_REACTION',
             'PES_full_mass_dependent_scattering':'NOT_RUN',
             'canonical_DAG':'34/49_UNCHANGED','distinct_author_R6_C9':'NOT_RUN'}
    if gl_path:
        results.update(gl_printed_joins(thresholds,gl_path,output))
    (output/'SUMMARY.json').write_text(json.dumps(results,indent=2,sort_keys=True,ensure_ascii=False)+'\n',encoding='utf-8')
    return results


def main():
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True)
    p.add_argument('--radex',type=Path,required=True);p.add_argument('--gl',type=Path);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--library',type=Path,default=ROOT/'build'/'libvelilla_h3plus.so')
    a=p.parse_args();print(json.dumps(compile_native(a.source,a.library),ensure_ascii=False))
    pes=NativeVelilla(a.library);print(json.dumps(generate(pes,a.radex,a.out,a.gl),indent=2,ensure_ascii=False))
if __name__=='__main__':main()
