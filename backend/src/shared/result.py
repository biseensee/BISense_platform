"""A small Result type for use cases that want explicit success/failure
values instead of relying purely on exceptions for expected failure paths
(e.g. "connection test failed" is a normal outcome, not an error log).

Use exceptions (`core/exceptions.py`) for programming errors and genuine
domain-rule violations that the presentation layer maps to 4xx/5xx; use
`Result` inside a use case when a failure is an ordinary, expected branch
that the caller must handle explicitly.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")
E = TypeVar("E")


@dataclass(frozen=True, slots=True)
class Ok(Generic[T]):
    value: T
    is_ok: bool = True


@dataclass(frozen=True, slots=True)
class Err(Generic[E]):
    error: E
    is_ok: bool = False


Result = Ok[T] | Err[E]
