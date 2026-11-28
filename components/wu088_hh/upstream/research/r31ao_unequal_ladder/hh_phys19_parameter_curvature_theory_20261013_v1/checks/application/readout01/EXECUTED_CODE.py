#!/usr/bin/env python3
"""Exact rational interval readout of the inherited/current finite response."""
import argparse,json,hashlib,pathlib,datetime
from fractions import Fraction as Q
from decimal import Decimal,localcontext,ROUND_FLOOR,ROUND_CEILING
class Interval:
 def __init__(self,a,b=None):
  self.a=Q(a);self.b=Q(a if b is None else b);assert self.a<=self.b
 def __add__(self,y):
  if not isinstance(y,Interval):y=Interval(y)
  return Interval(self.a+y.a,self.b+y.b)
 __radd__=__add__
 def __neg__(self):return Interval(-self.b,-self.a)
 def __sub__(self,y):return self+-y if isinstance(y,Interval) else self+Interval(-y)
 def __mul__(self,y):
  if not isinstance(y,Interval):y=Interval(y)
  z=[self.a*y.a,self.a*y.b,self.b*y.a,self.b*y.b];return Interval(min(z),max(z))
 __rmul__=__mul__
 def __truediv__(self,y):
  if not isinstance(y,Interval):y=Interval(y)
  assert not y.a<=0<=y.b
  return self*Interval(1/y.b,1/y.a)
 def square(self):return Interval(0 if self.a<=0<=self.b else min(self.a**2,self.b**2),max(self.a**2,self.b**2))
 def intersect(self,y):return Interval(max(self.a,y.a),min(self.b,y.b))
 def mag(self):return max(abs(self.a),abs(self.b))
 def midpoint(self):return (self.a+self.b)/2
 def radius(self):return (self.b-self.a)/2
 def record(self):
  d=[]
  for x,mode in [(self.a,ROUND_FLOOR),(self.b,ROUND_CEILING)]:
   with localcontext() as c:c.prec=13;c.rounding=mode;d.append(str(Decimal(x.numerator)/Decimal(x.denominator)))
  return {'exact':{'lo':[str(self.a.numerator),str(self.a.denominator)],'hi':[str(self.b.numerator),str(self.b.denominator)]},'outward_decimal':d,'sign':'STRICT_NEGATIVE' if self.b<0 else 'STRICT_POSITIVE' if self.a>0 else 'ZERO_CONTAINING'}
def read(x):return Interval(Q(*map(int,x['exact']['lo'])),Q(*map(int,x['exact']['hi'])))
def write(x):
 if isinstance(x,Interval):return x.record()
 if isinstance(x,dict):return {k:write(v) for k,v in x.items()}
 if isinstance(x,list):return [write(v) for v in x]
 return x

