from cvs import CVSBranch, CVSError, Command, Diff
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
            raise CVSError(str(err))

    def set_parser(self, subparsers_list) -> None:
        parser = subparsers_list.add_parser('reset')
        parser.set_defaults(command=Reset)
        parser.add_argument('-b', '--branch', default='master',
                            help='Branch name')
        parser.add_argument('-rev', '--revision', help='Revision number')
        parser.add_argument('-t', '--tag', help='Revision number')
        parser.add_argument('files', nargs='+', help='File name')

    def reset(self, file: Path) -> None:
        relative_path = file.relative_to(self.system.directory)
        if file.is_dir():
            raise CVSError(f'{relative_path} is a directory!')
        branch = self.get_branch()
        not_found_msg = f'{relative_path} was not reset because his source' \
                        f' was not found in repository'
        if str(relative_path) not in branch.source.keys():
            raise CVSError(not_found_msg)
        last_diff = None
        revision = self.get_revision_name()
        for rev in branch.revisions:
            if rev.id == revision:
                for diff in rev.diffs:
                    if diff.file == str(relative_path):
                        self.get_version(branch, diff, file)
                        return
                raise CVSError(not_found_msg)
            for diff in rev.diffs:
                if diff.file == str(relative_path):
                    last_diff = diff
        if last_diff is None:
            raise CVSError(not_found_msg)
        self.get_version(branch, last_diff, file)

    def get_version(self, branch: CVSBranch, diff: Diff, file: Path) -> None:
        relative_path = file.relative_to(self.system.directory)
        source_rev = branch.source[str(relative_path)]
        for rev_diff in source_rev.diffs:
            if rev_diff.file == diff.file:
                file_diff = rev_diff
                break
        else:
            logging.warning(f'{relative_path} was not reset because his source'
                            ' was not found in repository')
            return
        file_lines = file_diff.diff.split('\n')
        diff_lines = diff.diff.split('\n')
        self.restore_file(file_lines, diff_lines)
        logging.info(f'{relative_path} was reset from branch {branch.name},'
                     f' rev {source_rev.id}')
        if not self.arguments['no_disk_changes']:
            with file.open('w', encoding='utf-8') as file_wrapper:
                file_wrapper.write('\n'.join(file_lines))
