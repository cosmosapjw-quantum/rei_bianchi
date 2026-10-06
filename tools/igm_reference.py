"""Independent manufactured FLRW H/He reference.

Rates are separately transcribed from the pinned Grackle C harness, not imported
from the Rust implementation. No Rust call or trajectory is used in the RHS.
Grackle commit af7939494ce65007887ada7b98d1813df6843346.
Copyright (c) 2013-, Enzo/Grackle development team; Enzo Public License,
retained in rust/rei_microphysics/tests/data/igm_grackle/LICENSE.
"""
import math
import numpy as np

C = 29979245800.0
KB = 1.380649e-16
EV = 1.602176634e-12
G = 6.67430e-8
MP = 1.67262192595e-24
CHI = np.array([13.598434599702,24.587389011,54.41776])
CUTOFF = np.array([13.60,24.59,54.42])
RATE_COLUMNS = ('k1_HI_ci','k3_HeI_ci','k5_HeII_ci','k2_HII_rr','k4_HeII_rr','k6_HeIII_rr','k4_HeII_dr','ceHI','ceHeI_metastable','ceHeII','reHII','reHeII1','reHeIII','reHeII2_raw','brem','k4_total','reHeII2_matched')


def coefficients(t):
    """Literal selected Case-A source expressions, including source floors/caps."""
    if not math.isfinite(t) or not 1 <= t <= 1e6:
        raise ValueError('reference temperature outside [1,1e6] K')
    te = t/11605.0
    l = math.log(te)
    polynomial = lambda terms: math.exp(sum(v*l**i for i,v in enumerate(terms)))
    k1 = polynomial([-32.71396786375,13.53655609057,-5.739328757388,1.563154982022,-.2877056004391,.03482559773736999,-.00263197617559,.0001119543953861,-2.039149852002e-6])
    if te <= .8:
        k1 = max(1e-20,k1)
        k3 = k5 = 1e-20
    else:
        k3 = polynomial([-44.09864886561001,23.91596563469,-10.75323019821,3.058038757198,-.5685118909884001,.06795391233790001,-.005009056101857001,.0002067236157507,-3.649161410833e-6])
        k5 = polynomial([-68.71040990212001,43.93347632635,-18.48066993568,4.701626486759002,-.7692466334492,.08113042097303,-.005324020628287001,.0001975705312221,-3.165581065665e-6])
    rrhe = 3.92e-13 / te**.6353
    drhe = 1.54e-9*(1+.3/math.exp(8.099328789667/te))/(math.exp(40.49664394833662/te)*te**1.5) if te > .8 else 0.0
    k2 = polynomial([-28.61303380689232,-.7241125657826851,-.02026044731984691,-.002380861877349834,-.0003212605213188796,-.00001421502914054107,4.989108920299513e-6,5.755614137575758e-7,-1.856767039775261e-8,-3.071135243196595e-9]) if t > 5500 else rrhe
    k6 = 3.36e-10/math.sqrt(t)/(t/1e3)**.2/(1+(t/1e6)**.7)
    capexp = lambda a: math.exp(-min(math.log(1e30),a/t))
    ceh = 7.5e-19*capexp(118348)/(1+math.sqrt(t/1e5))
    cehe1 = 9.1e-27*capexp(13179)*t**(-.1687)/(1+math.sqrt(t/1e5))
    cehe2 = 5.54e-17*capexp(473638)*t**(-.397)/(1+math.sqrt(t/1e5))
    rh = lambda a: 1.778e-29*t*(2*a/t)**1.965/(1+((2*a/t)/.541)**.502)**2.697
    rrhcool = rh(157807)
    rrhecool = 3e-14*1.3806504e-16*t*(2*285335/t)**.654
    rrhe3cool = 8*rh(631515)
    drcool = 1.24e-13*t**(-1.5)*capexp(470000)*(1+.3*capexp(94000))
    brem = 1.43e-27*math.sqrt(t)*(1.1+.34*math.exp(-(5.5-math.log10(t))**2/3))
    return dict(zip(RATE_COLUMNS,[k1,k3,k5,k2,rrhe,k6,drhe,ceh,cehe1,cehe2,rrhcool,rrhecool,rrhe3cool,drcool,brem,rrhe+drhe,drcool if te>.8 else 0.0]))


