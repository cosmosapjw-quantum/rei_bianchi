"""Geometry-only cap diagnostic; zero states, eigenproblems or quadrature nodes."""
from pathlib import Path
import ast, hashlib, json, math, os, sys, time, tracemalloc
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'code/force_integral.py'
tree=ast.parse(source.read_text())
fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='rectangles')
class CapForDiagnostic(ast.NodeTransformer):
    def visit_Constant(self,node):
        if type(node.value) is int and node.value==50000:
            return ast.copy_location(ast.Constant(100000),node)
        return node
mod=ast.fix_missing_locations(CapForDiagnostic().visit(ast.Module(body=[fn],type_ignores=[])))
ns={'np':np}
exec(compile(mod,'geometry_diagnostic_copy_100000','exec'),ns)
rectangles=ns['rectangles']
c=json.loads((ROOT/'CONTRACT.json').read_text())
records=[]
for rs,profiles in c['fallback_profiles_by_R'].items():
    R=float(rs)
    for profile,p in profiles.items():
        nr=p['radial_elements'];na=p['angular_elements'];L=p['radial_extent']
        if profile=='tail':
            inner=c['tail_edges']['fallback_inner_elements'];outer=c['tail_edges']['fallback_outer_elements']
            y=np.r_[30*np.linspace(0,1,inner+1)**p['radial_grading'],np.linspace(30,40,outer+1)[1:]]
            xe=1+2*y/R
        else:
            xe=1+(2*L/R)*np.linspace(0,1,nr+1)**p['radial_grading']
        ye=np.linspace(-1,1,na+1)
        tracemalloc.start();start=time.perf_counter();cells,meta=rectangles(xe,ye);elapsed=time.perf_counter()-start
        current,peak=tracemalloc.get_traced_memory();tracemalloc.stop()
        corners=sum(a==1 and (cc==-1 or d==1) for a,b,cc,d in cells)
        unique={id(cells):sys.getsizeof(cells)}
        for cell in cells:
            unique[id(cell)]=sys.getsizeof(cell)
            for x in cell: unique[id(x)]=sys.getsizeof(x)
        records.append({'R':R,'profile':profile,**meta,'diagnostic_wall_seconds':elapsed,'tracemalloc_peak_bytes':peak,'geometry_unique_object_bytes':sum(unique.values()),'duffy_cells':corners,'points_at_q56':(len(cells)+corners)*56**2,'max_stream_batch_points_at_q56':32*56**2})
        del cells
maximum=max(x['rectangles'] for x in records)
result={'schema':'bass-he-c2d-geometry-cap-diagnostic-v1','new_physical_evaluations':0,'new_eigensolves':0,'quadrature_nodes_generated':0,'contract_sha256':hashlib.sha256((ROOT/'CONTRACT.json').read_bytes()).hexdigest(),'production_force_source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'method':'AST copy of production rectangles with only integer cap 50000 changed to100000 in diagnostic namespace; production file unchanged; exact registered fallback knot vectors.','records':records,'maximum_rectangles':maximum,'recommended_explicit_cap':100000,'maximum_subdivision_depth':max(x['maximum_depth'] for x in records),'maximum_geometry_tracemalloc_peak_bytes':max(x['tracemalloc_peak_bytes'] for x in records),'limits':'Geometry Python object memory only; excludes live eigenstates, coefficient basis arrays and streamed integrand working arrays. No physical runtime or full-worker memory claim.'}
p=ROOT/'review/GEOMETRY_CAP_DIAGNOSTIC.json'
with p.open('x') as f: json.dump(result,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
print(json.dumps(result,indent=2))
