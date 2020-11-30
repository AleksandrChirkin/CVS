from abc import abstractmethod
from cvs import System


class Command:
    @abstractmethod
    def run(self, system: System) -> None:
        raise NotImplementedError

    @abstractmethod
    def set_parser(self, subparsers_list) -> None:
        raise NotImplementedError