def spectral_nodes(lo=13.7, hi=100.0, subdivisions=1):
    """Positive composite Gauss2, split at binding energies AND fit cutoffs.

    The analytic SED normalization is retained, not renormalized to the finite
    quadrature sum: number and energy quadrature errors remain observable.
    """
    if not (0<lo<hi<=50000) or subdivisions<1:
        raise ValueError('invalid spectrum')
    bounds = sorted({lo,hi,*(x for x in (*CHI,*CUTOFF) if lo<x<hi)})
    energies,weights = [],[]
    normalizer = 1/(1/lo-1/hi)
    for lower,upper in zip(bounds,bounds[1:]):
        for j in range(subdivisions):
            a = lower+(upper-lower)*j/subdivisions
            b = lower+(upper-lower)*(j+1)/subdivisions
            half = (b-a)/2
            middle = (b+a)/2
            for sign in (-1,1):
                e = middle+sign*half/math.sqrt(3)
                energies.append(e)
                weights.append(half*normalizer/e**2)
    return np.array(energies),np.array(weights)


def he_ratio(config):
    return config['y_he']/(4*(1-config['y_he']))


def background(config, ln_a):
    a = math.exp(ln_a)
    h = config['h0']*math.sqrt(config['omega_r']/a**4+config['omega_m']/a**3+config['omega_lambda'])
    rho0 = 3*config['h0']**2/(8*math.pi*G)
    nh = (1-config['y_he'])*config['omega_b']*rho0/MP/a**3
    return dict(a=a,z=1/a-1,H=h,nH=nh,nHe=he_ratio(config)*nh,Tcmb=config['tcmb0']/a)


def build_births(config):
    energies,weights = spectral_nodes(config['energy_min_ev'],config['energy_max_ev'],int(config['energy_panels']))
    t0,t1 = -math.log1p(config['z_start']),-math.log1p(config['z_end'])
    panels = int(config['birth_panels'])
    if panels<1 or t0>=t1 or config['source_rate']<0:
        raise ValueError('invalid source history')
    if config['source_rate']==0:
        return np.empty((0,3))
    births = []
    for j in range(panels):
        a = t0+(t1-t0)*j/panels
        b = t0+(t1-t0)*(j+1)/panels
        half = (b-a)/2
        for sign in (-1,1):
            birth = (a+b)/2+sign*half/math.sqrt(3)
            photon_scale = half*config['source_rate']/background(config,birth)['H']
            births.extend((birth,e,photon_scale*w) for e,w in zip(energies,weights))
    if len(births)>config['max_packets']:
        raise ValueError('source exceeds max_packets')
    return np.array(births)


def cross_sections(energies, active_channels=None):
    """Verner et al. 1996 analytic cross section, cm^2.

    If supplied, active_channels is the interval's constant left/right event
    mask. It resolves roundoff exactly at an analytically scheduled crossing;
    it never changes photon energy or a gas state.
    """
    e=np.asarray(energies)
    if np.any(~np.isfinite(e)) or np.any(e<0) or np.any(e>50000):
        raise ValueError('cross-section energy domain')
    table = ((.4298,5.475e4,32.88,2.963,0.,0.,0.),(13.61,949.2,1.469,3.188,2.039,.4434,2.136),(1.720,1.369e4,32.88,2.963,0.,0.,0.))
    out=np.zeros((len(e),3))
    for i,(e0,s0,ya,p,yw,y0,y1) in enumerate(table):
        selected=e>=CUTOFF[i] if active_channels is None else active_channels[:,i]
        x=e[selected]/e0-y0
        y=np.sqrt(x*x+y1*y1)
        out[selected,i] = 1e-18*s0*((x-1)**2+yw*yw)*y**(.5*p-5.5)/(1+np.sqrt(y/ya))**p
    return out


