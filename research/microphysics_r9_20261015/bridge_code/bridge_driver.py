#!/usr/bin/env python3
"""Frozen R9 bridge. stdlib Python + C11/libm; no networking.
Run --r8 R8_ROOT --photo PHOTO_DAT --out RESULTS once to stage inputs.
Later standalone runs need only --out RESULTS.
Reconstructed from the earlier executed scratch implementation after scratch
exec-server outage. Numerical repair: photo4096, source2048, reference16384.
"""
import argparse, csv, ctypes, hashlib, json, math, os, platform, re, resource
import shutil, socket, subprocess, sys, time
from pathlib import Path
HERE=Path(__file__).resolve().parent
INPUTS=HERE/'inputs'
EV=1.602176634e-19
KB=1.380649e-23
MPC=3.0856775814913673e22
TS=[.001,.01,1.,2.7255,6.109701377331961,100.,1e4,1e6,1e7,1e8]
PHOTO_SHA='a53e73b0af4cc6b801aef67b84bd964e3ed8c9c4992f214e4a69dc7e4443f389'
X_HII=.000210349192936

def jwrite(p,v):p.write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def cwrite(p,rows):
    with p.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def readcsv(name):
    with (INPUTS/name).open(newline='') as f:return list(csv.DictReader(f))
def az(k):
    if k=='n':return 1,0
    if k=='p':return 1,1
    m=re.fullmatch(r'([A-Z][a-z]?)([0-9]+)',k)
    return int(m[2]),dict(H=1,He=2,Li=3,Be=4,B=5,C=6,N=7,O=8,F=9,Ne=10,Na=11)[m[1]]
def stage(r8,photo):
    INPUTS.mkdir(exist_ok=True)
    names={'transitions.csv':'hydrogenic/transitions.csv','cascade.csv':'hydrogenic/cascade.csv',
           'line_yields.csv':'hydrogenic/line_yields.csv','np_kernel.c':'nuclear/np_kernel.c',
           'np_kernel.h':'nuclear/np_kernel.h',
           'R5_DONOR_BBN.json':'local_codex/vendor_r6/evidence/nuclear/inputs/R5_DONOR_BBN.json'}
    if r8:
        for name,suffix in names.items():
            matches=[p for p in r8.rglob(name) if str(p).endswith(suffix)]
            if len(matches)!=1:raise ValueError(('ambiguous/missing R8 input',name,[str(p) for p in matches]))
            shutil.copy2(matches[0],INPUTS/name)
    if photo:shutil.copy2(photo,INPUTS/'photo.dat')
    if hashlib.sha256((INPUTS/'photo.dat').read_bytes()).hexdigest()!=PHOTO_SHA:
        raise ValueError('immutable Verner photo.dat identity mismatch')

