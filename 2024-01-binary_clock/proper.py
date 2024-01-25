skipped_twos_places_per_column: dict[int, list[int]] = {
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

        skipped_twos_places: list[int] = skipped_twos_places_per_column.get(char_id) or []

        for index in range(4):
            clock_lines[index] += ' ' if 2 ** index in skipped_twos_places else str(digit >> index & 1)

    return '\n'.join(clock_lines[::-1])


def clockify(binary_time: str):
    time_digits: list[int] = [0, 0, -1, 0, 0, -1, 0, 0]  # -1 is where : goes

    for twos_place, line in enumerate(binary_time.splitlines()[::-1]):
        for column, char in enumerate(line):
            try:
                binary_digit: int = int(char)
            except ValueError:  # Space present
                continue

            time_digits[column] += binary_digit << twos_place

    return ''.join(str(digit) if digit != -1 else ':' for digit in time_digits)
