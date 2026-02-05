# Guía Rápida: Publicar en Homebrew

## Resumen de 5 pasos

### 1️⃣ Compilar la app
```bash
./build_release.sh
shasum -a 256 build/OfficeDaysTracker.zip
```
Guarda el hash SHA256 que aparece.

### 2️⃣ Crear release en GitHub
```bash
# Si no tienes el repo en GitHub
git remote add origin https://github.com/TU_USUARIO/OfficeDaysTracker.git
git push -u origin main

# Crear tag y subirlo
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

Luego en GitHub:
- Ve a "Releases" → "Create a new release"
- Selecciona el tag `v1.0.0`
- Sube el archivo `build/OfficeDaysTracker.zip`
- Publica el release

### 3️⃣ Crear tu Homebrew Tap
```bash
# En GitHub, crea un repo llamado: homebrew-tap

# Clonarlo
git clone https://github.com/TU_USUARIO/homebrew-tap.git
cd homebrew-tap
mkdir -p Casks

# Copiar la fórmula
cp ../homebrew/officedaystracker.rb Casks/
```

### 4️⃣ Editar la fórmula
Abre `Casks/officedaystracker.rb` y reemplaza:
- `TU_SHA256_AQUI` → El hash del paso 1
- `TU_USUARIO` → Tu usuario de GitHub (2 veces)

```bash
# Publicar
git add Casks/officedaystracker.rb
git commit -m "Add OfficeDaysTracker cask"
git push origin main
```

### 5️⃣ Instalar con Homebrew
```bash
brew tap TU_USUARIO/tap
brew install --cask officedaystracker
```

## ✅ Listo!

Tu app ya está disponible para instalar con Homebrew.

Para más detalles, consulta [HOMEBREW_SETUP.md](HOMEBREW_SETUP.md)
