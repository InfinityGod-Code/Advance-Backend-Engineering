FROM maven:3.9-eclipse-temurin-21 AS build
WORKDIR /app
COPY pom.xml .
COPY common-events common-events/
COPY shipment-service shipment-service/
RUN mvn -N install -DskipTests && mvn -f common-events/pom.xml install -DskipTests && mvn -f shipment-service/pom.xml clean package -DskipTests

FROM eclipse-temurin:21-jre
WORKDIR /app
COPY --from=build /app/shipment-service/target/*.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
