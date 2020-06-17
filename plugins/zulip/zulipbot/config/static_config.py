"""Configurations fixed for plugin"""
import logging
import os
from dataclasses import dataclass
from typing import (
    Dict,
    List,
    Type as __Type,
    TypeVar as __TypeVar
)

import yaml

from zulipbot.loader import special_loader

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

T = __TypeVar("T")


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


def load(stream, as_type: __Type[T]) -> T:
    """Load yaml"""
    return yaml.load(stream, Loader=special_loader(as_type))


@dataclass(frozen=True)
class BaseConfiguration:
    """Base configuration class"""
    name: str
    params: dict


@dataclass(frozen=True)
class AlertaConfiguration:
    """Alerta configuration class"""
    config_id: int
    config_name: str
    alerta_endpoint: str
    alerta_timeout: int
    alerta_debug: bool
    skip_environment: str
    repeat_interval: int


@dataclass(frozen=True)
class TopicMap:
    """Topic map class"""
    to: str
    subject: str


@dataclass(frozen=True)
class SkipMap:
    """Topic map class"""
    skip: bool
    environment: str
    topic: str


def topic_map(data: list):
    """Topic map"""
    map = {}
    dct = {item[0]: item[1:] for item in data}
    for key, value in dct.items():
        map.update({key: TopicMap(*value)})
    return map


_CONFIGS = Resources(__file__)


def _cfg_load(cfg_file: str, cfg_class):
    with open(cfg_file, 'r') as src_cfg:
        configs = load(src_cfg, cfg_class)  # type: List[BaseConfiguration]
    result = {cfg.name: cfg for cfg in configs}
    return result


DATABASE: Dict[str, BaseConfiguration] = _cfg_load(_CONFIGS['db_structure.yaml'], List[BaseConfiguration])
DB_ROWS: Dict[str, BaseConfiguration] = _cfg_load(_CONFIGS['db_init_data.yaml'], List[BaseConfiguration])
