@echo off
set VERSION=1.0.0

echo 🔄 Actualizando datos del paquete en setup.py...
copy package.json qyro\builtin_commands\ /Y

echo 🧹 Limpiando builds anteriores...
rmdir /s /q build
rmdir /s /q dist
rmdir /s /q qyro.egg-info

echo 📦 Creando wheel para qyro v%VERSION%...
python setup.py sdist bdist_wheel

echo 📥 Instalando wheel local...
pip uninstall -y qyro
pip install dist\qyro-%VERSION%-py3-none-any.whl

echo ✅ Instalacion completada para qyro v%VERSION%