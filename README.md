# Proyecto: Prototipo 1 - Estructura arquitectónica simple

# Equipo
**Nombre:** 2B

**Integrantes:** 

    - Santiago Barrera Berrio (Leading Architect - First Delivery)
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

**1. Arquitectura Basada en Microservicios + Edge Computing (Global)**
Edge (Raspberry Pi) actúa como un nodo de procesamiento local (bajo consumo).

Backend en la nube maneja lógica de negocio, autenticación, persistencia y control de acceso.

Frontend web ofrece la interfaz al usuario autenticado.

**2. Arquitectura por Componentes**
**Componente 1:** Raspberry Pi
**Tipo de arquitectura:** Microkernel (Plug-in) + Edge Computing

**Tecnologías clave:** Python, TensorFlow Lite, Flask (API REST ligera).

**Estructura:**

**Módulo de visión por computadora:** detección de objetos en tiempo real.

**Módulo de zona segura:** define y monitorea el área de vigilancia.

**Módulo de grabación de video:** activa grabación solo cuando se detecta actividad.

**Módulo de envío de logs:** transforma eventos a JSON y los expone por API.

**Módulo de sincronización de videos:** sube videos a un sistema de almacenamiento en la nube (AWS S3, Google Cloud Storage, etc.).

**Módulo de limpieza diaria:** borra logs y videos locales automáticamente (via cron o script en Python).

En el componente de Edge Computing basado en Raspberry Pi se emplean dos estilos arquitectónicos principales:

Microkernel (también conocido como Plug-in Architecture): Este estilo se adopta para permitir la extensión y evolución modular del sistema, donde la funcionalidad básica de la Raspberry Pi se mantiene en el núcleo, y los módulos como visión por computadora, detección de zonas seguras, grabación de video y limpieza diaria actúan como plug-ins que interactúan con el núcleo a través de interfaces bien definidas.

Cliente-Servidor: Se utiliza en la interacción entre la Raspberry Pi y los sistemas externos (Backend y almacenamiento en la nube). La Raspberry Pi actúa como cliente al enviar datos mediante API RESTful a servicios en la nube como el Log API y al cargar archivos al almacenamiento de video (por ejemplo, AWS S3), mientras que los servicios remotos actúan como servidores.


### Descripción de elementos arquitectónicos y relaciones
Los elementos arquitectónicos definidos en la estructura C&C del componente Raspberry Pi incluyen:

**Componentes (Elementos Activos):**

    **Raspberry Pi (núcleo):** Nodo físico y lógico que centraliza la coordinación de los módulos. Ejecuta el software principal de detección y control.
    
    **Módulo de Visión por Computadora:** Utiliza TensorFlow Lite para detectar objetos de interés en tiempo real. Está directamente conectado al núcleo y emite eventos cuando identifica un objeto válido.
    
    **Módulo de Zona Segura:** Define coordenadas dentro del campo visual como área monitoreada. Evalúa si los objetos detectados entran en esta zona y activa alertas.
    
    **Módulo de Grabación de Video:** Se activa a partir de eventos generados por el módulo anterior. Administra el uso de la cámara y almacenamiento local temporal.
    
    **Módulo de Envío de Logs (Log API):** Convierte los eventos relevantes en mensajes JSON estructurados y los envía al Backend a través de una API REST.
    
    **Módulo de Sincronización de Videos (Sync API):** Sube automáticamente los archivos de video generados a un servicio de almacenamiento en la nube.
    
    **Módulo de Limpieza Diaria (Daily Cleanup):** Ejecutado con cron o script programado en Python, borra diariamente los archivos locales (videos y logs) para liberar espacio.

**Conectores (Relaciones):**

    Llamadas internas (invocación por interfaz): Entre el núcleo (Raspberry Pi) y los módulos de visión, zona segura, grabación, y limpieza. La comunicación se da mediante llamadas a funciones, eventos o señales internas.
    
    Conectores de red HTTP (REST API): El módulo Log API y el módulo Sync API utilizan protocolos HTTP para conectarse con el backend y la nube respectivamente. Esta conexión está asegurada bajo HTTPS.
    
    Canal de almacenamiento externo: El componente se conecta de forma asíncrona a un sistema de almacenamiento en la nube (Cloud Storage), usado como repositorio persistente de videos.

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
