"""Source-locked REI/BASS photo-channel compatibility, no ODE integrations.

The immutable 13-row Puchwein-2019 projection is NOT the source's full 59-row
raw file. BASS's fixed-spectrum/single-UV-amplitude rule is taken from its
original atomic_network.py. The adapter below is a mathematical event-rate
operator, NOT a reconstructed physical photon spectrum or thermal heating law.
"""
from __future__ import annotations

from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path
from typing import Sequence
import hashlib
import json
import math
import numpy as np
import sympy as sp

UNIT = Path(__file__).resolve().parents[1]
SOURCE = UNIT / "source"
P19 = SOURCE / "PUCHWEIN19_13.json"
BASS_NETWORK = SOURCE / "BASS_atomic_network.py"
BASS_MODEL = SOURCE / "BASS_atomic_model.json"
REI_SOURCE17 = SOURCE / "REI_UVB_source17.py"
REI_SAVED = SOURCE / "REI_saved7.json"
SHA256 = {
    "PUCHWEIN19_13.json": "dcd13144072584085f49698e40c9822e074fecc2a6046605dc9d67cfe7cc3eff",
    "BASS_atomic_network.py": "baecce07aded483fa60006cc576feff67d068c0d70394f7095abacc6d47eaa80",
    "BASS_atomic_model.json": "9cc399e9e33ece544109f442f50b00c463cde96e406965e796240eaabd49c614",
    "REI_UVB_source17.py": "3e8735874b53516dfe2df781598aaf77407fd12e64b72c048f257982cbb2812f",
    "REI_saved7.json": "7653f7f75fcbe92465de1b22faabf565efee36e90d1d967499f68ff123a6bc77",
}
SOURCE_FILES = {k: SOURCE / k for k in SHA256}
CHANNELS = ("HI", "HeI", "HeII")
RATE_FIELDS = (1, 3, 5)
EVENTS = (
    (1, 2, 0), (3, 4, 0), (5, 6, 0),
    (7, 8, 1), (8, 9, 2), (10, 11, 1), (11, 12, 2),
)
Q17 = (0, 0, 1, 0, 1, 0, 1, 0, 1, 2, 0, 1, 2, 0, 1, 2, 3)
A17 = (1, 1, 1, 2, 2, 3, 3, 3, 3, 3, 4, 4, 4, 7, 7, 7, 7)


def source_lock() -> dict[str,str]:
    out = {}
    for name, path in SOURCE_FILES.items():
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != SHA256[name]:
            raise ValueError(f"SOURCE_SHA_MISMATCH:{name}:{digest}")
        out[name] = digest
    bcode = SOURCE_FILES["BASS_atomic_network.py"].read_text()
    bmodel = json.loads(SOURCE_FILES["BASS_atomic_model.json"].read_text())
    p = json.loads(SOURCE_FILES["PUCHWEIN19_13.json"].read_text(), parse_float=Decimal)
    if "G0=uv * self._Gphoto" not in bcode:
        raise ValueError("BASS_FIXED_SPECTRAL_AMPLITUDE_MISSING")
    if bmodel["photon_field"]["late_Gamma_HI_s"] != 1e-12:
        raise ValueError("BASS_PHOTON_FIELD_LOCK_MISMATCH")
    if p["parent_git_blob"] != "218d81f68447da438228a7b102e1cec96a8e8a1a" or len(p["rows"]) != 13:
        raise ValueError("P19_SOURCE_MAPPING_MISMATCH")
    return out


def source_rows() -> list[tuple[Decimal,...]]:
    source_lock()
    p = json.loads(P19.read_text(), parse_float=Decimal)
    rows = [tuple(r) for r in p["rows"]]
    assert all(len(r) == 7 for r in rows)
    if not all(rows[i][0] < rows[i+1][0] for i in range(12)):
        raise ValueError("P19_GRID_NOT_SORTED")
    if not all(v > 0 for r in rows for v in r[1:]):
        raise ValueError("P19_NONPOSITIVE_RATES")
    return rows


def selected_rows() -> list[tuple[Decimal,...]]:
    return [r for r in source_rows() if Decimal("2.4") <= r[0] <= Decimal("4.75")]


def exact(x: Decimal | int | Fraction) -> Fraction:
    if isinstance(x, float) or isinstance(x, bool):
        raise TypeError("Use source decimal text, not binary float or bool")
    return Fraction(x)


def target_3(row: Sequence[Decimal]) -> tuple[Fraction,Fraction,Fraction]:
    return tuple(exact(row[i]) for i in RATE_FIELDS)


def exact_rate_matrices() -> tuple[sp.Matrix,sp.Matrix]:
    rows = selected_rows()
    mat3 = sp.Matrix([[sp.Rational(str(x)) for x in (r[1],r[3],r[5])] for r in rows])
    mat6 = sp.Matrix([[sp.Rational(str(x)) for x in r[1:]] for r in rows])
    return mat3,mat6


def rank_witness() -> dict:
    mat3,mat6=exact_rate_matrices()
    rows=selected_rows()
    wanted = (Decimal("2.48"),Decimal("3.64"),Decimal("4.62"))
    index=[next(i for i,r in enumerate(rows) if r[0] == z) for z in wanted]
    det = sp.factor(mat3[index,:].det(method="domain-ge"))
    return {"ranks": (int(mat3.rank()),int(mat6.rank())),
            "all_calibrated_rows":len(rows), "witness_knots":tuple(map(str,wanted)),
            "witness_det_3x3":str(det), "witness_det_scaled":float(det*10**36)}


