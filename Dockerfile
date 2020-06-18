from alerta/alerta-web:7.5.5

LABEL maintainer="Artem Goncharov <artem.goncharov@gmail.com>"

COPY plugins /tmp/plugins
RUN /venv/bin/pip install /tmp/plugins/zulip

COPY ldap /tmp/ldap
RUN cd /tmp/ldap && ./patch_ldap_library.sh
