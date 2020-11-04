#!/usr/bin/env python3
from argparse import Namespace
import json
import os
import sys
import unittest
import time
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             os.path.pardir))
import System


class TestCVS(unittest.TestCase):
    def setUp(self):
        self.slash = System.System.get_slash()
        self.levels = os.getcwd().split(self.slash)
        System.System(Namespace(command=System.Init, directory=os.getcwd(),
                                no_logging=False, no_disk_changes=False,
                                recreate=True, ignore_all=False,
                                ignore_most=False)).run()

    def test_init(self):
        os.remove('.repos/history.json')
        os.rmdir('.repos/diffs')
        os.rmdir('.repos/revisions')
        os.rmdir('.repos')
        os.remove('.cvsignore')
        System.System(Namespace(command=System.Init, directory=os.getcwd(),
                                no_logging=False, no_disk_changes=False,
                                recreate=False, ignore_all=False,
                                ignore_most=False)).run()
        self.assertTrue(os.path.exists('.cvsignore'))
        self.assertTrue(os.path.exists('.repos/diffs'))
        self.assertTrue(os.path.exists('.repos/revisions'))
        self.assertTrue(os.path.exists('.repos/history.json'))
        with open('.repos/history.json') as history:
            data = json.load(history)
            self.assertEqual(data['Contents: '][0]['Message: '],
                             'Repository created.')

    def test_add(self):
        System.System(Namespace(command=System.Add, directory=os.getcwd(),
                                files=['README.md'], no_logging=False,
                                message='Hello, Python!',
                                no_disk_changes=False, ignore_all=False,
                                ignore_most=False)).run()
        self.assertTrue(os.path.exists('.repos/add_list.cvs'))
        with open('.repos/add_list.cvs') as add_list:
            self.assertEqual('{0}/README.md->self'.format(os.getcwd()),
                             add_list.readline()[:-1])
        with open('.repos/history.json') as history:
            data = json.load(history)
            self.assertEqual(data['Contents: '][1]['Message: '],
                             '{0}/README.md was added.'.format(os.getcwd()))
            self.assertEqual(data['Contents: '][1]['Note: '],
                             'Hello, Python!')

    def test_commit(self):
        self.make_commit()
        self.assertFalse(os.path.exists('repos/add_list.cvs'))
        self.assertTrue(os.path.exists
                        ('.repos/revisions/1.0/{}/README.md'
                         .format(self.slash.join(self.levels[1:]))))
        with open('.repos/history.json') as history:
            data = json.load(history)
            self.assertEqual(data['Contents: '][2]['Message: '],
                             '{0}/README.md was committed to revision 1.0.'
                             .format(os.getcwd()))
            self.assertEqual(data['Contents: '][2]['Note: '],
                             'Hello, Python!')

    def test_reset(self):
        self.make_commit()
        start_time = int(time.time())
        System.System(Namespace(command=System.Reset, directory=os.getcwd(),
                                files=['README.md'], no_logging=False,
                                no_disk_changes=False, revision='1.0',
                                ignore_all=False, ignore_most=False)).run()
        with open('README.md') as file,\
                open('.repos/revisions/1.0/{}/README.md'
                     .format(self.slash.join(self.levels[1:]))) as version:
            self.assertEqual(file.readlines(), version.readlines())
        self.assertLessEqual(start_time, os.path.getmtime('README.md'))
        with open('.repos/history.json') as history:
            data = json.load(history)
            self.assertEqual(data['Contents: '][3]['Message: '],
                             '{0}/README.md was reset from revision 1.0.'
                             .format(os.getcwd()))

    @staticmethod
    def make_commit():
        System.System(Namespace(command=System.Add, directory=os.getcwd(),
                                files=['README.md'], no_logging=False,
                                message='Hello, Python!',
                                no_disk_changes=False, ignore_all=False,
                                ignore_most=False)).run()
        System.System(Namespace(command=System.Commit, directory=os.getcwd(),
                                no_logging=False,
                                message='Hello, Python!',
                                no_disk_changes=False,
                                revision='1.0', ignore_all=False,
                                ignore_most=False)).run()


if __name__ == '__main__':
    unittest.main()
