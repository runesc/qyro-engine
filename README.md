<p align="center">
  <img src="https://ik.imagekit.io/kummiktgaiq/ppg/Qyro-logo.svg?updatedAt=1755215983279" alt="Qyro Logo" width="50%">
</p>



<h3 align="center">Qyro - <b>Q</b>t p<b>y</b>thon <b>R</b>esource <b>O</b>rchestrator</h3>

![GitHub Release](https://img.shields.io/github/v/release/runesc/qyro-engine?include_prereleases&display_name=release&color=stable)
![GitHub Issues](https://img.shields.io/github/issues/runesc/qyro-engine?color=%23ab7df8)
![GitHub Issues Closed](https://img.shields.io/github/issues-closed/runesc/qyro-engine?color=green)
![GitHub forks](https://img.shields.io/github/forks/runesc/qyro-engine)
![GitHub stars](https://img.shields.io/github/stars/runesc/qyro-engine)
![GitHub license](https://img.shields.io/github/license/runesc/qyro-engine)


Qyro is a simple and powerful **Python application packager**, inspired by FBS.  
It allows you to compile Python/Qt applications into standalone executables with ease, manage resources, and create installers for multiple platforms.

---

### 🔥 Key Features

- **Cross-Platform Packaging**: Build standalone executables for Windows, macOS, and Linux.
- **Installer Creation**: Automatically generate platform-specific installers.
- **Resource Management**: Include assets, icons, and other files seamlessly.
- **CLI Driven**: Full project management via a simple command-line interface.
- **Hot Error & Info Messages**: Rich console messages for errors, warnings, info, debug, and critical notifications.

---

### 🚀 Quick Start

```bash
# 1. Install Qyro via pip
pip install qyro

# 2. Initialize a new project
qyro init

# 3. Run your app in development mode (optional)
qyro start

# 4. Compile your app into a standalone executable
qyro freeze

# 5. Create an installer
qyro installer
```

---

### CLI Usage

| Command          | Description                                                       |
| ---------------- | ----------------------------------------------------------------- |
| `qyro init`      | Initialize a new Qyro project with interactive setup.             |
| `qyro start`     | Run your application in development mode (optional, for testing). |
| `qyro freeze`    | Compile your Python/Qt app into a standalone executable.          |
| `qyro installer` | Create a platform-specific installer for your app.                |
| `qyro clean`     | Remove temporary files and build artifacts.                       |

---

### Installation

1. **Using pip** (recommended):

```bash
pip install qyro
```

2. **From GitHub (latest development version)**:

```bash
pip install git+https://github.com/neuri-ai/Qyro.git
```

3. **Or clone and install locally**:

```bash
git clone https://github.com/neuri-ai/Qyro.git
cd Qyro
python setup.py install
```

---

### Creators

**Luis Alfredo Reyes**

- [https://twitter.com/Fredo_Dev](https://twitter.com/Fredo_Dev)
- [https://github.com/runesc](https://github.com/runesc)

---

### License

Qyro code released under the [GPL v3 License](#).
Docs released under [Creative Commons](https://creativecommons.org/licenses/by/3.0/).

```

Si quieres, puedo hacer una **versión todavía más profesional**, incluyendo:
- Ejemplo completo de proyecto Qyro
- Cómo empaquetar recursos y assets
- Mensajes de consola con **EngineMessage**
- Diferencias frente a FBS/pyinstaller
```
