from cvs import CVSBranch, Command, CVSError, DiffKind
from pathlib import Path
import logging
import os


class Checkout(Command):
    """
    Switching to another branch
    """
    def run(self) -> None:
        try:
            branch = self.get_branch()
            if len(branch.revisions) == 0:
                raise CVSError(f'Branch {branch.name} does not exist!')
            for directory, _, files in os.walk(self.system.directory):
                for file in files:
                    full_path = Path(directory)/file
                    short_path = full_path\
                        .relative_to(self.system.directory)
                    if not self.system.is_in_cvsignore(short_path):
                        self.checkout(branch, full_path)
            if not self.arguments['no_disk_changes']:
                self.system.set_current_branch(branch.name)
        except Exception as err:
            raise CVSError(str(err))

    def set_parser(self, subparsers_list) -> None:
        parser = subparsers_list.add_parser('checkout')
        parser.set_defaults(command=Checkout)
        parser.add_argument('-rev', '--revision', help='Revision number')
        parser.add_argument('-t', '--tag', help='Tag name')
        parser.add_argument('branch', help='Branch name')

    def checkout(self, branch: CVSBranch, file: Path) -> None:
        relative_path = file.relative_to(self.system.directory)
        not_found_msg = f'{relative_path} was not found' \
                        f' in branch {branch.name}'
        if str(relative_path) not in branch.source.keys():
            logging.warning(not_found_msg)
            return
        last_version = None
        revision = self.get_revision_name()
        if revision is not None:
            for rev in branch.revisions:
                if rev.id == revision:
                    found_revision = rev
                    break
            else:
                raise CVSError(f'Revision {revision} was not found '
                               f'in branch {branch.name}')
            for diff in found_revision.diffs:
                if diff.file == str(relative_path):
                    last_version = diff
                    break
        else:
            for rev in branch.revisions:
                for diff in rev.diffs:
                    if diff.file == str(relative_path):
                        last_version = diff
                        break
        if last_version is None:
            logging.warning(not_found_msg)
            return
        if last_version.kind == DiffKind.ADD:
            if not self.arguments['no_disk_changes']:
                with Path(file).open('w', encoding='utf-8') as file_writer:
                    file_writer.write(last_version.diff)
            logging.info(f'{relative_path} was checked out '
                         f'from branch {branch.name}')
        else:
            for source_diff in branch.source[str(relative_path)].diffs:
                if source_diff.file == str(relative_path):
                    file_lines = source_diff.diff.split('\n')
                    break
            else:
                logging.warning(not_found_msg)
                return
            diff_lines = last_version.diff.split('\n')
            self.restore_file(file_lines, diff_lines)
            if not self.arguments['no_disk_changes']:
                with file.open('w', encoding='utf-8') as file_writer:
                    file_writer.write('\n'.join(file_lines))
            logging.info(f'{relative_path} was checked out'
                         f' from branch {branch.name}')
