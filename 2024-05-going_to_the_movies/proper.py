from dataclasses import dataclass
from typing import Iterator, NamedTuple, Self


class TaxicabVec(NamedTuple):
    x: int
    y: int

    def midpoint(self, other: Self) -> Self:
        return type(self)((self.x + other.x) // 2, (self.y + other.y) // 2)

    def dist(self, other: Self) -> int:
        return abs(self.x - other.x) + abs(self.y - other.y)


@dataclass(slots=True)
class MovieTheatre:
    seats: list[list[int]]

    @property
    def size(self) -> TaxicabVec:
        row_count: int = len(self.seats)
        seats_per_row: int = len(self.seats[0]) if row_count != 0 else 0

        return TaxicabVec(seats_per_row, row_count)

    @property
    def center(self) -> TaxicabVec:
        return self.size.midpoint(TaxicabVec(0, 0))

    def valid_positions(self, group_size: int) -> Iterator[TaxicabVec]:
        for y, row in enumerate(self.seats):
            untaken_seats: int = 0

            for x, seat_taken in enumerate(row):
                if seat_taken:
                    untaken_seats = 0
                else:
                    untaken_seats += 1

                if untaken_seats >= group_size:
                    yield TaxicabVec(x - round(untaken_seats / 2), y)


def find_seats(seats: list[list[int]], n: int) -> int:
    theatre: MovieTheatre = MovieTheatre(seats)

    return len(list(theatre.valid_positions(n)))


def optimal_seats(seats: list[list[int]], n: int) -> tuple[int, int]:
    theatre: MovieTheatre = MovieTheatre(seats)

    return min(theatre.valid_positions(n), key=theatre.center.dist)