def evaluate(config, ln_a, gas, energies, photons, active_channels=None):
    """Independent proper-time equations and per-H ledger derivatives.

    Nonphysical implicit solver trial vectors are not projected. Physical
    admission is checked on accepted integration states by the driver.
    """
    bg=background(config,ln_a)
    nh,nhhe,h,tcmb=bg['nH'],bg['nHe'],bg['H'],bg['Tcmb']
    f=he_ratio(config)
    x,y,z,w=gas
    electron=x+f*(y+2*z)
    ne=nh*electron
    t=2*w/(3*KB*(1+f+electron))
    r=coefficients(t)
    neutral=np.array([1-x,f*(1-y-z),f*y])
    ions=np.array([x,f*y,f*z])
    sigma=cross_sections(energies,active_channels)
    # Each owner is constructed once, including all competing absorbers.
    owners=(C*nh*sigma*neutral[None,:])*photons[:,None]
    photo=owners.sum(axis=0)
    gamma=C*nh*(sigma*photons[:,None]).sum(axis=0)
    heat=EV*np.sum(owners*(energies[:,None]-CHI))
    photon_dt=-owners.sum(axis=1)
    ci=ne*neutral*np.array([r[k] for k in ('k1_HI_ci','k3_HeI_ci','k5_HeII_ci')])
    rr=ne*ions*np.array([r[k] for k in ('k2_HII_rr','k4_HeII_rr','k6_HeIII_rr')])
    dr=ne*ions[1]*r['k4_HeII_dr']
    net=photo+ci-rr
    net[1]-=dr
    fractions=np.array([net[0],(net[1]-net[2])/f if f else 0,net[2]/f if f else 0])
    rr_sink=ne*ions*np.array([r[k] for k in ('reHII','reHeII1','reHeIII')])
    dr_sink=ne*ions[1]*r['reHeII2_matched']
    ce_pref=np.array([ne*neutral[0],ne*ne*ions[1],ne*ions[1]])
    ce=ce_pref*np.array([r[k] for k in ('ceHI','ceHeI_metastable','ceHeII')])
    freefree=ne*(ions[0]+ions[1]+4*ions[2])*r['brem']
    ci_bind=EV*CHI@ci
    capture=EV*(CHI@rr+CHI[1]*dr)
    radiation=rr_sink.sum()+dr_sink+ce.sum()+freefree
    a_rad=8*math.pi**5*KB**4/(15*(6.62607015e-27)**3*C**3)
    cmb=4*6.6524587051e-25*a_rad*KB/(9.1093837139e-28*C)*electron*tcmb**4*(tcmb-t)
    work=2*h*w
    gas_dt=np.r_[fractions,heat-ci_bind-radiation+cmb-work]
    floor=np.where(np.array([r[k] for k in ('k1_HI_ci','k3_HeI_ci','k5_HeII_ci')])==1e-20,ci,0.) if t/11605<=.8 else np.zeros(3)
    capped=np.where(np.array([118348.,13179.,473638.])/t>math.log(1e30),ce,0.)
    excluded=ne*ions[1]*r['reHeII2_raw'] if t/11605<=.8 else 0.
    return dict(photo_product_underflows=int(np.count_nonzero((sigma>0)&(neutral[None,:]>0)&(photons[:,None]>=np.finfo(float).tiny)&(owners<np.finfo(float).tiny))),owners=owners,gas_dt=gas_dt,photon_dt=photon_dt,opacity=(C*nh*sigma*neutral[None,:]).sum(axis=1),photo=photo,ci=ci,rr=rr,dr=dr,
                escape=capture+radiation,work=work,cmb_reservoir=-cmb,
                redshift=EV*np.dot(energies,photons)*h,ci_floor=floor,ce_cap=capped,
                excluded_dr=excluded,T=t,ne_per_h=electron,Gamma=gamma,bg=bg)


LEDGERS = ['abs_HI','abs_HeI','abs_HeII','ci_HI','ci_HeI','ci_HeII','rr_HII','rr_HeII','rr_HeIII','dr_HeII','escape_E','work_E','cmb_reservoir_E','redshift_E','ci_floor_HI','ci_floor_HeI','ci_floor_HeII','ce_cap_HI_E','ce_cap_HeI_E','ce_cap_HeII_E','excluded_dr_E','elapsed_s']
ENERGY_LEDGERS = {10,11,12,13,17,18,19,20}


def binding(gas,config):
    x,y,z=gas[:3]
    return EV*(CHI[0]*x+he_ratio(config)*(CHI[1]*y+(CHI[1]+CHI[2])*z))


