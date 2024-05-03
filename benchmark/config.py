import copy
import importlib
import timeit
from types import ModuleType
from typing import Any, Callable, Generic, TypeVar

from .errors import IncorrectOutput


T = TypeVar('T')

TestedFunction = Callable[..., T]
Args = tuple[Any, ...]
DisplayMethod = Callable[[T], str]


class Test(Generic[T]):
    __slots__ = ('repetitions', 'args', 'expected')

    repetitions: int

    args: tuple[Any, ...]
    expected: T

    def __init__(self, repetitions: int, args: tuple[Any, ...], expected: T):
        self.repetitions = repetitions
        self.args = args
        self.expected = expected

    def benchmark(self, tested_function: TestedFunction[T]) -> float:
        copied_args = copy.deepcopy(self.args) # Copy the args so that if the tested function mutates them, it won't mess up future tests.
        actual: T = tested_function(*copied_args)

        if actual != self.expected:
            raise IncorrectOutput[T](self.expected, actual)

        return timeit.timeit(lambda: tested_function(*copied_args), number=self.repetitions) / self.repetitions


def setup(module_name: str, repetitions: int) -> tuple[list[tuple[str, TestedFunction[Any]]], list[Test[Any]], DisplayMethod[Any]]:
    module: ModuleType = importlib.import_module(module_name)

    try:
        imported_functions: list[tuple[str, TestedFunction[Any]]] = [('', getattr(module, 'tested_function'))]
    except AttributeError:
        imported_functions = getattr(module, 'tested_functions')

    raw_test_cases: list[tuple[Args, Any]] = getattr(module, 'test_cases')
    test_cases: list[Test[Any]] = [Test(repetitions, args, expected) for args, expected in raw_test_cases]

    try:
        display_method: DisplayMethod[Any] = getattr(module, 'display_method')
    except AttributeError:
        display_method = str

    return (imported_functions, test_cases, display_method)
