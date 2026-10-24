# Builds the SysML v2 Pilot API server (https://github.com/Systems-Modeling/SysML-v2-API-Services)

FROM eclipse-temurin:11-jdk AS build

ARG SYSML_RELEASE=2026-04
ARG SBT_VERSION=1.10.7

RUN apt-get update \
    && apt-get install -y --no-install-recommends git curl \
    && rm -rf /var/lib/apt/lists/*

# The sbt launcher fetches the sbt version pinned by the project itself
RUN curl -fsSL "https://github.com/sbt/sbt/releases/download/v${SBT_VERSION}/sbt-${SBT_VERSION}.tgz" | tar -xz -C /opt
ENV PATH="/opt/sbt/bin:${PATH}"

WORKDIR /src
RUN git clone --depth 1 --branch "${SYSML_RELEASE}" https://github.com/Systems-Modeling/SysML-v2-API-Services .

# Point at the compose 'db' service and keep the schema between restarts (upstream uses create-drop)
RUN sed -i \
        -e 's#jdbc:postgresql://localhost:5432/#jdbc:postgresql://db:5432/#' \
        -e 's#"hibernate.hbm2ddl.auto" value="create-drop"#"hibernate.hbm2ddl.auto" value="update"#' \
        conf/META-INF/persistence.xml \
    && grep -q 'db:5432' conf/META-INF/persistence.xml \
    && grep -q 'hbm2ddl.auto" value="update"' conf/META-INF/persistence.xml

RUN sbt -batch clean stage

FROM eclipse-temurin:11-jre

WORKDIR /opt/sysml-api
COPY --from=build /src/target/universal/stage .

EXPOSE 9000

CMD bin/sysml-v2-api-services \
    -Dhttp.port=9000 \
    -Dpidfile.path=/dev/null \
    -Dplay.http.secret.key="${PLAY_SECRET}" \
    -Dplay.filters.hosts.allowed.0=.
