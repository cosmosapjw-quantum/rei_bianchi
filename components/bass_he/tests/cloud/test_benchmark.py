from bass_he.cloud.benchmark import choose,benchmark
class Host:usable_cpus=16
class Work:
    cases=list(range(16))
    def __init__(self):self.calls=[]
    def run_fresh(self,w,r,dispatch_deadline):
        self.calls.append((w,r));return {'valid':True,'throughput':{1:1,8:8,16:8.2}[w],'elapsed':.1}
def test_seeded_three_repeat_selection():
    w=Work();r=benchmark({},Host(),w,seed=3)
    assert r.selected==8 and len(w.calls)==9 and len(set(w.calls))==9
def test_smallest_worker_within_95pct():
    assert choose([{'workers':8,'valid':True,'throughput':9.6},{'workers':16,'valid':True,'throughput':10}])==8
def test_budget_keeps_best_observed_only():
    r=benchmark({},Host(),Work(),budget=0)
    assert r.status=='PARTIAL_BEST_OBSERVED' and r.selected is None
