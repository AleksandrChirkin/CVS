from abc import abstractmethod
from cvs import CVSBranch, CVSError, Diff, DiffKind, Revision, System
from datetime import datetime
from pathlib import Path
from typing import List, Optional
import difflib
import json
import uuid


class Command:
    def __init__(self, system: Optional[System] = None, **arguments):
        self.arguments = arguments
        self.system = system

    @abstractmethod
    def run(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def set_parser(self, subparsers_list) -> None:
        raise NotImplementedError

    def get_branch(self) -> CVSBranch:
        branch_name = self.arguments['branch']
        branch_path = self.system.branches / f'{branch_name}.json'
        branch = CVSBranch(name=self.arguments['branch'], revisions=[],
                           source={})
        if Path.exists(branch_path):
            with branch_path.open(encoding='utf-8') as branch_file:
                branch_info = json.load(branch_file)
                for rev in branch_info['Revisions']:
                    branch.revisions.append(self.get_revision(rev))
                source = branch_info['Source']
                for item in source:
                    for revision in branch.revisions:
                        if source[item] == revision.id:
                            branch.source[item] = revision
        return branch

    def get_revision(self, name: str) -> Revision:
        revision_path = self.system.revisions/f'{name}.json'
        revision = Revision(diffs=[], message='', id=uuid.uuid4().hex,
                            timestamp=datetime.now())
        with revision_path.open(encoding='utf-8') as rev_file:
            revision_info = json.load(rev_file)
            revision.message = revision_info['Message']
            revision.id = revision_info['ID']
            revision.timestamp = revision_info['Date, time']
            for item in revision_info['Diffs']:
                revision.diffs.append(self.get_diff(item))
        return revision

    def get_diff(self, name: str) -> Diff:
        diff_path = self.system.diffs/f'{name}.json'
        with diff_path.open(encoding='utf-8') as diff_file:
            diff_info = json.load(diff_file)
            return Diff(id=diff_info['ID'],
                        kind=self.get_diff_kind(diff_info),
                        file=diff_info['File'],
                        diff=diff_info['Diff'])

    @staticmethod
    def get_diff_kind(diff_info: dict) -> DiffKind:
        if diff_info['Kind'] == 'ADD':
            return DiffKind.ADD
        if diff_info['Kind'] == 'CHANGE':
            return DiffKind.CHANGE
        if diff_info['Kind'] == 'DELETE':
            return DiffKind.DELETE

    def is_file_modified(self, branch: CVSBranch, file: Path) -> bool:
        lines_modified = 0
        last_version = self.get_last_file_version(branch, file)
        with Path(file).open(encoding='utf-8') as current:
            current_version = ''.join(current.readlines())
        diff_iter = difflib.ndiff(current_version.split('\n'),
                                  last_version.split('\n'))
        for line in diff_iter:
            if line[0] == '+' or line[0] == '-' or line[0] == '?':
                lines_modified += 1
        return lines_modified > 0

    def get_last_file_version(self, branch: CVSBranch, file: Path) -> str:
        last_diff = self.get_original_version(branch, file)
        original = last_diff.diff.split('\n')
        relative_path = file.relative_to(self.system.directory)
        last_revision = branch.source[str(relative_path)]
        new_versions = branch.revisions[branch.revisions
                                        .index(last_revision)+1:]
        for revision in new_versions:
            for diff in revision.diffs:
                if diff.file == str(relative_path):
                    last_revision = revision
                    last_diff = diff
        if last_revision == branch.source[str(relative_path)]:
            return '\n'.join(original)
        diff_lines = last_diff.diff.split('\n')
        self.restore_file(original, diff_lines)
        return '\n'.join(original)

    def get_original_version(self, branch: CVSBranch, file: Path) -> Diff:
        relative_path = file.relative_to(self.system.directory)
        source_revision = branch.source[str(relative_path)]
        for diff in source_revision.diffs:
            if diff.file == str(relative_path):
                last_diff = diff
                break
        else:
            raise CVSError(f'No source to file {file} found')
        return last_diff

    @staticmethod
    def restore_file(file_lines: List[str], diff_lines: List[str]) -> None:
        files_margin = 0
        for i in range(len(diff_lines)):
            if len(diff_lines[i]) == 0:
                if len(diff_lines[i-1]) > 0 and diff_lines[i-1][0] == '?':
                    files_margin += 1
                continue
            if diff_lines[i][0] == '+':
                file_lines.insert(i - files_margin, diff_lines[i][2:])
            elif diff_lines[i][0] == '-':
                file_lines.pop(i - files_margin)
                files_margin += 1
            elif diff_lines[i][0] == '?':
                files_margin += 1

    def get_revision_name(self) -> Optional[str]:
        if self.arguments['revision'] is not None:
            return self.arguments['revision']
        elif self.arguments['tag'] is not None:
            return self.get_revision_from_tag(self.arguments['tag']).id
        else:
            return None

    def get_revision_from_tag(self, tag_name: str) -> Revision:
        branch = self.get_branch()
        try:
            with Path(self.system.tags/f'{tag_name}.json')\
                    .open(encoding='utf-8') as tag_file:
                tag_data = json.load(tag_file)
            revision_id = tag_data['Revision']
            for revision in branch.revisions:
                if revision.id == revision_id:
                    return revision
            else:
                raise CVSError(f'Revision {revision_id} was not found!')
        except FileNotFoundError:
            raise CVSError(f'Tag {tag_name} was not found!')
