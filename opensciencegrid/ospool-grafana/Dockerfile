FROM grafana/grafana:main-ubuntu

USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
            ca-certificates \
            curl \
            git \
    && rm -rf /var/lib/apt/lists/*

# Add our override entrypoint
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

USER grafana
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

