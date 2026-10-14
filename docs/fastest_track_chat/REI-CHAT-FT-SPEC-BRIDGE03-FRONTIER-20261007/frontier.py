"""Positive birth quadrature on a fixed finite reporting set.

The partition is selected before any gas solve. A source cell is never assigned
an output-dependent reweighting. All variants share one integration master.
"""
from __future__ import annotations
import math
from dataclasses import dataclass
END=1e12; H=1e-14; EB=13.7; SOURCE=5e-15
THRESHOLDS=(13.6,13.598434599702)
REPORTS=tuple(END*i/4 for i in range(1,5))
@dataclass(frozen=True)
class Rule:
    name: str
    bins: int
    order: int
    split: bool
RULES=(Rule('plain_m64',64,1,False),Rule('plain_m128',128,1,False),
       Rule('split_m64',64,1,True),Rule('split_m128',128,1,True),
       Rule('split_g2_32',32,2,True),Rule('split_g2_64',64,2,True))
def birth_edges(n:int,split:bool=True,reports=REPORTS):
    if type(n) is not int or not 1<=n<=4096: raise ValueError('BIRTH_BINS_DOMAIN')
    if any(not math.isfinite(t) or not 0<t<=END for t in reports):raise ValueError('REPORT_DOMAIN')
    if any(b<=a for a,b in zip(reports,reports[1:])):raise ValueError('REPORT_ORDER')
    edges={END*i/n for i in range(n+1)}
    if split:
        for t in reports:
            edges.add(t)
            for ec in THRESHOLDS:
                xi=t-math.log(EB/ec)/H
                if 0<xi<END:edges.add(xi)
    return sorted(edges)
def quadrature(n:int,order:int=1,split:bool=True,reports=REPORTS):
    if order not in (1,2):raise ValueError('QUADRATURE_ORDER')
    edges=birth_edges(n,split,reports);out=[]
    for left,right in zip(edges,edges[1:]):
        width=right-left;mid=left+width/2
        nodes=(mid,) if order==1 else (mid-width/(2*math.sqrt(3)),mid+width/(2*math.sqrt(3)))
        for b in nodes:
            if not left<b<right:raise ValueError('UNRESOLVED_BIRTH_CELL')
            out.append((b,SOURCE*width/order))
    return out
def all_rules():return {r.name:quadrature(r.bins,r.order,r.split) for r in RULES}
def master(lists=None):
    lists=all_rules() if lists is None else lists
    # Retain every original F08 T0 committed-half boundary.
    times={END*i/1600 for i in range(1601)}|set(REPORTS)
    births={b for nodes in lists.values() for b,_ in nodes}
    times.update(births)
    for b in births|{0.0}:
        for ec in THRESHOLDS:
            t=b+math.log(EB/ec)/H
            if 0<t<END:times.add(t)
    return sorted(times)
def refine(times,factor:int):
    if type(factor) is not int or factor not in (1,2):raise ValueError('REFINEMENT_DOMAIN')
    if any(b<=a for a,b in zip(times,times[1:])):raise ValueError('CLOCK_ORDER')
    return sorted(set(times)|{a+(b-a)/2 for a,b in zip(times,times[1:])}) if factor==2 else list(times)
def write_schedule(path,times,nodes):
    from pathlib import Path
    births={b:w for b,w in nodes}
    if len(births)!=len(nodes) or not births.keys()<=set(times):raise ValueError('BIRTH_CLOCK_MAPPING')
    Path(path).write_text('# physical birth at row time; interval ends at next row\n'+
        ''.join(f'{t:.17e}\t{births.get(t,0.0):.17e}\n' for t in times))
