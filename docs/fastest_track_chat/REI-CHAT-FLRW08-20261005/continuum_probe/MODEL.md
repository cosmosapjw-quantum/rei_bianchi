# Fixed-grid projected continuous-time candidate

This diagnostic covers proper time 0..1e10 s only. It uses the original 33
energy nodes (`m=8`) and 128 original midpoint rays (`mu8,phi16`), original
initial gas `[.9,.3,.6,w0]` at 50000 K, and .05 photons/H at exactly 13.7 eV,
uniformly over those rays. The six discrete trajectories call the unmodified
`paired_initial` and `paired_trial` functions. Each accepted macro call returns
two half endpoint steps. The continuous reference is separately implemented in
Python from the analytic coefficients below; it never calls a Rust RHS.

## Necessary correction to the original lower-boundary assumption

Let M_dt be the original endpoint transport map. For positive directional H
and any occupied lowest node E0=10 eV, M_dt transfers **all** its population to
the lower guard for every dt>0: E0*g(t+dt)/g(t)<10. Thus M_dt does not tend to
the identity on these full states; `(M_dt-I)/dt` has no finite full-domain
generator. The initially prescribed `Nguard'=H_d*p0` is not this map's limit.
The frozen original intent is retained. The Host correction is recorded in
`.cuh/fastest-track/REI-CHAT-FLRW08/continuum-probe/boundary-model-correction.json`.

Define P to transfer p0 into the lower guard, adding p0 to Nguard and 10*p0
to Uguard, and set p0=0. P preserves photon number and energy. This reference
uses the derivative of **P M_dt P on the reduced p0=0 state**. It is a candidate
projected limit of repeated original steps, not the full original one-step
derivative. The probe does not prove uniform convergence of these compositions.
Original output retains a transient p0; its number/energy must be combined with
the guard when comparing projected states or physical moments.

The real occupied-node witness moves .05 photons/H to the guard at both
dt=10000 and 1000 s; the guard-number secants are 5e-6 and 5e-5 /s. The allowed
macro minimum1000 s is preserved. No production boundary is changed.

## Geometry, transport, and source

For each original q ray,

`g_d(t)^2 = sum_i q_di^2 exp(-2 H_i t)` and
`H_d(t) = sum_i H_i q_di^2 exp(-2 H_i t) / g_d(t)^2`.

The geometries are FLRW `[1e-14;3]` and BI
`[1.01e-14,.99e-14,1e-14]` /s. For j>=1 define
`lambda_dj=H_d E_j/(E_j-E_(j-1))` and `F_dj=lambda_dj p_dj`.
For interior reduced nodes j>=1, transport is
`p_dj'=F_d(j+1)-F_dj`, with the incoming flux zero at the highest node.
The j1 downward flux goes directly to the guard:

`N_d'=F_d1`, `U_d'=-H_d U_d +10 F_d1`, `p_d0=0`.

Number including guard is conserved by transport, and its energy derivative is
exactly `-H_d*(sum_j E_j p_dj+U_d)`. Transport work is the positive opposite.
The source rate is `S=5e-15 photons/H/s` at exactly 13.7 eV. The ray weights are
`J_d=exp(-sum_i H_i*t)/g_d^3`, `W_d=J_d/sum_d J_d`; no continuum angular
substitution is made. Photon variables are per H, so they have no `-3H` term.
Proper hydrogen density is `nH=1e-4 exp(-sum H_i*t)` /cm3.

## Chemistry and energy

Let gas variables be `(x,a,b,w)` = HII fraction, HeII fraction, HeIII fraction,
thermal eV/H. Set `f=.083`, `L=[1-x,f(1-a-b),f*a]`,
`A=[x,f*a,f*b]`, `ne=nH*(x+f*(a+2b))`, and
`T=2*w*EV/(3*KB*(1+f+x+f*(a+2b)))`.
`KB=1.380649e-16 erg/K`, `EV=1.602176634e-12 erg/eV`,
`c=29979245800 cm/s`,
`chi=[13.598434599702,24.587389011,54.41776] eV`.

