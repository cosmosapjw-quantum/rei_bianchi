#!/usr/bin/env python3
"""Bounded 193-epoch source-scoped transport, resumable chunks, not another IVP."""
import argparse,json,pathlib,sys,time
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
from causal_firstflight import generate,ROOT
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--start',type=int,required=True);ap.add_argument('--stop',type=int,required=True)
 ap.add_argument('--order',type=int,default=16);ap.add_argument('--substeps',type=int,default=4)
 args=ap.parse_args();assert 0<=args.start<args.stop<=193
 out=ROOT/'chunks';out.mkdir(exist_ok=True)
 st=time.perf_counter()
 result,emission,flight,joint,arrival=generate(order=args.order,substeps=args.substeps,emission_indices=range(args.start,args.stop))
 obj={'range':[args.start,args.stop],'order':args.order,'substeps':args.substeps,'result':result,'emissions':emission,'flights':flight,'joint':joint,'arrival':arrival}
 name=f'CHUNK_{args.start:03d}_{args.stop:03d}_o{args.order}s{args.substeps}.json'
 (out/name).write_text(json.dumps(obj,sort_keys=True,allow_nan=False,ensure_ascii=False)+'\n')
 print(json.dumps({'result':name,'emission_rows':len(emission),'flight_rows':len(flight),'joint_rows':len(joint),'wall_s':round(time.perf_counter()-st,3)}),flush=True)
