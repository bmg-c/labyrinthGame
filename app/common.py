from enum import Enum

constants = {
    "START_COLOR": "#1F6AA5",
    "EXIT_COLOR": "#1F6AA5",
    "WALL_COLOR": "#171717",
    "PATH_COLOR": "#64AB00",
    "EMPTY_COLOR": "#DCE4EE",
}

blockState_to_color = ["WALL_COLOR", "EMPTY_COLOR", "PATH_COLOR", "START_COLOR", "EXIT_COLOR"]


class BlockState(Enum):
    WALL = 0
    EMPTY = 1
    PATH = 2
    START = 3
    EXIT = 4

    def to_color(self) -> str:
        return blockState_to_color[self.value]


class Block:
    rectangle: int

    def __init__(self, x: int, y: int, state: BlockState):
        self.x: int = x
        self.y: int = y
        self.state: BlockState = state

    def __str__(self):
        return f"{self.state}({self.x}, {self.y})"

    def __unicode__(self):
        return f"{self.state}({self.x}, {self.y})"

    def __repr__(self):
        return f"{self.state}({self.x}, {self.y})"
