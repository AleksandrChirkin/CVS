from cvsdomain import Command
from datetime import datetime
import json


class Log(Command):
    """
    Prints info about file and catalog history.
    """
    def run(self, system):
        with open(system.history) as history:
            log = json.load(history)
        for item in log["Contents: "]:
            if system.arguments.dates is not None and\
                    not self.is_date_in_interval(item["Date, time: "][0:10],
                                                 system.arguments.dates):
                continue
            if system.arguments.files is not None:
                for file in system.arguments.files:
                    if file in item["Message: "]:
                        break
                else:
                    continue
            if system.arguments.revisions is not None:
                for revision in system.arguments.revisions:
                    try:
                        if revision not in system.find_all_revisions():
                            raise ValueError('SAS')
                        if revision in item["Message: "]:
                            break
                    except ValueError:
                        print('ERROR: Revision {} does not exist!'
                              .format(revision))
                else:
                    continue
            print(' '.join(item.values()))

    def is_date_in_interval(self, date_str, interval) -> bool:
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
            print('ERROR: Incorrect date or date range format')

    @staticmethod
    def date_span(interval, separator):
        fragments = interval.split(separator)
        if len(fragments) > 2:
            raise ValueError
        for i in range(len(fragments)):
            if fragments[i] == '':
                fragments[i] = '1970-01-01'
        date_one = datetime.strptime(fragments[0], "%Y-%m-%d").date()
        date_two = datetime.strptime(fragments[1], "%Y-%m-%d").date()
        return date_one, date_two