def solve_history(config, output_ln_a=None, method='Radau', rtol=1e-9, atol=1e-12):
    """Solve independent continuously redshifting packet/gas ODEs.

    Positive born packets use optical depth coordinates, N=N_birth exp(-tau),
    mathematically equivalent to count depletion and positivity preserving.
    The empty list represents exactly zero photons. Authoritative optical
    depths/log-counts remain stored when a float readout enters its IEEE tail.
    Explicit conservative count/energy bounds account for those readouts; no
    packet is deleted except at physical cutoff. Approved after explicit count
    Radau trials produced negative roundoff on stiff extinction.

    Births and cutoff crossings are exact prescribed discontinuities. Energies
    are analytic characteristics in every RHS evaluation. The gas energy and
    energy ledgers are internally scaled by one eV for conditioning; external
    units are erg/H. There is no finite-step Rust transport/BE algorithm here.
    """
    from scipy.integrate import solve_ivp
    from scipy.sparse import lil_matrix
    import time
    started=time.monotonic()
    if method not in ('Radau','BDF'):
        raise ValueError('independent stiff method must be Radau or BDF')
    t0,t1=-math.log1p(config['z_start']),-math.log1p(config['z_end'])
    if output_ln_a is None:
        output_ln_a=np.linspace(t0,t1,int(config['output_panels'])+1)
    output_ln_a=np.asarray(output_ln_a,dtype=float)
    if np.any(np.diff(output_ln_a)<=0) or output_ln_a[0]!=t0 or output_ln_a[-1]!=t1:
        raise ValueError('output times must include exact start/end and be increasing')
    births=build_births(config)
    crossing = births[:,0,None]+np.log(births[:,1,None]/CUTOFF[None,:]) if len(births) else np.empty((0,3))
    crossings_in_range=crossing[(crossing>t0)&(crossing<t1)&(crossing>=births[:,0,None])]
    events=sorted(set([t0,t1,*output_ln_a,*births[:,0],*crossings_in_range]))
    f=he_ratio(config)
    initial=np.array([config['x_hii'],config['x_heii'],config['x_heiii'],0.])
    initial[3]=1.5*KB*config['temperature_k']*(1+f+initial[0]+f*(initial[1]+2*initial[2]))
    gas=initial.copy()
    ids=np.array([],dtype=int)
    tau=np.array([])
    ledgers=np.zeros(len(LEDGERS))
    emitted_n=emitted_e=out_n=out_e=0.
    stats=dict(method=method,rtol=rtol,atol=atol,nfev=0,njev=0,nlu=0,steps=0,segments=0,max_active_packets=0,source_packets=len(births),completed=False)
    rows=[]
    output_set=set(output_ln_a)

    tail_seen=set()
    underflow_photo_products=0
    tiny=np.finfo(float).tiny
    max_cnh=C*background(config,t0)['nH']

    def packet_counts(optical_depth,packet_ids,ln_a):
        logs=np.log(births[packet_ids,2])-optical_depth
        tail_seen.update(int(i) for i in packet_ids[logs<math.log(tiny)])
        with np.errstate(under='ignore'):
            return np.exp(logs)

    def readout_bounds(ln_a):
        # Conservative even if a Newton trial first flags a tail: every such
        # packet receives a full MIN_POSITIVE bound. Positive opacity makes
        # physical packet counts nonincreasing after each birth.
        tails=len(tail_seen)
        tail_energy=sum(float(births[i,1])*EV*tiny for i in tail_seen)
        dt_bound=(ln_a-t0)/background(config,t1)['H']
        # Each three-owner proper-time product can lose at most MIN_POSITIVE
        # on underflow. Bounding all products for the whole interval avoids
        # treating solver RHS call counts as a physical integration measure.
        rate_bound=3*len(births)*tiny*dt_bound
        nb=tails*tiny+rate_bound
        # Direct energy products can themselves underflow after eV->erg.
        eb=tail_energy+rate_bound*(1+config['energy_max_ev']*EV)+2*len(births)*tiny
        if nb>=1e-20 or eb>=1e-30:
            raise RuntimeError('IEEE readout error envelope exceeds frozen absolute budget floors')
        return dict(ieee_tail_packets=tails,ieee_underflow_N_bound=nb,ieee_underflow_E_bound=eb,ieee_Gamma_bound=(max_cnh+1)*len(births)*tiny,ieee_non_tail_photo_underflows_max=underflow_photo_products)

    def make_row(ln_a):
        photons=packet_counts(tau,ids,ln_a)
        energies=births[ids,1]*np.exp(births[ids,0]-ln_a)
        mask=crossing[ids]>ln_a
        v=evaluate(config,ln_a,gas,energies,photons,mask)
        nactive=float(photons.sum())
        eactive=EV*float(energies@photons)
        row=dict(ln_a=ln_a,z=v['bg']['z'],x_hii=gas[0],x_heii=gas[1],x_heiii=gas[2],w=gas[3],T=v['T'],Tcmb=v['bg']['Tcmb'],ne_per_h=v['ne_per_h'],Gamma_hi=v['Gamma'][0],Gamma_hei=v['Gamma'][1],Gamma_heii=v['Gamma'][2],Nactive=nactive,Eactive=eactive,emitted_N=emitted_n,emitted_E=emitted_e,out_N=out_n,out_E=out_e)
        row.update(zip(LEDGERS,ledgers))
        row.update(readout_bounds(ln_a))
        row['number_residual']=nactive+sum(ledgers[:3])+out_n-emitted_n
        row['energy_residual']=(gas[3]-initial[3])+(binding(gas,config)-binding(initial,config))+eactive+sum(ledgers[10:14])+out_e-emitted_e
        return row

    rows.append(make_row(t0))
    previous=t0
    for endpoint in events[1:]:
        n=len(ids)
        channel_mask=crossing[ids]>previous
        scale=np.ones(4+n+len(LEDGERS))
        scale[3]=EV
        for index in ENERGY_LEDGERS:
            scale[4+n+index]=EV
        # Elapsed time has a much larger magnitude; scale it separately.
        scale[-1]=1e15
        y0=np.r_[gas,tau,ledgers]/scale
        def fun(ln_a,y):
            nonlocal underflow_photo_products
            physical=y*scale
            energies=births[ids,1]*np.exp(births[ids,0]-ln_a)
            counts=packet_counts(physical[4:4+n],ids,ln_a)
            v=evaluate(config,ln_a,physical[:4],energies,counts,channel_mask)
            underflow_photo_products=max(underflow_photo_products,v['photo_product_underflows'])
            ledger_dt=np.r_[v['photo'],v['ci'],v['rr'],v['dr'],v['escape'],v['work'],v['cmb_reservoir'],v['redshift'],v['ci_floor'],v['ce_cap'],v['excluded_dr'],1.]
            return np.r_[v['gas_dt'],v['opacity'],ledger_dt]/(v['bg']['H']*scale)

        def jac(ln_a,y):
            # Four gas columns by finite differences; all optical-depth columns
            # analytic. A dense photo coupling row otherwise makes finite-
            # difference graph coloring require one RHS call per packet.
            matrix=lil_matrix((len(y),len(y)),dtype=float)
            base=fun(ln_a,y)
            for column in range(4):
                step=math.sqrt(np.finfo(float).eps)*max(abs(y[column]),1.)
                perturbed=y.copy();perturbed[column]+=step
                matrix[:,column]=((fun(ln_a,perturbed)-base)/step)[:,None]
            physical=y*scale
            energies=births[ids,1]*np.exp(births[ids,0]-ln_a)
            counts=packet_counts(physical[4:4+n],ids,ln_a)
            v=evaluate(config,ln_a,physical[:4],energies,counts,channel_mask)
            owners=v['owners']/v['bg']['H']
            if n:
                matrix[0,4:4+n]=-owners[:,0]
                if f:
                    matrix[1,4:4+n]=-(owners[:,1]-owners[:,2])/f
                    matrix[2,4:4+n]=-owners[:,2]/f
                matrix[3,4:4+n]=-np.sum(owners*(energies[:,None]-CHI),axis=1)
                for species in range(3):
                    matrix[4+n+species,4:4+n]=-owners[:,species]
                matrix[4+n+13,4:4+n]=-energies*counts
            return matrix.tocsc()

        solution=solve_ivp(fun,(previous,endpoint),y0,method=method,rtol=rtol,atol=atol,jac=jac)
        if not solution.success or solution.t[-1]!=endpoint:
            raise RuntimeError(f'reference integration failed at {previous}: {solution.message}')
        accepted=solution.y*scale[:,None]
        # Strict accepted-state admission, without absolute-tolerance projection.
        if np.any(accepted[:3]<0) or np.any(accepted[0]>1) or np.any(accepted[1]+accepted[2]>1) or np.any(accepted[4:4+n]<0):
            raise RuntimeError(f'reference nonphysical accepted state near {endpoint}: min fractions={accepted[:3].min():.17g}, min optical depths={accepted[4:4+n].min() if n else 0:.17g}')
        gas=accepted[:4,-1].copy()
        tau=accepted[4:4+n,-1].copy()
        photons=packet_counts(tau,ids,endpoint)
        ledgers=accepted[4+n:,-1].copy()
        for key in ('nfev','njev','nlu'):
            stats[key]+=getattr(solution,key)
        stats['steps']+=len(solution.t)-1
        stats['segments']+=1
        if stats['steps']>config['max_steps']:
            raise RuntimeError('reference accepted step resource limit')
        # Only the exact HI crossing removes an extant packet.
        leaving=crossing[ids,0]<=endpoint
        if np.any(leaving):
            out_n+=float(photons[leaving].sum())
            # Crossing energy is exactly the support boundary.
            out_e+=EV*CUTOFF[0]*float(photons[leaving].sum())
            ids=ids[~leaving]
            tau=tau[~leaving]
        born=np.flatnonzero(births[:,0]==endpoint)
        if len(born):
            emitted_n+=float(births[born,2].sum())
            emitted_e+=EV*float(births[born,1]@births[born,2])
            direct=born[births[born,1]<=CUTOFF[0]]
            out_n+=float(births[direct,2].sum())
            out_e+=EV*float(births[direct,1]@births[direct,2])
            retained=born[births[born,1]>CUTOFF[0]]
            ids=np.r_[ids,retained]
            tau=np.r_[tau,np.zeros(len(retained))]
        stats['max_active_packets']=max(stats['max_active_packets'],len(ids))
        if endpoint in output_set:
            rows.append(make_row(endpoint))
        previous=endpoint
    stats['completed']=previous==t1
    stats['runtime_s']=time.monotonic()-started
    stats.update(readout_bounds(t1))
    log_counts=np.log(births[ids,2])-tau
    energies=births[ids,1]*np.exp(births[ids,0]-t1)
    packets=np.column_stack([ids,births[ids,0],births[ids,1],tau,log_counts,energies,packet_counts(tau,ids,t1)])
    return dict(rows=rows,stats=stats,births=births,packets=packets)


