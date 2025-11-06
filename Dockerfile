from alerta/alerta-web:9.0.4

LABEL maintainer="Artem Goncharov <artem.goncharov@gmail.com>"

USER root
COPY plugins /tmp/plugins
RUN chown -R alerta:root /tmp/plugins
USER alerta

# Ensure build tools are present
RUN /venv/bin/pip install --upgrade pip setuptools wheel
# Install plugin
RUN /venv/bin/pip install /tmp/plugins/zulip
