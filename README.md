# Office Days Tracker

App nativa de macOS para controlar tu asistencia a la oficina mediante detección de red.

## Características

- 🖥️ **App de barra de menú**: Se muestra en la barra superior de macOS
- 🌐 **Detección automática de red**: Detecta el gateway de la red de tu oficina
- ⚙️ **Redes configurables**: Guarda varios gateways de oficina para registrar solo en esas redes
- ⏱️ **Intervalo ajustable**: Configura cada cuánto tiempo verificar la conexión (de 1 minuto a 24 horas)
- 📅 **Registro diario**: Registra automáticamente cada día que asistes a la oficina
- 📊 **Meta mensual**: Muestra tu progreso hacia la meta de 8 días al mes
- 🗓️ **Días hábiles restantes**: Calcula los días hábiles que quedan en el mes (excluyendo feriados de Argentina)
- 🔄 **Auto-inicio**: Opción para iniciar automáticamente al encender tu Mac

## Requisitos

- macOS 13.0 o superior

## Instalación

### 🍺 Instalación con Homebrew (Recomendado)

```bash
brew tap johzero18/tap
brew install --cask officedaystracker
```

Para actualizar:
```bash
brew upgrade --cask officedaystracker
```

### 📦 Instalación con DMG

1. Descarga el archivo `OfficeDaysTracker-Installer.dmg`
2. Abre el archivo DMG
3. Arrastra **OfficeDaysTracker.app** a la carpeta **Applications**
4. Cierra el DMG
5. Abre **OfficeDaysTracker** desde tu carpeta Aplicaciones

**Primera ejecución:**
- macOS puede mostrar un mensaje de seguridad
- Ve a **Preferencias del Sistema** → **Privacidad y Seguridad**
- Haz clic en **"Abrir de todas formas"**
- La app aparecerá en la barra de menú superior (no en el Dock)

## Uso

1. Al iniciar, la app aparece como un icono de edificio 🏢 en la barra de menú
2. Haz clic en el icono para ver:
   - **Estado actual**: Si estás en la oficina o fuera
   - **Registro de hoy**: Si ya se registró tu asistencia del día
   - **Progreso mensual**: Días asistidos vs meta (8 días/mes)
   - **Días hábiles restantes**: Cuántos días quedan en el mes
   - **Lista de días registrados**: Todos los días que asististe este mes
3. **🔄 Actualizar**: Fuerza la verificación del gateway inmediatamente sin esperar al intervalo programado
4. **⚙️ Configuración**: Personaliza tu instalación
   - Haz clic en **"Configuración"** en el menú
   - Configura los gateways de las redes de tu oficina
   - Usa **"Detectar"** y luego **"Usar actual"** para guardar el gateway actual
   - Ajusta el intervalo de chequeo (desde 1 minuto hasta 24 horas)
   - Usa los presets rápidos: 5 min, 15 min, 30 min, 1 hora
5. Activa **"Iniciar al encender la PC"** para que la app se ejecute automáticamente
6. La app verifica automáticamente si estás conectado a la red de la oficina según el intervalo configurado
7. Haz clic en **Salir** cuando quieras cerrar la aplicación

**Nota:** La app NO aparece en el Dock, solo en la barra de menú superior.

**Intervalos recomendados:**
- Para máxima precisión: 5-15 minutos
- Para uso normal: 30-60 minutos (ahorro de batería)
- Intervalos muy cortos (< 5 minutos) pueden consumir más batería

## Desinstalación

### Con Homebrew
```bash
brew uninstall --cask officedaystracker
```

### Manual
1. Arrastra **OfficeDaysTracker.app** desde la carpeta Aplicaciones a la Papelera
2. Vacía la Papelera
3. (Opcional) Elimina las preferencias: `~/Library/Preferences/com.officedaystracker.app.plist`

## Desarrollo

Para compilar y distribuir la app, consulta [HOMEBREW_SETUP.md](HOMEBREW_SETUP.md)