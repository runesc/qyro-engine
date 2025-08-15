#!/bin/bash

VERSION="1.0.0"

# copy package.json data to qyro/builtin_commands/
echo "🔄 Actualizando datos del paquete en setup.py..."
cp package.json qyro/builtin_commands/

echo "🧹 Limpiando builds anteriores..."
rm -rf build dist qyro.egg-info

echo "📦 Creando wheel para qyro v$VERSION..."
python setup.py sdist bdist_wheel

echo "📥 Instalando wheel local..."
pip uninstall -y qyro
pip install "dist/qyro-$VERSION-py3-none-any.whl"

echo "✅ Instalación completada para qyro v$VERSION"