def inventory(out):
    d=json.loads((INPUTS/'R5_DONOR_BBN.json').read_text());y=d['result']['Y_final'];x=X_HII
    chosen=[('n',[1.]),('p',[1-x,x]),('H2',[1-x,x]),('H3',[1-x,x]),
            ('He3',[1.,0.,0.]),('He4',[1.,0.,0.]),('Li7',[0.,1.,0.,0.])]
    labels=['n','H1_0','H1_1','D_0','D_1','T_0','T_1','He3_0','He3_1','He3_2',
            'He4_0','He4_1','He4_2','Li7_0','Li7_1','Li7_2','Li7_3']
    nb=d['constants_and_normalization']['nb0_cm^-3']*1e6*21**3
    rows=[]
    for k,probs in chosen:
        a,z=az(k)
        for q,p in enumerate(probs):
            rows.append(dict(state=labels[len(rows)],nuclide=k,A=a,Z=z,q=q,charge_probability=p,
              Y_per_donor_baryon=y[k]*p,conditional_density_z20_m3=nb*y[k]*p,
              zero_reason='exact selected charge probability zero' if p==0 else ''))
    omitted=[dict(nuclide=k,A=az(k)[0],Z=az(k)[1],Y_per_donor_baryon=v,
               AY_per_donor_baryon=az(k)[0]*v,ZY_per_donor_baryon=az(k)[1]*v,assigned_charge=None)
             for k,v in y.items() if k not in dict(chosen)]
    bf=math.fsum(az(k)[0]*v for k,v in y.items());zf=math.fsum(az(k)[1]*v for k,v in y.items())
    bt=math.fsum(r['A']*r['Y_per_donor_baryon'] for r in rows)
    zt=math.fsum(r['Z']*r['Y_per_donor_baryon'] for r in rows)
    bo=math.fsum(r['AY_per_donor_baryon'] for r in omitted);zo=math.fsum(r['ZY_per_donor_baryon'] for r in omitted)
    ef=math.fsum(r['q']*r['Y_per_donor_baryon'] for r in rows)
    eb=math.fsum((r['Z']-r['q'])*r['Y_per_donor_baryon'] for r in rows)
    heavy=math.fsum(r['Y_per_donor_baryon'] for r in rows)
    result=dict(scope='unchanged historical BBN endpoint inventory; selected conditional z20 ionic map; no evolution',
      registry_size=17,native_registry_size=13,input_endpoint=d['endpoint'],conditional_nb_z20_m3=nb,
      charge_assignment=dict(H_D_T='selected H-equality REC fraction',HII_fraction=x,He3_He4='neutral',Li7='singly ionized'),
      normalization='no renormalization of full or tracked inventory',Be7_policy='excluded reservoir; no decay or Li transfer',
      full_input_baryons=bf,full_input_minus_one=bf-1,tracked_baryons=bt,omitted_baryons=bo,
      baryon_map_residual=bt+bo-bf,full_input_nuclear_charge=zf,tracked_nuclear_charge=zt,
      omitted_nuclear_charge=zo,nuclear_charge_map_residual=zt+zo-zf,
      tracked_free_electrons_per_donor_baryon=ef,tracked_bound_electrons_per_donor_baryon=eb,
      tracked_electron_charge_residual=ef+eb-zt,tracked_heavy_particles_per_donor_baryon=heavy,
      conditional_tracked_thermal_particle_density_m3=nb*(heavy+ef),
      eos_convention='common ideal gas; no positrons; all tracked free electrons thermal',
      max_isotope_sum_relative=max(abs(math.fsum(r['Y_per_donor_baryon'] for r in rows if r['nuclide']==k)/y[k]-1) for k,_ in chosen),
      helium_normalization_diagnostic=dict(donor_He4_over_p=y['He4']/y['p'],donor_He3_over_p=y['He3']/y['p'],
          PR150_REC_fHe_source=.08188416223421702,REI_fHe=.08130135170951498),
      legacy_hhe_projection='REJECTED: nonzero D/T/He3/Li7 unsupported',omitted_electronic_charge=None,
      full_charge_state_history=None,omitted_reservoir=omitted)
    cwrite(out/'inventory17.csv',rows);jwrite(out/'inventory17.json',result)
    return result

def shape(e):return e*e/math.expm1(e/(KB/EV*50000.))
def simpson(lo,hi,n,m):
    h=(hi-lo)/n
    return h/3*math.fsum((1 if i in (0,n) else 4 if i%2 else 2)*shape(lo+i*h)*(lo+i*h)**m for i in range(n+1))
def response(lo,hi,n,row,ref):
    z,ne,eth,emax,e0,s0,ya,p,yw,y0,y1=row
    if (z,ne)!=(3,3) or lo<eth or hi>emax:raise ValueError('LiI single-fit support violation')
    h=(hi-lo)/n;terms=[[],[],[]]
    for i in range(n+1):
        e=lo+i*h;x=e/e0-y0;y=math.hypot(x,y1)
        sigma=s0*((x-1)**2+yw*yw)*y**(.5*p-5.5)*(1+math.sqrt(y/ya))**(-p)*1e-22
        v=(1 if i in (0,n) else 4 if i%2 else 2)*h/3*shape(e)*sigma/ref
        terms[0].append(v);terms[1].append(v*(e-eth)*EV);terms[2].append(v*e*EV)
    g,heat,absorbed=[math.fsum(t) for t in terms];bind=g*eth*EV
    return dict(Gamma_s_inverse=g,heating_J_s_per_LiI=heat,absorbed_energy_J_s_per_LiI=absorbed,
        binding_energy_J_s_per_LiI=bind,energy_identity_residual_J_s=absorbed-heat-bind,
        energy_identity_relative_residual=(absorbed-heat-bind)/absorbed)

