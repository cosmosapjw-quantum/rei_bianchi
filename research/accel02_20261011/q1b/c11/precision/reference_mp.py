"""Independent arbitrary precision evaluation of the same pinned FLRW formulas.

Uses exact binary64 provider constants/loaded table arrays as input, then 80 dps
arithmetic. Does not call the production moment kernel or production logR code.
Independent arithmetic, NOT independent physical data/interpolation model.
"""
import mpmath as mp


def volume(bg,t):
    w=mp.mpf(bg.omega); x=w*mp.mpf(t)
    A=1+mp.mpf(bg.B)/(2*mp.mpf(bg.D)*mp.mpf(bg.v_i))
    B=mp.mpf(bg.root_poly_i)/(mp.mpf(bg.v_i)*mp.sqrt(mp.mpf(bg.D)))
    return 1+A*(mp.cosh(x)-1)+B*mp.sinh(x)


def ray(bg,t):
    return volume(bg,t)**(-mp.mpf(1)/3)


def cell_moments(source,t,cell,angle=0):
    bg=source.provider.background; tab=source.provider.tables['emissivity']
    r=ray(bg,t); z=(1+mp.mpf(bg.z_i))*r-1
    zvals=list(map(mp.mpf,tab.redshifts)); iz=next(j for j,x in enumerate(zvals) if x>=z)
    if zvals[iz]==z:
        profile=[mp.mpf(x) for x in tab.spectra[::-1,iz]]
    else:
        f=(z-zvals[iz-1])/(zvals[iz]-zvals[iz-1])
        profile=[(1-f)*mp.mpf(a)+f*mp.mpf(b) for a,b in zip(tab.spectra[::-1,iz-1],tab.spectra[::-1,iz])]
    native=list(map(mp.mpf,tab.energies_eV))
    a,b=map(mp.mpf,source.edges[cell:cell+2]); lo=max(r*a,mp.mpf(10)); hi=min(r*b,mp.mpf(50000))
    if hi<=lo:return tuple(mp.mpf(0) for _ in range(3))
    import sys
    mod=sys.modules[type(tab).__module__]
    pref=mp.mpf(source.weights[angle])/r**3*(1+z)**3/(mp.mpf(mod.MPC_CM)**3*mp.mpf(mod.H_ERG_S))
    ns=[]; qs=[]; ds=[]
    for j in range(len(native)-1):
        left=max(lo,native[j]);right=min(hi,native[j+1])
        if right<=left:continue
        width=mp.log(native[j+1]/native[j]); slope=(profile[j+1]-profile[j])/width
        xl=mp.log(left/r/a); dx=mp.log(right/left)
        f0=profile[j]+slope*mp.log(left/native[j])
        f1=profile[j]+slope*mp.log(right/native[j])
        w0=(mp.expm1(dx)-dx)/dx**2
        w1=(dx*mp.exp(dx)-mp.expm1(dx))/dx**2
        nn=dx*(f0+f1)/2;qq=dx*left/r*(f0*w0+f1*w1)
        ns.append(nn);qs.append(qq);ds.append(qq-a*nn)
    return pref*mp.fsum(ns),pref*mp.fsum(qs),pref*mp.fsum(ds)