IDENTITIES=dict(schema='igm_history_config_v1',model_id='manufactured_hhe_v1',provider_id='grackle341_caseA_lowT_subset_v1',closure_id='caseA_escape_C1_primary_only',criteria_id='igm_history_frozen_20261006_v1')
INTEGER_KEYS={'birth_panels','energy_panels','output_panels','max_packets','max_steps'}
FLOAT_KEYS={'h0','omega_r','omega_m','omega_b','omega_lambda','y_he','tcmb0','z_start','z_end','x_hii','x_heii','x_heiii','temperature_k','source_rate','energy_min_ev','energy_max_ev','max_dln_a','min_dln_a'}


def read_config(path):
    from pathlib import Path
    values={}
    for line in Path(path).read_text().splitlines():
        line=line.strip()
        if not line or line.startswith('#'): continue
        if line.count('=')!=1: raise ValueError('manifest line must contain one =')
        key,value=map(str.strip,line.split('='))
        if key in values: raise ValueError(f'duplicate manifest key: {key}')
        if key in IDENTITIES:
            if value!=IDENTITIES[key]: raise ValueError(f'unsupported {key}: {value}')
        elif key in INTEGER_KEYS:
            value=int(value)
            if value<1: raise ValueError(f'nonpositive {key}')
        elif key in FLOAT_KEYS:
            value=float(value)
            if not math.isfinite(value): raise ValueError(f'nonfinite {key}')
        else: raise ValueError(f'unknown manifest key: {key}')
        values[key]=value
    missing=(set(IDENTITIES)|INTEGER_KEYS|FLOAT_KEYS)-set(values)
    if missing: raise ValueError(f'missing manifest keys: {sorted(missing)}')
    if abs(values['omega_r']+values['omega_m']+values['omega_lambda']-1)>1e-12:
        raise ValueError('manifest is not flat')
    if not (0<=values['y_he']<1 and 0<values['omega_b']<=values['omega_m'] and values['h0']>0 and values['tcmb0']>0):
        raise ValueError('invalid background')
    if not (0<=values['x_hii']<=1 and values['x_heii']>=0 and values['x_heiii']>=0 and values['x_heii']+values['x_heiii']<=1 and 1<=values['temperature_k']<=1e6):
        raise ValueError('invalid gas initial condition')
    if not (-1<values['z_end']<values['z_start'] and values['max_dln_a']>=values['min_dln_a']>0):
        raise ValueError('invalid coordinate range or step controls')
    return values


