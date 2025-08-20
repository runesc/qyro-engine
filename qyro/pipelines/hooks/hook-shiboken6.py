from glob import glob
from os.path import dirname, relpath, join
import PySide6

_support_module = None

# Attempt to import the support module for PySide2 or Shiboken2
# This module contains additional Python files required at runtime
# that PyInstaller might not detect automatically.
try:
    if PySide6.__version__ == "6.0.0":
        import PySide6.support as _support_module
    else:
        import shiboken6.support as _support_module
except ImportError:
    pass

if _support_module is not None:
    _support_root = dirname(_support_module.__file__)
    _support_files = glob(join(_support_root, '**', '*.py'), recursive=True)
    _site_packages_dir = dirname(dirname(_support_root))
    datas = [(f, relpath(dirname(f), _site_packages_dir)) for f in _support_files]
    hiddenimports = ['typing']
