# Proyecto: Prototipo 1 - Estructura arquitectónica simple

# Equipo
**Nombre:** 2B

**Integrantes:** 

- Santiago Barrera Berrio
- Cristian Alejandro Beltran Rojas
- Daniel Felipe Montenegro Herrera
- Breyner Ismael Ciro Otero
- Juan Felipe Fontecha Vasquez
- Miguelangel Mosquera

# Sistema de Software

**Nombre del Software:** OSP - Overwatch Sentinel Platform

**Logo:** 

![Logo-CapriBlue](https://github.com/user-attachments/assets/4e00fde1-3738-4922-8777-0c1bc1cc4965)


**Descripción:** OSP (Overwatch Sentinel Platform) es una plataforma de software para la vigilancia automatizada basada en visión por computadora, diseñada para funcionar sobre hardware de bajo consumo como Raspberry Pi. Utiliza la implementación pi-tensorflow-lite-object-detection, la cual permite detectar objetos definidos previamente dentro del campo visual de la cámara.

El sistema permite configurar un área específica dentro de la imagen —conocida como zona segura— que delimita el espacio de vigilancia. Cuando un objeto de interés entra en dicha zona, el sistema activa automáticamente la grabación de video. De este modo, se optimiza el uso de recursos, ya que solo se almacena material cuando se detecta actividad relevante.

Los videos generados se almacenan en un servidor central accesible mediante una página web bajo el protocolo HTTPS, y su consulta está restringida a usuarios autenticados mediante credenciales válidas.

Esta solución está orientada a escenarios donde se requiere supervisión eficiente y automática, con un diseño modular que permitirá, en futuras fases, incluir funcionalidades adicionales como el seguimiento (tracking) y el monitoreo continuo de objetos.


# Estructuras Arquitectonicas

## Estructura Componente y Conector (C&C)
### C&C View
### Descripción de los estilos arquitectónicos utilizados

El sistema OSP —Overwatch Sentinel Platform— adopta de forma integral el estilo arquitectónico basado en microservicios, aplicado coherentemente desde el procesamiento local en dispositivos Raspberry Pi hasta los servicios del backend en la nube y la interfaz web del frontend.

La arquitectura de microservicios implica descomponer el sistema en componentes autónomos, cada uno con una responsabilidad bien definida, que interactúan entre sí a través de interfaces ligeras (REST API sobre HTTP/HTTPS). Cada microservicio es desplegado, escalado y gestionado de forma independiente, permitiendo una mayor resiliencia, escalabilidad y facilidad de evolución del sistema.

Características clave de esta adopción:

Cada módulo del sistema cumple con el principio de única responsabilidad (Single Responsibility Principle), actuando como un microservicio incluso si reside en el borde (Edge).

Se fomenta el bajo acoplamiento entre servicios y la alta cohesión interna.

Las interfaces entre microservicios están bien definidas y utilizan formatos estandarizados como JSON y HTTP REST.

Se permite la integración tecnológica heterogénea: por ejemplo, Python en Raspberry Pi, Node.js o Flask en Backend, y React en Frontend, sin afectar la interoperabilidad.

Esta estrategia facilita el despliegue incremental, la automatización, la resiliencia ante fallos parciales y la futura extensión del sistema con nuevos servicios (como seguimiento de objetos, análisis forense, etc.).


### Descripción de elementos arquitectónicos y relaciones

A continuación se describen los principales elementos del sistema organizados como microservicios, y sus interacciones:

Microservicios del Componente Raspberry Pi (Edge Node)

Servicio de detección de objetos (object-detector-ms):
Microservicio local encargado de procesar el flujo de video en tiempo real con TensorFlow Lite, identificar objetos de interés y generar eventos.

Servicio de monitoreo de zona segura (safe-zone-ms):
Evalúa si los objetos detectados entran en el área previamente definida como segura y genera alertas cuando se viola.

Servicio de grabación (recorder-ms):
Escucha eventos del servicio safe-zone-ms y graba video solo cuando es necesario, almacenándolo localmente.

Servicio de envío de logs (log-dispatcher-ms):
Envía eventos en formato JSON al backend a través de una API REST.

Servicio de sincronización de videos (video-uploader-ms):
Sube los videos al sistema de almacenamiento en la nube usando autenticación y claves seguras.

Servicio de limpieza local (cleanup-ms):
Ejecuta tareas programadas (cron) para eliminar archivos y logs antiguos.

Microservicios del Backend (Cloud Node)

Servicio de autenticación (auth-ms):
Gestiona el login federado y emite tokens JWT que permiten el acceso controlado a los servicios protegidos.

Servicio de ingestión de logs (log-ingestor-ms):
Recibe los logs enviados desde múltiples Raspberry Pi y los almacena en la base de datos NoSQL (p. ej., MongoDB).

Servicio de gestión de metadatos (metadata-ms):
Maneja los datos estructurados asociados a usuarios, cámaras y videos. Utiliza una base de datos SQL (p. ej., PostgreSQL).

Servicio de consulta de videos (video-access-ms):
Genera URLs seguras (presigned) para permitir el acceso controlado a los archivos de video almacenados en la nube.

Servicio de interfaz API Gateway (gateway-ms):
Centraliza la entrada al sistema, validando tokens, redirigiendo las peticiones a los microservicios internos y agregando resultados.

Microservicios del Frontend (Web Client)

Servicio SPA de cliente (frontend-ui-ms):
Microservicio ejecutado en el navegador, desarrollado como una Single Page Application (SPA). Consume las APIs del gateway, muestra dashboards y permite al usuario autenticado consultar logs y visualizar videos.

Servicio de gestión de sesión (session-manager-ms):
Localmente gestiona la validez del token JWT, expira sesiones y restringe el acceso según los permisos del usuario.

Relaciones entre microservicios

Comunicación sincrónica vía REST: Todos los microservicios se comunican a través de interfaces RESTful sobre HTTPS, con intercambio de datos en formato JSON.

Autenticación y autorización: Todos los servicios protegidos verifican la validez del token JWT emitido por el auth-ms. Los permisos de acceso a logs o videos están vinculados al ID de usuario.

Integración de datos: log-ingestor-ms y metadata-ms sincronizan los datos provenientes del Edge para generar un historial completo de actividad por usuario/cámara.

Desacoplamiento total: El frontend no interactúa directamente con servicios internos del backend, sino a través del gateway-ms, lo que permite cambiar o actualizar servicios sin afectar al cliente.

Escalabilidad horizontal: Cada microservicio puede ser escalado de forma independiente según la carga (por ejemplo, múltiples instancias de video-access-ms si hay alta demanda de reproducción de video).

Esta arquitectura promueve un diseño distribuido robusto, en el cual cada elemento puede fallar o evolucionar sin comprometer el sistema global.
______________________________________________________________________________________________________________________________________________________________________________

## 1. Objective

The objective of the first delivery of the project is to build a **vertical prototype** of a software system, based on an **initial architectural design**.

## 2. Requirements

### 2.1. Functional Requirements

* The domain and the functional approach for the software system must be defined by the team.
* The functional scope of the prototype must be defined by the team.

### 2.2. Non-Functional Requirements

* The software system must follow a **distributed** architecture.
* The software system must include at least one **presentation**-type **component** (a web front-end).
* The software system must include a set of **logic**-type **components**.
* The software system must include a set of **data**-type **components** (a relational database and a NoSQL database).
* The software system must include at least two different types of **HTTP**-based **connectors**.
* The software system must be built using at least two different general-purpose programming languages.
* The deployment of the software system must be **container**-oriented.

## 3. Delivery

### 3.1. Artifact

~~Team~~
~~- Name (1a, 1b, ..., 2a, 2b, ...)~~
~~- Full names of the team members.~~
* Software System
  ~~- Name~~
  ~~- Logo~~
  ~~- Description~~
* Architectural Structures
  - Component-and Connector (C&C) Structure
    + C&C View
    + Description of architectural styles used.
    + Description of architectural elements and relations.
* Prototype
  - Instructions for deploying the software system locally.
