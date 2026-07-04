from .base import *

try:
    from .development import *
except ImportError:  # pragma: no cover - development settings may be absent in production
    pass
