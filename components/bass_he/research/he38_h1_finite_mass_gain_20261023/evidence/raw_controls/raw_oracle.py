"""Independent HE38 raw Maxwell/Grad quadrature.
No import from production model or its moment/coefficient implementation.
Units: kinetic masses in me, velocities in sqrt(theta/me), pressure events in theta.
"""
import itertools
import math
import numpy as np
from scipy.special import roots_hermite, roots_laguerre, roots_legendre

ME = 9.1093837139e-31
MP = 1.67262192595e-27
KB = 1.380649e-23
EV = 1.602176634e-19
A0 = 5.29177210544e-11
I_J = 13.6*EV
ION_MASS = MP/ME
NEUTRAL_MASS = ION_MASS+1.
TOTAL_MASS = ION_MASS+2.
REDUCED_MASS = NEUTRAL_MASS/TOTAL_MASS
INNER_REDUCED_MASS = ION_MASS/NEUTRAL_MASS
ELECTRON_OUTER = 1./TOTAL_MASS
NEUTRAL_OUTER = NEUTRAL_MASS/TOTAL_MASS
ION_INNER = ION_MASS/NEUTRAL_MASS
ELECTRON_INNER = 1./NEUTRAL_MASS
DIRECTIONS = np.array([np.diag([1.,-1.,0.])/math.sqrt(2.),
                      np.array([[0.,1.,2.],[1.,0.,3.],[2.,3.,0.]])/math.sqrt(28.)])

def rules(nradial, ntransfer):
    h, wh = roots_hermite(3)
    indices = np.array(list(itertools.product(range(3), repeat=3)))
    com = math.sqrt(2./TOTAL_MASS)*h[indices]
    wcom = np.prod(wh[indices]/math.sqrt(math.pi),axis=1)
    mu, wmu = roots_legendre(3)
    phi = np.arange(8)*2.*math.pi/8.
    directions = np.stack((np.sqrt(1.-mu[:,None]**2)*np.cos(phi)[None,:],
                           np.sqrt(1.-mu[:,None]**2)*np.sin(phi)[None,:],
                           np.broadcast_to(mu[:,None],(3,8))),axis=-1).reshape(-1,3)
    wdir = np.broadcast_to((wmu/2./8.)[:,None],(3,8)).ravel()
    axes = np.vstack((np.eye(3),-np.eye(3)))
    g1dirs = np.repeat(axes,6,axis=0)
    g2dirs = np.tile(axes,(6,1))
    t, wt = roots_laguerre(nradial)
    u, wu = roots_legendre(ntransfer)
    return com,wcom,directions,wdir,g1dirs,g2dirs,t,wt,(u+1.)/2.,wu/2.

def stf(a):
    return a - np.trace(a,axis1=-2,axis2=-1)[...,None,None]*np.eye(3)/3.

