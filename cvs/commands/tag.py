from cvs import Command, CVSError
from datetime import datetime
from pathlib import Path
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
                    with (self.system.tags/tag).open() as tag_file:
                        logging.info(tag_file)
            elif Path.exists(Path(name)):
                raise CVSError(Tag, '{} tag had already been created'
                                    .format(name))
            else:
                revision = self.arguments['revision']
                if revision is None:
                    revision = next(os.walk(self.system.revisions))[2][-1]
                elif not Path.exists(self.system.revisions/revision):
                    raise CVSError(Tag, 'Revision {} does not exist!'
                                        .format(revision))
                with (self.system.tags/name).open('w',
                                                  encoding='utf-8') \
                        as tag_file:
                    tag_file.write('{} {} {}'.format(name, revision,
                                                     self.arguments
                                                     ['message']))
                self.update_log()
        except Exception as err:
            raise CVSError(Tag, str(err))

    def set_parser(self, subparsers_list) -> None:
        parser = subparsers_list.add_parser('tag')
        parser.set_defaults(command=Tag)
        parser.add_argument('-m', '--message', help='Tag message')
        parser.add_argument('-rev', '--revision', help='Revision number')
        parser.add_argument('-name', help='Tag name')

    def update_log(self) -> None:
        json_message = {
            'Command: ': 'Tag',
            'Date, time: ': str(datetime.now()),
            'Comment: ': '{} tag was added to rev {}'
                         .format(self.arguments['name'],
                                 self.arguments['revision']),
            'Message': self.arguments['message']
        }
        self.put_message_into_log(json_message)
