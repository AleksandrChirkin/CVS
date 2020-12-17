from cvs import Command, CVSError
from pathlib import Path
import json
import logging
import os


class Tag(Command):
    """
    Create a new list or list existing ones
    """
    def run(self) -> None:
        try:
            name = self.arguments['name']
            if name is None:
                for tag in next(os.walk(self.system.tags))[2]:
                    with (self.system.tags/tag)\
                            .open(encoding='utf-8') as tag_file:
                        logging.info(' '.join(json.load(tag_file).values()))
            elif Path(name).exists():
                raise CVSError(f'{name} tag had already been created')
            elif self.arguments['message'] is None:
                with (self.system.tags / f'{name}.json')\
                        .open(encoding='utf-8') as tag_file:
                    logging.info(' '.join(json.load(tag_file).values()))
            else:
                revision = self.arguments['revision']
                if revision is None:
                    revision = next(os.walk(self.system.revisions))[2][-1][:-5]
                elif not (self.system.revisions/f'{revision}.json').exists():
                    raise CVSError(f'Revision {revision} does not exist!')
                if not self.arguments['no_disk_changes']:
                    json_msg = {
                            'Name': name,
                            'Revision': revision,
                            'Message': self.arguments['message']
                        }
                    with (self.system.tags/f'{name}.json')\
                            .open('w', encoding='utf-8') as tag_file:
                        json.dump(json_msg, tag_file, indent=4)
        except Exception as err:
            raise CVSError(str(err))

    def set_parser(self, subparsers_list) -> None:
        parser = subparsers_list.add_parser('tag')
        parser.set_defaults(command=Tag)
        parser.add_argument('-m', '--message', help='Tag message'
                                                    '(without it a tag with'
                                                    ' name would be searched'
                                                    ' and printed')
        parser.add_argument('-rev', '--revision', help='Revision number')
        parser.add_argument('-name', help='Tag name')
