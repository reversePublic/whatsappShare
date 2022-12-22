from .env import MyEnv
from .env_ios import iOSMyEnv
from .env_android import AndroidMyEnv

from .env_config import MyEnvConfig
from .env_config_id import IDEnvConfig
from .env_config_kz import KZEnvConfig
from .env_config_ru import RUEnvConfig
from .env_config_kh import KHEnvConfig
from .env_config_ph import PHEnvConfig
from .env_config_hk import HKEnvConfig
from .env_config_vn import VNEnvConfig
from .env_config_us import USEnvConfig


import logging

logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
# ch.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(levelname).1s %(asctime)s %(name)s - %(message)s')

ch.setFormatter(formatter)

logger.addHandler(ch)
