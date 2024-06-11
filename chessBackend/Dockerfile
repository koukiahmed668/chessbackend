# Use an official OpenJDK runtime as a parent image
FROM maven:3.8.5-openjdk-17 AS build
WORKDIR /app
COPY pom.xml .
COPY src ./src
RUN mvn clean package -DskipTests


FROM openjdk:17.0.1-jdk-slim
WORKDIR /app


COPY --from=build /app/target/chessBackend-0.0.1-SNAPSHOT.jar app.jar


# Make port 8080 available to the world outside this container
EXPOSE 8080

# Run the jar file
ENTRYPOINT ["java", "-jar", "chess-app.jar"]
