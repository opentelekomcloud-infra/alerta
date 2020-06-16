from alerta/alerta-web

LABEL maintainer="Artem Goncharov <artem.goncharov@gmail.com>"

RUN /venv/bin/pip install requests --upgrade

COPY plugins /tmp/plugins
RUN /venv/bin/pip install /tmp/plugins/zulip