def main():
    import argparse,csv,hashlib,json,time
    from pathlib import Path
    import scipy
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',required=True)
    parser.add_argument('--output',required=True)
    parser.add_argument('--method',choices=['Radau','BDF'],default='Radau')
    parser.add_argument('--rtol',type=float,default=1e-11)
    parser.add_argument('--atol',type=float,default=1e-14)
    parser.add_argument('--times-csv',help='Common output times only; no Rust states enter the RHS')
    args=parser.parse_args()
    config_path=Path(args.config)
    cfg=read_config(config_path)
    output=Path(args.output)
    output.mkdir(parents=True,exist_ok=False)
    output.joinpath('config.cfg').write_bytes(config_path.read_bytes())
    source_keys={'h0','omega_r','omega_m','omega_b','omega_lambda','y_he','tcmb0','z_start','z_end','source_rate','energy_min_ev','energy_max_ev','birth_panels','energy_panels'}
    source_bytes=json.dumps({key:cfg[key] for key in sorted(source_keys)},sort_keys=True,separators=(',',':')).encode()
    manifest=dict(implementation_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),source_input_sha256=hashlib.sha256(source_bytes).hexdigest(),rate_source_sha256='a900e726413da39bb24fc506846a09f7e0e4addbd5152197ca76d0e22ad02cea',config_sha256=hashlib.sha256(config_path.read_bytes()).hexdigest(),scipy=scipy.__version__,numpy=np.__version__,provider_commit='af7939494ce65007887ada7b98d1813df6843346',solver='independent_python_continuous_redshift_optical_depth_v1',method=args.method,rtol=args.rtol,atol=args.atol)
    output.joinpath('manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    times=None
    if args.times_csv:
        with open(args.times_csv) as stream:
            times=np.array([float(row['ln_a']) for row in csv.DictReader(stream)])
    started=time.monotonic()
    try:
        result=solve_history(cfg,times,args.method,args.rtol,args.atol)
    except Exception as error:
        status=dict(completed=False,error_type=type(error).__name__,error=str(error),runtime_s=time.monotonic()-started)
        output.joinpath('status.json').write_text(json.dumps(status,indent=2)+'\n')
        print(json.dumps(status))
        raise SystemExit(1)
    from igm_compare import compare_rows
    validation=compare_rows(result['rows'],result['rows'])
    result['stats']['ledger_valid']=validation['passed']
    result['stats']['budget_ratios']=validation['budgets']['candidate']
    with output.joinpath('history.csv').open('w') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(result['rows'][0]))
        writer.writeheader();writer.writerows(result['rows'])
    with output.joinpath('births.csv').open('w') as stream:
        writer=csv.writer(stream);writer.writerow(['birth_ln_a','energy_ev','per_h']);writer.writerows(result['births'])
    with output.joinpath('packets_final.csv').open('w') as stream:
        writer=csv.writer(stream);writer.writerow(['id','birth_ln_a','birth_energy_ev','tau','log_count','energy_ev','readout_count']);writer.writerows(result['packets'])
    output.joinpath('status.json').write_text(json.dumps(result['stats'],indent=2)+'\n')
    print(json.dumps(result['stats']))
    if not result['stats']['ledger_valid']:
        raise SystemExit(2)

if __name__=='__main__': main()
