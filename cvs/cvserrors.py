from pathlib import Path


class CVSError(Exception):
    message: str = "Unknown CVS Error"

    def __str__(self) -> str:
        return self.message


class AddListDoesNotExistError(CVSError):
    message = 'Add list does not exist!'


class BranchDoesNotExistError(CVSError):
    def __init__(self, branch_name: str) -> None:
        self.message = f'Branch {branch_name} does not exist!'


class EmptyRepositoryError(CVSError):
    message = 'Repository is empty!'


class IncorrectDateFormatError(CVSError):
    message = 'Incorrect data or data range format'


class IsDirectoryError(CVSError):
    def __init__(self, path: Path) -> None:
        self.message = f'{path} is a directory!'


class NoCommandError(CVSError):
    message = 'No command entered!'


class NotFoundInSourceError(CVSError):
    def __init__(self, path: Path) -> None:
        self.message = f'{path} was not reset because his source' \
                        f' was not found in repository'


class PathDoesNotExistError(CVSError):
    def __init__(self, path: Path) -> None:
        self.message = f'{path} does not exist!'


class RepositoryDoesNotExistError(CVSError):
    message = 'Repository does not exist! ' \
              'To create a repository, use \'init\' command'


class RepositoryExistsError(CVSError):
    message = 'Repository already exists!'


class RevisionDoesNotExistError(CVSError):
    def __init__(self, revision: str) -> None:
        self.message = f'Revision {revision} does not exist!'


class TagDoesNotExistError(CVSError):
    def __init__(self, name: str) -> None:
        self.message = f'Tag {name} does not exist!'


class TagExistsError(CVSError):
    def __init__(self, name: str) -> None:
        self.message = f'Tag {name} already exists!'
