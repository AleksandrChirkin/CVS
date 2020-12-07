from cvs import Command, CVSError
from pathlib import Path
import logging
import os
import shutil


class Init(Command):
    """
    Creates a repository (if it does not exist) or recreates it
    """

    def run(self) -> None:
        try:
            if self.arguments['recreate']:
                self.recreate_repository()
            else:
                self.create_repository()
        except Exception as err:
            raise CVSError(Init, str(err))

    def set_parser(self, subparsers_list) -> None:
        parser = subparsers_list.add_parser('init')
        parser.set_defaults(command=Init)
        parser.add_argument('-r', '--recreate', action='store_true',
                            help='Recreates repository')

    def recreate_repository(self) -> None:
        if not Path(self.system.repository).exists():
            raise CVSError(Init, "Repository does not exist! "
                           "To create a repository, use 'init' command")
        for rep_name, subdirs, files in os.walk(self.system.repository,
                                                False):
            for item in files:
                full_item = Path(rep_name) / item
                if not self.arguments['no_disk_changes']:
                    os.remove(full_item)
                logging.debug(f"{full_item} removed")
            for folder in subdirs:
                full_folder = Path(rep_name) / folder
                if not self.arguments['no_disk_changes']:
                    os.rmdir(full_folder)
                logging.debug(f"{full_folder} removed")
        if self.system.cvsignore.exists():
            if not self.arguments['no_disk_changes']:
                os.remove(self.system.cvsignore)
            logging.debug(f".cvsignore file in {self.system.directory}"
                          f" removed")
        if not self.arguments['no_disk_changes']:
            os.rmdir(self.system.repository)
        logging.info(f"Repository in {self.system.directory} removed")
        self.create_repository()

    def create_repository(self) -> None:
        if not self.arguments['no_disk_changes']:
            os.mkdir(self.system.repository)
        logging.info(f'Repository in {self.system.directory} created')
        if not self.arguments['no_disk_changes']:
            os.mkdir(self.system.branches)
        logging.debug('Branches folder created')
        if not self.arguments['no_disk_changes']:
            os.mkdir(self.system.revisions)
        logging.debug('Revisions folder created')
        if not self.arguments['no_disk_changes']:
            os.mkdir(self.system.diffs)
        logging.debug('Diffs folder created')
        if not self.arguments['no_disk_changes']:
            os.mkdir(self.system.tags)
        logging.debug('Tags folder created')
        if not self.arguments['no_disk_changes']:
            shutil.copyfile(self.system.directory / '.gitignore',
                            self.system.cvsignore)
            with self.system.cvsignore.open('a+',
                                            encoding='utf-8') as cvsignore:
                cvsignore.write('\n.git')
        logging.debug('.cvsignore file created')
