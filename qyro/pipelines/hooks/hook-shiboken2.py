from glob import glob
from os.path import dirname, relpath, join
import PySide2

_support_module = None

# Attempt to import the support module for PySide2 or Shiboken2
# This module contains additional Python files required at runtime
# that PyInstaller might not detect automatically.
try:
    if PySide2.__version__ == "5.12.2":
        import PySide2.support as _support_module
    else:
        import shiboken2.support as _support_module
except ImportError:
    pass

if _support_module is not None:
    _support_root = dirname(_support_module.__file__)
    _support_files = glob(join(_support_root, '**', '*.py'), recursive=True)
    _site_packages_dir = dirname(dirname(_support_root))
    datas = [(f, relpath(dirname(f), _site_packages_dir)) for f in _support_files]
    hiddenimports = ['typing']
