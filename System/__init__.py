from System.commands.command import Command
from System.commands.init import Init
from System.commands.add import Add
from System.commands.commit import Commit
from System.commands.reset import Reset
from System.commands.log import Log
from System.system import System

COMMANDS = [Init, Add, Commit, Reset, Log, System]
__all__ = ['Init', 'Add', 'Commit', 'Reset', 'Log', 'System', COMMANDS]
