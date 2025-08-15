from functools import lru_cache, wraps
from typing import Callable, TypeVar
from collections import namedtuple
from qyro_engine.utils.platform import windows_based, mac_based
from qyro_engine.utils import app_is_frozen
from qyro_engine._signal import QtSignalHandler
from qyro_engine._frozen import load_frozen_build_settings, get_frozen_resource_dirs
from qyro_engine._source import get_project_dir, get_resource_dirs, load_build_settings
from qyro_engine.utils.resources import ResourceLocator
from qyro_engine.exceptions.excepthooks import _Excepthook, StderrExceptionHandler

_T = TypeVar('_T')
_CallableGetter = Callable[..., _T]


def lazy_property(getter: _CallableGetter) -> property:
    """
    A decorator for properties that computes a function's value only once
    and then caches the result for reuse.
    """
    @wraps(getter)
    @lru_cache(maxsize=1)
    def wrapper(*args, **kwargs):
        return getter(*args, **kwargs)

    return property(wrapper)

QtBinding = namedtuple('QtBinding', ('QApplication', 'QIcon', 'QAbstractSocket'))

available_bindings = {
    'PySide6': QtBinding(
        QApplication='PySide6.QtWidgets.QApplication',
        QIcon='PySide6.QtGui.QIcon',
        QAbstractSocket='PySide6.QtNetwork.QAbstractSocket'
    ),
    'PyQt6': QtBinding(
        QApplication='PyQt6.QtWidgets.QApplication',
        QIcon='PyQt6.QtGui.QIcon',
        QAbstractSocket='PyQt6.QtNetwork.QAbstractSocket'
    ),
    'PySide2': QtBinding(
        QApplication='PySide2.QtWidgets.QApplication',
        QIcon='PySide2.QtGui.QIcon',
        QAbstractSocket='PySide2.QtNetwork.QAbstractSocket'
    ),
    'PyQt5': QtBinding(
        QApplication='PyQt5.QtWidgets.QApplication',
        QIcon='PyQt5.QtGui.QIcon',
        QAbstractSocket='PyQt5.QtNetwork.QAbstractSocket'
    ),
}

class _AppEngine:
    """
    Entry point for your Qt application.

    This class initializes the QApplication, sets up exception handling,
    signal handling, resource management, and build settings.
    """

    def __init__(self):
        # Install global exception hook
        if self.excepthook:
            self.excepthook.install()

        # Instantiate the QApplication early
        self.app

        # Install Ctrl+C handler on non-Windows systems
        if not windows_based():
            self._signal_handler = QtSignalHandler(self.app, self._qt_binding.QAbstractSocket)
            self._signal_handler.install()

        # Set application icon if available
        if self.app_icon:
            self.app.setWindowIcon(self.app_icon)

    @lazy_property
    def app(self):
        """
        The global Qt QApplication instance. Can be overridden to use
        a custom subclass.
        """
        result = self._qt_binding.QApplication([])
        result.setApplicationName(self.build_settings['app_name'])
        result.setApplicationVersion(self.build_settings['version'])
        return result

    @lazy_property
    def build_settings(self):
        """
        Returns the build settings dictionary.
        """
        if app_is_frozen():
            return load_frozen_build_settings()
        return load_build_settings(self._project_dir)

    @lazy_property
    def app_icon(self):
        """
        Returns the application icon (not used on macOS).
        """
        if not mac_based():
            return self._qt_binding.QIcon(self.get_resource('Icon.ico'))

    @lazy_property
    def excepthook(self):
        """
        Returns the global exception hook. Override to provide custom hooks.
        """
        return _Excepthook(self.exception_handlers)

    @lazy_property
    def exception_handlers(self):
        """
        List of exception handlers to invoke on errors.
        """
        return [StderrExceptionHandler()]

    @lazy_property
    def _qt_binding(self):
        """
        Subclasses must provide a Qt binding module, e.g., PyQt5 or PySide6.
        """
        raise NotImplementedError("Subclasses must define `_qt_binding`")

    @lazy_property
    def _resource_locator(self):
        """
        Returns a ResourceLocator for the application's resources.
        """
        resource_dirs = get_frozen_resource_dirs() if app_is_frozen() else get_resource_dirs(self._project_dir)
        return ResourceLocator(resource_dirs)

    @lazy_property
    def _project_dir(self):
        assert not app_is_frozen(), 'Only available when running from source'
        return get_project_dir()

    def get_resource(self, *rel_path):
        """
        Returns the absolute path to a resource.
        """
        return self._resource_locator.locate(*rel_path)