def source(out):
    bands=[('LiI_sub_Lyman',5.392,13.6),('LiI_single_fit_covered',5.392,64.39),('original_H_ionizing',13.6,100.)]
    ref=simpson(13.6,100.,2048,0);spectra=[];births=[];refine=[]
    ly=1/(.00038*.002**.227+.01858)-math.log10(2.55)
    for name,lo,hi in bands:
        vals={n:[simpson(lo,hi,n,m) for m in (0,1)] for n in (64,128,256,512,1024,2048,16384)}
        count,energy=vals[2048]
        spectra.append(dict(band=name,lower_eV=lo,upper_eV=hi,photon_integral_eV3=count,energy_integral_eV4=energy,
          number_ratio_original=count/ref,mean_energy_eV=energy/count,
          photon_1024_to_2048_relative=vals[1024][0]/count-1,energy_1024_to_2048_relative=vals[1024][1]/energy-1,
          photon_2048_to_16384_relative=count/vals[16384][0]-1,energy_2048_to_16384_relative=energy/vals[16384][1]-1))
        for n in (64,128,256,512,1024):
            err=[vals[n][m]/vals[2*n][m]-1 for m in (0,1)]
            refine.append(dict(band=name,coarse_n=n,fine_n=2*n,photon_relative=err[0],energy_relative=err[1],
                passes_1e_minus_10=max(abs(v) for v in err)<=1e-10))
        for z in (4.,6.,10.,15.,20.):
            sfr=.015*(1+z)**2.7/(1+((1+z)/2.9)**5.6);rate=.2*10**ly*sfr*count/ref
            births.append(dict(band=name,z=z,lower_eV=lo,upper_eV=hi,comoving_photons_s_cMpc3=rate,
              proper_photons_s_m3=rate/MPC**3*(1+z)**3,comoving_energy_J_s_cMpc3=rate*energy/count*EV,mean_energy_eV=energy/count))
    table=[[float(v) for v in line.split()] for line in (INPUTS/'photo.dat').read_text().splitlines() if line.strip()]
    li=next(r for r in table if r[:2]==[3.,3.]);photos=[];prefine=[]
    for name,lo,hi in bands[:2]:
        vals={n:response(lo,hi,n,li,ref) for n in (64,128,256,512,1024,2048,4096,16384)}
        photos.append(dict(band=name,lower_eV=lo,upper_eV=hi,**vals[4096],
          Gamma_4096_to_16384_relative=vals[4096]['Gamma_s_inverse']/vals[16384]['Gamma_s_inverse']-1,
          heating_4096_to_16384_relative=vals[4096]['heating_J_s_per_LiI']/vals[16384]['heating_J_s_per_LiI']-1))
        for n in (64,128,256,512,1024,2048):
            prefine.append(dict(band=name,coarse_n=n,fine_n=2*n,
              Gamma_relative=vals[n]['Gamma_s_inverse']/vals[2*n]['Gamma_s_inverse']-1,
              heating_relative=vals[n]['heating_J_s_per_LiI']/vals[2*n]['heating_J_s_per_LiI']-1))
    result=dict(scope='conditional BB50K source extension and LiI response per unit reference incident flux',
      source_id='MD14_Z002_FESC_BB50K_LiBandExtension_R9_V1',original_source_id='MD14_Z002_FESC_BB50K_13P6_100_V1',
      T_K=50000.,escape_fraction=.2,original_number_integral_eV3=ref,authoritative_source_panels=2048,
      authoritative_photo_panels=4096,bands=spectra,quadrature_refinement=refine,
      LiI_photo_response=photos,LiI_photo_response_refinement=prefine,
      reference_incident_photon_flux_m2_s=1.,reference_flux_is_MD14_emissivity=False,
      incident_flux_normalization='F_E=Fref*shape(E)/Iref; photon m^-2 s^-1 eV^-1; reference band13.6--100eV',
      Verner_LiI_row_columns=['Z','N','Eth_eV','Emax_eV','E0_eV','sigma0_Mb','ya','P','yw','y0','y1'],
      Verner_LiI_row=li,Verner_photo_dat_sha256=PHOTO_SHA,
      threshold_precision='5.392eV table heating convention, not isotope binding precision',
      sub_Lyman_fraction_of_covered_Gamma=photos[0]['Gamma_s_inverse']/photos[1]['Gamma_s_inverse'],
      sub_Lyman_fraction_of_covered_heating=photos[0]['heating_J_s_per_LiI']/photos[1]['heating_J_s_per_LiI'],
      transport_or_absorbed_flux=None,cosmological_transport_executed=False,
      photo_above_64_39_eV=None,interpretation='emissivity births and separately prescribed incident spectral response; no solved cosmic flux')
    cwrite(out/'source_band_moments.csv',births);cwrite(out/'LiI_photo_response.csv',photos)
    jwrite(out/'source_band_moments.json',result)
    return result

