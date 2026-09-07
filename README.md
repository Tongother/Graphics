# Proyecto de graficacion

Aplicacion de escritorio desarrollada en Python con Tkinter y Matplotlib. Permite calcular y graficar la recta que pasa por dos puntos.

## Requisitos

- Python 3.10 o superior
- Git, si se va a clonar el repositorio
- Tkinter, incluido normalmente en Python para Windows

## Instalacion en Windows

1. Clona el repositorio y entra a la carpeta del proyecto:

```powershell
git clone <URL_DEL_REPOSITORIO>
cd code
```

Si ya tienes el proyecto descargado, solo abre PowerShell en la carpeta raiz del proyecto.

2. Crea el entorno virtual:

```powershell
python -m venv .venv
```

3. Activa el entorno virtual:

```powershell
.\.venv\Scripts\Activate.ps1
```

Si PowerShell bloquea la activacion, ejecuta una vez en esa terminal:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

Despues vuelve a activar el entorno:

```powershell
.\.venv\Scripts\Activate.ps1
```

4. Instala las dependencias:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Ejecucion

Con el entorno virtual activo, ejecuta:

```powershell
python main.py
```

Se abrira la ventana principal de la aplicacion. Para cerrar el entorno virtual cuando termines:

```powershell
deactivate
```

## Actualizar las dependencias

Despues de instalar o actualizar paquetes, puedes volver a congelar las versiones instaladas:

```powershell
python -m pip freeze > requirements.txt
```

En otra computadora, las mismas versiones se instalan con:

```powershell
python -m pip install -r requirements.txt
```

## Estructura principal

```text
.
├── main.py
├── requirements.txt
├── components/
│   └── Button.py
└── pages/
    ├── Futuro.py
    ├── index.py
    └── puntos_colineales.py
```
