from pathlib import Path
from argparse import ArgumentParser
import os
import sys
import tests
import unittest
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             os.path.pardir))
from cvs import Command, Init, System, COMMANDS  # noqa


class TestCVS(unittest.TestCase):
    def setUp(self) -> None:
        self.system = System(Path.cwd())
        self.system.run(no_logging=False, no_disk_changes=False,
                        ignore_all=False, ignore_most=False, command=Init,
                        recreate=Path.exists(Path.cwd() / '.repos'))
        parser = ArgumentParser()
        subparsers = parser.add_subparsers()
        for command in COMMANDS:
            command(self.system).set_parser(subparsers)

    def test_is_in_cvsignore(self) -> None:
        self.assertTrue(self.system.is_in_cvsignore(str(Path.cwd() /
                                                    'cvs/__pycache__')))
        self.assertFalse(self.system.is_in_cvsignore
                         (str(Path.cwd()/'tests/test_cvs.py')))

    def test_get_current_branch(self) -> None:
        tests.make_first_commit()
        self.assertEqual(self.system.get_current_branch(), 'master')


if __name__ == '__main__':
    unittest.main()
