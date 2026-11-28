from __future__ import annotations

def state_index(N: int, l: int, m: int) -> int:
    """Paper Eq. (49), 1-based ARSENY state index j(N,l,m).

    j = (N-1) N (N+1) / 6 + l(l+1)/2 + |m| + 1
    """
    if N < 1:
        raise ValueError("N must be >= 1")
    if l < 0 or l >= N:
        raise ValueError("require 0 <= l < N")
    if abs(m) > l:
        raise ValueError("require |m| <= l")
    return (N - 1) * N * (N + 1) // 6 + l * (l + 1) // 2 + abs(m) + 1

def enumerate_states(Nmax: int):
    """Enumerate unique |m|-resolved states in the paper's Eq. (49) ordering."""
    if Nmax < 1:
        raise ValueError("Nmax must be >= 1")
    rows = []
    for N in range(1, Nmax + 1):
        for l in range(N):
            for mabs in range(l + 1):
                rows.append((state_index(N,l,mabs),N,l,mabs))
    return sorted(rows)
