#!/usr/bin/env python3
from argparse import ArgumentParser
from pathlib import Path
from System import Init, Add, Commit, Reset, Log, System, COMMANDS
import os


def parse_args():
    parser = ArgumentParser(description='Concurrent Versions System')
    parser.add_argument('-d', '--directory', default=Path(os.getcwd()),
                        help='Searches repository in other directory')
    parser.add_argument('-l', '--no_logging', action='store_true',
                        help='Executes command without logging it')
    parser.add_argument('-n', '--no_disk_changes', action='store_true',
                        help='Try to execute command without disk changes')
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument('-Q', '--ignore_all', action='store_true',
                              help='Ignores all messages, except for errors')
    output_group.add_argument('-q', '--ignore_most', action='store_true',
                              help='Ignores some messages')
    subparsers = parser.add_subparsers(title='command')
    for command in COMMANDS:
        if command is System:
            continue
        _parser = subparsers.add_parser(command.__name__.lower(),
                                        help=command.__doc__)
        _parser.set_defaults(command=command)
        if command is Init:
            _parser.add_argument('-r', '--recreate', action='store_true',
                                 help='Recreates repository')
        elif command is Add:
            _parser.add_argument('-m', '--message', default='',
                                 help='Log message')
            _parser.add_argument('files', nargs='+', help='Files names')
        elif command is Commit:
            _parser.add_argument('-m', '--message', default='',
                                 help='Log message')
            _parser.add_argument('-rev', '--revision', help='Revision number')
        elif command is Reset:
            _parser.add_argument('-rev', '--revision', help='Revision number')
            _parser.add_argument('files', nargs='+', help='File name')
        elif command is Log:
            _parser.add_argument('-dates', help='Time interval')
            _parser.add_argument('-files',  nargs='+', help='Files names')
            _parser.add_argument('-rev', '--revisions',
                                 help='Revisions number')
    return parser.parse_args()


if __name__ == '__main__':
    System(parse_args()).run()
