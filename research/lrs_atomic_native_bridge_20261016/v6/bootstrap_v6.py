"""Find the sibling pinned V4/V5 inputs, in repository or standalone ZIP."""
from pathlib import Path
import sys


def setup():
    here=Path(__file__).resolve().parent
    roots=(here.parent,here.parent.parent,here.parent/'intake',
           here.parent.parent/'intake',here.parent.parent/'research')
    for research in roots:
        old=research/'lrs_threshold_oracle_20261015'
        source=research/'lrs_atomic_native_bridge_20261016'
        if (old/'recomb_thermal.py').is_file() and (source/'donor'/'rate_table.py').is_file():
            for path in (here,old,source,source/'donor'):
                if str(path) not in sys.path:
                    sys.path.insert(0,str(path))
            return research
    raise ImportError('Could not locate source-pinned sibling V4/V5 scientific modules')
