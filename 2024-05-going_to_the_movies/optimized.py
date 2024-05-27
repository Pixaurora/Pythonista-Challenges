from typing import Iterator


TaxicabVec = tuple[int, int]
TheatreSeats = list[list[int]]


def midpoint(vec_1: TaxicabVec, vec_2: TaxicabVec) -> TaxicabVec:
    return ((vec_1[0] + vec_2[0]) // 2, (vec_1[1] + vec_2[1]) // 2)


def dist(vec_1: TaxicabVec, vec_2: TaxicabVec) -> int:
    return abs(vec_1[0] - vec_2[0]) + abs(vec_1[1] - vec_2[1])


def size(seats: TheatreSeats) -> TaxicabVec:
    return (len(seats[0]), len(seats))


def center(seats: TheatreSeats) -> TaxicabVec:
    return midpoint(size(seats), (0, 0))


def valid_positions(seats: TheatreSeats, group_size: int) -> Iterator[TaxicabVec]:
    for y, row in enumerate(seats):
        untaken_seats: int = 0

        for x, seat_taken in enumerate(row):
            if seat_taken:
                untaken_seats = 0
            else:
                untaken_seats += 1

            if untaken_seats >= group_size:
                yield (x - round(untaken_seats / 2), y)


def find_seats(seats: TheatreSeats, n: int) -> int:
    seat_count: int = 0

    for _ in valid_positions(seats, n):
        seat_count += 1

    return seat_count


def optimal_seats(seats: TheatreSeats, n: int) -> TaxicabVec | None:
    theatre_center: TaxicabVec = center(seats)

    lowest_vec: TaxicabVec | None = None
    lowest_dist: int = 0

    for seat_pos in valid_positions(seats, n):
        dist_to_center: int = dist(seat_pos, theatre_center)

        if lowest_vec is None or lowest_dist > dist_to_center:
            if dist_to_center == 0:
                return seat_pos

            lowest_vec = seat_pos
            lowest_dist = dist_to_center

    return lowest_vec
