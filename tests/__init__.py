from cvs import Add, Commit, System
from pathlib import Path


def make_first_commit() -> System:
    system = add_files()
    system.run(no_logging=False, no_disk_changes=False, ignore_all=False,
               ignore_most=False, command=Commit, branch='master',
               message='Test message')
    return system


def add_files() -> System:
    system = System(Path.cwd())
    system.run(no_logging=False, no_disk_changes=False, ignore_all=False,
               ignore_most=False, command=Add,
               files=['cvs', 'tests', 'README.md'], message='Test message')
    return system
