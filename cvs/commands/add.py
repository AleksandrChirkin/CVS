from cvs import Command, CVSError, System
from datetime import datetime
from pathlib import Path
import json
import os


class Add(Command):
    """
    Adds a new file to commit list.
    """

    def run(self, system: System) -> None:
        try:
            for file in system.arguments['files']:
                if not Path.exists(Path(file)):
                    raise CVSError(Add, '{}/{} does not exist!'
                                   .format(system.directory,
                                           file))
                elif Path.is_dir(Path(file)):
                    content = os.walk(file)
                    for line in content:
                        for item in line[2]:
                            self.add(system, Path('{}/{}/{}'
                                                  .format(system.directory,
                                                          line[0], item)))
                else:
                    self.add(system,
                             Path('{}/{}'.format(system.directory, file)))
        except OSError as err:
            raise CVSError(Add, str(err.__traceback__))

    def set_parser(self, subparsers_list) -> None:
        parser = subparsers_list.add_parser('add')
        parser.set_defaults(command=Add)
        parser.add_argument('-m', '--message', default='',
                            help='Log message')
        parser.add_argument('files', nargs='+', help='Files names')

    def add(self, system: System, file: Path) -> None:
        if system.is_in_cvsignore(str(file)):
            if not system.arguments['ignore_all']:
                print('{} was ignored because it is in .cvsignore'
                      .format(file))
        else:
            if Path.exists(system.add_list):
                with open(system.add_list, encoding='utf-8') as add_list:
                    added = json.load(add_list)
            else:
                added = []
            for item in added:
                if item == str(Path(file)):
                    if not system.arguments['ignore_all']:
                        print('{} had already been added'.format(file))
                    break
            else:
                added.append(str(file))
                if not system.arguments['no_disk_changes']:
                    with open(system.add_list, 'w',
                              encoding='utf-8') as add_list:
                        json.dump(added, add_list, indent=4)
                if not system.arguments['ignore_all'] and\
                        not system.arguments['ignore_most']:
                    print('{} was added'.format(file))
                if not system.arguments['no_disk_changes'] and\
                        not system.arguments['no_logging']:
                    self.update_log(system, file)

    @staticmethod
    def update_log(system: System, file: Path) -> None:
        json_message = {
            'Command: ': 'Add',
            'Date, time: ': str(datetime.now()),
            'Comment: ': '{} was added to add list.'.format(file),
            'Message: ': system.arguments['message']
        }
        with open(system.history, encoding='utf-8') as history:
            data = json.load(history)
        data['Contents: '].append(json_message)
        with open(system.history, 'w', encoding='utf-8') as history:
            json.dump(data, history, indent=4)
