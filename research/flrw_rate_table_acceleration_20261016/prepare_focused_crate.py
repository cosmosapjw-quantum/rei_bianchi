#!/usr/bin/env python3
"""Build harness importing production paths, excluding unrelated joint_affine.

Rust 1.85.1 cannot compile that unreferenced module's later-stabilized float
next_up/next_down API. This script changes no production source arithmetic.
"""
import pathlib,re
unit=pathlib.Path(__file__).resolve().parent;repo=unit.parent.parent
src=repo/'rust/rei_microphysics/src';text=(src/'lib.rs').read_text()
assert text.count('mod joint_affine;')==1
text=text.replace('mod joint_affine;\n','')
text,n=re.subn(r'pub use joint_affine::\{.*?\};\n','',text,flags=re.S)
assert n==1
def module(m):
 visibility=m.group(1) or '';name=m.group(2)
 return f'#[path = "{src/name}.rs"]\n{visibility}mod {name};'
text=re.sub(r'^(pub )?mod (\w+);$',module,text,flags=re.M)
dest=unit/'probe/focused_lib.rs';dest.write_text(text)
print(dest)
