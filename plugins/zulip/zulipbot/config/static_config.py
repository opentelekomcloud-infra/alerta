"""Configurations fixed for plugin"""
import logging
import os
from dataclasses import dataclass

import yaml

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class Resources:
    """Resource retrieval from dedicated resource directory.

    Example:
        ``resources = Resources(__file__)``

        ``resources["my_file.txt"]``

            will have return of:

        ``C:\\\\Path\\to\\python_file\\resources\\my_file.txt``
    """

    def __init__(self, content_root: str, resources_dir: str = "resources", create_resource_root=False):
        """Initialize resource retrieval, normally `content_root` should be `__file__`"""
        if os.path.isfile(content_root):
            content_root = os.path.dirname(content_root)
        self.resource_root = os.path.abspath(f"{content_root}/{resources_dir}")
        if create_resource_root and not os.path.exists(self.resource_root):
            LOGGER.warning("No resource root exists at %s, directory will be created", content_root)
            os.makedirs(self.resource_root, exist_ok=True)

    def __repr__(self):
        return f"{type(self).__name__} at {self.resource_root}"

    def __getitem__(self, resource_name):
        """Return path to resource by given name. If given path is absolute, return if without change"""
        if os.path.isabs(resource_name):
            return resource_name
        return os.path.abspath(f"{self.resource_root}/{resource_name}")


@dataclass(frozen=True)
class BaseConfiguration:
    """Base configuration class"""
    name: str
    params: dict


@dataclass(frozen=True)
class ZulipTopicMap:
    """Topic map class"""
    to: str
    subject: str
    template: str
    environment: str
    skip: bool


def topic_map(data: list):
    """Topic map"""
    map = {}
    dct = {item[0] + '.' + item[4]: item[1:] for item in data}
    for key, value in dct.items():
        map.update({key: ZulipTopicMap(*value)})
    return map


_CONFIGS = Resources(__file__)


def _dbcfg_load(cfg_file: str):
    map = {}
    with open(cfg_file, 'r') as src_cfg:
        try:
            config = yaml.safe_load(src_cfg)
        except yaml.YAMLError as exc:
            LOGGER.error(exc)
    dct = {item['name']: item["params"] for item in config}
    for key, value in dct.items():
        map.update({key: BaseConfiguration(key, value)})
    return map


DATABASE = _dbcfg_load(_CONFIGS['db_structure.yaml'])
DB_ROWS = _dbcfg_load(_CONFIGS['db_init_data.yaml'])
