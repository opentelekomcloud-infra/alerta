from alerta/alerta-web:8.3.3

LABEL maintainer="Artem Goncharov <artem.goncharov@gmail.com>"

COPY plugins /tmp/plugins
RUN /venv/bin/pip install /tmp/plugins/zulip

