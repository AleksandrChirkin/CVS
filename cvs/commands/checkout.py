from cvs import Branch, Command, CVSError, DiffKind, System
from datetime import datetime
import json


class Checkout(Command):
    def run(self, system: System) -> None:
        with open(system.add_list, encoding='utf-8') as add_list:
            added = json.load(add_list)
        branch = system.get_branch()
        for file in added:
            self.checkout(system, branch, file)

    def set_parser(self, subparsers_list) -> None:
        parser = subparsers_list.add_parser('checkout')
        parser.set_defaults(command=Checkout)
        parser.add_argument('branch', help='Branch name')

    def checkout(self, system: System, branch: Branch, file: str) -> None:
        not_found_msg = '{} was not found in branch {}'.format(file,
                                                               branch.name)
        if file not in branch.source.keys():
            raise CVSError(Checkout, not_found_msg)
        last_version = None
        for rev in branch.revisions:
            for diff in rev.diffs:
                if diff.file == file:
                    last_version = diff
                    break
        if last_version is None:
            raise CVSError(Checkout, not_found_msg)
        if last_version.kind == DiffKind.ADD:
            if not system.arguments['no_disk_changes']:
                with open(file, 'w', encoding='utf-8') as file_writer:
                    file_writer.write(last_version.diff)
            if not system.arguments['ignore_all'] and\
                    not system.arguments['ignore_most']:
                print('{} was checked out from branch {}'
                      .format(file, branch.name))
            if not system.arguments['no_logging'] and\
                    not system.arguments['no_disk_changes']:
                self.update_log(system, branch, file)
        else:
            for source_diff in branch.source[file].diffs:
                if source_diff.file == file:
                    file_lines = source_diff.diff.split('\n')
                    break
            else:
                raise CVSError(Checkout, not_found_msg)
            diff_lines = last_version.diff.split('\n')
            system.restore_file(file_lines, diff_lines)
            with open(file, 'w', encoding='utf-8') as file_writer:
                file_writer.write('\n'.join(file_lines))
            if not system.arguments['ignore_all'] and\
                    not system.arguments['ignore_most']:
                print('{} was checked out from branch {}'
                      .format(file, branch.name))
            if not system.arguments['no_logging'] and\
                    not system.arguments['no_disk_changes']:
                self.update_log(system, branch, file)

    @staticmethod
    def update_log(system: System, branch: Branch, file: str):
        json_message = {
            'Command: ': 'Checkout',
            'Date, time: ': str(datetime.now()),
            'Comment: ': '{} was checked out from branch {}'
                         .format(file, branch.name),
        }
        with open(system.history, encoding='utf-8') as history:
            data = json.load(history)
        data['Contents: '].append(json_message)
        with open(system.history, 'w', encoding='utf-8') as history:
            json.dump(data, history, indent=4)
