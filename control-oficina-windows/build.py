#!/usr/bin/env python3
"""
Build script for ControlOficina Windows.
Genera un .exe autoejecutable con PyInstaller.

Uso:
    python build.py          # Build normal
    python build.py --onedir # Build en directorio (más rápido para debug)
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

HERE = Path(__file__).parent
DIST = HERE / "dist"


def build(onefile: bool = True):
    # Limpiar builds anteriores
    for d in [HERE / "build", DIST]:
        if d.exists():
            shutil.rmtree(d)

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconsole",
        "--name", "ControlOficina",
        "--add-data", f"{HERE / 'resources'}{os.pathsep}resources",
    ]

    if onefile:
        cmd.append("--onefile")

    cmd.append(str(HERE / "main.py"))

    print(f"Ejecutando: {' '.join(cmd)}")
    subprocess.run(cmd, cwd=HERE, check=True)

    exe = DIST / "ControlOficina.exe"
    if exe.exists():
        print(f"\n✓ Build exitoso: {exe}")
        print(f"  Tamaño: {exe.stat().st_size / 1024 / 1024:.1f} MB")
    else:
        print("\n✗ Error: no se encontró el ejecutable")


if __name__ == "__main__":
    onefile = "--onedir" not in sys.argv
    build(onefile=onefile)
