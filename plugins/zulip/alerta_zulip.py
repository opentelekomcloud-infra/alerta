import logging
import os
from datetime import datetime

import zulip
from jinja2 import Template, UndefinedError

from zulipbot.config.static_config import DATABASE, DB_ROWS
from zulipbot.database import DBHelper

try:
    from alerta.plugins import app  # alerta >= 5.0
except ImportError:
    from alerta.app import app  # alerta < 5.0
from alerta.plugins import PluginBase

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
                or os.environ.get('ZULIP_SUBJECT', 'APImon alert')
ZULIP_ALLOW_UNSECURE = app.config.get('ZULIP_ALLOW_UNSECURE') \
                       or os.environ.get('ZULIP_ALLOW_UNSECURE')
ZULIP_REPEAT_INTERVAL = app.config.get('ZULIP_REPEAT_INTERVAL') \
                        or os.environ.get('ZULIP_REPEAT_INTERVAL', 5)
DATABASE_URL = app.config.get('DATABASE_URL') \
               or os.environ.get('DATABASE_URL')

DEFAULT_TMPL = """
{% if customer %}Customer: `{{customer}}` {% endif %}
*[{{ status.capitalize() }}] {{ environment }} {{ severity.capitalize() }}*
{{ event }} {{ resource.capitalize() }}
```
{{ text }}
```
"""


class ZulipBot(PluginBase):  # PluginBase

    def __init__(self, name=None):
        self.connection_string = DATABASE_URL
        self.db = DBHelper(self.connection_string)
        self.structure = DATABASE
        self.db_data = DB_ROWS
        self.ZULIP_TEMPLATES = {}
        self.ZULIP_SERVICE_TOPIC_MAP = {}
        self.SKIP_MAP = []

        zulip_args = {
            'site': ZULIP_SITE,
            'email': ZULIP_EMAIL,
            'api_key': ZULIP_API_KEY
        }
        if ZULIP_ALLOW_UNSECURE is not None:
            zulip_args['insecure'] = ZULIP_ALLOW_UNSECURE
        self.bot = zulip.Client(**zulip_args)

        self.db.__connect__()
        for item in self.structure.values():
            self.db.query(item.params)
        for item in self.db_data.values():
            self.db.query(item.params)
        self.db.__disconnect__()
        super(ZulipBot, self).__init__(name)

    def pre_receive(self, alert):
        return alert

    def post_receive(self, alert):
        template_name = '_'.join(alert.service)

        self.check_updates()

        if alert.status in ['ack', 'blackout', 'closed']:
            return
        elif alert.repeat and delta_minutes(alert.last_receive_time) <= ZULIP_REPEAT_INTERVAL:
            return
        for item in self.SKIP_MAP:
            if alert.environment == item.environment and template_name == item.topic and item.skip is True:
                return

        if template_name in self.ZULIP_TEMPLATES:
            template = Template(self.ZULIP_TEMPLATES[template_name])
        else:
            template = Template(DEFAULT_TMPL)

        try:
            text = template.render(alert.__dict__)
        except UndefinedError:
            text = "Can't render zulip template message."

        response = None

        try:
            message_to = None
            message_subject = None
            if (self.ZULIP_SERVICE_TOPIC_MAP
                    and isinstance(self.ZULIP_SERVICE_TOPIC_MAP, dict)):
                if template_name in self.ZULIP_SERVICE_TOPIC_MAP:
                    val = self.ZULIP_SERVICE_TOPIC_MAP[template_name]
                    message_subject = val.subject
                    message_to = val.to

            if not message_to:
                message_to = ZULIP_TO
            if not message_subject:
                message_subject = '_'.join(alert.service)

            request = {
                'type': ZULIP_TYPE.strip(),
                'to': message_to.strip(),
                'subject': message_subject.strip(),
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

    def check_updates(self):
        """Load/Re-Load Alerta configuration Topics and Templates"""
        self.db.__connect__()
        self.ZULIP_TEMPLATES = self.db.get_zulip_templates()
        self.ZULIP_SERVICE_TOPIC_MAP = self.db.get_topics()
        self.SKIP_MAP = self.db.get_skip_list()
        self.db.__disconnect__()


def delta_minutes(last_receive_time) -> int:
    if last_receive_time is None:
        return 0
    return (datetime.utcnow().timestamp() - last_receive_time.timestamp()) / 60
