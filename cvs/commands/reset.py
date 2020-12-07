from cvs import CVSBranch, CVSError, Command, Diff, Revision
from datetime import datetime
from pathlib import Path
import logging


class Reset(Command):
    """
    Resets the content from version of file.
    If version and branch was not entered,
    the last committed version from master branch would be reset.
    """
    def run(self) -> None:
        try:
            for file in self.arguments['files']:
                self.reset(self.system.directory / file)
        except Exception as err:
            raise CVSError(Reset, str(err))

    def set_parser(self, subparsers_list) -> None:
        parser = subparsers_list.add_parser('reset')
        parser.set_defaults(command=Reset)
        parser.add_argument('-b', '--branch', default='master',
                            help='Branch name')
        parser.add_argument('-rev', '--revision', help='Revision number')
        parser.add_argument('files', nargs='+', help='File name')

    def reset(self, file: Path) -> None:
        branch = self.get_branch()
        relative_path = file.relative_to(self.system.directory)
        not_found_msg = '{} was not reset because his source' \
                        ' was not found in repository'.format(relative_path)
        if str(relative_path) not in branch.source.keys():
            if not self.arguments['ignore_all']:
                logging.warning(not_found_msg)
        last_diff = None
        for rev in branch.revisions:
            if rev.id == self.arguments['revision']:
                for diff in rev.diffs:
                    if diff.file == str(relative_path):
                        self.get_version(branch, diff, file)
                        break
                else:
                    if not self.arguments['ignore_all']:
                        logging.warning(not_found_msg)
                    return
                break
            for diff in rev.diffs:
                if diff.file == str(relative_path):
                    last_diff = diff
        if last_diff is None:
            if not self.arguments['ignore_all']:
                logging.warning(not_found_msg)
            return
        self.get_version(branch, last_diff, file)

    def get_version(self, branch: CVSBranch, diff: Diff, file: Path) -> None:
        relative_path = file.relative_to(self.system.directory)
        source_rev = branch.source[str(relative_path)]
        for rev_diff in source_rev.diffs:
            if rev_diff.file == diff.file:
                file_diff = rev_diff
                break
        else:
            if not self.arguments['ignore_all']:
                logging.warning('{} was not reset because his source'
                                ' was not found in repository'
                                .format(relative_path))
            return
        file_lines = file_diff.diff.split('\n')
        diff_lines = diff.diff.split('\n')
        self.restore_file(file_lines, diff_lines)
        if not self.arguments['ignore_all'] and\
                not self.arguments['ignore_most']:
            logging.info('{} was reset from branch {}, rev {}'
                         .format(relative_path, branch.name, source_rev.id))
        if not self.arguments['no_disk_changes']:
            with file.open('w', encoding='utf-8') as file_wrapper:
                file_wrapper.write('\n'.join(file_lines))
            if not self.arguments['no_logging']:
                self.update_log(source_rev, relative_path)

    def update_log(self, revision: Revision, file: Path) -> None:
        json_message = {
                'Command: ': 'Reset',
                'Date, time: ': str(datetime.now()),
                'Comment: ': '{} was reset from branch {}, rev {}'
                             .format(file, self.arguments['branch'],
                                     revision.id)
        }
        self.put_message_into_log(json_message)
