from __future__ import annotations

from typing import Generic, NamedTuple, Self, TypeVar


SPEED_OF_SOUND: float = 0.343

SoundImpactData = tuple[int, int, float]

N = TypeVar('N', int, float)


class Vec(NamedTuple, Generic[N]):
    x: N
    y: N

    def __round__(self) -> Vec[int]:
        return Vec(round(self.x), round(self.y))

    def dot_product(self, other: tuple[N, N]) -> N:
        return self.x * other[0] + self.y * other[1]


class Circle(NamedTuple):
    """
    A line, graphed by an equation of the form `(x + pos.x)**2 + (y + pos.y)**2 - radius**2`
    """

    pos: Vec[float]
    radius: float

    def intersection_line(self, other: Circle) -> Line:
        """
        Returns the equation of the line which intersects both circles at the point they intersect with each other.

        See the attached image file `finding_intersection_line.png` in this directory for my proof of this line identity.
        """

        return Line(
            Vec(2 * (self.pos.x - other.pos.x), 2 * (self.pos.y - other.pos.y)),
            (self.radius**2 - self.pos.x**2 - self.pos.y**2) - (other.radius**2 - other.pos.x**2 - other.pos.y**2),
        )


Matrix2x2 = tuple[tuple[float, float], tuple[float, float]]


class Line(NamedTuple):
    """
    A line, graphed by an equation of the form `coefficient.x * x + coefficient.y * y = offset`
    """

    coefficient: Vec[float]
    offset: float

    def solve_system(self, other: Line) -> Vec[float]:
        """
        Solves the system of equations by using matrix/vector operations.

        I re-learned how to do this using a video from Khan Academy, you can use it if you want to understand this method better.
        https://www.youtube.com/watch?v=AUqeb9Z3y3k
        """

        coeff_matrix: Matrix2x2 = (self.coefficient, other.coefficient)

        offsets: Vec[float] = Vec[float](self.offset, other.offset)

        # First, the state of the equation is `coeff_matrix * Vec(x, y) = offsets`,
        # and we want to solve for Vec(x, y)

        # To do this, we would multiply both sides by the coeff_matrix's inverse,
        # which would single out Vec(x, y) and leave the answer Vec(x, y) = [something]

        # Step 1: Find the inverse of coeff_matrix.

        matrix_determinant: float = coeff_matrix[0][1] * coeff_matrix[1][0] - coeff_matrix[0][0] * coeff_matrix[1][1]
        matrix_determinant_i: float = 1 / matrix_determinant

        coeff_matrix_i: Matrix2x2 = (
            (coeff_matrix[1][1] * matrix_determinant_i, -coeff_matrix[0][1] * matrix_determinant_i),
            (-coeff_matrix[1][0] * matrix_determinant_i, coeff_matrix[0][0] * matrix_determinant_i),
        )

        # At this point, our equation is looking more like: `coeff_matrix_i * coeff_matrix * Vec(x, y) = coeff_matrix_i * offsets`
        # Since a square matrix multiplied by its inverse is the identity matrix, and multiplying by the identity matrix gives you
        # the original matrix/vector, the equation may be simplified to `Vec(x, y) = coeff_matrix_i * offsets`

        # This leads us on to
        # Step 2: Multiply coeff_matrix_i by offsets, to find the desired answer.

        return Vec[float](offsets.dot_product(coeff_matrix_i[0]), offsets.dot_product(coeff_matrix_i[1]))


def find(sound_1: SoundImpactData, sound_2: SoundImpactData, sound_3: SoundImpactData) -> tuple[int, int]:
    circle_1, circle_2, circle_3 = (Circle(Vec(s[0], s[1]), s[2] * SPEED_OF_SOUND) for s in (sound_1, sound_2, sound_3))

    # If all 3 circles overlap on one point, this can be found by finding where two of the intersection lines intersect each other.
    # Therefore, we find 2 intersection lines and then solve for the system of the 2 equations.

    intersecting_line_1: Line = circle_1.intersection_line(circle_2)
    intersecting_line_2: Line = circle_2.intersection_line(circle_3)

    return round(intersecting_line_1.solve_system(intersecting_line_2))
