"""Create-only, fsynced JSON outputs; existing success/failure artifacts are retained."""
from pathlib import Path
from typing import Any
import json
import os
import tempfile


def write_json_create_only(path: str | Path, data: Any) -> None:
    path = Path(path)
    payload = (json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode('utf-8')
    if path.exists() or path.is_symlink():
        raise FileExistsError(str(path))
    fd, temp = tempfile.mkstemp(prefix='.' + path.name + '.', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as f:
            f.write(payload)
            f.flush()
            os.fsync(f.fileno())
        os.link(temp, path, follow_symlinks=False)  # atomic, refuses a raced-in destination
        directory_fd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        os.unlink(temp)  # Only this invocation's temporary file is removed.
