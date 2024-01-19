from __future__ import annotations

from typing import Iterator, NamedTuple


class Vec(NamedTuple):
    x: int
    y: int

    def __add__(self, other: tuple[int, int]) -> Vec:
        return Vec(self[0] + other[0], self[1] + other[1])

    def __abs__(self) -> Vec:
        return Vec(abs(self[0]), abs(self[1]))

    def manhattan_dist(self, other: tuple[int, int]) -> int:
        return abs(self[0] - other[0]) + abs(self[1] - other[1])


def get_symbol_positions(symbol: str, original_map: str, map_start: int, chars_per_line: int) -> Iterator[Vec]:
    current_position: int = 0

    for _ in original_map:
        try:
            current_position = original_map.index(symbol, current_position + 1)
        except ValueError:  # Sub-string was not found past this point,
            break  # so quit searching

        pos_from_map_start: int = current_position - map_start
        yield Vec(pos_from_map_start % chars_per_line, pos_from_map_start // chars_per_line)
        # Modulo to get position within the line, divide to get total # of lines passed


def create_map(original_map: str) -> list[list[int]]:
    first_map_symbols: list[int] = []
    for row_character in ('S', 'T', '.'):
        try:
            first_map_symbols.append(original_map.index(row_character))
        except ValueError:
            pass

    map_start: int = min(first_map_symbols)
    # 0    .....S..T...
    #      ^ starting at this point in the line, after indentation

    size: Vec = Vec(original_map.find('\n', map_start) - map_start, original_map.count('\n', map_start) + 1)

    indentation: int = map_start - original_map.rfind('\n', 0, map_start)
    chars_per_line: int = indentation + size.x

    sensors: Iterator[Vec] = get_symbol_positions('S', original_map, map_start, chars_per_line)
    tags: list[Vec] = [*get_symbol_positions('T', original_map, map_start, chars_per_line)]

    deadzone_map: list[list[int]] = [[1] * size.x for _ in [None] * size.y]  # First assume all coordinates are deadzones
    for sensor in sensors:
        radius: int = min(map(sensor.manhattan_dist, tags))

        # use max/min to limit the range to be within the map bounds,
        for sensed_x in range(max(sensor.x - radius, 0), min(sensor.x + radius + 1, size.x)):
            column_height: int = radius - abs(sensed_x - sensor.x)

            for sensed_y in range(max(sensor.y - column_height, 0), min(sensor.y + column_height + 1, size.y)):
                deadzone_map[sensed_y][sensed_x] = 0

    return deadzone_map
