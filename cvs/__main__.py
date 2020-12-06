from argparse import ArgumentParser
from pathlib import Path
from typing import Any, Dict
import logging
import os
import sys
logging.basicConfig(format=u'%(message)s', level=logging.INFO,
                    stream=sys.stdout)
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             os.path.pardir))
from cvs import CVSError, System, COMMANDS  # noqa


def parse_args() -> Dict[str, Any]:
    parser = ArgumentParser(description='Concurrent Versions cvs')
    parser.add_argument('-d', '--directory', default=Path.cwd(),
                        help='Searches repository in other directory')
    parser.add_argument('-l', '--no-logging', action='store_true',
                        help='Executes command without logging it')
    parser.add_argument('-n', '--no-disk-changes', action='store_true',
                        help='Try to execute command without disk changes')
    output_group = parser.add_mutually_exclusive_group()
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
    if 'command' not in space.keys():
        raise CVSError(System, 'No command entered')
    return arguments


if __name__ == '__main__':
    try:
        parsed_args = parse_args()
        System(parsed_args['directory']).run(**parsed_args)
    except Exception as err:
        logging.error(err)
        exit(1)
