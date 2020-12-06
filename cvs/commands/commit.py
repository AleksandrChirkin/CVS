from cvs import CVSBranch, Diff, DiffKind, Command, CVSError, Revision
from datetime import datetime
from pathlib import Path
import difflib
import json
import logging
import os
import uuid


class Commit(Command):
    """
    Commits files to repository.
    """
    def run(self) -> None:
        try:
            branch = self.get_branch()
            revision = Revision(message=self.arguments['message'],
                                diffs=[], id=uuid.uuid4().hex,
                                timestamp=datetime.now())
            for item in os.walk(self.system.directory):
                for route in item[2]:
                    file = Path(item[0])/route
                    if self.system.is_in_cvsignore(str(file)):
                        continue
                    if file.exists():
                        relative_route = file.relative_to(self.system.
                                                          directory)
                        if str(relative_route) not in branch.source.keys():
                            self.add(file, branch, revision)
                        else:
                            self.change(file, branch, revision)
                    elif file in branch.source.keys():
                        self.delete(file, revision)
            branch.revisions.append(revision)
            self.enforce_commit(branch)
            if self.system.tagged.exists():
                for tagged_file in next(os.walk(self.system.tagged))[2]:
                    os.remove(self.system.tagged/tagged_file)
                os.rmdir(self.system.tagged)
            if self.system.add_list.exists():
                os.remove(self.system.add_list)
            last_rev = branch.revisions[-1]
            if len(last_rev.diffs) > 0:
                if not self.arguments['ignore_all']:
                    logging.info('{} files were committed to branch {} '
                                 '(rev {})'.format(len(last_rev.diffs),
                                                   branch.name, last_rev.id))
        except Exception as err:
            raise CVSError(Commit, str(err))

    def set_parser(self, subparsers_list) -> None:
        parser = subparsers_list.add_parser('commit')
        parser.set_defaults(command=Commit)
        parser.add_argument('-m', '--message', default='',
                            help='Log message')
        parser.add_argument('-b', '--branch', default='master',
                            help='Branch name')

    def add(self, file: Path, branch: CVSBranch, revision: Revision) -> None:
        relative_path = file.relative_to(self.system.directory)
        if self.system.add_list.exists():
            with self.system.add_list.open(encoding='utf-8') as add_list:
                added = json.load(add_list)
        else:
            added = {}
        if str(relative_path) in added.keys():
            with Path(self.system.tagged/added[str(relative_path)])\
                    .open(encoding='utf-8') as tagged:
                diff_text = ''.join(tagged.readlines())
        else:
            with file.open(encoding='utf-8') as content:
                diff_text = ''.join(content.readlines())
        diff = Diff(id=uuid.uuid4().hex, kind=DiffKind.ADD,
                    file=str(relative_path), diff=diff_text)
        revision.diffs.append(diff)
        branch.source[str(relative_path)] = revision

    def change(self, file: Path, branch: CVSBranch,
               revision: Revision) -> None:
        relative_path = file.relative_to(self.system.directory)
        if not self.is_file_modified(branch, file):
            if not self.arguments['ignore_all']:
                logging.warning('{} was not committed because '
                                'it had not been modified'
                                ' since last revision'.format(relative_path))
            return
        original = self.get_original_version(branch, file).diff
        if self.system.add_list.exists():
            with self.system.add_list.open(encoding='utf-8') as add_list:
                added = json.load(add_list)
        else:
            added = {}
        if str(relative_path) in added.keys():
            with Path(self.system.tagged/added[str(relative_path)])\
                    .open(encoding='utf-8') as tagged:
                current_content = ''.join(tagged.readlines())
        else:
            with Path(file).open(encoding='utf-8') as current:
                current_content = ''.join(current.readlines())
        diff_iter = difflib.ndiff(original.split('\n'),
                                  current_content.split('\n'))
        diff_content = ''
        for item in diff_iter:
            diff_content += item+'\n'
        diff = Diff(id=uuid.uuid4().hex, kind=DiffKind.CHANGE,
                    file=str(relative_path), diff=diff_content.strip())
        revision.diffs.append(diff)

    def delete(self, file: Path, revision: Revision) -> None:
        relative_path = file.relative_to(self.system.directory)
        change = Diff(id=uuid.uuid4().hex, kind=DiffKind.DELETE,
                      file=str(relative_path), diff=None)
        revision.diffs.append(change)

    def enforce_commit(self, branch: CVSBranch) -> None:
        revisions = []
        for rev in branch.revisions:
            revisions.append(rev.id)
        source = {}
        for item in branch.source:
            source[item] = branch.source[item].id
        new_revision = branch.revisions[-1]
        if len(new_revision.diffs) > 0:
            if not self.arguments['no_disk_changes']:
                with (self.system.branches / '{}.json'.format(branch.name))\
                        .open('w', encoding='utf-8') as branch_file:
                    content = {
                        'Name: ': branch.name,
                        'Revisions: ': revisions,
                        'Source: ': source
                    }
                    json.dump(content, branch_file, indent=4)
            diffs = []
            for diff in new_revision.diffs:
                diffs.append(diff.id)
            if not self.arguments['no_disk_changes']:
                with (self.system.revisions / '{}.json'
                        .format(new_revision.id))\
                        .open('w', encoding='utf-8') as rev_file:
                    content = {
                        'ID: ': new_revision.id,
                        'Date, time: ': str(new_revision.timestamp),
                        'Message: ': new_revision.message,
                        'Diffs: ': diffs
                    }
                    json.dump(content, rev_file, indent=4)
            for diff in new_revision.diffs:
                kind = self.get_kind_str(diff)
                if not self.arguments['no_disk_changes']:
                    with (self.system.diffs / '{}.json'.format(diff.id))\
                            .open('w', encoding='utf-8') as diff_file:
                        content = {
                            'ID: ': diff.id,
                            'Kind: ': kind,
                            'File: ': diff.file,
                            'Diff: ': diff.diff
                        }
                        json.dump(content, diff_file, indent=4)
                if not self.arguments['ignore_all'] and \
                        not self.arguments['ignore_most']:
                    logging.info('Version of {} was committed to branch {} '
                                 '(rev {}, diff {})'.format(diff.file,
                                                            branch.name,
                                                            new_revision.id,
                                                            diff.id))
                if not self.arguments['no_disk_changes'] and\
                        not self.arguments['no_logging']:
                    self.update_log(branch, diff)
            self.system.set_current_branch(self.arguments['branch'])

    @staticmethod
    def get_kind_str(diff: Diff) -> str:
        if diff.kind == DiffKind.ADD:
            return 'ADD'
        elif diff.kind == DiffKind.DELETE:
            return 'DELETE'
        return 'CHANGE'

    def update_log(self, branch: CVSBranch, diff: Diff) -> None:
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
        self.put_message_into_log(json_message)
