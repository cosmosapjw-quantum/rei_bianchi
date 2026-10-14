#!/usr/bin/env python3
"""SOURCE/IC completed-history sensitivity; delegates identical ZBAR reducer."""
import argparse,importlib.util,pathlib
path=pathlib.Path(__file__).resolve().parent.parent/'convergence/compare_histories.py'
spec=importlib.util.spec_from_file_location('axbi_completed_reducer',path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
p=argparse.ArgumentParser();p.add_argument('--manifest',required=True);p.add_argument('--output',required=True);p.add_argument('--kind',choices=['SOURCE','IC'],required=True);a=p.parse_args();module.run(a.manifest,a.output,a.kind)
