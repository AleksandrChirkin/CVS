from cvs import Add, Commit, System
from pathlib import Path


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
