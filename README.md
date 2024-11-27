Certificado de Alcaldía Kennedy

Descripción

Esta aplicación permite gestionar usuarios y radicados asociados mediante una base de datos PostgreSQL y una interfaz web desarrollada con Flask. Además, incluye funcionalidades para generar reportes PDF, manejar archivos CSS/SCSS y compilar estilos en tiempo real.

Requisitos previos

Antes de ejecutar la aplicación, asegúrate de tener instalados los siguientes componentes:

Python (versión 3.8 o superior).

PostgreSQL (con una base de datos configurada).

Node.js y npm (para gestionar dependencias relacionadas con SCSS, si es necesario).

Las siguientes librerías de Python:

Flask

SQLAlchemy

pdfkit

pandas

PyPDF2

reportlab

watchdog

sass

Instalación

1. Clonar el repositorio

Clona este repositorio en tu máquina local:

git clone <URL_DEL_REPOSITORIO>
cd <NOMBRE_DEL_REPOSITORIO>

2. Crear un entorno virtual

Crea y activa un entorno virtual para gestionar las dependencias:

python -m venv venv
source venv/bin/activate # En Windows: venv\Scripts\activate

3. Instalar las dependencias

Instala todas las dependencias necesarias listadas en el archivo requirements.txt:

pip install -r requirements.txt

4. Configurar la base de datos

Asegúrate de tener PostgreSQL ejecutándose y una base de datos llamada certificado creada.

Actualiza la cadena de conexión a la base de datos en el archivo database.py si es necesario:

DATABASE_URL = "postgresql://USUARIO:CONTRASEÑA@localhost:5432/certificado"

Crea las tablas necesarias ejecutando el siguiente comando:

python database.py

Esto mostrará un mensaje indicando que las tablas se crearon exitosamente.

5. Configurar CSS/SCSS

La aplicación usa archivos SCSS para los estilos. Para compilar los estilos, ejecuta:

python watch_scss.py

Este comando activará un monitor que recompilará los archivos SCSS ubicados en static/scss cada vez que detecte cambios. Los estilos compilados se generarán en static/css.

6. Instalar wkhtmltopdf

La generación de PDFs requiere wkhtmltopdf. Instálalo en tu sistema:

En Linux:

sudo apt-get install wkhtmltopdf

En macOS:

brew install --cask wkhtmltopdf

En Windows, descárgalo desde wkhtmltopdf.org y agrégalo a tu PATH.

Ejecución de la aplicación

Activa el entorno virtual:

source venv/bin/activate # En Windows: venv\Scripts\activate

Inicia la aplicación Flask:

python app.py

Accede a la aplicación en tu navegador en:

http://127.0.0.1:5000

Estructura del proyecto

.
├── app.py                  # Lógica principal de la aplicación
├── database.py             # Configuración y modelos de la base de datos
├── watch_scss.py           # Script para compilar archivos SCSS
├── requirements.txt        # Lista de dependencias de Python
├── static/
│   ├── css/                # Archivos CSS generados
│   ├── scss/               # Archivos SCSS fuente
├── templates/              # Plantillas HTML
└── README.md               # Documentación

Funcionalidades principales

Gestor de usuarios:

Crear, leer, actualizar y eliminar usuarios.

Manejo de campos como nombre, cédula, CPS, fechas y valores.

Gestor de radicados:

Asociar radicados a usuarios.

Generación de identificadores únicos.

Generación de reportes PDF:

Exportar datos a formatos PDF usando wkhtmltopdf y reportlab.

Compilación automática de SCSS:

Soporte para la compilación y monitoreo de cambios en los archivos SCSS mediante python watch_scss.py.

Contribuciones

Si deseas contribuir a este proyecto, envía un pull request o abre un issue en el repositorio.
