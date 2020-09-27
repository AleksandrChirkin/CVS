#!/usr/bin/env python3
from argparse import Namespace
import System
import os
import unittest


class TestCVS(unittest.TestCase):
    def setUp(self):
        System.System(Namespace(command=System.Init, directory=os.getcwd(),
                                no_logging=False, no_disk_changes=False,
                                recreate=True, ignore_all=False,
                                ignore_most=False)).run()

    def test_init(self):
        os.remove('.repos/history.rcs')
        os.rmdir('.repos/diffs')
        os.rmdir('.repos/revisions')
        os.rmdir('.repos')
        System.System(Namespace(command=System.Init, directory=os.getcwd(),
                                no_logging=False, no_disk_changes=False,
                                recreate=False, ignore_all=False,
                                ignore_most=False)).run()
        self.assertTrue(os.path.exists('.repos/diffs'))
        self.assertTrue(os.path.exists('.repos/revisions'))
        self.assertTrue(os.path.exists('.repos/history.rcs'))
        with open('.repos/history.rcs'.format(os.getcwd())) as history:
            self.assertIn('Repository created.', history.readline())

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
        with open('.repos/history.rcs') as history:
            test_cvs_line = history.readlines()[1]
            self.assertIn('{0}/README.md was added. '
                          'Message: Hello, Python!'.format(os.getcwd()),
                          test_cvs_line)

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
        with open('.repos/history.rcs') as history:
            self.assertIn('{0}/README.md was committed to revision 1.0.'
                          ' Message: Hello, Python!'
                          .format(os.getcwd()), history.readlines()[-1])


if __name__ == '__main__':
    unittest.main()
