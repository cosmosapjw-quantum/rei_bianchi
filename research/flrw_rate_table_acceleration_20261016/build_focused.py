#!/usr/bin/env python3
"""Portable dependency-free build of the frozen focused test executables."""
import argparse,pathlib,re,subprocess
p=argparse.ArgumentParser();p.add_argument('--rustc',default='rustc');p.add_argument('--output',required=True);a=p.parse_args()
unit=pathlib.Path(__file__).resolve().parent;bundle=unit/'focused_bundle';src=bundle/'rust/rei_microphysics/src';out=pathlib.Path(a.output).resolve();out.mkdir(parents=True,exist_ok=True)
text=(src/'lib.rs').read_text().replace('mod joint_affine;\n','')
text,n=re.subn(r'pub use joint_affine::\{.*?\};\n','',text,flags=re.S);assert n==1
def module(m):return f'#[path = "{src/m.group(2)}.rs"]\n{m.group(1) or ""}mod {m.group(2)};'
text=re.sub(r'^(pub )?mod (\w+);$',module,text,flags=re.M)
lib=out/'focused_lib.rs';lib.write_text(text)
common=[a.rustc,'--edition=2021','-C','opt-level=3','-C','codegen-units=4']
subprocess.run(common+['--crate-name','rei_microphysics','--crate-type','rlib',str(lib),'-o',str(out/'librei_microphysics.rlib')],check=True)
for name in ['rate_table','lithium_rates']:
 subprocess.run(common+['--test',str(bundle/f'rust/rei_microphysics/tests/{name}.rs'),'--extern',f'rei_microphysics={out/"librei_microphysics.rlib"}','-o',str(out/(name+'_tests'))],check=True)
print('Built frozen focused sources; full production crate build is not verified on Rust 1.85.1.')
