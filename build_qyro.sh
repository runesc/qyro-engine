#!/bin/bash

VERSION="1.0.0"

# Verificar que Poetry esté instalado
if ! command -v poetry &> /dev/null; then
    echo "❌ Poetry no está instalado. Instálalo con: pip install poetry"
    exit 1
fi

echo "🔄 Actualizando datos del paquete..."
if [ -f "package.json" ]; then
    cp package.json qyro/cli_commands/
    echo "✅ package.json copiado"
else
    echo "⚠️  package.json no encontrado, continuando..."
fi

echo "🧹 Limpiando builds anteriores..."
rm -rf build dist *.egg-info

echo "📦 Verificando configuración de Poetry..."
poetry check

echo "📦 Creando wheel para qyro v$VERSION con Poetry..."
poetry build

if [ $? -eq 0 ]; then
    echo "✅ Build exitoso"
    
    echo "📥 Desinstalando versión anterior..."
    pip uninstall -y qyro-engine
    
    echo "📥 Instalando wheel local..."
    if pip install "dist/qyro_engine-$VERSION-py3-none-any.whl"; then
        echo "✅ Instalación completada para qyro-engine v$VERSION"
    else
        echo "❌ Error en la instalación"
        exit 1
    fi
else
    echo "❌ Error en el build"
    exit 1
fi