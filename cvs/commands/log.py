from cvs import Command, CVSError, System
from datetime import date, datetime
from typing import Tuple
import json
import os


class Log(Command):
    """
    Prints info about file and catalog history.
    """
    def run(self, system: System) -> None:
        with open(system.history, encoding='utf-8') as history:
            log = json.load(history)
        for item in log["Contents: "]:
            if system.arguments['branches'] is not None:
                for branch in system.arguments['branches']:
                    if '{}.json'.format(branch) not\
                            in next(os.walk(system.branches))[2]:
                        raise CVSError(Log,
                                       'ERROR: Branch {} does not exist!'
                                       .format(branch))
                    if branch in item["Comment: "]:
                        break
                else:
                    continue
            if system.arguments['dates'] is not None and\
                    not self.is_date_in_interval(item["Date, time: "][0:10],
                                                 system.arguments['dates']):
                continue
            if system.arguments['files'] is not None:
                for file in system.arguments['files']:
                    if file in item["Comment: "]:
                        break
                else:
                    continue
            if system.arguments['revisions'] is not None:
                for revision in system.arguments['revisions']:
                    if '{}.json'.format(revision) not\
                            in next(os.walk(system.revisions))[2]:
                        raise CVSError(Log,
                                       'ERROR: Revision {} does not exist!'
                                       .format(revision))
                    if revision in item["Comment: "]:
                        break
                else:
                    continue
            print(' '.join(item.values()))

    def set_parser(self, subparsers_list) -> None:
        parser = subparsers_list.add_parser('log')
        parser.set_defaults(command=Log)
        parser.add_argument('-branches', nargs='+',
                            help='Branch names')
        parser.add_argument('-dates', help='Time interval')
        parser.add_argument('-files', nargs='+', help='Files names')
        parser.add_argument('-revisions', nargs='+',
                            help='Revisions numbers')

    def is_date_in_interval(self, date_str: str, interval: str) -> bool:
        try:
            if '<' not in interval and '=' not in interval and\
                    '>' not in interval:
                return date_str in interval.split(';')
            date_item = datetime.strptime(date_str, "%Y-%m-%d").date()
            if '<=' in interval:
                time_span = self.date_span(interval, '<=')
                return time_span[0] <= date_item <= time_span[1]
            if '>=' in interval:
                time_span = self.date_span(interval, '>=')
                return time_span[0] >= date_item >= time_span[1]
            if '<' in interval:
                time_span = self.date_span(interval, '<')
                return time_span[0] < date_item < time_span[1]
            if '>' in interval:
                time_span = self.date_span(interval, '>')
                return time_span[0] > date_item > time_span[1]
        except ValueError:
            raise CVSError(Log, 'ERROR: Incorrect date or date range format')

    @staticmethod
    def date_span(interval: str, separator: str) -> Tuple[date, date]:
        fragments = interval.split(separator)
        if len(fragments) > 2:
            raise ValueError
        for i in range(len(fragments)):
            if fragments[i] == '':
                fragments[i] = '1970-01-01'
        date_one = datetime.strptime(fragments[0], "%Y-%m-%d").date()
        date_two = datetime.strptime(fragments[1], "%Y-%m-%d").date()
        return date_one, date_two
