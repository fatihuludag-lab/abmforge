from __future__ import annotations

from abmforge.data.dataset import Dataset


class InMemoryStorage(Dataset):
    """In-memory storage backend.

    This backend preserves the current Dataset behavior while introducing
    a storage abstraction for future file-based and columnar backends.
    """

    pass
