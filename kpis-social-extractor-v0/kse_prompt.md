# Prompt para Crear una Aplicación Web de Extracción de KPIs de Redes Sociales

## Español

### Descripción del Proyecto

Crea una aplicación web llamada "KPIs Social Extractor" utilizando Python y Flask que extraiga automáticamente indicadores clave de rendimiento (KPIs) de perfiles de redes sociales. La aplicación debe utilizar un enfoque híbrido de tres niveles para la extracción de datos: APIs oficiales, web scraping avanzado y simulación de comportamiento humano.

### Requisitos Funcionales

1. **Plataformas Soportadas**:
   - Facebook
   - Instagram
   - YouTube
   - LinkedIn
   - Twitter/X
   - TikTok

2. **Métricas a Extraer**:
   - Número de seguidores/suscriptores
   - Cantidad de publicaciones/contenidos
   - Métricas de engagement (likes, comentarios, compartidos)
   - Tendencias de crecimiento y datos históricos
   - Tasas de engagement y puntuaciones de rendimiento

3. **Sistema de Extracción Híbrido**:
   - **Nivel 1**: Utilizar APIs oficiales cuando estén disponibles
   - **Nivel 2**: Implementar web scraping avanzado con técnicas anti-detección
   - **Nivel 3**: Utilizar simulación de comportamiento humano para plataformas con protección avanzada

4. **Técnicas Anti-Detección**:
   - Aleatorización de huellas digitales del navegador
   - Movimientos de ratón y desplazamiento similares a los humanos
   - Variaciones de tiempo y retrasos naturales
   - Soporte para rotación de proxies
   - Persistencia de sesión

5. **Interfaz de Usuario**:
   - Página principal para ingresar URLs de perfiles sociales
   - Dashboard interactivo para visualizar KPIs
   - Comparativas entre plataformas
   - Recomendaciones basadas en el análisis de datos

### Requisitos Técnicos

1. **Backend**:
   - Python 3.8+ con Flask
   - Estructura modular y escalable
   - Manejo de errores robusto
   - Caché para optimizar rendimiento

2. **Extracción de Datos**:
   - Playwright para web scraping
   - Requests para APIs
   - Sistema de reintentos con backoff exponencial
   - Rotación de user-agents y fingerprints

3. **Frontend**:
   - HTML5, CSS3, JavaScript
   - Bootstrap para diseño responsivo
   - Chart.js para visualizaciones
   - Interfaz intuitiva y profesional

4. **Seguridad**:
   - Limitación de tasa para prevenir sobrecarga
   - Respeto de directivas robots.txt
   - Cumplimiento con términos de servicio de plataformas

### Estructura del Proyecto

```
kpis-social-extractor/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── extractors/
│   │   ├── __init__.py
│   │   ├── base_extractor.py
│   │   ├── facebook_extractor.py
│   │   ├── instagram_extractor.py
│   │   ├── youtube_extractor.py
│   │   ├── linkedin_extractor.py
│   │   ├── twitter_extractor.py
│   │   └── tiktok_extractor.py
│   ├── utils/
│   │   ├── __init__.py
│   │   └── human_simulation.py
│   ├── config/
│   │   ├── __init__.py
│   │   └── config.py
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   └── img/
│   └── templates/
│       ├── index.html
│       └── dashboard.html
├── requirements.txt
├── readme.txt
└── kse_installation.txt
```

### Instrucciones de Implementación

1. Configura el entorno de desarrollo con Python y las dependencias necesarias
2. Implementa la estructura base del proyecto Flask
3. Desarrolla los extractores para cada plataforma social
4. Implementa las técnicas anti-detección y simulación humana
5. Crea los endpoints de API para la extracción de KPIs
6. Desarrolla la interfaz de usuario y el dashboard
7. Realiza pruebas exhaustivas con perfiles reales
8. Documenta la instalación y uso de la aplicación

## English

### Project Description

Create a web application called "KPIs Social Extractor" using Python and Flask that automatically extracts key performance indicators (KPIs) from social media profiles. The application must use a three-tier hybrid approach for data extraction: official APIs, advanced web scraping, and human behavior simulation.

### Functional Requirements

1. **Supported Platforms**:
   - Facebook
   - Instagram
   - YouTube
   - LinkedIn
   - Twitter/X
   - TikTok

2. **Metrics to Extract**:
   - Number of followers/subscribers
   - Number of posts/content
   - Engagement metrics (likes, comments, shares)
   - Growth trends and historical data
   - Engagement rates and performance scores

3. **Hybrid Extraction System**:
   - **Level 1**: Use official APIs when available
   - **Level 2**: Implement advanced web scraping with anti-detection techniques
   - **Level 3**: Use human behavior simulation for platforms with advanced protection

4. **Anti-Detection Techniques**:
   - Browser fingerprint randomization
   - Human-like mouse movements and scrolling
   - Timing variations and natural delays
   - Proxy rotation support
   - Session persistence

5. **User Interface**:
   - Main page for entering social profile URLs
   - Interactive dashboard to visualize KPIs
   - Comparisons between platforms
   - Recommendations based on data analysis

### Technical Requirements

1. **Backend**:
   - Python 3.8+ with Flask
   - Modular and scalable structure
   - Robust error handling
   - Caching for performance optimization

2. **Data Extraction**:
   - Playwright for web scraping
   - Requests for APIs
   - Retry system with exponential backoff
   - User-agent and fingerprint rotation

3. **Frontend**:
   - HTML5, CSS3, JavaScript
   - Bootstrap for responsive design
   - Chart.js for visualizations
   - Intuitive and professional interface

4. **Security**:
   - Rate limiting to prevent overload
   - Respect for robots.txt directives
   - Compliance with platform terms of service

### Project Structure

```
kpis-social-extractor/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── extractors/
│   │   ├── __init__.py
│   │   ├── base_extractor.py
│   │   ├── facebook_extractor.py
│   │   ├── instagram_extractor.py
│   │   ├── youtube_extractor.py
│   │   ├── linkedin_extractor.py
│   │   ├── twitter_extractor.py
│   │   └── tiktok_extractor.py
│   ├── utils/
│   │   ├── __init__.py
│   │   └── human_simulation.py
│   ├── config/
│   │   ├── __init__.py
│   │   └── config.py
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   └── img/
│   └── templates/
│       ├── index.html
│       └── dashboard.html
├── requirements.txt
├── readme.txt
└── kse_installation.txt
```

### Implementation Instructions

1. Set up the development environment with Python and necessary dependencies
2. Implement the base structure of the Flask project
3. Develop extractors for each social platform
4. Implement anti-detection techniques and human simulation
5. Create API endpoints for KPI extraction
6. Develop the user interface and dashboard
7. Perform thorough testing with real profiles
8. Document the installation and use of the application
