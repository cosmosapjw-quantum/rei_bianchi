"""Exact local MPFI checker with per-record common-expression reuse.

Point RHS values need no derivatives. Every interval AD box and inverse bound
uses the original independently reviewed local formula; no wider proof domain.
"""
import argparse,importlib.util,json,time
from pathlib import Path


def install_cache(v):
    m=v.m;R=m.R;original_model=m.Model;original_derivatives=m.derivatives
    original_j=m.J;original_record=v.certify_record
    stats={'records':0,'rhs_reuses':0,'derivative_reuses':0,'point_rhs_calls':0}
    rhs_cache={};derivative_cache={}
    def key(y):return tuple((str(R(x).lower()),str(R(x).upper())) for x in y)

    class Scalar:
        # Used only for point residual values; never for any AD or observables.
        def __init__(self,value,index=None):self.v=R(value)
        def __add__(self,b):return Scalar(self.v+(b.v if isinstance(b,Scalar) else R(b)))
        __radd__=__add__
        def __neg__(self):return Scalar(-self.v)
        def __sub__(self,b):return self+-(b if isinstance(b,Scalar) else Scalar(b))
        def __rsub__(self,b):return Scalar(b)-self
        def __mul__(self,b):return Scalar(self.v*(b.v if isinstance(b,Scalar) else R(b)))
        __rmul__=__mul__
        def __truediv__(self,b):return Scalar(self.v/(b.v if isinstance(b,Scalar) else R(b)))
        def __rtruediv__(self,b):return Scalar(b)/self
        def power(self,p):assert self.v.lower()>0;return Scalar((R(float(p))*self.v.log()).exp())
        def exp(self):return Scalar(self.v.exp())
        def log(self):return Scalar(self.v.log())

    class CachedModel(original_model):
        def rhs(self,y):
            if all(R(x).lower()==R(x).upper() for x in y):
                m.J=Scalar
                try:
                    stats['point_rhs_calls']+=1
                    return original_model.rhs(self,y)
                finally:m.J=original_j
            k=key(y)
            if k in rhs_cache:
                stats['rhs_reuses']+=1
                return rhs_cache[k]
            result=original_model.rhs(self,y);rhs_cache[k]=result
            return result

    def derivatives(model,y,dt,c):
        # C is part of the inverse proof; never reuse across preconditioners.
        k=(key(y),str(R(dt)),tuple(str(x) for x in c.list()))
        if k in derivative_cache:
            stats['derivative_reuses']+=1;return derivative_cache[k]
        result=original_derivatives(model,y,dt,c);derivative_cache[k]=result
        return result

    def record(row,previous_box,previous_state):
        rhs_cache.clear();derivative_cache.clear()
        m.Model=CachedModel;m.derivatives=derivatives
        try:
            result=original_record(row,previous_box,previous_state)
            stats['records']+=1;return result
        finally:
            m.Model=original_model;m.derivatives=original_derivatives;m.J=original_j
            rhs_cache.clear();derivative_cache.clear()

    v.certify_record=record
    return stats


def main():
    a=argparse.ArgumentParser();a.add_argument('run_dir',type=Path);a.add_argument('--receipt',required=True,type=Path);a.add_argument('--pilot',action='store_true');p=a.parse_args()
    s=importlib.util.spec_from_file_location('frozen_ft03_history',Path('.cuh/fastest-track/REI-F05/verify_candidate_v2.py'));v=importlib.util.module_from_spec(s);s.loader.exec_module(v)
    for f,expected in v.manifest['source_identity'].items():
        assert v.hashlib.sha256(Path(f).read_bytes()).hexdigest()==expected,'SOURCE_INPUT_MISMATCH: '+f
    stats=install_cache(v);start=time.monotonic();result=v.validate_run(p.run_dir,p.pilot)
    result['validation_expression_reuse']=stats;result['validation_wall_s']=time.monotonic()-start
    p.receipt.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)


if __name__=='__main__':
    main()
