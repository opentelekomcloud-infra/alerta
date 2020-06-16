import logging

import psycopg2

from plugins.zulip.config.static_config import topic_map, SkipMap

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class DBHelper:
    """Postgre client wrapper"""

    def __init__(self, connection_string: str):
        self.connection_string = connection_string

    def __connect__(self):
        """Open connection"""
        try:
            self.con = psycopg2.connect(self.connection_string)
            self.con.autocommit = True
            self.cur = self.con.cursor()
        except (Exception, psycopg2.Error) as error:
            raise error('Error while connecting to PostgreSQL')

    def __disconnect__(self):
        """Close connection"""
        if self.con:
            self.con.commit()
            self.cur.close()
            self.con.close()
        LOGGER.info(f'Connection to database closed')

    def get(self, table, columns, condition=None, custom_clause=None, limit=None):
        """Select data from table"""
        if condition:
            query = f'SELECT {columns} FROM {table} WHERE {condition};'
        elif custom_clause:
            query = f'SELECT {columns} FROM {table} {custom_clause};'
        else:
            query = f'SELECT {columns} FROM {table};'
        self.cur.execute(query)
        rows = self.cur.fetchall()
        return rows[len(rows) - limit if limit else 0:]

    def write(self, table, columns, data):
        """Insert data to table"""
        query = f'INSERT INTO {table} ({columns}) VALUES ({data});'
        self.cur.execute(query)
        self.con.commit()

    def query(self, sql):
        """Custom query"""
        self.cur.execute(sql)
        self.con.commit()

    def get_zulip_templates(self):
        return dict(self.get(columns='topic_name, template_data', table='templates',
                             custom_clause='INNER JOIN topics ON templates.template_id=topics.templ_id'))

    def get_topics(self):
        return topic_map(self.get(table='topics', columns='topic_name, zulip_to, zulip_subject'))

    def get_skip_list(self):
        return [SkipMap(*item) for item in
                (self.get(columns='sk.skip, env.name, tpc.topic_name', table='skip_topics sk',
                          custom_clause='INNER JOIN alerta_environments env ON sk.environment_id = env.id '
                                        'INNER JOIN topics tpc ON sk.topic_id = tpc.topic_id'))]