def cascade(out):
    trans,ys,cs=readcsv('transitions.csv'),readcsv('line_yields.csv'),readcsv('cascade.csv')
    energies={};branches={}
    for r in trans:
        s=r['species'];e=tuple(int(r[k]) for k in ('n_upper','l_upper','n_lower','l_lower'))
        energies.setdefault(s,{})[e]=float(r['photon_eV'])
        branches.setdefault(s,{}).setdefault(e[:2],[]).append((e[2:],float(r['branch_probability'])))
    yields={}
    for r in ys:
        u=(int(r['initial_n']),int(r['initial_l']))
        e=tuple(int(r[k]) for k in ('upper_n','upper_l','lower_n','lower_l'))
        yields.setdefault(u,[]).append((e,float(r['mean_photons_per_initial_atom'])))
    summary={(r['species'],int(r['n']),int(r['l'])):r for r in cs};moments=[];lines=[]
    for s,es in energies.items():
        chi=es[(2,1,1,0)]/.75;terminal={(1,0):(1.,0.),(2,0):(0.,1.)}
        for n in range(2,13):
            for l in range(n):
                if (n,l)==(2,0):continue
                terminal[(n,l)]=tuple(math.fsum(p*terminal[d][j] for d,p in branches[s][(n,l)]) for j in (0,1))
        for n in (3,5,10,12):
            weights={};p2s=[];reservoir=[];counts=[]
            for l in range(n):
                p=(2*l+1)/n**2;r=summary[(s,n,l)]
                p2s.append(p*float(r['P_terminal_2s']));reservoir.append(p*float(r['residual_excitation_eV']))
                counts.append(p*float(r['E1_photon_count']))
                for e,y in yields.get((n,l),[]):weights.setdefault(e,[]).append(p*y)
            wk={e:math.fsum(v) for e,v in weights.items()};count=math.fsum(wk.values())
            energy=math.fsum(w*es[e] for e,w in wk.items());p2=math.fsum(p2s);res=math.fsum(reservoir)
            initial=chi*(1-1/n**2)
            p1=math.fsum((2*l+1)/n**2*terminal[(n,l)][0] for l in range(n))
            p2check=math.fsum((2*l+1)/n**2*terminal[(n,l)][1] for l in range(n))
            moments.append(dict(species=s,n=n,E1_photon_count=count,E1_energy_eV=energy,
              terminal_1s_probability=p1,terminal_2s_probability=p2,terminal_2s_energy_eV=res,
              terminal_probability_residual=p1+p2check-1,terminal_2s_crosscheck_residual=p2check-p2,
              initial_excitation_eV=initial,energy_closure_eV=energy+res-initial,
              energy_closure_over_chi=(energy+res-initial)/chi,photon_crosscheck_residual=count-math.fsum(counts),
              Lyalpha_yield=wk.get((2,1,1,0),0.),Halpha_yield=math.fsum(w for e,w in wk.items() if e[0]==3 and e[2]==2)))
            for e,w in sorted(wk.items()):
                lines.append(dict(species=s,initial_n=n,upper_n=e[0],upper_l=e[1],lower_n=e[2],lower_l=e[3],
                 photon_eV=es[e],mean_photons_per_initial_atom=w,emitted_eV_per_initial_atom=w*es[e]))
    result=dict(scope='statistical fixed-n physical Coulomb E1 spectra; declared bound injection, not recombination capture',
      mixture='p_l=(2l+1)/n^2',n_values=[3,5,10,12],species=list(energies),total_mixtures=len(moments),
      max_energy_closure_over_chi=max(abs(r['energy_closure_over_chi']) for r in moments),
      max_photon_crosscheck_residual=max(abs(r['photon_crosscheck_residual']) for r in moments),
      terminal_2s_policy='separate metastable reservoir, no synthetic photons',two_photon_rate=None,
      two_photon_spectrum=None,continuum_capture=None,LiIII_mass_policy='existing infinite nuclear mass hydrogenic model',
      atomic_scope='finite n<=12 input; nonrelativistic Coulomb; spin and fine structure unresolved',
      mixture_moments=moments)
    cwrite(out/'cascade_mixture_lines.csv',lines);cwrite(out/'cascade_mixture_moments.csv',moments)
    jwrite(out/'cascade_mixture.json',result)
    return result

