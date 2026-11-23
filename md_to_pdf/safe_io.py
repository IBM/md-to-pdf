# Copyright IBM Corp. 2025, 2026
# SPDX-License-Identifier: Apache-2.0

"""Symlink-safe file writing."""

import os
import tempfile
from pathlib import Path


def atomic_write(path, data) -> Path:
    """Write str/bytes to `path` via temp file + os.replace().

    Never follows a symlink at `path`: symlinks are refused, and os.replace()
    would replace (not follow) one that appears after the check.
    """
    path = Path(path)
    if path.is_symlink():
        raise ValueError(f"Refusing to write to symlink: {path}")
    if isinstance(data, str):
        data = data.encode("utf-8")
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".md2pdf-", suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
        os.chmod(tmp, 0o644)
        os.replace(tmp, path)
    except BaseException:
        os.unlink(tmp)
        raise
    return path
