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

![C C](https://github.com/user-attachments/assets/0f2e3d43-78c5-4a40-b09a-f100c16bcfff)






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

![C C](https://github.com/user-attachments/assets/0f2e3d43-78c5-4a40-b09a-f100c16bcfff)






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
   
