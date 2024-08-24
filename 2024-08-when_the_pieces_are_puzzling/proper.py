from __future__ import annotations

import re
from enum import StrEnum
from re import Match
from typing import NamedTuple


letter_to_piece_side: dict[str, SideDirection] = {}

edge_regex: str = r'-?\d'
piece_regex: str = fr'@(\w(?:{edge_regex})+)' * 4


class SideDirection(StrEnum):
    TOP = 'T'
    BOTTOM = 'B'
    LEFT = 'L'
    RIGHT = 'R'

    letter: str

    def __init__(self, letter: str):
        self.letter = letter

        letter_to_piece_side[self.letter] = self

    @classmethod
    def from_str(cls, letter: str) -> SideDirection | None:
        return letter_to_piece_side.get(letter)


class Side(NamedTuple):
    edges: list[int]
    direction: SideDirection

    @classmethod
    def from_str(cls, representation: str) -> Side | None:
        direction: SideDirection | None = SideDirection.from_str(representation[0])

        if direction is None:
            return

        edges: list[int] = []
        for edge in re.findall(edge_regex, representation):
            edges.append(int(edge))

        return Side(edges, direction)

    def __len__(self):
        return len(self.edges)


class Piece(NamedTuple):
    representation: str
    sides: dict[SideDirection, Side]

    @classmethod
    def from_str(cls, representation: str) -> Piece | None:
        piece: Match | None = re.match(piece_regex, representation)

        if piece is None:
            return

        sides: dict[SideDirection, Side] = {}

        for i in range(4):
            side = piece.group(i + 1)
            side = Side.from_str(side)

            if side is None or sides.get(side.direction) is not None:
                return

            sides[side.direction] = side

        if len(sides) != 4:
            return

        return cls(representation, sides)

    def __len__(self):
        return len(self.sides[SideDirection.LEFT])

    @property
    def is_valid(self) -> bool:
        return self.all_sides_same_length and not self.has_internal_collisions

    @property
    def all_sides_same_length(self) -> bool:
        return len({len(side) for side in self.sides.values()}) == 1

    @property
    def has_internal_collisions(self) -> bool:
        # TODO: Somehow find collisions
        return False

    def __str__(self) -> str:
        return self.representation


def sort(pieces: list[str]) -> list[str]:
    parsed_pieces: list[Piece] = [piece for piece in map(Piece.from_str, pieces) if piece is not None and piece.is_valid]

    pieces_by_len: dict[int, list[Piece]] = {}
    for piece in parsed_pieces:
        length: int = len(piece)

        pieces_by_len[length] = pieces_by_len.get(length) or []

        pieces_by_len[length].append(piece)

    common_length_pieces = max(pieces_by_len.values(), key=len)
    return [str(piece) for piece in common_length_pieces]
