from typing import Type


class CVSError(Exception):
    def __init__(self, command: Type, text: str) -> None:
        self.command = str(command)
        self.txt = text
