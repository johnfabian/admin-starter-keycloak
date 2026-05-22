FROM maven:3.9.9-eclipse-temurin-17 AS provider-build

WORKDIR /workspace

COPY providers/disable-after-email-verify/pom.xml ./pom.xml
COPY providers/disable-after-email-verify/src ./src

RUN mvn -q -DskipTests package

FROM quay.io/keycloak/keycloak:26.0

COPY --from=provider-build /workspace/target/disable-after-email-verify.jar /opt/keycloak/providers/disable-after-email-verify.jar

RUN /opt/keycloak/bin/kc.sh build
