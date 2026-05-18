# ejem1

Aplicación de ejemplo en Python con layout `src/`, CLI y tests con pytest.

## Instalación

Crea y activa un entorno virtual, luego instala el paquete en modo editable:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Ejecución de tests

Con el entorno activado:

```bash
# Todos los tests
pytest

# Un test concreto
pytest tests/test_main.py::test_main
```

## Arrancar la aplicación

Una vez instalado, el comando `ejem1` queda disponible en el entorno:

```bash
ejem1
```

También puedes ejecutarlo directamente con Python:

```bash
python -m ejem1.main
```

## Estructura del proyecto

```
.
├── src/
│   └── ejem1/
│       └── main.py        # Punto de entrada de la aplicación
├── tests/
│   └── test_main.py       # Tests de pytest
└── pyproject.toml
```

## Instalar el cliente de GitHub 

Pasos para instalar el cliente de GitHub

```
# Instalar gh CLI
sudo apt install gh

# Autenticarse
gh auth login

# Crear el repositorio
gh repo create Ejem1-Project --public --description "Proyecto de ejemplo"
```

## Conectar Claude Code con GitHub vía MCP

### Paso 1. Crear un Personal Access Token en GitHub

Se crea un token en GitHub

Almacenar de forma segura el token.


```
# 1. Crea un archivo .env en la raíz del proyecto
echo "GITHUB_PAT=tu_token_aqui" > .env

# 2. Añádelo a .gitignore para no exponer el token
echo -e ".env\n.mcp.json" >> .gitignore
```

### Paso 2. Registra el GitHub MCO Server en Claude Code.

Ejecutamos desde la línea de comando la definición del MCP 

```
# Leyendo el token desde .env (recomendado)
claude mcp add-json github \
  '{"type":"http","url":"https://api.githubcopilot.com/mcp","headers":{"Authorization":"Bearer '"$(grep GITHUB_PAT .env | cut -d '=' -f2)"'"}}'
```



### Paso 3. Verificar la conexión

Para verificar que está conectado desde la línea de comando:
```
claude mcp list
```

Para verificar que está conectado desde la Consola de CC: teclear el comando ==/mcp==