from __future__ import annotations

import os


def is_cloud_mode() -> bool:
    """True when running on Render or other constrained cloud hosts."""
    if os.getenv("RENDER"):
        return True
    return os.getenv("CLOUD_MODE", "").lower() in ("1", "true", "yes")
