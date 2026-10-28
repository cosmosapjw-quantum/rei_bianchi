"""Correlated log-rate amplitude likelihood and fixed-shape UVB moments.

Standard library only. No atomic/nuclear IVP or old-run dependency.
"""
import bisect
import json
import math
from pathlib import Path

UNIT=Path(__file__).resolve().parents[1]
RATE_FIELDS=('Gamma_HI_s-1','heat_HI_eV_s-1','Gamma_HeI_s-1','heat_HeI_eV_s-1','Gamma_HeII_s-1','heat_HeII_eV_s-1')


def cholesky(covariance):
    n=len(covariance)
    if n==0 or any(len(row)!=n for row in covariance):raise ValueError('square nonempty covariance required')
    if any(not math.isfinite(x) for row in covariance for x in row):raise ValueError('finite covariance required')
    if any(not math.isclose(covariance[i][j],covariance[j][i],rel_tol=1e-12,abs_tol=1e-15) for i in range(n) for j in range(n)):
        raise ValueError('symmetric covariance required')
    lower=[[0.]*n for _ in range(n)]
    for i in range(n):
        for j in range(i+1):
            value=covariance[i][j]-sum(lower[i][k]*lower[j][k] for k in range(j))
            if i==j:
                if value<=0:raise ValueError('positive definite covariance required')
                lower[i][j]=math.sqrt(value)
            else:lower[i][j]=value/lower[j][j]
    return lower


def covariance_solve(lower,vector):
    n=len(lower)
    if len(vector)!=n or not all(math.isfinite(x) for x in vector):raise ValueError('finite matched vector required')
    forward=[0.]*n
    for i in range(n):forward[i]=(vector[i]-sum(lower[i][j]*forward[j] for j in range(i)))/lower[i][i]
    solution=[0.]*n
    for i in range(n-1,-1,-1):solution[i]=(forward[i]-sum(lower[j][i]*solution[j] for j in range(i+1,n)))/lower[i][i]
    return solution


def scalar_product(a,b):return sum(x*y for x,y in zip(a,b))


def fit_log_amplitude(observed,model,covariance,eos_shift):
    n=len(observed)
    if not n or len(model)!=n or len(eos_shift)!=n:raise ValueError('matched nonempty likelihood vectors required')
    if not all(math.isfinite(x) for x in list(observed)+list(model)+list(eos_shift)):
        raise ValueError('finite log rates and nuisance shift required')
    L=cholesky(covariance);one=[1.]*n
    Wone=covariance_solve(L,one);den=scalar_product(one,Wone)
    if den<=0:raise ValueError('nonpositive amplitude information')
    residual=[d-m for d,m in zip(observed,model)]
    beta=scalar_product(Wone,residual)/den
    centered=[r-beta for r in residual]
    chi2=scalar_product(centered,covariance_solve(L,centered))
    raw_chi2=scalar_product(residual,covariance_solve(L,residual))
    subtraction_chi2=raw_chi2-(scalar_product(Wone,residual)**2)/den
    vmean=scalar_product(Wone,eos_shift)/den
    vcentered=[v-vmean for v in eos_shift]
    Wv=covariance_solve(L,vcentered)
    curvature=scalar_product(vcentered,Wv)
    vscale=scalar_product(eos_shift,covariance_solve(L,eos_shift))
    degenerate=curvature<=1e-12*vscale if vscale>0 else True
    if curvature<-1e-12*max(vscale,1e-300):raise ValueError('negative nuisance curvature')
    unconstrained=None if degenerate else -scalar_product(centered,Wv)/curvature
    theta=0. if unconstrained is None else max(-1.,min(1.,unconstrained))
    beta_profile=beta+theta*vmean
    profile_residual=[r+theta*v-beta_profile for r,v in zip(residual,eos_shift)]
    profile_chi2=scalar_product(profile_residual,covariance_solve(L,profile_residual))
    endpoints=[]
    for endpoint in (-1.,1.):
        endpoint_beta=beta+endpoint*vmean
        endpoint_residual=[r+endpoint*v-endpoint_beta for r,v in zip(residual,eos_shift)]
        endpoints.append({'theta':endpoint,'beta':endpoint_beta,
                          'chi2':scalar_product(endpoint_residual,covariance_solve(L,endpoint_residual))})
    return {'statistical_only':{'beta_log10_amplitude':beta,'amplitude':10**beta,
              'variance_beta_dex2':1/den,'sigma_beta_dex':math.sqrt(1/den),'residual_chi2':chi2,
              'unscaled_template_chi2':raw_chi2,'profiled_subtraction_identity_chi2':subtraction_chi2,'degrees_of_freedom':n-1},
            'EOS_box_profile':{'theta':None if degenerate else theta,'theta_representative':theta,
              'theta_unconstrained':unconstrained,'gamma_TDR':None if degenerate else 1.4+.2*theta,
              'beta_log10_amplitude':beta_profile,'amplitude':10**beta_profile,'residual_chi2':profile_chi2,
              'theta_at_boundary':abs(theta)==1.,'theta_identifiable_after_amplitude':not degenerate,
              'degenerate_with_amplitude':degenerate,'degeneracy_relative_threshold':1e-12,
              'theta_endpoint_reports':endpoints,
              'beta_conditional_sigma_dex_at_fixed_theta':math.sqrt(1/den),
              'beta_range_as_theta_runs_minus1_to1':sorted([beta-vmean,beta+vmean]),
              'nuisance_convention':'observed log-rate d(theta)=d+theta*v; theta=(gamma_TDR-1.4)/.2',
              'uncertainty_status':'profile point and conditional statistical error; not a marginalized EOS posterior'},
            'covariance_model':'Full supplied correlated statistical covariance in dex²',
            'Jeans_systematic_included_in_fit':False,'residuals_statistical_only':centered,
            'residuals_EOS_profile':profile_residual,'cholesky_diagonal':[L[j][j] for j in range(n)]}


