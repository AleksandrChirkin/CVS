from abc import abstractmethod
from cvs import System


class Command:
    @abstractmethod
    def run(self, system: System) -> None:
        raise NotImplementedError
