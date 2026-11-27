"""Atomic project evidence writes; no scientific computation."""
import hashlib
import json
import os
from pathlib import Path
import tempfile


def identity(path):
    data = Path(path).read_bytes()
    return {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}


def atomic_bytes(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(dir=path.parent, prefix=path.name + '.')
    try:
        with os.fdopen(fd, 'wb') as f:
            f.write(data); f.flush(); os.fsync(f.fileno())
        os.replace(temporary, path)
        fd = os.open(path.parent, os.O_RDONLY)
        try: os.fsync(fd)
        finally: os.close(fd)
    finally:
        if os.path.exists(temporary): os.unlink(temporary)


def atomic_json(path, obj):
    atomic_bytes(path, (json.dumps(obj, indent=2, allow_nan=False) + '\n').encode('utf-8'))


def cjson(z):
    return {'real': float(z.real), 'imag': float(z.imag)}
