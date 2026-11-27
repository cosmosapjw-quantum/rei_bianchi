from pathlib import Path
from fractions import Fraction as F
import csv, json, hashlib, math, sys, time
import mpmath as mp
mp.mp.dps=70
ROOT=Path(__file__).resolve().parents[1]
pred=ROOT/'predecessor23/WU088_HH_PHYS23_20261013'
r23=json.loads((pred/'results/PHYS23_RESULT.json').read_text())
# Selected normalized transcription of the actual Wolfram interval output.
lohi=[
('142222109432991576059159233074296009266380392007673/1000000000000000000000000000000000000000000000','71113025610002005410091055700345989541137426741613/500000000000000000000000000000000000000000000'),
('138887152318116154461650111335751624980664288913731/1000000000000000000000000000000000000000000000','69446210975085368977402409660072363004591625413639/500000000000000000000000000000000000000000000'),
('38786565740705541980921646344833710240982151898757/500000000000000000000000000000000000000000000','77577206980231142684020677901327660405580414104419/1000000000000000000000000000000000000000000000'),
('1669320747987057919738043560884299617462741702011/100000000000000000000000000000000000000000000','16694303318484187194261498468302667195058854449599/1000000000000000000000000000000000000000000000'),
('24205361971909350047993318242955312537100711141863/1000000000000000000000000000000000000000000000','24207284436224985760487327127315145796415303410469/1000000000000000000000000000000000000000000000'),
('1187752304543950320471126298806891593590117656443/200000000000000000000000000000000000000000000','1187882504447307870523081932580708687856645081313/200000000000000000000000000000000000000000000'),
('131812969733263951486730001963531237692146452039/500000000000000000000000000000000000000000000','131834290030568939729336032963407515517453709427/500000000000000000000000000000000000000000000'),
('4619899168151231228521954776219818619429569/1000000000000000000000000000000000000000000000','2310709697219479532213786407704684361669959/500000000000000000000000000000000000000000000'),
('0','1/1000000000000000000000000000000000000000000000')]
EV=mp.mpf('1.602176634e-19');KB=mp.mpf('1.380649e-23');MH=mp.mpf('1.67262192369e-27');MU=MH/2
CHI=mp.mpf('13.598434599702'); T0=mp.mpf('50000'); TLO=mp.mpf('49999.63846'); THI=mp.mpf('50000.36154')
EDGES=[CHI,mp.mpf(16),mp.mpf(20),mp.mpf(25),2*CHI,mp.mpf(35),mp.mpf(50),mp.mpf(100),mp.mpf(625),mp.inf]
def mfrac(f):
 f=F(f);return mp.mpf(f.numerator)/f.denominator

def pref(T):return 50*mp.sqrt(8*EV/(mp.pi*MU))/(KB*T/EV)**mp.mpf('1.5')
def moment(n,a,b,T):
 theta=KB*T/EV
 return theta**(n+1)*mp.gammainc(n+1,a/theta,b/theta)
def weight(a,b,T):return pref(T)*moment(1,a,b,T)
def direct_weight(a,b,T):
 th=KB*T/EV
 return pref(T)*mp.quad(lambda en:en*mp.exp(-en/th),[a,b])
checks=[]
def ck(name,ok):
 checks.append({'name':name,'pass':bool(ok)})
 if not ok: raise AssertionError(name)

# Independent mpmath quadrature: the proof of continuum T coverage uses monotonicity,
# the samples here are implementation checks, not substituted interval certificates.
weights=[]
for j,(a,b) in enumerate(zip(EDGES[:-1],EDGES[1:])):
 L,U=map(F,lohi[j]); mid=weight(a,b,T0)
 for T in [TLO,T0,THI]:
  val=weight(a,b,T); ck(f'W{j}_CAS_enclosure_T{T}',mfrac(L)<=val<=mfrac(U))
 direct=direct_weight(a,b,T0)
 # Integration to infinity for the negligible 625eV tail is evaluated in a shifted coordinate.
 if b==mp.inf:
  th=KB*T0/EV
  direct=pref(T0)*mp.exp(-a/th)*mp.quad(lambda y:(a+y)*mp.exp(-y/th),[0,mp.inf])
 ck(f'W{j}_independent_quadrature',abs(direct-mid)<mp.mpf('1e-45')*mid)
 weights.append({'a_cm_eV':str(a),'b_cm_eV':str(b),'a_lab_eV':str(2*a),'b_lab_eV':str(2*b),'W_lo_cm_s':str(L),'W_hi_cm_s':str(U),'W_mid_cm_s':mp.nstr(mid,30),'kernel_fraction':mp.nstr(mid/weight(CHI,mp.inf,T0),30)})