def evaluate(temperature_K, nradial, ntransfer):
    com,wcom,ndir,wdir,dir1,dir2,t,wt,u,wu=rules(nradial,ntransfer)
    theta=KB*temperature_K
    x=I_J/theta
    radial_e=x+t
    w_radial=wt*t/(x+t)
    joint=wcom[:,None]*wdir[None,:]
    pressure_records=[]
    response_records=[]
    rate_grad_records=[]
    mean_transfer=[]
    max_energy_defect=0.
    max_momentum_defect=0.
    for e in radial_e:
        incoming_g=math.sqrt(2.*e/REDUCED_MASS)*ndir
        ve=com[:,None,:]+NEUTRAL_OUTER*incoming_g[None,:,:]
        vh=com[:,None,:]-ELECTRON_OUTER*incoming_g[None,:,:]
        # Inverse CDF of the original source transfer law, not its closed mean.
        transfer=x/((1.-u)+u*x/e)
        mean_transfer.append(float(wu@transfer))
        g1=np.sqrt(2.*(e-transfer)/REDUCED_MASS)[:,None,None]*dir1[None,:,:]
        g2=np.sqrt(2.*(transfer-x)/INNER_REDUCED_MASS)[:,None,None]*dir2[None,:,:]
        out1=com[:,None,None,:]+NEUTRAL_OUTER*g1[None,:,:,:]
        out2=com[:,None,None,:]-ELECTRON_OUTER*g1[None,:,:,:]+ION_INNER*g2[None,:,:,:]
        outp=com[:,None,None,:]-ELECTRON_OUTER*g1[None,:,:,:]-ELECTRON_INNER*g2[None,:,:,:]
        weights=wu/36.
        # Direct velocity dyads over all 36 Cartesian-axis direction pairs.
        gain_e=(np.einsum('u,vuqi,vuqj->vij',weights,out1,out1,optimize=True)
                +np.einsum('u,vuqi,vuqj->vij',weights,out2,out2,optimize=True))
        gain_p=ION_MASS*np.einsum('u,vuqi,vuqj->vij',weights,outp,outp,optimize=True)
        removed_e=np.einsum('vai,vaj->vaij',ve,ve)
        removed_h=NEUTRAL_MASS*np.einsum('vai,vaj->vaij',vh,vh)
        event=np.stack((gain_e[:,None,:,:]-removed_e,
                        -removed_h,
                        np.broadcast_to(gain_p[:,None,:,:],removed_h.shape)))
        # Direct first variation of each incoming Maxwellian, with pi_s=n_s theta Z.
        inp=np.stack((ve,vh))
        grad=.5*np.array([1.,NEUTRAL_MASS])[:,None,None,None]*np.einsum(
            'svai,dij,svaj->sdva',inp,DIRECTIONS,inp,optimize=True)
        pressure_records.append(np.einsum('va,svaij->sij',joint,event,optimize=True))
        response_records.append(np.einsum('va,cdva,svaij->scdij',joint,grad,event,optimize=True))
        rate_grad_records.append(np.einsum('va,cdva->cd',joint,grad,optimize=True))
        # These are checks on the very events used, not a separate event suite.
        pin=ve[:,0,:]+NEUTRAL_MASS*vh[:,0,:]
        pout=out1+out2+ION_MASS*outp
        pscale=np.maximum(1.,np.linalg.norm(pin,axis=-1))
        max_momentum_defect=max(max_momentum_defect,float(np.max(
            np.linalg.norm(pout-pin[:,None,None,:],axis=-1)/pscale[:,None,None])))
        ein=.5*(np.sum(ve[:,0,:]**2,axis=-1)+NEUTRAL_MASS*np.sum(vh[:,0,:]**2,axis=-1))
        eout=.5*(np.sum(out1**2,axis=-1)+np.sum(out2**2,axis=-1)+ION_MASS*np.sum(outp**2,axis=-1))
        max_energy_defect=max(max_energy_defect,float(np.max(
            np.abs(eout+x-ein[:,None,None])/np.maximum(1.,ein[:,None,None]))))
    pressure_records=np.asarray(pressure_records)
    response_records=np.asarray(response_records)
    rate_grad_records=np.asarray(rate_grad_records)
    pressure=np.einsum('r,rsij->sij',w_radial,pressure_records,optimize=True)
    response=np.einsum('r,rscdij->scdij',w_radial,response_records,optimize=True)
    # SI scalar prefactor derived from the Maxwell relative-energy density
    # times sqrt(2E/mu) sigma(E) dE, with E=theta(x+t).
    rate_prefactor=(4.*math.pi*A0*A0*I_J
                    *math.sqrt(8./(math.pi*(ME*REDUCED_MASS)*theta))*math.exp(-x))
    integrated_rate=float(np.sum(w_radial))
    return {
        "temperature_K":np.array(temperature_K),"nradial":np.array(nradial),
        "ntransfer":np.array(ntransfer),"theta_J":np.array(theta),
        "x":np.array(x),"rate_prefactor_m3_s":np.array(rate_prefactor),
        "dimensionless_rate":np.array(integrated_rate),
        "unperturbed_pressure":pressure,
        "unperturbed_heat":.5*np.trace(pressure,axis1=-2,axis2=-1),
        "unperturbed_STF":stf(pressure),
        "linear_pressure":response,"linear_STF":stf(response),
        "linear_heat":.5*np.trace(response,axis1=-2,axis2=-1),
        "linear_rate":np.einsum('r,rcd->cd',w_radial,rate_grad_records,optimize=True),
        "STF_directions":DIRECTIONS,"radial_energy_dimensionless":radial_e,
        "radial_weights":w_radial,"transfer_means_dimensionless":np.asarray(mean_transfer),
        "radial_unperturbed_pressure":pressure_records,
        "radial_linear_pressure":response_records,
        "radial_linear_rate":rate_grad_records,
        "com_nodes":com,"com_weights":wcom,"incoming_directions":ndir,
        "incoming_direction_weights":wdir,
        "max_pointwise_energy_scaled_defect":np.array(max_energy_defect),
        "max_pointwise_momentum_scaled_defect":np.array(max_momentum_defect)
    }

