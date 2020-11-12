from argparse import Namespace
from pathlib import Path
from typing import List
import os


class System:
    def __init__(self, arguments: Namespace):
        self.arguments = arguments
        self.directory = arguments.directory
        self.repository = Path('{}/.repos'.format(self.directory))
        self.history = Path('{}/history.json'.format(self.repository))
        self.diffs = Path('{}/diffs'.format(self.repository))
        self.revisions = Path('{}/revisions'.format(self.repository))
        self.cvsignore = Path('{}/.cvsignore'.format(self.directory))

    def run(self) -> None:
        try:
            self.arguments.command().run(self)
        except AttributeError as err:
            print("ERROR: Improper attributes:{}".format(err))

    def find_all_revisions(self) -> List[str]:
        try:
            revisions = next(os.walk(self.revisions))[1]
        except StopIteration:
            return list()
        else:
            all_revisions = []
            for revision in revisions:
                all_revisions.append(revision)
            return all_revisions

    def is_in_cvsignore(self, file: str) -> bool:
        with open(self.cvsignore) as cvsignore:
            ignored = cvsignore.readlines()
        for item in ignored:
            if item[:-1] in file:
                return True
        return False

    @staticmethod
    def get_slash() -> str:
        if os.name == 'nt':
            return '\\'
        return '/'
