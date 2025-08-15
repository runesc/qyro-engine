
import sys
import threading
import traceback
from collections import namedtuple

class ExceptionHandler:
    """
    Base class that defines the interface for exception handling.

    Designed to be inherited by classes that implement specific exception
    handling logic.

    Methods:
        init(self): Optional initialization method for the subclass.
        handle(self, exc_type, exc_value, enriched_tb): The central method
            for handling the exception.
    """
    def __init__(self):
        """Initialization method. Empty by default."""
        pass

    def handle(self, exc_type, exc_value, enriched_tb):
        """
        Handles an exception. This method must be overridden in derived classes.

        Args:
            exc_type (type): The exception type.
            exc_value (Exception): The exception instance.
            enriched_tb (traceback): The traceback object.

        Returns:
            bool: True if the handler considers the exception to have been
                  fully handled and no more handlers should be invoked.
                  False otherwise.

        Raises:
            NotImplementedError: If the method has not been overridden in
                                 the derived class.
        """
        raise NotImplementedError("The 'handle' method must be implemented by the subclass.")

class StderrExceptionHandler(ExceptionHandler):
    """
    Derived class that handles exceptions by printing the full traceback
    to the standard error output (stderr).
    """
    def handle(self, exc_type, exc_value, enriched_tb):
        """
        Handles the exception by printing its information to stderr.

        Args:
            exc_type (type): The exception type.
            exc_value (Exception): The exception instance.
            enriched_tb (traceback): The traceback object.

        Returns:
            bool: Always True, as this handler assumes the exception has
                  been visually handled.
        """
        print("Handling the exception with StderrExceptionHandler...", file=sys.stderr)
        traceback.print_exception(exc_type, exc_value, enriched_tb, file=sys.stderr)
        return True

# --- GLOBAL EXCEPTION HOOK SYSTEM FOR QT AND MULTI-THREADING ---

_fake_tb_frame = namedtuple('fake_tb', ('tb_frame', 'tb_lasti', 'tb_lineno', 'tb_next'))

def add_missing_qt_frames(tb):
    """
    Creates a 'fake' traceback to add missing frames from Qt callbacks.

    When exceptions occur in Qt's event loop, the original traceback can lose
    frames. This function attempts to reconstruct the traceback to include
    the root frame, making debugging easier.

    Args:
        tb (traceback): The original traceback object.

    Returns:
        namedtuple: A reconstructed traceback object with the missing
                    frames added, if a Qt-like traceback is detected.
                    Otherwise, it returns the original traceback.
    """
    fake_tb = None
    frame = tb.tb_frame
    while frame is not None:
        if 'QtCore.py' in frame.f_code.co_filename or 'QtGui.py' in frame.f_code.co_filename:
            # We've found a Qt-like frame, start reconstructing the traceback
            fake_tb = _fake_tb_frame(frame, frame.f_lasti, frame.f_lineno, fake_tb)
        frame = frame.f_back

    # If we found Qt frames, add the original traceback to the end of the fake one
    if fake_tb:
        tail = tb
        while tail.tb_next:
            tail = tail.tb_next
        tail.tb_next = fake_tb
        return tb
    else:
        return tb

class _Excepthook:
    """
    A global excepthook that dispatches exceptions to a list of handlers.

    This class should be used to replace sys.excepthook, providing a
    centralized and extensible way to manage uncaught exceptions.

    Args:
        handlers (list): A list of objects that implement the ExceptionHandler
                         interface.
    """
    def __init__(self, handlers):
        self.handlers = handlers
        self._previous_hook = sys.excepthook

    def install(self):
        """
        Initializes each handler and sets this instance as the new global
        exception hook.
        """
        for handler in self.handlers:
            handler.__init__()
        sys.excepthook = self

    def __call__(self, exc_type, exc_value, exc_tb):
        """
        The method called by Python when an uncaught exception occurs.

        This method iterates through the provided handlers, stopping when
        a handler returns True. It also handles Qt-specific tracebacks.

        Args:
            exc_type (type): The exception type.
            exc_value (Exception): The exception instance.
            exc_tb (traceback): The traceback object.
        """
        # Ignore SystemExit to allow graceful shutdown
        if issubclass(exc_type, SystemExit):
            self._previous_hook(exc_type, exc_value, exc_tb)
            return

        enriched_tb = add_missing_qt_frames(exc_tb)

        for handler in self.handlers:
            if handler.handle(exc_type, exc_value, enriched_tb):
                break

def enable_excepthook_for_threads():
    """
    Ensures that sys.excepthook is called for exceptions in non-main threads.

    This works by 'monkey-patching' threading.Thread.__init__ to wrap the
    thread's run method with a try/except block that calls the global hook.
    """
    original_run = threading.Thread.run

    def new_run(*args, **kwargs):
        try:
            original_run(*args, **kwargs)
        except Exception:
            sys.excepthook(*sys.exc_info())

    threading.Thread.run = new_run
