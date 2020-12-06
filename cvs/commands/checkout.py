from cvs import CVSBranch, Command, CVSError, DiffKind
from datetime import datetime
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
                raise CVSError(Checkout, 'Branch {} does not exist!'
                               .format(branch.name))
            for item in os.walk(self.system.directory):
                for file in item[2]:
                    file_path = Path(item[0])/file
                    if not self.system.is_in_cvsignore(str(file_path)):
                        self.checkout(branch, file_path)
            self.system.set_current_branch(self.arguments['branch'])

        except Exception as err:
            raise CVSError(Checkout, str(err))

    def set_parser(self, subparsers_list) -> None:
        parser = subparsers_list.add_parser('checkout')
        parser.set_defaults(command=Checkout)
        parser.add_argument('branch', help='Branch name')

    def checkout(self, branch: CVSBranch, file: Path) -> None:
        relative_path = file.relative_to(self.system.directory)
        not_found_msg = '{} was not found in branch {}'\
            .format(relative_path, branch.name)
        if str(relative_path) not in branch.source.keys():
            logging.warning(not_found_msg)
            return
        last_version = None
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
            self.make_output(branch, file)
        else:
            for source_diff in branch.source[str(relative_path)].diffs:
                if source_diff.file == str(relative_path):
                    file_lines = source_diff.diff.split('\n')
                    break
            else:
                raise CVSError(Checkout, not_found_msg)
            diff_lines = last_version.diff.split('\n')
            self.restore_file(file_lines, diff_lines)
            with file.open('w', encoding='utf-8') as file_writer:
                file_writer.write('\n'.join(file_lines))
            self.make_output(branch, file)

    def make_output(self, branch: CVSBranch, file: Path):
        if not self.arguments['ignore_all'] and \
                not self.arguments['ignore_most']:
            logging.info('{} was checked out from branch {}'
                         .format(file.relative_to(self.system.directory),
                                 branch.name))
        if not self.arguments['no_logging'] and \
                not self.arguments['no_disk_changes']:
            json_message = {
                'Command: ': 'Checkout',
                'Date, time: ': str(datetime.now()),
                'Comment: ': '{} was checked out from branch {}'
                             .format(file, branch.name),
            }
            self.put_message_into_log(json_message)
