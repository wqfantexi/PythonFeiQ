from enum import Enum


class ViewType(Enum):
    VIEW_UNKNOWN = 0
    VIEW_USER = 1
    VIEW_CONTENT = 2


class View:
    def __init__(self):
        pass

    def type(self):
        return ViewType.VIEW_UNKNOWN
