from abc import abstractmethod


class Command:
    @abstractmethod
    def run(self, system):
        raise NotImplementedError
