from System import Command
from datetime import datetime
from pathlib import Path
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
        if revision in system.find_all_revisions():
            print('ERROR: Attempt to modify already existing revision {}!'
                  .format(system.arguments.rev))
        try:
            with open(Path('{}/add_list.cvs'.format(system.repository)))\
                    as commit_list:
                files = commit_list.readlines()
            self.create_revision(system, revision)
            for file in files:
                self.commit(system, file[:file.index('->')],
                            file[file.index('->')+2:-1], revision)
        except OSError as err:
            print("OS ERROR:{}".format(err))
        else:
            os.remove(Path('{}/add_list.cvs'.format(system.repository)))

    @staticmethod
    def create_revision(system, revision):
        revision_folder = Path('{}/{}'.format(system.revisions, revision))
        if not system.arguments.no_disk_changes:
            os.mkdir(revision_folder)
        if not system.arguments.ignore_all and \
                not system.arguments.ignore_most:
            print('{} directory created'.format(revision_folder))
        slash = system.get_slash()
        levels = str(system.directory).split(slash)
        for i in range(2, len(levels)+1):
            level_folder = Path('{}/{}'.format(revision_folder,
                                               slash.join(levels[1:i])))
            if not system.arguments.no_disk_changes:
                os.mkdir(level_folder)
            if not system.arguments.ignore_all and \
                    not system.arguments.ignore_most:
                print('{} directory created'.format(level_folder))
        dir_contents = os.walk(system.directory)
        for level in dir_contents:
            for folder in level[1]:
                new_directory = Path('{}/{}/{}'.format(revision_folder,
                                                       slash.join(levels[1:]),
                                                       folder))
                original_path = str(Path('{}/{}'.format(level[0], folder)))
                if not system.arguments.no_disk_changes and \
                        not system.is_in_cvsignore(original_path):
                    os.mkdir(new_directory)
                    if not system.arguments.ignore_all and \
                            not system.arguments.ignore_most:
                        print('{} directory created'.format(new_directory))

    @staticmethod
    def commit(system, file, diff, revision):
        if diff == 'self':
            if not system.arguments.no_disk_changes:
                slash = system.get_slash()
                levels = str(file).split(slash)
                shutil.copyfile(file,
                                Path('{}/{}/{}'.format(system.revisions,
                                                       revision,
                                                       slash
                                                       .join(levels[1:]))))
        else:
            with open(file) as f, open(Path('{}/{}'.format(system.diffs,
                                                           diff))) as diff:
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
            with open(Path('{}/{}{}'.format(system.revisions, revision, file)),
                      'w') as file_in_revision:
                file_in_revision.write(''.join(file_lines))
        message = '{} was committed to revision {}.'.format(file, revision)
        if not system.arguments.no_disk_changes and \
                not system.arguments.no_logging:
            json_message = {
                'Command: ': 'Commit',
                'Date, time: ': str(datetime.now()),
                'Message: ': message,
                'Note: ': system.arguments.message
            }
            with open(system.history, 'r') as history:
                data = json.load(history)
            data['Contents: '].append(json_message)
            with open(system.history, 'w') as history:
                json.dump(data, history, indent=4)
        if not system.arguments.ignore_all:
            print(message)
