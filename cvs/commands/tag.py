from cvs import Command, CVSError, System
from pathlib import Path
import os


class Tag(Command):
    def run(self, system: System) -> None:
        name = system.arguments['name']
        if name is None:
            for tag in next(os.walk(system.tags))[2]:
                with open(system.tags/tag) as tag_file:
                    print(tag_file)
        elif Path.exists(Path(name)):
            raise CVSError(Tag, '{} tag had already been created'
                           .format(name))
        else:
            revision = system.arguments['revision']
            if revision is None:
                revision = next(os.walk(system.revisions))[2][-1]
            elif not Path.exists(system.revisions/revision):
                raise CVSError(Tag, 'Revision {} does not exist!'
                               .format(revision))
            with open(system.tags/name, 'w') as tag_file:
                tag_file.write('{} {} {}'.format(name, revision,
                                                 system.arguments['message']))

    def set_parser(self, subparsers_list) -> None:
        parser = subparsers_list.add_parser('tag')
        parser.set_defaults(command=Tag)
        parser.add_argument('-m', '--message', help='Tag message')
        parser.add_argument('-rev', '--revision', help='Revision number')
        parser.add_argument('-name', help='Tag name')
