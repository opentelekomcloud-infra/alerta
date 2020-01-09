import logging
import os

try:
    from alerta.plugins import app  # alerta >= 5.0
except ImportError:
    from alerta.app import app  # alerta < 5.0
from alerta.plugins import PluginBase

import zulip
from jinja2 import Template, UndefinedError


DEFAULT_TMPL = """
{% if customer %}Customer: `{{customer}}` {% endif %}
*[{{ status.capitalize() }}] {{ environment }} {{ severity.capitalize() }}*
{{ event }} {{ resource.capitalize() }}
```
{{ text }}
```
"""

LOG = logging.getLogger('alerta.plugins.zulip')

ZULIP_API_KEY = app.config.get('ZULIP_API_KEY') \
                or os.environ.get('ZULIP_API_KEY')
ZULIP_EMAIL = app.config.get('ZULIP_EMAIL') \
              or os.environ.get('ZULIP_EMAIL')
ZULIP_SITE = app.config.get('ZULIP_SITE') \
             or os.environ.get('ZULIP_SITE')
ZULIP_TYPE = app.config.get('ZULIP_TYPE') \
             or os.environ.get('ZULIP_TYPE', 'stream')
ZULIP_TO = app.config.get('ZULIP_TO') \
           or os.environ.get('ZULIP_TO')
ZULIP_SUBJECT = app.config.get('ZULIP_SUBJECT') \
             or os.environ.get('ZULIP_SUBJECT', 'Alert')
ZULIP_ALLOW_UNSECURE = app.config.get('ZULIP_ALLOW_UNSECURE') \
                       or os.environ.get('ZULIP_ALLOW_UNSECURE')
ZULIP_TEMPLATE = app.config.get('ZULIP_TEMPLATE') \
                 or os.environ.get('ZULIP_TEMPLATE')
ZULIP_SERVICE_TOPIC_MAP = app.confin.get('ZULIP_SERVICE_TOPIC_MAP')


class ZulipBot(PluginBase):

    def __init__(self, name=None):
        zulip_args = {
            'site': ZULIP_SITE,
            'email': ZULIP_EMAIL,
            'api_key': ZULIP_API_KEY
        }
        if ZULIP_ALLOW_UNSECURE is not None:
            zulip_args['insecure'] = ZULIP_ALLOW_UNSECURE
        self.bot = zulip.Client(**zulip_args)

        super(ZulipBot, self).__init__(name)

        if ZULIP_TEMPLATE:
            if os.path.exists(ZULIP_TEMPLATE):
                with open(ZULIP_TEMPLATE, 'r') as f:
                    self.template = Template(f.read())
            else:
                self.template = Template(ZULIP_TEMPLATE)
        else:
            self.template = Template(DEFAULT_TMPL)

    def pre_receive(self, alert):
        return alert

    def post_receive(self, alert):
        if alert.repeat and alert.status in ['ack', 'blackout', 'closed']:
            # skip sending message if original alert ACKed
            return

        try:
            text = self.template.render(alert.__dict__)
        except UndefinedError:
            text = "Can't render zulip template message."

        response = None

        try:
            message_to = None
            message_subject = None
            if (ZULIP_SERVICE_TOPIC_MAP
                    and isinstance(ZULIP_SERVICE_TOPIC_MAP, dict)):
                # ZULIP_SERVICE_TOPIC_MAP is a dict in the form
                # {'service1':
                #    {'to': 'stream_name', 'subject': 'topic_name'}
                # }
                for srv in alert.service:
                    if srv in ZULIP_SERVICE_TOPIC_MAP:
                        val = ZULIP_SERVICE_TOPIC_MAP[srv]
                        if 'subject' in val:
                            message_subject = val['subject']
                        if 'to' in val:
                            message_to = val['to']
                        break

            if not message_to:
                message_to = ZULIP_TO
            if not message_subject:
                message_subject = ZULIP_SUBJECT

            request = {
                'type': ZULIP_TYPE,
                'to': message_to,
                'subject': message_subject,
                'content': text
            }
            LOG.debug('Zulip: message=%s', text)

            response = self.bot.send_message(request)

            if response['result'] != 'success':
                LOG.warn('Error sending alert message to Zulip %s' %
                         response['msg'])
        except Exception as e:
            raise RuntimeError("Zulip: ERROR - %s", e)

        LOG.debug('Zulip: %s', response)

        return

    def status_change(self, alert, status, text):
        return
