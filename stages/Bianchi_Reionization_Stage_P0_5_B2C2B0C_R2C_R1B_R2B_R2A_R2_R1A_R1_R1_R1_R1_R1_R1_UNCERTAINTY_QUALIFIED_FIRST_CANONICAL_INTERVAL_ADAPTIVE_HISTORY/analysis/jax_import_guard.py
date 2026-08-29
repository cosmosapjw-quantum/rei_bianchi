#!/usr/bin/env python3
"""Import-only fail-closed JAX guard for the NumPy interval path."""
from __future__ import annotations
import importlib.util,sys,types
class GuardInvoked(RuntimeError):pass
class _Config:
    @staticmethod
    def update(name,value):
        if name!="jax_enable_x64" or value is not True:raise GuardInvoked("unsupported guarded configuration")
class _Deferred:
    def __init__(self,label):self.label=label
    def __call__(self,*a,**k):raise GuardInvoked(f"guarded JAX callable {self.label} invoked")
class _Namespace(types.ModuleType):
    def __getattr__(self,name):return _Deferred(f"{self.__name__}.{name}")
def _transform(name):return lambda *a,**k:_Deferred(name)
def install_if_missing():
    if importlib.util.find_spec("jax") is not None:return False
    jax=types.ModuleType("jax");jax.__path__=[];jax.config=_Config();jax.Array=type("GuardedJaxArray",(),{})
    jax.jit=_transform("jax.jit");jax.vmap=_transform("jax.vmap");jax.jacfwd=_transform("jax.jacfwd")
    jax.nn=_Namespace("jax.nn");jax.numpy=_Namespace("jax.numpy")
    sys.modules["jax"]=jax;sys.modules["jax.numpy"]=jax.numpy;sys.modules["jax.nn"]=jax.nn
    return True
