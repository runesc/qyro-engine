import importlib
from . import _AppEngine, QtBinding, available_bindings, lazy_property
from qyro_engine.utils import module_exists

class AppEngine(_AppEngine):
    preferred_binding = 'PySide2'
    def _load_binding_classes(self):
        """
        Loads the actual Qt classes dynamically from the string paths.
        Tries the preferred binding first if available.
        """
        # Primero intenta el binding preferido
        if module_exists(self.preferred_binding):
            return available_bindings[self.preferred_binding]

        # Si no está, busca el primero disponible
        for name, binding in available_bindings.items():
            if module_exists(name):
                return binding

        raise RuntimeError(
            f"No se encontró un binding de Qt compatible. Intentaste: {self.preferred_binding}"
        )
    @lazy_property
    def _qt_binding(self):
        """
        Returns an instance of _QtBinding with dynamically imported classes.
        """
        # Obtenemos las clases como strings del binding disponible.
        binding_strings = self._load_binding_classes()

        # Importamos las clases usando sus rutas de texto.
        q_application_class = importlib.import_module(
            ".".join(binding_strings.QApplication.split(".")[:-1]))
        q_icon_class = importlib.import_module(
            ".".join(binding_strings.QIcon.split(".")[:-1]))
        q_abstract_socket_class = importlib.import_module(
            ".".join(binding_strings.QAbstractSocket.split(".")[:-1]))

        # Obtenemos las clases finales.
        QApplication = getattr(q_application_class, "QApplication")
        QIcon = getattr(q_icon_class, "QIcon")
        QAbstractSocket = getattr(q_abstract_socket_class, "QAbstractSocket")

        return QtBinding(QApplication, QIcon, QAbstractSocket)