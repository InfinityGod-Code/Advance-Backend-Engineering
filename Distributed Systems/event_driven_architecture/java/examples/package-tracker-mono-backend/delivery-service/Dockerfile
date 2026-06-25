FROM maven:3.9-eclipse-temurin-21 AS build
WORKDIR /app
COPY pom.xml .
COPY common-events common-events/
COPY delivery-service delivery-service/
RUN mvn -N install -DskipTests && mvn -f common-events/pom.xml install -DskipTests && mvn -f delivery-service/pom.xml clean package -DskipTests

FROM eclipse-temurin:21-jre
WORKDIR /app
COPY --from=build /app/delivery-service/target/*.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
