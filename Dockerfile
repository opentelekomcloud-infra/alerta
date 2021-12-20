from alerta/alerta-web:8.7.0

LABEL maintainer="Artem Goncharov <artem.goncharov@gmail.com>"

COPY plugins /tmp/plugins
RUN /venv/bin/pip install /tmp/plugins/zulip

