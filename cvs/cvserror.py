from typing import Type


class CVSError(Exception):
    def __init__(self, command: Type, text: str) -> None:
        self.command = str(command)
        self.message = text

    def __str__(self) -> str:
        return ' {}: {}'.format(self.command.split('.')[-1][:-2],
                                self.message)
