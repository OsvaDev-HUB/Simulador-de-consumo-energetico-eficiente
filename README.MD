# EcoWatts

**EcoWatts** es una plataforma web moderna diseñada para ayudar a los usuarios a visualizar, analizar y optimizar el consumo eléctrico de su hogar. A través de simulaciones precisas y análisis de datos, permite tomar decisiones informadas para reducir tanto el impacto ambiental como el costo de la factura eléctrica.

## Características Principales

- **Gestión de Aparatos:** CRUD completo para registrar dispositivos eléctricos con potencia (W) y horas de uso.
- **Análisis en Tiempo Real:** Cálculos automáticos de consumo diario/mensual (kWh) y costos proyectados.
- **Visualización Avanzada:** Gráficos interactivos con **Chart.js** para identificar los mayores consumidores.
- **Sistema de Usuarios:** Autenticación segura (Registro/Login) con persistencia de datos individualizada y protección CSRF.
- **Simulación de Ahorro:** Herramienta predictiva para visualizar el impacto de reducir el uso en porcentajes específicos.
- **Sugerencias Inteligentes:** Algoritmo dinámico que sugiere recortes factibles y muestra el impacto económico exacto.
- **Interfaz Premium:** Diseño moderno con tipografía *Space Grotesk*, efectos de *glassmorphism* y animaciones dinámicas.

## Stack Tecnológico

- **Backend:** Python + Flask (Application Factory & Blueprints)
- **Base de Datos:** PostgreSQL + Flask-SQLAlchemy
- **Autenticación y Seguridad:** Flask-Login + Flask-WTF (CSRF) + Werkzeug Security
- **Frontend:** HTML5, CSS3 (Vanilla), JavaScript (Módulos ES6+)
- **Gráficos:** Chart.js v4
- **Entorno:** python-dotenv y Docker

## Instalación y Configuración

### 1. Requisitos Previos
- Python 3.10 o superior
- Servidor PostgreSQL activo (o Docker instalado)

### 2. Clonar el Proyecto
```bash
git clone https://github.com/OsvaDev-HUB/Simulador-de-consumo-energetico-eficiente.git
cd Simulador-de-consumo-energetico-eficiente
```

### 3. Configuración de Variables de Entorno
Copia el archivo de ejemplo para crear tu propio archivo `.env`:
```bash
cp .env.example .env
```
Luego edita el archivo `.env` agregando tu `SECRET_KEY` segura y los datos de tu base de datos PostgreSQL.

---

### Opción A: Ejecución Local (Nativa)

**1. Instalar Dependencias:**
Se recomienda usar un entorno virtual:
```bash
py -m venv venv
venv\Scripts\activate  # En Windows
pip install -r requirements.txt
```

**2. Ejecución:**
```bash
python run.py
```
Accede a `http://127.0.0.1:5000` en tu navegador.

---

### Opción B: Ejecución con Docker

Si tienes Docker instalado, puedes desplegar la aplicación y su base de datos PostgreSQL en un solo comando:
```bash
docker-compose up -d --build
```
La aplicación estará disponible en `http://localhost:5000`.

---

## Configuración de Tarifas
Toda la lógica de cálculo y proyecciones monetarias se basa en la tarifa real confirmada para Chile (2024-2025) de **$236 CLP por kWh**. Este valor es fácilmente modificable en la variable estática `TARIFA_KWH` dentro de `app/config.py`.
