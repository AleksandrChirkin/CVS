from abc import abstractmethod
from cvsdomain import System


class Command:
    @abstractmethod
    def run(self, system: System) -> None:
        raise NotImplementedError
