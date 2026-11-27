"""Explicit worker backend admission."""
import os
THREAD_POLICY={k:'1' for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS','NUMBA_NUM_THREADS')}

def prepare_environment():
    os.environ.update(THREAD_POLICY)

def activate(name):
    if name!='python': raise RuntimeError('ACCELERATOR_PAYLOAD_UNAVAILABLE')
    import numpy, scipy
    try:
        from threadpoolctl import threadpool_info
    except ImportError as exc: raise RuntimeError('threadpoolctl required for actual thread verification') from exc
    pools=threadpool_info()
    if any(x.get('num_threads')!=1 for x in pools): raise RuntimeError(f'nested numerical threads: {pools}')
    return {'backend':'python','pid':os.getpid(),'numpy':numpy.__version__,'scipy':scipy.__version__,'thread_pools':pools,'thread_policy':THREAD_POLICY}
