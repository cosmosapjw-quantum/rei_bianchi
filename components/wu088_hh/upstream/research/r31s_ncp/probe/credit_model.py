"""In-memory specification model for bounded asynchronous durability.

NOT a production scheduler, persistent WAL, uploader or admission mechanism.
The caller supplies already-verified, identity-bound receipt events; this model
only validates their state transitions. Failed jobs retain credits until an
external recovery protocol reconciles them. No I/O occurs here.
"""
from __future__ import annotations
import re


class CreditLedger:
    def __init__(self, capacity: int):
        if type(capacity) is not int or capacity < 1:
            raise ValueError('positive integer capacity required')
        self.capacity = capacity
        self.states: dict[str, str] = {}
        self.identities: dict[str, str] = {}
        self.receipts: dict[str, set[str]] = {}

    @property
    def outstanding(self) -> int:
        return sum(state != 'ACKED' for state in self.states.values())

    def reserve(self, key: str) -> None:
        if not isinstance(key, str) or not key or key in self.states:
            raise ValueError('nonempty unique job key required')
        if self.outstanding >= self.capacity:
            raise RuntimeError('durability capacity exhausted; stop dispatch')
        self.states[key] = 'INFLIGHT'
        self.receipts[key] = set()

    def local_complete(self, key: str, source_sha256: str) -> None:
        if self.states.get(key) != 'INFLIGHT':
            raise RuntimeError('completion requires an inflight reservation')
        if not isinstance(source_sha256,str) or not re.fullmatch(r'[0-9a-f]{64}',source_sha256):
            raise ValueError('invalid source SHA-256')
        self.identities[key] = source_sha256
        self.states[key] = 'LOCAL'

    def verified_receipt(self, key: str, provider: str, source_sha256: str) -> None:
        if provider not in ('drive','dropbox'):
            raise ValueError('unexpected provider')
        if self.states.get(key) not in ('LOCAL','ACKED'):
            raise RuntimeError('receipt requires a locally committed result')
        if source_sha256 != self.identities[key]:
            raise ValueError('receipt source identity mismatch')
        self.receipts[key].add(provider)
        if self.receipts[key] == {'drive','dropbox'}:
            self.states[key] = 'ACKED'

    def fail(self, key: str) -> None:
        if self.states.get(key) not in ('INFLIGHT','LOCAL'):
            raise RuntimeError('failure requires an outstanding job')
        self.states[key] = 'FAILED_RETAINED_CREDIT'
