from System import Command
from datetime import datetime
import difflib
import os
import random


class Add(Command):
    """
    Adds a new file to commit list.
    """
    def run(self, system):
        try:
            for file in system.arguments.files:
                if not os.path.exists(file) and\
                        not system.arguments.ignore_all:
                    print('{0}/{1} does not exist!'.format(system.directory,
                                                           file))
                elif os.path.isdir(file):
                    content = os.walk(file)
                    for line in content:
                        for item in line[2]:
                            self.add(system, '{0}/{1}/{2}'
                                     .format(system.directory, line[0], item))
                else:
                    self.add(system,
                             '{0}/{1}'.format(system.directory, file))
        except OSError as err:
            print("OS error: {0}".format(err))

    def add(self, system, file):
        if ".repos/" in file:
            if not system.arguments.ignore_all:
                print('{0} ignored because it is repository file'
                      .format(file))
        else:
            revisions = system.find_all_revisions(system)
            if len(revisions) == 0:
                self.add_if_no_previous_revisions(system, file)
            else:
                latest_revision = None
                for revision in revisions:
                    current_revision = '{0}/{1}{2}'.format(system.revisions,
                                                           revision, file)
                    if os.path.exists(current_revision):
                        latest_revision = current_revision
                if latest_revision is None:
                    self.add_if_no_previous_revisions(system, file)
                else:
                    self.add_if_previous_revisions_exist(system, file,
                                                         latest_revision)

    @staticmethod
    def add_if_no_previous_revisions(system, file):
        if not system.arguments.no_disk_changes:
            with open('{0}/add_list.cvs'.format(system.repository),
                      'a+') as add_list:
                add_list.write('{0}->self\n'.format(file))
            if not system.arguments.no_logging:
                with open(system.history, 'a+') as history:
                    history.write('{0} {1} was added. Message: {2}\n'
                                  .format(datetime.now(), file,
                                          system.arguments.message))
        if not system.arguments.ignore_all:
            print('{0} was added'.format(file))

    @staticmethod
    def add_if_previous_revisions_exist(system, file, latest_revision):
        with open(file) as f, open(latest_revision) as rev:
            differ = difflib.ndiff(f.readlines(), rev.readlines())
        diff_number = random.randint(0, 10 ** 32)
        if not system.arguments.no_disk_changes:
            with open('{0}/{1}'.format(system.diffs, diff_number), 'w') as diff:
                for item in differ:
                    diff.write(item)
        if not system.arguments.ignore_all and \
                not system.arguments.ignore_most:
            print('{0} differ created'.format(diff_number))
        if not system.arguments.no_disk_changes:
            with open('{0}/add_list.cvs'
                      .format(system.repository), 'a+') as add_list:
                add_list.write('{0}->{1}\n'.format(file, diff_number))
            if not system.arguments.no_logging:
                with open(system.history, 'a+') as history:
                    history.write('{0} {1} was added to diff {2}. '
                                  'Message: {3}\n'
                                  .format(datetime.now(), file, diff_number,
                                          system.arguments.message))
        if not system.arguments.ignore_all:
            print('{0} was added to diff {1}'.format(file, diff_number))
