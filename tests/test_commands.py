from datetime import date
from pathlib import Path
import json
import os
import sys
import tests
import unittest
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             os.path.pardir))
from cvs import Init, Add, Commit, Reset, Log, Checkout, Tag, System, COMMANDS  # noqa


class TestCommands(unittest.TestCase):
    def setUp(self) -> None:
        System({
            'directory': Path.cwd(),
            'no_logging': False,
            'no_disk_changes': False,
            'ignore_all': False,
            'ignore_most': False,
            'command': Init,
            'recreate': Path.exists(Path.cwd()/'.repos')
        }).run()
        with open(Path('tests/test_file.txt'), 'w',
                  encoding='utf-8') as test_file:
            test_file.write('I\'m temp file!')

    def test_init(self) -> None:
        for item in os.walk(Path.cwd()/'.repos', False):
            for file in item[2]:
                os.remove(Path(item[0])/file)
            for directory in item[1]:
                os.rmdir(Path(item[0])/directory)
        os.remove(Path.cwd()/'.cvsignore')
        os.rmdir(Path.cwd()/'.repos')
        system = System({
                        'directory': Path.cwd(),
                        'no_logging': False,
                        'no_disk_changes': False,
                        'ignore_all': False,
                        'ignore_most': False,
                        'command': Init,
                        'recreate': False
                        })
        system.run()
        self.assertTrue(Path.exists(system.repository))
        self.assertTrue(Path.exists(system.cvsignore))
        self.assertTrue(Path.exists(system.history))
        self.assertTrue(Path.exists(system.repository/'errorlog.json'))
        self.assertTrue(Path.exists(system.branches))
        self.assertTrue(Path.exists(system.diffs))
        self.assertTrue(Path.exists(system.revisions))

    def test_add(self) -> None:
        system = tests.add_files()
        self.assertTrue(Path.exists(system.add_list))
        with open(system.add_list, encoding='utf-8') as add_list:
            added = json.load(add_list)
        for item in os.walk(Path.cwd()/'cvs'):
            for file in item[2]:
                full_path = str(Path(item[0])/file)
                if not system.is_in_cvsignore(full_path):
                    self.assertTrue(added.__contains__(full_path))

    def test_first_commit(self) -> None:
        system = tests.make_first_commit()
        self.assertEqual(len(next(os.walk(system.branches))[2]), 1)
        self.assertTrue(Path.exists(system.branches/'master.json'))
        self.assertEqual(len(next(os.walk(system.revisions))[2]), 1)
        with open(system.add_list, encoding='utf-8') as add_list:
            added = json.load(add_list)
        self.assertTrue(len(next(os.walk(system.diffs))[2]), len(added))

    def test_new_commit_to_existing_branch(self) -> None:
        tests.make_first_commit()
        with open('tests/test_file.txt', 'a', encoding='utf-8') as readme:
            readme.write(' ')
        system = System({
            'directory': Path.cwd(),
            'no_logging': False,
            'no_disk_changes': False,
            'ignore_all': False,
            'ignore_most': False,
            'command': Commit,
            'branch': 'master',
            'message': 'Committing README'
        })
        system.run()
        self.assertEqual(len(next(os.walk(system.branches))[2]), 1)
        self.assertEqual(len(next(os.walk(system.revisions))[2]), 2)
        with open(system.add_list, encoding='utf-8') as add_list:
            added = json.load(add_list)
        self.assertTrue(len(next(os.walk(system.diffs))[2]), len(added)+1)

    def test_committing_new_file(self):
        system = tests.make_first_commit()
        with open(Path('tests/test_file2.txt'), 'w',
                  encoding='utf-8') as test_file:
            test_file.write('I\'m temp file!')
        with open(system.add_list, encoding='utf-8') as add_list:
            added = json.load(add_list)
        system = tests.make_first_commit()
        with open(system.add_list, encoding='utf-8') as add_list:
            self.assertEqual(len(added)+1, len(json.load(add_list)))
        self.assertEqual(len(next(os.walk(system.branches))[2]), 1)
        self.assertEqual(len(next(os.walk(system.revisions))[2]), 2)

    def test_commit_to_new_branch(self) -> None:
        tests.make_first_commit()
        system = System({
            'directory': Path.cwd(),
            'no_logging': False,
            'no_disk_changes': False,
            'ignore_all': False,
            'ignore_most': False,
            'command': Commit,
            'branch': 'test',
            'message': 'Creating test branch'
        })
        system.run()
        self.assertEqual(len(next(os.walk(system.branches))[2]), 2)
        self.assertTrue(Path.exists(system.branches/'test.json'))
        self.assertEqual(len(next(os.walk(system.revisions))[2]), 2)
        with open(system.add_list, encoding='utf-8') as add_list:
            added = json.load(add_list)
        self.assertTrue(len(next(os.walk(system.diffs))[2]), 2*len(added))

    def test_reset(self) -> None:
        tests.make_first_commit()
        with open('tests/test_file.txt', 'r+', encoding='utf-8') as readme:
            readme_content = ''.join(readme.readlines())
            readme.write(' ')
        System({
            'directory': Path.cwd(),
            'no_logging': False,
            'no_disk_changes': False,
            'ignore_all': False,
            'ignore_most': False,
            'command': Reset,
            'branch': 'master',
            'files': ['tests/test_file.txt'],
            'revision': None
        }).run()
        with open('tests/test_file.txt', encoding='utf-8') as readme:
            self.assertEqual(''.join(readme.readlines()), readme_content)

    def test_log(self) -> None:
        tests.make_first_commit()
        System({
            'directory': Path.cwd(),
            'no_logging': False,
            'no_disk_changes': False,
            'ignore_all': False,
            'ignore_most': False,
            'command': Log,
            'branches': ['master'],
            'dates': str(date.today()),
            'files': ['README.md'],
            'revisions': [next(os.walk(Path.cwd()/'.repos/revisions'))
                          [2][-1][:-5]]
        }).run()
        System({
            'directory': Path.cwd(),
            'no_logging': False,
            'no_disk_changes': False,
            'ignore_all': False,
            'ignore_most': False,
            'command': Log,
            'branches': ['master'],
            'dates': '{0}>{0}'.format(date.today()),
            'files': ['README.md'],
            'revisions': [next(os.walk(Path.cwd() / '.repos/revisions'))
                          [2][-1]]
        }).run()
        exc_type, value, traceback = sys.exc_info()
        self.assertIsNone(exc_type)

    def test_log_with_defaults(self) -> None:
        tests.make_first_commit()
        System({
            'directory': Path.cwd(),
            'no_logging': False,
            'no_disk_changes': False,
            'ignore_all': False,
            'ignore_most': False,
            'command': Log,
            'branches': None,
            'dates': None,
            'files': None,
            'revisions': None
        }).run()
        exc_type, value, traceback = sys.exc_info()
        self.assertIsNone(exc_type)

    def test_checkout(self) -> None:
        tests.make_first_commit()
        with open('tests/test_file.txt', 'r+', encoding='utf-8') as readme:
            readme_content = ''.join(readme.readlines())
            readme.write(' ')
        System({
            'directory': Path.cwd(),
            'no_logging': False,
            'no_disk_changes': False,
            'ignore_all': False,
            'ignore_most': False,
            'command': Checkout,
            'branch': 'master'
        }).run()
        with open('tests/test_file.txt', encoding='utf-8') as readme:
            self.assertEqual(''.join(readme.readlines()), readme_content)

    def test_tag(self) -> None:
        tests.make_first_commit()
        system = System({
            'directory': Path.cwd(),
            'no_logging': False,
            'no_disk_changes': False,
            'ignore_all': False,
            'ignore_most': False,
            'command': Tag,
            'name': 'TEST',
            'revision': None,
            'message': 'A test tag'
        })
        system.run()
        tags = next(os.walk(system.tags))[2]
        self.assertEqual(len(tags), 1)
        self.assertEqual(tags[0], 'TEST')
        with open(system.tags/'TEST') as test_tag:
            self.assertEqual(test_tag.readline(), 'TEST {} A test tag'
                             .format(next(os.walk(system.revisions))[2][-1]))

    def tearDown(self) -> None:
        os.remove(Path('tests/test_file.txt'))
        second_path = Path('tests/test_file2.txt')
        if Path.exists(second_path):
            os.remove(second_path)
        with open('README.md', 'r+') as readme:
            readme_size = readme.seek(0, 2)
            readme.seek(readme_size-1, 0)
            if readme.readline(1) == ' ':
                readme.truncate(0)


if __name__ == '__main__':
    unittest.main()
