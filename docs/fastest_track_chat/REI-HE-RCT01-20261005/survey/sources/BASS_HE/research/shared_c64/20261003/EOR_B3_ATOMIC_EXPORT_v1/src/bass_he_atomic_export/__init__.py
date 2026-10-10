"""Source-explicit atomic rate/count export; separate from optical solvers."""
from .api import (ContractError, SourceUnavailable, export_packet, validate_packet,
                  bundle_packets, write_packet, loads_strict, verify_runtime_bindings)
from .registry import sources
__version__ = '0.1.1'
