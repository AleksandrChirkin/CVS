from cvs import Add, Commit, System, Tag
from pathlib import Path
from typing import Tuple


def make_commit() -> System:
    system = add_files()
    system.run(no_disk_changes=False, command=Commit, branch='master',
               message='Test message')
    return system


def add_files() -> System:
    system = System(Path.cwd())
    system.run(no_disk_changes=False, command=Add,
               files=['cvs', 'tests', 'README.md'])
    return system


def tag_to_reset_or_checkout() -> Tuple[System, str]:
    system = make_commit()
    system.run(no_disk_changes=False, command=Tag, name='TEST',
               revision=None, message='A test tag')
    with Path('tests/test_file.txt') \
            .open('r+', encoding='utf-8') as test_file:
        test_content = ''.join(test_file.readlines())
        test_file.write(' ')
    return system, test_content
