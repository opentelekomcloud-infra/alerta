from alerta/alerta-web

LABEL maintainer="Artem Goncharov <artem.goncharov@gmail.com>"

COPY plugins /tmp/plugins
RUN /venv/bin/pip install /tmp/plugins/zulip

COPY ldap /tmp/ldap
RUN cd /tmp/ldap && ./update_ldap_library.sh
