from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar


if TYPE_CHECKING:
    from .config import DisplayMethod

T = TypeVar('T')


class IncorrectOutput(Generic[T], Exception):
    expected: T
    actual: T

    def __init__(self, expected: T, actual: T, name: str = 'item'):
        super().__init__(f'`{name}` must be {expected}, not {actual}!')

        self.expected = expected
        self.actual = actual

    def format(self, display_method: DisplayMethod[T]) -> IncorrectOutput[str]:
        return IncorrectOutput(display_method(self.expected), display_method(self.actual))
