from cvs import Command, CVSError
from datetime import datetime
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
        try:
            for file in self.arguments['files']:
                if not Path(file).exists():
                    raise CVSError(Add, '{}/{} does not exist!'
                                   .format(self.system.directory, file))
                elif Path(file).is_dir():
                    for line in os.walk(file):
                        for item in line[2]:
                            self.add(self.system.directory/line[0]/item)
                else:
                    self.add(self.system.directory/file)
        except Exception as err:
            raise CVSError(Add, str(err))

    def set_parser(self, subparsers_list) -> None:
        parser = subparsers_list.add_parser('add')
        parser.set_defaults(command=Add)
        parser.add_argument('-m', '--message', default='',
                            help='Log message')
        parser.add_argument('files', nargs='+', help='Files names')

    def add(self, file: Path) -> None:
        relative_path = file.relative_to(self.system.directory)
        if self.system.is_in_cvsignore(str(file)):
            if not self.arguments['ignore_all']:
                logging.warning('{} was ignored because it is in .cvsignore'
                                .format(relative_path))
        else:
            if self.system.add_list.exists():
                with self.system.add_list.open(encoding='utf-8') as add_list:
                    added = json.load(add_list)
            else:
                added = {}
            for item in added.keys():
                if Path(item) == relative_path:
                    if not self.arguments['ignore_all']:
                        logging.warning('{} had already been added'
                                        .format(relative_path))
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
                if not self.arguments['ignore_all'] and\
                        not self.arguments['ignore_most']:
                    logging.info('{} was added'.format(relative_path))
                if not self.arguments['no_disk_changes'] and\
                        not self.arguments['no_logging']:
                    self.update_log(relative_path)

    def update_log(self, file: Path) -> None:
        json_message = {
            'Command: ': 'Add',
            'Date, time: ': str(datetime.now()),
            'Comment: ': '{} was added to add list.'.format(file),
            'Message: ': self.arguments['message']
        }
        self.put_message_into_log(json_message)
