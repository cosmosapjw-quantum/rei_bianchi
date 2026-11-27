"""HE27 one-sided admission for tiny original cutoff-crossing intervals.

The immutable v2 table handles every long interval.  Within a short interval
between two original HE25 breakpoints, binary64 energy evaluation can round a
node to the opposite side of a Verner/source threshold while HE25 correctly
uses the fixed midpoint mask for the whole interval.  Fit each newborn source
on that *same* one-sided mask, retaining the HE26 donor N/U/species moments and
the original 3e-13 admission check.  Existing photons are never remapped.
"""
from sourcecut_v2 import SourceCutModel as _EventSegmentedModel


class SourceCutModel(_EventSegmentedModel):
    """Opt-in v3 source with a single owner for each interval's source mask."""

    def _raw_source(self, t):
        active = self._active_interval
        if (active is not None and active not in self._source_tables and
                self._cut_bounds[active] <= t <= self._cut_bounds[active + 1]):
            return self._one_sided_endpoint(t)
        return super()._raw_source(t)
