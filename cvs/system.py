from pathlib import Path
from typing import Union


class System:
    def __init__(self, directory: Union[str, Path] = None) -> None:
        self.directory = Path(directory)
        self.repository = self.directory/'.repos'
        self.history = self.repository/'history.json'
        self.branches = self.repository/'branches'
        self.diffs = self.repository/'diffs'
        self.revisions = self.repository/'revisions'
        self.tags = self.repository/'tags'
        self.add_list = self.repository/'add_list.json'
        self.tagged = self.repository/'tagged'
        self.cvsignore = self.directory/'.cvsignore'

    def run(self, **arguments) -> None:
        arguments['command'](self, **arguments).run()

    def is_in_cvsignore(self, file: str) -> bool:
        if not self.cvsignore.exists():
            return False
        with self.cvsignore.open(encoding='utf-8') as cvsignore:
            ignored = cvsignore.readlines()
        for ignored_item in ignored:
            glob = Path(self.directory).glob('**/'+ignored_item.strip())
            for glob_item in glob:
                try:
                    Path(file).relative_to(glob_item)
                except ValueError:
                    continue
                else:
                    return True
        return False

    def set_current_branch(self, branch_name: str) -> None:
        with (self.repository/'HEAD').open('w', encoding='utf-8') as head:
            head.write(branch_name)

    def get_current_branch(self) -> str:
        with (self.repository/'HEAD').open(encoding='utf-8') as head:
            return head.readline()
