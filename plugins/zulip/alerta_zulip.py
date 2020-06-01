import logging
import os
from datetime import datetime

import zulip
from jinja2 import Template, UndefinedError

from plugins.zulip.database import DBHelper

try:
    from alerta.plugins import app  # alerta >= 5.0
except ImportError:
    from alerta.app import app  # alerta < 5.0
from alerta.plugins import PluginBase

LOG = logging.getLogger('alerta.plugins.zulip')

ZULIP_API_KEY = app.config.get('ZULIP_API_KEY') or os.environ.get('ZULIP_API_KEY')
ZULIP_EMAIL = app.config.get('ZULIP_EMAIL') or os.environ.get('ZULIP_EMAIL')
ZULIP_SITE = app.config.get('ZULIP_SITE') or os.environ.get('ZULIP_SITE')
ZULIP_TYPE = app.config.get('ZULIP_TYPE') or os.environ.get('ZULIP_TYPE', 'stream')
ZULIP_TO = app.config.get('ZULIP_TO') or os.environ.get('ZULIP_TO')
ZULIP_SUBJECT = app.config.get('ZULIP_SUBJECT') or os.environ.get('ZULIP_SUBJECT', 'Alert')
ZULIP_ALLOW_UNSECURE = app.config.get('ZULIP_ALLOW_UNSECURE') or os.environ.get('ZULIP_ALLOW_UNSECURE')
DB_HOST = app.config.get('DB_HOST') or os.environ.get('DB_HOST')
DB_PORT = app.config.get('DB_PORT') or os.environ.get('DB_PORT')
DB_USER = app.config.get('DB_USER') or os.environ.get('DB_USER')
DB_PASSWORD = app.config.get('DB_PASSWORD') or os.environ.get('DB_PASSWORD')
DB_NAME = app.config.get('DB_NAME') or os.environ.get('DB_NAME', 'alerta')


class ZulipBot(PluginBase):  # PluginBase

    def __init__(self, name=None):
        self.db_args = {
            'host': DB_HOST,
            'port': DB_PORT,
            'username': DB_USER,
            'password': DB_PASSWORD,
            'dbname': DB_NAME
        }

        zulip_args = {
            'site': ZULIP_SITE,
            'email': ZULIP_EMAIL,
            'api_key': ZULIP_API_KEY
        }
        if ZULIP_ALLOW_UNSECURE is not None:
            zulip_args['insecure'] = ZULIP_ALLOW_UNSECURE
        self.bot = zulip.Client(**zulip_args)

        # super(ZulipBot, self).__init__(name)

    def pre_receive(self, alert):
        return alert

    def post_receive(self, alert):
        if alert.status in ['ack', 'blackout', 'closed'] and \
                alert.environment in self.environments_to_skip and \
                delta_minutes(alert.last_receive_time) <= self.alerta_config['repeat_interval']:
            return

        self.check_updates()
        template_name = '_'.join(alert.service)
        if template_name in self.ZULIP_TEMPLATES:
            template = Template(self.ZULIP_TEMPLATES[template_name])
        else:
            template = Template(self.ZULIP_TEMPLATES['DEFAULT_TMPL'])

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
                    if alert.environment == 'preprod':
                        message_subject = '[PREPROD]_' + val.subject
                    else:
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
        db = DBHelper(
            host=self.db_args['host'],
            port=self.db_args['port'],
            user=self.db_args['username'],
            password=self.db_args['password'],
            db=self.db_args['dbname']
        )
        db.__connect__()
        self.alerta_config = db.get_alerta_configuration()
        self.environments_to_skip = self.alerta_config.skip_environment.split(',')
        self.ZULIP_TEMPLATES = db.get_zulip_templates()
        self.ZULIP_SERVICE_TOPIC_MAP = db.get_topics()
        db.__disconnect__()


def delta_minutes(last_receive_time) -> int:
    if last_receive_time is None:
        return 0
    return (datetime.utcnow().timestamp() - last_receive_time.timestamp()) / 60
