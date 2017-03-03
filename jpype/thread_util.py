from __future__ import print_function

from contextlib import  contextmanager
import _jpype
import threading

_the_lock = threading.RLock()

@contextmanager
def thread_context():
    # if the current thread is already attached, do nothing
    if _jpype.isThreadAttachedToJVM():
        yield
    # otherwise obtain the lock and attach the current thread
    else:
        with _the_lock:
            _jpype.attachThreadToJVM()
            yield
            # after the context is left, detach again
            _jpype.detachThreadFromJVM()


def wrap_in_thread_context(f):
    def wrap(*args, **kwargs):
        with thread_context():
            return f(*args, **kwargs)

    return wrap
