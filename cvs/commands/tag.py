from cvs import Command, EmptyRepositoryError, RevisionDoesNotExistError,\
    TagExistsError, TagDoesNotExistError
from pathlib import Path
import json
import logging
import os


class Tag(Command):
    """
    Create a new list or list existing ones.
    To create tag, you need to enter message
    Without message, CVS would try to open it
    """

    def run(self) -> None:
        if len(next(os.walk(self.system.revisions))[2]) == 0:
            raise EmptyRepositoryError
        name = self.arguments['name']
        if name is None:
            for tag in next(os.walk(self.system.tags))[2]:
                with (self.system.tags / tag) \
                        .open(encoding='utf-8') as tag_file:
                    logging.info(' '.join(json.load(tag_file).values()))
        elif Path(name).exists():
            raise TagExistsError(name)
        elif self.arguments['message'] is None:
            tag_path = self.system.tags / f'{name}.json'
            if not tag_path.exists():
                raise TagDoesNotExistError(name)
            with tag_path.open(encoding='utf-8') as tag_file:
                logging.info(' '.join(json.load(tag_file).values()))
        else:
            revision = self.arguments['revision']
            if revision is None:
                self.arguments['branch'] = self.system.get_current_branch()
                revision = self.get_branch().revisions[-1].id
            elif not (self.system.revisions / f'{revision}.json').exists():
                raise RevisionDoesNotExistError(revision)
            if not self.arguments['no_disk_changes']:
                json_msg = {
                    'Name': name,
                    'Revision': revision,
                    'Message': self.arguments['message']
                }
                with (self.system.tags / f'{name}.json') \
                        .open('w', encoding='utf-8') as tag_file:
                    json.dump(json_msg, tag_file, indent=4)
            logging.info(f'Tag {name} was attached to revision {revision}')

    def set_parser(self, subparsers_list) -> None:
        parser = subparsers_list.add_parser('tag')
        parser.set_defaults(command=Tag)
        parser.add_argument('-m', '--message', help='Tag message'
                                                    '(without it a tag with'
                                                    ' name would be searched'
                                                    ' and printed)')
        parser.add_argument('-rev', '--revision', help='Revision number')
        parser.add_argument('-name', help='Tag name')
