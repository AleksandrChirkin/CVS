from argparse import ArgumentParser
from pathlib import Path
from typing import Any, Dict
import json
import os
import sys
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
        command().set_parser(subparsers)
    space = parser.parse_args().__dict__
    arguments = {}
    for argument in space:
        if argument[0] != '_':
            arguments[argument] = space[argument]
    return arguments


if __name__ == '__main__':
    try:
        System(parse_args()).run()
    except CVSError as err:
        try:
            print('FAILED: CVS Error occurred during execution')
            error_log = Path('{}/.repos/errorlog.json'.format(Path.cwd()))
            with open(error_log, encoding='utf-8') as log:
                errors = json.load(log)
            exc_message = {
                'Class': err.command,
                'Message': err.txt
            }
            errors['Errors List: '].append(exc_message)
            with open(error_log, 'w', encoding='utf-8') as log:
                json.dump(errors, log, indent=4)
            print('You can investigate exception in error log in repository')
        finally:
            exit(1)
