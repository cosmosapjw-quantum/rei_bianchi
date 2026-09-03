"""Pre-lease production-import firewall successor package.

Package imports expose the hostile-audit hardened common surface. Direct script
entry points explicitly import ``common_v2`` when they need receipt authority.
"""

from __future__ import annotations

import sys

from . import common_v2 as _hardened_common

sys.modules[__name__ + ".common"] = _hardened_common
