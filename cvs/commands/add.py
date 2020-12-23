from cvs import Command, PathDoesNotExistError
from pathlib import Path
import json
import logging
import os
import shutil
import uuid


class Add(Command):
    """
    Adds a new file to commit list.
    """

    def run(self) -> None:
        for file in self.arguments['files']:
            path = self.system.directory/file
            if not path.exists():
                raise PathDoesNotExistError(path)
            elif path.is_dir():
                for directory, _, items in os.walk(path):
                    for item in items:
                        self.add(Path(directory)/item)
            else:
                self.add(path)

    def set_parser(self, subparsers_list) -> None:
        parser = subparsers_list.add_parser('add')
        parser.set_defaults(command=Add)
        parser.add_argument('files', nargs='+', help='Files names')

    def add(self, file: Path) -> None:
        relative_path = file.relative_to(self.system.directory)
        if self.system.is_in_cvsignore(relative_path):
            logging.debug(f'{relative_path}'
                          f' was ignored because it is in .cvsignore')
        else:
            if self.system.add_list.exists():
                with self.system.add_list.open(encoding='utf-8') as add_list:
                    added = json.load(add_list)
            else:
                added = {}
            for item in added.keys():
                if Path(item) == relative_path:
                    logging.debug(f'{relative_path} had already been added')
                    break
            else:
                tagged_name = uuid.uuid4().hex
                added[str(relative_path).replace('\\', '/')] = tagged_name
                if not self.arguments['no_disk_changes']:
                    if not self.system.tagged.exists():
                        os.mkdir(self.system.tagged)
                    with self.system.add_list\
                            .open('w', encoding='utf-8') as add_list:
                        json.dump(added, add_list, indent=4)
                    shutil.copyfile(file, self.system.tagged/tagged_name)
                logging.info(f'{relative_path} was added')
