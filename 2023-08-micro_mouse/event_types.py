from typing import Awaitable, Callable, Literal, Self

import msgspec


class BaseEvent(msgspec.Struct):
    op: Literal["hello", "distances", "rot", "position_reset", "start", "end", "reload"]


class HelloEvent(BaseEvent):
    op: Literal["hello"]


class DistancesData(msgspec.Struct):
    left: float
    right: float
    forward: float
    back: float
    rotation: float


class DistancesEvent(BaseEvent):
    op: Literal["distances"]
    nonce: str
    d: DistancesData


class RotationEvent(BaseEvent):
    op: Literal["rot"]
    nonce: str
    current: float
    error: None | str


class PositionResetData(msgspec.Struct):
    run_number: int
    runs_remaining: int
    position: tuple[float, float]  # x, y
    rotation: float
    target_position: tuple[float, float]  # x, y


class PositionResetEvent(BaseEvent):
    op: Literal["position_reset"]
    d: PositionResetData


class StartData(msgspec.Struct):
    time_remaining: float


class StartEvent(BaseEvent):
    op: Literal["start"]
    d: StartData


class EndEvent(BaseEvent):
    op: Literal["end"]
    complete: bool


class ReloadEvent(BaseEvent):
    op: Literal["reload"]


class DistancesRequest(msgspec.Struct):
    nonce: str
    op: str = "distances"


class RotationRequest(msgspec.Struct):
    nonce: str
    rot: float
    op: str = "rot"


class MicroMouse:
    __gd__: Callable[[], Awaitable[DistancesData]]
    __r__: Callable[[float], Awaitable[tuple[str | None, float]]]

    async def rotate(self, angle: float) -> float:
        """
        Rotates the mouse by angle degrees. 90º -> right turn.

        :param angle: How many degrees to rotate by
        :type angle: float

        :return: the current angle of the mouse, after rotating
        :return type: float

        :raises ValueError: Something went wrong. Check the error.
        """
        error, angle = await self.__r__(angle)

        if error:
            raise ValueError(error)

        return angle

    async def get_distances(self) -> DistancesData:
        """
        Gets the distance from each direction of the mouse, plus the current rotation of the mouse.

        :return: The data about the mouse distance / rotation
        :return type: event_data.DistancesData
        """

        return await self.__gd__()

    @classmethod
    def _prepare(cls, gd, r) -> Self:
        self = cls.__new__(cls)
        self.__gd__ = gd
        self.__r__ = r
        self.__init__()

        return self
