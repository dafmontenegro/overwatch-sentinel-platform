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

El sistema OSP (Overwatch Sentinel Platform) adopta de forma integral el estilo arquitectónico basado en microservicios, aplicado coherentemente desde el procesamiento local en dispositivos Raspberry Pi hasta los servicios del backend y la interfaz web del frontend.

La arquitectura de microservicios implica descomponer el sistema en componentes autónomos, cada uno con una responsabilidad bien definida, que interactúan entre sí a través de interfaces ligeras (REST API sobre HTTP/HTTPS). Cada microservicio es desplegado, escalado y gestionado de forma independiente, permitiendo una mayor resiliencia, escalabilidad y facilidad de evolución del sistema.

**Características clave de esta adopción:**

1. Cada módulo del sistema cumple con el principio de única responsabilidad (Single Responsibility Principle), actuando como un microservicio incluso si reside en el borde (Edge).

2. Se fomenta el bajo acoplamiento entre servicios y la alta cohesión interna.

3. Las interfaces entre microservicios están bien definidas y utilizan formatos estandarizados como JSON y HTTP REST.

4. Se permite la integración tecnológica heterogénea: por ejemplo, Python en Raspberry Pi, Node.js o Flask en Backend, y React en Frontend, sin afectar la interoperabilidad.

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


# Prototipo

1. Descargar o clonar el repositorio alojado en [!LINK]
2. Verificar que Docker se encuentre en ejecución, en caso de no estarlo este debe ser inicializado.

   ![image](https://github.com/user-attachments/assets/792afc9b-2f21-4c0d-984a-e0e95655e753)

3. Descargar los dos (2) archivos ".env" proporcionados vía (pendiente slack o acceso a drive)
4. Colocar el archivo *.env* correspondiente al backend en las rutas *"...\overwatch-sentinel-platform-master\Compact_backend"* y *"...\overwatch-sentinel-platform-master"*.

   ![image](https://github.com/user-attachments/assets/1a096ccc-a076-462e-89a3-784cca5f8140)

   
5. Colocar el archivo *.env* correspondiente al frontend en la ruta *"...\overwatch-sentinel-platform-master\osp-frontend"*

   ![image](https://github.com/user-attachments/assets/f6230491-f24c-4b50-8952-4d01bea73894)

   
6. Posicionarse en la carpeta raiz *"...\overwatch-sentinel-platform-master"*, abrir una terminal y ejecutar las siguientes instrucciones.
   
   6.1. docker-compose build --no-cache

   ![image](https://github.com/user-attachments/assets/3f6230bb-48da-4452-91eb-046e9cd028c1)

   Se mostrará el resultado del Building para *web-backend* y *web-frontend*

   ![image](https://github.com/user-attachments/assets/88729237-e992-48e5-81f3-e0dd46c9998f)

   6.2. docker-compose up -d

   ![image](https://github.com/user-attachments/assets/6f33f92d-45ea-46ef-bd66-199185315d2b)

   Se mostrará en pantalla la correcta creación de los Contenedores.

   ![image](https://github.com/user-attachments/assets/c8a5f356-307d-4d25-a08c-feb103cb696b) 
  
7. Verificar la creación de los contenedores y de las imagenes en docker, y verificar que todos se encuentren ejecutando.

   **Contenedores:**

   ![image](https://github.com/user-attachments/assets/dbf5819b-eb79-4734-8508-a66f92a7ba7d)

   ![image](https://github.com/user-attachments/assets/8a6179f1-f8fa-4c9d-b455-fda0ecb85bea)

   **Imagenes:**
   
   ![image](https://github.com/user-attachments/assets/042eb701-b795-49d8-b25b-695d452e77c8)

   ![image](https://github.com/user-attachments/assets/1b15bf25-53a1-4cad-a505-581aba0e9774)

8. Ejecutar el archivo de prueba .................................

8. Comprobar la ejecución del backend.

   Abrir el navegador de preferencia y verificar las siguientes direcciones:
   
   8.1. **http://localhost:8000:** Se visualizará el mensaje *{"message":"Welcome to the backend called logic system"}*, el cual indica que el servicio de backend está                      corriendo correctamente.
        ![image](https://github.com/user-attachments/assets/4bca01ef-1db7-489c-aa8d-53c2fe2570f9)

   8.2. **http://localhost:8000/video:** Se puede apreciar la captura de video en vivo.
        ![Sin título](https://github.com/user-attachments/assets/a68e4551-1f87-438b-b481-265cb64ef7cc)

   8.3. **http://localhost:8000/auth/google:** Permite probar el inicio de sesión utilizando el servicio de OAuth2 de Google Cloud. Se debe seleccionar la cuenta a utilizar.
        ![Sin título](https://github.com/user-attachments/assets/2521c2d5-35d1-4dbf-ad27-3610d8d1a0ac)
        Pulsar en *Continuar*
        ![image](https://github.com/user-attachments/assets/9ca585e5-7e82-453e-859b-ebe8a1a33eb7)
        Se puede apreciar el token de acceso, lo cual indica una autenticación exitosa.

      **Nota:** El token solamente es visible para el usuario que se loguea, no es visible para usuaios diferentes.  
        ![image](https://github.com/user-attachments/assets/e114c966-1be6-43d8-b047-fd7b45f3863d)

   8.4. **http://localhost:8000/logs:** Muestra todos los eventos sucedidos en el lapso de tiempo que ha estado trabajando la captura de video.
        ![image](https://github.com/user-attachments/assets/f85dad98-27e2-42bd-ac3f-b2d38eb096b9)

10. Verificar la ejecución del frontend.
    
    10.1. Abrir el navegador de preferencia y verificar la siguiente dirección: **http://localhost:5173/**
    
    10.2. Se mostrará la página principal del sistema.
          ![image](https://github.com/user-attachments/assets/f02b7177-c185-4f99-8c60-b18d12c07d0f)

    10.3. Para acceder a la imagen en vivo se puede presionar sobre *"Acceder al Sistema"* o sobre *"Video en Vivo"*.
          ![image](https://github.com/user-attachments/assets/a32873fb-9005-44ed-b220-e4d8a591682f)
          ![image](https://github.com/user-attachments/assets/ea32eb4c-420b-48f3-8c34-f84697bfc9a0)

    10.4. Se puede apreciar la transmisión de video en vivo.
          ![Sin título](https://github.com/user-attachments/assets/b984e195-7e86-4cda-83a0-e4f161f66c3b)

    10.5. La transmisión puede ser pausada y reanudada pulsando sobre el ícono de play/pause.
          ![image](https://github.com/user-attachments/assets/6be22fb6-077e-40d7-b787-6edec11578c0)


_____________________________________________________________________________________________________________________________________________________________________________

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
