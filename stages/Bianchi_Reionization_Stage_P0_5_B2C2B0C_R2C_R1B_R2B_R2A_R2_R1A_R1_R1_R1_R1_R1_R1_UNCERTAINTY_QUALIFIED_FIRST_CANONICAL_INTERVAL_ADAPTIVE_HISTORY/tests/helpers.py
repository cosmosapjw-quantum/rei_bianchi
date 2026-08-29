import importlib.util,sys
from pathlib import Path
STAGE=Path(__file__).resolve().parents[1]
def load(name,relative):
    p=STAGE/relative;s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
