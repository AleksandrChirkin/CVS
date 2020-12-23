from cvs import Command
from pathlib import Path
import logging


class Branch(Command):
    """
    Returns list of all existing branches
    (current branch would be with asterisk)
    """

    def run(self) -> None:
        current_branch = self.system.get_current_branch()
        for branch in self.system.branches.iterdir():
            message = str(Path(branch)
                          .relative_to(self.system.branches))[:-5]
            if message == current_branch:
                message += '(HEAD)'
            logging.info(message)

    def set_parser(self, subparsers_list) -> None:
        parser = subparsers_list.add_parser('branch')
        parser.set_defaults(command=Branch)
