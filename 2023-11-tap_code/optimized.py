import re


# This is a stripped down version of my "proper" implementation, with almost no extra function calls unless absolutely necessary
# Because of these changes, it runs over twice as fast! This shows that function calls are very expensive in Python


TWO_TAPS: re.Pattern = re.compile(r'(\.+) (\.+) ?', flags=re.RegexFlag.UNICODE)


def convert(input_text: str) -> str:
    result: str = ''

    if input_text[0] == '.':
        for tap_section in TWO_TAPS.finditer(input_text):
            tap_cell_id: int = len(tap_section[1]) * 5 + len(tap_section[2])  # This number is 6 higher than it should be
            result += chr(91 + tap_cell_id + (tap_cell_id > 15))  # so these numbers are offset 6 from the proper version

        return result
    else:
        for letter in input_text:
            tap_cell_id: int = ord(letter) % 32 - 1  # So A is 0, B is 1, etc...

            if tap_cell_id == 10:
                tap_cell_id = 2  # K is skipped to have same ID as C
            elif tap_cell_id > 10:
                tap_cell_id -= 1  # Since K is skipped, the other cell IDs get pushed back one

            result = f'{result} {"." * (1 + tap_cell_id // 5)} {"." * (1 + tap_cell_id % 5)}'

        return result[1:]
