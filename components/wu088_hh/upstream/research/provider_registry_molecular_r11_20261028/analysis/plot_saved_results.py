"""Saved JSON postprocessing only: no scientific module, solver, or ODE import."""
from pathlib import Path
from fractions import Fraction as Q
from decimal import Decimal, localcontext
import hashlib
import json
import os
import sys

BASE = Path(__file__).resolve().parents[1]
REPO = BASE.parents[1]
P = BASE/'raw/PRIMARY_RESULTS.json'
OLD = BASE.parent/'provider_registry_molecular_r10_20261028/raw/PRIMARY_RESULTS.json'
REF = BASE/'raw/REFERENCE_RESULTS.json'
OUT = BASE/'analysis'
FIG = BASE/'figures'
R10_SHA='1713df54bc3653003614f3deba93212735a345e8d7220f053ab9af2d84677fb1'
NAMES = {
 'two_state_no_reaction': ('무반응 2상태', 'Two-state: no reaction'),
 'two_state_nonlinear': ('비선형 2상태', 'Two-state: nonlinear reaction'),
 'two_state_coarse_source_defect': ('coarse source defect 2상태', 'Two-state: coarse source defect'),
 'saved_native_nine_state_K_conditional_feedback': ('native9 K + 합성 조건부 반응', 'Native nine-state K + synthetic conditional reaction'),
}

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def desc(q):
 q=Q(q)
 with localcontext() as ctx:
  ctx.prec=60
  return {'exact':str(q),'decimal':str(Decimal(q.numerator)/Decimal(q.denominator))}
def pct(a,b): return None if a==0 else desc(100*(a-b)/a)
def tableval(q): return f'{float(Q(q)):.12g}'
def serialize(v):
 if isinstance(v,Q): return str(v)
 if isinstance(v,dict):return {k:serialize(x) for k,x in v.items()}
 if isinstance(v,(list,tuple)):return [serialize(x) for x in v]
 return v

def stats(new,old):
 counts={}
 for k,key in enumerate(('R','E')):
  pairs=[(Q(a[k]),Q(b[k])) for a,b in zip(new,old)]
  counts[key]={'less':sum(a<b for a,b in pairs),'equal':sum(a==b for a,b in pairs),'greater':sum(a>b for a,b in pairs)}
 counts['all']={c:sum(counts[k][c] for k in ('R','E')) for c in ('less','equal','greater')}
 return counts

def improvement(new,old,k):
 rows=[]
 for i,(newrow,oldrow) in enumerate(zip(new,old)):
  b,a=Q(newrow[k]),Q(oldrow[k])
  if b<a: rows.append({'cell_index':i,'difference':desc(a-b),'percent':pct(a,b),'one_dyadic128_ulp':a-b==Q(1,1<<128)})
 if not rows:return {'improved_cells':0,'max_percent':None,'all_differences_one_dyadic128_ulp':False}
 best=max(rows,key=lambda row:Q(row['percent']['exact']))
 return {'improved_cells':len(rows),'max_percent':best,'all_differences_one_dyadic128_ulp':all(x['one_dyadic128_ulp'] for x in rows), 'improved_cell_indices':[x['cell_index'] for x in rows]}

