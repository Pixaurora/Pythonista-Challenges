import re
from typing import Self

from .optimized import TWO_TAPS


TAP: str = '.'


def tap_plus_one(cell_index: int):  # Because the 1st is index 0, but has 1 tap
    return TAP * (1 + cell_index)


class TapCell:
    row: int
    column: int

    def __init__(self, row: int, column: int):
        self.row = row
        self.column = column

    @classmethod
    def from_letter(cls, letter: str) -> Self:
        tap_cell_id: int = ord(letter) % 32 - 1  # So A is 0, B is 1, etc...

        if tap_cell_id == 10:
            tap_cell_id = 2  # K is skipped to have same ID as C
        elif tap_cell_id > 10:
            tap_cell_id -= 1  # Since K is skipped, the other cell IDs get pushed back one

        return cls(tap_cell_id // 5, tap_cell_id % 5)

    @classmethod
    def from_tap_section(cls, first_taps: str, second_taps: str) -> Self:
        return cls(len(first_taps) - 1, len(second_taps) - 1)  # Subtract 1 because 1 tap is at 0

    @property
    def letter_id(self) -> int:
        return 5 * self.row + self.column + (self.row >= 2)  # K is skipped, which would be row 2 column 1 otherwise

    def to_letter(self) -> str:
        return chr(97 + self.letter_id)

    def to_taps(self) -> str:
        return f'{tap_plus_one(self.row)} {tap_plus_one(self.column)}'


def word_to_taps(word: str) -> str:
    taps: str = ''

    for letter in word:
        taps += ' ' + TapCell.from_letter(letter).to_taps()

    return taps[1:]


def tap_section_to_char(tap_section: re.Match[str]) -> str:
    return TapCell.from_tap_section(tap_section[1], tap_section[2]).to_letter()


def taps_to_word(taps: str) -> str:
    return TWO_TAPS.sub(tap_section_to_char, taps)


def convert(text: str) -> str:
    if text.startswith('.'):
        return taps_to_word(text)
    else:
        return word_to_taps(text)
