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

    def does_repository_exist(self) -> bool:
        return self.repository.exists()

    def run(self, **arguments) -> None:
        arguments['command'](self, **arguments).run()

    def is_in_cvsignore(self, file: Path) -> bool:
        if not self.cvsignore.exists():
            return False
        file_parents = set(parent.name for parent in file.parents
                           if parent != Path('.'))
        file_parents.add(file.name)
        with self.cvsignore.open(encoding='utf-8') as cvsignore:
            for ignored_item in cvsignore:
                ignored_item = Path(ignored_item.strip())
                if str(ignored_item) in file_parents:
                    return True
                try:
                    file.relative_to(ignored_item)
                except ValueError:
                    pass
                else:
                    return True
        return False

    def set_current_branch(self, branch_name: str) -> None:
        with (self.repository/'HEAD').open('w', encoding='utf-8') as head:
            head.write(branch_name)

    def get_current_branch(self) -> str:
        with (self.repository/'HEAD').open(encoding='utf-8') as head:
            return head.readline()
