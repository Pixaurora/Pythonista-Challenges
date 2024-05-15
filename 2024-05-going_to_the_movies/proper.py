from dataclasses import dataclass
from typing import Generator, NamedTuple, Self


class Vec(NamedTuple):
    x: int
    y: int

    def midpoint(self, other: Self) -> Self:
        return self.__class__((self.x + other.x) // 2, (self.y + other.y) // 2)

    def dist(self, other: Self) -> int:
        return abs(self.x - other.x) + abs(self.y - other.y)

@dataclass(slots=True)
class MovieTheatre:
    seats: list[list[int]]

    def __init__(self, seats: list[list[int]]) -> None:
        self.seats = seats

    @property
    def size(self) -> Vec:
        return Vec(len(self.seats[0]), len(self.seats))

    @property
    def center(self) -> Vec:
        return self.size.midpoint(Vec(0, 0))

    def valid_positions(self, number_of_friends: int) -> Generator[Vec, None, None]:
        for y, row in enumerate(self.seats):
            untaken_seats: int = 0

            for x, seat_taken in enumerate(row):
                if not seat_taken:
                    untaken_seats += 1

                    if untaken_seats >= number_of_friends:
                        yield Vec(x - round(untaken_seats / 2), y)
                else:
                    untaken_seats = 0

def find_seats(seats: list[list[int]], n: int) -> int:
    theatre: MovieTheatre = MovieTheatre(seats)

    return len(list(theatre.valid_positions(n)))


def optimal_seats(seats: list[list[int]], n: int) -> tuple[int, int]:
    theatre: MovieTheatre = MovieTheatre(seats)

    return min(theatre.valid_positions(n), key=theatre.center.dist)
