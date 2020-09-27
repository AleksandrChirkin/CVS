from System import Command
from datetime import datetime
import json
import os
import shutil


class Commit(Command):
    """
    Commits files to repository.
    """
    def run(self, system):
        if system.arguments.revision is None:
            revision = datetime.now().strftime('%Y%m%d%H%M%S%f')
        else:
            revision = system.arguments.revision
        if revision in system.find_all_revisions(system):
            print('ERROR: Attempt to modify already existing revision {0}!'
                  .format(system.arguments.rev))
        try:
            with open('{0}/add_list.cvs'.format(system.repository))\
                    as commit_list:
                files = commit_list.readlines()
            self.create_revision(system, revision)
            for file in files:
                self.commit(system, file[:file.index('->')],
                            file[file.index('->')+2:-1], revision)
        except OSError:
            print("ERROR: Commit list was not found")
        else:
            os.remove('{0}/add_list.cvs'.format(system.repository))

    @staticmethod
    def create_revision(system, revision):
        revision_folder = '{0}/{1}'.format(system.revisions, revision)
        if not system.arguments.no_disk_changes:
            os.mkdir(revision_folder)
        if not system.arguments.ignore_all and \
                not system.arguments.ignore_most:
            print('{0} directory created'.format(revision_folder))
        levels = system.directory.split('/')[1:]
        for i in range(1, len(levels)+1):
            level_folder = '{0}/{1}'.format(revision_folder,
                                            '/'.join(levels[:i]))
            if not system.arguments.no_disk_changes:
                os.mkdir(level_folder)
            if not system.arguments.ignore_all and \
                    not system.arguments.ignore_most:
                print('{0} directory created'.format(level_folder))
        dir_contents = os.walk(system.directory)
        for level in dir_contents:
            for folder in level[1]:
                new_directory = '{0}{1}/{2}'.format(revision_folder,
                                                    level[0], folder)
                if not system.arguments.no_disk_changes and \
                        '/.repos' not in '{0}/{1}'.format(level[0], folder):
                    os.mkdir(new_directory)
                    if not system.arguments.ignore_all and \
                            not system.arguments.ignore_most:
                        print('{0} directory created'.format(new_directory))

    @staticmethod
    def commit(system, file, diff, revision):
        if diff == 'self':
            if not system.arguments.no_disk_changes:
                shutil.copyfile(file,
                                '{0}/{1}{2}'.format(system.revisions,
                                                    revision, file))
        else:
            with open(file) as f, open('{0}/{1}'.format(system.diffs, diff)) as diff:
                file_lines = f.readlines()
                diff_lines = diff.readlines()
            files_margin = 0
            for i in range(len(diff_lines)):
                if diff_lines[i][0] == '+':
                    file_lines.pop(i-files_margin)
                    files_margin += 1
                elif diff_lines[i][0] == '-':
                    file_lines.insert(i-files_margin, diff_lines[i][2:])
                    files_margin += 1
                elif diff_lines[i][0] == '?':
                    files_margin += 1
            with open('{0}/{1}{2}'.format(system.revisions, revision, file),
                      'w') as file_in_revision:
                file_in_revision.write(''.join(file_lines))
        if not system.arguments.no_disk_changes and \
                not system.arguments.no_logging:
            message = {
                'Command: ': 'Commit',
                'Date, time: ': str(datetime.now()),
                'Message: ': '{0} was committed to revision {1}.'
                             .format(file, revision),
                'Note: ': system.arguments.message
            }
            with open(system.history, 'r') as history:
                data = json.load(history)
            data['Contents: '].append(message)
            with open(system.history, 'a+') as history:
                json.dump(data, history, indent=4)
        if not system.arguments.ignore_all:
            print('{0} was committed to revision {1}'.format(file, revision))
