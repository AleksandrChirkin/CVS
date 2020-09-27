from abc import abstractmethod
import os


class System:
    def __init__(self, arguments):
        self.arguments = arguments
        self.directory = arguments.directory
        self.repository = '{0}/.repos'.format(self.directory)
        self.history = '{0}/history.rcs'.format(self.repository)
        self.diffs = '{0}/diffs'.format(self.repository)
        self.revisions = '{0}/revisions'.format(self.repository)

    def run(self):
        try:
            self.arguments.command().run(self)
        except AttributeError:
            print("ERROR: Improper attributes!")

    @staticmethod
    def find_all_revisions(system):
        revisions = next(os.walk(system.revisions))
        all_revisions = []
        for revision in revisions[1]:
            all_revisions.append(revision)
        return all_revisions
