import math
from dataclasses import dataclass
from typing import NamedTuple


class Vec(NamedTuple):
    x: int
    y: int


@dataclass(slots=True)
class MovieTheatre:
    seats: list[list[int]]

    def __init__(self, seats: list[list[int]]) -> None:
        self.seats = seats

    def valid_positions(self, number_of_friends: int) -> list[Vec]:
        valid_pos: list[Vec] = []

        for y, row in enumerate(self.seats):
            untaken_seats: int = 0

            for x, seat_open in enumerate(row):
                if not seat_open:
                    untaken_seats += 1

                    if untaken_seats >= number_of_friends:
                        seat_group_pos: Vec = Vec(x - math.ceil(untaken_seats / 2), y)
                        valid_pos.append(seat_group_pos)
                else:
                    untaken_seats = 0

        return valid_pos


def find_seats(seats: list[list[int]], n: int) -> int:
    theatre: MovieTheatre = MovieTheatre(seats)

    return len(theatre.valid_positions(n))


def optimal_seats(seats: list[list[int]], n: int) -> int:
    ...
