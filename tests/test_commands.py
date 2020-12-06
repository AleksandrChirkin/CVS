from datetime import date
from pathlib import Path
import json
import os
import sys
import tests
import unittest

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             os.path.pardir))
from cvs import Init, Commit, Reset, Log, Checkout, Tag, Branch, Status,\
    System, COMMANDS  # noqa


class TestCommands(unittest.TestCase):
    def setUp(self) -> None:
        System(Path.cwd()).run(no_logging=False, no_disk_changes=False,
                               ignore_all=False, ignore_most=False,
                               command=Init,
                               recreate=(Path.cwd() / '.repos').exists())
        with Path('tests/test_file.txt') \
                .open('w', encoding='utf-8') as test_file:
            test_file.write('I\'m temp file!')

    def test_init(self) -> None:
        for item in os.walk(Path.cwd() / '.repos', False):
            for file in item[2]:
                os.remove(Path(item[0]) / file)
            for directory in item[1]:
                os.rmdir(Path(item[0]) / directory)
        os.remove(Path.cwd() / '.cvsignore')
        os.rmdir(Path.cwd() / '.repos')
        system = System(Path.cwd())
        system.run(no_logging=False, no_disk_changes=False,
                   ignore_all=False, ignore_most=False, command=Init,
                   recreate=False)
        self.assertTrue(system.repository.exists())
        self.assertTrue(system.cvsignore.exists())
        self.assertTrue(system.history.exists())
        self.assertTrue(system.branches.exists())
        self.assertTrue(system.diffs.exists())
        self.assertTrue(system.revisions.exists())

    def test_add(self) -> None:
        system = tests.add_files()
        self.assertTrue(system.add_list.exists())
        self.assertTrue(system.tagged.exists())
        with system.add_list.open(encoding='utf-8') as add_list:
            added = json.load(add_list)
        for item in os.walk(Path.cwd() / 'cvs'):
            for file in item[2]:
                full_path = Path(item[0]) / file
                if not system.is_in_cvsignore(str(full_path)):
                    relative_path = str(full_path.relative_to(Path.cwd()))
                    self.assertIn(relative_path, added.keys())
                    self.assertTrue((system.tagged / added[relative_path])
                                    .exists())

    def test_first_commit(self) -> None:
        system = tests.make_first_commit()
        self.assertEqual(len(next(os.walk(system.branches))[2]), 1)
        self.assertTrue((system.branches / 'master.json').exists())
        self.assertEqual(len(next(os.walk(system.revisions))[2]), 1)
        self.assertFalse(system.add_list.exists())
        self.assertFalse(system.tagged.exists())

    def test_new_commit_to_existing_branch(self) -> None:
        system = tests.make_first_commit()
        with Path('tests/test_file.txt').open('a', encoding='utf-8') as readme:
            readme.write(' ')
        system.run(no_logging=False, no_disk_changes=False,
                   ignore_all=False, ignore_most=False,
                   command=Commit, branch='master',
                   message='Committing README')
        self.assertEqual(len(next(os.walk(system.branches))[2]), 1)
        self.assertEqual(len(next(os.walk(system.revisions))[2]), 2)
        self.assertFalse(system.add_list.exists())
        self.assertFalse(system.tagged.exists())

    def test_committing_new_file(self):
        tests.make_first_commit()
        with Path('tests/test_file2.txt') \
                .open('w', encoding='utf-8') as test_file:
            test_file.write('I\'m temp file!')
        system = tests.make_first_commit()
        self.assertEqual(len(next(os.walk(system.revisions))[2]), 2)
        self.assertFalse(system.add_list.exists())
        self.assertFalse(system.tagged.exists())

    def test_commit_to_new_branch(self) -> None:
        system = tests.make_first_commit()
        system.run(no_logging=False, no_disk_changes=False, ignore_all=False,
                   ignore_most=False, command=Commit, branch='test',
                   message='Creating test branch')
        self.assertEqual(len(next(os.walk(system.branches))[2]), 2)
        self.assertTrue((system.branches / 'test.json').exists())
        self.assertEqual(len(next(os.walk(system.revisions))[2]), 2)
        self.assertFalse(system.add_list.exists())
        self.assertFalse(system.tagged.exists())

    def test_reset(self) -> None:
        system = tests.make_first_commit()
        with Path('tests/test_file.txt') \
                .open('r+', encoding='utf-8') as readme:
            readme_content = ''.join(readme.readlines())
            readme.write(' ')
        system.run(no_logging=False, no_disk_changes=False, ignore_all=False,
                   ignore_most=False, command=Reset, branch='master',
                   files=['tests/test_file.txt'],
                   revision=next(os.walk(system.revisions))[2][-1][:-5])
        with Path('tests/test_file.txt').open(encoding='utf-8') as readme:
            self.assertEqual(''.join(readme.readlines()), readme_content)

    def test_log(self) -> None:
        system = tests.make_first_commit()
        system.run(no_logging=False, no_disk_changes=False, ignore_all=False,
                   ignore_most=False, command=Log, branches=['master'],
                   dates=str(date.today()), files=['README.md'],
                   revisions=[next(os.walk(Path.cwd() / '.repos/revisions'))
                              [2][-1][:-5]])
        system.run(no_logging=False, no_disk_changes=False, ignore_all=False,
                   ignore_most=False, command=Log, branches=['master'],
                   dates='{0}>{0}'.format(date.today()),
                   files=['README.md'],
                   revisions=[next(os.walk(Path.cwd() /
                                           '.repos/revisions'))
                              [2][-1]])
        exc_type, value, traceback = sys.exc_info()
        self.assertIsNone(exc_type)

    def test_log_with_defaults(self) -> None:
        system = tests.make_first_commit()
        system.run(no_logging=False, no_disk_changes=False,
                   ignore_all=False, ignore_most=False,
                   command=Log, branches=None, dates=None,
                   files=None, revisions=None)
        exc_type, value, traceback = sys.exc_info()
        self.assertIsNone(exc_type)

    def test_checkout(self) -> None:
        system = tests.make_first_commit()
        with Path('tests/test_file.txt') \
                .open('r+', encoding='utf-8') as test_file:
            test_content = ''.join(test_file.readlines())
            test_file.write(' ')
        system.run(no_logging=False, no_disk_changes=False, ignore_all=False,
                   ignore_most=False, command=Checkout, branch='master')
        with Path('tests/test_file.txt').open(encoding='utf-8') as test_file:
            self.assertEqual(''.join(test_file.readlines()), test_content)

    def test_tag(self) -> None:
        system = tests.make_first_commit()
        system.run(no_logging=False, no_disk_changes=False, ignore_all=False,
                   ignore_most=False, command=Tag, name='TEST',
                   revision=None, message='A test tag')
        tags = next(os.walk(system.tags))[2]
        self.assertEqual(len(tags), 1)
        self.assertEqual(tags[0], 'TEST')
        with (system.tags / 'TEST').open() as test_tag:
            self.assertEqual(test_tag.readline(), 'TEST {} A test tag'
                             .format(next(os.walk(system.revisions))[2][-1]))

    def test_branch(self):
        system = tests.make_first_commit()
        system.run(no_logging=False, no_disk_changes=False, ignore_all=False,
                   ignore_most=False, command=Branch)
        exc_type, value, traceback = sys.exc_info()
        self.assertIsNone(exc_type)

    def test_status(self):
        system = tests.make_first_commit()
        system.run(no_logging=False, no_disk_changes=False, ignore_all=False,
                   ignore_most=False, command=Status, branch='master')
        exc_type, value, traceback = sys.exc_info()
        self.assertIsNone(exc_type)

    def tearDown(self) -> None:
        os.remove(Path('tests/test_file.txt'))
        second_path = Path('tests/test_file2.txt')
        if second_path.exists():
            os.remove(second_path)
        with Path('README.md').open('r+') as readme:
            readme_size = readme.seek(0, 2)
            readme.seek(readme_size - 1, 0)
            if readme.readline(1) == ' ':
                readme.truncate(0)


if __name__ == '__main__':
    unittest.main()
