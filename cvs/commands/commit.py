from cvs import Branch, Diff, DiffKind, Command, CVSError, Revision, \
    System
from datetime import datetime
from pathlib import Path
import difflib
import json
import uuid


class Commit(Command):
    """
    Commits files to repository.
    """
    def run(self, system: System) -> None:
        try:
            if not Path.exists(system.add_list):
                raise CVSError(Commit, 'None of files had been added')
            branch = system.get_branch()
            revision = Revision(message=system.arguments['message'],
                                diffs=[])
            with open(system.add_list, encoding='utf-8') as files:
                for file in json.load(files):
                    if Path.exists(Path(file)):
                        if file not in branch.source.keys():
                            self.add(file, branch, revision)
                        else:
                            self.change(system, file, branch, revision)
                    elif file in branch.source.keys():
                        self.delete(file, revision, system)
            branch.revisions.append(revision)
            self.enforce_commit(branch, system)
            if not system.arguments['ignore_all']:
                last_rev = branch.revisions[-1]
                print('{} files were committed to branch {} (rev {})'
                      .format(len(last_rev.diffs), branch.name, last_rev.id))
        except OSError as err:
            raise CVSError(Commit, str(err.__traceback__))

    def set_parser(self, subparsers_list) -> None:
        parser = subparsers_list.add_parser('commit')
        parser.set_defaults(command=Commit)
        parser.add_argument('-m', '--message', default='',
                            help='Log message')
        parser.add_argument('-b', '--branch', default='master',
                            help='Branch name')

    @staticmethod
    def add(file: str, branch: Branch, revision: Revision) -> None:
        with open(Path(file), encoding='utf-8') as content:
            diff = ''.join(content.readlines())
        diff = Diff(id=uuid.uuid4().hex,
                    kind=DiffKind.ADD, file=file, diff=diff)
        revision.diffs.append(diff)
        branch.source[file] = revision

    def change(self, system: System, file: str, branch: Branch,
               revision: Revision) -> None:
        if not self.is_file_modified(system, branch, file):
            if not system.arguments['ignore_all']:
                print('{} was not committed because it had not been modified'
                      ' since last revision'.format(file))
            return
        original = self.get_original_version(branch, file).diff
        with open(file, encoding='utf-8') as current:
            current_content = ''.join(current.readlines())
        diff_iter = difflib.ndiff(original.split('\n'),
                                  current_content.split('\n'))
        diff_content = ''
        for item in diff_iter:
            diff_content += item
        diff = Diff(id=uuid.uuid4().hex,
                    kind=DiffKind.CHANGE, file=file, diff=diff_content)
        revision.diffs.append(diff)

    def is_file_modified(self, system: System, branch: Branch,
                         file: str) -> bool:
        lines_modified = 0
        last_version = self.get_last_file_version(system, branch, file)
        with open(file, encoding='utf-8') as current:
            current_version = ''.join(current.readlines())
        diff_iter = difflib.ndiff(current_version.split('\n'),
                                  last_version.split('\n'))
        for line in diff_iter:
            if line[0] == '+' or line[0] == '-' or line[0] == '?':
                lines_modified += 1
        return lines_modified > 0

    def get_last_file_version(self, system: System, branch: Branch,
                              file: str) -> str:
        last_diff = self.get_original_version(branch, file)
        original = last_diff.diff.split('\n')
        last_revision = branch.source[file]
        new_versions = branch.revisions[branch.revisions
                                        .index(last_revision)+1:]
        for revision in new_versions:
            for diff in revision.diffs:
                if diff.file == file:
                    last_revision = revision
                    last_diff = diff
        if last_revision == branch.source[file]:
            return '\n'.join(original)
        diff_lines = last_diff.diff.split('\n')
        system.restore_file(original, diff_lines)
        return '\n'.join(original)

    @staticmethod
    def get_original_version(branch: Branch, file: str) -> Diff:
        last_revision = branch.source[file]
        for diff in last_revision.diffs:
            if diff.file == file:
                last_diff = diff
                break
        else:
            raise CVSError(Commit, 'No source fo file {} found'.format(file))
        return last_diff

    @staticmethod
    def delete(file: str, revision: Revision, system: System) -> None:
        with open(system.add_list, encoding='utf-8') as add_list:
            added = json.load(add_list)
        added.remove(file)
        with open(system.add_list, 'w', encoding='utf-8') as add_list:
            json.dump(added, add_list, indent=4)
        change = Diff(id=uuid.uuid4().hex,
                      kind=DiffKind.DELETE, file=file, diff=None)
        revision.diffs.append(change)

    def enforce_commit(self, branch: Branch, system: System) -> None:
        revisions = []
        for rev in branch.revisions:
            revisions.append(rev.id)
        source = {}
        for item in branch.source:
            source[item] = branch.source[item].id
        if not system.arguments['no_disk_changes']:
            with open('{}/{}.json'.format(system.branches, branch.name),
                      'w', encoding='utf-8') as branch_file:
                content = {
                    'Name: ': branch.name,
                    'Revisions: ': revisions,
                    'Source: ': source
                }
                json.dump(content, branch_file, indent=4)
        new_revision = branch.revisions[-1]
        diffs = []
        for diff in new_revision.diffs:
            diffs.append(diff.id)
        if not system.arguments['no_disk_changes']:
            with open('{}/{}.json'.format(system.revisions,
                                          new_revision.id), 'w',
                      encoding='utf-8') as rev_file:
                content = {
                    'ID: ': new_revision.id,
                    'Date, time: ': str(new_revision.timestamp),
                    'Message: ': new_revision.message,
                    'Diffs: ': diffs
                }
                json.dump(content, rev_file, indent=4)
        for diff in new_revision.diffs:
            kind = self.get_kind_str(diff)
            if not system.arguments['no_disk_changes']:
                with open('{}/{}.json'.format(system.diffs,
                                              diff.id), 'w',
                          encoding='utf-8') as diff_file:
                    content = {
                        'ID: ': diff.id,
                        'Kind: ': kind,
                        'File: ': diff.file,
                        'Diff: ': diff.diff
                    }
                    json.dump(content, diff_file, indent=4)
            if not system.arguments['ignore_all'] and\
                    not system.arguments['ignore_most']:
                print('Version of {} was committed to branch {} '
                      '(rev {}, diff {})'.format(diff.file, branch.name,
                                                 new_revision.id, diff.id))
            if not system.arguments['no_disk_changes'] and\
                    not system.arguments['no_logging']:
                self.update_log(system, branch, diff)

    @staticmethod
    def get_kind_str(diff: Diff) -> str:
        if diff.kind == DiffKind.ADD:
            return 'ADD'
        elif diff.kind == DiffKind.DELETE:
            return 'DELETE'
        return 'CHANGE'

    def update_log(self, system: System, branch: Branch, diff: Diff) -> None:
        json_message = {
            'Command: ': 'Commit',
            'Date, time: ': str(datetime.now()),
            'Comment: ': '{} was committed (branch {}, revision {}, diff {},'
                         'kind {})'
                         .format(diff.file, branch.name,
                                 branch.revisions[-1].id, diff.id,
                                 self.get_kind_str(diff)),
            'Message: ': branch.revisions[-1].message
        }
        with open(system.history, encoding='utf-8') as history:
            data = json.load(history)
        data['Contents: '].append(json_message)
        with open(system.history, 'w', encoding='utf-8') as history:
            json.dump(data, history, indent=4)
