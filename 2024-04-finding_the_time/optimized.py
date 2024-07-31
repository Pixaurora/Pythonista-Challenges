from dataclasses import dataclass
from typing import Callable, NamedTuple, Protocol


class Operation(Protocol):
    def apply(self, dates: list[str]) -> None: ...


# Assuming date format DD-MM-YYYY_HH:MM


def day(date: str) -> str:
    return date[0:2]


def month(date: str) -> str:
    return date[3:5]


def year(date: str) -> str:
    return date[6:10]


def hour(date: str) -> str:
    return date[11:13]


def minute(date: str) -> str:
    return date[14:16]


def without_separator(date: str) -> int:
    return int(year(date) + month(date) + day(date) + hour(date) + minute(date))


def indices_with_property(property: Callable[[str], str], value: str, dates: list[str]):
    return [index for index, date in enumerate(dates) if property(date) == value]


@dataclass(slots=True)
class SortAsc(Operation):
    def apply(self, dates: list[str]) -> None:
        dates.sort(key=without_separator)


@dataclass(slots=True)
class SortDsc(Operation):
    def apply(self, dates: list[str]) -> None:
        dates.sort(key=without_separator, reverse=True)


@dataclass(slots=True)
class MoveMonthUp(Operation):
    month: str

    def apply(self, dates: list[str]) -> None:
        for index in indices_with_property(month, self.month, dates):
            dates.insert(max(index - 1, 0), dates.pop(index))


@dataclass(slots=True)
class MoveDayDown(Operation):
    day: str

    def apply(self, dates: list[str]) -> None:
        end_index: int = len(dates)

        for index in indices_with_property(day, self.day, dates)[::-1]:
            dates.insert(min(index + 1, end_index), dates.pop(index))


@dataclass(slots=True)
class YearToTop(Operation):
    year: str

    def apply(self, dates: list[str]) -> None:
        for index in indices_with_property(year, self.year, dates):
            dates.insert(0, dates.pop(index))


@dataclass(slots=True)
class YearToBot(Operation):
    year: str

    def apply(self, dates: list[str]) -> None:
        for index in indices_with_property(year, self.year, dates):
            dates.append(dates.pop(index))


def parse_operation(operation: str) -> Operation:
    if operation.startswith('UP-'):
        return MoveMonthUp(operation[3:5])
    elif operation.startswith('DOWN-'):
        return MoveDayDown(operation[5:7])
    elif operation.startswith('TOP-'):
        return YearToTop(operation[4:8])
    elif operation.startswith('BOT-'):
        return YearToBot(operation[4:8])
    elif operation == 'ASC':
        return SortAsc()
    else:  # operation == 'DSC'
        return SortDsc()


def sort_dates(dates: list[str], operations: list[str]) -> list[str]:
    for operation in operations:
        parse_operation(operation).apply(dates)

    return dates
