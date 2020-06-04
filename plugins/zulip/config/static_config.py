"""Configurations fixed for plugin"""
from dataclasses import dataclass
from typing import Dict, List

import tyaml
from ocomone import Resources


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
        configs = tyaml.load(src_cfg, cfg_class)  # type: List[BaseConfiguration]
    result = {cfg.name: cfg for cfg in configs}
    return result


DATABASE: Dict[str, BaseConfiguration] = _cfg_load(_CONFIGS['db_structure.yaml'], List[BaseConfiguration])
DB_ROWS: Dict[str, BaseConfiguration] = _cfg_load(_CONFIGS['db_init_data.yaml'], List[BaseConfiguration])
