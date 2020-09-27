from System import Command
from datetime import datetime
import json
import os


class Init(Command):
    """
    Creates a repository (if it does not exist) or recreates it
    """
    def run(self, system):
        if system.arguments.recreate:
            self.reset_repository(system)
        else:
            self.create_repository(system)

    def reset_repository(self, system):
        try:
            if not os.path.exists(system.repository):
                raise OSError("Repository does not exist! "
                              "To create a repository, use 'init' command")
            content = os.walk(system.repository, False)
            for element in content:
                for item in element[2]:
                    if not system.arguments.no_disk_changes:
                        os.remove("{0}/{1}".format(element[0], item))
                    if not system.arguments.ignore_all and\
                            not system.arguments.ignore_most:
                        print("{0}/{1} removed".format(element[0], item))
                for folder in element[1]:
                    if not system.arguments.no_disk_changes:
                        os.rmdir("{0}/{1}".format(element[0], folder))
                    if not system.arguments.ignore_all and \
                            not system.arguments.ignore_most:
                        print("{0}/{1} removed".format(element[0], folder))
            if not system.arguments.no_disk_changes:
                os.rmdir(system.repository)
            if not system.arguments.ignore_all and \
                    not system.arguments.ignore_most:
                print("Repository in {0} removed".format(system.directory))
            self.create_repository(system)
        except OSError as err:
            print("ERROR: {0}".format(err))

    @staticmethod
    def create_repository(system):
        try:
            if not system.arguments.no_disk_changes:
                os.mkdir(system.repository)
                if not system.arguments.ignore_all and\
                        not system.arguments.ignore_most:
                    print('Repository created')
            if not system.arguments.no_logging:
                history_head = {
                    'Title: ': 'History of repository',
                    'Contents: ': []
                }
                message = {
                    'Command: ': 'Init',
                    'Date, time: ': str(datetime.now()),
                    'Message: ': 'Repository created.'
                }
                history_head['Contents: '].append(message)
                with open(system.history, 'w') as history:
                    json.dump(history_head, history, indent=4)
            if not system.arguments.ignore_all and \
                    not system.arguments.ignore_most:
                print('History file created')
            if not system.arguments.no_disk_changes:
                os.mkdir(system.revisions)
            if not system.arguments.ignore_all and \
                    not system.arguments.ignore_most:
                print('Revisions folder created')
            if not system.arguments.no_disk_changes:
                os.mkdir(system.diffs)
            if not system.arguments.ignore_all and \
                    not system.arguments.ignore_most:
                print('Diffs folder created')
        except OSError:
            print("ERROR: Repository has already been created!\n"
                  "To reset repository, use 'init -r' command")
