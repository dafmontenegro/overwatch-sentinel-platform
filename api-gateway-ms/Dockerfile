FROM eclipse-temurin:17-jdk-jammy

WORKDIR /app

# Copia los archivos de construcción
COPY build.gradle.kts .
COPY settings.gradle.kts .
COPY gradlew .
COPY gradle ./gradle

# Copia el código fuente
COPY src ./src

# Construye la aplicación (generará un JAR con el nombre correcto)
RUN chmod +x gradlew
RUN ./gradlew clean shadowJar

# Puerto estándar de Vert.x
EXPOSE 8888

# Comando para ejecutar la aplicación usando el JAR generado por shadowJar
CMD ["java", "-jar", "build/libs/api-gateway-ms-fat.jar"]