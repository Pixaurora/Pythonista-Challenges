from __future__ import annotations

import asyncio
import math
import time
from enum import Enum, IntEnum
from typing import Generic, TypeVar

import event_types


SIZE: int = 16
TILE_COUNT: int = SIZE**2

TILES_MOVED_PER_SECOND: float = 2
SECONDS_PER_TILE: float = 1 / TILES_MOVED_PER_SECOND

BRIGHT_RED_TEXT_CODE: str = '196'
CYAN_TEXT_CODE: str = '36'

DEGREES_TO_RADIANS: float = math.pi / 180
RADIANS_TO_DEGREES: float = 180 / math.pi

# Positions: Placement in the map, keeping track of the mouse's placement and where to go, etc.

T = TypeVar("T")
D = TypeVar("D", bound=int | float)


class Vec(Generic[D]):
    __slots__ = ('x', 'y')

    x: D
    y: D

    def __init__(self, x: D, y: D) -> None:
        self.x = x
        self.y = y

    def __str__(self) -> str:
        return f'({self.x}, {self.y})'

    def __add__(self, other: Vec[D] | tuple[D, D]) -> Vec[D]:
        if isinstance(other, tuple):
            return Vec[D](self.x + other[0], self.y + other[1])
        else:
            return Vec[D](self.x + other.x, self.y + other.y)

    def __sub__(self, other: Vec[D] | tuple[D, D]) -> Vec[D]:
        if isinstance(other, tuple):
            return Vec[D](self.x - other[0], self.y - other[1])
        else:
            return Vec[D](self.x - other.x, self.y - other.y)

    def __mul__(self, other: D) -> Vec[D]:
        return Vec[D](self.x * other, self.y * other)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, type(self)) and other.x == self.x and other.y == self.y

    def __repr__(self) -> str:
        return self.__str__()

    def __round__(self) -> Vec[int]:
        return Vec[int](round(self.x), round(self.y))

    def __floor__(self) -> Vec[int]:
        return Vec[int](math.floor(self.x), math.floor(self.y))

    def distance_to(self, other: Vec[D]) -> float:
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

    @property
    def is_legal(self) -> bool:
        return 0 <= self.x < SIZE and 0 <= self.y < SIZE

    @classmethod
    def from_angle(cls, angle: float) -> Vec[float]:
        return Vec[float](math.sin(angle), math.cos(angle))


def in_list_grid(real_coordinate: Vec[D]) -> Vec[int]:
    return math.floor(real_coordinate) + (8, 8)


def in_map_grid(list_coordinate: Vec[D]) -> Vec[float]:
    return Vec[float](list_coordinate.x, list_coordinate.y) - (8, 8)


class Axis(IntEnum):
    X = 0
    Y = 1


class Direction(Enum):
    angle: float

    delta: Vec[float]
    int_delta: Vec[int]  # because I couldn't figure out how to properly type the
    # __add__ function for ints to work with floats but not the other way around

    intersecting_axis: Axis
    wall_offset: Vec[int]

    def __init__(self, angle: float, intersecting_axis: Axis, is_positive: bool) -> None:
        self.angle = angle * DEGREES_TO_RADIANS

        self.delta = Vec.from_angle(self.angle)
        self.int_delta = round(self.delta)

        self.intersecting_axis = intersecting_axis

        if is_positive:
            self.wall_offset = self.int_delta
        else:
            self.wall_offset = Vec[int](0, 0)

    LEFT = (270.0, Axis.Y, False)
    DOWN = (180.0, Axis.X, False)
    UP = (0.0, Axis.X, True)
    RIGHT = (90.0, Axis.Y, True)


angle_mapping = {direction.angle: direction for direction in Direction}


def get_direction(angle: float) -> Direction:
    return angle_mapping[angle % math.tau]


def organize_by_angles(angles: list[float], items: list[T]) -> dict[Direction, T]:
    ordered_items: dict[Direction, T] = {}

    for angle, item in zip(angles, items):
        ordered_items[get_direction(angle)] = item

    return ordered_items


# The Maze: keeping track of where walls are, implementing a-maze-ing search algorithms, etc.


