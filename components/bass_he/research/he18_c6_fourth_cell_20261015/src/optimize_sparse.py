#!/usr/bin/env python3
"""Optional exact-interval sparse reaction update (not a floating-point threshold).

Only an identically-zero interval Jet opacity can enter the transparent fast path.
No photon/source node is dropped; all 2904 photon residuals remain evaluated.
"""
from pathlib import Path
import argparse

OLD="""        rp=[];node_values=[];cache={}
        for j in range(len(self.q)):
"""
NEW="""        rp=[];node_values=[];cache={}
        lf=[1-y[0],(1-y[1]-y[2])*FF,y[1]*FF]
        nhc=env['nh']*C
        c_over_volume=Jet.constant(C,order)/env['vr']
        for j in range(len(self.q)):
"""
OLD2="""            chi=y[0]+(y[1]+2*y[2])*FF;lf=[1-y[0],(1-y[1]-y[2])*FF,y[1]*FF]
            kap=sum((env['nh']*C*lf[a]*sigma[a] for a in range(3)),Jet.constant(0,order))
            N=y[4+j]
            for a in range(3):
                v=sigma[a]*C*N/env['vr'];gm[a]=gm[a]+v;qp[a]=qp[a]+v*(E-CHI[a])
            rp.append(dy[4+j]-(src-kap*N)*self.h)
"""
NEW2="""            N=y[4+j]
            # Exact enclosure-zero is the ONLY admission to sparse evaluation.
            zero=[all(lo(z)==hi(z)==0 for z in s.c) for s in sigma]
            if all(zero):
                rp.append(dy[4+j]-src*self.h)
            else:
                kap=sum((nhc*lf[a]*sigma[a] for a in range(3) if not zero[a]),
                        Jet.constant(0,order))
                photons=c_over_volume*N
                for a in range(3):
                    if not zero[a]:
                        v=sigma[a]*photons
                        gm[a]=gm[a]+v
                        qp[a]=qp[a]+v*(E-CHI[a])
                rp.append(dy[4+j]-(src-kap*N)*self.h)
"""
def optimize(src):
    if src.count(OLD)!=1 or src.count(OLD2)!=1:
        raise ValueError("SPARSE_SOURCE_ANCHOR_CHANGED")
    return src.replace(OLD,NEW,1).replace(OLD2,NEW2,1)
if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--runtime",type=Path,required=True)
    a=parser.parse_args()
    file=a.runtime/"src"/"warm_interval.py"
    source=file.read_text()
    optimized=optimize(source)
    file.write_text(optimized)
    print("CERTIFIED_ZERO_BRANCH_OPTIMIZER_APPLIED",file)
