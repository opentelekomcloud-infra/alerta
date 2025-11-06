from alerta/alerta-web:9.0.4

LABEL maintainer="Artem Goncharov <artem.goncharov@gmail.com>"

COPY plugins /tmp/plugins

# Ensure build tools are present
RUN /venv/bin/pip install --upgrade pip setuptools wheel

RUN TMPDIR=/tmp /venv/bin/pip install /tmp/plugins/zulip
# RUN /venv/bin/pip install /tmp/plugins/zulip

