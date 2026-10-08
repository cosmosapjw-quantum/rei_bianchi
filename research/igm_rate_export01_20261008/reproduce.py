"""Replay the PR88 public packet; no native observer/provider or history work."""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import struct
import subprocess
import sys
import adapter


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():parser.error('fresh output required')
    args.output.mkdir(parents=True)
    root=adapter.HERE.parents[1]
    commands=[]
    for relative in ('tests','consumers'):
        cmd=[sys.executable,'-m','unittest','discover','-s',str(adapter.HERE/relative),'-v']
        p=subprocess.run(cmd,capture_output=True,text=True)
        (args.output/(relative+'.stdout')).write_text(p.stdout)
        (args.output/(relative+'.stderr')).write_text(p.stderr)
        commands.append({'command':cmd,'exit':p.returncode})
        if p.returncode:raise RuntimeError('TARGETED_TEST_FAILURE')
    calls={k:0 for k in ('conditional_joint_enclosure','project','spectral_moments','observe','cross_section','igm_point_rhs','advance','native_or_child_spawns')}
    def profile(frame,event,arg):
        if event=='call' and frame.f_code.co_name in calls:
            calls[frame.f_code.co_name]+=1
            if frame.f_code.co_name in ('spectral_moments','observe','cross_section','igm_point_rhs','advance'):
                raise RuntimeError('FORBIDDEN_SCIENCE_CALL')
    def audit(event,args):
        if event in ('subprocess.Popen','os.system','os.exec','os.posix_spawn','ctypes.dlopen'):
            calls['native_or_child_spawns']+=1
            raise RuntimeError('FORBIDDEN_NATIVE_LAUNCH')
    packet=adapter.upstream().load_packet()
    sys.addaudithook(audit);sys.setprofile(profile)
    try:
        result=adapter.readout(packet)
        missing=adapter.readout({'total':[0]*13,'rates':[0]*3,'rhs':{'photo':[0]*3}})
    finally:sys.setprofile(None)
    previous=json.loads((adapter.PACKAGE/'receiver-observed/RECEIVER_OUTPUT.json').read_text())
    assert result['conditional_output']==previous
    assert missing['status']=='MISSING_INSTANTANEOUS_JOINT_MOMENTS'
    # Ordered replay of saved terms; not new provider samples or continuum sums.
    samples=adapter.PACKAGE/'observed/samples.binary64.csv'
    assert hashlib.sha256(samples.read_bytes()).hexdigest()==packet['context']['samples_sha256']
    gamma=[0.]*3;energy=[0.]*3;n=0
    with samples.open() as f:
        for row in csv.reader(f):
            x=[struct.unpack('>d',bytes.fromhex(v))[0] for v in row]
            for i in range(3):gamma[i]+=x[7+i];energy[i]+=x[7+i]*x[3]
            n+=1
    assert [v.hex() for v in gamma+energy]==[v.hex() for v in packet['Gamma']+packet['incident_Ecal']]
    receipt={'status':'PASS_STORED_READ_ONLY_REPLAY','commands':commands,'ordered_saved_sample_rows':n,
             'six_binary64_reduction_bit_matches':6,'typed_output_exact_parity':True,
             'primary_call_counts':calls,'new_native_observer_calls':0,'new_provider_calls':0,'new_history_steps':0,
             'historical_native_cost':'unchanged PR88 evidence; not reset or remeasured',
             'physical':'HOLD','provider_error':'UNKNOWN','continuum_error':'UNKNOWN',
             'count_scope':'Python profile + audit for primary readout; tests are separate pure Python children before audit'}
    for name,value in [('READOUT.json',result),('MISSING.json',missing),('RESULTS.json',receipt)]:
        (args.output/name).write_text(json.dumps(value,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))

if __name__=='__main__':main()
