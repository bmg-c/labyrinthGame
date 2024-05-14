from enum import Enum

constants = {
    "START_COLOR": "blue",
    "EXIT_COLOR": "blue",
    "WALL_COLOR": "black",
    "PATH_COLOR": "green",
    "EMPTY_COLOR": "#ddd",
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
