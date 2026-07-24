"""Safe filesystem primitives used by ABMForge writers."""

from __future__ import annotations

import os
from pathlib import Path


class UnsafePathError(ValueError):
    """Raised when a filesystem target violates a safety invariant."""


def _absolute_without_requiring_existence(path: Path) -> Path:
    """Return an absolute path without requiring the target to exist."""
    return path.expanduser().absolute()


def _assert_contained(path: Path, *, root: Path) -> None:
    """Require path to be contained inside root."""
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise UnsafePathError(f"Destination is outside the allowed root: {path}") from exc


def _assert_no_symlink_parents(path: Path, *, root: Path) -> None:
    """Reject existing symlinks between root and the destination parent."""
    try:
        relative_parent = path.parent.relative_to(root)
    except ValueError as exc:
        raise UnsafePathError(f"Destination is outside the allowed root: {path}") from exc

    current = root

    for part in relative_parent.parts:
        current = current / part

        if current.exists() and current.is_symlink():
            raise UnsafePathError(f"Destination parent is a symbolic link: {current}")


def ensure_safe_destination(
    destination: str | os.PathLike[str],
    *,
    allowed_root: str | os.PathLike[str],
    reject_symlink_parents: bool = True,
) -> Path:
    """Validate and normalize a write destination.

    The destination must remain inside ``allowed_root`` after lexical
    normalization and symbolic-link resolution. Existing symbolic-link
    parents are rejected by default.

    This function validates a path only. It does not create directories or
    write files.
    """
    root = _absolute_without_requiring_existence(Path(allowed_root)).resolve(strict=False)

    candidate = _absolute_without_requiring_existence(Path(destination))

    # Normalize "." and ".." without resolving symbolic links. This lets us
    # reject traversal before inspecting existing parent components.
    lexical_candidate = Path(os.path.abspath(candidate))

    _assert_contained(lexical_candidate, root=root)

    if lexical_candidate == root:
        raise UnsafePathError("Destination must not be the allowed root itself.")

    if reject_symlink_parents:
        _assert_no_symlink_parents(
            lexical_candidate,
            root=root,
        )

    if lexical_candidate.exists() and lexical_candidate.is_symlink():
        raise UnsafePathError(f"Destination itself is a symbolic link: {lexical_candidate}")

    # Existing path components may resolve through symlinks or junctions.
    # Verify containment again after filesystem resolution.
    resolved_candidate = lexical_candidate.resolve(strict=False)
    _assert_contained(resolved_candidate, root=root)

    return resolved_candidate
