from qyro_engine.core import lazy_property
from qyro_engine.utils import app_is_frozen
from qyro_engine.utils.resources import FileLocator
from qyro_engine._frozen import get_frozen_resource_dirs, load_frozen_build_settings
from qyro_engine._source import find_project_root_directory, get_project_resource_locations, load_build_configurations

try:
    from PySide6.QtWidgets import QWidget, QApplication
except ImportError:
    try:
        from PySide2.QtWidgets import QApplication, QWidget
    except ImportError:
        try:
            from PyQt6.QtWidgets import QApplication, QWidget
        except ImportError:
            try:
                from PyQt5.QtWidgets import QApplication, QWidget

            except ImportError:
                raise ImportError(
                    "PySide6, PySide2, PyQt6, or PyQt5 was not found."
                    "Please install one of them: pip install PySide6 (or PySide2, PyQt6, PyQt5)"
                )


def bootstrap(cls):
    def __init__(self, *args, **kwargs):
        super(cls, self).__init__(*args, **kwargs)
        self.component_will_mount()
        self.allow_bg()
        self.render_()
        self.component_did_mount()
        self.set_styles()
        self.responsive()

    cls.__init__ = __init__
    return cls


class Component:
    def component_will_mount(self): pass

    def allow_bg(self):
        try:
            from PySide2.QtCore import Qt
            self.setAttribute(Qt.WA_StyledBackground, True)
        except ImportError:
            try:
                from PySide6.QtCore import Qt
                self.setAttribute(Qt.WA_StyledBackground, True)
            except ImportError:
                try:
                    from PyQt5.QtCore import Qt
                    self.setAttribute(Qt.WA_StyledBackground, True)
                except ImportError:
                    try:
                        from PyQt6.QtCore import Qt
                        self.setAttribute(Qt.WA_StyledBackground, True)
                    except ImportError:
                        pass

    def render_(self): pass

    def resizeEvent(self, e=None):
        self.responsive()

    def component_did_mount(self): pass
    def set_styles(self, path=None): pass
    def responsive(self): pass

    def destroyComponent(self):
        self.setParent(None)
        self.deleteLater()

    def find(self, type, name):
        return self.findChild(type, name)

    @lazy_property
    def build_settings(self) -> dict:
        if app_is_frozen():
            return load_frozen_build_settings()
        else:
            project_root = find_project_root_directory()
            return load_build_configurations(project_root)

    @lazy_property
    def _project_dir(self):
        assert app_is_frozen(), 'Only available when running from source'
        return find_project_root_directory()

    @lazy_property
    def get_resource_locator(self):
        if app_is_frozen():
            resource_dirs = get_frozen_resource_dirs()
        else:
            project_root = find_project_root_directory()
            resource_dirs = get_project_resource_locations(project_root)

        return FileLocator(resource_dirs)

    def get_resource(self, *rel_path):
        return self.get_resource_locator.find(*rel_path)

    def _clear_widgets(self):
        """
            Clear all child widgets except for the main widget.
        """
        try:
            for child_obj in self.findChildren(QWidget):
                if child_obj != self:
                    child_obj.deleteLater()
            QApplication.processEvents()
        except RuntimeError:
            pass

    def _ensure_children_visibility(self):
        """
        Ensure all child widgets are visible.

        Raises:
            RuntimeError: If a widget was already deleted.
            e: If any other error occurs.
        """
        try:
            for child_obj in self.findChildren(QWidget):
                child_obj.show()
            self.adjustSize()
            self.update()
            self.repaint()
        except RuntimeError as e:
            if 'already deleted' in str(e):
                raise RuntimeError("A widget was already deleted.")
            else:
                raise e

    def _trigger_render(self):
        """
        Trigger a re-render of the component (for Pydux instances)
        """
        try:
            # Todo el ciclo de vida se envuelve en el try
            self._clear_widgets()
            self.allow_bg()
            self.render_()
            self.responsive()
            self.component_did_mount()
            self.set_styles()

            self._ensure_children_visibility()
        except RuntimeError:
            pass
        finally:
            self.setUpdatesEnabled(True)

    @staticmethod
    def calc(a, b): return int((a * b) / 100.0)
