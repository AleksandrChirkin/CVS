from cvs import Command, CVSError, System
from datetime import datetime
from pathlib import Path
import json
import os
import shutil


class Init(Command):
    """
    Creates a repository (if it does not exist) or recreates it
    """

    def run(self, system: System) -> None:
        try:
            if system.arguments['recreate']:
                self.reset_repository(system)
            else:
                self.create_repository(system)
        except OSError as err:
            raise CVSError(Init, str(err.__traceback__))

    def set_parser(self, subparsers_list) -> None:
        parser = subparsers_list.add_parser('init')
        parser.set_defaults(command=Init)
        parser.add_argument('-r', '--recreate', action='store_true',
                            help='Recreates repository')

    def reset_repository(self, system: System) -> None:
        if not Path.exists(system.repository):
            raise CVSError(Init, "Repository does not exist! "
                           "To create a repository, use 'init' command")
        content = os.walk(system.repository, False)
        for element in content:
            for item in element[2]:
                if not system.arguments['no_disk_changes']:
                    os.remove(Path("{}/{}".format(element[0], item)))
                if not system.arguments['ignore_all'] and \
                        not system.arguments['ignore_most']:
                    print(Path("{}/{} removed".format(element[0], item)))
            for folder in element[1]:
                if not system.arguments['no_disk_changes']:
                    os.rmdir(Path("{}/{}".format(element[0], folder)))
                if not system.arguments['ignore_all'] and \
                        not system.arguments['ignore_most']:
                    print(Path("{}/{} removed".format(element[0], folder)))
        if not system.arguments['no_disk_changes']:
            os.remove(system.cvsignore)
        if not system.arguments['ignore_all'] and \
                not system.arguments['ignore_most']:
            print(".cvsignore file in {} removed".format(system.directory))
        if not system.arguments['no_disk_changes']:
            os.rmdir(system.repository)
        if not system.arguments['ignore_all'] and \
                not system.arguments['ignore_most']:
            print("Repository in {} removed".format(system.directory))
        self.create_repository(system)

    def create_repository(self, system: System) -> None:
        if not system.arguments['no_disk_changes']:
            os.mkdir(system.repository)
        if not system.arguments['ignore_all'] and \
                not system.arguments['ignore_most']:
            print('Repository created')
        if not system.arguments['no_disk_changes'] and\
                not system.arguments['no_logging']:
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
            with open(system.history, 'w', encoding='utf-8') as history:
                json.dump(history_head, history, indent=4)
        if not system.arguments['ignore_all'] and \
                not system.arguments['ignore_most']:
            print('History file created')
        if not system.arguments['no_disk_changes']:
            os.mkdir(system.branches)
        if not system.arguments['ignore_all'] and \
                not system.arguments['ignore_most']:
            print('Branches folder created')
        if not system.arguments['no_disk_changes']:
            os.mkdir(system.revisions)
        if not system.arguments['ignore_all'] and \
                not system.arguments['ignore_most']:
            print('Revisions folder created')
        if not system.arguments['no_disk_changes']:
            os.mkdir(system.diffs)
        if not system.arguments['ignore_all'] and \
                not system.arguments['ignore_most']:
            print('Diffs folder created')
        self.make_cvsignore(system)
        self.make_error_log(system)

    @staticmethod
    def make_cvsignore(system: System) -> None:
        if not system.arguments['no_disk_changes']:
            shutil.copyfile(Path('{}/.gitignore'.format(system.directory)),
                            system.cvsignore)
            with open(system.cvsignore, 'a', encoding='utf-8') as cvsignore:
                cvsignore.write('\n.git')
        if not system.arguments['ignore_all'] and \
                not system.arguments['ignore_most']:
            print('.cvsignore file created')

    @staticmethod
    def make_error_log(system: System) -> None:
        log_head = {
            'Title: ': 'CVS Errors List',
            'Errors List: ': []
        }
        if not system.arguments['no_disk_changes']:
            with open('{}/errorlog.json'.format(system.repository),
                      'w', encoding='utf-8') as history:
                json.dump(log_head, history, indent=4)
        if not system.arguments['ignore_all'] and \
                not system.arguments['ignore_most']:
            print('Error log created')
