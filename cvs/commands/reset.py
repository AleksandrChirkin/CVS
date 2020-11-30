from cvs import Branch, Command, Diff, Revision, System
from datetime import datetime
from pathlib import Path
import json


class Reset(Command):
    """
    Resets the content from version of file.
    If version and branch was not entered,
    the last committed version from master branch would be reset.
    """
    def run(self, system: System) -> None:
        for file in system.arguments['files']:
            self.reset(system, Path('{}/{}'.format(system.directory, file)))

    def set_parser(self, subparsers_list) -> None:
        parser = subparsers_list.add_parser('reset')
        parser.set_defaults(command=Reset)
        parser.add_argument('-b', '--branch', default='master',
                            help='Branch name')
        parser.add_argument('-rev', '--revision', help='Revision number')
        parser.add_argument('files', nargs='+', help='File name')

    def reset(self, system: System, file: Path) -> None:
        branch = system.get_branch()
        not_found_msg = '{} was not reset because his source was not found in repository'.format(file)
        if file not in branch.source:
            if not system.arguments['ignore_all']:
                print(not_found_msg)
        last_diff = None
        for rev in branch.revisions:
            if rev.id == system.arguments['revision']:
                for diff in rev.diffs:
                    if diff.file == str(file):
                        self.get_version(system, branch, diff, file)
                        break
                else:
                    if not system.arguments['ignore_all']:
                        print(not_found_msg)
                    return
                break
            for diff in rev.diffs:
                if diff.file == str(file):
                    last_diff = diff
        if last_diff is None:
            if not system.arguments['ignore_all']:
                print(not_found_msg)
            return
        self.get_version(system, branch, last_diff, file)

    def get_version(self, system: System, branch: Branch,
                    diff: Diff, file: Path) -> None:
        source_rev = branch.source[str(file)]
        file_diff = None
        for rev_diff in source_rev.diffs:
            if rev_diff.id == diff.id:
                file_diff = rev_diff
                break
        if file_diff is None:
            if not system.arguments['ignore_all']:
                print('')
            return
        file_lines = file_diff.diff.split('\n')
        diff_lines = diff.diff.split('\n')
        system.restore_file(file_lines, diff_lines)
        if not system.arguments['ignore_all'] and not system.arguments['ignore_most']:
            print('{} was reset from branch {}, rev {}'
                  .format(file, branch.name, source_rev.id))
        if not system.arguments['no_disk_changes']:
            with open(file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(file_lines))
        elif not system.arguments['no_logging']:
            self.update_log(system, source_rev, file)

    @staticmethod
    def update_log(system: System, revision: Revision,
                   file: Path) -> None:
        json_message = {
                'Command: ': 'Reset',
                'Date, time: ': str(datetime.now()),
                'Comment: ': '{} was reset from branch {}, rev {}'
                             .format(file, system.arguments['branch'],
                                     revision.id)
        }
        with open(system.history, 'r', encoding='utf-8') as history:
            data = json.load(history)
        data['Contents: '].append(json_message)
        with open(system.history, 'w', encoding='utf-8') as history:
            json.dump(data, history, indent=4)
