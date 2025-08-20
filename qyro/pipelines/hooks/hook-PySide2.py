from glob import glob
from os.path import dirname, relpath, join
import PySide2

support = None

# Attempt to import the PySide2 support module if it exists
# This module contains additional Python files required at runtime
# that PyInstaller might not detect automatically.
try:
    import PySide2.support as support
except ImportError:
    pass

if support is not None:
    _pyside_root = dirname(support.__file__)
    _pyside_files = glob(join(_pyside_root, '**', '*.py'), recursive=True)
    _site_packages_dir = dirname(dirname(_pyside_root))
    datas = [(f, relpath(dirname(f), _site_packages_dir)) for f in _pyside_files]
    hiddenimports = ['typing']
