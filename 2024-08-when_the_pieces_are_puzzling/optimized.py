def piece_from_str(representation: str) -> tuple[str, list[list[int]], int] | None:
    piece: list[str] = representation.split('@')

    if len(piece) != 5:  # First split is simply '' as the string starts with @
        return

    sides: list[list[int]] = [None, None, None, None]  # type: ignore
    size: int = None  # type: ignore

    for i in range(4):
        side_representation = piece[i + 1]

        try:
            direction: int = 'LBTR'.index(side_representation[0])
        except ValueError:
            return

        edges: list[int] = []

        index: int = 1
        sign: int = +1
        while index < len(side_representation):
            converted: str = side_representation[index]

            if converted == '-':
                if sign == -1:
                    return

                sign = -1
                index += 1

                continue

            next: int = ord(converted) - 48
            if not 0 <= next < 10:
                return

            edges.append(sign * next)
            sign = +1

            index += 1

        if size is None or len(edges) == 0:
            size = len(edges)
        elif size != len(edges) or sides[direction] is not None:
            return

        sides[direction] = edges

    if len(sides) != 4:
        return

    return (representation, sides, size)


def is_self_colliding(sides: list[list[int]], size: int) -> bool:
    for main, opposite in ((1, 2), (0, 3)):
        for main_edge, opposite_edge in zip(sides[main], sides[opposite]):
            if size + opposite_edge + main_edge <= 0:
                return True

    return False


def sort(pieces: list[str]) -> list[str]:
    parsed_pieces: list[tuple[str, list[list[int]], int]] = [
        piece for piece in map(piece_from_str, pieces) if piece is not None and not is_self_colliding(piece[1], piece[2])
    ]

    pieces_by_len: dict[int, list[str]] = {}
    for representation, _, size in parsed_pieces:
        pieces_by_len[size] = pieces_by_len.get(size) or []

        pieces_by_len[size].append(representation)

    return max(pieces_by_len.values(), key=len)
