from pathlib import Path
from argparse import ArgumentParser
import json
import os
import sys
import tests
import unittest
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             os.path.pardir))
from cvs import Init, System, COMMANDS  # noqa


class TestCVS(unittest.TestCase):
    def setUp(self) -> None:
        self.system = System({
            'directory': Path.cwd(),
            'no_logging': False,
            'no_disk_changes': False,
            'ignore_all': False,
            'ignore_most': False,
            'command': Init,
            'recreate': Path.exists(Path.cwd() / '.repos')
        })
        self.system.run()
        parser = ArgumentParser()
        subparsers = parser.add_subparsers()
        for command in COMMANDS:
            command().set_parser(subparsers)

    def test_is_in_cvsignore(self) -> None:
        self.assertTrue(self.system.is_in_cvsignore('.gitignore'))
        self.assertFalse(self.system.is_in_cvsignore
                         (str(Path.cwd()/'tests/test_cvs.py')))

    def test_get_branch(self) -> None:
        system = tests.make_first_commit()
        branch = system.get_branch()
        self.assertTrue(branch.name, 'master')
        self.assertEqual(len(branch.revisions), 1)
        revision = branch.revisions[0]
        with open(system.add_list) as add_list:
            self.assertEqual(len(revision.diffs), len(json.load(add_list)))


if __name__ == '__main__':
    unittest.main()
