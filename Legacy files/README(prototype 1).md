# Proyecto: Prototipo 1 - Estructura arquitectónica simple

# Equipo
**Nombre:** 2BMore actions

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


**Descripción:** OSP (Overwatch Sentinel Platform) es una plataforma de software para la vigilancia automatizada basada en visión por computadora, diseñada para funcionar sobre hardware de bajo consumo como Raspberry Pi. Utiliza la implementación [pi-tensorflow-lite-object-detection](https://github.com/dafmontenegro/pi-tensorflow-lite-object-detection), la cual permite detectar objetos definidos previamente dentro del campo visual de la cámara.

El sistema permite configurar un área específica dentro de la imagen —conocida como zona segura— que delimita el espacio de vigilancia. Cuando un objeto de interés entra en dicha zona, el sistema activa automáticamente la grabación de video. De este modo, se optimiza el uso de recursos, ya que solo se almacena material cuando se detecta actividad relevante.

Esta solución está orientada a escenarios donde se requiere supervisión eficiente y automática, con un diseño modular que permitirá, en futuras fases, incluir funcionalidades adicionales como el seguimiento (tracking) y el monitoreo continuo de objetos.


# Estructuras Arquitectonicas

## Estructura Componente y Conector (C&C)
### C&C View

![CyC drawio](https://github.com/user-attachments/assets/1a7a53ca-c2a2-4e49-b266-8eecea4c1be2)


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

La arquitectura del sistema OSP se compone de tres dominios principales —Frontend, Backend y Raspberry Pi (Edge)—, cada uno diseñado como una colección de microservicios independientes que se comunican mediante interfaces RESTful sobre HTTPS. A continuación se describen los elementos arquitectónicos y sus relaciones:

**1. Microservicios en el Componente Raspberry Pi (Edge):** 

- **osp-raspberrypi-ms:** Microservicio local que agrupa múltiples tareas en la Raspberry Pi, incluyendo la detección de objetos, evaluación de la zona segura, grabación de video y sincronización de datos. Expone una API REST mínima para enviar logs al backend.

- **Relación:**

   - Envía eventos al backend (osp-backend-ms) mediante interfaces REST con mensajes JSON.

   - Sube los videos grabados a un almacenamiento en la nube externo (representado como nube externa en el modelo).

**2. Microservicios en el Backend**

- **osp-backend-ms:** Microservicio central que recibe, valida y persiste los datos enviados por las Raspberry Pi. Internamente, realiza las siguientes funciones:

   - Gestión de autenticación federada (conexión a Google OAuth2).

   - Recepción y persistencia de logs desde los nodos Raspberry.

   - Generación de respuestas al frontend con datos y videos filtrados por usuario.

- **Bases de Datos:**

   - **PostgreSQL:** Almacena usuarios, permisos, metadatos de videos, y configuración del sistema.

   - **MongoDB:** Almacena los logs generados por los dispositivos en formato JSON.

   - **auth_db:** Contiene tokens, sesiones y credenciales de acceso autenticadas.

   - **logs_db:** Esquema especializado para búsquedas de eventos históricos.

- **Relación:**

   - Conecta bidireccionalmente con osp-raspberrypi-ms mediante API REST para recibir datos.

   - Autentica usuarios con Google OAuth2.

   - Responde al frontend con los datos filtrados según token de usuario.

**3. Microservicio en el Frontend**

- osp-frontend-web: SPA (Single Page Application) ejecutada en navegador, desarrollada como microservicio independiente. Sus responsabilidades incluyen:

   - Interfaz de login con autenticación federada (Google OAuth2).

   - Consulta segura de logs y videos asociados al usuario autenticado.

   - Visualización estructurada de datos en el navegador.

- **Relación:**

   - Se comunica con osp-backend-ms a través de API REST autenticadas con token.

   - Consume los endpoints protegidos expuestos por el backend.

   - Representa visualmente los datos y videos asociados al usuario.

**Conectores y Relaciones**

- Todos los microservicios se comunican a través de HTTP/HTTPS siguiendo el estilo RESTful.

- Se utilizan JWT (JSON Web Tokens) para validar autenticidad del usuario entre el frontend y backend.

- El backend actúa como gateway para proteger y filtrar el acceso a los datos almacenados.

- Las relaciones entre frontend y backend, así como entre backend y Raspberry, están representadas como conectores con roles bien definidos: productor, consumidor, autenticador o despachador.

Este modelo garantiza el cumplimiento de los principios de microservicios: escalabilidad, independencia, despliegue individual, integración heterogénea (Python, JS, NoSQL/SQL) y separación de responsabilidades.


# Prototipo

1. Descargar o clonar el repositorio alojado en [!LINK]
2. Verificar que Docker se encuentre en ejecución, en caso de no estarlo este debe ser inicializado.

   ![image](https://github.com/user-attachments/assets/792afc9b-2f21-4c0d-984a-e0e95655e753)

3. Descargar los dos (2) archivos ".env" proporcionados vía (pendiente slack o acceso a drive)
4. Colocar el archivo *.env* correspondiente al backend en las rutas *"...\overwatch-sentinel-platform-master\osp-backend-ms"* y *"...\overwatch-sentinel-platform-master"*.

   ![Imagen de WhatsApp 2025-05-21 a las 23 38 14_5d12f444](https://github.com/user-attachments/assets/56a49d68-8820-4da3-b675-80e15aa953ab)

5. Colocar el archivo *.env* correspondiente al frontend en la ruta *"...\overwatch-sentinel-platform-master\osp-frontend-web"*

   ![Imagen de WhatsApp 2025-05-21 a las 23 37 24_46379484](https://github.com/user-attachments/assets/a5078d50-e63f-4601-9744-86fd7760d685)

6. Posicionarse en la carpeta raiz *"...\overwatch-sentinel-platform-master"*, abrir una terminal y ejecutar las siguientes instrucciones.

   6.1. docker-compose build --no-cache

   ![image](https://github.com/user-attachments/assets/3f6230bb-48da-4452-91eb-046e9cd028c1)

   Se mostrará el resultado del Building para *web-backend* y *web-frontend*

   ![image](https://github.com/user-attachments/assets/88729237-e992-48e5-81f3-e0dd46c9998f)

   6.2. docker-compose up -d

   ![image](https://github.com/user-attachments/assets/6f33f92d-45ea-46ef-bd66-199185315d2b)

   6.3. Posicionarse en la carpeta *"...\overwatch-sentinel-platform-master\osp-raspberrypi-ms"*, y ejecutar las siguientes instrucciones.

      - docker build -t osp-raspberrypi-ms .

      - docker compose up -d





7. Verificar la creación de los contenedores y de las imagenes en docker, y verificar que todos se encuentren ejecutando.

   **Contenedores:**

   ![image](https://github.com/user-attachments/assets/dbf5819b-eb79-4734-8508-a66f92a7ba7d)

   ![Imagen de WhatsApp 2025-05-21 a las 23 50 04_85872d12](https://github.com/user-attachments/assets/b084e502-4a5e-4e3b-8d80-14fdc1314b0a)

   **Imagenes:**

@@ -185,46 +181,46 @@

8. Ir a la carpeta *"...\overwatch-sentinel-platform-master\osp-raspberrypi-ms"* y ejecutar el archivo app.py.\

   ![Imagen de WhatsApp 2025-05-21 a las 23 48 25_66f03b49](https://github.com/user-attachments/assets/2f616aef-5568-4d16-a329-94cd30187c41)

   Este archivo fue diseñado para ejecutar una función similar a la que realiza la Rasberry Pi del proyecto, y se realizó con la finalidad de poder probar el software sin necesidad    de una Rasberry Pi.

9. Comprobar la ejecución del backend.

   Abrir el navegador de preferencia y verificar las siguientes direcciones:

   9.1. **http://localhost:8000:** Se visualizará el mensaje *{"message":"Welcome to the backend called logic system"}*, el cual indica que el servicio de backend está                      corriendo correctamente.
        ![image](https://github.com/user-attachments/assets/4bca01ef-1db7-489c-aa8d-53c2fe2570f9)

   9.2. **http://localhost:8000/video:** Se puede apreciar la captura de video en vivo.
        ![Sin título](https://github.com/user-attachments/assets/a68e4551-1f87-438b-b481-265cb64ef7cc)

   9.3. **http://localhost:8000/auth/google:** Permite probar el inicio de sesión utilizando el servicio de OAuth2 de Google Cloud. Se debe seleccionar la cuenta a utilizar.
        ![Sin título](https://github.com/user-attachments/assets/2521c2d5-35d1-4dbf-ad27-3610d8d1a0ac)
        Pulsar en *Continuar*
        ![image](https://github.com/user-attachments/assets/9ca585e5-7e82-453e-859b-ebe8a1a33eb7)
        Se puede apreciar el token de acceso, lo cual indica una autenticación exitosa.

      **Nota:** El token solamente es visible para el usuario que se loguea, no es visible para usuarios diferentes.  
        ![image](https://github.com/user-attachments/assets/e114c966-1be6-43d8-b047-fd7b45f3863d)

   9.4. **http://localhost:8000/logs:** Muestra todos los eventos sucedidos en el lapso de tiempo que ha estado trabajando la captura de video.
        ![image](https://github.com/user-attachments/assets/f85dad98-27e2-42bd-ac3f-b2d38eb096b9)

10. Verificar la ejecución del frontend.

    10.1. Abrir el navegador de preferencia y verificar la siguiente dirección: **http://localhost:5173/**

    10.2. Se mostrará la página principal del sistema.
          ![image](https://github.com/user-attachments/assets/f02b7177-c185-4f99-8c60-b18d12c07d0f)

    10.3. Para acceder a la imagen en vivo se puede presionar sobre *"Acceder al Sistema"* o sobre *"Video en Vivo"*.
          ![image](https://github.com/user-attachments/assets/a32873fb-9005-44ed-b220-e4d8a591682f)
          ![image](https://github.com/user-attachments/assets/ea32eb4c-420b-48f3-8c34-f84697bfc9a0)

    10.4. Se puede apreciar la transmisión de video.
          ![Imagen de WhatsApp 2025-05-21 a las 23 44 08_42ca8c0c](https://github.com/user-attachments/assets/2d8a36ac-e1fc-49b4-a8f0-19a74d5c5e3d)

    10.5. La transmisión puede ser pausada y reanudada pulsando sobre el ícono de play/pause.\
          ![image](https://github.com/user-attachments/assets/6be22fb6-077e-40d7-b787-6edec11578c0)\
          ![image](https://github.com/user-attachments/assets/28ef443c-c273-44b0-a4c8-8df522c9c34c)
