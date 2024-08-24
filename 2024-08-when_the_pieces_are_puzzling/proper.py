from __future__ import annotations

import re
from enum import StrEnum
from typing import NamedTuple


letter_to_piece_side: dict[str, SideDirection] = {}

edge_regex: str = r'-?\d'
piece_regex: str = r'@(\w(?:-?\d)+)@(\w(?:-?\d)+)@(\w(?:-?\d)+)@(\w(?:-?\d)+)'


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
        return letter_to_piece_side[letter]


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
    edges: list[Side]

    @classmethod
    def from_str(cls, representation: str) -> Piece | None:
        regex_match = re.match(piece_regex, representation)

        if regex_match is None:
            return

        sides: list[Side] = []

        for i in range(4):
            side = regex_match.group(i + 1)
            side = Side.from_str(side)

            if side is None:
                return

            sides.append(side)

        return cls(representation, sides)

    def __str__(self) -> str:
        return self.representation


def sort(pieces: list[str]) -> list[str]:
    parsed_pieces: list[Piece] = [piece for piece in map(Piece.from_str, pieces) if piece is not None]

    return [str(piece) for piece in parsed_pieces]
