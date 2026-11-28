"""Read-only postprocessing of saved R10/R9/R7 evidence; no solver imports."""
from pathlib import Path
from fractions import Fraction as Q
import hashlib,json,math,os
L=Path(__file__).resolve().parents[1];ROOT=L.parents[1]
def load(p):return json.loads(p.read_text())
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def real(x):return float(Q(x))
def vectors(x):return [[real(v) for v in row] for row in x]
def counts(a,b):
 vals=[(Q(x),Q(y)) for u,v in zip(a,b) for x,y in zip(u,v)]
 return {'less':sum(x<y for x,y in vals),'equal':sum(x==y for x,y in vals),'greater':sum(x>y for x,y in vals),'total':len(vals)}
def main():
 p=L/'raw/PRIMARY_RESULTS.json';r=L/'raw/REFERENCE_RESULTS.json';oldpath=ROOT/'research/provider_registry_molecular_r9_20261028/raw/PRIMARY_RESULTS.json';samplepath=ROOT/'research/provider_registry_molecular_r7_20261027/raw/REFERENCE_RESULTS.json'
 new,ref,old,samples=map(load,[p,r,oldpath,samplepath]);assert new['status']==ref['status']=='PASS'
 analysis={'schema':'WU_R10_SAVED_RESULT_ANALYSIS_V1','scientific_solver_calls':0,'source_SHA256':{str(x.relative_to(ROOT)):digest(x) for x in [p,r,oldpath,samplepath]},'cases':[],'aggregate_counts':{},'CPU_s':{},'scope':'Exact Fraction comparisons; decimal percentages/ratios are displays; saved reference samples are not continuous certificates'}
 for lane in ['PRIMARY','REFERENCE']:analysis['CPU_s'][lane]=load(L/('raw/'+lane+'_PROCESS.json'))['OS_CPU_s']
 analysis['CPU_s']['sum']=sum(analysis['CPU_s'].values())
 for row,prior,sample in zip(new['hd_cases'],old['hd_cases'],samples['hd_cases']):
  assert row['id']==prior['id'] and sample['id']=='HD:'+row['id']; raw=row['raw'];cap=row['capped'];oldcap=prior['capped'];N=raw['cells'];gen=row['generator']
  out={'id':row['id'],'lambda':real(gen['lambda']),'lambda_exact':gen['lambda'],'lambda_K':real(gen['lambda_K']),'lambda_H':real(gen['lambda_H']),'lambda_split_lower':real(gen['separate_sum_lower']),'generator':gen,'delta':raw['delta'],'cells':N,'horizon':real(raw['delta'])*N,'initial':raw['initial'],'coefficients':row['coefficients'],'R9_final':list(map(real,oldcap['endpoints'][-1])),'raw_final':list(map(real,raw['endpoints_upper'][-1])),'capped_final':list(map(real,cap['endpoints_upper'][-1])),'saved_sample_final':list(map(real,sample['R_E'][-1]))}
  out['capped_reduction_percent']=[float(100*(Q(o)-Q(n))/Q(o)) if Q(o)!=0 else None for o,n in zip(oldcap['endpoints'][-1],cap['endpoints_upper'][-1])]
  out['raw_over_R9_final']=[float(Q(n)/Q(o)) if Q(o)!=0 else None for o,n in zip(oldcap['endpoints'][-1],raw['endpoints_upper'][-1])]
  out['capped_over_saved_sample_final']=[n/s if s else None for n,s in zip(out['capped_final'],out['saved_sample_final'])]
  out['counts']={m+'_'+kind:counts(row[m][key],oldcap[oldkey]) for m in ['raw','capped'] for kind,key,oldkey in [('endpoints','endpoints_upper','endpoints'),('whole','whole_cells_upper','whole_cells')]}
  out['max_raw_comparison_interval_width']=float(max(Q(h)-Q(l) for lo,hi in zip(raw['endpoints_lower'],raw['endpoints_upper']) for l,h in zip(lo,hi)))
  out['flow_interval_max_width']=float(max(Q(h)-Q(l) for lo,hi in zip(raw['flow_interval']['lower'],raw['flow_interval']['upper']) for l,h in zip(lo,hi)))
  analysis['cases'].append(out)
 for key in analysis['cases'][0]['counts']:
  analysis['aggregate_counts'][key]={metric:sum(x['counts'][key][metric] for x in analysis['cases']) for metric in ['less','equal','greater','total']}
 best=None
 for row,samp in zip(new['hd_cases'],samples['hd_cases']):
  assert samp['id']=='HD:'+row['id']
  for mode in ['raw','capped']:
   for n,(bound,obs) in enumerate(zip(row[mode]['endpoints_upper'],samp['R_E'])):
    for k in [0,1]:
     v={'case':row['id'],'mode':mode,'n':n,'component':k,'saved_sample':obs[k],'bound':float(Q(bound[k])),'excess':float(Q(obs[k])-Q(bound[k])),'frozen_tolerance':2e-12+2e-10*abs(float(obs[k]))}
     if best is None or v['excess']>best['excess']:best=v
 analysis['max_saved_sample_excess']=best
 analysis['case_binding']='R7_reference.id == HD: + production.id; all other production IDs exactly equal'
 (L/'raw/RESULT_ANALYSIS.json').write_text(json.dumps(analysis,ensure_ascii=False,indent=2)+'\n')
 lines=['# R10 실제 결과','',f"Primary {new['check_count']}/{new['check_count']} PASS; independent {ref['check_count']}/{ref['check_count']} PASS, {ref['component_comparisons']} component comparisons /0failed. 각1회이며 Python 전체OS CPU합 {analysis['CPU_s']['sum']:.6f}s다. 아래 계산은 저장된출력을읽는후처리이고추가solver/ODE호출0이다.",'','| 사례 | R9 R최종 | R10 raw R | R10 capped R | R 감소% | R9 E최종 | R10 capped E | E 감소% |','|---|---:|---:|---:|---:|---:|---:|---:|']
 labels=['2state no reaction','2state nonlinear','2state coarse defect','native9 conditional']
 for label,x in zip(labels,analysis['cases']):
  a,b=x['capped_reduction_percent'];lines.append(f"|{label}|{x['R9_final'][0]:.12g}|{x['raw_final'][0]:.12g}|{x['capped_final'][0]:.12g}|{a:.9g}|{x['R9_final'][1]:.12g}|{x['capped_final'][1]:.12g}|{b if b is not None else 'NA: both zero'}|")
 lines+=['','## 정확한 성분 비교','','이 카운트는 독립적인 물리 사례 수가 아니라 저장한 clock/cell의 R,E성분 수다. 다음 less/equal/greater는 Fraction exact 비교다.','', '| 모드/영역 | 작음 | 같음 | 큼 | 합계 |','|---|---:|---:|---:|---:|']
 for k,cnt in analysis['aggregate_counts'].items():lines.append('|'+k+'|'+'|'.join(str(cnt[k2]) for k2 in ['less','equal','greater','total'])+'|')
 x=analysis['cases'][-1]
 lines+=['','## Native9의 순간 수축률과 남은 보수성','',f"Native9 lambda(K)={x['lambda_K']:.12g}, lambda(full A)={x['lambda']:.12g}다. K의 sparse 구조는 한 단계의 column overlap이0이어도 유한시간에 혼합될 수 있다. 이번 순간계수는 그 다단계 혼합을 포착하지 못해 raw R최종이R9의 {x['raw_over_R9_final'][0]:.9g}배다. 실제 관측된native9 raw endpoint성분381개, whole성분380개가R9보다크다. 이 결과를유효한R9block인증의소멸이나물리적발산으로해석하지않는다.",'',f"동일시각의R9인증상계와교차하면최종R은그대로이고 E는{x['capped_reduction_percent'][1]:.9g}%감소한다. 최종capped/sample비율은R {x['capped_over_saved_sample_final'][0]:.9g}, E {x['capped_over_saved_sample_final'][1]:.9g}다. 표본은cap이나연속구간인증으로사용하지않았다.",'','## 수치·자원과 한계','',f"가장넓은raw ideal-comparison endpoint interval폭은 {max(z['max_raw_comparison_interval_width'] for z in analysis['cases']):.9g}다. lower배열은비교방정식의해를둘러싼다. 실제물리오차lower를주지않는다. Dyadic128/Taylor96는고정했고Decimal160reference의1e-80guard도실행후변경하지않았다. 수렴차수나속도향상비교는수행하지않았다.",'','Wolfram은15개잔차0/all_zeroTrue와Infinity/Power경고를함께반환했다. QUALIFIED_SYMBOLIC_CORROBORATION으로보존하며원인을별도확정하지않았다. 직접증명과독립reference의zero/resonance/near-resonance검사를함께사용한다. 기존R8원래726/727PASS+1FAIL과별도phi24/24PASS는그대로다.','', 'Actual HD reactive array, named physical consumer, density and clock remain INPUT_PENDING. HH_R10=OFF; production=NOT_ISSUED; L4_ready=false; physical/central delta0.']
 lines+=['','## 저장 표본과 해석적 상계의 작은 차이','',f"No-reaction 사례에서 저장된 수치표본이 새 해석적 상계를 소폭 넘는 지점이 있다. 최대 초과는 {best['excess']:.12g}이며 사전에 고정한 containment 허용오차 {best['frozen_tolerance']:.12g} 이내다. 정확한 비교해를 둘러싼 dyadic interval과 유한오차의 과거 ODE 표본은 역할이 다르다. 저장표본의 strict containment 또는 그 표본 자체의 exactness를 주장하지 않는다.",'','## 그림의 범위','','BOUND_COMPARISON 그림의 선은 저장 endpoint 값을 연결한 시각적 안내다. 점 사이의 선형 보간을 인증 상계로 사용하지 않는다. 전체 셀 인증은 별도의 whole_cells_upper 배열과 증명에 있다.']
 (L/'RESULTS_KO.md').write_text('\n'.join(lines)+'\n')
 os.environ.setdefault('MPLCONFIGDIR','/tmp/wu_r10_matplotlib')
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 fig,axs=plt.subplots(2,2,figsize=(11,7.4),constrained_layout=True)
 for rridx,ci in enumerate([1,3]):
  n=new['hd_cases'][ci];o=old['hd_cases'][ci];s=samples['hd_cases'][ci];t=[real(n['raw']['delta'])*i for i in range(n['raw']['cells']+1)]
  for k in [0,1]:
   ax=axs[rridx,k]
   for ar,label,col,style in [(o['capped']['endpoints'],'R9 certified','#777777','--'),(n['raw']['endpoints_upper'],'R10 raw','#d55e00',':'),(n['capped']['endpoints_upper'],'R10 capped','#0072b2','-')]:ax.plot(t,[real(x[k]) for x in ar],label=label,color=col,linestyle=style,linewidth=1.8)
   ax.plot(t,[real(x[k]) for x in s['R_E']],label='Saved sample',color='#009e73',linewidth=1.25)
   if rridx==1:ax.set_yscale('symlog',linthresh=1e-10)
   ax.set_title(('Two-state nonlinear' if ci==1 else 'Native nine-state conditional')+' / '+('R' if k==0 else 'E'))
   ax.set_xlabel('Inherited fixture time');ax.set_ylabel('Error or certified upper bound');ax.grid(alpha=.2)
 axs[0,0].legend(fontsize=8);fig.suptitle('R10 full-generator triangular comparison: saved-output analysis\nEndpoint values joined for display; whole-cell certificates are stored separately.',fontsize=11)
 (L/'figures').mkdir(exist_ok=True);fig.savefig(L/'figures/BOUND_COMPARISON.png',dpi=160);fig.savefig(L/'figures/BOUND_COMPARISON.svg');plt.close(fig)
 print(json.dumps({'cases':[{k:x[k] for k in ['id','lambda','lambda_K','R9_final','raw_final','capped_final','capped_reduction_percent','capped_over_saved_sample_final','max_raw_comparison_interval_width']} for x in analysis['cases']],'aggregate_counts':analysis['aggregate_counts'],'CPU_s':analysis['CPU_s']},ensure_ascii=False))
if __name__=='__main__':main()
