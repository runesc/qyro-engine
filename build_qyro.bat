@echo off
set VERSION=1.0.0

echo 🔄 Actualizando datos del paquete...
copy package.json qyro\cli_commands\ /Y

echo 🧹 Limpiando builds anteriores...
rmdir /s /q build
rmdir /s /q dist
rmdir /s /q *.egg-info

echo 📦 Creando wheel para qyro v%VERSION% con Poetry...
poetry build

echo 📥 Desinstalando version anterior...
pip uninstall -y qyro-engine

echo 📥 Instalando wheel local...
pip install dist\qyro_engine-%VERSION%-py3-none-any.whl

echo ✅ Instalacion completada para qyro-engine v%VERSION%

pause