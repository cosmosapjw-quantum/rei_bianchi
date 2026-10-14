from pathlib import Path
import concurrent.futures,subprocess,json,os,time
R=Path.cwd();P=R/'.cuh/fastest-track/REI-F08-PAIRED'
def run(l):
 b=P/'whole-matched'/l;d=b/l;cmd=['cuhg-telemetry','run','--project',str(R),'--task','REI-F08','--',str(P/'matched-producer.binary'),'--scenario',str(R/'configs/rei_fastest_v1/science_scenario_v1.json'),'--output',str(b),'--full','--only',l]
 if b.exists():cmd+=['--resume']
 t=time.monotonic()
 with (P/(l+'-producer-durable-resume.log')).open('wb') as f:code=subprocess.call(cmd,stdout=f,stderr=subprocess.STDOUT,env={**os.environ,'CUHG_EXECUTION_MODE':'CODEX_ONLY'})
 r={'task':'REI-F08','run':l,'argv':cmd,'exit_code':code,'wall_s':time.monotonic()-t,'durable_resume':b.exists(),'prior_exit':'UNKNOWN_AFTER_INTERRUPTION','previous_attempt':'archive binary lacked executable mode; science never started'};(P/(l+'-production-receipt.json')).write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r),flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as e:list(e.map(run,['S2_BI','A0_BI','A2_FLRW','A2_BI']))