def interpolate_rate(z,knots,values):
    if not math.isfinite(z) or z<knots[0] or z>knots[-1]:raise ValueError('redshift outside supported interpolation interval')
    if len(knots)!=len(values) or len(knots)<2 or any(b<=a for a,b in zip(knots,knots[1:])):
        raise ValueError('ordered matched interpolation knots required')
    if any(not math.isfinite(v) or v<0 for v in values):raise ValueError('nonnegative finite rates required')
    j=bisect.bisect_left(knots,z)
    if j<len(knots) and knots[j]==z:return {'value':float(values[j]),'method':'EXACT_KNOT'}
    fraction=(z-knots[j-1])/(knots[j]-knots[j-1])
    if values[j-1]==0 or values[j]==0:
        return {'value':(1-fraction)*values[j-1]+fraction*values[j],'method':'LINEAR_RATE_ZERO_ENDPOINT'}
    return {'value':10**((1-fraction)*math.log10(values[j-1])+fraction*math.log10(values[j])),
            'method':'LINEAR_LOG10_RATE_IN_Z'}


def log_interpolate(z,knots,values):return interpolate_rate(z,knots,values)['value']


def load_sources():
    data=json.loads((UNIT/'sources/BECKER_BOLTON_2013.json').read_text())
    template=json.loads((UNIT/'sources/PUCHWEIN_2019_FIDUCIAL.json').read_text())
    expected=['z',*RATE_FIELDS,'Compton_raw']
    if template['columns']!=expected or len(template['rows'])!=template['row_count']:
        raise ValueError('physical UVB source columns or row count mismatch')
    if any(len(row)!=8 or any(not math.isfinite(x) for x in row) or any(x<0 for x in row) for row in template['rows']):
        raise ValueError('physical UVB source shape/nonnegative-finite check failed')
    if any(b[0]<=a[0] for a,b in zip(template['rows'],template['rows'][1:])):
        raise ValueError('physical UVB redshifts not strictly ordered')
    cholesky(data['statistical_covariance_dex2'])
    return data,template


def template_moments(z,template=None):
    if template is None:_,template=load_sources()
    columns=template['columns'];rows=template['rows'];knots=[row[0] for row in rows]
    return {field:log_interpolate(z,knots,[row[columns.index(field)] for row in rows]) for field in RATE_FIELDS}


