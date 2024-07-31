def binarify(time: str):
    return '\n'.join(
        map(
            ''.join,
            zip(
                *[
                    (
                        [
                            (
                                ' '
                                if char_num in (3, 6) and twos_place == 3 or char_num == 0 and twos_place in (2, 3)
                                else str(int(char) >> twos_place & 1)
                            )
                            for twos_place in range(4)[::-1]
                        ]
                        if char.isnumeric()
                        else [' '] * 4
                    )
                    for char_num, char in enumerate(time)
                ]
            ),
        )
    )


def clockify(binary_time: str):
    return ''.join(
        str(sum(bit_column)) if char_num % 3 != 2 else ':'
        for char_num, bit_column in enumerate(
            zip(*[[1 << twos_place if char == '1' else 0 for char in line] for twos_place, line in enumerate(binary_time.splitlines()[::-1])])
        )
    )