class Maze:
    __slots__ = ('edges', 'distances', 'goal_tiles')

    # If the value is TRUE, it can be passed through, otherwise there is a wall (impassable)
    edges: tuple[list[list[bool]], list[list[bool]]]
    # It's important to note that the dimensions of the 2D lists differ:
    # X: 16x by 17y
    # Y: 17x by 16y

    distances: list[list[int]]

    goal_tiles: list[Vec[int]]

    def __init__(self, goal: Vec[float]) -> None:
        self.edges = (
            [[True for X in range(SIZE)] for Y in range(SIZE + 1)],
            [[True for X in range(SIZE + 1)] for Y in range(SIZE)],
        )
        self.distances = [[0 for X in range(SIZE)] for Y in range(SIZE)]

        self.update_goal(goal)

    def update_goal(self, goal: Vec[float]) -> None:
        self.goal_tiles = [in_list_grid(goal)]

        if goal.x % 1.0 == 0:
            self.goal_tiles.append(self.goal_tiles[0] - (1, 0))

        if goal.y % 1.0 == 0:
            self.goal_tiles += [pos - (0, 1) for pos in self.goal_tiles]

    def get_distance(self, tile: Vec[int]) -> int:
        return self.distances[tile.y][tile.x]

    def get_edge_passability(self, tile: Vec[int]) -> dict[Direction, bool]:
        return {
            Direction.LEFT: self.edges[Axis.Y][tile.y][tile.x],
            Direction.DOWN: self.edges[Axis.X][tile.y][tile.x],
            Direction.UP: self.edges[Axis.X][tile.y + 1][tile.x],
            Direction.RIGHT: self.edges[Axis.Y][tile.y][tile.x + 1],
        }

    def get_optimal_next_move(self, tile: Vec[int]) -> tuple[Direction, int]:
        aim_distance = self.get_distance(tile) - 1

        for direction, passable in self.get_edge_passability(tile).items():
            if passable and self.get_distance(tile + direction.int_delta) == aim_distance:
                return (direction, aim_distance)

        print('Failed to find a suitable direction to turn, will run into a wall!')

        return (Direction.LEFT, 255)

    def get_adjacent_tiles(self, tile: Vec[int], edges: dict[Direction, bool] | None = None) -> list[Vec[int] | None]:
        if edges is None:
            edges = self.get_edge_passability(tile)

        return [None if not edges[direction] else tile + direction.int_delta for direction in Direction]

    def update_distances(self) -> None:
        for goal_tile in self.goal_tiles:
            self.distances[goal_tile.y][goal_tile.x] = 0

        tiles_to_check: list[Vec[int]] = [*self.goal_tiles]

        for tile in tiles_to_check:
            next_distance: int = self.get_distance(tile) + 1
            edges: dict[Direction, bool] = self.get_edge_passability(tile)

            for direction in Direction:
                neighbor_tile: Vec[int] = tile + direction.int_delta

                if neighbor_tile.is_legal and edges[direction]:
                    if self.get_distance(neighbor_tile) > next_distance or neighbor_tile not in tiles_to_check:
                        self.distances[neighbor_tile.y][neighbor_tile.x] = next_distance
                        tiles_to_check.append(neighbor_tile)


# Maze Debugging: Printing the maze to the screen, to get an idea of what our little mouse sees.

# Besides checking up on the algorithm to see if it's working correctly,
# the other motivation for me to write this bit of code was to help myself wrap my head around the data


def y_wall(passable: bool) -> str:
    return ' ' if passable else '|'


def x_wall(passable: bool) -> str:
    return '  ' if passable else '--'


def distance_ascii(distance: int) -> str:
    if distance < 99:
        return f'{distance:2}'
    else:
        representation: str = hex(distance)[2:] if distance < TILE_COUNT else 'NA'
        return f'\033[38;5;{BRIGHT_RED_TEXT_CODE}m{representation}\033[0;0m'


def pretty(maze: Maze, mouse_pos: Vec[int]) -> str:
    ascii_art: str = ''

    for y in range(SIZE)[::-1]:
        ascii_art += f'  {"   ".join(map(x_wall, maze.edges[Axis.X][y + 1]))}\n'

        for x in range(SIZE):
            wall: str = y_wall(maze.edges[Axis.Y][y][x])
            appearance: str = distance_ascii(maze.distances[y][x])

            if mouse_pos == Vec[int](x, y):
                appearance = f'\033[1;36m{appearance}\033[0;0m'

            ascii_art += f'{wall} {appearance} '

        ascii_art += f'{y_wall(maze.edges[Axis.Y][y][SIZE])}\n'

    ascii_art += f'  {"   ".join(map(x_wall, maze.edges[Axis.X][0]))}'

    return ascii_art


# Micro Mouse: This is where the central logic exists, ie what the mouse should do and when.


