"""PHYS42 adaptive interval is a safe exact rational partition, not heuristic proof."""
from fractions import Fraction as F
from pathlib import Path
import pytest
from wu088_hh.phys42_adaptive import adaptive_strip
from wu088_hh.phys42_joint_interval import joint_strip

SRC=Path(__file__).resolve().parents[1]/"research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz"


def test_adaptive_frozen_original_partition_and_validated_min():
    z=adaptive_strip(SRC,F(1),F(1,1000),radial_bins=1,
                     initial_mu_bins=4,target_mu_bins=16,workers=1)
    row=z["radial_partitions"][0]
    cells=[(F(a),F(b),F(q)) for a,b,q in row["best_rational_partition"]]
    assert cells[0][0]==-1 and cells[-1][1]==1
    assert all(x[1]==y[0] for x,y in zip(cells,cells[1:]))
    assert sum((x[2] for x in cells),F(0))==F(row["best_exact_sq"])
    assert len(cells)==row["best_partition_cells"]
    assert z["evaluated_exact_cell_certifications"]==4+2*(16-4)
    coarse=joint_strip(SRC,F(1),F(1,1000),radial_bins=1,mu_bins=4,workers=1)
    assert F(z["certified_signed_broken_L2_upper"])<=F(coarse["full_3D_broken_L2_upper"])
    assert z["source_sha256"]==coarse["source_sha256"]


def test_adaptive_rejects_wrong_domain_and_invalid_workers():
    with pytest.raises(ValueError,match="cusp"):
        adaptive_strip(SRC,F(7,10),F(1,1000),1,4,8)
    with pytest.raises(ValueError):
        adaptive_strip(SRC,F(1),F(0),1,4,8)
    with pytest.raises(ValueError):
        adaptive_strip(SRC,F(1),F(1,1000),1,16,8)
    with pytest.raises(ValueError):
        adaptive_strip(SRC,F(1),F(1,1000),1,4,8,7)
