from cvs import Branch, Diff, DiffKind, Revision
from pathlib import Path
from typing import Any, Dict, List
import json


class System:
    def __init__(self, arguments: Dict[str, Any]) -> None:
        self.arguments = arguments
        self.directory = arguments['directory']
        self.repository = Path('{}/.repos'.format(self.directory))
        self.history = Path('{}/history.json'.format(self.repository))
        self.branches = Path('{}/branches'.format(self.repository))
        self.diffs = Path('{}/diffs'.format(self.repository))
        self.revisions = Path('{}/revisions'.format(self.repository))
        self.add_list = Path('{}/add_list.json'.format(self.repository))
        self.cvsignore = Path('{}/.cvsignore'.format(self.directory))

    def run(self) -> None:
        self.arguments['command']().run(self)

    def get_branch(self) -> Branch:
        branch_path = Path('{}/{}.json'.format(self.branches,
                                               self.arguments['branch']))
        branch = Branch(name=self.arguments['branch'], revisions=[],
                        source={})
        if Path.exists(branch_path):
            with open(branch_path, encoding='utf-8') as branch_file:
                branch_info = json.load(branch_file)
                for rev in branch_info['Revisions: ']:
                    branch.revisions.append(self.get_revision(rev))
                source = branch_info['Source: ']
                for item in source:
                    for revision in branch.revisions:
                        if source[item] == revision.id:
                            branch.source[item] = revision
        return branch

    def get_revision(self, name: str) -> Revision:
        revision_path = Path('{}/{}.json'.format(self.revisions, name))
        revision = Revision(diffs=[], message='')
        with open(revision_path, encoding='utf-8') as rev_file:
            revision_info = json.load(rev_file)
            revision.message = revision_info['Message: ']
            revision.id = revision_info['ID: ']
            revision.timestamp = revision_info['Date, time: ']
            for item in revision_info['Diffs: ']:
                revision.diffs.append(self.get_diff(item))
        return revision

    def get_diff(self, name: str) -> Diff:
        diff_path = Path('{}/{}.json'.format(self.diffs, name))
        with open(diff_path, encoding='utf-8') as diff_file:
            diff_info = json.load(diff_file)
            return Diff(id=diff_info['ID: '],
                        kind=self.get_diff_kind(diff_info),
                        file=diff_info['File: '],
                        diff=diff_info['Diff: '])

    @staticmethod
    def get_diff_kind(diff_info: dict) -> DiffKind:
        if diff_info['Kind: '] == 'ADD':
            return DiffKind.ADD
        if diff_info['Kind: '] == 'CHANGE':
            return DiffKind.CHANGE
        if diff_info['Kind: '] == 'DELETE':
            return DiffKind.DELETE

    @staticmethod
    def restore_file(file_lines: List[str], diff_lines: List[str]) -> None:
        files_margin = 0
        for i in range(len(diff_lines)):
            if diff_lines[i][0] == '+':
                file_lines.pop(i - files_margin)
                files_margin += 1
            elif diff_lines[i][0] == '-':
                file_lines.insert(i - files_margin, diff_lines[i][2:])
                files_margin += 1
            elif diff_lines[i][0] == '?':
                files_margin += 1