class MouseTracker:
    __slots__ = ('start_time', 'start_pos', 'goal_pos', 'current_pos', 'angle', 'mouse')

    start_time: float
    start_pos: Vec[float]
    goal_pos: Vec[float]

    current_pos: Vec[float]
    angle: float

    mouse: event_types.MicroMouse

    def __init__(self, micromouse: MicroMouse, starting_data: event_types.PositionResetData, start_time: float) -> None:
        self.start_time = start_time
        self.start_pos = Vec[float](*starting_data.position)
        self.goal_pos = Vec[float](*starting_data.target_position)

        self.mouse = micromouse

        self.current_pos = self.start_pos
        self.angle = starting_data.rotation * DEGREES_TO_RADIANS

    def __str__(self) -> str:
        return f'My position: {self.current_pos} @ {self.angle}° -> goal: {self.goal_pos}'

    async def turn(self, direction: Direction) -> None:
        turn_angle: float = direction.angle - self.angle

        await self.mouse.rotate(turn_angle * RADIANS_TO_DEGREES)
        self.angle = direction.angle

    def add_distance_for(self, time_length: float) -> None:
        distance: float = time_length * TILES_MOVED_PER_SECOND
        distance_vector: Vec[float] = Vec.from_angle(self.angle) * distance

        self.current_pos += distance_vector

    async def move_forward_until(self, time_length: float) -> None:
        await asyncio.sleep(time_length)
        self.add_distance_for(time_length)

    async def get_wall_positions(self) -> dict[Direction, Vec[float]]:
        distances: event_types.DistancesData = await self.mouse.get_distances()

        angles: list[float] = [self.angle - direction.angle for direction in Direction]
        wall_positions = [
            self.current_pos + Vec.from_angle(angle) * distance
            for angle, distance in zip(angles, (distances.right, distances.back, distances.forward, distances.left))
        ]

        return organize_by_angles(angles, wall_positions)

    async def update_walls(self, maze: Maze) -> None:
        walls: dict[Direction, Vec[float]] = await self.get_wall_positions()

        for direction, wall_pos in walls.items():
            wall_coordinate: Vec[int] = in_list_grid(wall_pos - direction.delta * 0.1) + direction.wall_offset

            maze.edges[direction.intersecting_axis][wall_coordinate.y][wall_coordinate.x] = False

    async def get_wall_tiles(self) -> dict[Direction, Vec[int]]:
        distances: event_types.DistancesData = await self.mouse.get_distances()

        angles = [self.angle - modifier.angle for modifier in Direction]
        literal_wall_positions = [
            self.current_pos + Vec.from_angle(angle) * distance
            for angle, distance in zip(angles, (distances.right, distances.back, distances.forward, distances.left))
        ]

        wall_coordinates: dict[Direction, Vec[float]] = organize_by_angles(angles, literal_wall_positions)

        return {direction: in_list_grid(wall_pos) for direction, wall_pos in wall_coordinates.items()}


class MicroMouse(event_types.MicroMouse):
    start_data: event_types.PositionResetData | None

    exploring_task: asyncio.Task[Maze] | None
    maze: Maze | None

    def __init__(self) -> None:
        self.start_data = None

        self.exploring_task = None
        self.maze = None

    async def position_reset(self, data: event_types.PositionResetData) -> None:
        self.start_data = data

    async def explore_maze(self, time_remaining: float, start_data: event_types.PositionResetData) -> Maze:
        mouse: MouseTracker = MouseTracker(self, start_data, time.time())

        maze: Maze | None = self.maze

        if maze is None:
            maze = Maze(mouse.goal_pos)
        else:
            maze.update_goal(mouse.goal_pos)

        # We take a snapshot of the walls at 80% of the way of being to the next tile,
        # as we will be able to see if we will run into walls from making a decision,
        # but we are not too late to make that decision
        partially_next_tile_time: float = SECONDS_PER_TILE * 0.8
        rest_time: float = SECONDS_PER_TILE - partially_next_tile_time

        explorable_tile_count: int = math.floor(time_remaining * TILES_MOVED_PER_SECOND)

        await mouse.update_walls(maze)

        try:
            next_direction: Direction
            distance: int = 1  # Set it to anything that isn't 0 so it doesn't exit on the first iteration

            for _ in range(explorable_tile_count):
                if distance == 0:
                    print('Got to my aimed goal, stopping algo.')

                    break

                await mouse.move_forward_until(partially_next_tile_time)

                grid_pos: Vec[int] = in_list_grid(mouse.current_pos)

                await mouse.update_walls(maze)
                maze.update_distances()
                next_direction, distance = maze.get_optimal_next_move(grid_pos)

                print(f'{pretty(maze, grid_pos)}\n{mouse}')

                mouse.add_distance_for(rest_time)
                time_to_wait: float = SECONDS_PER_TILE - (time.time() - mouse.start_time) % SECONDS_PER_TILE
                await asyncio.sleep(time_to_wait)

                await mouse.turn(next_direction)

        except asyncio.CancelledError:
            ...  # Don't need to do anything, return the maze as-is

        return maze

    async def start(self, time_remaining: float) -> None:
        if self.start_data is None:
            raise ValueError('Start data is not stored yet')

        self.exploring_task = asyncio.create_task(self.explore_maze(time_remaining, self.start_data))

        self.maze = await self.exploring_task

    async def end(self, complete: bool) -> None:
        if self.exploring_task is None:
            return

        self.exploring_task.cancel()


print('CODE RELOADED')