The actual frozen Verner fit cutoffs `[13.60,24.59,54.42] eV` are separate
from chi. For energy below its fit cutoff sigma=0, without clipping heat or
changing thresholds. Above cutoff use
`sigma=1e-18*s0*((X-1)^2+yw^2)*Y^(p/2-5.5)*(1+sqrt(Y/ya))^(-p)`,
`X=E/e0-y0`, `Y=sqrt(X^2+y1^2)`; `(e0,s0,ya,p,yw,y0,y1)` are
HI `(.4298,5.475e4,32.88,2.963,0,0,0)`,
HeI `(13.61,949.2,1.469,3.188,2.039,.4434,2.136)`,
HeII `(1.720,1.369e4,32.88,2.963,0,0,0)`.

Photo events per H per second are
`Pi_k=c*nH*L_k*sum_dj sigma_jk*p_dj`.
Each directional photon sink is
`-c*nH*p_dj*sum_k L_k*sigma_jk`.
Collision and radiative recombination events are `C_k=L_k*ne*beta_k`,
`R_k=A_k*ne*alpha_k`. Dielectronic events are `D_r=A_1*ne*alphaDR_r`.
Set `J=Pi+C-R`, `J_1-=sum D`; then
`x'=J_0`, `a'=(J_1-J_2)/f`, `b'=J_2/f`.

Independent FT03 Case A coefficients use `l=[315614,570670,1263030]/T`.
For HI/HeII,
`alpha=prefactor*1.269e-13*l^1.503/(1+(l/.522)^.470)^1.923`,
prefactor1/2, with logarithmic slope
`s=-1.503+1.923*.470*u/(1+u)`, `u=(l/.522)^.470`.
For HeI `alpha=3e-14*l^.654`, `s=-.654`.
RR kinetic coefficient is `K_k=KB*T*alpha_k*(1.5+s_k)`.
Collision coefficients are
`beta_k=Aci_k*T^-1.5*exp(-l_k/2)*l_k^p_k/(1+(l_k/c_k)^r_k)^d_k`,
where arrays are
`Aci=[21.11,32.38,19.95]`, `p=[-1.089,-1.146,-1.089]`,
`c=[.354,.416,.553]`, `r=[.874,.987,.735]`, `d=[1.101,1.056,1.275]`.
Let `B1=40.49664394833662*11605`, `B2=8.099328789667*11605` K.
DR coefficients are
`1.54e-9*11605^1.5*T^-1.5*[exp(-B1/T),.3*exp(-(B1+B2)/T)]`;
DR kinetic energies are `KB*[B1,B1+B2]` erg.

Photo heating is `Q=sum_djk c*nH*L_k*sigma_jk*p_dj*(E_j-chi_k)` eV/H/s.
With `Kloss=sum_k A_k*ne*K_k/EV`, `Dloss=sum_r D_r*Edr_r/EV`,
the thermal equation is
`w'=Q-sum C_k*chi_k-Kloss-Dloss-2*Hmean*w`.
Expansion contributes `-2Hmean*w` **once**. Escape ledger derivative is
`sum R_k*chi_k +chi_1*sum D +Kloss+Dloss`.
Other ledgers have derivatives redshift work, `2Hmean*w`, S, `13.7*S`,
and `sum Pi`, in that order. There is no density-dilution loss in w per H.
All species, binding, photon, escape, and work terms cancel in the total
energy ledger after subtracting source energy.

## Numerical relation and claim ceiling

Time is scaled as `tau=t/1e10`. DOP853 and RK45 use rtol2e-12,
atol2e-15 times coordinate scales, maximum tau step .025. The gas fraction
scales are1, w/escape/thermal-work scale initial_w, individual photon/guard
N/sourceN/absorption scale .05, guard U/redshift/sourceU scale .685.
The complete scale vector and solver counts are recorded in RESULTS.
The required endpoint agreement is maximum full-coordinate scaled difference
<=1e-8. This is two numerical methods agreeing, not a rigorously enclosed error
bound. Small negative dense-output photon/guard coordinates are recorded
unchanged; no clipping or exact positivity claim is made.

The four initial secants use macro dt1e6,1e5,1e4,1e3 s; they support the local
projected derivative for the birth initial state. Roundoff rises at1e3 s, and
they do not certify arbitrary-state consistency. The separate two-node
analytic solution checks exponential survival and guard retention/redshift.
Historical endpoint parity uses the Host's unit-scaled1e-12 relation with
temperature50000 K, w initial_w, N .05, U .685 scales, retaining actual signed
differences. It does not require identical V1/V2 scientific output bytes.

Scientific admission remains HOLD; continuum time-error certificate,
full-campaign convergence, angular/spectral continuum, global contraction,
physical validity and BI-minus-FLRW sign admission are NOT_ESTABLISHED.