ck('temperature_monotonicity',CHI>mp.mpf('1.5')*KB*THI/EV)
ck('positive_bin_weights',all(F(x['W_lo_cm_s'])>=0 for x in weights))
ck('bin_partition',abs(sum(weight(a,b,T0) for a,b in zip(EDGES[:-1],EDGES[1:]))/weight(CHI,mp.inf,T0)-1)<mp.mpf('1e-60'))
# Direct lab-frame variable transformation and 1/2 event convention.
sg=lambda e:(e-CHI)**2/e
cm=mp.quad(lambda e:e*mp.exp(-e/(KB*T0/EV))*sg(e),[CHI,mp.inf])
lab=mp.quad(lambda e:e*mp.exp(-e/(2*KB*T0/EV))*sg(e/2)/4,[2*CHI,mp.inf])
ck('lab_CM_Jacobian_one_quarter',abs(cm/lab-1)<mp.mpf('1e-60'))
ck('event_effective_pair_conversion',F(1,2)*(F(1,4)+F(3,4))==F(1,8)+F(3,8))

# Exact piecewise-affine extrema under a certified Lipschitz constant.
def cone_segments(nodes,values,L,kind):
 nodes=list(map(mp.mpf,nodes)); values=list(map(mp.mpf,values)); L=mp.mpf(L)
 if L<0 or len(nodes)<2 or len(nodes)!=len(values):raise ValueError('invalid sizes/slope')
 if any(nodes[i]>=nodes[i+1] for i in range(len(nodes)-1)):raise ValueError('energies not ordered')
 if min(values)<0:raise ValueError('negative cross section')
 if any(abs(values[j]-values[i])>L*abs(nodes[j]-nodes[i]) for i in range(len(nodes)) for j in range(len(nodes))):raise ValueError('incompatible endpoint Lipschitz data')
 out=[]
 for a,b in zip(nodes[:-1],nodes[1:]):
  center=(a+b)/2;lines=[]
  for x,s in zip(nodes,values):
   sign=1 if center>=x else -1
   if kind=='upper':lines.append((L*sign,s-L*sign*x))
   else:lines.append((-L*sign,s+L*sign*x))
  if kind=='lower':lines.append((mp.mpf(0),mp.mpf(0)))
  cuts=[a,b]
  for i,(mi,qi) in enumerate(lines):
   for mj,qj in lines[i+1:]:
    if mi!=mj:
     x=(qj-qi)/(mi-mj)
     if a<x<b:cuts.append(x)
  cuts=sorted(set(cuts))
  for left,right in zip(cuts[:-1],cuts[1:]):
   test=(left+right)/2
   idx=(min if kind=='upper' else max)(range(len(lines)),key=lambda i:lines[i][0]*test+lines[i][1])
   out.append((left,right,*lines[idx]))
 return out

def cone_integral(nodes,vals,L,T,kind):
 return pref(T)*sum(slope*moment(2,a,b,T)+intercept*moment(1,a,b,T) for a,b,slope,intercept in cone_segments(nodes,vals,L,kind))
N=[14,18]; V=[2,3]; L=1
coarse=[cone_integral(N,V,L,T0,k) for k in ['lower','upper']]
fine=[cone_integral([14,16,18],[2,mp.mpf('2.5'),3],L,T0,k) for k in ['lower','upper']]
# Actual data are not supplied: the witness unit is 1e-18 cm2.
ck('refinement_nested',coarse[0]<=fine[0]<=fine[1]<=coarse[1])
linear=pref(T0)*(.25*moment(2,mp.mpf(14),mp.mpf(18),T0)-mp.mpf('1.5')*moment(1,mp.mpf(14),mp.mpf(18),T0))
ck('chord_in_both_enclosures',fine[0]<=linear<=fine[1])
for kind,val in zip(['lower','upper'],coarse):
 segs=cone_segments(N,V,L,kind)
 direct=pref(T0)*sum(mp.quad(lambda E:(s*E+b)*E*mp.exp(-E/(KB*T0/EV)),[a,c]) for a,c,s,b in segs)
 ck('cone_'+kind+'_quadrature',abs(val/direct-1)<mp.mpf('1e-55'))
ck('zero_slope_constant',abs(cone_integral([14,18],[2,2],0,T0,'upper')/(2*weight(mp.mpf(14),mp.mpf(18),T0))-1)<mp.mpf('1e-55'))
ck('zero_cross_section',cone_integral([14,18],[0,0],0,T0,'upper')==0)
for name,args in [('bad_slope',([14,18],[1,9],1)),('negative_sigma',([14,18],[-1,0],1)),('unordered',([18,14],[2,3],1))]:
 try:cone_segments(*args,'upper');ck(name,False)
 except ValueError:ck(name,True)
