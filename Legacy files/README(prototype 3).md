# Proyecto: Prototipo 2 - Estructura arquitectónica avanzada

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

![Component_ _Connector](https://github.com/user-attachments/assets/1e9f9624-d12f-4123-a6a4-07c4fcbacd90)

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

   - Conecta bidireccionalmente con osp-apigateway mediante HTTP para recibir datos.

   - Autentica usuarios con Google OAuth2.

   - Responde al frontend con los datos filtrados según token de usuario.

**3. Microservicio en el Frontend**

- osp-frontend-web: SPA (Single Page Application) ejecutada en navegador, desarrollada como microservicio independiente. Sus responsabilidades incluyen:

   - Interfaz de login con autenticación federada (Google OAuth2).

   - Consulta segura de logs y videos asociados al usuario autenticado.

   - Visualización estructurada de datos en el navegador.

- **Relación:**

   - Se comunica con osp-apigateway mediante HTTP autenticadas con token.

   - Consume los endpoints protegidos expuestos por el backend.

   - Representa visualmente los datos y videos asociados al usuario.

**Conectores y Relaciones**

- Todos los microservicios se comunican a través de HTTP/HTTPS siguiendo el estilo RESTful.

- Se utilizan JWT (JSON Web Tokens) para validar autenticidad del usuario entre el frontend y backend.

- El backend actúa como gateway para proteger y filtrar el acceso a los datos almacenados.

- Las relaciones entre frontend y backend, así como entre backend y Raspberry, están representadas como conectores con roles bien definidos: productor, consumidor, autenticador o despachador.

Este modelo garantiza el cumplimiento de los principios de microservicios: escalabilidad, independencia, despliegue individual, integración heterogénea (Python, JS, NoSQL/SQL) y separación de responsabilidades.


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
![Deployment view](https://github.com/user-attachments/assets/1d88de83-aa02-4565-bed2-64739e271fb5)





### Descripción de elementos arquitectónicos y relaciones
Para ser desplegado el sistema OSP tiene en consideración cinco entornos:

   - Authentication enviroment: Despliega el proceso y la base de datos de autenticación. 
     
   - Information enviroment: Despliega el gestor de información asi como las bases de datos respectivas. 

   - Raspberrypie enviroment: Despliega tanto el componente físico como el gestor de raspberries.

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

#### b. Escenario: Exposición de endpoints sensibles

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

#### a. Escenario: Concurrencia de usuarios en login

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
     ```bash
     import http from 'k6/http';
     import { check } from 'k6';

     export const options = {
       stages: [
         { duration: '30s', target: 50 },   // Rampa de 0 a 50 usuarios en 30s
         { duration: '1m', target: 150 },   // Mantener 150 usuarios
       ],
     };
      
     export default function () {
       const res = http.post('http://<TU_IP_SERVIDOR>:80/api/auth/google');
       check(res, { 'status was 200': (r) => r.status == 200 });
     }
     ```

#### Resultados 

**Previos**
| Usuarios Concurrentes  | Requests Exitosos  | Tiempo Respuesta (p95)        | Errores |
|------------------------|--------------------|-------------------------------|---------|
| Por ejecutar	         |  Pendiente         |Pendiente                      | Pendiente|

**Posteriores**
| Usuarios Concurrentes  | Requests Exitosos  | Tiempo Respuesta (p95)        | Errores |
|------------------------|--------------------|-------------------------------|---------|
| Por ejecutar	         |  Pendiente         |Pendiente                      | Pendiente|
#### b. Escenario: Streaming de video en vivo

**Objetivo:**
Identificar el límite de espectadores concurrentes antes de colapsar.

#### Prueba Propuesta
1. **Herramienta**: FFmpeg + Apache Bench.
2. **Métrica clave**:
   - Latencia de video < 5s.
   - Pérdida de paquetes < 1%.
3. **Ejecución**:
   - Simular espectadores con:
     ```bash
     ab -n 1000 -c 50 http://tudominio.com/api/video
     ```
   - Monitorear ancho de banda y CPU del servidor.

#### Resultados

**Previos**
| Usuarios Concurrentes  | Requests Exitosos  | Tiempo Respuesta (p95)        | Errores |
|------------------------|--------------------|-------------------------------|---------|
| Por ejecutar	         |  Pendiente         |Pendiente                      | Pendiente|

**Posteriores**
| Usuarios Concurrentes  | Requests Exitosos  | Tiempo Respuesta (p95)        | Errores |
|------------------------|--------------------|-------------------------------|---------|
| Por ejecutar	         |  Pendiente         |Pendiente                      | Pendiente|
#### b. Escenario: Streaming de video en vivo

### Tácticas arquitectónicas aplicadas 

Pending

### Patrones arquitectónicos aplicados  

Pending
