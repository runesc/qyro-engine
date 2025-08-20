from glob import glob
from os.path import dirname, relpath, join
import PySide6.support as _support_module

# Attempt to import the PySide6 support module
# This module contains additional Python files required at runtime
# that PyInstaller might not detect automatically.

if _support_module is not None:
    _support_root = dirname(_support_module.__file__)
    _support_files = glob(join(_support_root, '**', '*.py'), recursive=True)
    _site_packages_dir = dirname(dirname(_support_root))
    datas = [(f, relpath(dirname(f), _site_packages_dir)) for f in _support_files]
    hiddenimports = ['typing']