def main():
 OUT.mkdir(exist_ok=True);FIG.mkdir(exist_ok=True)
 assert sha(OLD)==R10_SHA
 p,old=json.loads(P.read_text()),json.loads(OLD.read_text())
 assert p['status']=='PASS' and old['status']=='PASS'
 assert [x['id'] for x in p['hd_cases']]==[x['id'] for x in old['hd_cases']]
 summary={'schema':'WU_R11_SAVED_OUTPUT_ANALYSIS_V1','unit':p['unit'],
          'scope':{'solver_calls':0,'production_module_imports':0,'reference_solver_calls':0,'ODE_calls':0,
                   'operation':'exact Fraction comparisons of saved arrays; plotting converts only display coordinates to binary floats'},
          'sources':{'R11_primary':{'path':str(P.relative_to(REPO)),'bytes':P.stat().st_size,'sha256':sha(P)},
                     'R10_primary':{'path':str(OLD.relative_to(REPO)),'bytes':OLD.stat().st_size,'sha256':sha(OLD)}},
          'primary':{'status':p['status'],'checks':p['check_count'],'failures':p['failure_count']},
          'cases':[], 'all_capped_endpoints_exactly_equal_R10':True,
          'endpoint_lines':'visual connectors through certified point bounds; no between-point certification from connectors',
          'whole_cell_steps':'each height is an upper certificate on its exact closed cell; at a shared endpoint both adjacent certificates apply',
          'lower_arrays':'ideal chosen-rational-q comparison only, never a lower bound on physical error',
          'physical_status':{'actual_HD_reactive_array':'INPUT_PENDING','named_physical_consumer_density_clock':'INPUT_PENDING',
                             'HH_R10':'OFF','production':'NOT_ISSUED','L4_ready':False,'central_delta':0,'physical_delta':0,
                             'native_case':'native K + synthetic conditional reaction fixture; native v=UNSPECIFIED, MISSING_NOT_ZERO; TIQM/SQM kept distinct'}}
 for x,o in zip(p['hd_cases'],old['hd_cases']):
  gen=x['raw']['generator'];baseline=o['capped'];case={'id':x['id'],'source_scope':x['source_scope'],'tau':desc(gen['tau']),
    'q_K':desc(gen['rho_K']),'q_additive':desc(gen['q_additive']),'q_minorization_interval':[desc(t) for t in gen['q_minorization_interval']],
    'q_chosen':desc(gen['q']),'strict_implemented_contraction':gen['strict_implemented_contraction'],
    'endpoint_count':193,'whole_cell_count':192,'components':['R','E'],'counts':{},'final':{},'capped_whole_improvement':{}}
  for mode in ('raw','capped'):
   case['counts'][mode]={}
   for key in ('endpoints_upper','whole_cells_upper'):
    count=stats(x[mode][key],baseline[key]);case['counts'][mode][key]=count
    assert count['all']==x['comparison'][mode+'_'+key+'_counts']
   case['final'][mode]={k:desc(x[mode]['endpoints_upper'][-1][i]) for i,k in enumerate(('R','E'))}
  case['final']['R10_capped']={k:desc(baseline['endpoints_upper'][-1][i]) for i,k in enumerate(('R','E'))}
  case['final']['capped_improvement_percent']={k:pct(Q(baseline['endpoints_upper'][-1][i]),Q(x['capped']['endpoints_upper'][-1][i])) for i,k in enumerate(('R','E'))}
  case['final']['raw_improvement_percent']={k:pct(Q(baseline['endpoints_upper'][-1][i]),Q(x['raw']['endpoints_upper'][-1][i])) for i,k in enumerate(('R','E'))}
  case['capped_endpoints_exactly_equal_R10']=all(Q(a)==Q(b) for aa,bb in zip(x['capped']['endpoints_upper'],baseline['endpoints_upper']) for a,b in zip(aa,bb))
  summary['all_capped_endpoints_exactly_equal_R10'] &= case['capped_endpoints_exactly_equal_R10']
  for k,name in enumerate(('R','E')):case['capped_whole_improvement'][name]=improvement(x['capped']['whole_cells_upper'],baseline['whole_cells_upper'],k)
  summary['cases'].append(case)
 controls={x['id']:x for x in p['controls']}
 jump=controls['block_jump_left_limit']['raw'];late=controls['late_forcing_q0']['raw']
 summary['discriminating_controls']={'block_jump_left_limit':{'cell_index':1,'whole_R':jump['whole_cells_upper'][1][0],
   'right_endpoint_R':jump['endpoints_upper'][2][0],'right_left_limit_R_interval':jump['R_affine_cells'][1]['right_left_limit_interval']},
   'late_forcing_q0':{'final_R':late['endpoints_upper'][-1][0],'final_E':late['endpoints_upper'][-1][1],'h0':late['h0'],
   'current_forcing_cell':3,'current_forcing_rate':1},
   'additive_saturation':next(x['certificate'] for x in p['generator_controls'] if x['id']=='additive_saturation')}
 cpu=[]
 for lane in ('PRIMARY','REFERENCE'):
  path=BASE/f'raw/{lane}_PROCESS.json'
  if path.exists():
   d=json.loads(path.read_text());cpu.append(d['OS_CPU_s']);summary[lane.lower()+'_process']={k:d[k] for k in ['source_commit','returncode','OS_CPU_s','wall_s','includes_imports_and_serialization']}
 summary['new_scientific_python_OS_CPU_sum_s']=sum(cpu)
 if REF.exists():
  r=json.loads(REF.read_text());assert r['primary_sha256']==sha(P)
  summary['reference']={k:r[k] for k in ['status','check_count','failure_count','component_comparisons','exact_component_comparisons','decimal_component_comparisons','sample_component_comparisons','failed_components','Decimal_precision']}
  summary['reference']['guard']=r['scope']['guard']
  samples=[x for x in r['checks'] if x['name'].endswith(':saved_sample_tolerance')]
  summary['saved_samples']={'checks':samples,'criterion':'inherited atol2e-12+rtol2e-10; sample points are validation only, never caps',
   'all_tolerance_checks_pass':all(x['status']=='PASS' for x in samples),
   'all_strict_sample_containment':all(x['evidence']['strict_sample_containment'] for x in samples),
   'strictly_above_upper_component_count':sum(x['evidence']['strictly_above_upper_component_count'] for x in samples)}
  maxrow=max(samples,key=lambda x:Decimal(x['evidence']['maximum_actual_positive_excess']['excess']))
  summary['saved_samples']['maximum_actual_positive_excess']={'check':maxrow['name'],**maxrow['evidence']['maximum_actual_positive_excess']}
  summary['saved_samples']['historical_R10_max_excess_preserved']='4.0013206434938575e-12 (original binary-float postprocessing); current exact-rational/Decimal comparison is a distinct representation-level readout'
  summary['sources']['R11_reference']={'path':str(REF.relative_to(REPO)),'bytes':REF.stat().st_size,'sha256':sha(REF)}
 else:summary['reference']={'status':'NOT_YET_READ'}
 cas=BASE/'raw/CAS_ASSESSMENT.json'
 if cas.exists():summary['CAS']=json.loads(cas.read_text())
 (OUT/'SAVED_OUTPUT_SUMMARY.json').write_text(json.dumps(serialize(summary),indent=2,ensure_ascii=False)+'\n')
 os.environ.setdefault('MPLCONFIGDIR','/tmp/wu_r11_savedplot_mpl')
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 from matplotlib.lines import Line2D
 plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.titlesize':11,'axes.labelsize':10,'svg.hashsalt':'WU_R11_SAVED_OUTPUT_PLOTS_V1'})
 palette={'R10 capped':'#4D5359','R11 raw':'#1566A4','R11 capped':'#CC6B28'}
 lines=[Line2D([0],[0],color=palette[n],lw=2,ls='--' if n=='R11 capped' else '-') for n in palette]
 figs=[]
 def save(fig,name):
  for ext in ('png','svg'):
   path=FIG/(name+'.'+ext)
   temp=path.with_name(path.stem+'.temporary.'+ext)
   fig.savefig(temp,dpi=180,facecolor='white',metadata={'Date':None} if ext=='svg' else {'Software':'WU R11 saved-output postprocessing'})
   if ext=='png':
    from PIL import Image
    with Image.open(temp) as im:im.verify()
   os.replace(temp,path)
   figs.append({'path':str(path.relative_to(BASE)),'bytes':path.stat().st_size,'sha256':sha(path)})
  plt.close(fig)
 for whole,filename in [(False,'BOUND_ENDPOINTS'),(True,'WHOLE_CELL_CERTIFICATES')]:
  fig,axes=plt.subplots(4,2,figsize=(12.8,13.8))
  fig.subplots_adjust(left=.09,right=.97,top=.90,bottom=.10,hspace=.42,wspace=.24)
  fig.suptitle('Closed-cell upper certificates' if whole else 'Certified endpoint values: connectors are visual guides',fontsize=17,y=.98)
  fig.text(.5,.945,'Every R11 capped endpoint equals its R10 capped endpoint exactly (all four fixtures).',ha='center',fontsize=11)
  fig.legend(lines,list(palette),loc='upper center',ncol=3,bbox_to_anchor=(.5,.93),frameon=False)
  for row,(x,o) in enumerate(zip(p['hd_cases'],old['hd_cases'])):
   m=x['raw']['block_steps'];N=x['raw']['cells'];clock=[n/m for n in range(N+1)]
   data={'R10 capped':o['capped'],'R11 raw':x['raw'],'R11 capped':x['capped']}
   for k,col in enumerate(('R','E')):
    ax=axes[row,k]
    for label,d in data.items():
     key='whole_cells_upper' if whole else 'endpoints_upper';values=[float(Q(v[k])) for v in d[key]]
     style={'color':palette[label],'lw':2 if label=='R10 capped' else 1.5,'ls':'--' if label=='R11 capped' else '-', 'zorder':3 if label=='R11 capped' else 2}
     if whole:ax.stairs(values,clock,baseline=None,**style)
     else:ax.plot(clock,values,**style)
    ax.set_title(NAMES[x['id']][1]+' / '+col)
    ax.set_xlabel(r'Exact time / $\tau$');ax.set_ylabel(col+' upper [declared density units]')
    ax.set_xlim(0,3);ax.grid(alpha=.22)
    if row==3 and k==0:ax.set_yscale('log')
    if row==0 and k==1:ax.set_ylim(-.05,.05);ax.text(.5,.65,'E = 0 for every stored bound',transform=ax.transAxes,ha='center')
    elif k==1:ax.ticklabel_format(axis='y',style='sci',scilimits=(-3,3))
  caption=('Each step height bounds its entire exact closed cell. Shared endpoints satisfy both adjacent certificates.\n'
           if whole else 'Lines only connect certified endpoint bounds; they do not certify intermediate times.\n')
  caption+='Native nine-state K is paired with a synthetic conditional reaction fixture. E = |eta|; coarse l1 = 4E.'
  fig.text(.5,.035,caption,ha='center',va='center',fontsize=10)
  save(fig,filename)
 fig,axes=plt.subplots(2,2,figsize=(12.8,8.7));fig.subplots_adjust(left=.085,right=.97,top=.89,bottom=.10,hspace=.38,wspace=.25)
 fig.suptitle('Block age, fresh forcing, and limited whole-cell changes',fontsize=16,y=.975)
 native=p['hd_cases'][-1]['raw'];h=[float(Q(v)) for v in native['kernel_upper']]
 axes[0,0].stairs(h[:-1],[n/64 for n in range(193)],baseline=None,color=palette['R11 raw'],lw=2)
 axes[0,0].plot([3],[h[-1]],'o',color=palette['R11 raw']);axes[0,0].set_yscale('log')
 axes[0,0].set_title('Native9 full-A kernel: every start, every allowed w')
 axes[0,0].text(.04,.08,'q = '+tableval(native['q'])+'; h(0) = 1',transform=axes[0,0].transAxes)
 axes[0,0].set_xlabel(r'Age / $\tau$');axes[0,0].set_ylabel('h upper')
 jj=controls['block_jump_left_limit']['raw'];xx=[n/2 for n in range(7)]
 axes[0,1].stairs([float(Q(v[0])) for v in jj['whole_cells_upper']],xx,baseline=None,label='Closed-cell R upper',color=palette['R11 capped'],lw=2)
 axes[0,1].plot(xx,[float(Q(v[0])) for v in jj['endpoints_upper']],'o',label='Exact endpoint R bound',color=palette['R11 raw'])
 axes[0,1].scatter([1],[1],marker='D',s=55,facecolors='white',edgecolors='#212121',zorder=6,label='Right left-limit')
 axes[0,1].set_title('Block jump: whole bound 1, right endpoint 1/2')
 axes[0,1].set_xlabel(r'Age / $\tau$');axes[0,1].set_ylabel('R upper');axes[0,1].legend(fontsize=8)
 ll=controls['late_forcing_q0']['raw'];clock=[n for n in range(5)]
 axes[1,0].plot(clock,[float(Q(v[0])) for v in ll['endpoints_upper']],'o-',color=palette['R11 raw'],label='R endpoint bound')
 axes[1,0].plot(clock,[float(Q(v[1])) for v in ll['endpoints_upper']],'s--',color=palette['R11 capped'],label='E endpoint bound')
 axes[1,0].axvspan(3,4,color='#6DB0D8',alpha=.18,label='Fresh forcing cell')
 axes[1,0].set_title('q = 0 control: fresh source enters with h0 = 1')
 axes[1,0].text(.04,.55,'Final R = 1/8\nFinal E = 1/128',transform=axes[1,0].transAxes)
 axes[1,0].set_xlabel(r'Exact time / $\Delta$');axes[1,0].set_ylabel('Endpoint upper');axes[1,0].legend(fontsize=8,loc='upper left')
 for i,color in ((1,'#1566A4'),(2,'#945B91')):
  x,o=p['hd_cases'][i],old['hd_cases'][i]
  values=[]
  for new,oldv in zip(x['capped']['whole_cells_upper'],o['capped']['whole_cells_upper']):
   a,b=Q(oldv[1]),Q(new[1]);values.append(float(100*(a-b)/a) if a else 0.0)
  axes[1,1].stairs(values,[n/64 for n in range(193)],baseline=None,color=color,label='Nonlinear' if i==1 else 'Coarse source defect')
 axes[1,1].set_title('Capped whole-cell E improvement is small and local')
 axes[1,1].set_xlabel(r'Exact time / $\tau$');axes[1,1].set_ylabel('100 (R10 - R11) / R10 [%]')
 axes[1,1].ticklabel_format(axis='y',style='sci',scilimits=(-3,3));axes[1,1].legend(fontsize=9)
 for ax in axes.flat:ax.grid(alpha=.22)
 fig.text(.5,.025,'Control endpoint connectors are guides. Whole-cell step heights are certificates. Final capped endpoint improvements are 0%.',ha='center',fontsize=10)
 save(fig,'KERNEL_CONTROL_DIAGNOSTICS')
 (FIG/'FIGURE_MANIFEST.json').write_text(json.dumps({'schema':'WU_R11_FIGURE_MANIFEST_V1','files':figs,'source_primary_sha256':sha(P),'source_R10_sha256':sha(OLD),'producer':'analysis/plot_saved_results.py','scientific_solver_calls':0},indent=2)+'\n')
 lines=['# R11 저장 결과 분석','',
  '**R11 capped endpoint는 네 사례의 모든 저장 시각에서 R10 capped와 정확히 같다. 최종 R·E 상계 개선은 0%다.** 새 결과는 전체 A family에 대한 유한 블록 인증과 forcing convolution의 구현이며, 현재 저장 사례의 final upper 개선과 구별한다.','',
  '## 실제 검증과 비용','',
  f"Primary {p['check_count']}/{p['check_count']} PASS. 독립 reference {summary['reference'].get('check_count','PENDING')}/{summary['reference'].get('check_count','PENDING')} PASS, component comparisons {summary['reference'].get('component_comparisons','PENDING'):,}, 실패 0. Python 각 1회, 전체 OS CPU 합 {summary['new_scientific_python_OS_CPU_sum_s']:.6f}초이며 import·serialization을 포함한다. 이 분석은 저장 JSON만 읽으며 solver·production module·ODE 호출은 0회다.", '',
  '독립 reference는 exact Fraction kernel/convolution과 Decimal160 closed-form E moments를 사용했다. 실행 전 고정한 guard는 `1e-80*max(1,abs(reference),abs(lower),abs(upper))`다. Component 비교 수는 서로 다른 물리 시나리오 수가 아니다.','',
  'Wolfram은 15개 zero residual을 반환했고 Power/General 경고가 함께 있었다. 상태는 `QUALIFIED_SYMBOLIC_CORROBORATION`, 원인은 `NOT_ESTABLISHED`다. R10의 원래 CAS 상태와 실행 예산을 변경하지 않는다.','',
  '## Full-A 블록 계수','',
  '| 사례 | 기존 K 인증 qK | additive Duhamel | 채택 minorization upper q |','|---|---:|---:|---:|']
 for c in summary['cases']:
  lines.append(f"| {NAMES[c['id']][0]} | {tableval(c['q_K']['exact'])} | {tableval(c['q_additive']['exact'])} | {tableval(c['q_chosen']['exact'])} |")
 lines+=['',
  '각 q는 고정 K/pi/destruction과 인증된 전체 w box의 모든 가측 경로·모든 시작시각에 적용되는 증명에 결속되어 있다. Native9의 q는 1보다 작아 full-A finite-block contraction을 제공한다. K-only q를 full A에 그대로 이식하지 않는다. Additive saturation control에서는 q_add=1이지만 minorization q=0.862045209560709…<1이다.','',
  '## 최종 endpoint 상계','',
  '| 사례 | 성분 | R10 capped | R11 raw | R11 capped | capped 개선 |','|---|---|---:|---:|---:|---:|']
 for c in summary['cases']:
  for comp in ('R','E'):
   final=c['final'];percent=final['capped_improvement_percent'][comp]
   lines.append(f"| {NAMES[c['id']][0]} | {comp} | {tableval(final['R10_capped'][comp]['exact'])} | {tableval(final['raw'][comp]['exact'])} | {tableval(final['capped'][comp]['exact'])} | {'0% (양쪽 0)' if percent is None else tableval(percent['exact'])+'%'} |")
 lines+=['',
  '무반응 E=0의 비율은 수학적으로 0/0이므로 JSON에서는 percent=null로 기록하고 표에서는 양쪽 0의 동일성을 표시했다. 그 밖의 최종 capped percent는 정확히 0이다.','',
  '## 원소별 raw/capped 비교','',
  '비교 기준은 **R10 capped**다. Endpoint는 사례마다 193시각×2성분=386개, whole-cell은 192닫힌 셀×2성분=384개다. 아래는 R11이 기준보다 작은/같은/큰 성분 수다.','',
  '| 사례 | raw endpoint < / = / > | raw whole < / = / > | capped endpoint < / = / > | capped whole < / = / > |','|---|---:|---:|---:|---:|']
 for c in summary['cases']:
  cells=[]
  for mode,key in [('raw','endpoints_upper'),('raw','whole_cells_upper'),('capped','endpoints_upper'),('capped','whole_cells_upper')]:
   counts=c['counts'][mode][key]['all'];cells.append(' / '.join(str(counts[k]) for k in ('less','equal','greater')))
  lines.append('| '+NAMES[c['id']][0]+' | '+' | '.join(cells)+' |')
 lines+=['',
  '현재 floor kernel은 첫 블록의 homogeneous age에 대해 h=1을 사용한다. 따라서 저장된 더 세밀한 R10 cap과 비교한 raw 수치는 위 표처럼 커질 수 있다. Capped는 같은 clock·point/닫힌 셀의 인증 상계와 교차한 결과다. Raw의 보편적 우위를 주장하지 않는다.','',
  '## 닫힌 셀에서 관찰된 제한된 개선','',
  '| 사례 | 개선한 E 셀 수 / 192 | 최대 whole-E 개선율 | 최대가 발생한 셀 (0-based) |','|---|---:|---:|---:|']
 for c in summary['cases']:
  im=c['capped_whole_improvement']['E'];best=im['max_percent']
  lines.append(f"| {NAMES[c['id']][0]} | {im['improved_cells']} / 192 | {tableval(best['percent']['exact'])+'%' if best else '0%'} | {best['cell_index'] if best else '—'} |")
 lines+=['',
  '세 반응 사례의 첫 R whole-cell 값에는 dyadic128의 1 ulp, 즉 정확히 2^-128만큼의 감소가 하나씩 있다. 이는 반올림 수준의 차이다. 비선형 및 coarse-defect 사례의 작은 E whole-cell 개선은 위 셀들에 한정된다. Native9 E whole 및 모든 capped endpoint는 R10과 정확히 같다.','',
  '## Fresh forcing·블록 경계 판별','',
  '`q=0` late-forcing control에서 마지막 셀의 새 forcing은 h0=1로 들어가 final R=1/8, E=1/128을 얻었다. q를 새 forcing에 미리 곱하는 방식과 구별된다. Block-jump control의 닫힌 셀 R upper는 1이고 그 오른쪽 endpoint upper는 1/2다. 셀의 오른쪽 끝점에 왼쪽에서 접근한 극한을 whole-cell 인증에 포함했다.','',
  '## 저장 sample과 허용오차','',
  f"독립 reference의 저장 sample 비교 {summary['reference'].get('sample_component_comparisons',0):,}성분은 기존 `atol=2e-12`, `rtol=2e-10` 기준을 통과했다. 전체 strict containment는 false이며, 저장 sample이 upper를 조금 넘는 성분은 {summary.get('saved_samples',{}).get('strictly_above_upper_component_count',0)}개다. 저장 sample은 cap으로 사용하지 않았다.",'',
  'R11의 Decimal 비교에서 최대 초과는 무반응 capped R의 index23에서 `4.001332174731647…e-12`, 해당 tolerance는 `4.377656370786352e-11`이다. 이는 저장된 decimal sample과 exact rational upper의 비교다. R10의 원래 binary-float 후처리 기록 `4.0013206434938575e-12`는 그대로 보존한다. 두 수치는 표현과 비교 정밀도가 다른 readout이며, 기존 허용오차를 바꾸지 않았다.','',
  '## 그림과 출처','',
  '- `figures/BOUND_ENDPOINTS.png`: endpoint 값의 연결선은 시각적 안내다. 중간 시각의 인증은 연결선에서 얻지 않는다.',
  '- `figures/WHOLE_CELL_CERTIFICATES.png`: 각 step 높이는 정확한 닫힌 셀 전체의 인증 upper다. 공유 endpoint에는 양쪽 셀의 인증이 적용된다.',
  '- `figures/KERNEL_CONTROL_DIAGNOSTICS.png`: full-A block age, fresh forcing, left-limit control 및 작은 whole-E 차이를 표시한다.',
  '- 정확한 수치·비교 count·source SHA는 `analysis/SAVED_OUTPUT_SUMMARY.json`, 재생산 코드는 `analysis/plot_saved_results.py`에 있다.','',
  'Native9는 native K와 synthetic conditional reaction fixture의 조합이다. 실제 HD reactive array 및 named physical consumer/density/clock은 INPUT_PENDING이다. E=abs(eta), coarse l1=4E를 유지하고, raw lower는 chosen-q ideal comparison의 lower다. HH_R10=OFF, production=NOT_ISSUED, L4=false, physical/central delta=0이며, native v=UNSPECIFIED·MISSING_NOT_ZERO·TIQM/SQM 구별을 유지한다.','']
 (BASE/'RESULTS_KO.md').write_text('\n'.join(lines))
 print(json.dumps({'status':'SAVED_POSTPROCESSING_COMPLETE','cases':len(summary['cases']),'capped_endpoint_exact_equality':summary['all_capped_endpoints_exactly_equal_R10'],'figures':len(figs),'solver_calls':0,'summary_sha256':sha(OUT/'SAVED_OUTPUT_SUMMARY.json')}))

if __name__=='__main__':main()