def fit_sources():
    data,template=load_sources()
    model=[math.log10(template_moments(z,template)['Gamma_HI_s-1']/1e-12) for z in data['z']]
    result=fit_log_amplitude(data['values'],model,data['statistical_covariance_dex2'],data['slope_nuisance']['response_dex'])
    result.update({'observed_z':data['z'],'observed_log10_Gamma12':data['values'],'template_log10_Gamma12':model,
                   'calibrated_redshift_domain':data['domain']['z'],'data_id':data['id'],'template_id':template['id'],
                   'Jeans_lower_dex':data['jeans_systematic_lower_dex'],'Jeans_upper_dex':data['jeans_systematic_upper_dex']})
    return result


def calibrated_moments(z,beta,template=None,calibrated_domain=(2.4,4.75)):
    if not calibrated_domain[0]<=z<=calibrated_domain[1]:raise ValueError('outside observed calibrated redshift domain; no fit extrapolation')
    if not math.isfinite(beta):raise ValueError('finite log-amplitude required')
    amplitude=10**beta
    return {key:value*amplitude for key,value in template_moments(z,template).items()}


def bath_adapter(z,beta):
    return {'z':z,'moments':calibrated_moments(z,beta),'rate_units':'per target proper-second',
            'heating_units':'eV per target proper-second','calibration':'HI amplitude conditional on fixed Puchwein2019 UVB shape',
            'prediction_owner':'HeI/HeII and heating follow adopted physical template; not independently measured by this HI likelihood',
            'T_K':None,'electron_density_cm-3':None,'Li_photo_rates':None,'MeV_photodisintegration':None,
            'CR_source_yields':None,'fast_stopping_escape':None,'inverse_weak_bath':None,'H_s-1':None,
            'shear':None,'initial_populations':None,'missing_fields_status':'MISSING_INPUT_NOT_ZERO',
            'Compton':'EXCLUDED_PENDING_NORMALIZATION','old_bath_mutated':False,'solver_invoked':False}


def observation_weights(z,data):
    knots=data['z'];n=len(knots)
    if not math.isfinite(z) or z<knots[0] or z>knots[-1]:raise ValueError('outside observed redshift support')
    j=bisect.bisect_left(knots,z);weights=[0.]*n
    if j<n and knots[j]==z:weights[j]=1.
    else:
        fraction=(z-knots[j-1])/(knots[j]-knots[j-1]);weights[j-1]=1-fraction;weights[j]=fraction
    return weights


def observed_covariance(z1,z2,data=None):
    if data is None:data,_=load_sources()
    a,b=observation_weights(z1,data),observation_weights(z2,data)
    covariance=data['statistical_covariance_dex2']
    return sum(a[i]*covariance[i][j]*b[j] for i in range(len(a)) for j in range(len(b)))


def observed_HI(z,data=None):
    if data is None:data,_=load_sources()
    weights=observation_weights(z,data);logGamma=scalar_product(weights,data['values'])
    variance=observed_covariance(z,z,data)
    return {'z':z,'Gamma_HI_s-1':1e-12*10**logGamma,'log10_Gamma12':logGamma,
            'statistical_variance_dex2':variance,'EOS_shift_dex':scalar_product(weights,data['slope_nuisance']['response_dex']),
            'weights':weights,'interpolation':'LINEAR_OBSERVED_LOG10_RATE_IN_Z',
            'between_knot_interpolation_error':'NOT_MEASURED_BY_COVARIANCE','heating':None,'helium_rates':None}


def event_heat_mapping(y_target,Gamma,heating_eV_s,threshold_eV,nHref_cm3):
    if not all(math.isfinite(x) and x>=0 for x in (y_target,Gamma,heating_eV_s,threshold_eV)) or not math.isfinite(nHref_cm3) or nHref_cm3<=0:
        raise ValueError('nonnegative event/heat inputs and positive proper reference density required')
    events=y_target*Gamma;heat=y_target*heating_eV_s;internal=threshold_eV*events
    return {'events_per_Href_s':events,'heat_eV_per_Href_s':heat,'ionization_internal_eV_per_Href_s':internal,
            'absorbed_eV_per_Href_s':heat+internal,'events_cm-3_s-1':nHref_cm3*events,
            'heat_eV_cm-3_s-1':nHref_cm3*heat,'extra_4pi_or_c_applied':False}
