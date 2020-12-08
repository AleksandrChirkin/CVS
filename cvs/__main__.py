from argparse import ArgumentParser
from pathlib import Path
from typing import Any, Dict
import logging
import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             os.path.pardir))
from cvs import CVSError, Init, System, COMMANDS  # noqa


def parse_args() -> Dict[str, Any]:
    parser = ArgumentParser(description='Concurrent Versions cvs')
    parser.add_argument('-d', '--directory', default=Path.cwd(),
                        help='Searches repository in other directory')
    parser.add_argument('-n', '--no-disk-changes', action='store_true',
                        help='Try to execute command without disk changes')
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument('-a', '--debug', action='store_true',
                              help='Debug mode')
    output_group.add_argument('-Q', '--ignore-all', action='store_true',
                              help='Ignores all messages, except for errors')
    output_group.add_argument('-q', '--ignore-most', action='store_true',
                              help='Ignores some messages')
    subparsers = parser.add_subparsers(title='command')
    for command in COMMANDS:
        command(None).set_parser(subparsers)
    space = parser.parse_args().__dict__
    arguments = {}
    for argument in space:
        if not argument.startswith('__') and not argument.endswith('__'):
            arguments[argument] = space[argument]
    return arguments


def config_logging(args):
    if args['ignore_all']:
        logging.basicConfig(format=u'%(message)s', level=logging.ERROR,
                            stream=sys.stdout)
    elif args['ignore_most']:
        logging.basicConfig(format=u'%(message)s', level=logging.WARNING,
                            stream=sys.stdout)
    elif args['debug']:
        logging.basicConfig(format=u'%(message)s', level=logging.DEBUG,
                            stream=sys.stdout)
    else:
        logging.basicConfig(format=u'%(message)s', level=logging.INFO,
                            stream=sys.stdout)


if __name__ == '__main__':
    try:
        parsed_args = parse_args()
        config_logging(parsed_args)
        if 'command' not in parsed_args.keys():
            raise CVSError("No command entered")
        system = System(parsed_args['directory'])
        if parsed_args['command'] is not Init and\
                not system.does_repository_exist():
            raise CVSError("Repository does not exist! "
                           "To create a repository, use 'init' command")
        system.run(**parsed_args)
    except CVSError as err:
        logging.error(err)
        exit(1)
