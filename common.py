from enum import Enum

constants = {
    "START_COLOR": "blue",
    "EXIT_COLOR": "blue",
    "WALL_COLOR": "black",
    "PATH_COLOR": "green",
    "EMPTY_COLOR": "#ddd",
}


class BlockState(Enum):
    WALL = 0
    EMPTY = 1
    PATH = 2
    START = 3
    EXIT = 4


class Block:
    def __init__(self, x, y, state: BlockState):
        self.x = x
        self.y = y
        self.state = state
        self.rectangle = None

    def __str__(self):
        return f"{self.state}({self.x}, {self.y})"

    def __unicode__(self):
        return f"{self.state}({self.x}, {self.y})"

    def __repr__(self):
        return f"{self.state}({self.x}, {self.y})"
