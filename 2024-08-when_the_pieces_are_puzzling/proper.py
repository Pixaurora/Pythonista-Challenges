from __future__ import annotations

from enum import StrEnum
from typing import NamedTuple


letter_to_piece_side: dict[str, SideDirection] = {}


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


def side_from_str(representation: str) -> tuple[list[int], SideDirection] | None:
    direction: SideDirection | None = SideDirection.from_str(representation[0])

    if direction is None:
        return

    edges: list[int] = []

    index: int = 1
    sign: int = +1
    while index < len(representation):
        try:
            converted: str = representation[index]

            if converted == '-':
                sign = -1
            else:
                next: int = sign * int(converted)

                sign = +1
                edges.append(next)
        except ValueError | IndexError:
            # Side isn't valid because - is the last char, or can't be parsed as an int
            return

        index += 1

    return (edges, direction)


class Piece(NamedTuple):
    representation: str
    sides: dict[SideDirection, list[int]]
    size: int

    @classmethod
    def from_str(cls, representation: str) -> Piece | None:
        piece: list[str] = representation.split('@')

        if len(piece) != 5:  # First split is simply '' as the string starts with @
            return

        sides: dict[SideDirection, list[int]] = {}
        size: int | None = None

        for i in range(4):
            side = piece[i + 1]
            side = side_from_str(side)

            if side is None:
                return

            edges, direction = side

            if size is None:
                size = len(edges)
            elif size != len(edges) or sides.get(direction) is not None:
                return

            sides[direction] = edges

        if size is None or len(sides) != 4:
            return

        return cls(representation, sides, size)

    def __len__(self):
        return self.size

    def is_self_colliding(self) -> bool:
        size: int = len(self)

        for main, opposite in ((SideDirection.TOP, SideDirection.BOTTOM), (SideDirection.LEFT, SideDirection.RIGHT)):
            for main_edge, opposite_edge in zip(self.sides[main], self.sides[opposite]):
                if size + opposite_edge + main_edge <= 0:
                    return True

        return False

    def __str__(self) -> str:
        return self.representation


def sort(pieces: list[str]) -> list[str]:
    parsed_pieces: list[Piece] = [piece for piece in map(Piece.from_str, pieces) if piece is not None and not piece.is_self_colliding()]

    pieces_by_len: dict[int, list[Piece]] = {}
    for piece in parsed_pieces:
        length: int = len(piece)

        pieces_by_len[length] = pieces_by_len.get(length) or []

        pieces_by_len[length].append(piece)

    common_length_pieces = max(pieces_by_len.values(), key=len)
    return [str(piece) for piece in common_length_pieces]
