class CVSError(Exception):
    def __init__(self, text: str) -> None:
        self.message = text

    def __str__(self) -> str:
        return self.message