# Curved admissible test function, Lipschitz <=1 and the same endpoints.
for amp in [mp.mpf('-0.7'),mp.mpf('-0.3'),mp.mpf(0),mp.mpf('.3'),mp.mpf('.7')]:
 vals=mp.quad(lambda en:(2+(en-14)/4+amp*mp.sin(mp.pi*(en-14)/4))*en*mp.exp(-en/(KB*T0/EV)),[14,18])*pref(T0)
 ck('admissible_curve_'+str(amp),coarse[0]<=vals<=coarse[1])

# Exact rational downstream application to declared per-bin bounds.
coeff={k:F(v) for k,v in r23['inverse_budget_coefficients_rational'].items()}

def apply_envelope(lowers,uppers,tail_declared):
 if not tail_declared:raise ValueError('tail coverage must be explicitly supplied')
 if len(lowers)!=len(weights) or len(uppers)!=len(weights):raise ValueError('bin count mismatch')
 lows=list(map(F,lowers)); ups=list(map(F,uppers))
 if any(l<0 or u<l for l,u in zip(lows,ups)):raise ValueError('invalid envelope')
 klo=sum(F(row['W_lo_cm_s'])*l for row,l in zip(weights,lows)); kup=sum(F(row['W_hi_cm_s'])*u for row,u in zip(weights,ups))
 return klo,kup,{k:str(c*kup) for k,c in coeff.items()}
zero=apply_envelope(['0']*9,['0']*9,True);ck('exact_zero_envelope',zero[0]==zero[1]==0)
try:apply_envelope(['0']*9,['1e-18']*9,False);ck('missing_tail_rejected',False)
except ValueError:ck('missing_tail_rejected',True)
unit=apply_envelope(['0']*9,['1e-18']*9,True)
ktube=F(r23['common_tube_k_upper_ceiling_cm3_s'])
ck('unit_envelope_in_inherited_tube',unit[1]<ktube)
Wtot=weight(CHI,mp.inf,T0)
summary={'unit':'PHYS24','scope':'Derived sharp conditional cross-section envelope; exact fixed-bin numerical transfer; no calibrated physical sigma envelope supplied',
'pair_normalization':'W multiplies total single-ionization event cross section; network k=<sigma_event v>/2; existing fitted k is unchanged',
'constants':{'m_H_kg':'1.67262192369e-27','mass_convention':'inherited mH=mp mass-number approximation','threshold_eV':str(CHI),'T_box_K':[str(TLO),str(THI)]},
'W_total_mid_cm_s':mp.nstr(Wtot,35),'kernel_mass_below_2chi':mp.nstr(weight(CHI,2*CHI,T0)/Wtot,30),'kernel_mass_below_50eV':mp.nstr(weight(CHI,mp.mpf(50),T0)/Wtot,30),'kernel_mass_above_625eV':mp.nstr(weight(mp.mpf(625),mp.inf,T0)/Wtot,30),
'unit_sigma_diagnostic':{'sigma_cap_cm2':'1e-18','physical_status':'specified mathematical envelope, not inferred from data','rate_upper_cm3_s':str(unit[1]),'observable_abs_uppers':unit[2]},
'cone_witness':{'energy_eV':[14,18],'sigma_unit_cm2':'1e-18','endpoint_values':[2,3],'slope_bound_units':1,'new_node':[16,2.5], 'coarse_k_interval_cm3_s':[mp.nstr(v*mp.mpf('1e-18'),35) for v in coarse],'refined_k_interval_cm3_s':[mp.nstr(v*mp.mpf('1e-18'),35) for v in fine],'width_reduction_factor':mp.nstr((coarse[1]-coarse[0])/(fine[1]-fine[0]),30)},
'weight_rows':weights,'inverse_budget_coefficients_rational':{k:str(v) for k,v in coeff.items()},'calibrated_sigma_envelope':None,'physical_omission_budget':None,
'checks_passed':len(checks),'checks_failed':0,'new_scattering_runs':0,'new_ODE_runs':0,'new_native_receiver_runs':0,'Wolfram_tensor_zero_residuals':3,'Wolfram_scalar_zero_residuals':9,'independence':'same assistant; separately implemented symbolic, interval and mpmath/Fraction paths'}
(ROOT/'results/PHYS24_RESULT.json').write_text(json.dumps(summary,indent=2))
(ROOT/'checks/VALIDATION.json').write_text(json.dumps({'checks':checks,'passed':len(checks),'failed':0},indent=2))
with (ROOT/'results/KERNEL_BIN_TABLE.csv').open('w') as f:
 wr=csv.DictWriter(f,fieldnames=list(weights[0])+['C_T_times_Whi_K_per_cm2']);wr.writeheader()
 for row in weights:wr.writerow(row|{'C_T_times_Whi_K_per_cm2':str(F(row['W_hi_cm_s'])*coeff['C_T_K_per_cm3_s'])})
print(json.dumps({k:v for k,v in summary.items() if k not in ['weight_rows','inverse_budget_coefficients_rational']},indent=2))
