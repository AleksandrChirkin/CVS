from cvs.system import System
from cvs.commands.command import Command  # noqa
from cvs.commands.init import Init
from cvs.commands.add import Add
from cvs.commands.commit import Commit
from cvs.commands.reset import Reset
from cvs.commands.log import Log

COMMANDS = [Init, Add, Commit, Reset, Log, System]
__all__ = ['Init', 'Add', 'Commit', 'Reset', 'Log', 'System', COMMANDS]
