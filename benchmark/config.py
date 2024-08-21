import copy
import importlib
import timeit
from dataclasses import dataclass
from types import ModuleType
from typing import Any, Callable, Generic, TypeVar

from .errors import IncorrectOutput


T = TypeVar('T')

TestedFunction = Callable[..., T]
Args = tuple[Any, ...]
DisplayMethod = Callable[[T], str]
VerifyMethod = Callable[[T, T], bool]


def default_verify(actual: T, expected: T) -> bool:
    return actual == expected


@dataclass(slots=True)
class Test(Generic[T]):
    repetitions: int

    args: tuple[Any, ...]
    expected: T

    _verify: VerifyMethod[T]

    def verify(self, actual: T, expected: T):
        if expected is not None and actual is None:
            return False

        return self._verify(actual, expected)

    def benchmark(self, tested_function: TestedFunction[T]) -> float:
        copied_args = copy.deepcopy(self.args)  # Copy the args so that if the tested function mutates them, it won't mess up future tests.
        actual: T = tested_function(*copied_args)

        if not self.verify(actual, self.expected):
            raise IncorrectOutput[T](self.expected, actual)

        return timeit.timeit(lambda: tested_function(*copied_args), number=self.repetitions) / self.repetitions


@dataclass(slots=True)
class TestProfile(Generic[T]):
    functions: list[tuple[str, TestedFunction[T]]]
    cases: list[Test[T]]

    display: DisplayMethod[T]


def setup(module_name: str, repetitions: int) -> TestProfile[Any]:
    module: ModuleType = importlib.import_module(module_name)

    try:
        imported_functions: list[tuple[str, TestedFunction[Any]]] = [('', getattr(module, 'tested_function'))]
    except AttributeError:
        imported_functions = getattr(module, 'tested_functions')

    try:
        verify: VerifyMethod[Any] = getattr(module, 'verify')
    except AttributeError:
        verify = default_verify

    raw_test_cases: list[tuple[Args, Any]] = getattr(module, 'test_cases')
    test_cases: list[Test[Any]] = [Test(repetitions, args, expected, verify) for args, expected in raw_test_cases]

    try:
        display_method: DisplayMethod[Any] = getattr(module, 'display_method')
    except AttributeError:
        display_method = str

    return TestProfile(imported_functions, test_cases, display_method)
