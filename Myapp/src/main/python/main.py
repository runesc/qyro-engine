import sys
from qyro_engine.core.PySide6 import AppEngine
from qyro_engine.core.base import Component, init_lifecycle
from qyro_engine.core.utils import app_is_frozen
from qyro_engine.devtools.reloader import hot_reloading
from qyro_engine.store import Pydux
from PySide6.QtWidgets import QMainWindow, QLabel

# --------------------------------------------------------------------------------------
# Important! Production Considerations for Hot Reloading
# --------------------------------------------------------------------------------------
# Hot reloading is a development tool that allows you to instantly see UI changes
# when you save a file. It's extremely useful for rapid prototyping and designing
# interfaces.
#
# However, this functionality is not designed for use in production environments.
# For the final version of your application, it is highly recommended to remove
# the code related to hot reloading, such as the `@hot_reloading` decorator
# and the `window._init_hot_reload_system(__file__)` call.
#
# Keeping hot reloading active in production can negatively impact the application's
# performance, stability, and security.
# --------------------------------------------------------------------------------------

@init_lifecycle
@hot_reloading
class Myapp(QMainWindow, Component, Pydux):
    def component_will_mount(self):
        self.subscribe_to_store(self)

    def render_(self):
       QLabel('Hello World!', parent=self)

    def responsive_UI(self):
        self.setMinimumSize(640, 480)


if __name__ == '__main__':
    appctxt = AppEngine()
    window = Myapp()
    if not app_is_frozen():
        window._init_hot_reload_system(__file__)
    window.show()
    exec_func = getattr(appctxt.app, 'exec', appctxt.app.exec_)
    sys.exit(exec_func())