import importlib.util,pathlib,sys
spec=importlib.util.spec_from_file_location('p','/workspace/scratch/6af5e9e6c737/v16_work/implementation/prepare_and_run.py');p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
raise SystemExit(p.run_cases(pathlib.Path('/tmp/tmp7xyqfyhf/evidence'),[sys.executable,'/tmp/tmp7xyqfyhf/stub.py'],[('fail','radau','2'),('fail','radau','4'),('good','ssprk','8')]))
