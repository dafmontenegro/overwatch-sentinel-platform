# Proyecto: Prototipo 3 - Atributos de calidad, Parte 1


# Equipo
**Nombre:** 2B

**Integrantes:** 

- Santiago Barrera Berrio
- Cristian Alejandro Beltran Rojas
- Daniel Felipe Montenegro Herrera
- Breyner Ismael Ciro Otero
- Juan Felipe Fontecha Vasquez
- Miguelangel Mosquera

# Repositorio

https://github.com/dafmontenegro/overwatch-sentinel-platform/tree/master

# Sistema de Software

**Nombre del Software:** OSP - Overwatch Sentinel Platform

**Logo:** 

![Logo-CapriBlue](https://github.com/user-attachments/assets/4e00fde1-3738-4922-8777-0c1bc1cc4965)


**Descripción:** OSP (Overwatch Sentinel Platform) es una plataforma de software para la vigilancia automatizada basada en visión por computadora, diseñada para funcionar sobre hardware de bajo consumo como Raspberry Pi. Utiliza la implementación [pi-tensorflow-lite-object-detection](https://github.com/dafmontenegro/pi-tensorflow-lite-object-detection), la cual permite detectar objetos definidos previamente dentro del campo visual de la cámara.

El sistema permite configurar un área específica dentro de la imagen —conocida como zona segura— que delimita el espacio de vigilancia. Cuando un objeto de interés entra en dicha zona, el sistema activa automáticamente la grabación de video. De este modo, se optimiza el uso de recursos, ya que solo se almacena material cuando se detecta actividad relevante.

Esta solución está orientada a escenarios donde se requiere supervisión eficiente y automática, con un diseño modular que permitirá, en futuras fases, incluir funcionalidades adicionales como el seguimiento (tracking) y el monitoreo continuo de objetos.


# Estructuras Arquitectonicas

## Estructura Componente y Conector (C&C)
### C&C View

![Components & Connectors](https://github.com/user-attachments/assets/73ac7544-07e7-467e-8e6c-d7fb2e1f50a6)

### Descripción de los estilos arquitectónicos utilizados

El sistema OSP (Overwatch Sentinel Platform) implementa una arquitectura de microservicios integral que abarca desde los dispositivos Raspberry Pi en el edge hasta los servicios backend y la interfaz web frontend. Esta arquitectura descompone el sistema en componentes autónomos con responsabilidades bien definidas que interactúan mediante APIs REST sobre HTTP/HTTPS.

La arquitectura de microservicios implica descomponer el sistema en componentes autónomos, cada uno con una responsabilidad bien definida, que interactúan entre sí a través de interfaces ligeras (REST API sobre HTTP/HTTPS). Cada microservicio es desplegado, escalado y gestionado de forma independiente, permitiendo una mayor resiliencia, escalabilidad y facilidad de evolución del sistema.

**Características clave de esta adopción:**

1. **Principio de única responsabilidad:** Cada microservicio, incluyendo los que operan en dispositivos edge como las Raspberry Pi, gestiona un dominio funcional específico. Por ejemplo, el componente osp-raspberrypi se encarga exclusivamente de la captura y procesamiento inicial de video, mientras que osp-authentication maneja únicamente la autenticación federada.

2. **Comunicación segura:** Todos los microservicios se comunican mediante HTTPS con TLS 1.2+ utilizando certificados gestionados automáticamente. Las conexiones desde el frontend al navegador implementan cifrado punto a punto con perfect forward secrecy.

3. **Comunicación clarificada:** Las interfaces entre microservicios están bien definidas y utilizan formatos estandarizados como JSON y HTTP REST.

4. **Se permite la integración tecnológica heterogénea:** por ejemplo, Python en Raspberry Pi, Node.js o Flask en Backend, y React en Frontend, sin afectar la interoperabilidad.

5. **Réplica del API:** El servicio osp-api está diseñado para desplegarse en tres instancias idénticas que comparten acceso a las mismas bases de datos. Esta replicación proporciona alta disponibilidad mediante balanceo de carga implementado en osp-rightx-proxy.

Esta estrategia facilita el despliegue incremental, la automatización, la resiliencia ante fallos parciales y la futura extensión del sistema con nuevos servicios (como seguimiento de objetos, análisis forense, etc.).

### Descripción de elementos arquitectónicos y relaciones

La arquitectura del sistema OSP se compone de tres dominios principales —Frontend, Backend y Raspberry Pi (Edge)—, cada uno diseñado como una colección de microservicios independientes que se comunican mediante interfaces RESTful sobre HTTPS. A continuación se describen los elementos arquitectónicos y sus relaciones:

**1. Microservicios en el Componente Raspberry Pi (Edge):** 

- **osp-raspberrypi:** Funciona como un componente físico autónomo que ejecuta tareas de detección de objetos y gestión de video.
- **osp-processing-ms:** Funciona como controlador de datos y balanceador de solicitudes a los recursos físicos.
- **Relación:**

   - Envía eventos al microservicio de processing (osp-processing-ms) mediante interfaces REST con mensajes JSON.

**2. Microservicios en el Backend**

- **osp-authentication-ms:** Microservicio que recibe, valida y persiste los datos de autenticación dada porl os usuarios. Internamente, realiza las siguientes funciones:

   - Gestión de autenticación federada (conexión a Google OAuth2).

- **osp-information-ms:** Microservicio que recibe, valida y persite la información generada por el elemento fisico para guardarlo en bases de respaldo o de consistencia de datos.

   - Recepción y persistencia de logs desde los nodos Raspberry.

   - Generación de respuestas al frontend con datos y videos filtrados por usuario.
 
   - Sube los logs videos grabados a un almacenamiento en la nube externo (representado como nube externa en el modelo).
 
- **osp-processing-ms:** Microservicio necargado de reducción de tareas del componente fisico, expone el video, unico con acceso a los eventos, logs, videos y mideo en vivo dado por el dispositivo de manera directa funcionando como puente.

   - Generación de respuestas al frontend con datos y videos filtrados por usuario.
 
   - Sube los videos grabados a un almacenamiento en la nube externo (representado como nube externa en el modelo).

- **Bases de Datos:**

   - **PostgreSQL:** Almacena usuarios, permisos, metadatos de videos, y configuración del sistema.

   - **MongoDB:** Almacena los logs generados por los dispositivos en formato JSON.

   - **auth_db:** Contiene tokens, sesiones y credenciales de acceso autenticadas.

   - **logs_db:** Esquema especializado para búsquedas de eventos históricos.

- **Relación:**

   - Conecta bidireccionalmente con osp-apigateway mediante HTTP para recibir datos.

   - Autentica usuarios con Google OAuth2.

   - Responde al frontend con los datos filtrados según token de usuario.

**3. Microservicio en el Frontend**

- osp-frontend-web: SPA (Single Page Application) ejecutada en navegador, desarrollada como microservicio independiente. Sus responsabilidades incluyen:

   - Interfaz de login con autenticación federada (Google OAuth2).

   - Consulta segura de logs y videos asociados al usuario autenticado.

   - Visualización estructurada de datos en el navegador.
 
- osp-app: Es una aplicación renderizada desde el lado del servidor que toma como base la estructura del componente web. Sus responsabilidades incluyen:

   - Replicar las funcionalidad del frontend web
 
   - No presentar puntos de acceso

- **Relación:**

   - Se comunica con osp-nginx-proxy mediante HTTP autenticadas con token.

   - Consume los endpoints protegidos expuestos por el backend.

   - Representa visualmente los datos y videos asociados al usuario.

**Conectores y Relaciones**

- Los microservicios se comunican a través de HTTP/HTTPS o TCP/IP siguiendo el estilo RESTful.

- Se utilizan JWT (JSON Web Tokens) para validar autenticidad del usuario entre el frontend y backend.

- El Api Gateway actúa como relacionador entre las redes pública y privada para proteger y filtrar el acceso a los componentes y datos almacenados.

Este modelo garantiza el cumplimiento de los principios de microservicios: escalabilidad, independencia, despliegue individual, integración heterogénea (Python, JS, NoSQL/SQL, Java, HTML) y separación de responsabilidades.

## Layered Structure
### Layered View
 ![2fbc5179-06c2-4fc0-b18b-06e20dcdb9bd](https://github.com/user-attachments/assets/da45d63c-3465-4dc2-902e-e68696e1b6cc)

### Descripción de elementos arquitectónicos y relaciones

El sistema OSP maneja cuatro capas en este caso: 

   - Una capa de presentación que muestra las diferentes páginas que el usuario observa y usa para interactuar, siendo estas:
      - Home page
      - Login page
      - Account page

   - Una capa de servicios que describe las peticiones del usuario para autenticarse, revisar el livestream o pedir información.
       
   - Una capa de negocios donde se realiza el proceso de autenticación de cuentas, la captura del livestream o la generacion de videos y logs.
     
   - Una capa de datos que maneja bases de datos para la información de autenticación, los videos, los logs y los respaldos.

  **Relaciones:**

   - La página de acceso muestra la información del sistema y permite ir a la sección de autenticación.
  
   - La página de acceso requiere del proceso de autenticación para llevar al usuario a su cuenta o mostrar un error, este proceso se realiza validando la información presente en la base de datos de autenticación.
     
   - La página de transmisiones en vivo muestra la captura del componente físico siendo procesada por el sistema y recogiendo la información desde una base de datos separada.
     
## Deployment Structure
### Deployment View
![Deployment View](https://github.com/user-attachments/assets/ae1a50cc-ae84-43a1-a648-875c1351d3a2)


### Descripción de elementos arquitectónicos y relaciones
Para ser desplegado el sistema OSP tiene en consideración cinco entornos:

   - Raspberrypi enviroment: Despliega tanto el componente físico como el gestor de raspberries.


   - Authentication enviroment: Despliega el proceso y la base de datos de autenticación. 
     
   - Information enviroment: Despliega el gestor de información asi como las bases de datos respectivas. 

   - Proxy enviroment: Despliega el proxy que sirve también como balanceador de carga.

   - Frontend enviroment: Depliega el componente de frontend.

   - Apigateway enviroment: Despliega el apigateway asi como conecta los demás ambientes.
     

## Decomposition Structure
### Decomposition View
![Decomposition structure](https://github.com/user-attachments/assets/ca1c845a-ea39-4183-9966-1ead49c842db)


### Descripción de elementos arquitectónicos y relaciones
El sistema OSP trabaja con 4 elementos actualmente según las funciones que realiza:
   - Visualización

   - Autenticación

   - Procesamiento de imagenes

   - Almacenamiento de datos

   **Relaciones:**
   
   Se tiene la presentación de las diferentes páginas para que el usuario interactue o realice peticiones al sistema.
   
   Hay un proceso para la autenticación para todos los usuarios comprobando la información presente.

   Las imagenes generadas por los componentes físicos son procesadas para que puedan ser vistas o guardadas según sea necesario.

   Todos los datos necesarios se guardan en bases de datos para garantizar permanencia e integridad. 

# Atributos de calidad

## Atributos de calidad de Seguridad

### Escenarios de seguridad

#### a. Escenario: Ataques de acceso no autorizado a microservicios

#### Amenaza 

En arquitecturas de microservicios, si un atacante compromete un contenedor (ej: mediante una vulnerabilidad en la API Gateway), puede intentar propagarse a otros servicios mediante conexiones no restringidas.
Su impacto es la pérdida de confidencialidad (datos robados), escalamiento de privilegios o denegación de servicio.

#### Solución: Segmentación de redes con Docker

- **Táctica**: Aislamiento de redes en `docker-compose.yml`
  - **Red pública**: Frontend y Nginx.
  - **Red privada (`internal: true`)**: Microservicios y bases de datos.
  - El API Gateway tiene acceso a ambas redes.
 
![image](https://github.com/user-attachments/assets/af777860-dac4-44cd-b5ed-ee8192f8a048)

**Por qué funciona**

Docker bloquea el tráfico no autorizado entre redes usando iptables.

Ejemplo: Desde un contenedor en la red pública, no se puede acceder directamente a un microservicio

#### b. Escenario: Ataque de denegación de servicios (DoS)

#### Amenaza

Endpoints como /api/auth/google o /api/video están expuestos y podrían ser objetivo de fuerza bruta, scanning automatizado o inyecciones.

#### Solución: Proxy reverso (Nginx)

Las tacticas usadas son el "rate limiting" que limita las solicitudes por IP (limit_req_zone en nginx.conf). Y, además Headers de seguridad: X-Frame-Options, Content-Security-Policy también ubicado en el archivo mencionado `nginx.conf`.

![image](https://github.com/user-attachments/assets/06c67610-d91c-4556-b0d0-defece5609fa)

**Por qué funciona**

- Nginx actúa como un filtro:
  - Oculta la estructura interna (los microservicios no son accesibles directamente desde internet).
  - Bloquea tráfico malicioso (ej: demasiadas solicitudes consecutivas).

#### c. Escenario: Interceptación de datos (Man-in-the-Middle)

#### Amenaza

El tráfico entre el frontend y el cliente viaja en HTTP (sin encriptar), lo que permite interceptación de datos (credenciales, tokens).

#### Solución: Canal de comunicación seguro (HTTPS/TLS).

- Configuración:
  - Certificado TLS en Nginx (a implementar).
  - Redirección automática de HTTP a HTTPS.

![image](https://github.com/user-attachments/assets/e606bae7-e045-4b8d-b1d3-8978818eb767)

**Por qué funciona**

- Encripta los datos en tránsito usando TLS.
- Autentica el servidor, evitando ataques de suplantación (MitM).

#### d. Ataque de inyección (SQL, XSS) en microservicios

#### Amenaza

El API Gateway construido con Vert.x procesa solicitudes que podrían contener código malicioso (SQLi, XSS) antes de redirigirlas a los microservicios.

#### Solución: Validación de entradas

Usando el patrón de Gatekeeper que centraliza las validaciones antes de pasar al backend pueden ponerse condicionales que validen que la información sea como se espera que debe ser y así evitar inyecciones de código malicioso

![image](https://github.com/user-attachments/assets/70690227-3422-46fc-9b36-cccfdb09ab06)

**Por qué funciona**

- Whitelisting: Solo acepta caracteres alfanuméricos, bloqueando scripts o SQL malicioso.

- Centralización: Evita duplicar validaciones en cada microservicio.

### Tácticas arquitectónicas aplicadas 

| Táctica                  | Implementación                          | Fundamentación Técnica                                                                 |
|--------------------------|----------------------------------------|---------------------------------------------------------------------------------------|
| **Segmentación de redes** | Redes Docker `internal: true`          | Aislamiento mediante namespaces de red y políticas iptables                           |
| **Rate limiting**         | Configuración en `nginx.conf`          | Control de tráfico usando algoritmos de "leaky bucket"                                |
| **Validación de inputs**  | Regex en Vert.x (`token.matches()`)    | Whitelisting para prevenir inyecciones                                               |
| **Encriptación TLS**      | Certificados en Nginx                  | Cifrado AES-256-GCM y autenticación X.509                                            |

### Patrones arquitectónicos aplicados

| Patrón                   | Componente               | Propósito                                                                             |
|--------------------------|--------------------------|---------------------------------------------------------------------------------------|
| **Reverse Proxy**        | Nginx                    | Ocultar topología interna y filtrar tráfico                                           |
| **Gatekeeper**           | API Gateway (Vert.x)     | Centralizar validaciones de seguridad                                                 |
| **Secure Communication** | HTTPS/TLS                | Proteger datos en tránsito                                                            |
| **Microsegmentation**    | Redes Docker             | Limitar movimiento lateral entre servicios                                           |

## Atributos de calidad de rendimiento y escalabilidad

### Escenarios de rendimiento

#### a. Escenario: Concurrencia de usuarios en plataforma web

**Objetivo:**
Determinar cuántos usuarios pueden autenticarse simultáneamente sin degradación del servicio.

#### Prueba Propuesta
1. **Herramienta**: JMeter o k6.
2. **Métrica clave**: 
   - Requests exitosos (<pending) vs tasa de error.
   - Tiempo de respuesta pending < 2s.
3. **Ejecución**:
   - Incrementar usuarios gradualmente (ej: 50, 100, 200... hasta fallo).
   - Ejemplo de script con k6:

#### Resultados 

| Usuarios Concurrentes  | Requests Exitosos  | Tiempo Respuesta Promedio (ms)| Errores              |
|------------------------|--------------------|-------------------------------|----------------------|
| 50     	             |  50                | 126                           | Ninguno              |
| 200     	             |  200               | 177                           | Ninguno              |
| 500     	             |  500               | 252                           | Ninguno              |
| 1000     	             |  1000              | 442                           | Ninguno              |
| 3000     	             |  1606              | 13615                         | Connection timed out |
| 5000     	             |  1325              | 14532                         | Connection timed out |



#### b. Escenario: Streaming de video en vivo

| Usuarios Concurrentes  | Requests Exitosos  | Tiempo Respuesta (p95)        | Errores |
|------------------------|--------------------|-------------------------------|---------|
| Por ejecutar	         |  Pendiente         |Pendiente                      | Pendiente|

**Objetivo:**
Identificar el límite de espectadores concurrentes antes de colapsar.

#### Prueba Propuesta
1. **Herramienta**:  JMeter.
2. **Métrica clave**:
   - Latencia de video < 5s.
   - Pérdida de paquetes < 1%.
3. **Ejecución**:
   - Simular espectadores con:
     ```bash
     ab -n 1000 -c 50 http://localhost/api/video
     ```
   - Monitorear ancho de banda y CPU del servidor.

#### Resultados

**Previos**
| Usuarios Concurrentes  | Requests Exitosos  | Tiempo Respuesta (p95)        | Errores |
|------------------------|--------------------|-------------------------------|---------|
| Por ejecutar	         |  Pendiente         |Pendiente                       |Pendiente|

**Posteriores**
| Usuarios Concurrentes  | Requests Exitosos  | Tiempo Respuesta (p95)        | Errores |
|------------------------|--------------------|-------------------------------|---------|
| Por ejecutar	         |  Pendiente         |Pendiente                      | Pendiente|
#### b. Escenario: Streaming de video en vivo

### Tácticas arquitectónicas aplicadas 

Pending

### Patrones arquitectónicos aplicados  

Pending
