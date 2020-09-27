from System import Command
from datetime import date


class Log(Command):
    """
    Prints info about file and catalog history.
    """
    def run(self, full_request):
        if full_request.files is None:
            self.log(full_request)
        else:
            for file in full_request.files:
                self.log(full_request, '{0}/{1}'.format(full_request.d, file))

    def log(self, full_request, file=None):
        revisions = self.find_all_relevant_revisions(full_request)
        with open('{0}/repos/history.rcs'.format(full_request.d)) as history:
            for line in history.readlines():
                line_date = line[:10]
                if full_request.dates is not None and\
                        not self.is_date_in_interval(line_date,
                                                     full_request.dates) or\
                        full_request.rev is not None and\
                        line[line.find('Revision: ')+10:
                             line.find('Note: ')-1] not in revisions or\
                        file is not None and file not in line:
                    continue
                print(line[:-1])

    def find_all_relevant_revisions(self, full_request):
        revisions = self.find_all_revisions(full_request)
        if full_request.rev is None:
            return revisions
        interval = full_request.rev.split(':')
        if len(interval) == 1:
            if self.is_revision_correct(interval[0]):
                return interval[0]
            print('ERROR: Entered revision is invalid!')
        elif len(interval) == 2:
            if interval[0] == '':
                interval[0] = revisions[0]
            if interval[1] == '':
                interval[1] = revisions[-1]
            if not self.is_revision_correct(interval[0]) or \
                    not self.is_revision_correct(interval[1]):
                print('ERROR: At least one of entered revisions is invalid!')
            else:
                return revisions[revisions.index(interval[0]):
                                 revisions.index(interval[1])+1]
        else:
            print('ERROR: Incorrectly entered revisions interval!')

    def is_date_in_interval(self, date_str, interval) -> bool:
        try:
            if '<' not in interval and '=' not in interval and '>' not in interval:
                return date_str in interval[1:-1].split(';')
            date_item = date(int(date_str[:4]), int(date_str[5:7]),
                             int(date_str[8:]))
            if '<=' in interval:
                time_span = self.date_span(interval, '<=')
                return time_span[0] <= date_item <= time_span[1]
            if '>=' in interval:
                time_span = self.date_span(interval, '>=')
                return time_span[1] <= date_item <= time_span[0]
            if '<' in interval:
                time_span = self.date_span(interval, '<')
                return time_span[0] < date_item < time_span[1]
            if '>' in interval:
                time_span = self.date_span(interval, '>')
                return time_span[1] < date_item < time_span[0]
        except TypeError:
            print('ERROR: Incorrect date or dates interval format!')
        except ValueError:
            print('ERROR: Incorrect date format')

    @staticmethod
    def date_span(interval, separator):
        fragments = interval.split(separator)
        if len(fragments) > 2:
            return None
        for i in range(len(fragments)):
            if fragments[i] == '':
                fragments[i] = '1970-01-01'
        return (date(int(fragments[0][:4]), int(fragments[0][5:7]),
                     int(fragments[0][8:10])),
                date(int(fragments[1][:4]), int(fragments[1][5:7]),
                     int(fragments[1][8:10])))
