from cvs import Command, System
from datetime import datetime
from pathlib import Path
import os
import shutil
import json


class Reset(Command):
    """
    Resets the content from version of file.
    If version was not entered, the last committed version would be reset.
    """
    def run(self, system: System) -> None:
        for file in system.arguments.files:
            self.reset(system, Path('{}/{}'.format(system.directory, file)))

    def reset(self, system: System, file: Path) -> None:
        revision = system.arguments.revision
        if revision is None:
            all_revisions = system.find_all_revisions()
            for rev in reversed(all_revisions):
                if self.make_output(system, file, rev):
                    break
            else:
                if not system.arguments.ignore_all:
                    print('ERROR: {} was not found in any previous revisions'
                          .format(file))
        elif not self.make_output(system, file, revision):
            print('ERROR: {} was not found in entered revision'.format(file))

    def make_output(self, system: System, file: Path, revision: str) -> bool:
        revisions_dir = system.revisions
        slash = system.get_slash()
        levels = str(file).split(slash)
        file_version = Path('{}/{}/{}'.format(revisions_dir, revision,
                                              slash.join(levels[1:])))
        if os.path.exists(file_version):
            if not system.arguments.no_disk_changes:
                shutil.copyfile(file_version, file)
            message = '{} was reset from revision {}.'.format(file, revision)
            if not system.arguments.no_disk_changes and\
                    not system.arguments.no_logging:
                self.update_log(system, message)
            if not system.arguments.ignore_all:
                print(message)
            return True
        return False

    @staticmethod
    def update_log(system: System, message: str) -> None:
        json_message = {
                'Command: ': 'Reset',
                'Date, time: ': str(datetime.now()),
                'Message: ': message
        }
        with open(system.history, 'r') as history:
            data = json.load(history)
        data['Contents: '].append(json_message)
        with open(system.history, 'w') as history:
            json.dump(data, history, indent=4)