def nuclear(out):
    so=out/'libnp_bridge.so'
    cmd=['cc','-std=c11','-O3','-Wall','-Wextra','-Wpedantic','-DNP_NO_MAIN','-shared','-fPIC',
         str(INPUTS/'np_kernel.c'),'-lm','-o',str(so)]
    b=subprocess.run(cmd,text=True,capture_output=True,check=True);(out/'nuclear_build.log').write_text(b.stdout+b.stderr)
    lib=ctypes.CDLL(str(so.resolve()))
    lib.np_fit_L.argtypes=[ctypes.c_double];lib.np_fit_L.restype=ctypes.c_double
    lib.np_maxwell.argtypes=[ctypes.c_double,ctypes.c_double,ctypes.c_int];lib.np_maxwell.restype=ctypes.c_double
    anchors=[334.2*.99,334.2,334.2*1.01];fitted=[lib.np_fit_L(a) for a in anchors]
    dL=lib.np_fit_L(335.2)-lib.np_fit_L(334.2);rows=[]
    for t in TS:
        vals={(a,n):lib.np_maxwell(t,L,n) for a,L in zip(anchors,fitted) for n in (32,64,128,256)}
        for a,L in zip(anchors,fitted):
            for n in (32,64,128,256):
                k=vals[(a,n)];base=vals[(334.2,n)]
                derivative=(lib.np_maxwell(t,1.,n)-lib.np_maxwell(t,0.,n))*dL
                if not math.isfinite(k) or k<=0:raise ValueError('nonpositive/nonfinite np result')
                rows.append(dict(T_K=t,anchor_mb=a,L_fm2=L,quadrature_n=n,capture_m3_s=k,
                  relative_to_256=k/vals[(a,256)]-1,relative_to_central_256=k/vals[(334.2,256)]-1,
                  exact_affine_dcapture_danchor_m3_s_per_mb=derivative,central_anchor_elasticity=334.2/base*derivative,
                  scenario_difference_derivative_m3_s_per_mb=(vals[(anchors[2],n)]-vals[(anchors[0],n)])/(.02*334.2),
                  affine_prediction_residual_m3_s=k-(base+derivative*(a-334.2))))
    result=dict(scope='historical Chen--Savage np thermal-anchor sensitivity; no new posterior',
      anchor_scenarios_mb=anchors,L_scenarios_fm2=fitted,dL_danchor_fm2_per_mb=dL,T_K=TS,quadrature_n=[32,64,128,256],
      max_64_vs_256_relative=max(abs(r['relative_to_256']) for r in rows if r['quadrature_n']==64),
      max_128_vs_256_relative=max(abs(r['relative_to_256']) for r in rows if r['quadrature_n']==128),
      uncertainty_covariance=None,model_scope='inherited equal-mass amplitude; E<=1MeV; Maxwell x<=80; no model changes',
      derivative='exact affine L-fit model; independent chosen +/-1 percent scenario difference retained',
      build_command=cmd,raw_rows=len(rows))
    cwrite(out/'np_anchor_sensitivity.csv',rows);jwrite(out/'np_anchor_sensitivity.json',result)
    return result

def main():
    p=argparse.ArgumentParser();p.add_argument('--r8',type=Path);p.add_argument('--photo',type=Path)
    p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    start=time.monotonic();stage(a.r8,a.photo)
    for name,fn in [('inventory17',inventory),('source_band',source),('cascade_mixtures',cascade),('np_sensitivity',nuclear)]:
        fn(a.out)
    receipt=dict(scope='four bounded calculations executed; independent scientific admission pending',global_eight_job_closure=False,
      wall_seconds=time.monotonic()-start,actual_execution_hostname=socket.gethostname(),platform=platform.platform(),
      python_version=sys.version,process_id=os.getpid(),allowed_cpu_count=len(os.sched_getaffinity(0)),
      process_cpu_seconds=time.process_time(),peak_self_rss_kib_linux=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
      driver_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
      input_sha256={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(INPUTS.iterdir()) if f.is_file()},
      reconstruction='scratch implementation rebuilt on authorized desktop after scratch exec-server outage',
      numerical_repair='root-authorized photo4096 versus2048; earlier failed levels retained; physics unchanged',
      floating_point_residual_policy='raw arithmetic residuals; displayed zero may be floating-point cancellation, never a proof of exact physical closure')
    jwrite(a.out/'BRIDGE_EXECUTION.json',receipt);print(json.dumps(receipt))
if __name__=='__main__':main()
