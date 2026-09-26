# syntax=docker/dockerfile:1
# Keel & Cloud dedicated server. Build from the repository root:
#   docker build -f server/Dockerfile -t keel-and-cloud .
# The pack is baked in at build time, so an image tag is an exact, reproducible server.

# Ubuntu-based, not Alpine: Sable ships native physics libraries built against glibc.
ARG JAVA_IMAGE=eclipse-temurin:21-jre-noble

# https://github.com/packwiz/packwiz-installer-bootstrap/releases
# https://github.com/packwiz/packwiz-installer/releases
# https://github.com/itzg/rcon-cli/releases
ARG PACKWIZ_BOOTSTRAP_VERSION=v0.0.3
ARG PACKWIZ_INSTALLER_VERSION=v0.5.14
ARG RCON_CLI_VERSION=1.7.7

# The NeoForge version comes from pack.toml. Copying just the extracted version into the next stage keeps
# the slow NeoForge install cached across pack changes (BuildKit caches COPY by file content).
FROM ${JAVA_IMAGE} AS version
COPY pack/pack.toml /tmp/
RUN sed -n 's/^neoforge = "\(.*\)"/\1/p' /tmp/pack.toml > /neoforge-version && test -s /neoforge-version

FROM ${JAVA_IMAGE} AS neoforge
COPY --from=version /neoforge-version /
WORKDIR /server
RUN V=$(cat /neoforge-version) && \
    curl -fsSL -o /tmp/installer.jar "https://maven.neoforged.net/releases/net/neoforged/neoforge/$V/neoforge-$V-installer.jar" && \
    java -jar /tmp/installer.jar --install-server . > /dev/null && \
    cp "libraries/net/neoforged/neoforge/$V/unix_args.txt" . && \
    rm -f /tmp/installer.jar run.sh run.bat user_jvm_args.txt *.log

FROM ${JAVA_IMAGE} AS pack
ARG PACKWIZ_BOOTSTRAP_VERSION
ARG PACKWIZ_INSTALLER_VERSION
WORKDIR /server
ADD https://github.com/packwiz/packwiz-installer-bootstrap/releases/download/${PACKWIZ_BOOTSTRAP_VERSION}/packwiz-installer-bootstrap.jar /opt/
ADD https://github.com/packwiz/packwiz-installer/releases/download/${PACKWIZ_INSTALLER_VERSION}/packwiz-installer.jar .
COPY pack/ /pack/
# The server side of the pack: client-only mods (Sodium, maps) are skipped, hashes are verified.
RUN java -jar /opt/packwiz-installer-bootstrap.jar --bootstrap-no-update -g -s server file:///pack/pack.toml && \
    rm -f packwiz-installer.jar packwiz.json options.txt servers.dat

FROM ${JAVA_IMAGE}
ARG RCON_CLI_VERSION
ARG TARGETARCH
ADD https://github.com/itzg/rcon-cli/releases/download/${RCON_CLI_VERSION}/rcon-cli_${RCON_CLI_VERSION}_linux_${TARGETARCH}.tar.gz /tmp/rcon-cli.tgz
# The noble base image already has uid 1000 ("ubuntu"); replace it so files in /data belong to "minecraft".
RUN tar -xzf /tmp/rcon-cli.tgz -C /usr/local/bin rcon-cli && rm /tmp/rcon-cli.tgz && \
    ln -s rcon-cli /usr/local/bin/rcon && \
    (userdel -r ubuntu 2>/dev/null || true) && \
    groupadd -g 1000 minecraft && useradd -u 1000 -g minecraft -M -d /data minecraft && \
    mkdir /data && chown minecraft:minecraft /data

# Libraries change only with NeoForge, mods with every pack release: separate layers, cheap pulls.
COPY --from=neoforge /server/ /opt/minecraft/server/
COPY --from=pack /server/ /opt/minecraft/server/
COPY server/entrypoint.sh server/server.properties /opt/minecraft/
COPY assets/icon-64.png /opt/minecraft/server-icon.png

# Heap size, then Aikar's G1 flags (https://docs.papermc.io/paper/aikars-flags).
# Size the container's memory limit at least 1.5 GB above MEMORY_SIZE.
ENV MEMORY_SIZE=6G \
    JAVA_FLAGS="-XX:+UseG1GC -XX:+ParallelRefProcEnabled -XX:MaxGCPauseMillis=200 -XX:+UnlockExperimentalVMOptions -XX:+DisableExplicitGC -XX:+AlwaysPreTouch -XX:G1NewSizePercent=30 -XX:G1MaxNewSizePercent=40 -XX:G1HeapRegionSize=8M -XX:G1ReservePercent=20 -XX:G1HeapWastePercent=5 -XX:G1MixedGCCountTarget=4 -XX:InitiatingHeapOccupancyPercent=15 -XX:G1MixedGCLiveThresholdPercent=90 -XX:G1RSetUpdatingPauseTimePercent=5 -XX:SurvivorRatio=32 -XX:+PerfDisableSharedMem -XX:MaxTenuringThreshold=1" \
    RCON_PORT=25575

USER 1000
WORKDIR /data
VOLUME ["/data"]
EXPOSE 25565/tcp
ENTRYPOINT ["/opt/minecraft/entrypoint.sh"]
