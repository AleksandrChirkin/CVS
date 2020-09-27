#!/usr/bin/env python3
from argparse import Namespace
import System
import json
import os
import unittest


class TestCVS(unittest.TestCase):
    def setUp(self):
        System.System(Namespace(command=System.Init, directory=os.getcwd(),
                                no_logging=False, no_disk_changes=False,
                                recreate=True, ignore_all=False,
                                ignore_most=False)).run()

    def test_init(self):
        os.remove('.repos/history.json')
        os.rmdir('.repos/diffs')
        os.rmdir('.repos/revisions')
        os.rmdir('.repos')
        System.System(Namespace(command=System.Init, directory=os.getcwd(),
                                no_logging=False, no_disk_changes=False,
                                recreate=False, ignore_all=False,
                                ignore_most=False)).run()
        self.assertTrue(os.path.exists('.repos/diffs'))
        self.assertTrue(os.path.exists('.repos/revisions'))
        self.assertTrue(os.path.exists('.repos/history.json'))
        with open('.repos/history.json') as history:
            data = json.load(history)
            self.assertEqual(data['Contents: '][0]['Message: '], 'Repository created.')

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
        self.assertFalse(os.path.exists('repos/add_list.cvs'))
        self.assertTrue(os.path.exists
                        ('.repos/revisions/1.0{0}/README.md'
                         .format(os.getcwd())))
        with open('.repos/history.json') as history:
            data = json.load(history)
            self.assertEqual(data['Contents: '][2]['Message: '],
                             '{0}/README.md was committed to revision 1.0.'
                             .format(os.getcwd()))
            self.assertEqual(data['Contents: '][2]['Note: '],
                             'Hello, Python!')


if __name__ == '__main__':
    unittest.main()
