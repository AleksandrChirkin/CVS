from cvs import Command, CVSError
from pathlib import Path
import logging
import os


class Status(Command):
    """
    Shows the current status of repository
    """
    def run(self) -> None:
        try:
            branch = self.get_branch()
            logging.info(f'Current branch: {branch.name}')
            for item in os.walk(self.system.directory):
                for file in item[2]:
                    full_path = Path(item[0]) / file
                    relative_path = full_path\
                        .relative_to(self.system.directory)
                    if str(relative_path) not in branch.source.keys():
                        if not self.system.is_in_cvsignore(full_path):
                            logging.info(f'New file: {relative_path}')
                    elif self.is_file_modified(branch, full_path):
                        logging.info(f'File {relative_path} was modified')
        except Exception as err:
            raise CVSError(str(err))

    def set_parser(self, subparsers_list) -> None:
        parser = subparsers_list.add_parser('status')
        parser.set_defaults(command=Status)
        parser.add_argument('-b', '--branch', default='master',
                            help='Branch name')
