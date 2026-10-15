"""Domain errors. The CLI translates them into exit codes and messages."""


class FileMetaError(Exception):
    """Base class of all expected errors of this program."""


class InvalidInputPathError(FileMetaError):
    """The given input path does not exist or is empty."""


class InvalidOutputPathError(FileMetaError):
    """The output path is empty, a directory, or has no existing parent directory."""


class ExifToolNotFoundError(FileMetaError):
    """The `exiftool` program is not installed or not on the PATH."""


class ExifToolExecutionError(FileMetaError):
    """`exiftool` produced no usable output."""
