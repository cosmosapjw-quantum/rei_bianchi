import os
from pathlib import Path
from fractions import Fraction
import pytest
from energy06_preflight import owner_birth_measure, require_energy05_macro, LinkRefused

OWNER = Path(os.environ['HH_ON06G_CRATE'])/'src'
SOURCE = OWNER/'paired_runtime.rs'
HH = OWNER/'hh_paired_extension.rs'


def test_actual_owner_births_are_not_the_same_measure():
    full, half = owner_birth_measure(SOURCE, HH, 1.6e11, 1.25e9)
    assert sum(w for _, w in full) == sum(w for _, w in half)
    assert full != half
    assert len(full) == 1 and len(half) == 2
    assert [t for t, _ in half] == [Fraction(1.60625e11), Fraction(1.6125e11)]
    assert half[0][1] > 0


def test_no_birth_chain_cannot_be_committed_as_owner_macro():
    with pytest.raises(LinkRefused, match='ENERGY05_NO_BIRTH_OWNER_BIRTH_MISMATCH'):
        require_energy05_macro(SOURCE, HH, 1.6e11, 1.25e9)


@pytest.mark.parametrize('t0,dt', [(float('nan'),1.25e9),(1.6e11,float('inf')),(1.6e11,0.),(-1.,1.25e9),(1e13,1.25e9)])
def test_invalid_clock_refused_before_schedule(t0, dt):
    with pytest.raises(LinkRefused, match='CLOCK'):
        owner_birth_measure(SOURCE, HH, t0, dt)


def test_source_identity_is_not_inferred_from_filename(tmp_path):
    modified = tmp_path/'paired_runtime.rs'
    modified.write_bytes(SOURCE.read_bytes()+b'\n')
    with pytest.raises(LinkRefused, match='SOURCE_IDENTITY'):
        owner_birth_measure(modified, HH, 1.6e11, 1.25e9)
