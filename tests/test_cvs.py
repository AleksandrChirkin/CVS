from argparse import Namespace
from datetime import date
from pathlib import Path
import json
import os
import sys
import unittest
import time

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             os.path.pardir))
from cvs import Init, Add, Commit, Reset, Log, System  # noqa


class TestCVS(unittest.TestCase):
    def setUp(self) -> None:
        self.slash = System.get_slash()
        self.levels = os.getcwd().split(self.slash)
        if os.path.exists('.repos'):
            System(Namespace(command=Init, directory=os.getcwd(),
                             no_logging=False, no_disk_changes=False,
                             recreate=True, ignore_all=False,
                             ignore_most=False)).run()
        else:
            System(Namespace(command=Init, directory=os.getcwd(),
                             no_logging=False, no_disk_changes=False,
                             recreate=False, ignore_all=False,
                             ignore_most=False)).run()

    def test_init(self) -> None:
        if os.path.exists('.repos'):
            os.remove(Path('.repos/history.json'))
            os.rmdir(Path('.repos/diffs'))
            os.rmdir(Path('.repos/revisions'))
            os.rmdir('.repos')
        if os.path.exists('.cvsignore'):
            os.remove('.cvsignore')
        System(Namespace(command=Init, directory=os.getcwd(),
                         no_logging=False, no_disk_changes=False,
                         recreate=False, ignore_all=False,
                         ignore_most=False)).run()
        self.assertTrue(os.path.exists('.cvsignore'))
        self.assertTrue(os.path.exists(Path('.repos/diffs')))
        self.assertTrue(os.path.exists(Path('.repos/revisions')))
        self.assertTrue(os.path.exists(Path('.repos/history.json')))
        with open(Path('.repos/history.json')) as history:
            data = json.load(history)
            self.assertEqual(data['Contents: '][0]['Message: '],
                             'Repository created.')

    def test_add(self) -> None:
        System(Namespace(command=Add, directory=os.getcwd(),
                         files=['README.md'], no_logging=False,
                         message='Hello, Python!',
                         no_disk_changes=False, ignore_all=False,
                         ignore_most=False)).run()
        self.assertTrue(os.path.exists(Path('.repos/add_list.cvs')))
        with open(Path('.repos/add_list.cvs')) as add_list:
            self.assertEqual('{}/README.md->self'.format(os.getcwd()),
                             add_list.readline()[:-1])
        with open(Path('.repos/history.json')) as history:
            data = json.load(history)
            self.assertEqual(data['Contents: '][1]['Message: '],
                             '{0}/README.md was added.'.format(os.getcwd()))
            self.assertEqual(data['Contents: '][1]['Note: '],
                             'Hello, Python!')

    def test_first_commit(self) -> None:
        self.make_commit('1.0')
        self.assertFalse(os.path.exists(Path('repos/add_list.cvs')))
        self.assertTrue(os.path.exists
                        (Path('.repos/revisions/1.0/{}/README.md'
                              .format(self.slash.join(self.levels[1:])))))
        with open(Path('.repos/history.json')) as history:
            data = json.load(history)
            self.assertEqual(data['Contents: '][2]['Message: '],
                             '{}/README.md was committed to revision 1.0.'
                             .format(os.getcwd()))
            self.assertEqual(data['Contents: '][2]['Note: '],
                             'Hello, Python!')

    def test_non_first_commit(self) -> None:
        self.make_commit('1.0')
        with open('README.md', 'a') as readme:
            readme.write(' ')
        self.make_commit('1.1')
        revisions = next(os.walk('.repos/revisions'))
        self.assertEqual(len(revisions[1]), 2)

    def test_reset(self) -> None:
        self.make_commit('1.0')
        start_time = int(time.time())
        System(Namespace(command=Reset, directory=os.getcwd(),
                         files=['README.md'], no_logging=False,
                         no_disk_changes=False, revision=None,
                         ignore_all=False, ignore_most=False)).run()
        with open('README.md') as file,\
                open(Path('.repos/revisions/1.0/{}/README.md'
                     .format(self.slash.join(self.levels[1:])))) as version:
            self.assertEqual(file.readlines(), version.readlines())
        self.assertLessEqual(start_time, os.path.getmtime('README.md'))
        with open(Path('.repos/history.json')) as history:
            data = json.load(history)
            self.assertEqual(data['Contents: '][3]['Message: '],
                             '{}/README.md was reset from revision 1.0.'
                             .format(os.getcwd()))

    def test_correct_log(self) -> None:
        self.make_commit('1.0')
        System(Namespace(command=Log, dates='<={}'.format(date.today()),
                         directory=os.getcwd(), files=['README.md'],
                         no_logging=False, no_disk_changes=False,
                         revisions=['1.0'], ignore_all=False,
                         ignore_most=False)).run()
        System(Namespace(command=Log, dates=str(date.today()),
                         directory=os.getcwd(), files=['README.md'],
                         no_logging=False, no_disk_changes=False,
                         revisions=['1.0'], ignore_all=False,
                         ignore_most=False)).run()
        exc_type, value, traceback = sys.exc_info()
        self.assertIsNone(exc_type)

    def test_incorrect_log(self) -> None:
        self.make_commit('1.0')
        System(Namespace(command=Log,
                         dates='{}>=notadate'.format(date.today()),
                         directory=os.getcwd(), files=['README.md'],
                         no_logging=False, no_disk_changes=False,
                         revisions=['1.0'], ignore_all=False,
                         ignore_most=False)).run()
        self.assertRaises(ValueError)

    @staticmethod
    def make_commit(revision: str) -> None:
        System(Namespace(command=Add, directory=os.getcwd(),
                         files=['README.md'], no_logging=False,
                         message='Hello, Python!',
                         no_disk_changes=False, ignore_all=False,
                         ignore_most=False)).run()
        System(Namespace(command=Commit, directory=os.getcwd(),
                         no_logging=False, message='Hello, Python!',
                         no_disk_changes=False,
                         revision=revision, ignore_all=False,
                         ignore_most=False)).run()

    def tearDown(self) -> None:
        with open('README.md', 'r+') as readme:
            lines = readme.readlines()
            if lines[-1] == ' ':
                end = readme.seek(0, 2)
                readme.seek(0, 1)
                readme.truncate(end - 1)


if __name__ == '__main__':
    unittest.main()
