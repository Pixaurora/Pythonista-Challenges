from typing import NamedTuple

SPEED_OF_SOUND: float = 0.343

SoundImpactData = tuple[int, int, float]

class Circle(NamedTuple):
    x: int
    y: int
    radius: float

def find(s1: SoundImpactData, s2: SoundImpactData, s3: SoundImpactData) -> tuple[int, int]:
    c1, c2, c3 = (Circle(s[0], s[1], s[0] * SPEED_OF_SOUND) for s in (s1, s2, s3))

    return (0, 0)
