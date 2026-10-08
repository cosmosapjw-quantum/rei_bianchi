from pathlib import Path
import json,sys
from igm_compare import read_csv,compare_rows
r=Path(__file__).parent
end=int(sys.argv[1]);fineend=2*end
c=read_csv(r/'coarse'/f'endpoint_{end}.csv');f=read_csv(r/'fine'/f'endpoint_{fineend}.csv');t=read_csv(r/'tail'/f'endpoint_{end}.csv')
results={label:compare_rows(c,other) for label,other in [('temporal',f),('tail',t)]}
old=Path('/home/cosmosapjw/Documents/Codex/2026-10-07/task-4/duration-unprojected-20261008/progressive-support')
for label,folder,row,k in [('coarse','h0008-coarse',c[0],9),('fine','h0008-fine-diagnostic',f[0],18),('tail','h0008-tail-diagnostic',t[0],9)]:
 p=json.loads((old/folder/f'PHASE_{k}_{k}.json').read_text())
 history=list((old/folder).glob('history_0_*.csv'))[0];previous=read_csv(history)[-1]
 baseN=previous['emitted_N']-p['incremental_emitted_N'];baseE=previous['emitted_E']-p['incremental_emitted_E']
 phase=json.loads(sorted((r/label).glob('PHASE_*.json'),key=lambda p:int(p.stem.split('_')[-1]))[-1].read_text())
 ni=phase['source_simpson128'];ei=ni*phase['source_mean_energy_erg']
 ratios=[abs(row['emitted_N']-baseN-ni)/(1e-8+1e-3*abs(ni)),abs(row['emitted_E']-baseE-ei)/(1e-20+1e-3*abs(ei))]
 results[label+'_source']={'ratios':ratios,'passed':max(ratios)<=1,'original_allowance':True}
results['passed']=all(v['passed'] for v in results.values());results['scope']='same next common epoch only' if end==10 else 'same last accepted common epoch only; full0008suffix NOT_COMPLETED'
(r/f'comparison_{end}.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps({'passed':results['passed'],'worst_temporal':max(v['max_allowance_ratio'] for v in results['temporal']['fields'].values()),'worst_tail':max(v['max_allowance_ratio'] for v in results['tail']['fields'].values()),'source':[results[k+'_source']['ratios'] for k in ('coarse','fine','tail')]}));raise SystemExit(0 if results['passed'] else 1)
