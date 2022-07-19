import sys
import traceback
from types import FrameType, TracebackType
from typing import Callable, Optional, Type, TypeVar

A = TypeVar("A", bound="ModelRunError")
# a function that takes a frame and indicates whether it is a
# frame of user code or not.
StackFilter = Callable[[FrameType], bool]


def get_user_stack_depth(tb: TracebackType, f: StackFilter) -> int:
    """Determines the depth of the stack within user-code.

    Takes a 'StackFilter' function that filters frames by whether
    they are in user code or not and returns the number of frames
    in the traceback that are within user code.

    The return value can be negated for use with the limit argument
    to functions in the traceback module.

    """
    depth = 0
    for s, _ in traceback.walk_tb(tb):
        if depth or f(s):
            depth += 1
    return depth


class ModelRunError(Exception):
    error: str
    details: str

    def __init__(self, details):
        self.details = details

    @classmethod
    def from_exception(cls: Type[A], filter_stack: Optional[StackFilter] = None) -> A:
        limit = 0
        if filter_stack:
            _, _, tb = sys.exc_info()
            limit = get_user_stack_depth(tb, filter_stack)
        exc = traceback.format_exc(limit=(-limit if limit else None))
        return cls(exc)


class CodeSyntaxError(ModelRunError):
    error = "Syntax Error"


class CodeError(ModelRunError):
    error = "Code Error"


class CodeRaisedError(ModelRunError):
    error = "Unhandled Exception"
