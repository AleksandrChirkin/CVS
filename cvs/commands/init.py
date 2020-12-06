from cvs import Command, CVSError
from datetime import datetime
from pathlib import Path
import json
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
        content = os.walk(self.system.repository, False)
        for element in content:
            for item in element[2]:
                if not self.arguments['no_disk_changes']:
                    os.remove(Path(element[0]) / item)
                if not self.arguments['ignore_all'] and \
                        not self.arguments['ignore_most']:
                    logging.info("{} removed".format(Path(element[0]) /
                                                     item))
            for folder in element[1]:
                if not self.arguments['no_disk_changes']:
                    os.rmdir(Path(element[0]) / folder)
                if not self.arguments['ignore_all'] and \
                        not self.arguments['ignore_most']:
                    logging.info("{} removed".format(Path(element[0]) /
                                                     folder))
        if Path(self.system.cvsignore).exists():
            if not self.arguments['no_disk_changes']:
                os.remove(self.system.cvsignore)
            if not self.arguments['ignore_all'] and \
                    not self.arguments['ignore_most']:
                logging.info(".cvsignore file in {} removed"
                             .format(self.system.directory))
        if not self.arguments['no_disk_changes']:
            os.rmdir(self.system.repository)
        if not self.arguments['ignore_all'] and \
                not self.arguments['ignore_most']:
            logging.info("Repository in {} removed"
                         .format(self.system.directory))
        self.create_repository()

    def create_repository(self) -> None:
        if not self.arguments['no_disk_changes']:
            os.mkdir(self.system.repository)
        if not self.arguments['ignore_all'] and \
                not self.arguments['ignore_most']:
            logging.info('Repository created')
        if not self.arguments['no_disk_changes'] and\
                not self.arguments['no_logging']:
            history_head = {
                'Title: ': 'History of repository',
                'Contents: ': []
            }
            message = {
                'Command: ': 'Init',
                'Date, time: ': str(datetime.now()),
                'Comment: ': 'Repository created.'
            }
            history_head['Contents: '].append(message)
            with self.system.history.open('w', encoding='utf-8') as history:
                json.dump(history_head, history, indent=4)
        if not self.arguments['ignore_all'] and \
                not self.arguments['ignore_most']:
            logging.info('History file created')
        if not self.arguments['no_disk_changes']:
            os.mkdir(self.system.branches)
        if not self.arguments['ignore_all'] and \
                not self.arguments['ignore_most']:
            logging.info('Branches folder created')
        if not self.arguments['no_disk_changes']:
            os.mkdir(self.system.revisions)
        if not self.arguments['ignore_all'] and \
                not self.arguments['ignore_most']:
            logging.info('Revisions folder created')
        if not self.arguments['no_disk_changes']:
            os.mkdir(self.system.diffs)
        if not self.arguments['ignore_all'] and \
                not self.arguments['ignore_most']:
            logging.info('Diffs folder created')
        if not self.arguments['no_disk_changes']:
            os.mkdir(self.system.tags)
        if not self.arguments['ignore_all'] and \
                not self.arguments['ignore_most']:
            logging.info('Tags folder created')
        self.make_cvsignore()

    def make_cvsignore(self) -> None:
        if not self.arguments['no_disk_changes']:
            shutil.copyfile(self.system.directory / '.gitignore',
                            self.system.cvsignore)
            with self.system.cvsignore.open('a+',
                                            encoding='utf-8') as cvsignore:
                cvsignore.write('\n.git')
        if not self.arguments['ignore_all'] and\
                not self.arguments['ignore_most']:
            logging.info('.cvsignore file created')
