from cvs import Command, CVSError
from datetime import date, datetime
from typing import Tuple
import json
import logging


class Log(Command):
    """
    Prints info about file and catalog history.
    """
    def run(self) -> None:
        try:
            with self.system.history.open(encoding='utf-8') as history:
                log = json.load(history)
            for item in log:
                if self.arguments['branches'] is not None:
                    for branch in self.arguments['branches']:
                        if branch == item['Branch']:
                            break
                    else:
                        continue
                if self.arguments['dates'] is not None and\
                        not self.is_date_in_interval(item["Date, time"]
                                                     [0:10],
                                                     self.arguments
                                                     ['dates']):
                    continue
                if self.arguments['revisions'] is not None:
                    for revision in self.arguments['revisions']:
                        if revision == item['Revision']:
                            break
                    else:
                        continue
                logging.info(' '.join(item.values()))
        except Exception as err:
            raise CVSError(str(err))

    def set_parser(self, subparsers_list) -> None:
        parser = subparsers_list.add_parser('log')
        parser.set_defaults(command=Log)
        parser.add_argument('-branches', nargs='+',
                            help='Branch names')
        parser.add_argument('-dates', help='Time interval')
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
            raise CVSError('Incorrect date or date range format')

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
