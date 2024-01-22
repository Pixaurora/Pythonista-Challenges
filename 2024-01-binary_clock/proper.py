skipped_2s_place_entries: dict[int, list[int]] = {
    0: [8, 4],
    3: [8],
    6: [8],
}


def binarify(time: str) -> str:
    clock_lines: list[str] = [''] * 4

    for char_id, char in enumerate(time):
        try:
            digit: int = int(char)
        except ValueError:  # Next character was :
            for index in range(4):
                clock_lines[index] += ' '

            continue

        skipped_2s_places: list[int] = skipped_2s_place_entries.get(char_id) or []

        for index in range(4):
            clock_lines[index] += ' ' if 2 ** index in skipped_2s_places else str(digit >> index & 1)

    return '\n'.join(clock_lines[::-1])
