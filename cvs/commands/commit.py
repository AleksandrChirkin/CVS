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
            if not self.system.add_list.exists():
                raise CVSError("Add list does not exist!")
            branch = self.get_branch()
            revision = Revision(message=self.arguments['message'],
                                diffs=[], id=uuid.uuid4().hex,
                                timestamp=datetime.now())
            with self.system.add_list.open(encoding='utf-8') as add_list:
                added = json.load(add_list)
            for file, tagged in added.items():
                path = self.system.directory / file
                if path.exists():
                    relative_route = path.relative_to(self.system.directory)
                    if str(relative_route) not in branch.source.keys():
                        self.add(relative_route, tagged, branch, revision)
                    else:
                        self.change(path, tagged, branch, revision)
                elif path in branch.source.keys():
                    self.delete(path, revision)
            branch.revisions.append(revision)
            self.enforce_commit(branch)
            for tagged_file in next(os.walk(self.system.tagged))[2]:
                os.remove(self.system.tagged/tagged_file)
            os.rmdir(self.system.tagged)
            if self.system.add_list.exists():
                os.remove(self.system.add_list)
            last_rev = branch.revisions[-1]
            if len(last_rev.diffs) > 0:
                logging.info(f'{len(last_rev.diffs)} files were committed '
                             f'to branch {branch.name} (rev {last_rev.id})')
        except Exception as err:
            raise CVSError(str(err))

    def set_parser(self, subparsers_list) -> None:
        parser = subparsers_list.add_parser('commit')
        parser.set_defaults(command=Commit)
        parser.add_argument('-m', '--message', default='',
                            help='Log message')
        parser.add_argument('-b', '--branch', default='master',
                            help='Branch name')

    def add(self, file: Path, tagged: str, branch: CVSBranch,
            revision: Revision) -> None:
        with (self.system.tagged/tagged).open(encoding='utf-8') as tagged_file:
            diff_text = ''.join(tagged_file.readlines())
        diff = Diff(id=uuid.uuid4().hex, kind=DiffKind.ADD,
                    file=str(file), diff=diff_text)
        revision.diffs.append(diff)
        branch.source[str(file)] = revision

    def change(self, file: Path, tagged: str, branch: CVSBranch,
               revision: Revision) -> None:
        relative_path = file.relative_to(self.system.directory)
        if not self.is_file_modified(branch, file):
            logging.debug(f'{relative_path} was not committed because '
                          'it had not been modified'
                          ' since last revision')
            return
        original = self.get_original_version(branch, file).diff
        with (self.system.tagged/tagged)\
                .open(encoding='utf-8') as tagged_file:
            current_content = ''.join(tagged_file.readlines())
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
                with (self.system.branches / f'{branch.name}.json')\
                        .open('w', encoding='utf-8') as branch_file:
                    content = {
                        'Name': branch.name,
                        'Revisions': revisions,
                        'Source': source
                    }
                    json.dump(content, branch_file, indent=4)
            diffs = []
            for diff in new_revision.diffs:
                diffs.append(diff.id)
            if not self.arguments['no_disk_changes']:
                with (self.system.revisions / f'{new_revision.id}.json')\
                        .open('w', encoding='utf-8') as rev_file:
                    content = {
                        'ID': new_revision.id,
                        'Date, time': str(new_revision.timestamp),
                        'Message': new_revision.message,
                        'Diffs': diffs
                    }
                    json.dump(content, rev_file, indent=4)
            for diff in new_revision.diffs:
                kind = self.get_kind_str(diff)
                if not self.arguments['no_disk_changes']:
                    with (self.system.diffs / f'{diff.id}.json')\
                            .open('w', encoding='utf-8') as diff_file:
                        content = {
                            'ID': diff.id,
                            'Kind': kind,
                            'File': diff.file,
                            'Diff': diff.diff
                        }
                        json.dump(content, diff_file, indent=4)
                logging.info(f'Version of {diff.file} was committed to'
                             f' branch {branch.name} '
                             f'(rev {new_revision.id}, diff {diff.id})')
            if not self.arguments['no_disk_changes']:
                self.update_log(branch)
            self.system.set_current_branch(self.arguments['branch'])

    @staticmethod
    def get_kind_str(diff: Diff) -> str:
        if diff.kind == DiffKind.ADD:
            return 'ADD'
        elif diff.kind == DiffKind.DELETE:
            return 'DELETE'
        return 'CHANGE'

    def update_log(self, branch: CVSBranch) -> None:
        json_message = {
            'Date, time': str(datetime.now()),
            'Revision': branch.revisions[-1].id,
            'Branch': branch.name,
            'Message': self.arguments['message']
        }
        if self.system.history.exists():
            with self.system.history.open(encoding='utf-8') as history:
                data = json.load(history)
        else:
            data = []
        data.append(json_message)
        with self.system.history.open('w', encoding='utf-8') as history:
            json.dump(data, history, indent=4)
