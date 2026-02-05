# Configuración de Homebrew para OfficeDaysTracker

Esta guía te ayudará a hacer tu app instalable mediante Homebrew.

## Paso 1: Preparar el Release

### 1.1 Compilar la app para distribución

```bash
chmod +x build_release.sh
./build_release.sh
```

Esto creará:
- `build/Release/OfficeDaysTracker.app` - La aplicación compilada
- `build/OfficeDaysTracker.zip` - Archivo ZIP para distribución

### 1.2 Calcular el SHA256

```bash
shasum -a 256 build/OfficeDaysTracker.zip
```

Guarda este hash, lo necesitarás para la fórmula de Homebrew.

## Paso 2: Crear un Release en GitHub

### 2.1 Crear el repositorio (si no existe)

```bash
# Inicializar git si no está inicializado
git init
git add .
git commit -m "Initial commit"

# Crear repositorio en GitHub y conectarlo
git remote add origin https://github.com/TU_USUARIO/OfficeDaysTracker.git
git branch -M main
git push -u origin main
```

### 2.2 Crear un tag y release

```bash
# Crear tag
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

### 2.3 Subir el archivo ZIP a GitHub Releases

1. Ve a tu repositorio en GitHub
2. Click en "Releases" → "Create a new release"
3. Selecciona el tag `v1.0.0`
4. Título: `v1.0.0`
5. Descripción: Agrega las características principales
6. Arrastra el archivo `build/OfficeDaysTracker.zip` a la sección de assets
7. Click en "Publish release"

## Paso 3: Crear tu Homebrew Tap

### 3.1 Crear el repositorio del tap

En GitHub, crea un nuevo repositorio llamado: `homebrew-tap`

**Importante:** El nombre DEBE seguir el formato `homebrew-NOMBRE`

### 3.2 Clonar y configurar el tap

```bash
# Clonar el repositorio del tap
git clone https://github.com/TU_USUARIO/homebrew-tap.git
cd homebrew-tap

# Crear la estructura de directorios
mkdir -p Casks

# Copiar la fórmula
cp ../homebrew/officedaystracker.rb Casks/
```

### 3.3 Actualizar la fórmula con tus datos

Edita `Casks/officedaystracker.rb` y reemplaza:

1. `TU_SHA256_AQUI` → El hash SHA256 que calculaste en el Paso 1.2
2. `TU_USUARIO` → Tu usuario de GitHub (en ambas URLs)

Ejemplo:
```ruby
cask "officedaystracker" do
  version "1.0.0"
  sha256 "a1b2c3d4e5f6..."  # Tu hash real

  url "https://github.com/miusuario/OfficeDaysTracker/releases/download/v#{version}/OfficeDaysTracker.zip"
  name "Office Days Tracker"
  desc "App nativa de macOS para controlar tu asistencia a la oficina mediante detección de red"
  homepage "https://github.com/miusuario/OfficeDaysTracker"
  
  # ... resto del archivo
end
```

### 3.4 Publicar el tap

```bash
git add Casks/officedaystracker.rb
git commit -m "Add OfficeDaysTracker cask"
git push origin main
```

## Paso 4: Instalar tu app con Homebrew

### 4.1 Agregar tu tap

```bash
brew tap TU_USUARIO/tap
```

### 4.2 Instalar la app

```bash
brew install --cask officedaystracker
```

### 4.3 Actualizar la app (en el futuro)

```bash
brew upgrade --cask officedaystracker
```

### 4.4 Desinstalar

```bash
brew uninstall --cask officedaystracker
```

## Paso 5: Actualizar el README

Agrega estas instrucciones de instalación a tu `README.md`:

```markdown
## Instalación con Homebrew

### Instalar

\`\`\`bash
brew tap TU_USUARIO/tap
brew install --cask officedaystracker
\`\`\`

### Actualizar

\`\`\`bash
brew upgrade --cask officedaystracker
\`\`\`

### Desinstalar

\`\`\`bash
brew uninstall --cask officedaystracker
\`\`\`
```

## Publicar Nuevas Versiones

Cuando quieras publicar una nueva versión:

1. **Actualizar la versión** en tu proyecto
2. **Compilar**: `./build_release.sh`
3. **Calcular nuevo SHA256**: `shasum -a 256 build/OfficeDaysTracker.zip`
4. **Crear tag**: `git tag -a v1.0.1 -m "Release v1.0.1"`
5. **Push tag**: `git push origin v1.0.1`
6. **Crear release en GitHub** y subir el ZIP
7. **Actualizar la fórmula** en `homebrew-tap/Casks/officedaystracker.rb`:
   - Cambiar `version`
   - Cambiar `sha256`
8. **Commit y push** del tap:
   ```bash
   cd homebrew-tap
   git add Casks/officedaystracker.rb
   git commit -m "Update OfficeDaysTracker to v1.0.1"
   git push origin main
   ```

## Verificación

Para verificar que tu fórmula está correcta:

```bash
brew audit --cask officedaystracker
brew style --cask officedaystracker
```

## Notas Importantes

- El nombre del repositorio del tap DEBE ser `homebrew-NOMBRE`
- Los usuarios instalarán con: `brew tap USUARIO/NOMBRE` (sin el prefijo "homebrew-")
- El archivo ZIP debe estar en los assets del release de GitHub
- El SHA256 debe coincidir exactamente con el archivo ZIP
- La versión en la fórmula debe coincidir con el tag del release

## Troubleshooting

### Error: "SHA256 mismatch"
- Recalcula el SHA256 del archivo ZIP
- Asegúrate de que el archivo en GitHub es el mismo que compilaste

### Error: "Cask not found"
- Verifica que el repositorio se llame `homebrew-tap`
- Verifica que el archivo esté en `Casks/officedaystracker.rb`
- Haz `brew untap` y vuelve a hacer `brew tap`

### La app no se instala en /Applications
- Verifica que el nombre del archivo .app en el ZIP sea exactamente `OfficeDaysTracker.app`
- Verifica la línea `app "OfficeDaysTracker.app"` en la fórmula
