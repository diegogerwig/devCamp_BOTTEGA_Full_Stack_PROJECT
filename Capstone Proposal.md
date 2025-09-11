# Propuesta de Proyecto de Desarrollo Web

## 1. Título del Proyecto
**TimeTracer** - Gestión Inteligente de Ausencias y Jornada Laboral

## 2. Propósito o Problema a Resolver
El propósito de esta aplicación es modernizar y digitalizar la gestión de la asistencia y las ausencias en el entorno laboral. El problema específico que resuelve es la ineficiencia de los sistemas tradicionales (hojas de cálculo, papel) para:
*   **Centralizar y automatizar** la solicitud y aprobación de vacaciones, permisos y días libres.
*   **Registrar de forma fiable** la jornada laboral diaria (entradas y salidas) de cada empleado.
*   **Reducir errores administrativos** y proporcionar una visión clara y en tiempo real del calendario de ausencias de toda la empresa.
*   **Empoderar a los empleados** dándoles acceso inmediato al estado de sus solicitudes y su historial, mejorando la transparencia.

## 3. Usuario Final Previsto
La aplicación está dirigida a tres tipos de usuarios finales dentro de una pequeña o mediana empresa:
*   **Administradores (HR/Admin):** Personal de recursos humanos o administración que necesita acceso total para gestionar usuarios, roles y auditar toda la actividad.
*   **Jefes de equipo/Managers:** Responsables de departamento que necesitan aprobar o rechazar solicitudes de su equipo y supervisar su asistencia.
*   **Trabajadores/Empleados:** El resto de la plantilla, que necesita solicitar días libres y registrar sus horarios de entrada y salida de forma sencilla.

## 4. Tecnologías y Lenguajes a Emplear
Se empleará un stack tecnológico robusto y moderno, dividido en front-end y back-end:

### Front-end (Cliente)
*   **Lenguaje:** JavaScript (ES6+)
*   **Framework/Librería:** React.js (con Hooks y Context API o Redux para gestión de estado) para construir una interfaz de usuario interactiva, dinámica y SPA.
*   **Estilo:** CSS3 con un framework como **Tailwind CSS** para un diseño utilitario, responsive y ágil.
*   **Gráficos:** Chart.js para visualizaciones de resumen de horas o ausencias (si se requirieran).

### Back-end (Servidor)
*   **Lenguaje:** Python
*   **Framework:** Flask (junto con bibliotecas como Flask-SQLAlchemy, Flask-JWT-Extended, Flask-CORS).
*   **Base de Datos:** PostgreSQL, una base de datos relacional y SQL robusta ideal para datos estructurados como usuarios, roles y registros de tiempo.
*   **Autenticación:** JSON Web Tokens (JWT) para la gestión segura de sesiones y autorización de roles.

### Despliegue y Control de Versiones
*   **Despliegue:** **Render.com** para ambos entornos (Back-end como Web Service y PostgreSQL como base de datos add-on; Front-end como Static Site).
*   **Control de Versiones:** Git y GitHub.

## 5. Cronograma Previsto e Hitos
El desarrollo se dividirá en 4 sprints o hitos principales con una duración total estimada de 10-12 semanas.

| Hito | Tareas Principales | Duración Estimada |
| :--- | :--- | :--- |
| **1. Diseño y Modelado** | Definir requisitos y modelos de datos (User, TimeLog, TimeOffRequest). Diseñar wireframes y esquema de la DB. Configurar entornos. | 1.5 - 2 semanas |
| **2. Desarrollo del Núcleo (MVP)** | Configurar back-end (API Flask, modelos SQLAlchemy, auth JWT). Implementar funcionalidades básicas del front-end: Login, Registro de jornada y Dashboard de usuario. | 4 - 5 semanas |
| **3. Gestión de Ausencias y Roles** | Implementar flujo completo de solicitud/aprobación de vacaciones. Desarrollar vistas específicas para Admin y Jefes. Crear paneles de gestión. | 3 semanas |
| **4. Pulido, Pruebas y Despliegue** | Realizar pruebas de integración y de usuario. Pulir la UI/UX, optimizar el código y realizar el despliegue final en **Render.com**. | 1.5 - 2 semanas |