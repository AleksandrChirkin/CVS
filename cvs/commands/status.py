from cvs import Command
from pathlib import Path
import logging
import os


class Status(Command):
    """
    Shows the current status of repository
    """
    def run(self) -> None:
        branch = self.get_branch()
        logging.info('Current branch: {}'.format(branch.name))
        for item in os.walk(self.system.directory):
            for file in item[2]:
                full_path = Path(item[0]) / file
                relative_path = full_path.relative_to(self.system.directory)
                if str(relative_path) not in branch.source.keys():
                    if not self.system.is_in_cvsignore(str(full_path)):
                        logging.info('New file: {}'.format(relative_path))
                elif self.is_file_modified(branch, full_path):
                    logging.info('File {} was modified'
                                 .format(relative_path))

    def set_parser(self, subparsers_list) -> None:
        parser = subparsers_list.add_parser('status')
        parser.set_defaults(command=Status)
        parser.add_argument('-b', '--branch', default='master',
                            help='Branch name')
