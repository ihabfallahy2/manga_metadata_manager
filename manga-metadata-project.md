# Manga Metadata Manager

Un gestor de metadatos para colecciones de manga con interfaz TUI (Terminal User Interface) construido con Textual.

## Estructura del Proyecto

```
manga-metadata-manager/
├── README.md
├── requirements.txt
├── setup.py
├── .gitignore
├── main.py
├── src/
│   ├── __init__.py
│   ├── app.py
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── cache.py
│   │   ├── metadata.py
│   │   └── scanner.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── anilist.py
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── screens/
│   │   │   ├── __init__.py
│   │   │   ├── add_path.py
│   │   │   └── scan.py
│   │   └── styles/
│   │       ├── __init__.py
│   │       └── app.css
│   └── utils/
│       ├── __init__.py
│       ├── file_manager.py
│       └── text_utils.py
└── tests/
    ├── __init__.py
    ├── test_metadata.py
    ├── test_scanner.py
    └── test_utils.py
```

## Instalación

```bash
git clone <repository-url>
cd manga-metadata-manager
pip install -r requirements.txt
```

## Uso

```bash
python main.py
```

## Características

- ✅ Interfaz de usuario en terminal (TUI)
- ✅ Búsqueda automática de metadatos en AniList
- ✅ Gestión de múltiples rutas de manga
- ✅ Sistema de caché para evitar búsquedas duplicadas
- ✅ Descarga automática de portadas
- ✅ Limpieza inteligente de títulos
- ✅ Progreso visual durante el escaneo

## Tecnologías

- **Textual**: Framework para interfaces de usuario en terminal
- **Requests**: Cliente HTTP para APIs
- **AniList API**: Base de datos de anime y manga

## Contribuir

Las contribuciones son bienvenidas. Por favor, abre un issue antes de hacer cambios importantes.

## Licencia

MIT License