#!/usr/bin/env python3
"""C4 source-versioned direction/memory resource design.
No chemistry ODE or production AXBI Driver changes.
"""
from pathlib import Path
import sys,math,json,struct,hashlib
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'source07_c1_baseline_20261014'))
from q_emission_baseline import Scenario

root=Path(__file__).resolve().parents[2]
sc=Scenario(root)
a1,a2,af=1/21,1/12,1/5
mu=0.5
nxy=math.sqrt(1-mu*mu)
def vectors(a,b):
    return (a*math.exp(-b)*100*nxy,a*math.exp(2*b)*100*mu)
def energy(q,a,b):
    return math.hypot(q[0]/(a*math.exp(-b)),q[1]/(a*math.exp(2*b)))
cases=[]
for q in (-.01,-.005,0.,.005,.01):
    b1,b2,bf=(sc.b(a,q) for a in (a1,a2,af))
    k1,k2=vectors(a1,b1),vectors(a2,b2)
    direct=energy(k1,af,bf)+energy(k2,af,bf)
    averaged=2*energy(((k1[0]+k2[0])/2,(k1[1]+k2[1])/2),af,bf)
    dot=sum(x*y for x,y in zip(k1,k2))
    sine=abs(k1[0]*k2[1]-k1[1]*k2[0])/(math.hypot(*k1)*math.hypot(*k2))
    cases.append({'q_ref':q,'b_a1':b1,'b_a2':b2,'b_af':bf,'sin_q_angle':sine,
                 'old_energy_ev_per_2photons':direct,'naive_merged_energy_ev_per_2photons':averaged,
                 'lost_energy_ev_per_2photons':direct-averaged,
                 'relative_energy_deficit':(direct-averaged)/direct})
# These are controlled resource projections, not a full memory profile.
trial_designs=[]
for ne,nmu in [(64,8),(128,16),(256,32),(512,32)]:
    lanes=4
    per_bin=8*lanes
    trial_designs.append({'N_E':ne,'N_mu':nmu,'arrays':lanes,'bytes_per_cell_all_arrays':per_bin,
       'dynamic_array_bytes':ne*nmu*per_bin,'dynamic_array_mib':ne*nmu*per_bin/(2**20)})
source_per_step=48*8
raw_bytes_200k=source_per_step*200000*32
report={'kind':'C4 resource/design analysis with current MD14 scenario',
        'source_sha256':hashlib.sha256((root/'rust/rei_microphysics/src/axbi_sources.rs').read_bytes()).hexdigest(),
        'parameter_identity':sc.data['scenario_id'],
        'actual_bianchi_source_geometry_cross_epoch_energy_gap':cases,
        'fixed_q_candidates':trial_designs,
        'cohort_memory':{'fresh_per_epoch':source_per_step,'after_200000_uncompressed_packets':source_per_step*200000,
           'single_CovariantPhoton_bytes':32,'unbounded_packet_bytes':raw_bytes_200k,
           'unbounded_packet_gib':raw_bytes_200k/2**30,'c4_limited_packet_count':256,
           'pilot_implementation_tagged_packet_bytes':40,'pilot_256_packet_payload_bytes':256*40},
        'recommendation':"Pursue fixed q energy-angle phase-space binning for unbounded source time; retain q cohorts as test oracle and permit only transactionally bounded direction-and-threshold safe reduction.",
        'important_boundary':"Fixed q grid needs R*J local-source injection and moving threshold split, and its moment accuracy must be separately verified."
}
folder=Path(__file__).resolve().parent
(folder/'evidence/DESIGN_CAPACITY.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2)[:8500])
