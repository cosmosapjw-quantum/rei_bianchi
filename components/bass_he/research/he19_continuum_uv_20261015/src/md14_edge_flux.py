"""Research-only MD14 continuum threshold source splitting."""
from dataclasses import dataclass
from functools import lru_cache
import math
EDGES = (13.6,24.59,54.42,100.0)
KTEV = 1.380649e-16*50000.0/1.602176634e-12

@dataclass(frozen=True)
class Cell:
    lo:float
    hi:float
    n:float
    u:float
    @property
    def mean(self): return self.u/self.n

def shape(e):
    x=e/KTEV
    return 0.0 if x>700 else e*e/math.expm1(x)

def simpson(lo,hi,moment=0,panels=32):
    if not(math.isfinite(lo) and math.isfinite(hi) and lo>0 and hi>=lo and panels>=2 and panels%2==0):
        raise ValueError("invalid quadrature")
    if lo==hi:return 0.0
    step=(hi-lo)/panels
    acc=0.0
    for i in range(panels+1):
        e=lo+step*i
        w=1 if i in (0,panels) else (2 if i%2==0 else 4)
        acc+=w*shape(e)*(e if moment else 1)
    return acc*step/3
@lru_cache(maxsize=24)
def source_cells(m):
    """Match original AxbiSource Simpson32/log-energy bins."""
    if type(m)!=int or not 1<=m<=1024:raise ValueError("native m domain")
    out=[]
    for a,b in zip(EDGES[:-1],EDGES[1:]):
        for j in range(m):
            lo=a if j==0 else a*(b/a)**(j/m)
            hi=b if j+1==m else a*(b/a)**((j+1)/m)
            out.append(Cell(lo,hi,simpson(lo,hi),simpson(lo,hi,1)))
    return tuple(out)

def realizable(c):
    if c is None:return True
    if not(c.n>0 and c.u>0):return False
    return c.lo-2e-11 <= c.u/c.n <= c.hi+2e-11

def split_cell(c,cut):
    """Two supported nonnegative children, preserving source parent N/U."""
    if cut<=c.lo:return None,c
    if cut>=c.hi:return c,None
    nl=simpson(c.lo,cut); nr=simpson(cut,c.hi)
    if not(nl>0 and nr>0):raise ArithmeticError("invalid positive split")
    fac=c.n/(nl+nr)
    nl*=fac; nr=c.n-nl
    ul=fac*simpson(c.lo,cut,1)
    ur=fac*simpson(cut,c.hi,1)
    correction=c.u-(ul+ur)
    if nl>=nr:ul+=correction
    else:ur+=correction
    l=Cell(c.lo,cut,nl,ul);r=Cell(cut,c.hi,nr,ur)
    if not(realizable(l) and realizable(r)):
        raise ArithmeticError("unsupported conditional centroid")
    return l,r

def partition(cells,g,threshold):
    """Snapshot cut; irreversible passivation only if photon never blueshifts."""
    if not(math.isfinite(g) and g>0 and math.isfinite(threshold) and threshold>0):
        raise ValueError("invalid geometry/threshold")
    passive=[];active=[]
    for c in cells:
        p,a=split_cell(c,threshold/g)
        if p is not None:passive.append(p)
        if a is not None:active.append(a)
    return (math.fsum(c.n for c in passive),
            math.fsum(c.u for c in passive),
            math.fsum(c.n for c in active),
            math.fsum(c.u for c in active))

def native_lower_node(cells):
    """Old source-centroid distribution to physical lower node."""
    first=cells[0]
    total=math.fsum(c.n for c in cells)
    w=(first.hi-first.mean)/(first.hi-first.lo)
    if not 0<=w<=1:raise ArithmeticError("source centroid outside support")
    return first.n*w/total
def audit(m,h):
    """Single source birth, FLRW g=exp(-h), h=ln(a_final/a_birth)."""
    if not math.isfinite(h) or h<0:raise ValueError("h domain")
    cells=source_cells(m);g=math.exp(-h)
    n=math.fsum(c.n for c in cells);u=math.fsum(c.u for c in cells)
    np,up,na,ua=partition(cells,g,13.6)
    final_u=g*(up+ua);work=(1-g)*u
    species={name:partition(cells,g,cut)[0]/n
             for name,cut in zip(("HI","HeI","HeII"),EDGES[:3])}
    return {"m":m,"h":h,"g":g,"emitted_n":n,"emitted_u_eV":u,
            "passive_n":np,"active_n":na,"passive_u_eV":g*up,
            "active_u_eV":g*ua,"redshift_work_eV":work,
            "N_residual":n-np-na,"U_residual_eV":u-final_u-work,
            "physical_below13p6_fraction":np/n,
            "native_first_node_ghost_fraction":native_lower_node(cells),
            "species_below_cut_fractions":species,"mean_birth_eV":u/n}

def independent_reference(h,cut=13.6,panels=4096):
    """Whole-band Simpson numerical reference, not certified enclosure."""
    if not math.isfinite(h) or h<0:raise ValueError("h domain")
    boundary=cut*math.exp(h)
    total=math.fsum(simpson(a,b,panels=panels)
                    for a,b in zip(EDGES[:-1],EDGES[1:]))
    below=math.fsum(simpson(a,min(b,boundary),panels=panels)
                    for a,b in zip(EDGES[:-1],EDGES[1:])
                    if boundary>a)
    return below/total
