"""Full-covariance, fixed-source BB13 redshift-tilt/EOS box GLS profile.

No physical gamma prior, Jeans covariance, UVB rate solve or native IVP.
"""
import math

FIXED_Z=(2.4,2.8,3.2,3.6,4.0,4.4,4.75)

def dot(x,y):
    if len(x)!=len(y):raise ValueError('MISMATCHED_DOT')
    return math.fsum(a*b for a,b in zip(x,y))

def cholesky(C):
    n=len(C)
    if n<2 or any(len(row)!=n for row in C):raise ValueError('NON_SQUARE_C')
    if any(not math.isfinite(v) for row in C for v in row):raise ValueError('NONFINITE_C')
    if any(C[i][j]!=C[j][i] for i in range(n) for j in range(n)):
        raise ValueError('NONSYMMETRIC_C')
    L=[[0.0]*n for _ in range(n)]
    for i in range(n):
        for j in range(i+1):
            t=C[i][j]-math.fsum(L[i][k]*L[j][k] for k in range(j))
            if i==j:
                if t<=0 or not math.isfinite(t):raise ValueError('NON_SPD_C')
                L[i][j]=math.sqrt(t)
            else:L[i][j]=t/L[j][j]
    return L

def solve(L,b):
    n=len(L)
    if len(b)!=n or any(not math.isfinite(u) for u in b):raise ValueError('BAD_SOLVE_RHS')
    forward=[0.0]*n
    for i in range(n):forward[i]=(b[i]-math.fsum(L[i][k]*forward[k] for k in range(i)))/L[i][i]
    result=[0.0]*n
    for i in range(n-1,-1,-1):result[i]=(forward[i]-math.fsum(L[k][i]*result[k] for k in range(i+1,n)))/L[i][i]
    return result

def fit(z,obs,model,C,source_shift):
    n=len(z)
    if n!=7 or any(len(vec)!=n for vec in (obs,model,source_shift)) or len(C)!=n:
        raise ValueError('FROZEN_SEVEN_ROWS')
    if tuple(sorted(z))!=FIXED_Z or any(not math.isfinite(v) for vec in (z,obs,model,source_shift) for v in vec):
        raise ValueError('NON_SOURCE_GRID_OR_NONFINITE')
    L=cholesky(C);one=[1.0]*n;x=[v-3.6 for v in z];r=[d-m for d,m in zip(obs,model)]
    def w(a):return solve(L,a)
    w1,wx,wr,wv=(w(s) for s in (one,x,r,source_shift))
    a=dot(one,w1);b=dot(one,wx);c=dot(x,wx)
    u=dot(one,wr);v=dot(x,wr);uu=dot(one,wv);vv=dot(x,wv)
    det=a*c-b*b
    if a<=0 or det<=0 or not math.isfinite(det):raise ValueError('RANK_DEFICIENT_DESIGN')
    cov=[[c/det,-b/det],[-b/det,a/det]]
    theta0=((c*u-b*v)/det,(a*v-b*u)/det)
    shift=((c*uu-b*vv)/det,(a*vv-b*uu)/det)
    def coefficients(theta):return [theta0[i]+theta*shift[i] for i in range(2)]
    def residual(y,co):return [y[i]-co[0]-co[1]*x[i] for i in range(n)]
    residual0=residual(r,theta0);residual_v=residual(source_shift,shift)
    Q_center=dot(residual0,w(residual0));qcross=dot(residual_v,w(residual0));qcurve=dot(residual_v,w(residual_v))
    if qcurve<=0:raise ValueError('SOURCE_RESPONSE_NOT_IDENTIFIABLE_AFTER_2_COLUMNS')
    optimal_unconstrained=-qcross/qcurve
    optimal=max(-1.0,min(1.0,optimal_unconstrained))
    def at(th):
        if not -1<=th<=1 or not math.isfinite(th):raise ValueError('THETA_OUTSIDE_BOX')
        y=[r[i]+th*source_shift[i] for i in range(n)]
        co=coefficients(th);e=residual(y,co)
        Q2=dot(e,w(e))
        a0=dot(one,w(y))/a;ez=[y[i]-a0 for i in range(n)]
        Q0=dot(ez,w(ez));source_q=Q_center+2*th*qcross+th*th*qcurve
        delta_id=(dot(x,w(ez))**2)/(c-b*b/a)
        return dict(theta=th,gamma_TDR=1.4+0.2*th,beta=co[0],kappa=co[1],Q2=Q2,
                    Q2_quadratic=source_q,beta_amplitude_only=a0,Q0=Q0,
                    DeltaQ=Q0-Q2,DeltaQ_identity=delta_id,residual=e)
    # Correlation AFTER removing the amplitude column only (not removing x).
    x_amp=[x[i]-b/a for i in range(n)]
    v_amp=[source_shift[i]-uu/a for i in range(n)]
    corr=dot(x_amp,w(v_amp))/math.sqrt(dot(x_amp,w(x_amp))*dot(v_amp,w(v_amp)))
    profiles=[at(t) for t in (-1.0,0.0,1.0,optimal)]
    return dict(schema='REI_UVB_TILT_EOS_PROFILE_V1',input_z=z,theta_box=[-1,1],source_shift=source_shift,
                conditional_covariance=cov,conditional_sigma_kappa=math.sqrt(cov[1][1]),
                beta_theta0=theta0[0],kappa_theta0=theta0[1],
                beta_dtheta=shift[0],kappa_dtheta=shift[1],
                kappa_box=[min(coefficients(-1)[1],coefficients(1)[1]),max(coefficients(-1)[1],coefficients(1)[1])],
                beta_box=[min(coefficients(-1)[0],coefficients(1)[0]),max(coefficients(-1)[0],coefficients(1)[0])],
                projected_EOS_vs_tilt_correlation=corr,
                Q2_quadratic_coefficients=[Q_center,2*qcross,qcurve],
                unconstrained_theta_diagnostic=optimal_unconstrained,
                bounded_theta_star=optimal,profile_points=profiles,
                theta0=profiles[1],theta_plus=profiles[2],theta_minus=profiles[0],best_profile=profiles[3],
                nested_box_profile_improvement=min(t['Q0'] for t in profiles[:3])-profiles[3]['Q2'],
                status='CONDITIONAL_STATISTICAL_ONLY',F4='PARTIAL',L4=False,physical_radii=None)
