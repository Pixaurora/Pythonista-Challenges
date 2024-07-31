# I didn't use any extra functions or constants for this, which would've been good practice, but can only slow me down!
def decipher(codes: list[str]) -> str:
    processed_codes: list[tuple[int, bool]] = []

    for code in codes:
        if code in '0123456789 9876543210':
            # code is fully consecutive, break
            processed_codes.append((0, True))
        elif code in '0000 1111 2222 3333 4444 5555 6666 7777 8888 9999':
            # code is all 1 digit, also a break
            processed_codes.append((ord(code[0]) - 48, True))  # using ord/chr with an offset of 48 ('0' is 48 in ASCII) is an easy optimization

        elif code[0:3] in '0123456789 9876543210':
            # first 3 digits are consecutive, 4th isn't. add 4th digit
            processed_codes.append((ord(code[3]) - 48, False))
        elif code[0:2] in '0123456789 9876543210':
            # first 2 digits are consecutive, 3rd isn't. add 3rd digit
            processed_codes.append((ord(code[2]) - 48, False))

        else:
            # No digits at the start are consecutive, which is a break
            processed_codes.append((max(ord(digit) - 48 for digit in code), True))

    code: str = ''
    total: int = 0

    while len(code) != 4:
        for amount_added, is_break in processed_codes:
            total += amount_added

            if is_break:
                code += chr(total % 10 + 48)
                total = 0

                if len(code) == 4:
                    break

    return code