def main(source,output):
 data=source.read_bytes();r=json.loads(data);fin=r['finite_response']
 A,D,M=[read(fin[k]) for k in ['F_lambda_lambda_K','F_b_b_K','interaction_coefficient_K']]
 # PHYS18 certifies the same interval for F_lambda_b and the integral coefficient.
 det=A*D-M.square();counter=A-M/12+D/576
 assert A.b<0 and D.b<0 and det.b<0 and counter.a>0
 al,ab,f00=[read(fin[k]) for k in ['chord_a_lambda_K','chord_a_b_K','anchor_F00_K']]
 assert al.b<0 and ab.a>0
 # Every one of the four same-family corners also belongs to the global F range.
 anchor=f00.intersect(f00-al).intersect(f00-ab).intersect(f00-al-ab-M)
 bilinear=(A.mag()+D.mag())/8;corrected=(A.radius()+D.radius())/8
 # Define displayed usable coefficients as exact finite decimals, preserving the extra rounding error.
 cA=Q('-3.797385260416e-14');cD=Q('-4.681380466304e-11')
 rA=max(abs(A.a-cA),abs(A.b-cA));rD=max(abs(D.a-cD),abs(D.b-cD))
 fixed_corrected=(rA+rD)/8
 # Deterministic polynomial uses centers; coefficient uncertainty remains explicit.
 coeff={'anchor':anchor,'lambda_chord':al,'birth_chord':ab,'interaction':M}
 radii={k:Interval(v.radius()) for k,v in coeff.items()}
 total_midpoint_error=anchor.radius()+al.radius()+ab.radius()+M.radius()+fixed_corrected
 result={'schema':'WU088_HH_PHYS19_CURVATURE_GEOMETRY_V1','status':'computed',
 'input':{'path':str(source),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()},
 'arithmetic':'exact Fraction interval operations without dyadic rounding',
 'hessian':{'lambda_lambda_K':A,'lambda_b_K':M,'b_b_K':D,'determinant_K2':det,
             'classification':'one positive and one negative eigenvalue at each parameter point',
             'countervariation_direction':['1','-1/24'],'countervariation_curvature_K':counter,
             'direction_domain':'line segments entirely in [0,1]^2; same fixed admissible alpha'},
 'interpolation':{'signed_error_center_K':-(A+D)/8,'bilinear_abs_bound_K':Interval(bilinear),
                  'pure_midpoint_abs_bound_K':Interval(corrected),
                  'improvement_factor':Interval(bilinear/corrected),
                  'usable_fixed_decimal_coefficients_K':{'lambda_lambda':str(cA),'b_b':str(cD)},
                  'usable_fixed_decimal_radii_K':{'lambda_lambda':Interval(rA),'b_b':Interval(rD)},
                  'fixed_decimal_correction_abs_bound_K':Interval(fixed_corrected),
                  'birth_fraction_of_bilinear_bound':Interval(D.mag()/(A.mag()+D.mag()))},
 'coefficient_resolution':{'original_F_global_K':f00,'corner_consistent_F00_K':anchor,
                  'coefficient_intervals_K':coeff,'midpoints_exact_K':{k:[str(v.midpoint().numerator),str(v.midpoint().denominator)] for k,v in coeff.items()},
                  'radii_K':radii,'anchor_width_reduction_fraction':Interval(1-anchor.radius()/f00.radius()),
                  'deterministic_midpoint_model_uniform_error_bound_K':Interval(total_midpoint_error),
                  'deterministic_model':'m0+ml*lambda+mb*b+mm*lambda*b-cA*lambda*(1-lambda)/2-cD*b*(1-b)/2',
                  'pointwise_error_formula':'r0+rl*lambda+rb*b+rm*lambda*b+rA*lambda*(1-lambda)/2+rD*b*(1-b)/2',
                  'coupling':'Each exact coefficient is a corner value/difference of one fixed-alpha family; no independent physical variation is introduced.'},
 'execution':{'source_calls':0,'root_solves':0,'history_replays':0,'completed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}}
 output.mkdir(parents=True,exist_ok=False);(output/'CURVATURE_GEOMETRY.json').write_text(json.dumps(write(result),ensure_ascii=False,indent=2)+'\n')
 summary={
 'determinant_K2':det.record(),'countervariation_curvature_K':counter.record(),
 'bilinear_abs_bound_K':Interval(bilinear).record(),'pure_midpoint_abs_bound_K':Interval(corrected).record(),
 'fixed_decimal_correction_abs_bound_K':Interval(fixed_corrected).record(),'improvement_factor':Interval(bilinear/corrected).record(),
 'anchor_F00_K':anchor.record(),'total_midpoint_model_error_bound_K':Interval(total_midpoint_error).record()}
 (output/'SUMMARY.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({k:v['outward_decimal'] for k,v in summary.items()},ensure_ascii=False,indent=2))
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--source',type=pathlib.Path,required=True);a.add_argument('--output',type=pathlib.Path,required=True);x=a.parse_args();main(x.source.resolve(),x.output.resolve())
