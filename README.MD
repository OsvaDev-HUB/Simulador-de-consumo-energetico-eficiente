
**EcoWatts** es una plataforma web moderna diseñada para ayudar a los usuarios a visualizar, analizar y optimizar el consumo eléctrico de su hogar. A través de simulaciones precisas y análisis de datos, permite tomar decisiones informadas para reducir tanto el impacto ambiental como el costo de la factura eléctrica.

## Características Principales

- **Gestión de Aparatos:** CRUD completo para registrar dispositivos eléctricos con potencia (W) y horas de uso.
- **Análisis en Tiempo Real:** Cálculos automáticos de consumo diario/mensual (kWh) y costos proyectados.
- **Visualización Avanzada:** Gráficos interactivos con **Chart.js** para identificar los mayores consumidores.
- **Sistema de Usuarios:** Autenticación segura (Registro/Login) con persistencia de datos individualizada.
- **Simulación de Ahorro:** Herramienta predictiva para visualizar el impacto de reducir el uso en porcentajes específicos.
- **Interfaz Premium:** Diseño moderno con tipografía *Space Grotesk*, efectos de *glassmorphism* y animaciones dinámicas.

## Stack Tecnológico

- **Backend:** Python + Flask
- **Base de Datos:** PostgreSQL + Flask-SQLAlchemy
- **Autenticación:** Flask-Login + Werkzeug Security
- **Frontend:** HTML5, CSS3 (Vanilla), JavaScript (ES6+)
- **Gráficos:** Chart.js
- **Entorno:** python-dotenv para gestión de variables de entorno

## Instalación y Configuración

### 1. Requisitos Previos
- Python 3.10 o superior
- Servidor PostgreSQL activo

### 2. Clonar y Preparar el Entorno
```bash
git clone https://github.com/OsvaDev-HUB/Simulador-de-consumo-energetico-eficiente.git
cd Simulador-de-consumo-energetico-eficiente
```

### 3. Instalar Dependencias
Se recomienda usar un entorno virtual:
```bash
py -m pip install flask flask-sqlalchemy psycopg2-binary flask-login python-dotenv
```

### 4. Configuración de Variables de Entorno
Crea un archivo `.env` en la raíz del proyecto con el siguiente formato:
```env
SECRET_KEY=tu_llave_secreta_aqui
DATABASE_URL=postgresql://usuario:password@localhost:5432/Eco_Watts
```

### 5. Ejecución
```bash
py app.py
```
Accede a `http://127.0.0.1:5000` en tu navegador.

## Configuración de Tarifas
El sistema utiliza actualmente un valor promedio de **$262 CLP por kWh** (Chile, 2024), configurable dentro de la lógica del servidor.
