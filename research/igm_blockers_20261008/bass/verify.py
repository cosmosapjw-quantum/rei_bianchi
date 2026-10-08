#!/usr/bin/env python3
"""Bounded focused source consumer + independent Decimal70 finite-surrogate oracle."""
import argparse,copy,decimal,hashlib,json,os,resource,subprocess,time
from pathlib import Path
from adapter import extract,validate
P=Path(__file__).resolve().parent
D=decimal.Decimal
def bounded(cmd,*,input=None,memory=512*1024*1024):
    def limit():
        resource.setrlimit(resource.RLIMIT_CPU,(900,900));resource.setrlimit(resource.RLIMIT_AS,(memory,memory));os.sched_setaffinity(0,{min(os.sched_getaffinity(0))})
    t=time.monotonic();u=resource.getrusage(resource.RUSAGE_CHILDREN);r=subprocess.run(cmd,input=input,text=True,capture_output=True,timeout=1200,preexec_fn=limit);v=resource.getrusage(resource.RUSAGE_CHILDREN)
    row=dict(command=cmd,exit=r.returncode,wall_seconds=time.monotonic()-t,cpu_seconds=v.ru_utime+v.ru_stime-u.ru_utime-u.ru_stime,maxrss_kib=v.ru_maxrss,stderr=r.stderr)
    if r.returncode:raise RuntimeError(json.dumps(row))
    return r.stdout,row
def oracle(packet,tail):
    with decimal.localcontext() as ctx:
        ctx.prec=70; widths=[]; rates=[]; edges=[D(0)]
        for r in packet['records']:
            f=lambda x:D.from_float(float.fromhex(x));s0=f(r['s0']);s1=f(r['s1']);bg=list(map(f,r['background']));g=list(map(f,r['gas']))
            dt=(s1-s0)/bg[2];edges.append(edges[-1]+dt);ne=(bg[3]*g[0]+bg[4]*(g[1]+2*g[2]))*D(1000000)
            rates.append(ne*D(299792458)*D.from_float(6.6524587e-29));widths.append(dt)
        tau=[D(0),D(0),D.from_float(tail)]
        for i in (1,0):tau[i]=tau[i+1]+rates[i]*widths[i]
        survival=[(-x).exp() for x in tau];mass=[survival[i+1]*(1-(-rates[i]*widths[i]).exp()) for i in range(2)]
        return dict(tau=tau,survival=survival,mass=mass)
def run(out,payload=None):
    out.mkdir(parents=True,exist_ok=False);packet=json.loads((P/'accepted_history.json').read_text())
    if payload:
        actual=extract(payload)
        assert actual==packet,'STORED_ACCEPTED_PROJECTION_MISMATCH'
    edges,cells=validate(packet);commands=[];binary=out/'receiver'
    _,log=bounded(['rustc','--edition=2024','-Awarnings',str(P/'receiver.rs'),'-o',str(binary)],memory=2*1024**3);commands.append(log)
    results=[]
    for tail in (0.,.125):
        values=edges+[x for cell in cells for x in cell]+[tail]
        stdout,log=bounded([str(binary)],input=' '.join(map(repr,values)));commands.append(log);native=json.loads(stdout);ref=oracle(packet,tail);errors={}
        for key in ('tau','survival','mass'):
            error=[]
            for a,b in zip(native[key],ref[key]):
                e=abs(D.from_float(a)-b); tol=D('4e-16') if key=='survival' else max(abs(b)*D('3e-15'),D('1e-30'))
                assert e<=tol,(key,e,tol);error.append(str(e))
            errors[key]=error
        results.append(dict(tail=tail,native=native,decimal70_absolute_errors=errors))
    # Tail shifts and probability scaling for the same prescribed finite cells.
    a,b=[r['native'] for r in results];factor=float((-D('.125')).exp())
    assert all(abs((y-x)-.125)<3e-17 for x,y in zip(a['tau'],b['tau']))
    assert all(abs(y-x*factor)<4e-16 for x,y in zip(a['survival'],b['survival']))
    assert all(abs(y-x*factor)<=abs(y)*3e-15 for x,y in zip(a['mass'],b['mass']))
    negatives=[]
    for label,change in [('wrong_epoch',lambda p:p['records'][0].update(midpoint='0x0.0p+0')),('wrong_provider',lambda p:p.update(provider_id='wrong')),('wrong_source',lambda p:p.update(typed_sha256='wrong')),('fake_single_endpoint',lambda p:p.update(records=p['records'][:1])),('double_density',lambda p:p.update(density_conversion_count=1)),('wrong_density_units',lambda p:p.update(density_units='proper m^-3')),('double_D',lambda p:p.update(doppler_application_count=1)),('missing_clock',lambda p:p.pop('clock')),('wrong_background_density',lambda p:p['records'][0]['background'].__setitem__(3,float(1).hex())),('broken_gas_continuity',lambda p:p['records'][1]['y0'].__setitem__(0,float(.5).hex()))]:
        p=copy.deepcopy(packet);change(p)
        try:validate(p)
        except (ValueError,KeyError) as e:negatives.append(dict(case=label,status='EXPECTED_REJECTION',reason=str(e)))
        else:raise AssertionError(label)
    report=dict(status='PASS_SCOPED_ACTUAL_FINITE_HISTORY_CONSUMER',source_pin=json.loads((P/'SOURCE_PIN.json').read_text()),commands=commands,accepted_records=2,normal_time_edges_seconds=edges,clock_authority='dt=delta_ln_a/H_mid NORMAL_TIME_SURROGATE; not exact cosmological t(z)',reconstruction='supplied frozen midpoint density cells',observer_at_last_edge=True,cosmological_observer_tail='UNKNOWN',density_conversion_count=1,doppler_application_count=1,results=results,negative_tests=negatives,cost=dict(additional_photon_observer=0,provider=0,RHS=0,new_history=0),physical_admission='HOLD',binary_sha256=hashlib.sha256(binary.read_bytes()).hexdigest())
    (out/'RESULT.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ('status','accepted_records','cost')}));return report
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--payload',type=Path);a=p.parse_args();run(a.output,a.payload)
