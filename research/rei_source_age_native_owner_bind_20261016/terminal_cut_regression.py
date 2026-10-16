"""PR164 manufactured coarse-angle counterexample, separate from native MD14."""
import json,sys
from pathlib import Path
repo=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(repo/'research/rei_source_age_bianchi_20261016/src'))
from age_transport import Model,integrate_source,integrate_angular_event_source
m=Model(signed_v0=-.04)
reference=integrate_angular_event_source(m,24,64,64)
global4=integrate_source(m,24,4,64)
split4=integrate_angular_event_source(m,24,4,64)
a=abs(global4.final_pi_ev-reference.final_pi_ev);b=abs(split4.final_pi_ev-reference.final_pi_ev)
assert b>a*10,(a,b)
result=dict(scope='PR164 manufactured neutral-stock control; native nmu4 unsupported',global4_Pi_error=a,split4_Pi_error=b,reference_mu=64,coarse_mu=4,regression='terminal-cut split worsens coarse pressure by more than10x')
Path(sys.argv[1]).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
