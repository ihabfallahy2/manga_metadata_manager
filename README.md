# Manga Metadata Manager

Una aplicación de interfaz de línea de comandos (CLI) desarrollada en Python con Textual para gestionar metadatos de manga. Permite añadir directorios de manga y descargar automáticamente metadatos y portadas desde AniList.

## Características

- **Interfaz TUI moderna**: Interfaz de usuario textual intuitiva y fácil de usar
- **Gestión de directorios**: Añadir y gestionar múltiples directorios de manga
- **Descarga automática de metadatos**: Obtiene información de manga desde AniList
- **Descarga de portadas**: Descarga automática de imágenes de portada
- **Sistema de caché inteligente**: Evita reprocesar directorios ya escaneados
- **Barra de progreso en tiempo real**: Muestra el progreso del escaneo
- **Selector de directorios**: Función de browse para seleccionar carpetas sin salir de la aplicación
- **Logs detallados**: Información completa del proceso de escaneo

## Instalación

1. **Clona el repositorio (opcional):**
   Si quieres la última versión de desarrollo, clona el repositorio.
   ```bash
   git clone <repository-url>
   cd manga-metadata-manager
   ```

2. **Instala la aplicación:**
   Desde el directorio clonado, puedes instalar el paquete. Esto también instalará todas las dependencias necesarias.
   ```bash
   pip install .
   ```
   Para desarrollo, usa el modo editable:
   ```bash
   pip install -e .
   ```

## Uso

Una vez instalado, puedes ejecutar la aplicación desde cualquier lugar usando el comando:
```bash
manga-manager
```

### Añadir directorios de manga

1. Presiona `a` o haz clic en "Add Path" para añadir un nuevo directorio
2. Escribe la ruta manualmente o usa el botón "Browse" para seleccionar una carpeta
3. La aplicación validará que el directorio existe y es accesible

### Escanear directorios

1. Presiona `s` o haz clic en "Scan All" para comenzar el escaneo
2. La barra de progreso mostrará el avance en tiempo real
3. Los logs mostrarán información detallada de cada manga procesado
4. Los metadatos se guardarán en una carpeta `metadata` dentro de cada directorio de manga

### Navegación

- `q`: Salir de la aplicación
- `a`: Añadir directorio
- `d`: Eliminar directorio seleccionado
- `s`: Iniciar escaneo
- `r`: Actualizar vista

## Estructura de archivos

```
manga_metadata_manager/
├── main.py                 # Punto de entrada principal
├── requirements.txt        # Dependencias del proyecto
├── src/
│   ├── app.py             # Aplicación principal
│   ├── config/
│   │   └── settings.py    # Configuración de la aplicación
│   ├── core/
│   │   ├── cache.py       # Gestión de caché
│   │   ├── metadata.py    # Gestión de metadatos
│   │   └── scanner.py     # Escáner de directorios
│   ├── services/
│   │   └── anilist.py     # Servicio de AniList API
│   ├── ui/
│   │   ├── screens/       # Pantallas de la interfaz
│   │   └── styles/        # Estilos CSS
│   └── utils/
│       ├── file_manager.py # Utilidades de archivos
│       └── text_utils.py   # Procesamiento de texto
```

## Mejoras implementadas

### Funcionalidad de Browse
- Integración con tkinter para selección de directorios
- Fallback automático si tkinter no está disponible
- Validación de permisos y accesibilidad

### Barra de progreso mejorada
- Progreso en tiempo real con porcentaje
- Información de carpeta actual siendo procesada
- ETA (tiempo estimado) de finalización
- Actualización fluida sin bloqueos

### Sistema de caché optimizado
- Auto-guardado cada 30 segundos
- Limpieza automática de entradas antiguas
- Metadatos detallados de cada entrada
- Gestión de errores y reintentos
- Exportación de información de caché

### Mejoras de UX
- Interfaz más responsiva
- Mejor manejo de errores
- Logs más detallados y organizados
- Estilos CSS mejorados

## Configuración

La aplicación utiliza los siguientes archivos de configuración:

- `config.json`: Directorios de manga configurados
- `cache.json`: Caché de directorios procesados

## API de AniList

La aplicación utiliza la API pública de AniList para obtener metadatos de manga. No se requiere autenticación para las consultas básicas.

## Requisitos del sistema

- Python 3.7+
- Conexión a internet para descargar metadatos
- Permisos de escritura en los directorios de manga

## Solución de problemas

### Error de tkinter
Si el botón "Browse" aparece deshabilitado, significa que tkinter no está disponible. Puedes:
- Instalar tkinter: `sudo apt-get install python3-tk` (Ubuntu/Debian)
- Usar rutas manuales en su lugar

### Errores de permisos
Asegúrate de que la aplicación tenga permisos de lectura y escritura en los directorios de manga.

### Problemas de red
Si hay problemas para descargar metadatos, verifica tu conexión a internet y que AniList esté accesible.

## Calidad de Código

Este proyecto utiliza `black` para el formateo de código y `ruff` para el linting. Para asegurar la consistencia del código, por favor ejecuta las siguientes herramientas antes de hacer un commit.

1. **Instala las dependencias de desarrollo:**
```bash
pip install -r requirements.txt
```

2. **Formatea el código con Black:**
```bash
black .
```

3. **Verifica y corrige problemas de linting con Ruff:**
```bash
ruff check . --fix
```

## Contribuir

Las contribuciones son bienvenidas. Por favor:
1. Fork el proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo LICENSE para más detalles.
