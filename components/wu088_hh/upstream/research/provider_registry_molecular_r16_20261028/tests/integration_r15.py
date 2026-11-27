"""R16 -> unchanged, git-blob-pinned R15 real engine end-to-end fixture."""
import sys, json, subprocess, tempfile, hashlib, os
from pathlib import Path
from fractions import Fraction as Q
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import r16_nonnegative_cubic as m
ROOT=Path(__file__).resolve().parents[1]
R15=ROOT/'parent/research/provider_registry_molecular_r15_20261028/src/cubic_convolution.py'

def make_case():
 b=[Q(1,9),Q(-1,9),Q(-2,9),Q(4,9)]
 # This is not necessarily the actual coefficients of (t-1/3)^2: create from polynomial powers explicitly.
 p=(Q(1,9),Q(-2,3),Q(1),Q(0))
 b=[p[0],p[0]+p[1]/3,p[0]+2*p[1]/3+p[2]/3,sum(p)]
 gr=[[str(x) for x in b]];ge=[['0']*4]
 binding={'source_id':'R16_SYNTHETIC_NONNEGATIVE_CUBIC','clock_id':'synthetic-t','clock_unit':'s',
    'full_A_family_id':'ARITHMETIC_PREMISE_ONLY','source_locator':'synthetic:exact-polynomial',
    'source_sha256':'f'*64,'whole_forcing_source_sha256':'',
    'scientific_status':'ARITHMETIC_CONTROL_PREMISE','state_order':['x0','x1'],
    'whole_forcing_hash_format':m.R15_FORCING_SCHEMA}
 hh=m.canonical_r15_hash([Q(0),Q(1)],[b],[list(map(Q,ge[0]))],binding)
 binding['whole_forcing_source_sha256']=hh
 cert=dict(binding);cert.update({'generator':'A=K+wH;H=pi*d^T-diag(d)',
     'fixed_K_pi_d':True,'full_w_box':True,'all_start_times':True,
     'zero_mass_residual':True,'short_remainder_nonexpansive':True,
     'forcing_whole_fine_coarse_domain':True,'q':'1/2','tau':'1',
     't0':'0','T':'1','w_box':['0','1']})
 return {'states':2,'q':'1/2','tau':'1','c':'1','d':'-1',
         'initial':['0','0'],'source_knots':['0','1'],
         'observation_knots':['0','1'],
         'g_r':gr,'g_e':ge,'binding':binding,'certificate':cert}

if __name__=='__main__':
 case=make_case()
 p=ROOT/'results/R16_INTEGRATION_INPUT.json'
 p.write_text(json.dumps(case,indent=2,sort_keys=True)+'\n')
 out=ROOT/'results/R16_INTEGRATED_R15_RESULT.json'
 cmd=[sys.executable,str(ROOT/'src/r16_cli.py'),'--input',str(p),'--output',str(out),'--r15-core',str(R15)]
 proc=subprocess.run(cmd,capture_output=True,text=True)
 print('cmd', ' '.join(cmd),'rc',proc.returncode,'stderr',proc.stderr[:1000]);
 assert out.exists()
 data=json.loads(out.read_text());print('status',data['status'])
 if proc.returncode:print('reason',data);raise SystemExit(proc.returncode)
 assert data['lineage']['refined_cells']>=2
 print('r15_output_keys',list(data['R15_result'])[:10])
 print('result_bytes',out.stat().st_size)
