import importlib
from functools import lru_cache, wraps
from typing import Callable, TypeVar, Any
from collections import namedtuple
from qyro.utils.platform import windows_based, mac_based
from qyro_engine.utils import app_is_frozen
from qyro_engine._signal import QtSignalHandler
from qyro_engine._frozen import load_frozen_build_settings, get_frozen_resource_dirs
from qyro_engine._source import find_project_root_directory, get_project_resource_locations, load_build_configurations
from qyro_engine.utils.resources import FileLocator
from qyro_engine.exceptions.excepthooks import _Excepthook, StderrExceptionHandler
import sys

_T = TypeVar('_T')
QtBinding = namedtuple('QtBinding', ['QApplication', 'QIcon', 'QAbstractSocket'])
available_bindings = {}

def lazy_property(func: Callable[[Any], _T]) -> _T:
    @wraps(func)
    @lru_cache(maxsize=1)
    def wrapper(self):
        return func(self)
    return property(wrapper)

def load_qt_binding(binding_name: str) -> QtBinding:
    try:
        if binding_name == 'PyQt5':
            widgets = importlib.import_module('PyQt5.QtWidgets')
            gui = importlib.import_module('PyQt5.QtGui')
            network = importlib.import_module('PyQt5.QtNetwork')
        elif binding_name == 'PyQt6':
            widgets = importlib.import_module('PyQt6.QtWidgets')
            gui = importlib.import_module('PyQt6.QtGui')
            network = importlib.import_module('PyQt6.QtNetwork')
        elif binding_name == 'PySide2':
            widgets = importlib.import_module('PySide2.QtWidgets')
            gui = importlib.import_module('PySide2.QtGui')
            network = importlib.import_module('PySide2.QtNetwork')
        elif binding_name == 'PySide6':
            widgets = importlib.import_module('PySide6.QtWidgets')
            gui = importlib.import_module('PySide6.QtGui')
            network = importlib.import_module('PySide6.QtNetwork')
        else:
            raise ValueError(f"Unknown binding: {binding_name}")
    except ModuleNotFoundError as e:
        raise ImportError(f"Cannot load Qt binding '{binding_name}'. Module not found: {e}")

    return QtBinding(
        QApplication=getattr(widgets, 'QApplication'),
        QIcon=getattr(gui, 'QIcon'),
        QAbstractSocket=getattr(network, 'QAbstractSocket')
    )

class _AppEngine:
    """
    Base engine para apps Qt con bindings dinámicos.
    """
    preferred_binding = 'PySide6'
    _qt_binding = None

    def __init__(self, argv: list[str] = None):
        if argv is None:
            argv = sys.argv
        self._argv = argv

        # Carga el binding
        if self._qt_binding is None:
            self._qt_binding = self.preferred_binding
        available_bindings[self._qt_binding] = load_qt_binding(self._qt_binding)

        # Creamos la app
        self.app = self.get_application_instance

        # Configuramos icono si aplica
        if self.set_app_icon:
            self.app.setWindowIcon(self.set_app_icon)

        # Manejo de excepciones y señales
        self.exception_handler = StderrExceptionHandler()
        self.install_exception_hook()
        self.setup_signal_handler()

    @staticmethod
    def _validate_qt_binding(binding_name: str, binding: QtBinding):
        if not isinstance(binding, QtBinding):
            raise TypeError(f"Invalid Qt binding type for '{binding_name}'")
        if binding.QApplication is None:
            raise ValueError(f"QApplication class not found for binding '{binding_name}'")

    @lazy_property
    def get_application_instance(self):
        binding = available_bindings[self._qt_binding]
        self._validate_qt_binding(self._qt_binding, binding)
        build_settings = self.load_build_settings()

        app = binding.QApplication(self._argv)
        app.setApplicationName(build_settings.get('app_name', 'App'))
        app.setApplicationVersion(build_settings.get('version', '1.0'))
        return app

    @lazy_property
    def get_resource_locator(self):
        if app_is_frozen():
            resource_dirs = get_frozen_resource_dirs()
        else:
            project_root = find_project_root_directory()
            resource_dirs = get_project_resource_locations(project_root)
        return FileLocator(resource_dirs)

    def _resource(self, *rel_path):
        return self.get_resource_locator.find(*rel_path)

    @lazy_property
    def set_app_icon(self):
        if mac_based():
            return None
        binding = available_bindings[self._qt_binding]
        return binding.QIcon(self._resource('Icon.ico'))

    def install_exception_hook(self):
        _Excepthook(self.exception_handler)

    def setup_signal_handler(self):
        if not windows_based():
            binding = available_bindings[self._qt_binding]
            QtSignalHandler(self.app, binding.QAbstractSocket).install()

    def load_build_settings(self) -> dict:
        if not app_is_frozen():
            return load_frozen_build_settings()
        else:
            project_root = find_project_root_directory()
            return load_build_configurations(project_root)