def ratio_exact(row: Sequence[Decimal], numerator_field: int = 5) -> Fraction:
    if numerator_field not in (3,5):
        raise ValueError("Must use HeI or HeII relative to HI")
    return exact(row[numerator_field])/exact(row[1])


def minimax_two_epochs() -> dict:
    rows=selected_rows()
    a=next(r for r in rows if r[0]==Decimal("2.48"))
    b=next(r for r in rows if r[0]==Decimal("4.62"))
    ratios=(ratio_exact(a),ratio_exact(b))
    rlo,rhi=sorted(ratios)
    with localcontext() as ctx:
        ctx.prec=80
        lo=Decimal(rlo.numerator)/Decimal(rlo.denominator)
        hi=Decimal(rhi.numerator)/Decimal(rhi.denominator)
        factor=hi/lo
        k=(lo*hi).sqrt()
        eps=(hi.sqrt()-lo.sqrt())/(hi.sqrt()+lo.sqrt())
        t_hi=2*hi/(hi+k)
        t_lo=2*lo/(lo+k)
    return {"epochs":["2.48","4.62"],"HeII_over_HI_exact": [f"{x.numerator}/{x.denominator}" for x in ratios],
            "rmax_over_rmin":str(factor),"optimal_static_ratio":str(k),
            "minimax_relative_error":str(eps),"optimal_HI_amplitudes_relative": [str(t_hi),str(t_lo)],
            "exact_cross_ratio_witness": str(ratios[0]-ratios[1]),
            "claim":"Sharp for 2 epochs x {HI,HeII} over ANY positive fixed channel ratio and freely chosen per-epoch scalar; only printed P19 13-row numeric projection"}


def generator_17(r: Sequence[Fraction]) -> list[list[Fraction]]:
    if len(r)!=3 or any(x<=0 for x in r):
        raise ValueError("Need three strictly positive photo rate moments")
    m=[[Fraction(0) for _ in range(17)] for _ in range(17)]
    for s,d,k in EVENTS:
        m[s][s]-=r[k]
        m[d][s]+=r[k]
    return m


def derivative_17(r: Sequence[Fraction],y: Sequence[Fraction]) -> list[Fraction]:
    if len(y)!=17:raise ValueError("y length17 required")
    if any(v<0 for v in y):raise ValueError("negative frozen state")
    g=generator_17(r)
    return [sum(g[i][j]*y[j] for j in range(17)) for i in range(17)]


def electronic_jacobian_17(r: Sequence[Fraction]) -> list[list[Fraction]]:
    return generator_17(r)


def check_event_conservation(r: Sequence[Fraction],y: Sequence[Fraction]):
    v=derivative_17(r,y)
    return {"nucleon":sum(a*f for a,f in zip(A17,v)),
            "nuclear_count":sum(v),
            "electron":sum(q*f for q,f in zip(Q17,v)),
            "positive_event_electrons":sum(r[k]*y[s] for s,d,k in EVENTS)}


def p19_float_rates(z: float, coeff: tuple[float,float]=(0.,0.)) -> np.ndarray:
    """Match PR261 log(rate) interpolation and COMMON beta,kappa multiplier only."""
    if not (2.4<=z<=4.75):raise ValueError("OUTSIDE_CALIBRATION_DOMAIN")
    rows=source_rows()
    grid=np.array([float(row[0]) for row in rows])
    vals=np.array([[float(row[i]) for i in RATE_FIELDS] for row in rows])
    if len(coeff)!=2 or not all(math.isfinite(a) for a in coeff):
        raise ValueError("INVALID_BETA_KAPPA")
    return np.exp(np.array([np.interp(z,grid,np.log(vals[:,j])) for j in range(3)])) * 10.**(coeff[0]+coeff[1]*(z-3.6))


def float_generator_17(r: np.ndarray) -> np.ndarray:
    m=np.zeros((17,17),float)
    for s,d,k in EVENTS:
        m[s,s]-=r[k];m[d,s]+=r[k]
    return m


def same_source_frozen_replay() -> list[dict]:
    """Compare with the unmodified PR262 source17.run_saved() on 7 saved states.

    Import runs *only* frozen-state source algebra, no new IVP or photo histories.
    """
    import importlib.util
    root=UNIT/"source/pr262_replay/research/rei_uvb_saved_state_source_tangent_20261029/code/source17.py"
    if not root.exists():raise FileNotFoundError("PR262_REPLAY_SOURCE_MISSING")
    spec=importlib.util.spec_from_file_location("verified_pr262_source17",root)
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    port,d,p,rows,geo=mod.load_parent()
    out=[]
    for item in mod.saved_rows():
        z=item["z"]
        yy=np.asarray(item["y"],float)
        original=mod.source17(z,yy,geo["a0"],rows,port)
        rate=p19_float_rates(z,tuple(geo["a0"]))
        replay=float_generator_17(rate)@yy
        actual_jac=float_generator_17(rate)
        abs_F=float(np.max(np.abs(original["F"]-replay)))
        rel_F=abs_F/max(float(np.max(np.abs(original["F"]))),1e-300)
        abs_J=float(np.max(np.abs(original["J_y"]-actual_jac)))
        rel_J=abs_J/max(float(np.max(np.abs(original["J_y"]))),1e-300)
        out.append({"z":z,"max_relative_rhs_difference":rel_F,
                    "max_relative_jacobian_difference":rel_J,
                    "orig_electrons":float(original["electron_rate_per_Href_s"]),
                    "replay_electrons":float(np.array(Q17)@replay)})
    return out
