from cvs import Command, System
from datetime import datetime
from pathlib import Path
import difflib
import json
import os
import random


class Add(Command):
    """
    Adds a new file to commit list.
    """
    def run(self, system: System) -> None:
        try:
            for file in system.arguments.files:
                if not os.path.exists(file) and\
                        not system.arguments.ignore_all:
                    print('{}/{} does not exist!'.format(system.directory,
                                                         file))
                elif os.path.isdir(file):
                    content = os.walk(file)
                    for line in content:
                        for item in line[2]:
                            self.add(system, Path('{}/{}/{}'
                                     .format(system.directory, line[0],
                                             item)))
                else:
                    self.add(system,
                             Path('{}/{}'.format(system.directory, file)))
        except OSError as err:
            print("OS error: {}".format(err))

    def add(self, system: System, file: Path) -> None:
        if system.is_in_cvsignore(str(file)):
            if not system.arguments.ignore_all:
                print('{} was ignored because it is in .cvsignore'
                      .format(file))
        else:
            revisions = system.find_all_revisions()
            if len(revisions) == 0:
                self.add_if_no_previous_revisions(system, file)
            else:
                latest_revision = None
                for revision in revisions:
                    current_revision = Path('{}/{}{}'
                                            .format(system.revisions,
                                                    revision, file))
                    if os.path.exists(current_revision):
                        latest_revision = current_revision
                if latest_revision is None:
                    self.add_if_no_previous_revisions(system, file)
                else:
                    self.add_if_previous_revisions_exist(system, file,
                                                         latest_revision)

    def add_if_no_previous_revisions(self, system: System,
                                     file: Path) -> None:
        message = '{} was added.'.format(file)
        if not system.arguments.no_disk_changes:
            with open(Path('{}/add_list.cvs'.format(system.repository)),
                      'a+') as add_list:
                add_list.write('{}->self\n'.format(file))
            if not system.arguments.no_logging:
                self.update_log(system, message)
        if not system.arguments.ignore_all:
            print(message)

    def add_if_previous_revisions_exist(self, system: System, file: Path,
                                        latest_revision: Path) -> None:
        with open(file) as f, open(latest_revision) as rev:
            differ = difflib.ndiff(f.readlines(), rev.readlines())
        diff_number = random.randint(0, 10 ** 32)
        if not system.arguments.no_disk_changes:
            with open(Path('{}/{}'.format(system.diffs, diff_number)),
                      'w') as diff:
                for item in differ:
                    diff.write(item)
        if not system.arguments.ignore_all and \
                not system.arguments.ignore_most:
            print('{} differ created'.format(diff_number))
        message = '{} was added to diff {}.'.format(file, diff_number)
        if not system.arguments.no_disk_changes:
            with open(Path('{}/add_list.cvs'
                      .format(system.repository)), 'a+') as add_list:
                add_list.write('{}->{}\n'.format(file, diff_number))
            if not system.arguments.no_logging:
                self.update_log(system, message)
        if not system.arguments.ignore_all:
            print(message)

    @staticmethod
    def update_log(system: System, message: str) -> None:
        json_message = {
            'Command: ': 'Add',
            'Date, time: ': str(datetime.now()),
            'Message: ': message,
            'Note: ': system.arguments.message
        }
        with open(system.history, 'r') as history:
            data = json.load(history)
        data['Contents: '].append(json_message)
        with open(system.history, 'w') as history:
            json.dump(data, history, indent=4)
