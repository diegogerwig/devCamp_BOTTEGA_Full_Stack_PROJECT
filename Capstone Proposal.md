# Propuesta de Proyecto de Desarrollo Web

## 1. Título del Proyecto
**EcoTrackr** - Rastreador Personal de Huella de Carbono y Hábitos Sostenibles

## 2. Propósito o Problema a Resolver
El propósito de esta aplicación es abordar la creciente preocupación por el cambio climático y la desconexión entre la conciencia ambiental y la acción individual. El problema específico que resuelve es la falta de una herramienta fácil de usar que permita a los usuarios:
*   **Medir y comprender** su impacto ambiental personal de manera cuantificable (huella de carbono).
*   **Rastrear sus hábitos** diarios relacionados con el consumo de energía, transporte, dieta y residuos.
*   **Recibir recomendaciones personalizadas** y accionables para reducir su impacto.
*   **Visualizar su progreso** a lo largo del tiempo, motivándolos a mantener un estilo de vida más sostenible.

## 3. Usuario Final Previsto
El usuario final principal es un **adulto consciente del medio ambiente**, de entre 20 y 45 años, que:
*   Vive en zonas urbanas o suburbanas.
*   Tiene acceso a un smartphone y/o computadora y está familiarizado con las aplicaciones web.
*   Está interesado en la sostenibilidad pero no sabe por dónde empezar o cómo medir su progreso.
*   Puede estar motivado por comunidades y la comparación saludable (gamificación).

## 4. Tecnologías y Lenguajes a Emplear
Se espera emplear un stack tecnológico moderno y robusto dividido en front-end y back-end:

### Front-end (Cliente)
*   **Lenguaje:** JavaScript (ES6+)
*   **Framework/Librería:** React.js (con Hooks) para construir una interfaz de usuario interactiva y dinámica.
*   **Estilo:** CSS3 con un framework como Tailwind CSS o Bootstrap para un diseño responsive y ágil.
*   **Gráficos:** Una librería como Chart.js o D3.js para visualizar los datos de la huella de carbono y el progreso.

### Back-end (Servidor)
*   **Lenguaje:** JavaScript (Node.js)
*   **Framework:** Express.js para crear la API RESTful.
*   **Base de Datos:** MongoDB (una base de datos NoSQL) con Mongoose como ODM para almacenar datos de usuarios, hábitos y cálculos de huella de carbono.
*   **Autenticación:** JSON Web Tokens (JWT) para la gestión segura de sesiones de usuario.

### Otros
*   **Control de Versiones:** Git y GitHub.
*   **Despliegue:** Servicios como Vercel/Netlify para el front-end y Heroku/Railway para el back-end y la base de datos.

## 5. Cronograma Previsto e Hitos
El desarrollo se dividirá en 4 sprints o hitos principales con una duración total estimada de 10-12 semanas.

| Hito | Tareas Principales | Duración Estimada |
| :--- | :--- | :--- |
| **1. Diseño y Planificación** | Definir requisitos finales, diseñar wireframes y mockups, configurar el entorno de desarrollo y la estructura del proyecto. | 1.5 - 2 semanas |
| **2. Desarrollo del Núcleo (MVP)** | Configurar back-end (API, base de datos, autenticación). Implementar las funcionalidades básicas del front-end: registro, login, formulario de entrada de datos y dashboard básico. | 4 - 5 semanas |
| **3. Funcionalidades Avanzadas** | Implementar gráficos y visualización de datos, sistema de recomendaciones, gamificación (logros, metas) y optimizar la experiencia de usuario (UX). | 3 semanas |
| **4. Pruebas, Revisión y Despliegue** | Realizar pruebas exhaustivas (testing), corregir errores (debugging), optimizar el rendimiento y desplegar la aplicación en un entorno de producción. | 1.5 - 2 semanas |